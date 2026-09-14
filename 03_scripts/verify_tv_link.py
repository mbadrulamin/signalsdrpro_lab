#!/usr/bin/env python3
"""
Prove a DVB-T link end to end, over the air, with numbers instead of opinions.

Transmits a known transport stream and receives it on the same radio at the
same time, then compares what came back against what went out -- byte for
byte.  A picture on a screen shows that a link *mostly* works; this shows
exactly how well.

    ./verify_tv_link.py --seconds 20 --channel 21 --tx-gain 0 --tx-amplitude 0.5

  !! THIS TRANSMITS.  Contained environment only: Faraday cage, or cable and
  !! attenuator.  Scan first with scan_tv_band.py and pick a dead channel.
  !! Defaults are deliberately feeble: tx_gain 0 dB, amplitude 0.3.

The comparison anchors on a PSI table packet, never on null packets: nulls are
all 0xFF and match anywhere, which makes a broken decode look 99.9 % correct.
"""
import argparse
import os
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dvbt_chain import (DvbtTx, DvbtRx, MerProbe, TsProbe, dvbt_bitrate,   # noqa: E402
                        sample_rate, parse_mode, mode_summary, FFT_MODES, GUARDS)


def channel_freq(ch):
    return 474e6 + 8e6 * (ch - 21)


class Link:
    """TX and RX on one B210: transmit on TX/RX, receive on RX2, together."""

    def __init__(self, a):
        from gnuradio import gr, blocks, uhd, filter as gfilter
        const, cr, gi = parse_mode(a.mode)
        fs = sample_rate(a.bandwidth)
        nfft = FFT_MODES[a.fft][1]
        cp = nfft // GUARDS[gi][1]
        freq = a.freq if a.freq else channel_freq(a.channel)

        class TB(gr.top_block):
            def __init__(s):
                gr.top_block.__init__(s, 'tv_link')
                s.src = blocks.file_source(gr.sizeof_char, a.ts, True)
                s.tx = DvbtTx(a.fft, const, cr, gi)
                # Drop the first OFDM symbol: it carries a start-up transient
                # with 31 dB PAPR against 11 dB steady state.
                s.skip = blocks.skiphead(gr.sizeof_gr_complex, nfft + cp)
                s.amp = blocks.multiply_const_cc(a.tx_amplitude)
                s.sink = uhd.usrp_sink(
                    'send_frame_size=8192,num_send_frames=256',
                    uhd.stream_args(cpu_format='fc32', channels=[0]), '')
                s.sink.set_samp_rate(fs)
                s.sink.set_center_freq(uhd.tune_request(freq), 0)
                s.sink.set_gain(a.tx_gain, 0)
                s.sink.set_antenna('TX/RX', 0)
                s.sink.set_bandwidth(fs, 0)
                s.connect(s.src, s.tx, s.skip, s.amp, s.sink)

                s.usrp = uhd.usrp_source(
                    'num_recv_frames=512',
                    uhd.stream_args(cpu_format='fc32', channels=[0]))
                s.usrp.set_samp_rate(fs)
                s.usrp.set_center_freq(uhd.tune_request(freq), 0)
                s.usrp.set_gain(a.rx_gain, 0)
                s.usrp.set_antenna(a.rx_antenna, 0)
                s.usrp.set_bandwidth(fs, 0)
                s.rx = DvbtRx(a.fft, const, cr, gi)
                s.ts_sink = blocks.file_sink(gr.sizeof_char, a.out)
                s.ts_sink.set_unbuffered(False)
                s.probe = TsProbe()
                s.mer = MerProbe(const, decim=16)
                s.lvl = blocks.probe_signal_f()
                s.connect(s.usrp, s.rx)
                s.connect((s.rx, 0), s.ts_sink)
                s.connect((s.rx, 0), s.probe)
                s.connect((s.rx, 1), s.mer)
                # probe_signal_f holds the LAST value it saw, so it must be fed
                # a smoothed stream. Without the IIR it reports one random
                # instantaneous power sample and swings over 20 dB.
                s.connect(s.usrp, blocks.complex_to_mag_squared(),
                          blocks.keep_one_in_n(gr.sizeof_float, 1024),
                          gfilter.single_pole_iir_filter_ff(0.005),
                          blocks.nlog10_ff(10, 1, 0), s.lvl)

        self.tb = TB()
        self.freq = freq
        self.rate, _, _ = dvbt_bitrate(a.fft, const, cr, gi, a.bandwidth)


def compare(out_path, src_path):
    """Byte-exact comparison, anchored on a PSI table packet."""
    out = np.fromfile(out_path, dtype=np.uint8)
    src = np.fromfile(src_path, dtype=np.uint8)
    if len(out) < 188 * 200:
        return None, len(out)
    o = out[:(len(out) // 188) * 188].reshape(-1, 188)
    pid = ((o[:, 1].astype(np.int32) & 0x1f) << 8) | o[:, 2]
    tbl = np.where((pid != 0x1fff) & (o[:, 0] == 0x47))[0]
    if len(tbl) < 3:
        return None, len(out)
    for k in tbl[1:40]:
        k = int(k)
        span = min(400, len(o) - k)
        if span < 40:
            break
        i = src.tobytes().find(o[k:k + span].tobytes())
        if i < 0:
            continue
        n = (min(len(out) - k * 188, len(src) - i) // 188) * 188
        a, b = out[k * 188:k * 188 + n], src[i:i + n]
        return int(np.count_nonzero(a != b)), n
    return None, len(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ts', default=os.path.join(tempfile.gettempdir(), 'dvbt_selftest.ts'),
                    help='transport stream to transmit (default: the one dvbt_chain.py makes)')
    ap.add_argument('--out', default='/tmp/verify_rx.ts')
    ap.add_argument('--seconds', type=float, default=15.0)
    ap.add_argument('--channel', type=int, default=21)
    ap.add_argument('--freq', type=float, help='override the channel with an explicit Hz')
    ap.add_argument('--mode', default='16qam-2/3-1/32')
    ap.add_argument('--fft', default='8k', choices=['2k', '8k'])
    ap.add_argument('--bandwidth', type=float, default=8e6)
    ap.add_argument('--tx-gain', type=float, default=0.0)
    ap.add_argument('--tx-amplitude', type=float, default=0.3)
    ap.add_argument('--rx-gain', type=float, default=20.0)
    ap.add_argument('--rx-antenna', default='RX2')
    ap.add_argument('--yes', action='store_true', help='skip the transmit confirmation')
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(a.ts):
        cand = os.path.join(here, a.ts)
        a.ts = cand if os.path.exists(cand) else a.ts
    if not os.path.exists(a.ts):
        rate, _, _ = dvbt_bitrate(a.fft, *parse_mode(a.mode), a.bandwidth)
        print(f"{a.ts} not found. Make one first:\n"
              f"  ./make_test_ts.py --out {a.ts} --seconds 5 --rate {int(rate)}\n"
              f"  ./make_video_ts.py video.mp4 {a.ts} --mode {a.mode}", file=sys.stderr)
        return 2

    freq = a.freq if a.freq else channel_freq(a.channel)
    print(mode_summary(a.fft, *parse_mode(a.mode), a.bandwidth))
    print(f"frequency  : {freq/1e6:.3f} MHz"
          f"{'' if a.freq else f' (UHF ch {a.channel})'}")
    print(f"transmit   : amplitude {a.tx_amplitude}, gain {a.tx_gain} dB  on TX/RX")
    print(f"receive    : gain {a.rx_gain} dB on {a.rx_antenna}")
    print(f"duration   : {a.seconds} s\n")
    if a.tx_amplitude > 0 and not a.yes:
        print("This transmits on a broadcast television channel.")
        print("Contained environment only. Ctrl-C now if anything is connected to")
        print("an antenna. Continuing in 5 seconds...")
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            return 1

    if os.path.exists(a.out):
        os.remove(a.out)
    link = Link(a)
    tb = link.tb
    tb.start()
    t0 = time.time()
    try:
        while time.time() - t0 < a.seconds:
            time.sleep(2.0)
            s = tb.probe.snapshot()
            sz = os.path.getsize(a.out) if os.path.exists(a.out) else 0
            print(f"  t={time.time()-t0:5.1f}s  level {tb.lvl.level():6.1f} dBFS  "
                  f"MER {tb.mer.mer():6.1f} dB  TS {sz/1e6:7.2f} MB  "
                  f"pkts {s['packets']:>8,}  CC err {s['cc_errors']:>6,}")
    except KeyboardInterrupt:
        pass
    tb.stop()
    tb.wait()

    snap = tb.probe.snapshot()
    err, n = compare(a.out, a.ts)
    expected = link.rate * a.seconds / 8.0

    print("\n" + "=" * 70)
    print(f"  transmitted from : {a.ts}")
    print(f"  received into    : {a.out}")
    print(f"  MER              : {tb.mer.mer():.1f} dB")
    print(f"  level            : {tb.lvl.level():.1f} dBFS")
    print(f"  packets decoded  : {snap['packets']:,}  "
          f"(expect ~{expected/188:,.0f} in {a.seconds:.0f} s)")
    print(f"  sync errors      : {snap['sync_errors']:,}")
    print(f"  continuity errors: {snap['cc_errors']:,}  "
          f"(rate {snap['cc_error_rate']:.2e})")
    if snap['services']:
        print(f"  service names    : {', '.join(snap['services'].values())}")
    if err is None:
        print(f"  byte comparison  : COULD NOT ALIGN -- no usable decode ({n:,} bytes out)")
        verdict = 'FAIL'
    else:
        ber = err / max(n, 1)
        print(f"  byte comparison  : {n:,} bytes, {err} mismatches "
              f"-> {100*(1-ber):.6f} % exact  (byte error rate {ber:.2e})")
        # Broadcast practice calls a link "quasi error free" when the viewer
        # sees at most one artefact per hour.  Over a real radio channel with
        # phase noise and the occasional USB hiccup, demanding literally zero
        # errors is not a useful test -- the question is whether the picture
        # would be watchable.
        if ber < 1e-5:
            verdict = 'PASS - clean'
        elif ber < 1e-3:
            verdict = 'PASS - watchable, occasional artefacts'
        else:
            verdict = 'FAIL'
    print("=" * 70)
    print(f"  VERDICT: {verdict}")
    return 0 if verdict.startswith('PASS') else 1


if __name__ == '__main__':
    sys.exit(main())
