# 🟠 Lab 03 — Advanced WBFM with AGC, Squelch, and Filtering

> **Time:** 1 hour  
> **Difficulty:** Intermediate  
> **New blocks:** Low Pass Filter, AGC2, Power Squelch, Multiply Const  
> **Concepts:** Real-world receiver design, dynamic range, noise gating

---

## 🎯 Goal

Build a **production-quality** FM receiver by adding:
1. **Pre-filter** — removes out-of-band interference before demodulation
2. **AGC** (Automatic Gain Control) — keeps audio level constant regardless of station strength
3. **Squelch** — mutes audio when no station is present (no more hiss!)
4. **Volume control** — user-adjustable audio level

---

## 📐 Architecture

```
┌──────────────┐     ┌──────────────┐     ┌───────────────┐     ┌─────┐
│ USRP Source  │────▶│ Low Pass     │────▶│ Rational      │────▶│ AGC │
│   (B210)     │     │ Filter (FIR) │     │ Resampler     │     │     │
└──────────────┘     └──────────────┘     └───────────────┘     └──┬──┘
                                                                   │
                                                                   ▼
┌────────────┐     ┌───────────────┐     ┌───────────────┐     ┌──────────┐
│ Audio Sink │◀────│ Multiply Const│◀────│ WBFM Receive  │◀────│ Squelch  │
│            │     │ (Volume)      │     │               │     │          │
└────────────┘     └───────────────┘     └───────────────┘     └──────────┘
```

Plus visualization branches (same as Lab 02).

---

## 📋 New Blocks Explained

### 1. Low Pass Filter (`low_pass_filter`)

Placed **immediately after the USRP Source** to restrict the bandwidth before demodulation.

**Why:** Without it, strong out-of-band signals (e.g., cell phones, Wi-Fi, FM stations far from your tuned frequency) can overload the AGC and cause intermodulation.

| Parameter | Value | Why |
|---|---|---|
| Type | `fff` or `ccf` | Complex in, complex out, float taps |
| Decimation | 1 | No rate change |
| Sample Rate | `samp_rate` | Match USRP |
| Cutoff Freq | 100,000 Hz | Half of 200 kHz FM bandwidth |
| Transition Width | 20,000 Hz | Roll-off from pass to stop |
| Window | Hamming | Standard, low sidelobes |

**Filter response:**
- Passband: 0–100 kHz (where FM signal lives)
- Transition: 100–120 kHz
- Stopband: >120 kHz (heavily attenuated)

### 2. AGC2 (`agc2_cc`) — Automatic Gain Control

Keeps the signal level constant despite fading and varying station distances.

| Parameter | Value | Why |
|---|---|---|
| Type | `cc` | Complex in, complex out |
| Reference | 0.5 | Target amplitude (half of full scale) |
| Attack Rate | 0.01 | How fast AGC responds to signal increase |
| Decay Rate | 0.001 | How fast AGC responds to signal decrease |
| Max Gain | 65536 | Maximum amplification (linear, not dB) |
| Min Gain | 1.0 | No attenuation |

**How AGC works:**
$$
y[n] = g[n] \cdot x[n]
$$
$$
g[n] = g[n-1] + \alpha \cdot \bigl(R - |y[n-1]|\bigr)
$$

Where $R$ is the reference level, $\alpha$ is the rate.

**Attack vs Decay:**
- **Attack** (signal gets stronger): fast (0.01) to avoid clipping
- **Decay** (signal gets weaker): slow (0.001) to avoid "pumping" noise

### 3. Power Squelch (`analog_pwr_squelch_cc`)

Mutes the output when signal power drops below a threshold. **No more hissing between stations!**

| Parameter | Value | Why |
|---|---|---|
| Type | `cc` | Complex in, complex out |
| Threshold | -50 dB | Power level below which to mute |
| Alpha | 0.01 | Averaging speed for power estimate |
| Ramp | 0 | Transition samples (0 = hard cut) |
| Gate | True | Drop samples instead of outputting zeros |

**How it works:**
$$
P[n] = \alpha \cdot |x[n]|^2 + (1-\alpha) \cdot P[n-1]
$$

If $P[n] < 10^{\text{threshold}/10}$, output is muted (or zeros sent).

### 4. Multiply Const (`multiply_const_vff`)

Simple volume control — scales the audio by a constant.

| Parameter | Value |
|---|---|
| Type | `ff` | Float in, float out |
| Constant | `volume` (from a GUI slider) |

$$
y[n] = k \cdot x[n]
$$

Where $k$ ranges from 0.0 (mute) to 5.0 (5× volume).

---

## 🔬 Why Each Block Is Where It Is

The order matters enormously. Let's justify:

1. **USRP Source first** — obviously, it's the hardware interface.

2. **Low Pass Filter second** — must come BEFORE any non-linear block. If strong out-of-band signals reach the AGC, the AGC will reduce gain, starving your weak FM station.

3. **Rational Resampler third** — reduces sample rate from 2 MSPS to 384 kSPS. Doing this before AGC/Squelch reduces CPU load (fewer samples to process).

4. **AGC fourth** — operates on complex IQ samples before demodulation. This is critical: FM demodulation is a non-linear process, and AGC works best when the signal is still in its native form.

5. **Squelch fifth** — operates after AGC (so threshold is stable) but before demodulation. The reason: squelch on complex data allows a clean "soft mute" transition.

6. **WBFM Receive sixth** — demodulates the (filtered, gain-controlled, squelched) IQ stream into audio.

7. **Multiply Const last** — audio-domain volume control. Could also be done before the audio sink, but putting it here makes the flowgraph self-contained.

---

## 📡 What You'll Observe

### Before and After AGC

**Without AGC:**
- Distant stations are barely audible
- Nearby stations blast your ears
- Signal fading causes volume fluctuations

**With AGC:**
- All stations at roughly the same volume
- Fading is smoothed out
- The "reference" level sets a consistent loudness

### Before and After Squelch

**Without squelch:** Constant hiss between stations  
**With squelch:** Silence between stations, audio only when tuned to a real station

Adjust the **squelch threshold** with a GUI slider:
- Too sensitive (-70 dB): you hear hiss again
- Too insensitive (-30 dB): weak stations get muted
- Sweet spot: typically -50 to -40 dB

---

## 🎛️ GUI Controls

| Control | Range | Purpose |
|---|---|---|
| Frequency | 87.5–108 MHz | Tune the radio |
| RF Gain | 0–76 dB | Hardware gain (analog) |
| Squelch | -80 to 0 dB | Noise gate threshold |
| Volume | 0.0–5.0 | Audio level (digital) |

---

## 🔧 Tuning Guide

### "Weak stations are quiet"
→ Increase RF gain to 50 dB, lower squelch threshold to -60 dB.

### "Audio volume jumps around"
→ AGC attack/decay rates are too fast. Try attack=0.005, decay=0.0005.

### "Hiss between stations"
→ Squelch threshold is too sensitive. Raise to -40 dB.

### "Audio sounds distorted"
→ Volume constant too high. Lower to 1.0 and turn up your PC speakers.

### "AGC 'pumps' the volume rhythmically"
→ Strong interfering signal is dominating AGC. Make the low-pass filter narrower (cutoff 80 kHz instead of 100 kHz).

---

## 🧪 Testing the Flowgraph

1. **Open:** `gnuradio-companion lab03_advanced_wbfm.grc`
2. **Execute:** Press F5
3. **Tune** to a station, confirm clean audio
4. **Tune** off-station, confirm silence (not hiss)
5. **Adjust squelch** until hiss just disappears
6. **Compare** audio levels between weak and strong stations — should be similar
7. **Set volume to 0** — confirm mute works
8. **Lower RF gain to 10 dB** — AGC should compensate

---

## ❓ Questions to Ponder

1. Why is AGC done on complex IQ, not on the demodulated audio?
   → Because FM demod is non-linear. AGC on audio doesn't help with weak-signal reception.

2. Why does squelch have a "ramp" parameter?
   → To avoid clicks when squelch opens/closes. Ramp = number of samples to fade in/out.

3. What's the difference between RF gain (hardware) and volume (software)?
   → RF gain amplifies the analog signal BEFORE digitization → affects signal-to-noise ratio. Volume just scales digital numbers → no effect on SNR.

4. Why is AGC decay slower than attack?
   → To prevent the "breathing" effect where the receiver keeps pumping gain up/down. Slow decay = smoother audio.

---

## 📚 Key Takeaways

- **Receiver design is an engineering discipline** — each block has a reason and a position.
- **AGC is essential** for real-world operation where signal strengths vary by 1000× or more.
- **Squelch is a quality-of-life feature** that makes SDR radios usable.
- **Filter early, filter often** — prevent strong signals from corrupting weak ones.

---

**Next:** [Lab 04 — Stereo WBFM with Full MPX Decoding →](../lab04_stereo_wbfm/README.md)
