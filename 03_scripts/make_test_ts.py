#!/usr/bin/env python3
"""Generate a standards-valid MPEG-2 Transport Stream for DVB-T2 testing.

Produces PAT / PMT / SDT / NIT tables plus null stuffing at an exact constant
mux rate.  A real DVB-T2 receiver (TV or USB tuner) will lock to the resulting
carrier, find the service, and display its name in the channel list.

It carries no video: generating a compliant MPEG-2 or H.264 elementary stream
from scratch is a different project.  For a picture, use ffmpeg (see --help).
"""
import argparse, struct, sys

PKT = 188
SYNC = 0x47
PID_PAT, PID_SDT, PID_NIT, PID_NULL = 0x0000, 0x0011, 0x0010, 0x1FFF
PID_PMT, PID_VIDEO, PID_PCR = 0x1000, 0x1001, 0x1001


def crc32_mpeg(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for b in data:
        crc ^= b << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc


def section(table_id, ext_id, payload, version=0, section_no=0, last_no=0,
            private=False):
    """Build a PSI section with its CRC-32."""
    body = struct.pack('>HBBB', ext_id, 0xC0 | (version << 1) | 1, section_no, last_no) + payload
    length = len(body) + 4                       # + CRC
    syntax = 0xB0 if not private else 0xF0
    head = struct.pack('>BH', table_id, (syntax << 8) | length)
    s = head + body
    return s + struct.pack('>I', crc32_mpeg(s))


def packetise(pid, payload, cc, pusi=True):
    """Wrap one section into a 188-byte TS packet (pointer_field + payload)."""
    data = (b'\x00' + payload) if pusi else payload
    if len(data) > PKT - 4:
        raise ValueError('section too large for one packet')
    hdr = struct.pack('>BHB', SYNC, ((0x40 if pusi else 0) << 8) | pid, 0x10 | (cc & 0x0F))
    return hdr + data + b'\xFF' * (PKT - 4 - len(data))


def null_packet():
    return struct.pack('>BHB', SYNC, PID_NULL, 0x10) + b'\xFF' * (PKT - 4)


def build_pat(ts_id, prog_no):
    return section(0x00, ts_id, struct.pack('>HH', prog_no, 0xE000 | PID_PMT))


def build_pmt(prog_no):
    # stream_type 0x02 = MPEG-2 video
    es = struct.pack('>BHH', 0x02, 0xE000 | PID_VIDEO, 0xF000)
    return section(0x02, prog_no, struct.pack('>HH', 0xE000 | PID_PCR, 0xF000) + es)


def build_sdt(ts_id, net_id, prog_no, provider, name):
    prov, nam = provider.encode()[:255], name.encode()[:255]
    desc = struct.pack('>BBB', 0x48, 3 + len(prov) + len(nam), 0x01) + \
           bytes([len(prov)]) + prov + bytes([len(nam)]) + nam
    svc = struct.pack('>HBH', prog_no, 0xFC, 0x8000 | len(desc)) + desc
    return section(0x42, ts_id, struct.pack('>HB', net_id, 0xFF) + svc, private=True)


def build_nit(net_id, name):
    nam = name.encode()[:255]
    net_desc = struct.pack('>BB', 0x40, len(nam)) + nam
    payload = struct.pack('>H', 0xF000 | len(net_desc)) + net_desc + struct.pack('>H', 0xF000)
    return section(0x40, net_id, payload, private=True)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
For a stream that actually shows a picture, use ffmpeg instead:

  ffmpeg -f lavfi -i testsrc2=size=720x576:rate=25 \\
         -f lavfi -i sine=frequency=1000 \\
         -c:v mpeg2video -b:v 3000k -c:a mp2 -b:a 192k \\
         -muxrate 4000000 -f mpegts -t 60 test.ts

The -muxrate must match the --rate you would pass here.
""")
    ap.add_argument('--out', default='test.ts')
    ap.add_argument('--seconds', type=float, default=10.0)
    ap.add_argument('--rate', type=float, default=4e6, help='mux rate in bit/s')
    ap.add_argument('--name', default='SDR LAB TV')
    ap.add_argument('--provider', default='SignalSDR Pro Lab')
    ap.add_argument('--network', default='SDR LAB NET')
    ap.add_argument('--ts-id', type=int, default=1)
    ap.add_argument('--net-id', type=int, default=1)
    ap.add_argument('--program', type=int, default=1)
    a = ap.parse_args()

    total = int(a.rate * a.seconds / 8 / PKT)
    # DVB requires PAT/PMT at least every 100 ms, SDT/NIT every 2 s
    pps = a.rate / 8 / PKT                                   # packets per second
    iv_pat = max(1, int(pps * 0.050))
    iv_sdt = max(1, int(pps * 0.500))
    cc = {PID_PAT: 0, PID_PMT: 0, PID_SDT: 0, PID_NIT: 0}
    pat = build_pat(a.ts_id, a.program)
    pmt = build_pmt(a.program)
    sdt = build_sdt(a.ts_id, a.net_id, a.program, a.provider, a.name)
    nit = build_nit(a.net_id, a.network)

    counts = {'PAT': 0, 'PMT': 0, 'SDT': 0, 'NIT': 0, 'null': 0}
    with open(a.out, 'wb') as f:
        for i in range(total):
            if i % iv_pat == 0:
                f.write(packetise(PID_PAT, pat, cc[PID_PAT])); cc[PID_PAT] += 1
                counts['PAT'] += 1
            elif i % iv_pat == 1:
                f.write(packetise(PID_PMT, pmt, cc[PID_PMT])); cc[PID_PMT] += 1
                counts['PMT'] += 1
            elif i % iv_sdt == 2:
                f.write(packetise(PID_SDT, sdt, cc[PID_SDT])); cc[PID_SDT] += 1
                counts['SDT'] += 1
            elif i % iv_sdt == 3:
                f.write(packetise(PID_NIT, nit, cc[PID_NIT])); cc[PID_NIT] += 1
                counts['NIT'] += 1
            else:
                f.write(null_packet()); counts['null'] += 1

    print(f"wrote {a.out}: {total:,} packets, {total*PKT/1e6:.2f} MB, "
          f"{a.seconds:.1f} s at {a.rate/1e6:.3f} Mbit/s")
    print(f"  service {a.program} '{a.name}' by '{a.provider}' on network '{a.network}'")
    print(f"  tables: " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
