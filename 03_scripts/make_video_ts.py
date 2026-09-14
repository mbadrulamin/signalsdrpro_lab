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


# ---------------------------------------------------------------------------
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

    const, cr, gi = args.mode
    nfft = 8192 if args.fft == '8k' else 2048
    mux, Tu, Ts = dvbt_bitrate(nfft, const, cr, gi, args.bandwidth)
    mux_i = int(mux)                      # ffmpeg wants an integer

    # Leave room for audio, PSI tables and PES headers.  Everything left over
    # after the reservation goes to video; ffmpeg stuffs the remainder with
    # null packets to hit -muxrate exactly.
    audio = args.audio_bitrate
    overhead = int(mux_i * 0.04) + 100_000
    video = mux_i - audio - overhead
    if video < 300_000:
        print(f"mode {args.mode_str} gives only {mux_i/1e6:.3f} Mbit/s -- "
              f"too little for {audio/1e3:.0f} kbit/s audio plus video.\n"
              f"Pick a faster mode (see --list-modes) or lower --audio-bitrate.",
              file=sys.stderr)
        return 2

    print(f"DVB-T mode : {'8K' if nfft == 8192 else '2K'} {const.upper()} "
          f"CR {cr} GI {gi}, {args.bandwidth/1e6:.0f} MHz")
    print(f"  Tu = {Tu*1e6:.1f} us   Ts = {Ts*1e6:.1f} us   "
          f"sample rate {sample_rate(args.bandwidth)/1e6:.6f} Msps")
    print(f"  transport rate {mux_i:,} bit/s  "
          f"= video {video:,} + audio {audio:,} + overhead {overhead:,}")

    vf = f"scale={args.width}:-2" if args.width else "null"
    cmd = [ffmpeg, '-y']
    if args.loop:
        cmd += ['-stream_loop', '-1']
    cmd += ['-i', args.input,
            '-vf', vf,
            '-r', str(args.fps),
            '-c:v', args.vcodec,
            '-b:v', str(video), '-minrate', str(video), '-maxrate', str(video),
            '-bufsize', str(video),
            '-g', str(args.gop),
            '-c:a', args.acodec, '-b:a', str(audio), '-ar', '48000', '-ac', '2',
            '-muxrate', str(mux_i),
            '-pcr_period', '20',
            '-mpegts_service_name', args.service_name,
            '-mpegts_service_provider', args.provider,
            '-mpegts_original_network_id', str(args.net_id),
            '-mpegts_transport_stream_id', str(args.ts_id),
            '-metadata', f'service_name={args.service_name}',
            '-f', 'mpegts']
    if args.duration:
        cmd += ['-t', str(args.duration)]
    cmd += [args.output]

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
    ap.add_argument('--acodec', default='mp2')
    ap.add_argument('--audio-bitrate', type=int, default=192_000)
    ap.add_argument('--service-name', default='SDR LAB TV')
    ap.add_argument('--provider', default='SignalSDR Pro')
    ap.add_argument('--ts-id', type=int, default=1)
    ap.add_argument('--net-id', type=int, default=1)
    ap.add_argument('--duration', type=float, help='seconds to encode')
    ap.add_argument('--loop', action='store_true',
                    help='repeat the input forever (use with --duration)')
    ap.add_argument('--list-modes', action='store_true')
    ap.add_argument('--verify', action='store_true',
                    help='check an existing .ts instead of building one')
    a = ap.parse_args()

    if a.list_modes:
        list_modes(8192 if a.fft == '8k' else 2048, a.bandwidth)
        return 0

    if a.verify:
        target = a.output or a.input
        if not target:
            ap.error('--verify needs a .ts path')
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
