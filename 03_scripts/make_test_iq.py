#!/usr/bin/env python3
"""
make_test_iq.py — make a fake radio station, as IQ, with contents you know.

Use it to test Labs 01-06 with no radio: every setting of the signal is known,
so you can check the flowgraph's output against it.

Three kinds of station:
    wbfm  broadcast FM, mono or stereo (the default)
    nbfm  narrow FM, 5 kHz deviation, like a walkie-talkie
    am    AM with a carrier, like aircraft voice

The stereo signal follows the broadcast standard (ITU-R BS.450):

    mpx(t) = 0.9 * [ (L+R)/2 + (L-R)/2 * sin(2*wp*t) ] + 0.1 * sin(wp*t)

with the pilot wp = 2*pi*19 kHz and the 38 kHz subcarrier locked to it so that
both cross zero, rising, at the same moment. Peak deviation is 75 kHz.

Put a different tone on each channel, and you can measure stereo separation:
the left output should contain only the left tone.

Usage:
    python3 make_test_iq.py out.cfile                 # stereo, L=1000 Hz, R=1700 Hz
    python3 make_test_iq.py out.cfile --mono          # no pilot, no L-R
    python3 make_test_iq.py out.cfile --offset 200e3  # station 200 kHz above centre
    python3 make_test_iq.py out.cfile --snr 30        # add noise (dB, in 200 kHz)
    python3 make_test_iq.py out.cfile --mode am       # AM, 80 % modulation, 1000 Hz tone
    python3 make_test_iq.py out.cfile --mode nbfm     # NBFM, 5 kHz deviation, 1000 Hz tone

Output: complex64 IQ (.cfile), the same format as Lab 05 records.
"""
import argparse
import numpy as np


def make(rate=2e6, seconds=3.0, left_hz=1000.0, right_hz=1700.0, level=0.8,
         stereo=True, offset=0.0, snr_db=None, amplitude=0.3, seed=1, mode='wbfm'):
    n = int(rate * seconds)
    t = np.arange(n) / rate
    if mode in ('am', 'nbfm'):
        tone = level * np.sin(2 * np.pi * left_hz * t)
        if mode == 'am':
            iq = amplitude * (1 + tone) * np.exp(2j * np.pi * offset * t)     # level = modulation depth
        else:
            iq = amplitude * np.exp(1j * (2 * np.pi * 5e3 * np.cumsum(tone) / rate + 2 * np.pi * offset * t))
        return _add_noise(iq, amplitude, snr_db, rate, 16e3, seed)
    left = level * np.sin(2 * np.pi * left_hz * t)
    right = level * np.sin(2 * np.pi * right_hz * t)
    wp = 2 * np.pi * 19000.0
    if stereo:
        mpx = 0.9 * ((left + right) / 2 + (left - right) / 2 * np.sin(2 * wp * t)) \
              + 0.1 * np.sin(wp * t)
    else:
        mpx = 0.9 * (left + right) / 2
    phase = 2 * np.pi * 75e3 * np.cumsum(mpx) / rate
    iq = amplitude * np.exp(1j * (phase + 2 * np.pi * offset * t))
    return _add_noise(iq, amplitude, snr_db, rate, 200e3, seed)


def _add_noise(iq, amplitude, snr_db, rate, channel_bw, seed):
    """Add white noise so the SNR holds inside one channel of width channel_bw."""
    if snr_db is not None:
        rng = np.random.default_rng(seed)
        noise_power = amplitude ** 2 / 10 ** (snr_db / 10) * (rate / channel_bw)
        n = iq.size
        iq = iq + np.sqrt(noise_power / 2) * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    return iq.astype(np.complex64)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out')
    ap.add_argument('--rate', type=float, default=2e6)
    ap.add_argument('--seconds', type=float, default=3.0)
    ap.add_argument('--left', type=float, default=1000.0, help='left tone, Hz')
    ap.add_argument('--right', type=float, default=1700.0, help='right tone, Hz')
    ap.add_argument('--mono', action='store_true')
    ap.add_argument('--offset', type=float, default=0.0, help='station offset from centre, Hz')
    ap.add_argument('--snr', type=float, default=None,
                    help='SNR in dB within one channel (200 kHz for wbfm, 16 kHz for am/nbfm)')
    ap.add_argument('--mode', choices=('wbfm', 'nbfm', 'am'), default='wbfm')
    args = ap.parse_args()
    iq = make(args.rate, args.seconds, args.left, args.right, stereo=not args.mono,
              offset=args.offset, snr_db=args.snr, mode=args.mode)
    iq.tofile(args.out)
    print(f'wrote {iq.size} samples ({iq.size / args.rate:.1f} s at {args.rate / 1e6:g} MSPS) to {args.out}')
    kind = args.mode if args.mode != 'wbfm' else ('mono' if args.mono else 'stereo')
    print(f'  {kind}: left {args.left:g} Hz, right {args.right:g} Hz, '
          f'offset {args.offset:g} Hz, SNR {args.snr if args.snr is not None else "infinite"}')


if __name__ == '__main__':
    main()
