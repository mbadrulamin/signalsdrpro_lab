#!/usr/bin/env python3
"""
make_diagrams.py - Generate the SVG figures used by 01_fundamentals/00_introduction_to_sdr.md.

All four diagrams are original work drawn from published specifications, so the
repository carries no third-party images. Re-run this after editing the data
tables below (for example when MCMC updates a Class Assignment).

Usage:
    python3 make_diagrams.py [--outdir ../01_fundamentals/images]
"""
import argparse, math, pathlib

# ---------------------------------------------------------------- helpers --
FONT = "font-family='DejaVu Sans, Segoe UI, Helvetica, Arial, sans-serif'"
INK, MUTED, PAPER = "#1a1a1a", "#5a6570", "#ffffff"


def svg(w, h, body, title=""):
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' "
            f"width='{w}' height='{h}' role='img'>\n"
            f"<title>{title}</title>\n"
            f"<rect width='{w}' height='{h}' fill='{PAPER}'/>\n"
            "<defs><marker id='a' viewBox='0 0 10 10' refX='9' refY='5' "
            "markerWidth='6' markerHeight='6' orient='auto-start-reverse'>"
            f"<path d='M0,0 L10,5 L0,10 z' fill='{INK}'/></marker></defs>\n"
            f"{body}\n</svg>\n")


def box(x, y, w, h, label, sub="", fill="#eef3f8", stroke="#33689c", fs=13, rx=6):
    s = (f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{rx}' fill='{fill}' "
         f"stroke='{stroke}' stroke-width='1.6'/>")
    if sub:
        s += (f"<text x='{x+w/2}' y='{y+h/2-4}' text-anchor='middle' {FONT} "
              f"font-size='{fs}' font-weight='600' fill='{INK}'>{label}</text>")
        for i, line in enumerate(sub.split("|")):
            s += (f"<text x='{x+w/2}' y='{y+h/2+12+i*12}' text-anchor='middle' {FONT} "
                  f"font-size='10.5' fill='{MUTED}'>{line}</text>")
    else:
        s += (f"<text x='{x+w/2}' y='{y+h/2+4}' text-anchor='middle' {FONT} "
              f"font-size='{fs}' font-weight='600' fill='{INK}'>{label}</text>")
    return s


def txt(x, y, s, fs=12, anchor="start", fill=INK, weight="400", style=""):
    return (f"<text x='{x}' y='{y}' text-anchor='{anchor}' {FONT} font-size='{fs}' "
            f"font-weight='{weight}' fill='{fill}' {style}>{s}</text>")


def arrow(x1, y1, x2, y2, dash=""):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    return (f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{INK}' "
            f"stroke-width='1.8' marker-end='url(#a)'{d}/>")


def line(x1, y1, x2, y2, col=INK, w=1.4, dash=""):
    d = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{col}' stroke-width='{w}'{d}/>"


# ------------------------------------------------- 1. superhet vs SDR ------
def diagram_architecture():
    b = [txt(20, 30, "Where the digital boundary sits", 17, weight="700")]
    b.append(txt(20, 52, "Everything to the right of the dashed line is software you can change.", 12, fill=MUTED))
    # classic superhet
    b.append(txt(20, 92, "Classic superheterodyne receiver  (1918-)", 13, weight="700"))
    xs, y, w, h = 20, 105, 118, 52
    stages = [("Antenna", ""), ("RF filter", "fixed, tuned"), ("Mixer + LO", "tunable"),
              ("IF filter", "FIXED in glass|or crystal"), ("Demodulator", "AM or FM|hardwired"),
              ("Audio amp", "")]
    for i, (lab, sub) in enumerate(stages):
        x = xs + i * (w + 22)
        b.append(box(x, y, w, h, lab, sub, fill="#fdeeee", stroke="#b4534f"))
        if i:
            b.append(arrow(x - 22, y + h / 2, x - 3, y + h / 2))
    b.append(line(xs, y + h + 16, xs + 6 * (w + 22) - 22, y + h + 16, "#b4534f", 1.2, "5 4"))
    b.append(txt(xs, y + h + 33, "All of it is metal. Changing the mode means changing the hardware.",
                 11.5, fill="#b4534f", style="font-style='italic'"))
    # SDR
    b.append(txt(20, 215, "Software-defined radio", 13, weight="700"))
    y2 = 228
    sdr = [("Antenna", ""), ("RF front end", "wideband|LNA + filter"), ("Mixer + LO", "agile, wide"),
           ("ADC", "12-bit|61.44 MSPS")]
    for i, (lab, sub) in enumerate(sdr):
        x = xs + i * (w + 22)
        b.append(box(x, y2, w, h, lab, sub, fill="#eef3f8", stroke="#33689c"))
        if i:
            b.append(arrow(x - 22, y2 + h / 2, x - 3, y2 + h / 2))
    xd = xs + 4 * (w + 22) - 11
    b.append(line(xd, y2 - 22, xd, y2 + h + 40, "#2f7d46", 2.2, "7 5"))
    b.append(txt(xd + 8, y2 - 28, "the digital boundary", 11.5, fill="#2f7d46", weight="700"))
    for i, (lab, sub) in enumerate([("Filter", "your taps"), ("Demodulate", "any mode"),
                                    ("Decode", "any protocol")]):
        x = xs + (4 + i) * (w + 22)
        b.append(box(x, y2, w, h, lab, sub, fill="#eaf6ee", stroke="#2f7d46"))
        b.append(arrow(x - 22, y2 + h / 2, x - 3, y2 + h / 2))
    b.append(txt(xd + 8, y2 + h + 33,
                 "Software. Change the mode by editing a flowgraph - no soldering iron.",
                 11.5, fill="#2f7d46", style="font-style='italic'"))
    return svg(1010, 338, "\n".join(b), "Superheterodyne versus software-defined radio")


# ----------------------------------------- 2. SignalSDR Pro block diagram --
def diagram_signalsdr():
    b = [txt(20, 28, "SignalSDR Pro - hardware block diagram", 17, weight="700"),
         txt(20, 48, "Analog Devices AD9361 transceiver + AMD Zynq-7020 SoC. "
                     "Drawn from published specifications.", 11.5, fill=MUTED)]
    # RF front end
    b.append(box(20, 80, 120, 150, "RF ports", "TX1/RX1  RX1|TX2/RX2  RX2|SMA female|50 ohm",
                 fill="#f6f0fa", stroke="#7a52a1"))
    # AD9361
    b.append(box(175, 70, 250, 235, "", "", fill="#eef3f8", stroke="#33689c"))
    b.append(txt(300, 92, "AD9361 RF Transceiver", 13.5, "middle", weight="700"))
    b.append(txt(300, 108, "70 MHz - 6 GHz  |  2x2 MIMO", 11, "middle", fill=MUTED))
    b.append(box(190, 122, 220, 46, "RX chain x2", "LNA - mixer - LPF - 12-bit ADC",
                 fill="#dcebf7", stroke="#33689c", fs=12))
    b.append(box(190, 178, 220, 46, "TX chain x2", "12-bit DAC - LPF - mixer - driver",
                 fill="#dcebf7", stroke="#33689c", fs=12))
    b.append(box(190, 234, 220, 46, "Fractional-N synthesisers", "independent RX and TX LOs",
                 fill="#dcebf7", stroke="#33689c", fs=12))
    # Zynq
    b.append(box(465, 70, 250, 235, "", "", fill="#eaf6ee", stroke="#2f7d46"))
    b.append(txt(590, 92, "AMD Zynq-7020 SoC", 13.5, "middle", weight="700"))
    b.append(txt(590, 108, "85K logic cells  |  DDR3", 11, "middle", fill=MUTED))
    b.append(box(480, 122, 220, 74, "Programmable Logic (FPGA)",
                 "DDC / DUC, decimation|packetising, DMA|B210 or Pluto personality",
                 fill="#d9efe0", stroke="#2f7d46", fs=12))
    b.append(box(480, 206, 220, 74, "Processing System",
                 "dual ARM Cortex-A9|embedded Linux|runs UHD / libiio server",
                 fill="#d9efe0", stroke="#2f7d46", fs=12))
    # host
    b.append(box(755, 80, 140, 150, "Host interfaces",
                 "USB 3.0 Type-B|Gigabit Ethernet|USB-OTG / TTL|microSD|40-pin GPIO|JTAG",
                 fill="#fdf3e6", stroke="#b97d29"))
    # clock
    b.append(box(175, 330, 250, 62, "Reference clock",
                 "+/- 1 ppm TCXO, built-in GPSDO|external clock input",
                 fill="#fdeeee", stroke="#b4534f"))
    b.append(box(465, 330, 250, 62, "GNSS receiver",
                 "active GPS antenna|disciplines the TCXO",
                 fill="#fdeeee", stroke="#b4534f"))
    # arrows
    b.append(arrow(142, 140, 173, 140)); b.append(txt(157, 133, "RF", 9.5, "middle", fill=MUTED))
    b.append(arrow(173, 200, 142, 200))
    b.append(arrow(427, 150, 463, 150)); b.append(txt(445, 143, "LVDS", 9.5, "middle", fill=MUTED))
    b.append(arrow(463, 210, 427, 210))
    b.append(arrow(717, 150, 753, 150))
    b.append(arrow(753, 200, 717, 200))
    b.append(arrow(300, 328, 300, 308))
    b.append(arrow(590, 328, 590, 308))
    b.append(arrow(463, 361, 427, 361))
    b.append(txt(20, 425, "The AD9361 turns RF into numbers. The Zynq moves and reshapes those "
                          "numbers. Everything above the ADC is physics; everything below it is software.",
                 12, fill=MUTED, style="font-style='italic'"))
    return svg(920, 445, "\n".join(b), "SignalSDR Pro hardware block diagram")


# ----------------------------------------------- 3. Malaysian spectrum -----
# (band_start_Hz, band_end_Hz, label, category)
MY_BANDS = [
    (526.5e3, 1606.5e3, "MW broadcast", "bc"),
    (3.9e6, 26.1e6, "Shortwave broadcast bands", "bc"),
    (7.0e6, 7.2e6, "40 m amateur", "am"),
    (14.0e6, 14.35e6, "20 m amateur", "am"),
    (87.5e6, 108e6, "FM broadcast", "bc"),
    (108e6, 137e6, "Aeronautical (AM)", "av"),
    (144e6, 148e6, "2 m amateur", "am"),
    (156e6, 162e6, "Maritime VHF", "mar"),
    (433e6, 435e6, "SRD 100 mW", "srd"),
    (430e6, 440e6, "70 cm amateur", "am"),
    (470e6, 694e6, "DTT - DVB-T2 (MYTV)", "bc"),
    (703e6, 803e6, "Mobile 700 (n28)", "cell"),
    (880e6, 960e6, "Mobile 900", "cell"),
    (919e6, 923e6, "SRD 500 mW (LoRa AS923)", "srd"),
    (1090e6, 1091e6, "ADS-B", "av"),
    (1710e6, 1880e6, "Mobile 1800", "cell"),
    (1920e6, 2170e6, "Mobile 2100", "cell"),
    (2400e6, 2500e6, "ISM 2.4 GHz", "srd"),
    (2500e6, 2690e6, "Mobile 2600", "cell"),
    (3300e6, 3800e6, "5G 3.5 GHz (n78)", "cell"),
    (5150e6, 5875e6, "ISM / RLAN 5 GHz", "srd"),
]
CAT = {"bc": ("#33689c", "Broadcasting"), "am": ("#2f7d46", "Amateur"),
       "av": ("#b97d29", "Aeronautical"), "mar": ("#7a52a1", "Maritime"),
       "srd": ("#b4534f", "Licence-exempt (SRD/ISM)"), "cell": ("#4a5a68", "Mobile / cellular")}
LABS = [(88e6, 108e6, "Labs 01-08"), (1090e6, 1090e6, "Lab 09"), (470e6, 694e6, "Lab 10")]


def diagram_malaysia():
    W = 1040
    x0, x1 = 215, W - 130          # wide left gutter: some band names are long
    fmin, fmax = 3e5, 6.5e9
    lg = lambda f: x0 + (math.log10(f) - math.log10(fmin)) / (math.log10(fmax) - math.log10(fmin)) * (x1 - x0)
    b = [txt(20, 30, "Radio spectrum in Malaysia - the bands an SDR user meets", 17, weight="700"),
         txt(20, 50, "Simplified from the MCMC Spectrum Plan and Class Assignment. "
                     "Indicative only - always check the current MCMC documents.", 11.5, fill=MUTED)]
    ay = 92
    b.append(line(x0, ay, x1, ay, INK, 1.4))
    for f, lab in [(1e6, "1 MHz"), (10e6, "10 MHz"), (100e6, "100 MHz"),
                   (1e9, "1 GHz"), (6e9, "6 GHz")]:
        x = lg(f)
        b.append(line(x, ay - 5, x, ay + 5, INK, 1.4))
        b.append(txt(x, ay - 12, lab, 11, "middle", fill=MUTED))
    cx0, cx1 = lg(70e6), lg(6e9)
    b.append(f"<rect x='{cx0}' y='{ay+8}' width='{cx1-cx0}' height='26' rx='4' "
             f"fill='#2f7d46' fill-opacity='0.16' stroke='#2f7d46' stroke-width='1.4'/>")
    b.append(txt((cx0 + cx1) / 2, ay + 26, "SignalSDR Pro tunes here:  70 MHz - 6 GHz",
                 12, "middle", fill="#2f7d46", weight="700"))
    b.append(f"<rect x='{x0}' y='{ay+8}' width='{cx0-x0}' height='26' rx='4' "
             f"fill='#b4534f' fill-opacity='0.10' stroke='#b4534f' stroke-width='1.2' "
             f"stroke-dasharray='5 4'/>")
    b.append(txt((x0 + cx0) / 2, ay + 26, "needs an upconverter", 10.5, "middle", fill="#b4534f"))
    y, rowh = ay + 58, 23
    for f1, f2, label, cat in MY_BANDS:
        col = CAT[cat][0]
        xa, xb = lg(f1), max(lg(f2), lg(f1) + 3)
        b.append(f"<rect x='{xa}' y='{y}' width='{xb-xa}' height='{rowh-7}' rx='3' "
                 f"fill='{col}' fill-opacity='0.72'/>")
        rng = (f"{f1/1e6:.4g}-{f2/1e6:.4g} MHz" if f2 < 1e9
               else f"{f1/1e9:.4g}-{f2/1e9:.4g} GHz")
        b.append(txt(x0 - 10, y + rowh - 12, label, 11, "end", weight="600"))
        b.append(txt(xb + 7, y + rowh - 12, rng, 9.5, fill=MUTED))
        y += rowh
    # everything below is laid out from the running y, so nothing can overlap
    y += 12
    b.append(line(20, y, W - 20, y, "#d8dee4", 1.2)); y += 24
    b.append(txt(20, y, "Category", 12, weight="700"))
    for i, (k, (col, name)) in enumerate(CAT.items()):
        cxp = 95 + (i % 3) * 300
        yy = y + (i // 3) * 20
        b.append(f"<rect x='{cxp}' y='{yy-10}' width='14' height='12' rx='2' fill='{col}' fill-opacity='0.72'/>")
        b.append(txt(cxp + 20, yy, name, 10.5, fill=MUTED))
    y += 20 * ((len(CAT) + 2) // 3) + 16
    b.append(txt(20, y, "This lab uses", 12, weight="700"))
    for f1, f2, name in LABS:
        xa, xb = lg(f1), max(lg(f2), lg(f1) + 4)
        b.append(f"<rect x='{xa}' y='{y-11}' width='{xb-xa}' height='14' rx='2' "
                 f"fill='#1a1a1a' fill-opacity='0.75'/>")
        b.append(txt((xa + xb) / 2, y + 14, name, 10, "middle", weight="600"))
    y += 40
    b.append(txt(20, y, "Transmitting in any of these bands without an assignment is an offence "
                        "under the Communications and Multimedia Act 1998.",
                 11, fill="#b4534f", style="font-style='italic'"))
    return svg(W, y + 20, "\n".join(b), "Malaysian radio spectrum overview")


# ------------------------------------------------ 4. the SDR landscape -----
SDRS = [
    ("RTL-SDR v4",        0.5e6, 1.766e9, 8,  2.4,  0, "~$40"),
    ("Airspy R2",         24e6,  1.8e9,  12, 10,   0, "~$200"),
    ("SDRplay RSPdx",     1e3,   2e9,    14, 10,   0, "~$250"),
    ("HackRF One",        1e6,   6e9,    8,  20,   1, "~$330"),
    ("ADALM-Pluto",       70e6,  6e9,    12, 20,   1, "~$230"),
    ("LimeSDR Mini 2.0",  10e6,  3.5e9,  12, 40,   1, "~$400"),
    ("bladeRF 2.0 micro", 47e6,  6e9,    12, 56,   1, "~$550"),
    ("SignalSDR Pro",     70e6,  6e9,    12, 56,   1, "~$500"),
    ("USRP B210",         70e6,  6e9,    12, 56,   1, "~$1500"),
]


def diagram_landscape():
    W, H = 940, 430
    x0, x1 = 185, W - 150
    fmin, fmax = 1e3, 7e9
    lg = lambda f: x0 + (math.log10(max(f, fmin)) - math.log10(fmin)) / (
        math.log10(fmax) - math.log10(fmin)) * (x1 - x0)
    b = [txt(20, 30, "The SDR landscape - frequency coverage and capability", 17, weight="700"),
         txt(20, 50, "Bar = tuning range.  Green = can transmit.  Blue = receive only.  "
                     "Prices are indicative, 2026.", 11.5, fill=MUTED)]
    ay = 82
    b.append(line(x0, ay, x1, ay, INK, 1.4))
    for f, lab in [(1e3, "1 kHz"), (1e6, "1 MHz"), (100e6, "100 MHz"), (1e9, "1 GHz"), (6e9, "6 GHz")]:
        x = lg(f)
        b.append(line(x, ay - 5, x, ay + 5, INK, 1.4))
        b.append(txt(x, ay - 12, lab, 11, "middle", fill=MUTED))
    y = ay + 20
    for name, f1, f2, bits, bw, tx, price in SDRS:
        col = "#2f7d46" if tx else "#33689c"
        xa, xb = lg(f1), lg(f2)
        hi = name == "SignalSDR Pro"
        if hi:
            b.append(f"<rect x='{x0-175}' y='{y-3}' width='{W-40-(x0-175)}' height='28' rx='4' "
                     f"fill='#fdf3e6' stroke='#b97d29' stroke-width='1.2'/>")
        b.append(f"<rect x='{xa}' y='{y+3}' width='{max(xb-xa,4)}' height='16' rx='3' "
                 f"fill='{col}' fill-opacity='{0.85 if hi else 0.65}'/>")
        b.append(txt(x0 - 12, y + 16, name, 11.5, "end", weight="700" if hi else "600"))
        b.append(txt(x1 + 10, y + 16, f"{bits}-bit  {bw:g} MHz  {price}", 10, fill=MUTED))
        y += 25
    b.append(txt(20, y + 22, "Two numbers decide almost everything: how wide a slice you can see "
                             "at once (bandwidth), and how finely you can measure it (bits).",
                 11.5, fill=MUTED, style="font-style='italic'"))
    b.append(txt(20, y + 42, "A wider, deeper receiver costs more and needs a faster host. "
                             "Transmitting brings legal duties that receiving does not.",
                 11.5, fill=MUTED, style="font-style='italic'"))
    return svg(W, y + 58, "\n".join(b), "Comparison of common SDR platforms")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--outdir', default='../01_fundamentals/images')
    a = ap.parse_args()
    out = pathlib.Path(a.outdir); out.mkdir(parents=True, exist_ok=True)
    figs = {'sdr_vs_superhet.svg': diagram_architecture(),
            'signalsdr_pro_block_diagram.svg': diagram_signalsdr(),
            'malaysia_spectrum.svg': diagram_malaysia(),
            'sdr_landscape.svg': diagram_landscape()}
    bad = 0
    for name, data in figs.items():
        (out / name).write_text(data)
        w, h, mx, my = _extent(data)
        fits = mx <= w and my <= h
        bad += not fits
        print(f"  {name:38} {int(w)}x{int(h)}  content to ({mx:.0f},{my:.0f})  "
              f"{'ok' if fits else 'OVERFLOWS ITS VIEWBOX'}")
    print(f"{len(figs)} diagrams written" + ("" if not bad else f", {bad} OVERFLOWING"))
    return 1 if bad else 0


def _extent(data):
    """Largest x and y any element reaches, so nothing is silently clipped."""
    import xml.etree.ElementTree as ET
    r = ET.fromstring(data)
    w, h = [float(v) for v in r.get('viewBox').split()[2:]]
    mx = my = 0.0
    for el in r.iter():
        tag = el.tag.split('}')[-1]
        if tag == 'text':
            mx, my = max(mx, float(el.get('x', 0))), max(my, float(el.get('y', 0)))
        elif tag == 'rect' and el.get('y') is not None:
            mx = max(mx, float(el.get('x', 0)) + float(el.get('width', 0)))
            my = max(my, float(el.get('y', 0)) + float(el.get('height', 0)))
        elif tag == 'line':
            mx = max(mx, float(el.get('x1', 0)), float(el.get('x2', 0)))
            my = max(my, float(el.get('y1', 0)), float(el.get('y2', 0)))
    return w, h, mx, my


if __name__ == '__main__':
    raise SystemExit(main())
