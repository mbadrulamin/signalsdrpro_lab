# 🟡 Lab 02 — Enhanced WBFM with Visualization

> **Time:** 45 minutes  
> **Difficulty:** Beginner-Intermediate  
> **Blocks added:** QT GUI Freq Sink, Waterfall Sink, Time Sink, Rational Resampler  
> **Concepts:** Spectrum analysis, resampling, GUI interaction

---

## 🎯 Goal

Add **visual feedback** and **audio resampling** to the simple receiver. You'll see what the FM signal actually looks like in the frequency and time domains, and produce cleaner 48 kHz audio.

---

## 📐 Architecture

```
                            ┌───────────────────────┐
                       ┌───▶│ QT GUI Freq Sink       │
                       │    │ (spectrum view)        │
                       │    └───────────────────────┘
┌──────────────┐       │    ┌───────────────────────┐
│ USRP Source  │───────┼───▶│ QT GUI Waterfall Sink  │
│   (B210)     │       │    │ (spectrum over time)   │
└──────────────┘       │    └───────────────────────┘
                       │    ┌───────────────────────┐
                       ├───▶│ QT GUI Time Sink       │
                       │    │ (raw IQ waveform)      │
                       │    └───────────────────────┘
                       │    ┌──────────────────┐     ┌─────────────┐     ┌────────────┐
                       └───▶│ Rational         │────▶│ WBFM Receive│────▶│ Audio Sink │
                            │ Resampler        │     │             │     │            │
                            │ (2M → 384k SPS)  │     └─────────────┘     └────────────┘
                            └──────────────────┘
```

**Four branches** from the USRP Source: three for visualization, one for audio.

---

## 📋 New Blocks Explained

### 1. Rational Resampler (`rational_resampler_xxx`)

This block changes the sample rate by a **rational ratio** $I/D$ (interpolation/decimation).

**Why we need it:** The WBFM Receive block expects `quad_rate = audio_rate × audio_decimation`. For nice 48 kHz audio with decimation of 8, we need `quad_rate = 384,000 Hz`. Our USRP runs at 2 MSPS.

**Math:**
$$
\text{Output rate} = \text{Input rate} \times \frac{I}{D}
$$

We want $2,000,000 \times \frac{I}{D} = 384,000$

$$
\frac{I}{D} = \frac{384,000}{2,000,000} = \frac{384}{2000} = \frac{12}{62.5} = \frac{24}{125}
$$

So: **Interpolation = 24, Decimation = 125**.

| Parameter | Value | Why |
|---|---|---|
| Type | `ccc` (complex in, complex out, float taps) | IQ signal throughout |
| Interpolation | `24` | Upsample factor |
| Decimation | `125` | Downsample factor |
| Taps | `[]` (auto) | GRC computes optimal FIR filter |
| Fractional BW | `0` (auto) | Filter bandwidth chosen automatically |

**What it does internally:**
1. Insert 23 zeros between every input sample (upsampling)
2. Apply a low-pass FIR filter (anti-imaging)
3. Keep every 125th sample (downsampling)

This is called **polyphase filtering** and is computationally efficient.

### 2. QT GUI Freq Sink (`qtgui_freq_sink_x`)

Shows the **power spectral density** of the signal in real-time.

| Parameter | Value |
|---|---|
| Type | Complex |
| FFT Size | 2048 |
| Center Freq | `freq` |
| Bandwidth | `samp_rate` |
| Update Period | 0.10 s |
| Y-axis | -140 to +10 dB |

**What you see:**
- The FM station's spectrum (a wide bump, ~200 kHz wide)
- Other stations as bumps at different offsets
- The noise floor as a roughly flat line
- A spike at 0 Hz (DC offset)

### 3. QT GUI Waterfall Sink (`qtgui_waterfall_sink_x`)

Shows **spectrum over time** — a 2D image where color = power. X-axis is frequency, Y-axis is time (scrolling down).

This is invaluable for:
- Seeing stations turn on/off
- Identifying intermittent signals
- Spotting interference

### 4. QT GUI Time Sink (`qtgui_time_sink_x`)

Shows the **waveform** — amplitude vs time. For a complex signal, it shows I and Q as separate traces.

This lets you see:
- Clipping (signal hitting ±1)
- Noise floor level
- Transients

---

## 🔬 How Resampling Works Mathematically

The rational resampler implements a polyphase FIR filter. Let's derive the filter length.

For our 24/125 resampler:
- Input rate: 2 MSPS
- Output rate: 384 kSPS
- The "effective" sampling rate for filter design = `lcm(24, 125) × 2 MSPS / 125` ≈ 48 MSPS

The filter must suppress images at multiples of the input rate while passing our signal up to ~100 kHz.

**Typical filter specs:**
- Passband: 0–180 kHz (the FM signal)
- Stopband: >192 kHz (image frequencies)
- Stopband attenuation: ≥60 dB
- Filter length: ~100–200 taps

GNU Radio's `firdes.low_pass` computes this automatically when taps=`[]`.

---

## 📡 What You'll Observe

### On the Frequency Sink
When tuned to 100.1 MHz:
- A bump spanning ~180 kHz centered at 0 Hz
- Bumps at ±200 kHz, ±400 kHz for neighboring stations
- Noise floor at -90 to -110 dBFS

When you adjust gain:
- All signals rise/fall together
- Noise floor rises with gain (LNA noise)

### On the Waterfall
- Vertical bright lines = active stations
- Horizontal scrolling = time progression
- Fading = multipath (signal bouncing off buildings)
- Pulsing = intermittent transmitters

### On the Time Sink
- Two traces: I (blue) and Q (red)
- A dense cloud of noise around 0
- Occasional large excursions = strong signals

---

## 🎛️ Interactive Controls

Three GUI controls appear at the top:

1. **Station Frequency** (slider + textbox) — tune 87.5–108 MHz
2. **RF Gain** (slider + textbox) — adjust 0–76 dB
3. **Sample Rate** (dropdown or textbox) — try 1 MSPS vs 2 MSPS

Try these experiments:
- Sweep `freq` slowly across the band — watch the waterfall paint
- Set `gain` = 0 and watch the signal disappear into noise
- Increase `samp_rate` to 2 MSPS — see more spectrum, but CPU load increases

---

## 🔧 Parameters Summary

| Block | Key Parameter | Value |
|---|---|---|
| Variable `samp_rate` | — | 2,000,000 |
| Variable `freq` | — | 100,000,000 |
| Variable `gain` | — | 40 |
| USRP Source | Sample Rate | `samp_rate` |
| USRP Source | Ch0 Center Freq | `freq` |
| USRP Source | Ch0 Gain | `gain` |
| USRP Source | Ch0 Antenna | `TX/RX` |
| Rational Resampler | Interp | 24 |
| Rational Resampler | Decim | 125 |
| WBFM Receive | Quadrature Rate | 384000 |
| WBFM Receive | Audio Decimation | 8 |
| Audio Sink | Sample Rate | 48000 |

---

## 🧪 Testing the Flowgraph

1. **Open:** `gnuradio-companion lab02_enhanced_wbfm.grc`
2. **Execute:** Press F5
3. **Observe the waterfall** — identify all visible FM stations
4. **Tune** the slider to a station, confirm clear audio
5. **Zoom** the frequency sink to 500 kHz span, verify the ~200 kHz FM bandwidth
6. **Reduce gain** to 0, confirm signal disappears
7. **Increase gain** to 70, check for clipping in time sink

---

## ❓ Questions to Ponder

1. Why does the waterfall scroll downward? → New time samples are at the top, old ones at the bottom.

2. Why do we see a spike at 0 Hz in the frequency sink? → DC offset from the mixer LO leakage.

3. What would happen if we skip the rational resampler and feed 2 MSPS directly into WBFM Receive? → Audio decimation of 8 would give 250 kHz audio rate, way too high for the audio sink.

4. Why is the resampler `ccc` type (complex in, complex out, float taps)? → The IQ signal stays complex throughout; only the filter taps are real.

---

## 📚 Key Takeaways

- **Visualization is essential** for debugging — you can't fix what you can't see.
- **Resampling** lets you match sample rates throughout the flowgraph.
- **The waterfall is the SDR's "eyes"** — it shows you everything happening in the spectrum.
- **Rational ratios** are how GNU Radio handles arbitrary sample rate changes.

---

**Next:** [Lab 03 — Advanced WBFM with AGC & Squelch →](../lab03_advanced_wbfm/README.md)
