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

Why the buffer
--------------
A pipe holds 64 kB by default, which at 40 Mbit/s is 13 ms.  The encoder is
fast on average -- measured 2.6x real time at 1080p -- but not uniformly: a
scene change or a lookahead flush can stall it for a moment.  Without a
reservoir that stall reaches the DAC.  This keeps about ten seconds.
"""
import argparse
import os
import queue
import shutil
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
        """Hand the stream to the flowgraph. Blocks until it opens the FIFO."""
        fd = os.open(self.fifo, os.O_WRONLY)   # waits for a reader
        with os.fdopen(fd, 'wb', buffering=0) as fh:
            print(f"[playout] flowgraph attached to {self.fifo}")
            while not self.stop.is_set():
                try:
                    data = self.q.get(timeout=1.0)
                except queue.Empty:
                    self.underruns += 1
                    continue
                try:
                    fh.write(data)
                    self.written += len(data)
                except (BrokenPipeError, OSError):
                    print("[playout] flowgraph closed the pipe")
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
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()
    a.loop = True                      # the entire point of this script

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

    if os.path.exists(a.fifo) and not os.path.isfifo(a.fifo):
        os.remove(a.fifo)
    if not os.path.exists(a.fifo):
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
    print("Waiting for the flowgraph to open the FIFO. Point ts_file at it and start it.\n")

    cmd = ffmpeg_command(a, ffmpeg, mux_i, video, audio, 'pipe:1')
    Playout(cmd, a.fifo, depth).run(report=not a.quiet)
    return 0


if __name__ == '__main__':
    sys.exit(main())
