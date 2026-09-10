# 📶 11 — Radar & Sensing

> Using radio to measure the physical world rather than to carry messages. This is where SDR
> stops being a receiver and becomes an **instrument**.
>
> [← Navigation & Timing](./10_navigation_and_timing.md) · [Catalogue index](./README.md) · [Next: Science →](./12_science_and_radio_astronomy.md)

---

## The two ways to do radar with an SDR

### Active — you transmit

You control the waveform, so you know exactly what you are looking for. But you need a licence,
a transmitter, and enough isolation between TX and RX that you do not deafen yourself. Your
SignalSDR Pro **can** do this (it has a transmitter), which puts genuine radar within reach.

### Passive — somebody else transmits

You listen to a broadcast transmitter you do not own, on two antennas: one pointed at the
transmitter (the **reference**), one pointed at the sky (the **surveillance**). Cross-correlate
the two and moving targets appear as peaks at a given delay and Doppler.

$$
\chi(\tau, f_d) = \int s_{\text{surv}}(t)\, s^*_{\text{ref}}(t-\tau)\, e^{-j2\pi f_d t}\, dt
$$

**No licence, no transmitter, no spectrum allocation.** You are borrowing a 100 kW FM or DVB-T
station as your illuminator. This is the single most impressive thing you can build with two
cheap SDRs, and it is entirely legal.

---

## Passive radar

| Project | Illuminator | Diff | Needs | Notes |
|---|---|---|---|---|
| **FM broadcast passive radar** | 88–108 MHz | ⭐⭐⭐⭐ | ✅📡🖥️ | 🟢 Best illuminator for beginners: strong, continuous, and you already know the band |
| **DVB-T passive radar** | 470–790 MHz | ⭐⭐⭐⭐ | ✅📡🖥️ | 🟢 Wider bandwidth → much better range resolution ($c/2B$) |
| **DAB passive radar** | 174–240 MHz | ⭐⭐⭐⭐ | ✅📡🖥️ | 🟢 OFDM gives a clean, well-behaved ambiguity function |
| **GSM/LTE passive radar** | cellular downlink | ⭐⭐⭐⭐⭐ | ✅📡🖥️ | 🟢 Cell reference signals are known pilots |
| **Starlink / satellite illumination** | Ku band | ⭐⭐⭐⭐⭐ | 🔺📡🖥️ | 🟢 Research-grade |
| **Aircraft detection & tracking** | any of the above | ⭐⭐⭐⭐ | ✅📡🖥️ | 🟢 **Verify your detections against ADS-B from [Lab 09](../02_flowgraphs/lab09_adsb_receiver/README.md)** |
| **Drone detection** | FM/DVB-T | ⭐⭐⭐⭐⭐ | ✅📡🖥️ | 🟢 Small, slow targets — genuinely hard |
| **Meteor trail detection** | see [Weather](./05_weather_and_environment.md) | ⭐⭐ | ✅📡 | 🟢 The easiest passive detection of all |

**Range resolution** is set by the illuminator's bandwidth: $\Delta R = c/(2B)$. FM broadcast
(200 kHz) gives 750 m; DVB-T (8 MHz) gives 19 m. That is why DVB-T is the serious choice.

---

## Active radar you can build

| Project | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **FMCW ranging radar** | 2.4 or 5.8 GHz ISM | linear chirp | ⭐⭐⭐⭐ | ✅📡🔴 | 🔴 Beat frequency ∝ range. The classic build-your-own-radar project |
| **CW Doppler speed radar** | 2.4 GHz ISM | continuous tone | ⭐⭐⭐ | ✅📡🔴 | 🔴 $f_d = 2v f_0/c$. Measure a passing car |
| **Pulse radar** | ISM band | short pulses | ⭐⭐⭐⭐ | ✅📡🔴 | 🔴 Needs fast TX/RX switching |
| **SAR (synthetic aperture)** | ISM | FMCW + motion | ⭐⭐⭐⭐⭐ | ✅📡🔴🖥️ | 🔴 Move the radar along a rail and synthesise a large antenna |
| **Through-wall / GPR** | UWB, low frequency | pulse or stepped-FMCW | ⭐⭐⭐⭐⭐ | ✅📡🔴 | 🔴 Heavily regulated in most countries |
| **Vital-signs radar** | 2.4, 24 GHz | CW Doppler | ⭐⭐⭐⭐⭐ | ✅📡🔴 | 🔴 Detect breathing and heartbeat from chest displacement |
| **Radar altimeter (experimental)** | ISM | FMCW | ⭐⭐⭐⭐ | ✅📡🔴 | 🔴 |
| **Bistatic radar with two SDRs** | ISM | separated TX/RX | ⭐⭐⭐⭐⭐ | ✅📡🔴🖥️ | 🔴 Solves the TX/RX isolation problem |

> 🔴 **Every active radar project requires a licence** (or an amateur allocation, or an ISM band
> used within its power and duty-cycle limits). Use a dummy load and an attenuator while
> developing, and check your national rules on radiodetermination — many countries prohibit
> radar in ISM bands entirely.

---

## Observing other people's radar

Entirely passive, entirely legal, and a good way to understand radar without transmitting.

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Air traffic control (primary) radar** | 1.2–1.4, 2.7–2.9 GHz | pulsed | ⭐⭐⭐ | ✅📡 | 🟢 Watch the rotation period — usually 4–12 s |
| **Weather radar** | 2.7–3.0, 5.6, 9.4 GHz | pulsed Doppler | ⭐⭐⭐ | ✅/🔺📡 | 🟢 S-band is within your tuning range |
| **Marine radar** | 2.9–3.1, 9.3–9.5 GHz | pulsed | ⭐⭐⭐ | ✅/🔺📡 | 🟢 |
| **Automotive radar** | 24, 77 GHz | FMCW | ⭐⭐⭐⭐⭐ | 🔺📡 | 🟢 Needs specialised front end |
| **Speed enforcement radar** | 24, 34 GHz | CW/FMCW | ⭐⭐⭐⭐ | 🔺📡 | 🟢 |
| **Automatic door / motion sensors** | 10.5, 24 GHz | CW Doppler | ⭐⭐⭐ | 🔺📡 | 🟢 Cheap modules you can buy and study |
| **GRAVES space surveillance** | 143.050 MHz | CW | ⭐⭐ | ✅📡 | 🟢 France. **The easiest radar signal in Europe** |
| **Over-the-horizon radar** | 3–30 MHz | FMCW sweeps | ⭐⭐⭐ | 🔻📡 | 🟢 The "Woodpecker" style sweeps; very visible on an HF waterfall |
| **Wind profilers** | 400–500 MHz, 900 MHz | pulsed Doppler | ⭐⭐⭐⭐ | ✅📡 | 🟢 Vertically pointing atmospheric radar |
| **Radar altimeter (aircraft)** | 4.2–4.4 GHz | FMCW | ⭐⭐⭐⭐ | ✅📡 | 🟢 Only near approach paths |
| **Ionosondes** | see [Weather](./05_weather_and_environment.md) | | | | |

---

## Non-radar sensing

| Project | Frequency | Method | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Wi-Fi CSI sensing** | 2.4/5 GHz | channel state information | ⭐⭐⭐⭐⭐ | ✅🖥️ | 🟢 Detect motion and gestures from Wi-Fi channel changes |
| **RF tomography** | ISM | link-quality between nodes | ⭐⭐⭐⭐⭐ | ✅ | 🟢 Image a room from how people block links |
| **Soil moisture from GNSS-R** | 1575 MHz | reflected GNSS | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 See [Navigation](./10_navigation_and_timing.md) |
| **Rain attenuation monitoring** | microwave links | signal level | ⭐⭐⭐ | ✅📡 | 🟢 Commercial link fade correlates with rainfall rate |
| **Sea-state from HF radar** | 3–30 MHz | Doppler spectrum | ⭐⭐⭐⭐⭐ | 🔻📡 | 🟢 Bragg scattering off ocean waves |
| **Ionospheric TEC from GNSS** | dual-frequency GNSS | differential delay | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **Passive thermal (radiometry)** | microwave | noise power | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Measure sky and ground brightness temperature |
| **Lightning direction finding** | VLF | TDOA between sites | ⭐⭐⭐⭐ | 🔻📡 | 🟢 Blitzortung runs a global volunteer network |

---

## Try this first: watch an airport radar sweep

Point a directional antenna toward your nearest airport and tune to **1.3 GHz** (L-band primary
radar) with your Lab 05 recorder running. You do not need to decode anything — just plot the
magnitude over time:

```python
import numpy as np
d = np.fromfile('radar.iq', dtype=np.complex64)
m = np.abs(d)
# decimate to a 1 ms envelope
env = m[:len(m)//2000*2000].reshape(-1, 2000).max(axis=1)
```

You will see the beam sweep past you **once every rotation** — typically 4 to 12 seconds — as a
periodic swell in received power. Measuring that rotation period, and the pulse repetition
interval inside each sweep, tells you the radar's unambiguous range:

$$
R_{\text{max}} = \frac{c \cdot \text{PRI}}{2}
$$

It is a complete radar measurement made entirely passively, with no licence and no transmitter.

---

## Then: passive radar, properly

Passive radar needs **two coherent receive channels**, and this is where your hardware earns its
keep: the B210 has **two RX channels sharing one clock and one LO**, which is exactly the
requirement. Most cheap SDRs cannot do this at all.

```
   Channel 0 ── antenna pointed AT the FM transmitter    (reference)
   Channel 1 ── antenna pointed at the sky, transmitter nulled out (surveillance)
              │
              ▼
   cross-ambiguity function over delay x Doppler
              │
              ▼
   clutter cancellation (the direct path is 60+ dB stronger than any target)
              │
              ▼
   detections -> compare against ADS-B truth
```

The hard part is not the correlation — it is **clutter cancellation**. The direct signal from the
transmitter arrives enormously stronger than any aircraft echo, and you must subtract it
adaptively before anything else is visible. That single problem will teach you more about
adaptive filtering than any textbook.

---

[← Navigation & Timing](./10_navigation_and_timing.md) · [Catalogue index](./README.md) · [Next: Science →](./12_science_and_radio_astronomy.md)
