# 🧭 10 — Navigation & Timing

> How the world knows where it is and what time it is. Also the domain containing the single most
> impressive thing an SDR can do: pull a signal out from **20 dB below the noise floor** by
> correlation alone.
>
> [← Cellular](./09_cellular.md) · [Catalogue index](./README.md) · [Next: Radar & Sensing →](./11_radar_and_sensing.md)

---

## Why GNSS is the best hard project in SDR

A GPS satellite transmits about 27 W from 20,200 km away. By the time it reaches you, the signal
is around **−130 dBm** — roughly 20 dB *below* the thermal noise in its own bandwidth. You cannot
see it on any spectrum display. It simply is not there.

And yet it decodes perfectly, because of [Fundamentals 06's](../01_fundamentals/06_noise_snr_and_gain.md)
processing gain:

$$
G_p = 10\log_{10}(1023) = 30.1 \text{ dB}
$$

Each bit is spread across a 1023-chip Gold code. Correlate against the right code with the right
alignment and the signal rises 30 dB out of the noise; correlate against the wrong one and you get
nothing. Every satellite uses a different code, so they all share the same frequency without
interfering — that is CDMA, and GPS is its most elegant deployment.

**Building a GPS receiver from raw IQ is the graduation exercise of amateur SDR.** It uses
correlation, Doppler search, carrier tracking, code tracking, bit synchronisation, frame
decoding, and finally orbital mechanics — every skill in this repository plus astronomy.

---

## GNSS constellations

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **GPS L1 C/A** | 1575.42 MHz | BPSK, 1.023 Mchip/s Gold codes | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 The classic. Fully documented in IS-GPS-200 |
| **GPS L2C** | 1227.60 MHz | BPSK, civil | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Dual-frequency ionospheric correction |
| **GPS L5** | 1176.45 MHz | QPSK, higher power | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Safety-of-life band, stronger than L1 |
| **GPS P(Y)** | L1/L2 | encrypted military | — | — | ⛔ |
| **GLONASS L1OF** | 1598–1606 MHz | **FDMA** BPSK | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Unusual: each satellite has its own frequency, not its own code |
| **GLONASS L2OF** | 1242–1249 MHz | FDMA BPSK | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **Galileo E1 OS** | 1575.42 MHz | BOC(1,1) | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Shares L1 with GPS; split-spectrum modulation |
| **Galileo E5a/E5b** | 1176.45 / 1207.14 MHz | AltBOC | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Very wide, very precise |
| **BeiDou B1I** | 1561.098 MHz | BPSK | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **BeiDou B1C / B2a** | 1575.42 / 1176.45 MHz | BOC / QPSK | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **QZSS** | 1575.42 MHz | GPS-compatible | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Japan; high-elevation orbits |
| **NavIC / IRNSS** | 1176.45, 2492.028 MHz | BPSK/BOC | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 India; S-band signal is unusual |
| **SBAS (WAAS/EGNOS/MSAS/GAGAN)** | 1575.42 MHz | from geostationary | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Correction data. **No tracking needed — it sits still** |

---

## Time and frequency standards

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **WWV / WWVH** | 2.5, 5, 10, 15, 20 MHz | AM voice + ticks | ⭐ | 🔻📡 | 🟢 USA. Voice announcements, propagation reports, 1 pps ticks |
| **WWVB** | 60 kHz | phase/amplitude modulated | ⭐⭐ | 🔻📡 | 🟢 What American "atomic clocks" listen to |
| **DCF77** | 77.5 kHz | AM + phase modulation | ⭐⭐ | 🔻📡 | 🟢 Germany; covers most of Europe. **One bit per second — trivially decodable** |
| **MSF** | 60 kHz | AM | ⭐⭐ | 🔻📡 | 🟢 UK |
| **JJY** | 40, 60 kHz | AM | ⭐⭐ | 🔻📡 | 🟢 Japan |
| **BPC** | 68.5 kHz | AM | ⭐⭐ | 🔻📡 | 🟢 China |
| **RBU / RWM** | 66.66 kHz, 4.996/9.996/14.996 MHz | various | ⭐⭐ | 🔻📡 | 🟢 Russia |
| **CHU** | 3.330, 7.850, 14.670 MHz | AM + FSK time code | ⭐⭐ | 🔻📡 | 🟢 Canada |
| **TDF** | 162 kHz | phase modulation on a broadcast carrier | ⭐⭐⭐ | 🔻📡 | 🟢 France; time code hidden on a longwave station |
| **GPS-disciplined oscillator output** | — | 1 pps | ⭐⭐ | ✅ | 🟢 **Your SignalSDR Pro has one built in.** Use it to discipline measurements |

---

## Terrestrial navigation

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **NDB (non-directional beacon)** | 190–535 kHz | AM carrier + Morse ident | ⭐ | 🔻📡 | 🟢 The oldest navigation aid still flying. Vanishing fast — hear them while you can |
| **eLoran / Loran-C** | 100 kHz | pulsed, hyperbolic | ⭐⭐⭐⭐ | 🔻📡 | 🟢 Being revived as a GPS backup |
| **DGPS beacons** | 283.5–325 kHz | MSK, RTCM corrections | ⭐⭐⭐ | 🔻📡 | 🟢 Maritime differential corrections |
| **VOR / DME / TACAN** | see [Aviation](./02_aviation.md) | | | | |
| **Alpha / RSDN-20** | 11.9, 12.6, 14.9 kHz | pulsed VLF | ⭐⭐⭐⭐ | 🔻📡 | 🟢 Russian VLF navigation system |
| **Omega (historical)** | 10–14 kHz | — | — | — | 🟢 Shut down 1997; see [Oddities](./16_oddities_and_historical.md) |
| **Racon** | X/S band radar | see [Maritime](./03_maritime.md) | | | |
| **Marker / locator beacons** | 75 MHz, 300–400 kHz | AM | ⭐ | 🔻/✅ | 🟢 |

---

## Precision positioning

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **RTK correction streams** | over radio or internet | RTCM 3.x | ⭐⭐⭐⭐ | ✅ | 🟢 Centimetre positioning from carrier phase |
| **Carrier-phase GNSS** | L1/L2/L5 | phase tracking | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 The technique behind RTK and PPP |
| **GNSS reflectometry (GNSS-R)** | 1575.42 MHz | reflected signals | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Measure soil moisture, sea state and ice from reflected GPS |
| **Radio occultation** | GNSS through atmosphere | phase delay | ⭐⭐⭐⭐⭐ | 🔺📡 | 🟢 Atmospheric profiling; normally done from orbit |
| **GNSS interference / jamming detection** | 1575.42 MHz | spectrum monitoring | ⭐⭐⭐ | ✅📡 | 🟢 Cheap "personal privacy devices" are a real and growing problem |
| **GNSS spoofing detection** | 1575.42 MHz | consistency checking | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Compare arrival angles, signal levels and clock consistency |

---

## Try this first: DCF77 or WWVB

If you have an upconverter, a longwave time station is the **gentlest possible introduction to
decoding a real protocol**, because the data rate is *one bit per second*.

DCF77 (77.5 kHz, Germany) reduces its carrier amplitude to 15 % at the start of every second. A
100 ms reduction is a `0`; a 200 ms reduction is a `1`. Fifty-nine bits per minute carry the
minute, hour, day, month, year and two parity bits — and the 60th second has no marker at all,
which is how you find the frame boundary.

You can decode it with an envelope detector and a stopwatch. No synchronisation loop, no FEC,
nothing hidden. And at the end you have set a clock from a caesium standard 1000 km away.

---

## Then: acquire one GPS satellite

You do not need a full position fix to have done something remarkable. **Acquisition alone** —
proving that satellite PRN 7 is overhead, at a Doppler shift of −2100 Hz, by finding a
correlation peak that is invisible in the spectrum — is a complete and deeply satisfying project.

```
1. Record 10 s of IQ at 1575.42 MHz, ~2–4 MSPS, with an active GPS antenna
2. Generate the 1023-chip C/A code for PRN 1..32
3. For each PRN, search a 2-D grid:
       code phase   0..1022 chips
       Doppler      -5 kHz .. +5 kHz in 500 Hz steps
   (do the code search with an FFT — it is a circular correlation)
4. A peak more than ~2.5x the noise floor means that satellite is visible
```

Plot the correlation surface. The peak rises out of a flat plain of noise like a lighthouse, and
it will be the most convincing demonstration of processing gain you ever see.

**An active GPS antenna is essential** — the patch antennas sold for a few dollars include an
LNA and need 3–5 V bias. Your SDR does not supply bias; use a bias tee.

---

[← Cellular](./09_cellular.md) · [Catalogue index](./README.md) · [Next: Radar & Sensing →](./11_radar_and_sensing.md)
