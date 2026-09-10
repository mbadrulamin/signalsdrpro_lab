# 🛰️ 04 — Satellite & Space

> The domain with the highest reward-to-effort ratio in all of SDR. A $5 antenna made of coat
> hanger wire will give you a photograph of your own continent, taken from orbit ten minutes ago.
>
> [← Maritime](./03_maritime.md) · [Catalogue index](./README.md) · [Next: Weather & Environment →](./05_weather_and_environment.md)

---

## Two kinds of satellite, two kinds of problem

| | **LEO** (low Earth orbit) | **GEO** (geostationary) |
|---|---|---|
| Altitude | 400–1400 km | 35,786 km |
| Motion | Crosses the sky in 10–15 minutes | Fixed point in the sky |
| Doppler | **±3–5 kHz at VHF** — must be corrected | Negligible |
| Antenna | Omnidirectional or hand-tracked | Fixed dish, aim once |
| Difficulty | Timing your pass | Pointing accurately, and link budget |
| Examples | NOAA, Meteor, ISS, cubesats | GOES, Inmarsat, TV |

**Doppler shift** is the defining LEO problem:

$$
\Delta f = f_0 \cdot \frac{v_{\text{radial}}}{c}
$$

A NOAA satellite at 137 MHz closing at 7 km/s gives $137\text{e}6 \times 7000/3\text{e}8 = 3.2$ kHz
of shift, sweeping through zero at closest approach. Wideband FM tolerates it; anything
narrowband or coherent does not, and you must correct with predicted orbital elements (TLEs).

---

## Weather satellites — start here

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **NOAA APT** | 137.100, 137.9125, 137.620 MHz | WBFM → 2.4 kHz AM subcarrier | ⭐⭐ | ✅📡 | 🟢 **The best second project in SDR.** Analog line-by-line image, 4 km/pixel |
| **Meteor-M N2 LRPT** | 137.100 / 137.900 MHz | QPSK 72 kbit/s, Viterbi + Reed-Solomon | ⭐⭐⭐⭐ | ✅📡 | 🟢 Digital, full colour, much sharper than APT |
| **GOES HRIT** | 1694.1 MHz | BPSK 927 kbit/s | ⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Full-disc Earth images every 10 minutes. Needs a dish + LNA |
| **GOES EMWIN** | 1692.7 MHz | BPSK | ⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Text warnings and charts alongside HRIT |
| **GK-2A LRIT** | 1692.14 MHz | BPSK | ⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Korean geostationary; covers Asia-Pacific |
| **Elektro-L LRIT** | 1691 MHz | BPSK | ⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Russian geostationary |
| **FengYun** | 137 MHz, 1.7 GHz | various | ⭐⭐⭐⭐ | ✅/🔺📡 | 🟢 Chinese meteorological series |
| **Metop AHRPT** | 1701.3 MHz | OQPSK 3.5 Mbit/s | ⭐⭐⭐⭐⭐ | 🔺📡🔊🖥️ | 🟢 Very high rate; needs tracking dish |
| **NOAA HRPT** | 1698, 1702.5, 1707 MHz | 665 kbit/s | ⭐⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Full-resolution version of APT |
| **DSCOVR / space weather** | various | telemetry | ⭐⭐⭐⭐⭐ | 🔺📡 | 🟢 Deep-space climate observatory |

---

## Amateur and educational satellites

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **FM voice repeaters (e.g. SO-50, AO-91)** | 145 / 435 MHz | NBFM | ⭐⭐ | ✅📡 | 🔴 TX needs a licence; RX is free. A handheld Yagi works |
| **Linear transponders (e.g. AO-7, RS-44)** | 145 / 435 MHz | SSB/CW inverting | ⭐⭐⭐ | ✅📡 | 🔴 Full Doppler correction on both links |
| **ISS voice repeater** | 145.990 up / 437.800 down | NBFM | ⭐⭐ | ✅📡 | 🟢 RX is easy on a good pass |
| **ISS SSTV** | 145.800 MHz | NBFM + SSTV audio | ⭐⭐ | ✅📡 | 🟢 Periodic image events. **A great confidence builder** |
| **ISS APRS digipeater** | 145.825 MHz | AFSK 1200 packet | ⭐⭐⭐ | ✅📡 | 🟢 Watch packets relayed from orbit |
| **Cubesat CW beacons** | 435–438 MHz | CW / Morse | ⭐⭐ | ✅📡 | 🟢 Dozens of them; simplest satellite signal that exists |
| **Cubesat telemetry (AX.25)** | 435–438 MHz | AFSK/GMSK 1200–9600 | ⭐⭐⭐ | ✅📡 | 🟢 Many publish decoders and welcome reports |
| **FUNcube telemetry** | 145.935 MHz | BPSK 1200 | ⭐⭐⭐ | ✅📡 | 🟢 Educational payload with an official dashboard |
| **QO-100 / Es'hail-2** | 10.489 GHz down | SSB/CW/DATV | ⭐⭐⭐⭐ | 🔺📡 | 🔴 **Geostationary amateur transponder** — no tracking needed |
| **SatNOGS network** | various | many | ⭐⭐⭐ | ✅📡 | 🟢 Contribute your receiver to a global observation network |

---

## Commercial satellite

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Inmarsat STD-C (EGC)** | 1537–1544 MHz | BPSK 1200 | ⭐⭐⭐ | ✅📡🔊 | 🟡 Safety broadcasts to ships, in readable text. **Geostationary — aim once** |
| **Inmarsat Classic Aero** | 1545 MHz region | BPSK 600–10500 | ⭐⭐⭐⭐ | ✅📡🔊 | 🟡 Aircraft SATCOM. `JAERO` decodes it |
| **Inmarsat AERO-L / -H** | 1.5 GHz | BPSK | ⭐⭐⭐⭐ | ✅📡🔊 | 🟡 Higher rate aeronautical channels |
| **Iridium downlink** | 1616–1626.5 MHz | QPSK bursts, TDMA | ⭐⭐⭐⭐⭐ | ✅📡🖥️ | ⛔ Ring alerts and frame sync are studied openly; traffic is not |
| **Globalstar** | 2483.5–2500 MHz | CDMA | ⭐⭐⭐⭐⭐ | ✅📡 | ⛔ |
| **Orbcomm** | 137–138 MHz | SDPSK 4800 | ⭐⭐⭐ | ✅📡 | 🟡 Machine-to-machine messaging; easy to see on a waterfall |
| **Starlink beacons** | 10.7–12.7 GHz | — | ⭐⭐⭐⭐⭐ | 🔺📡 | 🟡 Detecting presence is feasible; decoding is not |
| **GEO TV downlinks** | 10.7–12.75 GHz | DVB-S2 | ⭐⭐⭐⭐ | 🔺📡 | 🟢 See [Broadcast](./01_broadcast_and_media.md) |
| **Satellite phone uplinks** | 1.6 GHz | various | ⭐⭐⭐⭐⭐ | ✅📡 | ⛔ Interception prohibited nearly everywhere |
| **Military UHF SATCOM** | 240–270, 290–320 MHz | NBFM, PSK | ⭐⭐ | ✅📡 | 🟡 Famously easy to hear; "pirates" often occupy them |

---

## Navigation constellations

*Full detail in [Navigation & Timing](./10_navigation_and_timing.md).*

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **GPS L1 C/A** | 1575.42 MHz | BPSK, 1023-chip Gold code | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 20 dB *below* the noise floor. Recovered by correlation |
| **GLONASS L1** | 1598–1606 MHz | FDMA BPSK | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **Galileo E1** | 1575.42 MHz | BOC(1,1) | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **BeiDou B1** | 1561.098 MHz | BPSK | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **SBAS (WAAS/EGNOS)** | 1575.42 MHz | from GEO satellites | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Correction data, no tracking needed |

---

## Space science and deep space

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Deep Space Network downlinks** | 2.2–2.3, 8.4 GHz | BPSK, very low rate | ⭐⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Voyager, Mars orbiters. Needs a large dish |
| **Lunar orbiter telemetry** | S-band | PSK | ⭐⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Occasionally within amateur reach during missions |
| **Amateur deep-space (e.g. Tianwen, LICIACube)** | S/X band | various | ⭐⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Community efforts have decoded several |
| **Launch vehicle telemetry** | S-band | PCM/FM | ⭐⭐⭐⭐⭐ | ✅📡 | 🟡 Brief and geographically specific |
| **Reentry / debris radar returns** | see [Radar](./11_radar_and_sensing.md) | | | | |

---

## Try this first: NOAA APT

This is the project that converts people from "I have an SDR" to "I do radio". Everything you
need:

**The antenna** — a V-dipole. Two 530 mm wires at 120°, horizontal, pointing north-south. Cost:
a coat hanger and an SMA pigtail. It genuinely works.

**The pass** — use any tracking site or `gpredict` to find when NOAA-15, -18 or -19 goes over.
You get 10–15 minutes.

**The chain** — you already built it in [Lab 03](../02_flowgraphs/lab03_advanced_wbfm/README.md):

```
USRP (137.1 MHz, 2 MSPS)
  → xlating filter, ~40 kHz wide      ← Lab 06's technique
  → WBFM demod                        ← Lab 01's block
  → resample to 11025 Hz
  → AM-envelope the 2400 Hz subcarrier
  → one image line per 0.5 s, 2080 pixels
```

**The catch that gets everyone:** APT's *carrier* is FM but the *image* is AM on a 2400 Hz
subcarrier. If you feed the FM audio straight to an image decoder you get noise. Envelope-detect
first ([Fundamentals 07](../01_fundamentals/07_am_and_narrowband_fm.md)).

**Record the pass with [Lab 05](../02_flowgraphs/lab05_iq_record_playback/README.md).** You get
one attempt per pass; a recording gives you unlimited attempts at the decoder.

---

## Then: geostationary, because you only aim once

Once LEO passes start feeling like a scheduling chore, **Inmarsat STD-C** is a revelation: the
satellite never moves, so you aim a small patch antenna once and leave it. It transmits
maritime safety broadcasts in plain readable English, continuously, forever. It is the easiest
geostationary decode there is, and it makes the jump to GOES HRIT feel natural.

---

[← Maritime](./03_maritime.md) · [Catalogue index](./README.md) · [Next: Weather & Environment →](./05_weather_and_environment.md)
