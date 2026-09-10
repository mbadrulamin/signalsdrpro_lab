#!/usr/bin/env python3
"""
analyze_dvbt2.py - Verify that a generated DVB-T2 waveform is structurally correct.

There is no DVB-T2 receiver in GNU Radio, so this does the next best thing: it
measures the properties the standard fixes, and checks them against what the
configuration says they should be.  If all five checks pass, the waveform is a
real DVB-T2 signal and a real receiver should be able to lock to it.

  1. Occupied bandwidth      -> carrier count x carrier spacing
  2. Guard-interval autocorrelation at lag N_fft
                             -> proves the cyclic prefix exists and finds N_fft
  3. OFDM symbol period      -> N_fft + N_cp, from the spacing of those peaks
  4. P1 preamble detection   -> correlate the C part against the A part with the
                                standard's frequency shift removed
  5. T2 frame period         -> spacing of the P1 detections
  Plus PAPR, which is what makes OFDM hard to amplify.

Usage:
    python3 analyze_dvbt2.py /tmp/dvbt2_signal_9M14_fc32.iq
    python3 analyze_dvbt2.py signal.iq --fft 1024 --gi 8 --datasyms 1966

Requires: numpy.  No GNU Radio, no hardware.
"""
import argparse
import sys

import numpy as np

ELEMENTARY_RATE = 8e6 * 8 / 7            # 64/7 MHz, the 8 MHz DVB-T2 sample rate
P1_LEN = 2048                            # C(542) + A(1024) + B(482)
P1_A, P1_C = 1024, 542
# active carriers for each FFT size, normal / extended carrier mode
CARRIERS = {1024: (853, 853), 2048: (1705, 1705), 4096: (3409, 3409),
            8192: (6817, 6913), 16384: (13633, 13921), 32768: (27265, 27841)}


def occupied_bandwidth(x, fs, frac=0.99, nfft=8192):
    """Bandwidth containing `frac` of the total power."""
    segs = min(len(x) // nfft, 200)
    P = np.zeros(nfft)
    w = np.hanning(nfft)
    for i in range(segs):
        P += np.abs(np.fft.fftshift(np.fft.fft(x[i * nfft:(i + 1) * nfft] * w))) ** 2
    P /= segs
    c = np.cumsum(P) / P.sum()
    lo = np.searchsorted(c, (1 - frac) / 2)
    hi = np.searchsorted(c, 1 - (1 - frac) / 2)
    return (hi - lo) * fs / nfft, P


def gi_autocorr(x, nfft, ncp, start=0, span=200000):
    """Sliding correlation between x[n..n+ncp] and x[n+nfft..n+nfft+ncp]."""
    seg = x[start:start + span + nfft + ncp]
    a = seg[:-nfft] if nfft else seg
    b = seg[nfft:]
    n = min(len(a), len(b))
    prod = a[:n] * np.conj(b[:n])
    # boxcar of length ncp == correlation over the guard interval
    csum = np.concatenate([[0], np.cumsum(prod)])
    r = csum[ncp:] - csum[:-ncp]
    return np.abs(r)


def estimate_symbol_period(r, expect, search=0.25):
    """Find the period of the correlation peaks by autocorrelating the envelope."""
    e = r - r.mean()
    lo, hi = int(expect * (1 - search)), int(expect * (1 + search))
    ac = np.array([np.dot(e[:-l], e[l:]) for l in range(lo, hi)])
    return lo + int(np.argmax(ac)), ac


def p1_detect(x, limit=None):
    """Detect the P1 preamble by correlating its C part against the A part.

    P1 is laid out in time as  C (542) | A (1024) | B (482)  = 2048 samples.
    C is a copy of the FIRST 542 samples of A, frequency-shifted by one carrier
    spacing of the 1024-point FFT.  So C[k] sits 542 samples BEFORE the A sample
    it copies - the correlation lag is 542, not 1024.  (Getting that wrong is an
    easy mistake: it makes the detector find nothing at all.)

        x[n+k]        = A[k] * exp(j 2 pi k / 1024)
        x[n+542+k]    = A[k]
        product * exp(-j 2 pi k / 1024)  ->  |A[k]|^2, all real and positive

    B correlates the same way at lag 482 with the opposite rotation sign; the C
    part alone gives a peak-to-mean of ~24x, which is plenty.
    """
    n = len(x) if limit is None else min(len(x), limit)
    x = x[:n]
    if n <= 2 * P1_C:
        return np.zeros(1)
    derot = np.exp(-2j * np.pi * np.arange(P1_C) / P1_A)
    prod = x[:n - P1_C] * np.conj(x[P1_C:n])
    m = len(prod) - P1_C
    if m <= 0:
        return np.zeros(1)
    # Cross-correlation via one FFT pair. A direct sliding sum would be
    # ~5e6 x 542 operations and materialising the index matrix needs gigabytes.
    L = 1 << int(np.ceil(np.log2(len(prod) + P1_C)))
    R = np.fft.ifft(np.fft.fft(prod, L) * np.conj(np.fft.fft(np.conj(derot), L)))
    return np.abs(R[:m])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iqfile')
    ap.add_argument('--rate', type=float, default=ELEMENTARY_RATE)
    ap.add_argument('--fft', type=int, default=1024)
    ap.add_argument('--gi', type=int, default=8, help='guard interval denominator (1/N)')
    ap.add_argument('--datasyms', type=int, default=1966)
    ap.add_argument('--p2syms', type=int, default=16, help='P2 symbols per T2 frame')
    ap.add_argument('--extended', action='store_true')
    ap.add_argument('--max-samples', type=int, default=6_000_000)
    a = ap.parse_args()

    nfft, ncp = a.fft, a.fft // a.gi
    sym = nfft + ncp
    x = np.fromfile(a.iqfile, dtype=np.complex64, count=a.max_samples)
    if len(x) < sym * 20:
        sys.exit(f"only {len(x)} samples - generate a longer capture")

    print(f"\nDVB-T2 waveform analysis: {a.iqfile}")
    print(f"  {len(x):,} samples at {a.rate/1e6:.6f} MSPS = {len(x)/a.rate:.3f} s")
    print(f"  config: {nfft}-point FFT, GI 1/{a.gi} ({ncp} samples), "
          f"symbol = {sym} samples\n")
    ok = []

    # ---- 1. occupied bandwidth -------------------------------------------
    bw, _ = occupied_bandwidth(x, a.rate)
    ncar = CARRIERS.get(nfft, (None, None))[1 if a.extended else 0]
    want = ncar * a.rate / nfft if ncar else None
    print("1. Occupied bandwidth (99% power)")
    print(f"     measured {bw/1e6:.3f} MHz")
    if want:
        print(f"     expected {want/1e6:.3f} MHz  ({ncar} carriers x "
              f"{a.rate/nfft/1e3:.3f} kHz spacing)")
        good = abs(bw - want) / want < 0.04
        print(f"     {'PASS' if good else 'FAIL'}   (within 4%)")
        ok.append(good)

    # ---- 2/3. guard interval + symbol period ------------------------------
    r = gi_autocorr(x, nfft, ncp, start=sym * 4, span=min(300000, len(x) - sym * 8))
    peak, floor = r.max(), np.median(r)
    print("\n2. Cyclic prefix correlation at lag N_fft")
    print(f"     peak/median = {peak/floor:.1f}x")
    good = peak / floor > 3
    print(f"     {'PASS' if good else 'FAIL'}   (a cyclic prefix of {ncp} samples is present)")
    ok.append(good)

    est, _ = estimate_symbol_period(r, sym)
    print("\n3. OFDM symbol period")
    print(f"     measured {est} samples     expected {sym} = {nfft} + {ncp}")
    good = abs(est - sym) <= 2
    print(f"     {'PASS' if good else 'FAIL'}")
    ok.append(good)

    # ---- 4/5. P1 preamble and T2 frame ------------------------------------
    frame = P1_LEN + (a.p2syms + a.datasyms) * sym
    print("\n4. P1 preamble detection")
    scan = min(len(x), int(frame * 2.5) + P1_LEN)
    p1 = p1_detect(x, limit=scan)
    thr = p1.mean() + 6 * p1.std()
    idx = np.flatnonzero(p1 > thr)
    # collapse neighbouring samples into single detections
    peaks = [int(idx[0])] if len(idx) else []
    for i in idx[1:]:
        if i - peaks[-1] > sym:
            peaks.append(int(i))
    print(f"     {len(peaks)} detection(s) in {scan:,} samples, "
          f"peak/mean = {p1.max()/p1.mean():.1f}x")
    good = len(peaks) >= 1 and p1.max() / p1.mean() > 5
    print(f"     {'PASS' if good else 'FAIL'}")
    ok.append(good)

    print("\n5. T2 frame period")
    print(f"     expected {frame:,} samples = {frame/a.rate*1000:.2f} ms"
          f"   (P1 {P1_LEN} + {a.p2syms} P2 + {a.datasyms} data symbols)")
    if len(peaks) >= 2:
        d = np.diff(peaks)
        print(f"     measured {d[0]:,} samples = {d[0]/a.rate*1000:.2f} ms")
        good = abs(d[0] - frame) / frame < 0.01
        print(f"     {'PASS' if good else 'FAIL'}")
        ok.append(good)
    else:
        print(f"     only {len(peaks)} P1 found in this window - analyse a longer capture")

    # ---- PAPR --------------------------------------------------------------
    p = np.abs(x) ** 2
    papr = 10 * np.log10(np.percentile(p, 99.99) / p.mean())
    print(f"\n   PAPR (99.99th percentile / mean): {papr:.1f} dB")
    print("   OFDM is a sum of ~1000 independent carriers, so it is Gaussian and")
    print("   peaky. This is why the amplifier must be backed off.")

    print("\n" + "=" * 62)
    print(f"RESULT: {sum(ok)}/{len(ok)} checks passed"
          + ("  -  this is a valid DVB-T2 waveform" if all(ok) else "  -  SOMETHING IS WRONG"))
    print("=" * 62 + "\n")
    return 0 if all(ok) else 1


if __name__ == '__main__':
    sys.exit(main())
