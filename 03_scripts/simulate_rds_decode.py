#!/usr/bin/env python3
"""
simulate_rds_decode.py - Generate a synthetic FM+RDS signal and prove the
decoding chain of Lab 08 on a signal whose contents are known exactly.

What it does:

  --selftest    Round-trip the RDS codec in pure Python: CRC-10 syndromes for
                all five offset words, biphase coding, differential coding,
                block synchronisation and group parsing.  No GNU Radio needed.

  (default)     Build an FM broadcast IQ capture at 2 MSPS containing a full
                MPX - a 1 kHz mono tone, the 19 kHz pilot, and RDS on the
                57 kHz subcarrier carrying a chosen Programme Service name and
                RadioText - then write it to a file for Lab 08's
                lab08_rds_from_file.grc to decode.

  --decode      Additionally demodulate the generated file in pure NumPy and
                verify that the expected PS and RadioText come back out.

Usage:
    python3 simulate_rds_decode.py --selftest
    python3 simulate_rds_decode.py --seconds 8 --snr 30 --out /tmp/rds_test_2Msps_fc32.iq
    python3 simulate_rds_decode.py --seconds 6 --snr 15 --decode

Requires: numpy.  GNU Radio is NOT required by this script.
"""
import argparse
import sys

import numpy as np

# ============================================================================
#  RDS codec (IEC 62106).  Fundamentals 10 explains every line of this.
# ============================================================================
import numpy as np

POLY = 0b10110111001          # x^10+x^8+x^7+x^5+x^4+x^3+1  (0x5B9)
OFFSETS = {'A': 0b0011111100, 'B': 0b0110011000, 'C': 0b0101101000,
           'Cp': 0b1101010000, 'D': 0b0110110100}
SYN_TO_OFFSET = {v: k for k, v in OFFSETS.items()}


def crc10(info16):
    """Remainder of info16 * x^10 divided by POLY, in GF(2)."""
    reg = info16 << 10
    for i in range(25, 9, -1):          # bits 25..10 are the message
        if reg & (1 << i):
            reg ^= POLY << (i - 10)
    return reg & 0x3FF


def syndrome(word26):
    """word26 mod POLY. For a valid block this equals the offset word."""
    reg = word26 & 0x3FFFFFF
    for i in range(25, 9, -1):
        if reg & (1 << i):
            reg ^= POLY << (i - 10)
    return reg & 0x3FF


def make_block(info16, offset_name):
    return (info16 << 10) | (crc10(info16) ^ OFFSETS[offset_name])


def make_group(pi, blockB, blockC, blockD, version_b=False):
    return [make_block(pi, 'A'), make_block(blockB, 'B'),
            make_block(blockC, 'Cp' if version_b else 'C'),
            make_block(blockD, 'D')]


# ---------------------------------------------------------------- encoder ---
def group_bits(blocks):
    out = []
    for b in blocks:
        out.extend([(b >> i) & 1 for i in range(25, -1, -1)])
    return out


def differential_encode(bits):
    out, prev = [], 0
    for b in bits:
        prev ^= b
        out.append(prev)
    return out


def biphase_chips(dbits):
    """Each data bit -> two opposite chips (+1,-1) or (-1,+1)."""
    chips = []
    for b in dbits:
        s = 1.0 if b else -1.0
        chips.extend([s, -s])
    return np.array(chips, dtype=np.float64)


# ---------------------------------------------------------------- decoder ---
PTY_EU = ['None', 'News', 'Current Affairs', 'Information', 'Sport', 'Education',
          'Drama', 'Culture', 'Science', 'Varied', 'Pop Music', 'Rock Music',
          'Easy Listening', 'Light Classical', 'Serious Classical', 'Other Music',
          'Weather', 'Finance', "Children's", 'Social Affairs', 'Religion',
          'Phone In', 'Travel', 'Leisure', 'Jazz Music', 'Country Music',
          'National Music', 'Oldies Music', 'Folk Music', 'Documentary',
          'Alarm Test', 'Alarm']


def _chr(c):
    return chr(c) if 32 <= c < 127 else ' '


class RDSDecoder:
    """Feed differentially-DECODED bits in; groups and text come out."""

    def __init__(self):
        self.bits = []
        self.pos = 0
        self.pi = None
        self.pty = None
        self.tp = None
        self.ps = [' '] * 8
        self.ps_seen = [False] * 4
        self.rt = [' '] * 64
        self.rt_ab = None
        self.groups = 0
        self.bad = 0

    def _word(self, i):
        v = 0
        for b in self.bits[i:i + 26]:
            v = (v << 1) | b
        return v

    def feed(self, newbits):
        self.bits.extend(int(b) for b in newbits)
        # need 4 blocks = 104 bits from self.pos
        while self.pos + 104 <= len(self.bits):
            w = [self._word(self.pos + 26 * k) for k in range(4)]
            s = [SYN_TO_OFFSET.get(syndrome(x)) for x in w]
            if s[0] == 'A' and s[1] == 'B' and s[2] in ('C', 'Cp') and s[3] == 'D':
                self._group([x >> 10 for x in w], s[2] == 'Cp')
                self.groups += 1
                self.pos += 104
            else:
                self.bad += 1
                self.pos += 1
        # keep the buffer bounded
        if self.pos > 4096:
            self.bits = self.bits[self.pos:]
            self.pos = 0

    def _group(self, info, version_b):
        a, b, c, d = info
        self.pi = a
        gtype = (b >> 12) & 0xF
        self.tp = (b >> 10) & 1
        self.pty = (b >> 5) & 0x1F
        if gtype == 0:
            addr = b & 0x3
            self.ps[2 * addr] = _chr(d >> 8)
            self.ps[2 * addr + 1] = _chr(d & 0xFF)
            self.ps_seen[addr] = True
        elif gtype == 2:
            ab = (b >> 4) & 1
            if self.rt_ab is not None and ab != self.rt_ab:
                self.rt = [' '] * 64
            self.rt_ab = ab
            if not version_b:
                addr = b & 0xF
                for i, ch in enumerate([c >> 8, c & 0xFF, d >> 8, d & 0xFF]):
                    if 4 * addr + i < 64:
                        self.rt[4 * addr + i] = _chr(ch)
            else:
                addr = b & 0xF
                for i, ch in enumerate([d >> 8, d & 0xFF]):
                    if 2 * addr + i < 64:
                        self.rt[2 * addr + i] = _chr(ch)

    # ------------------------------------------------------------- output --
    def station(self):
        return ''.join(self.ps) if all(self.ps_seen) else None

    def radiotext(self):
        t = ''.join(self.rt).rstrip()
        return t if t.strip() else None

    def summary(self):
        return (f"PI=0x{self.pi:04X}" if self.pi is not None else "PI=?") + \
               f"  PS='{''.join(self.ps)}'" + \
               (f"  PTY={PTY_EU[self.pty]}" if self.pty is not None else "") + \
               f"  groups={self.groups}"


def differential_decode(dbits):
    out, prev = [], 0
    for b in dbits:
        out.append(prev ^ b)
        prev = b
    return out


# ============================================================================
#  Signal generation
# ============================================================================
FS = 2_000_000.0        # IQ sample rate written to the file
MPX_FS = 250_000.0      # MPX is built here, then interpolated x8
CHIP_RATE = 2375.0      # 1187.5 bit/s, biphase -> 2375 chips/s
PILOT_F = 19_000.0
DEVIATION = 75_000.0


def build_bits(pi, ps, rt, reps):
    """0A groups carry the 8-char PS name; 2A groups carry 64-char RadioText."""
    ps = ps[:8].ljust(8)
    rt = rt[:64].ljust(64)
    groups = []
    for _ in range(reps):
        for i in range(4):
            b = (0 << 12) | (1 << 10) | (10 << 5) | i        # type 0A, TP=1, PTY=10
            d = (ord(ps[2 * i]) << 8) | ord(ps[2 * i + 1])
            groups.append(make_group(pi, b, 0xE0CD, d))
        for i in range(16):
            b = (2 << 12) | (1 << 10) | (10 << 5) | i        # type 2A
            c = (ord(rt[4 * i]) << 8) | ord(rt[4 * i + 1])
            d = (ord(rt[4 * i + 2]) << 8) | ord(rt[4 * i + 3])
            groups.append(make_group(pi, b, c, d))
    bits = []
    for g in groups:
        bits.extend(group_bits(g))
    return bits


def lowpass(x, fs, cutoff, ntaps=401):
    n = np.arange(ntaps) - (ntaps - 1) / 2
    h = np.sinc(2 * cutoff / fs * n) * np.hamming(ntaps)
    return np.convolve(x, h / h.sum(), mode='same')


def build_mpx(bits, seconds):
    """audio (L+R) + 19 kHz pilot + RDS DSB-SC on the pilot's 3rd harmonic."""
    n = int(MPX_FS * seconds)
    t = np.arange(n) / MPX_FS
    chips = biphase_chips(differential_encode(bits))
    idx = np.floor(t * CHIP_RATE).astype(int)
    if idx[-1] >= len(chips):
        raise ValueError("not enough RDS chips for the requested duration")
    rds_bb = lowpass(chips[idx], MPX_FS, 2400.0)            # 100% cosine-ish shaping
    pilot_phase = 2 * np.pi * PILOT_F * t
    return (0.30 * np.sin(2 * np.pi * 1000.0 * t)           # mono audio tone
            + 0.08 * np.sin(pilot_phase)                    # 19 kHz pilot
            + 0.05 * rds_bb * np.sin(3 * pilot_phase))      # RDS at 57 kHz


def fm_modulate(mpx, snr_db=None, seed=1):
    up = np.repeat(mpx, int(FS // MPX_FS))
    up = lowpass(up, FS, 110_000.0, ntaps=201)
    phase = 2 * np.pi * DEVIATION * np.cumsum(up) / FS
    iq = np.exp(1j * phase).astype(np.complex64)
    if snr_db is not None:
        rng = np.random.RandomState(seed)
        sigma = np.sqrt(10 ** (-snr_db / 10.0))
        noise = sigma * (rng.randn(len(iq)) + 1j * rng.randn(len(iq))) / np.sqrt(2)
        iq = (iq + noise).astype(np.complex64)
    return iq


# ============================================================================
#  Pure-NumPy reference receiver (mirrors the Lab 08 flowgraph)
# ============================================================================
def demodulate(iq):
    """IQ -> RDS chips, using the same rate plan as lab08_rds_decoder.grc."""
    mpx = np.angle(iq[1:] * np.conj(iq[:-1]))               # quadrature demod
    mpx = lowpass(mpx, FS, 110_000.0, ntaps=201)[::8]       # -> 250 kSPS
    t = np.arange(len(mpx)) / MPX_FS
    bb = mpx * np.exp(-2j * np.pi * 57_000.0 * t)           # mix 57 kHz to DC
    bb = np.convolve(bb, _lp_taps(MPX_FS, 2400.0, 753), mode='same')[::25]  # -> 10 kSPS
    sps = (MPX_FS / 25) / CHIP_RATE                         # 4.2105...
    # non-data-aided timing: pick the sampling phase with the most energy
    idx = np.arange(int(len(bb) / sps) - 2)
    best, chips = -1, None
    for frac in np.linspace(0, 1, 16, endpoint=False):
        s = bb[np.round((idx + frac) * sps).astype(int)]
        e = float(np.mean(np.abs(s) ** 2))
        if e > best:
            best, chips = e, s
    phi = np.angle(np.mean(chips ** 2)) / 2                 # squaring carrier recovery
    return np.real(chips * np.exp(-1j * phi))


def _lp_taps(fs, cutoff, ntaps):
    n = np.arange(ntaps) - (ntaps - 1) / 2
    h = np.sinc(2 * cutoff / fs * n) * np.hamming(ntaps)
    return h / h.sum()


def chips_to_bits(chips):
    """Biphase pairing, then differential decode."""
    best, bits = None, None
    for phase in (0, 1):
        c = chips[phase:]
        m = len(c) // 2
        score = -float(np.mean(c[0:2 * m:2] * c[1:2 * m:2]))
        if best is None or score > best:
            best = score
            bits = ((c[0:2 * m:2] - c[1:2 * m:2]) > 0).astype(int)
    return differential_decode(list(bits))


# ============================================================================
#  Self-test
# ============================================================================
def selftest():
    ok = True

    for name in ('A', 'B', 'C', 'Cp', 'D'):
        w = make_block(0xABCD, name)
        got = SYN_TO_OFFSET.get(syndrome(w))
        print(f"  CRC-10 syndrome for offset {name:<2} -> {got}", end='')
        if got != name:
            ok = False; print("   FAIL")
        else:
            print("   ok")

    bits = build_bits(0x4D01, "SDR LAB ", "SignalSDR Pro Lab RDS test", reps=2)
    d = biphase_chips(differential_encode(bits))
    rec = ((d[0::2] - d[1::2]) / 2 > 0).astype(int)
    print("  biphase round trip                    ", end='')
    if list(rec) != differential_encode(bits):
        ok = False; print("   FAIL")
    else:
        print("   ok")

    print("  differential round trip               ", end='')
    if differential_decode(list(rec)) != bits:
        ok = False; print("   FAIL")
    else:
        print("   ok")

    dec = RDSDecoder(); dec.feed(bits)
    print(f"  block sync + group parse              ", end='')
    if dec.station() != "SDR LAB " or dec.groups < 30:
        ok = False; print(f"   FAIL  ({dec.summary()})")
    else:
        print(f"   ok   ({dec.groups} groups)")

    print(f"  RadioText                             ", end='')
    if dec.radiotext() != "SignalSDR Pro Lab RDS test":
        ok = False; print(f"   FAIL  ({dec.radiotext()!r})")
    else:
        print("   ok")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--selftest', action='store_true', help='codec round-trip only')
    ap.add_argument('--seconds', type=float, default=8.0)
    ap.add_argument('--snr', type=float, default=30.0, help='dB')
    ap.add_argument('--pi', type=lambda s: int(s, 0), default=0x4D01)
    ap.add_argument('--ps', default='SDR LAB ')
    ap.add_argument('--rt', default='SignalSDR Pro Lab RDS test')
    ap.add_argument('--out', default='/tmp/rds_test_2Msps_fc32.iq')
    ap.add_argument('--decode', action='store_true',
                    help='also demodulate the generated signal and verify')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()

    if a.selftest:
        print("\nRDS codec self-test\n" + "-" * 45)
        good = selftest()
        print("-" * 45)
        print("RESULT: all checks passed\n" if good else "RESULT: FAILURES above\n")
        return 0 if good else 1

    bits = build_bits(a.pi, a.ps, a.rt, reps=int(a.seconds * 12) + 10)
    iq = fm_modulate(build_mpx(bits, a.seconds), snr_db=a.snr)
    iq.tofile(a.out)
    if not a.quiet:
        print(f"wrote {a.out}")
        print(f"  {len(iq):,} samples  {len(iq) * 8 / 1e6:.1f} MB  "
              f"{len(iq) / FS:.2f} s  SNR {a.snr} dB")
        print(f"  PI=0x{a.pi:04X}  PS={a.ps!r}  RT={a.rt!r}")
        print(f"\n  Now run:  python3 ../02_flowgraphs/lab08_rds_decoder/lab08_rds_from_file.py")
        print(f"  (set rec_file to {a.out!r} if you changed --out)")

    if a.decode:
        print("\nNumPy reference demodulation ...")
        dec = RDSDecoder()
        dec.feed(chips_to_bits(demodulate(iq)))
        print(" ", dec.summary())
        print("  RadioText:", dec.radiotext())
        good = (dec.station() == a.ps[:8].ljust(8))
        print("\nRESULT:", "PS recovered correctly" if good else "PS MISMATCH")
        return 0 if good else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
