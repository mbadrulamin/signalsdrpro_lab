# ✈️ 02 — Aviation

> Aircraft are the most rewarding thing a beginner can track: they are numerous, they broadcast
> constantly, they move, and you can verify every decode against a public flight tracker.
>
> [← Broadcast](./01_broadcast_and_media.md) · [Catalogue index](./README.md) · [Next: Maritime →](./03_maritime.md)

---

## Why aviation is a good hunting ground

Everything in this domain is designed for **safety**, which means it is designed to be
*received easily*. Signals are unencrypted, formats are published in ICAO standards, and there
is a global fleet transmitting them 24 hours a day. It is also the domain where
[Lab 09](../02_flowgraphs/lab09_adsb_receiver/README.md) already gave you a working decoder.

> ⚖️ **Reception is legal in most countries. Publishing or acting on it may not be.** Several
> jurisdictions restrict re-transmission of aeronautical communications specifically. Never
> transmit on any aviation frequency, ever — this is the clearest bright line in the hobby.

---

## Surveillance & position

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **ADS-B (Mode S, DF17)** | 1090 MHz | PPM, 1 Mbit/s, CRC-24 | ⭐⭐⭐ | ✅📡🔊 | 🟡 [Lab 09](../02_flowgraphs/lab09_adsb_receiver/README.md). Identity, altitude, CPR position, velocity |
| **Mode S short replies** | 1090 MHz | PPM, 56-bit | ⭐⭐⭐ | ✅📡 | 🟡 DF 0/4/5/11. Parity is XORed with the ICAO address |
| **Mode A/C replies** | 1090 MHz | pulse pairs | ⭐⭐ | ✅📡 | 🟡 Legacy squawk code and altitude |
| **UAT (ADS-B for GA)** | 978 MHz | PPM, 1.041 Mbit/s | ⭐⭐⭐ | ✅📡 | 🟡 USA only. Also carries FIS-B weather uplink |
| **TIS-B / ADS-R** | 1090 / 978 MHz | as ADS-B | ⭐⭐⭐ | ✅📡 | 🟡 Ground stations rebroadcasting radar tracks |
| **FIS-B weather uplink** | 978 MHz | UAT frames | ⭐⭐⭐⭐ | ✅📡 | 🟡 NEXRAD imagery and METARs, uplinked to aircraft |
| **Interrogations (Mode S uplink)** | 1030 MHz | PPM | ⭐⭐⭐ | ✅📡 | 🟡 The ground radar asking; harder than the replies |
| **Multilateration reference** | 1090 MHz, multi-site | TDOA | ⭐⭐⭐⭐⭐ | ✅📡🖥️ | 🟡 Position from arrival-time differences across receivers |

---

## Voice

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **VHF airband (tower, approach, ground)** | 118–137 MHz | **AM**, 25 or 8.33 kHz spacing | ⭐ | ✅ | 🟡 [Lab 06](../02_flowgraphs/lab06_multimode_receiver/README.md). AM so simultaneous transmissions both stay audible |
| **ATIS** | within 118–137 MHz | AM, looped recording | ⭐ | ✅ | 🟡 Continuous airport weather. **The easiest airband signal to find** |
| **VOLMET** | HF and VHF | AM | ⭐ | 🔻/✅ | 🟡 Scheduled en-route weather broadcasts |
| **UNICOM / CTAF** | 122.700–123.000 MHz | AM | ⭐ | ✅ | 🟡 Uncontrolled fields; pilots self-announcing |
| **Oceanic / long-haul HF** | 2.8–22 MHz families | USB | ⭐ | 🔻📡 | 🟡 Where there is no radar. Very long range |
| **Emergency / guard** | 121.500 MHz, 243.000 MHz | AM | ⭐ | ✅ | ⛔ **Monitor only.** Transmitting here is a serious offence |
| **Military air** | 225–400 MHz | AM | ⭐ | ✅ | 🟡 Often restricted; check local law |
| **HF SELCAL** | with HF voice | dual-tone pairs | ⭐⭐ | 🔻 | 🟡 Selective calling so crews need not monitor continuously |

---

## Data links

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **ACARS (VHF)** | 131.550, 131.725, 136.x MHz | MSK, 2400 bit/s | ⭐⭐ | ✅ | 🟡 Aircraft text messaging. Readable plain text — a great first data decode |
| **ACARS (HF)** | 2–22 MHz | HFDL, PSK | ⭐⭐⭐⭐ | 🔻📡 | 🟡 Oceanic. `dumphfdl` |
| **VDL Mode 2** | 136.725–136.975 MHz | D8PSK, 31.5 kbit/s | ⭐⭐⭐⭐ | ✅ | 🟡 The modern replacement for VHF ACARS |
| **CPDLC** | over VDL2 / SATCOM | text over datalink | ⭐⭐⭐⭐ | ✅ | 🟡 Controller–pilot text clearances |
| **SATCOM (Inmarsat Classic Aero)** | 1.5 GHz | BPSK | ⭐⭐⭐⭐ | ✅📡🔊 | 🟡 See [Satellite](./04_satellite_and_space.md). `JAERO` |
| **Iridium Aero** | 1.616–1.626 GHz | QPSK bursts | ⭐⭐⭐⭐⭐ | ✅📡 | 🟡 Short bursts, hard to catch |

---

## Navigation aids

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **VOR** | 108–117.95 MHz | AM + 30 Hz reference/variable | ⭐⭐⭐ | ✅ | 🟢 Decode the bearing yourself: compare phase of the 30 Hz FM subcarrier against the 30 Hz AM |
| **DVOR (Doppler VOR)** | same | inverted phase relationship | ⭐⭐⭐ | ✅ | 🟢 Most modern installations |
| **ILS localizer** | 108.10–111.95 MHz | 90/150 Hz AM tones | ⭐⭐ | ✅ | 🟢 Left/right guidance. Difference in depth of modulation |
| **ILS glideslope** | 328.6–335.4 MHz | 90/150 Hz AM tones | ⭐⭐ | ✅ | 🟢 Vertical guidance |
| **Marker beacons** | 75 MHz | AM tone (400/1300/3000 Hz) | ⭐ | ✅ | 🟢 Outer/middle/inner. Being decommissioned |
| **DME** | 962–1213 MHz | pulse pairs | ⭐⭐⭐ | ✅📡 | 🟢 Distance measuring; interrogate/reply timing |
| **TACAN** | 962–1213 MHz | DME + bearing | ⭐⭐⭐⭐ | ✅📡 | 🟡 Military |
| **NDB** | 190–535 kHz | AM carrier + Morse ident | ⭐ | 🔻📡 | 🟢 Beautifully simple, and disappearing fast. See [Oddities](./16_oddities_and_historical.md) |
| **Radio altimeter** | 4.2–4.4 GHz | FMCW | ⭐⭐⭐⭐ | ✅📡 | 🟡 Only detectable near an airport approach path |
| **ELT (emergency locator)** | 406 MHz + 121.5 MHz | digital burst + sweep tone | ⭐⭐ | ✅ | ⛔ **If you hear a real one, report it. Do not transmit** |

---

## Try this first: ATIS

Before you chase ADS-B, tune your Lab 06 receiver in **AM mode** to your nearest airport's ATIS
frequency (find it on any aviation chart or airport website). It is:

- **Continuous** — unlike tower chatter, it never stops
- **Strong** — transmitted from the airport at high power
- **Verifiable** — it reads out the weather, which you can check

It is the perfect signal for confirming that your AM chain, your antenna and your squelch
setting all work, before you go hunting for something bursty.

---

## Then: extend Lab 09

Your ADS-B decoder handles DF17 only. Three natural extensions, in increasing difficulty:

1. **Short frames (56-bit)** — DF 0/4/5/11. Note the parity trick: for DF 4/5/20/21 the CRC is
   XORed with the aircraft address, so you must maintain a list of addresses seen from DF17 to
   validate them ([Fundamentals 10](../01_fundamentals/10_error_detection_and_framing.md)).
2. **Surface position (TC 5–8)** — different CPR encoding for aircraft on the ground.
3. **A live map** — log CSV and plot with `folium`. Compare your tracks against a public
   tracker to measure your own receiver's range and coverage pattern.

---

[← Broadcast](./01_broadcast_and_media.md) · [Catalogue index](./README.md) · [Next: Maritime →](./03_maritime.md)
