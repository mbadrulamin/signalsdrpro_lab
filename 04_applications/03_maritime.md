# 🚢 03 — Maritime

> Ships are aircraft that move slowly, transmit more predictably, and carry a legal obligation
> to broadcast their identity. If you live near water, AIS is the easiest tracking project there
> is.
>
> [← Aviation](./02_aviation.md) · [Catalogue index](./README.md) · [Next: Satellite & Space →](./04_satellite_and_space.md)

---

## Why maritime is easy

**AIS is mandatory** for most commercial vessels over 300 gross tonnes, transmits every 2–10
seconds, uses a single well-documented format, and sits in a quiet part of VHF with almost no
interference. A vertical antenna and a few metres of height will reach 20–40 km over water —
much further than the same setup manages over land, because the sea is flat and conductive.

> ⚖️ Reception of AIS is unrestricted in most countries and the data is published openly by
> several services. **Distress traffic (DSC, EPIRB, Ch 16) is different** — never transmit, and
> if you decode a genuine distress message, contact your coastguard rather than posting it.

---

## Vessel tracking

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **AIS Class A** | 161.975 / 162.025 MHz | GMSK, 9600 bit/s, HDLC | ⭐⭐⭐ | ✅ | 🟢 Commercial vessels. Position, MMSI, course, speed, destination |
| **AIS Class B** | same two channels | GMSK, lower power | ⭐⭐⭐ | ✅ | 🟢 Leisure and small craft. Weaker, less frequent |
| **AIS-SART** | same | AIS message 1 with special MMSI | ⭐⭐⭐ | ✅ | ⛔ Search-and-rescue transponder. Report, do not publish |
| **AIS aids-to-navigation** | same | AIS message 21 | ⭐⭐⭐ | ✅ | 🟢 Buoys and lighthouses announcing themselves |
| **AIS base stations** | same | AIS message 4 | ⭐⭐⭐ | ✅ | 🟢 Shore infrastructure, includes an accurate UTC timestamp |
| **Long-range AIS (satellite)** | 156.775 / 156.825 MHz | GMSK | ⭐⭐⭐⭐ | ✅📡 | 🟢 Channels reserved for satellite reception |
| **LRIT** | Inmarsat | — | ⭐⭐⭐⭐⭐ | 🔺📡 | ⛔ Encrypted long-range identification and tracking |
| **VDES** | 157–162 MHz | successor to AIS | ⭐⭐⭐⭐ | ✅ | 🟢 Emerging; higher data rate |

---

## Voice and calling

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Marine VHF voice** | 156.000–162.025 MHz | NBFM, 25 kHz | ⭐ | ✅ | 🟡 [Lab 06](../02_flowgraphs/lab06_multimode_receiver/README.md). Channels 1–88 |
| **Channel 16 (distress/calling)** | 156.800 MHz | NBFM | ⭐ | ✅ | ⛔ **Monitor only.** Internationally protected |
| **Channel 13 (bridge-to-bridge)** | 156.650 MHz | NBFM | ⭐ | ✅ | 🟡 Ship manoeuvring coordination — often the busiest channel |
| **Port operations** | various in band | NBFM | ⭐ | ✅ | 🟡 Pilots, tugs, harbour control |
| **Marine HF (SSB)** | 2–22 MHz bands | USB | ⭐ | 🔻📡 | 🟡 Long-range ship-to-shore |
| **DSC (VHF)** | 156.525 MHz (Ch 70) | FSK, 1200 baud | ⭐⭐⭐ | ✅ | 🟡 Digital selective calling — automated alerting |
| **DSC (MF/HF)** | 2187.5 kHz and others | FSK, 100 baud | ⭐⭐⭐ | 🔻 | 🟡 Long-range equivalent |

---

## Safety, weather and distress

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **NAVTEX** | 518 kHz (English), 490, 4209.5 kHz | FSK, 100 baud, SITOR-B | ⭐⭐ | 🔻📡 | 🟢 Navigational warnings and forecasts as plain text. **A lovely first HF data decode** |
| **EPIRB** | 406.028 MHz + 121.5 MHz | short digital burst | ⭐⭐⭐ | ✅ | ⛔ Emergency beacon. If real, call your coastguard |
| **SART (radar transponder)** | 9.2–9.5 GHz | responds to X-band radar | ⭐⭐⭐⭐ | 🔺📡 | ⛔ Shows as a line of blips on a ship's radar |
| **Weatherfax (HF fax)** | 3–18 MHz schedules | FM-subcarrier fax | ⭐⭐ | 🔻📡 | 🟢 Synoptic charts drawn line by line. Deeply satisfying |
| **Marine weather (VHF)** | Ch 21B, WX channels | NBFM voice | ⭐ | ✅ | 🟢 Continuous in North America |
| **Coastguard broadcasts** | various VHF/HF | NBFM / USB | ⭐ | ✅/🔻 | 🟡 Scheduled safety information |

---

## Ship systems

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **X-band marine radar** | 9.3–9.5 GHz | pulsed | ⭐⭐⭐⭐ | 🔺📡 | 🟢 Detect the pulses; imaging needs a rotating antenna |
| **S-band marine radar** | 2.9–3.1 GHz | pulsed | ⭐⭐⭐⭐ | ✅📡 | 🟢 Within your SDR's range — you can see the sweep |
| **Inmarsat FleetBroadband** | 1.5 / 1.6 GHz | PSK | ⭐⭐⭐⭐ | ✅📡🔊 | 🟡 See [Satellite](./04_satellite_and_space.md) |
| **VHF Data Exchange (VDE)** | 157–162 MHz | digital | ⭐⭐⭐⭐ | ✅ | 🟢 Part of the VDES family |
| **Racon (radar beacon)** | X/S band | Morse on radar return | ⭐⭐⭐⭐ | 🔺📡 | 🟢 Navigation marks that paint their identity on a ship's radar screen |

---

## Try this first: AIS

If you can see water from where you live, AIS is a better second project than ADS-B:

- **Two channels only** — 161.975 and 162.025 MHz, so a 2 MSPS capture covers both at once
- **Slow** — 9600 bit/s GMSK, far gentler than 1 Mbit/s PPM
- **Self-verifying** — every message contains an MMSI you can look up, and a position you can
  sanity-check against a public tracker
- **The antenna is easy** — a 470 mm quarter-wave, which is a length you can cut accurately

The decode chain is: NBFM demodulate → GMSK bit recovery → NRZI decode → HDLC de-stuffing →
CRC-16 → six-bit ASCII payload unpacking. Everything except GMSK is already in your toolkit
after [Lab 08](../02_flowgraphs/lab08_rds_decoder/README.md).

---

## Then: NAVTEX

If you have an upconverter, NAVTEX at 518 kHz is one of the most satisfying decodes in radio: a
100-baud FSK signal that resolves into **readable English sentences** about storms and
navigation hazards, transmitted on a fixed schedule from a station you can identify. It uses
SITOR-B forward error correction — each character is sent twice, offset in time — which is a
gentle introduction to FEC.

---

[← Aviation](./02_aviation.md) · [Catalogue index](./README.md) · [Next: Satellite & Space →](./04_satellite_and_space.md)
