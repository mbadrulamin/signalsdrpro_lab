# 🔭 12 — Science & Radio Astronomy

> Point your antenna at the sky and you are doing astronomy. Not metaphorically — the same
> hydrogen line that professional observatories map is detectable from a garden with equipment
> costing less than a phone.
>
> [← Radar & Sensing](./11_radar_and_sensing.md) · [Catalogue index](./README.md) · [Next: Security Research →](./13_security_research.md)

---

## What makes radio astronomy different

Everything else in this catalogue is a **signal someone transmitted**. Astronomical sources emit
**noise** — broadband, incoherent, and usually weaker than your receiver's own noise floor. You
are not decoding; you are **measuring power** with enough precision to see a small excess.

The instrument you need is a **total-power radiometer**, and its sensitivity is given by the
radiometer equation:

$$
\frac{\Delta T}{T_{\text{sys}}} = \frac{1}{\sqrt{B \cdot \tau}}
$$

where $B$ is bandwidth and $\tau$ is integration time. With $B = 2$ MHz and $\tau = 60$ s:

$$
\frac{\Delta T}{T_{\text{sys}}} = \frac{1}{\sqrt{2\times10^6 \times 60}} = 9.1 \times 10^{-5}
$$

So a system at 150 K can detect a **0.014 K** change. That is why integration matters more than
gain: you buy sensitivity with *time*, not amplification. It is the same processing-gain idea as
[Fundamentals 06](../01_fundamentals/06_noise_snr_and_gain.md), applied to noise instead of signal.

---

## The hydrogen line — the accessible one

**1420.405751 MHz.** Neutral hydrogen throughout the galaxy emits here when the electron and
proton spins flip relative alignment. It is:

- **Within your SDR's tuning range** ✅
- **Protected** — no terrestrial transmissions are permitted in this band, so it is quiet
- **Everywhere** — the Milky Way is full of hydrogen, so you need only point at the galactic plane
- **Doppler-shifted** by the rotation of the galaxy, which means you can *measure that rotation*

| Project | Diff | Needs | What you get |
|---|---|---|---|
| **Detect the hydrogen line at all** | ⭐⭐⭐⭐ | ✅📡🔊 | A bump in an averaged spectrum when pointed at the galactic plane |
| **Measure galactic rotation** | ⭐⭐⭐⭐⭐ | ✅📡🔊 | Doppler shift vs galactic longitude → **a rotation curve** |
| **Map the galactic plane** | ⭐⭐⭐⭐⭐ | ✅📡🔊 | Scan in longitude, build a position-velocity diagram |
| **Detect the flat rotation curve** | ⭐⭐⭐⭐⭐ | ✅📡🔊 | The observational evidence for **dark matter**, from your garden |

**What you need:** a 1–1.5 m dish or a horn antenna (a cardboard-and-foil horn genuinely works),
a 1420 MHz LNA at the feed, and patience for integration. The signal is a few kelvin against a
system temperature of ~100 K, so you need minutes of averaging per pointing.

---

## Solar and planetary

| Source | Frequency | Character | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Solar radio bursts (Type III)** | 20–400 MHz | fast frequency drift | ⭐⭐⭐ | ✅📡 | 🟢 Electron beams from flares. Visible as diagonal streaks on a waterfall |
| **Solar Type II bursts** | 20–150 MHz | slow drift | ⭐⭐⭐⭐ | ✅📡 | 🟢 Shock waves from coronal mass ejections |
| **Quiet Sun continuum** | 1–10 GHz | steady thermal | ⭐⭐⭐ | ✅📡🔊 | 🟢 Point at the Sun and watch total power rise. **A great first radiometer test** |
| **Solar transit measurement** | any | drift-scan | ⭐⭐⭐ | ✅📡🔊 | 🟢 Let the Sun drift through your beam to measure the beam pattern |
| **Jupiter decametric (Io-B storms)** | 18–24 MHz | bursty, "popcorn" | ⭐⭐⭐⭐ | 🔻📡 | 🟢 Jupiter's magnetosphere, modulated by the moon Io. Predictable from ephemerides |
| **Jupiter S-bursts** | 20 MHz | millisecond bursts | ⭐⭐⭐⭐⭐ | 🔻📡 | 🟢 |
| **Lunar reflection (EME)** | 144, 432, 1296 MHz | see [Amateur](./07_amateur_radio.md) | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **Meteor radio afterglow** | VHF | see [Weather](./05_weather_and_environment.md) | ⭐⭐ | ✅📡 | 🟢 |

---

## Deep sky

| Source | Frequency | Character | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Galactic background continuum** | 100–500 MHz | broadband synchrotron | ⭐⭐⭐ | ✅📡🔊 | 🟢 Sky brightness varies with galactic latitude — measurable as a total-power change |
| **Cassiopeia A** | 400 MHz–5 GHz | supernova remnant | ⭐⭐⭐⭐ | ✅📡🔊 | 🟢 One of the brightest radio sources in the sky |
| **Cygnus A** | 1–5 GHz | radio galaxy | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **Taurus A (Crab Nebula)** | 1–5 GHz | supernova remnant | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **Sagittarius A\*** | 1420 MHz+ | galactic centre | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **Pulsars (e.g. B0329+54)** | 300–1400 MHz | periodic pulses | ⭐⭐⭐⭐⭐ | ✅📡🔊🖥️ | 🟢 Needs folding at the known period and dedispersion. Genuinely hard, and genuinely done by amateurs |
| **OH maser lines** | 1612, 1665, 1667, 1720 MHz | narrow lines | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 |
| **Cosmic microwave background** | 1–30 GHz | 2.7 K everywhere | ⭐⭐⭐⭐⭐ | 🔺📡🔊 | 🟢 Detecting it requires careful absolute calibration |
| **Fast radio bursts** | 400–1400 MHz | millisecond, dispersed | ⭐⭐⭐⭐⭐ | ✅📡🔊🖥️ | 🟢 Beyond amateur reach for now, but the technique is the same as pulsars |

---

## Techniques and instrumentation

| Project | Diff | Needs | Notes |
|---|---|---|---|
| **Total-power radiometer** | ⭐⭐⭐ | ✅🔊 | The foundation. Measure power, integrate, calibrate against hot/cold loads |
| **Dicke switching** | ⭐⭐⭐⭐ | ✅🔊 | Alternate between antenna and reference load to cancel gain drift |
| **Noise-source calibration** | ⭐⭐⭐ | ✅ | Inject a known noise temperature to convert counts to kelvin |
| **Drift scanning** | ⭐⭐⭐ | ✅📡 | Let the Earth rotate the source through your fixed beam |
| **Spectral averaging / integration** | ⭐⭐⭐ | ✅🖥️ | Thousands of FFTs averaged; the radiometer equation in code |
| **Interferometry (two antennas)** | ⭐⭐⭐⭐⭐ | ✅📡🖥️ | Correlate two receivers for angular resolution. **Your B210's two coherent channels make this possible** |
| **Pulsar folding & dedispersion** | ⭐⭐⭐⭐⭐ | ✅🖥️ | |
| **RFI excision** | ⭐⭐⭐⭐ | ✅🖥️ | Removing terrestrial interference is most of the practical work |

---

## Try this first: point at the Sun

Before you attempt hydrogen, prove your radiometer works on the brightest source in the sky.

```
1. Any directional antenna (even a dish for satellite TV) + LNA
2. Tune anywhere quiet in 1–2 GHz, 2 MSPS
3. Compute mean |x|^2 over 1-second blocks and log it
4. Point at cold sky. Record for a minute.
5. Point at the Sun. Record for a minute.
```

The Sun should raise the total power measurably — typically a fraction of a dB with a small
antenna, more with a dish. **If you can see that step, you have a working radiometer**, and
everything else in this file is a matter of more integration and better pointing.

Then repeat it as a **drift scan**: point where the Sun *will be*, start recording, and let the
Earth's rotation carry the Sun through your beam. The resulting curve is your antenna's beam
pattern, measured using a celestial source. That is a real observatory technique.

---

## Then: hydrogen, and the rotation of the galaxy

Once the radiometer works:

1. Tune to **1420.4 MHz**, 2 MSPS, and average thousands of FFTs
2. Point at a **cold reference** patch of sky, save the spectrum
3. Point at the **galactic plane**, save the spectrum
4. Divide one by the other — the hydrogen line emerges as a peak

Then do it at several galactic longitudes. The line's **Doppler shift changes with direction**,
because you are looking at gas orbiting the galactic centre at different angles. Plot shift
against longitude, apply the tangent-point method, and you have measured the **rotation curve of
the Milky Way** — and found it flat, which is the observation that dark matter was invented to
explain.

There is no better demonstration that this hobby is real science.

---

[← Radar & Sensing](./11_radar_and_sensing.md) · [Catalogue index](./README.md) · [Next: Security Research →](./13_security_research.md)
