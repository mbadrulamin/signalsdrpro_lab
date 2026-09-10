#!/usr/bin/env python3
"""
simulate_adsb_decode.py - Generate a synthetic 1090 MHz ADS-B capture and
prove the decoding chain of Lab 09 against frames whose contents are known.

What it does:

  --selftest    Decode four canonical Mode S reference frames taken from the
                published literature and check every field: CRC-24, ICAO
                address, callsign, altitude, velocity, and globally
                unambiguous CPR position.  No GNU Radio needed.

  (default)     Build a 2 MSPS IQ capture containing PPM-modulated DF17
                frames at random times in noise, and write it to a file for
                Lab 09's lab09_adsb_from_file.grc to decode.

  --decode      Additionally run the reference detector over the generated
                file and report the detection and CRC statistics.

Usage:
    python3 simulate_adsb_decode.py --selftest
    python3 simulate_adsb_decode.py --seconds 2 --snr 20 --out /tmp/adsb_test_2Msps_fc32.iq
    python3 simulate_adsb_decode.py --seconds 2 --snr 8 --decode

Requires: numpy.  GNU Radio is NOT required by this script.
"""
import argparse
import sys

import numpy as np

# ============================================================================
#  Mode S frame decoding.  Fundamentals 10 covers the CRC; the Lab 09 README
#  covers CPR.
# ============================================================================
import math

GEN = 0x1FFF409          # x^24+x^23+...+x^10+x^3+1  (25 bits, degree 24)
CHARSET = "#ABCDEFGHIJKLMNOPQRSTUVWXYZ##### ###############0123456789######"


def crc24(bits):
    """Remainder of the whole message (parity included) modulo GEN.
    Zero means the frame is intact -- and for DF17 the parity is plain CRC."""
    reg = 0
    for b in bits:
        reg = ((reg << 1) | b) & 0x1FFFFFF
        if reg & 0x1000000:
            reg ^= GEN
    # flush is unnecessary: the parity bits are already part of `bits`
    return reg & 0xFFFFFF


def bits_from_hex(h):
    n = len(h) * 4
    v = int(h, 16)
    return [(v >> i) & 1 for i in range(n - 1, -1, -1)]


def getbits(bits, start, length):
    v = 0
    for b in bits[start:start + length]:
        v = (v << 1) | b
    return v


def nl(lat):
    """CPR longitude-zone count for a latitude."""
    if abs(lat) >= 87.0:
        return 1
    if lat == 0:
        return 59
    try:
        return int(math.floor(2 * math.pi / math.acos(
            1 - (1 - math.cos(math.pi / 30.0)) / math.cos(math.radians(abs(lat))) ** 2)))
    except ValueError:
        return 1


def cpr_global(even, odd, even_first=True):
    """even/odd = (lat_cpr, lon_cpr) as 17-bit integers."""
    lat_e, lon_e = even[0] / 131072.0, even[1] / 131072.0
    lat_o, lon_o = odd[0] / 131072.0, odd[1] / 131072.0
    j = math.floor(59 * lat_e - 60 * lat_o + 0.5)
    rlat_e = (360.0 / 60) * ((j % 60) + lat_e)
    rlat_o = (360.0 / 59) * ((j % 59) + lat_o)
    if rlat_e >= 270:
        rlat_e -= 360
    if rlat_o >= 270:
        rlat_o -= 360
    if nl(rlat_e) != nl(rlat_o):
        return None
    if even_first:
        n = max(nl(rlat_e), 1)
        m = math.floor(lon_e * (nl(rlat_e) - 1) - lon_o * nl(rlat_e) + 0.5)
        lon = (360.0 / n) * ((m % n) + lon_e)
        lat = rlat_e
    else:
        n = max(nl(rlat_o) - 1, 1)
        m = math.floor(lon_e * (nl(rlat_o) - 1) - lon_o * nl(rlat_o) + 0.5)
        lon = (360.0 / n) * ((m % n) + lon_o)
        lat = rlat_o
    if lon >= 180:
        lon -= 360
    return lat, lon


def altitude(ac12):
    """12-bit AC field -> feet, or None."""
    if ac12 == 0:
        return None
    q = (ac12 >> 4) & 1
    if q:
        n = ((ac12 >> 5) << 4) | (ac12 & 0xF)
        return n * 25 - 1000
    return None                      # Gillham-coded, rarely seen in ADS-B


def callsign(me_bits):
    """me_bits: the 56-bit ME field as a bit list. TC 1-4."""
    s = ''.join(CHARSET[getbits(me_bits, 8 + 6 * i, 6)] for i in range(8))
    return s.replace('#', '').strip()


def decode_frame(bits):
    """bits: 112-bit list. Returns a dict, or None if the CRC fails."""
    if len(bits) != 112 or crc24(bits) != 0:
        return None
    df = getbits(bits, 0, 5)
    if df not in (17, 18):
        return {'df': df, 'icao': getbits(bits, 8, 24)}
    icao = getbits(bits, 8, 24)
    me = bits[32:88]
    tc = getbits(me, 0, 5)
    out = {'df': df, 'icao': icao, 'tc': tc}
    if 1 <= tc <= 4:
        out['type'] = 'identification'
        out['callsign'] = callsign(me)
    elif 9 <= tc <= 18:
        out['type'] = 'airborne_position'
        out['altitude_ft'] = altitude(getbits(me, 8, 12))
        out['odd'] = getbits(me, 21, 1)
        out['lat_cpr'] = getbits(me, 22, 17)
        out['lon_cpr'] = getbits(me, 39, 17)
    elif tc == 19:
        out['type'] = 'velocity'
        st = getbits(me, 5, 3)
        if st in (1, 2):
            ew_sign = getbits(me, 13, 1)
            ew = getbits(me, 14, 10) - 1
            ns_sign = getbits(me, 24, 1)
            ns = getbits(me, 25, 10) - 1
            mult = 4 if st == 2 else 1
            vx = (-ew if ew_sign else ew) * mult
            vy = (-ns if ns_sign else ns) * mult
            out['speed_kt'] = round(math.hypot(vx, vy))
            out['heading_deg'] = round((math.degrees(math.atan2(vx, vy)) + 360) % 360)
            vr_sign = getbits(me, 36, 1)
            vr = (getbits(me, 37, 9) - 1) * 64
            out['vert_rate_fpm'] = -vr if vr_sign else vr
    else:
        out['type'] = f'tc{tc}'
    return out


# ============================================================================
#  PPM signal generation at 2 MSPS
# ============================================================================
FS = 2_000_000.0
SPB = 2                            # samples per 1 us bit -> 1 per PPM half-bit
PREAMBLE_HIGH = [0, 2, 7, 9]       # pulses at 0, 1.0, 3.5, 4.5 us
PREAMBLE_LOW = [1, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15]
PREAMBLE_LEN = 16                  # 8 us
FRAME_BITS = 112
FRAME_LEN = PREAMBLE_LEN + SPB * FRAME_BITS      # 240 samples = 120 us

# Canonical reference frames (Junzi Sun, "The 1090 MHz Riddle")
REFERENCE = [
    ("8D40621D58C382D690C8AC2863A7", "airborne position, EVEN, 38000 ft"),
    ("8D40621D58C386435CC412692AD6", "airborne position, ODD,  38000 ft"),
    ("8D4840D6202CC371C32CE0576098", "identification, callsign KLM1023"),
    ("8D485020994409940838175B284F", "velocity, 159 kt, 183 deg, -832 ft/min"),
]


def frame_samples(hexmsg, amp=1.0):
    bits = bits_from_hex(hexmsg)
    s = np.zeros(PREAMBLE_LEN + SPB * len(bits))
    for i in PREAMBLE_HIGH:
        s[i] = amp
    for i, b in enumerate(bits):
        s[PREAMBLE_LEN + SPB * i + (0 if b else 1)] = amp
    return s


def build(seconds, snr_db, rate_hz=40.0, seed=0):
    rng = np.random.RandomState(seed)
    n = int(FS * seconds)
    env = np.zeros(n)
    placed = []
    for k in range(int(seconds * rate_hz)):
        h = REFERENCE[k % len(REFERENCE)][0]
        s = frame_samples(h)
        p = rng.randint(0, n - len(s) - 1)
        if any(abs(p - q) < len(s) + 20 for q, _ in placed):
            continue                                  # avoid deliberate collisions
        env[p:p + len(s)] += s
        placed.append((p, h))
    env = np.convolve(env, np.array([0.15, 0.7, 0.15]), mode='same')   # ~0.1 us edges
    iq = env.astype(np.complex64)
    sigma = np.sqrt(10 ** (-snr_db / 10.0))
    iq = iq + (sigma * (rng.randn(n) + 1j * rng.randn(n)) / np.sqrt(2)).astype(np.complex64)
    return iq.astype(np.complex64), sorted(placed)


# ============================================================================
#  Reference detector (the same algorithm as the Lab 09 Embedded Python Block)
# ============================================================================
def detect(iq, threshold=0.25, ratio=3.0):
    m = np.abs(iq).astype(np.float64)
    n = len(m) - FRAME_LEN
    hi = sum(m[i:i + n] for i in PREAMBLE_HIGH) / len(PREAMBLE_HIGH)
    lo = sum(m[i:i + n] for i in PREAMBLE_LOW) / len(PREAMBLE_LOW)
    cand = np.flatnonzero(((hi - lo) > threshold) & (hi > ratio * lo))

    frames, skip = [], -1
    for p in cand:
        if p < skip:
            continue
        d = m[p + PREAMBLE_LEN: p + FRAME_LEN]
        bits = (d[0::2] > d[1::2]).astype(np.uint8).tolist()
        if crc24(bits) != 0:
            continue
        info = decode_frame(bits)
        if info:
            frames.append((p, info))
            skip = p + FRAME_LEN
    return len(cand), frames


# ============================================================================
#  Self-test against the published reference frames
# ============================================================================
def selftest():
    ok = True
    decoded = {}
    for h, desc in REFERENCE:
        bits = bits_from_hex(h)
        rem = crc24(bits)
        info = decode_frame(bits)
        good = (rem == 0 and info is not None)
        print(f"  {h}")
        print(f"    {desc}")
        print(f"    CRC-24 remainder = 0x{rem:06X}  ", end='')
        if not good:
            ok = False; print("FAIL")
            continue
        print("ok")
        print(f"    -> {info}")
        decoded[h] = info

    e = decoded.get(REFERENCE[0][0])
    o = decoded.get(REFERENCE[1][0])
    print("\n  Field checks")
    checks = [
        ("ICAO of frame 1 is 0x40621D", e and e['icao'] == 0x40621D),
        ("altitude is 38000 ft", e and e['altitude_ft'] == 38000),
        ("callsign is KLM1023", decoded.get(REFERENCE[2][0], {}).get('callsign') == 'KLM1023'),
        ("velocity is 159 kt", decoded.get(REFERENCE[3][0], {}).get('speed_kt') == 159),
        ("vertical rate is -832 ft/min",
         decoded.get(REFERENCE[3][0], {}).get('vert_rate_fpm') == -832),
    ]
    pos = None
    if e and o:
        pos = cpr_global((e['lat_cpr'], e['lon_cpr']), (o['lat_cpr'], o['lon_cpr']), True)
        checks.append(("CPR position is 52.2572 N, 3.9194 E",
                       pos is not None and abs(pos[0] - 52.2572) < 1e-3
                       and abs(pos[1] - 3.91937) < 1e-3))
    for label, good in checks:
        print(f"    {label:<38} {'ok' if good else 'FAIL'}")
        ok = ok and good
    if pos:
        print(f"    decoded position: {pos[0]:.6f}, {pos[1]:.6f}")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--seconds', type=float, default=2.0)
    ap.add_argument('--snr', type=float, default=20.0, help='dB')
    ap.add_argument('--rate', type=float, default=40.0, help='frames per second')
    ap.add_argument('--threshold', type=float, default=0.25)
    ap.add_argument('--ratio', type=float, default=3.0)
    ap.add_argument('--out', default='/tmp/adsb_test_2Msps_fc32.iq')
    ap.add_argument('--decode', action='store_true')
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args()

    if a.selftest:
        print("\nADS-B / Mode S decoder self-test")
        print("(reference frames from the published Mode S literature)\n" + "-" * 62)
        good = selftest()
        print("-" * 62)
        print("RESULT: all checks passed\n" if good else "RESULT: FAILURES above\n")
        return 0 if good else 1

    iq, placed = build(a.seconds, a.snr, a.rate)
    iq.tofile(a.out)
    if not a.quiet:
        print(f"wrote {a.out}")
        print(f"  {len(iq):,} samples  {len(iq) * 8 / 1e6:.1f} MB  "
              f"{len(iq) / FS:.2f} s  SNR {a.snr} dB  {len(placed)} frames")
        print(f"\n  Now run:  python3 ../02_flowgraphs/lab09_adsb_receiver/lab09_adsb_from_file.py")

    if a.decode:
        ncand, frames = detect(iq, a.threshold, a.ratio)
        print(f"\nReference detector (threshold={a.threshold}, ratio={a.ratio})")
        print(f"  preamble candidates : {ncand}")
        print(f"  CRC-valid frames    : {len(frames)} / {len(placed)} transmitted")
        print(f"  rejected by CRC     : {ncand - len(frames)}  "
              f"({100 * (ncand - len(frames)) / max(ncand, 1):.0f}% of detections)")
        seen = {}
        for _, info in frames:
            seen.setdefault(info['icao'], set()).add(info.get('type'))
        for icao, types in sorted(seen.items()):
            print(f"  ICAO {icao:06X}: {', '.join(sorted(types))}")
        rate = len(frames) / max(len(placed), 1)
        print(f"\nRESULT: {100 * rate:.1f}% of transmitted frames recovered")
        return 0 if rate > 0.5 else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
