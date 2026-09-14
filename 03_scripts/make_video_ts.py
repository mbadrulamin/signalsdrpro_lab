#!/usr/bin/env python3
"""
Turn a video file into a constant-bit-rate MPEG-2 transport stream sized
*exactly* for a DVB-T mode.

Why the rate has to be exact
---------------------------
A DVB-T modulator is a clock, not a queue.  Once you choose FFT size,
constellation, code rate and guard interval, the chain swallows transport
bytes at one fixed rate and nothing you do changes it.  Feed it a stream muxed
at a different rate and one of two things happens:

  TS rate too low  -> the modulator starves; the flowgraph stalls or repeats
  TS rate too high -> bytes pile up; the picture drifts ahead of its clock and
                      the receiver's buffer eventually overruns

So the mux rate is computed from the modulation parameters, not chosen, and
ffmpeg is told to stuff null packets up to precisely that figure.  This is the
same reason a real broadcaster's multiplex is quoted to the bit per second.

    ./make_video_ts.py --list-modes
    ./make_video_ts.py input.mp4 out.ts --mode 16qam-2/3-1/32
    ./make_video_ts.py out.ts --verify

Requires ffmpeg for the encode (`sudo apt install ffmpeg`).  --verify and
--list-modes are pure Python and need nothing.
"""
import argparse
import os
import shutil
import subprocess
import sys

# ---------------------------------------------------------------------------
# DVB-T useful bit rate, derived rather than tabulated (ETSI EN 300 744)
# ---------------------------------------------------------------------------
# Elementary period T, from which every other time in the standard follows.
ELEMENTARY_T = {8e6: 7.0 / 64e6, 7e6: 1.0 / 8e6, 6e6: 7.0 / 48e6}
DATA_CARRIERS = {2048: 1512, 8192: 6048}   # payload cells per OFDM symbol
BITS = {'qpsk': 2, '16qam': 4, '64qam': 6}
CODE_RATES = {'1/2': (1, 2), '2/3': (2, 3), '3/4': (3, 4), '5/6': (5, 6), '7/8': (7, 8)}
GUARDS = {'1/32': 32, '1/16': 16, '1/8': 8, '1/4': 4}
RS_RATE = 188.0 / 204.0                    # outer Reed-Solomon (204,188)

# ---------------------------------------------------------------------------
# DVB-T2 (ETSI EN 302 755).  Its payload rate is not a closed-form function of
# "mode" the way DVB-T's is: a T2 frame is an explicit number of OFDM symbols
# carrying an explicit number of LDPC blocks, so the rate follows from those
# two counts and nothing else.
# ---------------------------------------------------------------------------
# Kbch: BCH payload bits per FEC block.  Nldpc = 64800 (normal) / 16200 (short).
DVBT2_KBCH = {
    'normal': {'1/2': 32208, '3/5': 38688, '2/3': 43040,
               '3/4': 48408, '4/5': 51648, '5/6': 53840},
    'short':  {'1/2': 7032, '3/5': 9552, '2/3': 10632,
               '3/4': 11712, '4/5': 12432, '5/6': 13152},
}
# Number of P2 preamble symbols, by FFT size (EN 302 755 table 14)
DVBT2_NP2 = {1024: 16, 2048: 8, 4096: 4, 8192: 2, 16384: 1, 32768: 1}
DVBT2_FFT = {'1k': 1024, '2k': 2048, '4k': 4096,
             '8k': 8192, '16k': 16384, '32k': 32768}
DVBT2_GUARDS = {'1/128': 128, '1/32': 32, '1/16': 16, '19/256': 256.0 / 19,
                '1/8': 8, '19/128': 128.0 / 19, '1/4': 4}
BBHEADER_BITS = 80          # 10-byte BBHEADER in front of every BBFRAME
P1_SAMPLES = 2048           # C + A + B = 542 + 1024 + 482


def dvbt2_bitrate(fft, guard, code_rate, fecblocks, numdatasyms,
                  framesize='normal', chan_bw=8e6):
    """Useful transport-stream bit rate of one DVB-T2 PLP, in bit/s.

    Per T2 frame the chain swallows exactly

        fecblocks x (Kbch - 80)   bits

    and emits exactly

        2048 + (NP2 + numdatasyms) x (Nfft + Ncp)   samples

    at one sample per elementary period.  Divide one by the other.

    Verified against the running chain: Lab 10's configuration (1K, QPSK,
    CR 1/2, GI 1/8, 48 FEC blocks, 1966 data symbols) consumed 15,421,440
    transport bytes while emitting exactly 80.0000 T2 frames of 2,285,312
    samples -- 192,768 bytes per frame, 6.169662 Mbit/s, which is what this
    function returns to six decimal places.
    """
    nfft = DVBT2_FFT[fft]
    ncp = int(round(nfft / DVBT2_GUARDS[guard]))
    kbch = DVBT2_KBCH[framesize][code_rate]
    fs = 1.0 / ELEMENTARY_T[chan_bw]
    frame_samples = P1_SAMPLES + (DVBT2_NP2[nfft] + numdatasyms) * (nfft + ncp)
    frame_bits = fecblocks * (kbch - BBHEADER_BITS)
    return frame_bits / (frame_samples / fs), frame_samples, frame_bits // 8


def dvbt_bitrate(nfft, const, code_rate, guard, chan_bw=8e6):
    """Useful (transport-stream) bit rate in bit/s for one DVB-T mode.

        Tu = nfft * T                       useful symbol time
        Ts = Tu * (1 + 1/G)                 plus the guard interval
        Rb = cells * bits/cell / Ts         raw cell rate
             * code_rate                    inner convolutional code
             * 188/204                      outer Reed-Solomon
    """
    T = ELEMENTARY_T[chan_bw]
    Tu = nfft * T
    Ts = Tu * (1.0 + 1.0 / GUARDS[guard])
    num, den = CODE_RATES[code_rate]
    raw = DATA_CARRIERS[nfft] * BITS[const] / Ts
    return raw * num / den * RS_RATE, Tu, Ts


def sample_rate(chan_bw=8e6):
    """The modulator's complex sample rate: one sample per elementary period."""
    return 1.0 / ELEMENTARY_T[chan_bw]


def parse_mode(s):
    """'16qam-2/3-1/32' -> ('16qam', '2/3', '1/32')"""
    parts = s.split('-')
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"mode must look like 16qam-2/3-1/32, got {s!r}")
    const, cr, gi = parts
    if const not in BITS or cr not in CODE_RATES or gi not in GUARDS:
        raise argparse.ArgumentTypeError(f"unknown mode {s!r} (see --list-modes)")
    return const, cr, gi


def list_modes(nfft, chan_bw):
    print(f"DVB-T useful bit rates, {int(chan_bw/1e6)} MHz channel, "
          f"{'8K' if nfft == 8192 else '2K'} mode")
    print(f"sample rate {sample_rate(chan_bw)/1e6:.6f} Msps   "
          f"data carriers {DATA_CARRIERS[nfft]}\n")
    header = "  ".join(f"{g:>7}" for g in GUARDS)
    print(f"{'constellation':>14} {'CR':>5}   {header}   (Mbit/s)")
    print("-" * 60)
    for const in BITS:
        for cr in CODE_RATES:
            cells = []
            for gi in GUARDS:
                br, _, _ = dvbt_bitrate(nfft, const, cr, gi, chan_bw)
                cells.append(f"{br/1e6:7.3f}")
            print(f"{const:>14} {cr:>5}   " + "  ".join(cells))
    print("\nmode string is  <constellation>-<code rate>-<guard>, "
          "e.g.  16qam-2/3-1/32")


def list_t2_modes(a):
    print(f"DVB-T2 payload rate, {int(a.bandwidth/1e6)} MHz channel, "
          f"{a.t2_fecblocks} FEC blocks x {a.t2_datasyms} data symbols, "
          f"{a.t2_framesize} FECFRAME\n")
    print(f"{'FFT':>5} {'GI':>7}  " + "  ".join(f"{r:>8}" for r in DVBT2_KBCH[a.t2_framesize]))
    print("-" * 72)
    for fft in DVBT2_FFT:
        for gi in DVBT2_GUARDS:
            cells = []
            for cr in DVBT2_KBCH[a.t2_framesize]:
                r, _, _ = dvbt2_bitrate(fft, gi, cr, a.t2_fecblocks,
                                        a.t2_datasyms, a.t2_framesize, a.bandwidth)
                cells.append(f"{r/1e6:8.3f}")
            print(f"{fft:>5} {gi:>7}  " + "  ".join(cells))
    print("\nThese assume the FEC-block and data-symbol counts above. Changing")
    print("FFT size or guard interval without changing those two is not a valid")
    print("T2 frame -- the frame mapper will refuse it. Lab 10's numbers are")
    print("1K / GI 1/8 / CR 1/2 / 48 blocks / 1966 symbols -> 6.170 Mbit/s.")


# ---------------------------------------------------------------------------
# Transport stream verification (no external tools)
# ---------------------------------------------------------------------------
def verify_ts(path, expect_rate=None):
    import numpy as np
    d = np.fromfile(path, dtype=np.uint8)
    if len(d) < 188 * 10:
        print(f"{path}: too short ({len(d)} bytes)")
        return 1
    npkt = len(d) // 188
    pk = d[:npkt * 188].reshape(-1, 188)
    sync_ok = int((pk[:, 0] == 0x47).sum())
    pid = ((pk[:, 1].astype(np.int32) & 0x1f) << 8) | pk[:, 2]
    uniq, cnt = np.unique(pid, return_counts=True)
    order = np.argsort(-cnt)

    print(f"{path}")
    print(f"  {len(d):,} bytes = {npkt:,} packets of 188")
    print(f"  sync byte 0x47 present on {sync_ok:,}/{npkt:,} "
          f"({100.0*sync_ok/npkt:.3f} %)")
    print(f"  distinct PIDs: {len(uniq)}")
    for i in order[:10]:
        p, c = int(uniq[i]), int(cnt[i])
        name = {0: 'PAT', 16: 'NIT', 17: 'SDT/BAT', 18: 'EIT', 0x1fff: 'null'}.get(p, '')
        print(f"    PID {p:>5} ({p:#06x})  {c:>8,} packets  {100.0*c/npkt:6.2f} %  {name}")

    # Recover the mux rate from the PCR: the two timestamps and the number of
    # bytes between them give bit/s directly, which is how a real receiver
    # locks its own clock to the multiplex.
    rate = pcr_rate(pk)
    if rate:
        print(f"  PCR-derived mux rate: {rate/1e6:.6f} Mbit/s")
        if expect_rate:
            err = (rate - expect_rate) / expect_rate * 100
            print(f"  expected            : {expect_rate/1e6:.6f} Mbit/s  "
                  f"({err:+.4f} % error)")
            if abs(err) > 0.5:
                print("  *** rate mismatch: the picture will drift. Re-mux.")
                return 1
    else:
        print("  no PCR found (cannot confirm mux rate)")
    return 0 if sync_ok == npkt else 1


def pcr_rate(pk):
    """Bit rate implied by the first and last PCR in the stream."""
    import numpy as np
    has_af = (pk[:, 3] & 0x20) != 0
    idx = np.where(has_af)[0]
    marks = []
    for i in idx:
        af_len = int(pk[i, 4])
        if af_len < 7:
            continue
        if not (pk[i, 5] & 0x10):          # PCR_flag
            continue
        b = pk[i, 6:12].astype(np.int64)
        base = (b[0] << 25) | (b[1] << 17) | (b[2] << 9) | (b[3] << 1) | (b[4] >> 7)
        ext = ((int(b[4]) & 0x01) << 8) | int(b[5])
        pcr = base * 300 + ext             # in 27 MHz units
        marks.append((int(i), pcr))
        if len(marks) > 4000:
            break
    if len(marks) < 2:
        return None
    (i0, p0), (i1, p1) = marks[0], marks[-1]
    dt = (p1 - p0) / 27e6
    if dt <= 0:
        return None
    return (i1 - i0) * 188 * 8 / dt



def audio_frame_seconds(acodec, rate=48000):
    """Duration of one compressed audio frame."""
    return {'mp2': 1152.0 / rate, 'mp3': 1152.0 / rate,
            'aac': 1024.0 / rate}.get(acodec, 1152.0 / rate)


def loop_safe_duration(src_seconds, fps, acodec):
    """Longest duration that is a whole number of video AND audio frames.

    A stream meant to be looped forever must end on a boundary both codecs
    share, or every lap leaves a sliver of one stream unmatched and the lip
    sync walks away a little more each time.  Bintang.mp4 is 209.066 s with
    video running 208.960 s and audio 209.066 s -- 106 ms apart -- which is
    exactly the kind of gap that accumulates.

    At 25 fps a video frame is 40 ms; an MP2 frame at 48 kHz is 1152/48000 =
    24 ms.  The smallest interval containing a whole number of each is 120 ms,
    so the stream is trimmed down to a multiple of that.
    """
    from fractions import Fraction
    vf = Fraction(1, 1) / Fraction(str(fps))
    af = Fraction(audio_frame_seconds(acodec)).limit_denominator(10 ** 6)
    lcm = vf * af / Fraction(__import__('math').gcd(
        vf.numerator * af.denominator, af.numerator * vf.denominator)
    ) * Fraction(vf.denominator * af.denominator)
    # simpler and safe: step by the product, then reduce by trial
    step = vf
    while (step / af).denominator != 1:
        step += vf
    n = int(Fraction(str(src_seconds)) / step)
    return float(step * n), float(step)


# ---------------------------------------------------------------------------
def ffmpeg_command(args, ffmpeg, mux_i, video, audio, output):
    """Build the encoder command line.

    Shared with tv_playout.py so that a file written for a mode and a live
    playout of the same mode are byte-for-byte the same encode -- the only
    difference being that playout loops the *input* so its clock never
    restarts.
    """
    vf = f"scale={args.width}:-2" if args.width else "null"
    cmd = [ffmpeg, '-y']
    if args.loop:
        # -stream_loop repeats the INPUT, so the muxer keeps counting upwards.
        # Looping the finished .ts instead sends the PCR backwards at every lap.
        cmd += ['-stream_loop', '-1']
    cmd += ['-i', args.input,
            '-vf', vf,
            '-r', str(args.fps),
            '-c:v', args.vcodec,
            # Constant bit rate, not merely an average: a broadcast multiplex
            # has no room to borrow from later.
            '-b:v', str(video), '-minrate', str(video), '-maxrate', str(video),
            '-bufsize', str(video // 2),
            # Baseline decodability for consumer tuners: 4:2:0 8-bit, High
            # profile level 4.0, closed GOP with a real IDR every GOP so a
            # television can start decoding at any keyframe rather than
            # waiting for an open-GOP recovery point.
            '-pix_fmt', 'yuv420p',
            '-profile:v', args.profile, '-level', args.level,
            '-g', str(args.gop), '-keyint_min', str(args.gop),
            '-sc_threshold', '0',
            '-x264opts', f'open-gop=0:min-keyint={args.gop}:keyint={args.gop}',
            '-c:a', args.acodec, '-b:a', str(audio), '-ar', '48000', '-ac', '2']
    if getattr(args, 'loop_safe', False):
        # Pad the audio with silence so it reaches exactly the same instant the
        # video does. Resampling 44.1 kHz source to 48 kHz MP2 otherwise lands
        # a couple of frames short, and a stream that loops forever cannot
        # afford a ragged edge.
        cmd += ['-af', 'apad']
    cmd += [
            # The SDT service name and provider are METADATA, not muxer
            # options: ffmpeg has no -mpegts_service_name. This is what a
            # television shows in its channel list.
            '-metadata', f'service_name={args.service_name}',
            '-metadata', f'service_provider={args.provider}',
            # -f mpegts must precede the muxer's private options, or ffmpeg
            # has no muxer to resolve them against.
            '-f', 'mpegts',
            '-muxrate', str(mux_i),
            '-pcr_period', '20',
            '-mpegts_flags', '+resend_headers',
            '-mpegts_service_type', 'digital_tv',
            '-sdt_period', '0.5', '-pat_period', '0.1', '-nit_period', '0.5',
            '-mpegts_original_network_id', str(args.net_id),
            '-mpegts_transport_stream_id', str(args.ts_id),
            '-mpegts_service_id', str(args.service_id)]
    if args.duration:
        cmd += ['-t', str(args.duration)]
    if getattr(args, 'shortest', False):
        cmd += ['-shortest']
    cmd += [output]
    return cmd


def plan_rates(args):
    """Return (mux_i, video, audio, overhead) for the requested mode."""
    if args.standard == 'dvbt2':
        mux, frame_samples, frame_bytes = dvbt2_bitrate(
            args.t2_fft, args.t2_guard, args.t2_rate, args.t2_fecblocks,
            args.t2_datasyms, args.t2_framesize, args.bandwidth)
    else:
        const, cr, gi = parse_mode(args.mode_str)
        nfft = 8192 if args.fft == '8k' else 2048
        mux, _, _ = dvbt_bitrate(nfft, const, cr, gi, args.bandwidth)
        frame_samples = frame_bytes = 0
    mux_i = int(mux)
    audio = args.audio_bitrate
    overhead = int(mux_i * 0.04) + 100_000
    video = mux_i - audio - overhead
    if getattr(args, 'video_bitrate', 0):
        video = min(video, args.video_bitrate)
    return mux_i, video, audio, overhead, frame_samples, frame_bytes


def build(args):
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        print("ffmpeg not found.\n\n"
              "  sudo apt install ffmpeg\n\n"
              "It is needed only to turn the video into a transport stream. "
              "Everything else in this repository runs without it, and\n"
              "03_scripts/make_test_ts.py will produce a valid (pictureless) "
              "stream if you just want to exercise the modulator.",
              file=sys.stderr)
        return 2

    if args.standard == 'dvbt2':
        mux, frame_samples, frame_bytes = dvbt2_bitrate(
            args.t2_fft, args.t2_guard, args.t2_rate, args.t2_fecblocks,
            args.t2_datasyms, args.t2_framesize, args.bandwidth)
        mux_i = int(mux)
        print(f"DVB-T2 mode: {args.t2_fft.upper()} FFT, GI {args.t2_guard}, "
              f"CR {args.t2_rate}, {args.t2_fecblocks} FEC blocks x "
              f"{args.t2_datasyms} data symbols")
        print(f"  T2 frame = {frame_samples:,} samples "
              f"({frame_samples/(1.0/ELEMENTARY_T[args.bandwidth])*1000:.3f} ms) "
              f"carrying {frame_bytes:,} transport bytes")
    else:
        const, cr, gi = args.mode
        nfft = 8192 if args.fft == '8k' else 2048
        mux, Tu, Ts = dvbt_bitrate(nfft, const, cr, gi, args.bandwidth)
        mux_i = int(mux)
        print(f"DVB-T mode : {'8K' if nfft == 8192 else '2K'} {const.upper()} "
              f"CR {cr} GI {gi}, {args.bandwidth/1e6:.0f} MHz")
        print(f"  Tu = {Tu*1e6:.1f} us   Ts = {Ts*1e6:.1f} us   "
              f"sample rate {sample_rate(args.bandwidth)/1e6:.6f} Msps")

    # Leave room for audio, PSI tables and PES headers.  Everything left over
    # after the reservation goes to video; ffmpeg stuffs the remainder with
    # null packets to hit -muxrate exactly.
    audio = args.audio_bitrate
    overhead = int(mux_i * 0.04) + 100_000
    video = mux_i - audio - overhead
    if args.video_bitrate:
        # A high-capacity mode does not oblige you to fill it with one service.
        # 32K/256QAM/CR2/3 carries 40 Mbit/s; a broadcaster puts six or seven
        # programmes in that. With one programme the remainder becomes null
        # packets, which is exactly what -muxrate already does.
        if args.video_bitrate > video:
            print(f"--video-bitrate {args.video_bitrate:,} exceeds the {video:,} bit/s "
                  f"this mode leaves for video after audio and overhead.", file=sys.stderr)
            return 2
        video = args.video_bitrate
    if video < 300_000:
        print(f"mode {args.mode_str} gives only {mux_i/1e6:.3f} Mbit/s -- "
              f"too little for {audio/1e3:.0f} kbit/s audio plus video.\n"
              f"Pick a faster mode (see --list-modes) or lower --audio-bitrate.",
              file=sys.stderr)
        return 2

    stuffing = mux_i - video - audio - overhead
    print(f"  transport rate {mux_i:,} bit/s  = video {video:,} + audio {audio:,} "
          f"+ overhead {overhead:,}" + (f" + null stuffing {stuffing:,}" if stuffing > 0 else ""))

    if args.loop_safe:
        import subprocess as _sp
        probe = _sp.run([shutil.which('ffprobe') or 'ffprobe', '-v', 'error',
                         '-show_entries', 'format=duration', '-of', 'csv=p=0',
                         args.input], capture_output=True, text=True)
        try:
            src = float(probe.stdout.strip())
        except ValueError:
            src = None
        if src:
            d, step = loop_safe_duration(src, args.fps, args.acodec)
            args.duration = min(args.duration, d) if args.duration else d
            # NOT -shortest. An exact -t on a duration that divides both frame
            # periods gives both streams the same length; -shortest instead
            # stops at whichever codec happens to finish first and leaves them
            # one audio frame apart -- 24 ms of lip-sync slip per lap, which is
            # invisible on the first pass and obvious after ten.
            args.shortest = False
            print(f"  loop-safe: {src:.3f} s source -> {args.duration:.3f} s "
                  f"({args.duration*args.fps:.0f} video frames, "
                  f"{args.duration/audio_frame_seconds(args.acodec):.0f} audio frames, "
                  f"step {step*1000:.0f} ms)")

    cmd = ffmpeg_command(args, ffmpeg, mux_i, video, audio, args.output)
    print("\n" + " ".join(cmd) + "\n")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        return r.returncode
    print()
    return verify_ts(args.output, expect_rate=mux)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input', nargs='?', help='source video (any format ffmpeg reads)')
    ap.add_argument('output', nargs='?', help='destination .ts')
    ap.add_argument('--standard', default='dvbt', choices=['dvbt', 'dvbt2'],
                    help='which modulator this stream will feed (default dvbt)')
    ap.add_argument('--t2-fft', default='1k', choices=list(DVBT2_FFT))
    ap.add_argument('--t2-guard', default='1/8', choices=list(DVBT2_GUARDS))
    ap.add_argument('--t2-rate', default='1/2', choices=list(DVBT2_KBCH['normal']))
    ap.add_argument('--t2-framesize', default='normal', choices=['normal', 'short'])
    ap.add_argument('--t2-fecblocks', type=int, default=48)
    ap.add_argument('--t2-datasyms', type=int, default=1966)
    ap.add_argument('--profile', default='high', help='H.264 profile')
    ap.add_argument('--level', default='4.0', help='H.264 level')
    ap.add_argument('--mode', default='16qam-2/3-1/32', dest='mode_str',
                    help='DVB-T mode, e.g. 16qam-2/3-1/32 (default) or qpsk-1/2-1/4')
    ap.add_argument('--fft', default='8k', choices=['8k', '2k'])
    ap.add_argument('--bandwidth', type=float, default=8e6, choices=[6e6, 7e6, 8e6])
    ap.add_argument('--width', type=int, default=1280,
                    help='scale to this width, keeping aspect (0 = leave alone)')
    ap.add_argument('--fps', type=float, default=25)
    ap.add_argument('--gop', type=int, default=25,
                    help='keyframe interval; short GOP = faster channel-change')
    ap.add_argument('--vcodec', default='libx264')
    ap.add_argument('--acodec', default='mp2',
                    help='mp2 is the DVB baseline every television decodes; '
                         'aac is smaller but not universal on older sets')
    ap.add_argument('--audio-bitrate', type=int, default=192_000)
    ap.add_argument('--video-bitrate', type=int, default=0,
                    help='cap the video rate and let null packets fill the rest '
                         '(0 = use everything the mode leaves over)')
    ap.add_argument('--service-name', default='SDR LAB TV')
    ap.add_argument('--provider', default='SignalSDR Pro')
    ap.add_argument('--ts-id', type=int, default=1)
    ap.add_argument('--service-id', type=int, default=1)
    ap.add_argument('--net-id', type=int, default=1)
    ap.add_argument('--duration', type=float, help='seconds to encode')
    ap.add_argument('--loop-safe', action='store_true',
                    help='trim to a whole number of both video and audio frames '
                         'so the stream can be looped without the lip sync walking')
    ap.add_argument('--loop', action='store_true',
                    help='repeat the input forever (use with --duration)')
    ap.add_argument('--list-modes', action='store_true')
    ap.add_argument('--verify', action='store_true',
                    help='check an existing .ts instead of building one')
    a = ap.parse_args()

    if a.list_modes:
        if a.standard == 'dvbt2':
            list_t2_modes(a)
        else:
            list_modes(8192 if a.fft == '8k' else 2048, a.bandwidth)
        return 0

    if a.verify:
        target = a.output or a.input
        if not target:
            ap.error('--verify needs a .ts path')
        if a.standard == 'dvbt2':
            mux, _, _ = dvbt2_bitrate(a.t2_fft, a.t2_guard, a.t2_rate,
                                      a.t2_fecblocks, a.t2_datasyms,
                                      a.t2_framesize, a.bandwidth)
        else:
            const, cr, gi = parse_mode(a.mode_str)
            nfft = 8192 if a.fft == '8k' else 2048
            mux, _, _ = dvbt_bitrate(nfft, const, cr, gi, a.bandwidth)
        return verify_ts(target, expect_rate=mux)

    if not a.input or not a.output:
        ap.error('need INPUT and OUTPUT (or --verify / --list-modes)')
    if not os.path.exists(a.input):
        ap.error(f'no such file: {a.input}')
    a.mode = parse_mode(a.mode_str)
    return build(a)


if __name__ == '__main__':
    sys.exit(main())
