#!/usr/bin/env python3
"""
Continuous television playout: feed a modulator a transport stream whose clock
never goes backwards.

The problem this solves
-----------------------
The obvious way to transmit a video on a loop is to encode it once and point a
File Source at the result with `repeat = True`.  That works for a few minutes
and then betrays you.

A transport stream carries its own clock.  Every 20 ms the muxer writes a
Programme Clock Reference, and the television slaves a 27 MHz oscillator to it.
When the file wraps, the PCR jumps *backwards* by the whole length of the
file, with no discontinuity flag to warn the receiver.  Measured on this
repository's own 209-second stream:

    first PCR   0.700 s
    last  PCR 209.560 s
    -> every lap the clock jumps back 208.86 s

The presentation timestamps go backwards at the same moment, so the decoder is
handed frames it believes are three minutes stale.  The picture does not break
up -- every byte is still perfect -- it goes *sluggish*, and stays that way,
because the receiver's clock recovery never gets a stable reference again.

The fix is not to loop the finished stream.  It is to loop the **input** and
let the muxer keep counting upwards forever, which is what a real playout
chain does.  That is all this script is: ffmpeg with `-stream_loop -1`, a
buffer, and a named pipe.

    ./tv_playout.py ~/Downloads/Bintang.mp4 --standard dvbt2 --t2-fft 32k \\
        --t2-guard 1/128 --t2-rate 2/3 --t2-fecblocks 202 --t2-datasyms 59 \\
        --video-bitrate 12000000 --fifo /tmp/tv.fifo

Then point the flowgraph's `ts_file` at /tmp/tv.fifo and start it.  Opening a
FIFO for writing blocks until a reader appears, so starting this first is
correct: it fills its buffer while it waits.

Why the buffer, and what "underruns" means
------------------------------------------
A pipe holds 64 kB by default, which at 40 Mbit/s is 13 ms.  The encoder is
fast on average -- measured 2.6x real time at 1080p -- but not uniformly: a
scene change or a lookahead flush can stall it for a moment.  Without a
reservoir that stall reaches the DAC.  This keeps about ten seconds.

**An underrun is that reservoir running dry**: the buffer was empty for a
whole second and there was nothing to hand the modulator.  The flowgraph then
blocks on its read, the transmit chain stops, and the radio puts a *gap* on
the air.  A television rides out the gap by draining its own buffers -- but
its audio and video buffers drain and recover by different amounts, so what
you see afterwards is **lip sync that has slipped and stays slipped**.

Underruns and desynchronised audio are the same fault, not two.

The cure is to stop encoding in real time.  `--copy` loops an already-encoded
file and only re-multiplexes it, which costs almost nothing:

    # once
    ./make_video_ts.py video.mp4 /tmp/show.ts --standard dvbt2 ... --loop-safe
    # then, forever
    ./tv_playout.py /tmp/show.ts --copy --standard dvbt2 ... --fifo /tmp/tv.fifo

`--loop-safe` matters for the first step.  A stream that will be looped must
end on a boundary the video and audio codecs share, or every lap leaves a
sliver of one of them unmatched.  Bintang.mp4 is 209.066 s with video running
208.960 s and audio 209.066 s -- 106 ms apart -- and at 25 fps with MP2 audio
the nearest clean cut is a multiple of 120 ms.
"""
import argparse
import os
import queue
import stat
import ctypes
import shutil
import signal
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_video_ts import (ffmpeg_command, plan_rates, dvbt2_bitrate,   # noqa: E402
                           dvbt_bitrate, parse_mode, DVBT2_FFT,
                           DVBT2_GUARDS, DVBT2_KBCH)

CHUNK = 188 * 1000          # 188 kB, a whole number of transport packets


class Playout:
    def __init__(self, cmd, fifo, depth):
        self.cmd, self.fifo = cmd, fifo
        self.q = queue.Queue(maxsize=depth)
        self.depth = depth
        self.written = 0
        self.stalls = 0
        self.underruns = 0
        self._warned = 0
        self.stop = threading.Event()
        self.proc = None

    def _read(self):
        """Pull from the encoder as fast as it will go; block when full."""
        while not self.stop.is_set():
            data = self.proc.stdout.read(CHUNK)
            if not data:
                break
            while not self.stop.is_set():
                try:
                    self.q.put(data, timeout=0.5)
                    break
                except queue.Full:
                    self.stalls += 1          # encoder ahead: normal, healthy

    def _write(self):
        """Hand the stream to the flowgraph.

        Opened O_RDWR, not O_WRONLY, and that matters. Opening a FIFO for
        writing alone *blocks until a reader appears*, so playout would sit
        invisible until the flowgraph started -- and, worse, the flowgraph
        opening the read end blocks until a writer exists, so if playout is
        not running the flowgraph hangs inside its constructor and no GUI
        window ever appears. Holding both ends means a writer is present the
        instant playout starts, the flowgraph opens immediately, and it can be
        stopped and restarted without restarting playout.
        """
        fd = os.open(self.fifo, os.O_RDWR)     # never blocks
        with os.fdopen(fd, 'wb', buffering=0) as fh:
            print(f"[playout] {self.fifo} is open and ready - start the flowgraph")
            while not self.stop.is_set():
                try:
                    data = self.q.get(timeout=1.0)
                except queue.Empty:
                    self.underruns += 1
                    continue
                try:
                    fh.write(data)             # blocks when the pipe is full
                    self.written += len(data)
                except (BrokenPipeError, OSError) as e:
                    print(f"[playout] pipe write failed: {e}")
                    self.stop.set()
                    return

    def run(self, report=True):
        self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                     stderr=subprocess.DEVNULL, bufsize=0)
        tr = threading.Thread(target=self._read, daemon=True)
        tw = threading.Thread(target=self._write, daemon=True)
        tr.start(); tw.start()
        t0 = time.time()
        try:
            while not self.stop.is_set():
                time.sleep(2.0)
                if self.proc.poll() is not None and self.q.empty():
                    print("[playout] encoder exited")
                    break
                if report:
                    fill = self.q.qsize()
                    if self.underruns > self._warned:
                        self._warned = self.underruns
                        print("  *** UNDERRUN: buffer empty, the transmitter is "
                              "putting a gap on the air.")
                        print("      Pre-encode once and re-run with --copy; "
                              "live encoding cannot share the CPU with the modulator.")
                    print(f"  buffer {fill:>4}/{self.depth} "
                          f"({100.0*fill/self.depth:5.1f} %)  "
                          f"delivered {self.written/1e6:9.1f} MB  "
                          f"({self.written*8/max(1e-9, time.time()-t0)/1e6:6.3f} Mbit/s)  "
                          f"underruns {self.underruns}")
        except KeyboardInterrupt:
            print("\n[playout] stopping")
        finally:
            self.stop.set()
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input', help='source video, looped forever')
    ap.add_argument('--fifo', default='/tmp/tv.fifo')
    ap.add_argument('--buffer-seconds', type=float, default=10.0)
    ap.add_argument('--standard', default='dvbt2', choices=['dvbt', 'dvbt2'])
    ap.add_argument('--t2-fft', default='32k', choices=list(DVBT2_FFT))
    ap.add_argument('--t2-guard', default='1/128', choices=list(DVBT2_GUARDS))
    ap.add_argument('--t2-rate', default='2/3', choices=list(DVBT2_KBCH['normal']))
    ap.add_argument('--t2-framesize', default='normal', choices=['normal', 'short'])
    ap.add_argument('--t2-fecblocks', type=int, default=202)
    ap.add_argument('--t2-datasyms', type=int, default=59)
    ap.add_argument('--mode', dest='mode_str', default='16qam-2/3-1/32')
    ap.add_argument('--fft', default='8k', choices=['2k', '8k'])
    ap.add_argument('--bandwidth', type=float, default=8e6)
    ap.add_argument('--width', type=int, default=1920)
    ap.add_argument('--fps', type=float, default=25)
    ap.add_argument('--gop', type=int, default=25)
    ap.add_argument('--vcodec', default='libx264')
    ap.add_argument('--acodec', default='mp2')
    ap.add_argument('--audio-bitrate', type=int, default=192_000)
    ap.add_argument('--video-bitrate', type=int, default=12_000_000)
    ap.add_argument('--profile', default='high')
    ap.add_argument('--level', default='4.0')
    ap.add_argument('--service-name', default='SDR LAB TV')
    ap.add_argument('--provider', default='SignalSDR Pro')
    ap.add_argument('--ts-id', type=int, default=1)
    ap.add_argument('--net-id', type=int, default=1)
    ap.add_argument('--service-id', type=int, default=1)
    ap.add_argument('--duration', type=float, default=None)
    ap.add_argument('--copy', action='store_true',
                    help='input is already encoded: remux it instead of '
                         're-encoding. Use this for anything long-running.')
    ap.add_argument('--launch', metavar='CMD',
                    help='start this command once the FIFO is ready, e.g. '
                         '"python3 ../02_flowgraphs/lab10_dvbt2_tx_rx/lab10_dvbt2_tx.py". '
                         'Guarantees the ordering the FIFO requires.')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    a.loop = True                      # the entire point of this script
    a.loop_safe = False
    a.shortest = False

    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        print("ffmpeg not found: sudo apt install ffmpeg", file=sys.stderr)
        return 2
    if not os.path.exists(a.input):
        print(f"no such file: {a.input}", file=sys.stderr)
        return 2

    mux_i, video, audio, overhead, frame_samples, frame_bytes = plan_rates(a)
    if video < 300_000:
        print(f"mode leaves only {video:,} bit/s for video", file=sys.stderr)
        return 2

    # os.path has no isfifo(); the test is on the mode bits.
    if os.path.exists(a.fifo):
        if not stat.S_ISFIFO(os.stat(a.fifo).st_mode):
            print(f"{a.fifo} exists and is not a FIFO - removing it")
            os.remove(a.fifo)
            os.mkfifo(a.fifo)
    else:
        os.mkfifo(a.fifo)

    depth = max(4, int(a.buffer_seconds * mux_i / 8 / CHUNK))
    if a.standard == 'dvbt2':
        print(f"DVB-T2 {a.t2_fft.upper()} GI {a.t2_guard} CR {a.t2_rate}, "
              f"{a.t2_fecblocks} FEC blocks x {a.t2_datasyms} data symbols")
        print(f"  T2 frame {frame_samples:,} samples carrying {frame_bytes:,} bytes")
    else:
        print(f"DVB-T {a.fft.upper()} {a.mode_str}")
    print(f"  transport rate {mux_i:,} bit/s  = video {video:,} + audio {audio:,} "
          f"+ overhead {overhead:,} + null stuffing {mux_i-video-audio-overhead:,}")
    print(f"  buffer {depth} x {CHUNK/1000:.0f} kB = "
          f"{depth*CHUNK*8/mux_i:.1f} s at this rate")
    print(f"  FIFO {a.fifo}\n")

    if a.copy:
        # Remux only. This is the important mode: re-encoding 1080p in real
        # time while the modulator is also running means ffmpeg and GNU Radio
        # fight over the same cores, and when the encoder loses, playout's
        # buffer empties, the flowgraph starves, and the transmitter puts a
        # gap on the air. Encode once, then loop the finished file for free.
        cmd = [ffmpeg, '-y', '-stream_loop', '-1', '-i', a.input, '-c', 'copy',
               '-metadata', f'service_name={a.service_name}',
               '-metadata', f'service_provider={a.provider}',
               '-f', 'mpegts',
               '-muxrate', str(mux_i),
               '-pcr_period', '20',
               '-mpegts_flags', '+resend_headers',
               '-mpegts_service_type', 'digital_tv',
               '-sdt_period', '0.5', '-pat_period', '0.1', '-nit_period', '0.5',
               '-mpegts_original_network_id', str(a.net_id),
               '-mpegts_transport_stream_id', str(a.ts_id),
               '-mpegts_service_id', str(a.service_id),
               'pipe:1']
        print("  mode: REMUX ONLY (-c copy) - no encoding, negligible CPU\n")
    else:
        cmd = ffmpeg_command(a, ffmpeg, mux_i, video, audio, 'pipe:1')
        print("  mode: LIVE ENCODE - competes with the modulator for CPU.\n"
              "        If you see underruns, pre-encode once and use --copy.\n")
    pl = Playout(cmd, a.fifo, depth)

    launched = None
    if a.launch:
        import shlex
        import threading as _th

        def _die_with_parent():
            """Ask the kernel to SIGTERM this child when playout dies.

            Without it, killing playout leaves the flowgraph running -- and
            the flowgraph is a TRANSMITTER. A `finally:` block is not enough,
            because SIGTERM kills Python without unwinding. PR_SET_PDEATHSIG
            is handled by the kernel and survives any way the parent exits.
            """
            PR_SET_PDEATHSIG = 1
            try:
                ctypes.CDLL("libc.so.6").prctl(PR_SET_PDEATHSIG, signal.SIGTERM)
            except Exception:
                pass
            os.setpgrp()                       # also kill as a group

        def _go():
            time.sleep(2.0)                    # let the buffer prime first
            print(f"[playout] launching: {a.launch}")
            pl.child = subprocess.Popen(shlex.split(a.launch),
                                        preexec_fn=_die_with_parent)
            # Stay alive for as long as the child does. PR_SET_PDEATHSIG
            # watches the parent THREAD, not the parent process, so if this
            # thread returned here the kernel would kill the flowgraph the
            # instant it started -- which is exactly what happened the first
            # time this was written.
            pl.child.wait()
        _th.Thread(target=_go, daemon=True).start()

    def _cleanup(signum=None, frame=None):
        child = getattr(pl, 'child', None)
        if child and child.poll() is None:
            print("\n[playout] stopping the flowgraph it launched")
            try:
                os.killpg(os.getpgid(child.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                child.terminate()
        pl.stop.set()
        if signum is not None:
            sys.exit(0)

    signal.signal(signal.SIGTERM, _cleanup)
    signal.signal(signal.SIGINT, _cleanup)
    try:
        pl.run(report=not a.quiet)
    finally:
        _cleanup()
    return 0


if __name__ == '__main__':
    sys.exit(main())
