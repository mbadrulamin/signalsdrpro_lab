# 🚢 03 — Maritime

> Ships are like slow aircraft. They transmit regularly, and most are required by law to
> broadcast who they are. If you live near water, AIS ship tracking is the easiest tracking
> project there is.
>
> [← Aviation](./02_aviation.md) · [Catalogue index](./README.md) · [Next: Satellite & Space →](./04_satellite_and_space.md)

---

## Why maritime is easy

**AIS** (Automatic Identification System) is **required** on most commercial ships over 300
gross tonnes. It:

- sends a message every 2–10 seconds,
- uses one well-documented format, and
- sits in a quiet part of VHF, with almost no interference.

A vertical antenna a few metres up will reach **20–40 km over water** — much further than over
land, because the sea is flat and conducts well. The Straits of Malacca is one of the busiest
shipping lanes in the world.

> ⚖️ Receiving AIS is allowed in most countries, and several websites publish the data openly.
> **Distress signals (DSC, EPIRB, channel 16) are different.** Never transmit on them. If you
> ever decode a real distress message, contact the coastguard (in Malaysia, the Malaysian
> Maritime Enforcement Agency) — do not post it online.

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

If you can see the sea from where you live, AIS is an even better second project than ADS-B:

- **Only two channels** — 161.975 and 162.025 MHz. One 2 MSPS recording covers both.
- **Slow** — 9600 bits per second (GMSK), much gentler than ADS-B's 1 Mbit/s.
- **Easy to check** — every message has the ship's **MMSI** number, which you can look up, and a
  position you can compare with a public ship-tracking website.
- **An easy antenna** — a **463 mm** quarter-wave.

The decoding steps: narrow-FM demodulate → recover the GMSK bits → NRZI decode → remove HDLC
"bit stuffing" → check the 16-bit CRC → unpack the 6-bit text. After
[Lab 08](../02_flowgraphs/lab08_rds_decoder/README.md) you already know every step except GMSK.

---

## Then: NAVTEX

With an upconverter (NAVTEX is at 518 kHz, below the SignalSDR Pro's range), NAVTEX is one of the
most satisfying decodes in radio. A slow 100-baud FSK signal turns into **readable English
sentences** about storms and hazards to ships, sent on a fixed schedule from a known station. It
sends every character twice, a little apart in time (SITOR-B) — a gentle first look at error
correction.

---

[← Aviation](./02_aviation.md) · [Catalogue index](./README.md) · [Next: Satellite & Space →](./04_satellite_and_space.md)
