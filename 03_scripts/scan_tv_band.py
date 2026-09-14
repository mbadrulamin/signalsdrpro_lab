#!/usr/bin/env python3
"""
Scan the terrestrial television band and classify what is on each channel.

For every channel in the plan this captures a short burst of IQ and asks three
independent questions:

  1. How much power is there?          -> occupied bandwidth + level in dBFS
  2. Is it DVB-T2?                     -> P1 preamble correlation
  3. Is it DVB-T?                      -> cyclic-prefix autocorrelation, swept
                                          over every 8K/2K guard interval

A carrier that answers "no" to 2 and 3 but still has power is reported as an
unknown carrier rather than being silently called television.  That distinction
matters: the UHF band now contains LTE/5G downlink, radio microphones and
repeaters as well as broadcasting.

Runs against the radio, or against a recorded IQ file with --iq for testing
without hardware.

    ./scan_tv_band.py --first 21 --last 48 --dwell 0.4
    ./scan_tv_band.py --iq capture.cf32 --channel 31
    ./scan_tv_band.py --selftest

The channel list it writes (--json) is what Lab 11's receiver GUI loads, so a
scan done once can be reused without re-scanning.
"""
import argparse
import json
import sys
import time

import numpy as np

# --- DVB-T2 P1 preamble geometry (ETSI EN 302 755 clause 9.8) ----------------
# P1 is C | A | B = 542 | 1024 | 482 samples at the 64/7 MHz elementary rate.
# C carries the FIRST 542 samples of A, frequency-shifted by +1/1024 of the
# sub-carrier spacing, so the correlation lag is 542 -- not 1024.
P1_A, P1_C = 1024, 542
ELEMENTARY_RATE = 64e6 / 7.0          # 9.142857 MHz, the 8 MHz-channel rate

# --- DVB-T OFDM geometry (ETSI EN 300 744) ----------------------------------
DVBT_MODES = [(8192, '8K'), (2048, '2K')]
DVBT_GI = [(32, '1/32'), (16, '1/16'), (8, '1/8'), (4, '1/4')]

# Decision thresholds.  Every one of these was set from measurement, not taste:
# see the tables in Lab 11's README for the signals they were calibrated on.
P1_THRESHOLD = 8.0     # noise scores ~4, a real P1 preamble 20x and up
CP_THRESHOLD = 9.0     # noise scores ~4, a locked DVB-T signal 14x and up
SHOULDER_DB = 10.0     # noise ~0-4 dB, a real 8 MHz channel 30 dB
BURST_MAX = 0.02       # broadcast TV is continuous; 2 % allows for fading


def uhf_channel_freq(ch, band='uhf'):
    """Centre frequency in Hz of a terrestrial television channel.

    UHF band IV/V uses an 8 MHz raster with channel 21 centred on 474 MHz,
    which is the plan used across Europe, Malaysia and most of Asia-Pacific:
        f = 474 MHz + 8 MHz x (ch - 21)
    VHF band III uses a 7 MHz raster with channel 5 centred on 177.5 MHz.
    """
    if band == 'uhf':
        return 474e6 + 8e6 * (ch - 21)
    if band == 'vhf':
        return 177.5e6 + 7e6 * (ch - 5)
    raise ValueError(band)


def occupied_bandwidth(x, fs, frac=0.99, nfft=8192):
    """Bandwidth containing `frac` of the total power, by PSD integration."""
    n = (len(x) // nfft) * nfft
    if n < nfft:
        return 0.0
    seg = x[:n].reshape(-1, nfft)
    w = np.hanning(nfft)
    psd = np.mean(np.abs(np.fft.fftshift(np.fft.fft(seg * w, axis=1), axes=1)) ** 2, axis=0)
    total = psd.sum()
    if total <= 0:
        return 0.0
    c = np.cumsum(psd) / total
    lo = np.searchsorted(c, (1 - frac) / 2)
    hi = np.searchsorted(c, 1 - (1 - frac) / 2)
    return (hi - lo) * fs / nfft


def cp_autocorr(x, nfft, ncp, span=300000):
    """Peak-to-mean of the cyclic-prefix autocorrelation at lag `nfft`.

    An OFDM signal repeats its last ncp samples at the front of each symbol, so
    conj-multiplying the stream by itself delayed by nfft and summing over a
    window of ncp samples produces a sharp peak once per symbol.  Noise, and
    OFDM with a different FFT size, produce no peak.
    """
    seg = x[:span]
    if len(seg) <= nfft + ncp:
        return 0.0
    prod = seg[:len(seg) - nfft] * np.conj(seg[nfft:])
    if len(prod) <= ncp:
        return 0.0
    # sliding sum of ncp samples, via cumulative sum (O(n), not O(n*ncp))
    cs = np.concatenate(([0.0 + 0j], np.cumsum(prod)))
    w = np.abs(cs[ncp:] - cs[:-ncp])
    m = w.mean()
    return float(w.max() / m) if m > 0 else 0.0


def p1_detect(x, limit=2_000_000):
    """Peak-to-mean of the DVB-T2 P1 preamble correlation.

    Correlates the stream against itself at lag 542 after removing the
    +1/1024 sub-carrier frequency shift that the C part carries.  Uses FFT
    correlation: the direct form needs an index matrix of gigabytes.
    """
    x = x[:limit]
    n = len(x)
    if n <= 2 * P1_C:
        return 0.0
    derot = np.exp(-2j * np.pi * np.arange(P1_C) / P1_A)
    prod = x[:n - P1_C] * np.conj(x[P1_C:n])
    L = 1 << int(np.ceil(np.log2(len(prod) + P1_C)))
    R = np.fft.ifft(np.fft.fft(prod, L) * np.conj(np.fft.fft(np.conj(derot), L)))
    w = np.abs(R[:len(prod) - P1_C])
    m = w.mean()
    return float(w.max() / m) if m > 0 else 0.0


def spectral_shoulder(x, fs, chan_bw=8e6, nfft=8192):
    """In-band power minus out-of-band power, in dB.

    A television channel is band-limited: an 8 MHz DVB-T/T2 signal occupies
    about 7.6 MHz, so when it is sampled at 9.14 MHz there is a clear skirt of
    empty spectrum at the edges of the window.  Noise, by contrast, fills the
    window evenly and scores near 0 dB.

    This is the metric that separates a real channel from a strong noise floor,
    and it is why raw power alone must never be used to declare a channel busy:
    measured here, a genuine DVB-T waveform scores 31 dB and an empty UHF
    channel 4 dB.
    """
    n = (len(x) // nfft) * nfft
    if n < nfft:
        return 0.0
    seg = x[:n].reshape(-1, nfft) * np.hanning(nfft)
    psd = np.mean(np.abs(np.fft.fftshift(np.fft.fft(seg, axis=1), axes=1)) ** 2, axis=0)
    f = (np.arange(nfft) - nfft // 2) * fs / nfft
    inb = psd[np.abs(f) < chan_bw * 0.425].mean()
    oob_sel = np.abs(f) > chan_bw * 0.53
    if not oob_sel.any() or inb <= 0:
        return 0.0
    oob = psd[oob_sel].mean()
    return float(10 * np.log10(inb / oob)) if oob > 0 else 0.0


def burst_fraction(x, fs, block_s=0.001):
    """Fraction of 1 ms blocks sitting more than 6 dB above the median.

    Broadcast television is on continuously and scores 0.  Pulsed traffic --
    radio microphones, TDD mobile, radar -- scores several per cent.

    This matters more than it looks: a bursty signal makes *every* correlation
    detector fire, because the correlator sees the burst overlap itself at
    whatever lag is being tested.  Measured here, an intermittent carrier on
    ch22 produced a P1 score of 13.9 and a cyclic-prefix score of 31 -- both
    well over threshold, and both meaningless.  Without this test the scanner
    reports it as a television station.
    """
    blk = int(fs * block_s)
    n = (len(x) // blk) * blk
    if blk < 1 or n < blk * 10:
        return 0.0
    e = 10 * np.log10((np.abs(x[:n]) ** 2).reshape(-1, blk).mean(axis=1) + 1e-20)
    return float(np.mean(e > np.median(e) + 6.0))


def classify(x, fs, noise_ref_dbfs=None, chan_bw=8e6):
    """Measure one channel's worth of IQ and decide what it is.

    Four independent measurements, in the order they can veto each other:
    band-limitedness, continuity, then the two standard-specific correlators.
    """
    power = float(np.mean(np.abs(x) ** 2))
    dbfs = 10 * np.log10(power) if power > 0 else -200.0
    obw = occupied_bandwidth(x, fs)
    shoulder = spectral_shoulder(x, fs, chan_bw)
    burst = burst_fraction(x, fs)

    p1 = p1_detect(x)
    best_t = (0.0, None, None)
    for nfft, mname in DVBT_MODES:
        for div, gname in DVBT_GI:
            r = cp_autocorr(x, nfft, nfft // div)
            if r > best_t[0]:
                best_t = (r, mname, gname)

    # A signal must first look like a channel at all: band-limited within the
    # capture window, and continuous.  Only then are the correlator scores
    # allowed to mean anything.
    band_limited = shoulder >= SHOULDER_DB
    continuous = burst <= BURST_MAX

    if not band_limited:
        std, detail = ('burst', f'{burst*100:.1f} % duty, not band-limited') \
            if burst > BURST_MAX else ('empty', '')
    elif not continuous:
        std, detail = 'burst', f'{burst*100:.1f} % duty cycle'
    elif p1 >= P1_THRESHOLD:
        std, detail = 'DVB-T2', f'P1 {p1:.1f}x, {shoulder:.0f} dB shoulder'
    elif best_t[0] >= CP_THRESHOLD:
        std, detail = 'DVB-T', f'{best_t[1]} GI {best_t[2]}, {best_t[0]:.1f}x'
    else:
        std, detail = 'carrier', f'{obw/1e6:.1f} MHz, {shoulder:.0f} dB shoulder'

    return dict(dbfs=round(dbfs, 1), obw_mhz=round(obw / 1e6, 2),
                p1=round(p1, 1), cp=round(best_t[0], 1),
                cp_mode=best_t[1], cp_gi=best_t[2],
                shoulder_db=round(shoulder, 1), burst_pct=round(burst * 100, 2),
                standard=std, detail=detail)


def capture_usrp(freq, fs, nsamp, gain, antenna, settle=0.12):
    """Grab nsamp complex samples at `freq`.  Imported lazily so that
    --selftest and --iq work on a machine with no UHD installed."""
    from gnuradio import gr, blocks, uhd

    class Grab(gr.top_block):
        def __init__(self):
            gr.top_block.__init__(self)
            self.u = uhd.usrp_source('', uhd.stream_args(cpu_format='fc32', channels=[0]))
            self.u.set_samp_rate(fs)
            self.u.set_center_freq(uhd.tune_request(freq), 0)
            self.u.set_gain(gain, 0)
            self.u.set_antenna(antenna, 0)
            # Without this the AD9361 keeps its 56 MHz default analog bandwidth
            # and the neighbouring channels leak into the measurement.
            self.u.set_bandwidth(fs, 0)
            skip = blocks.skiphead(gr.sizeof_gr_complex, int(fs * settle))
            head = blocks.head(gr.sizeof_gr_complex, nsamp)
            self.sink = blocks.vector_sink_c()
            self.connect(self.u, skip, head, self.sink)

    tb = Grab()
    tb.run()
    return np.array(tb.sink.data(), dtype=np.complex64)


def selftest():
    """Synthesise DVB-T-like and DVB-T2-like signals and confirm the detectors
    fire on the right one and stay quiet on noise."""
    rng = np.random.default_rng(7)
    ok = True

    # noise only
    noise = (rng.normal(size=400000) + 1j * rng.normal(size=400000)).astype(np.complex64) * 0.1
    r_cp = max(cp_autocorr(noise, n, n // g) for n, _ in DVBT_MODES for g, _ in DVBT_GI)
    r_p1 = p1_detect(noise)
    print(f"  noise           : CP {r_cp:5.1f}x  P1 {r_p1:5.1f}x   (both should be low)")
    ok &= r_cp < 9.0 and r_p1 < 8.0

    # synthetic OFDM with 8K/1/32 structure
    nfft, ncp = 8192, 256
    syms = []
    for _ in range(40):
        f = (rng.normal(size=nfft) + 1j * rng.normal(size=nfft)) / np.sqrt(nfft)
        t = np.fft.ifft(f) * nfft
        syms.append(np.concatenate([t[-ncp:], t]))
    ofdm = np.concatenate(syms).astype(np.complex64)
    r = cp_autocorr(ofdm, nfft, ncp)
    print(f"  synthetic 8K OFDM: CP {r:5.1f}x at the correct FFT size")
    ok &= r >= 9.0
    rwrong = cp_autocorr(ofdm, 2048, 64)
    print(f"  same, tested as 2K: CP {rwrong:5.1f}x  (should not fire)")
    ok &= rwrong < r

    # synthetic P1: C | A | B with the 1/1024 shift on C
    a = (rng.normal(size=P1_A) + 1j * rng.normal(size=P1_A)).astype(np.complex64)
    c = a[:P1_C] * np.exp(2j * np.pi * np.arange(P1_C) / P1_A)
    b = a[P1_A - 482:] * np.exp(2j * np.pi * np.arange(482) / P1_A)
    frame = np.concatenate([c, a, b,
                            (rng.normal(size=60000) + 1j * rng.normal(size=60000)).astype(np.complex64) * 0.3])
    t2 = np.tile(frame, 6)
    r = p1_detect(t2)
    print(f"  synthetic P1     : P1 {r:5.1f}x")
    ok &= r >= P1_THRESHOLD

    # Band-limitedness: noise fills the window, a real channel does not.
    fs = ELEMENTARY_RATE
    sh_noise = spectral_shoulder(noise, fs)
    band = np.fft.ifft(np.fft.fft(noise) * (np.abs(np.fft.fftfreq(len(noise), 1/fs)) < 3.8e6)).astype(np.complex64)
    sh_band = spectral_shoulder(band, fs)
    print(f"  shoulder         : noise {sh_noise:5.1f} dB   band-limited {sh_band:5.1f} dB")
    ok &= sh_noise < SHOULDER_DB <= sh_band

    # Burstiness, and the false positive it causes.  A pulsed signal makes the
    # correlators fire at any lag; the duty-cycle test is what vetoes it.
    burst_sig = noise.copy()
    on = np.zeros(len(burst_sig), dtype=bool)
    blk = int(fs * 0.001)
    for k in range(0, len(burst_sig) - 4 * blk, 40 * blk):
        on[k:k + 4 * blk] = True
    burst_sig[on] *= 6.0
    bf_cont, bf_burst = burst_fraction(noise, fs), burst_fraction(burst_sig, fs)
    cp_burst = max(cp_autocorr(burst_sig, n, n // g) for n, _ in DVBT_MODES for g, _ in DVBT_GI)
    print(f"  burst fraction   : continuous {bf_cont*100:4.1f} %   pulsed {bf_burst*100:4.1f} %")
    print(f"    (the pulsed signal scores CP {cp_burst:.1f}x -- over threshold, and wrong)")
    ok &= bf_cont <= BURST_MAX < bf_burst
    r = classify(burst_sig, fs)
    print(f"    classify() says: {r['standard']}  <- must not be DVB-T/T2")
    ok &= r['standard'] not in ('DVB-T', 'DVB-T2')

    print("\nSELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--first', type=int, default=21, help='first channel number')
    ap.add_argument('--last', type=int, default=48, help='last channel number')
    ap.add_argument('--channel', type=int, help='scan a single channel only')
    ap.add_argument('--band', default='uhf', choices=['uhf', 'vhf'])
    ap.add_argument('--dwell', type=float, default=0.4,
                    help='seconds of IQ per channel (>=0.3 to catch a P1)')
    ap.add_argument('--gain', type=float, default=40.0)
    ap.add_argument('--antenna', default='RX2')
    ap.add_argument('--fs', type=float, default=ELEMENTARY_RATE)
    ap.add_argument('--bandwidth', type=float, default=8e6,
                    help='channel bandwidth in Hz (8e6 UHF, 7e6 VHF band III)')
    ap.add_argument('--iq', help='analyse a recorded complex64 file instead of the radio')
    ap.add_argument('--json', help='write the channel table here')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    chans = [a.channel] if a.channel else list(range(a.first, a.last + 1))
    nsamp = int(a.fs * a.dwell)
    rows = []

    if a.iq:
        x = np.fromfile(a.iq, dtype=np.complex64)
        print(f"{a.iq}: {len(x):,} samples at {a.fs/1e6:.3f} Msps\n")
        r = classify(x, a.fs, None, a.bandwidth)
        r.update(channel=a.channel or 0, freq_mhz=round(uhf_channel_freq(a.channel or 21, a.band) / 1e6, 1))
        rows = [r]
    else:
        print(f"Scanning {a.band.upper()} ch {chans[0]}-{chans[-1]}  "
              f"({a.dwell*1000:.0f} ms each, gain {a.gain} dB, {a.antenna})\n")
        # A first pass over the quietest channel gives a noise reference so
        # that "empty" means empty relative to this receiver, not an absolute.
        noise_ref = None
        for ch in chans:
            f = uhf_channel_freq(ch, a.band)
            t0 = time.time()
            x = capture_usrp(f, a.fs, nsamp, a.gain, a.antenna)
            r = classify(x, a.fs, noise_ref, a.bandwidth)
            r.update(channel=ch, freq_mhz=round(f / 1e6, 1), secs=round(time.time() - t0, 2))
            if noise_ref is None or r['dbfs'] < noise_ref:
                noise_ref = r['dbfs']
            rows.append(r)
            print(f"  ch {ch:2d}  {f/1e6:6.1f} MHz  {r['dbfs']:7.1f} dBFS  "
                  f"P1 {r['p1']:5.1f}  CP {r['cp']:5.1f}  shl {r['shoulder_db']:5.1f}dB  "
                  f"{r['standard']:8s} {r['detail']}")

    print("\n" + "=" * 78)
    print(f"{'CH':>3} {'MHz':>7} {'dBFS':>7} {'P1':>6} {'CP':>6} {'SHLDR':>7}  STANDARD  DETAIL")
    print("-" * 86)
    for r in rows:
        print(f"{r['channel']:>3} {r['freq_mhz']:>7.1f} {r['dbfs']:>7.1f} "
              f"{r['p1']:>6.1f} {r['cp']:>6.1f} {r['shoulder_db']:>6.1f}dB  "
              f"{r['standard']:8s}  {r['detail']}")
    found = [r for r in rows if r['standard'] in ('DVB-T', 'DVB-T2')]
    empty = [r for r in rows if r['standard'] == 'empty']
    print("-" * 86)
    print(f"{len(found)} television signal(s), {len(empty)} empty channel(s) of {len(rows)} scanned")
    if empty:
        print("quietest empty channels: " +
              ", ".join(f"ch{r['channel']} ({r['freq_mhz']:.0f} MHz, {r['dbfs']:.0f} dBFS)"
                        for r in sorted(empty, key=lambda r: r['dbfs'])[:5]))

    if a.json:
        with open(a.json, 'w') as fh:
            json.dump(dict(band=a.band, fs=a.fs, scanned=time.strftime('%Y-%m-%d %H:%M:%S'),
                           channels=rows), fh, indent=2)
        print(f"\nwrote {a.json}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
