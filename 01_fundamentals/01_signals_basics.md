# 📊 Fundamentals 01 — Signals & Systems Basics

> **Prerequisite:** None. We start from zero. (New to SDR entirely? Read [the introduction](./00_introduction_to_sdr.md) first.)  
> **Time to read:** 30 minutes

---

## What Is a Signal?

A **signal** is any physical quantity that varies over time (or space) and carries information. Examples:

- The voltage at the output of a microphone (varies with sound pressure)
- The current flowing through an antenna (varies with incoming electromagnetic waves)
- The brightness of a pixel in an image (varies over 2D space)

In radio, we care almost exclusively about **voltage signals** — because that's what an antenna produces and what an SDR digitizes.

---

## Three Properties of Every Signal

Every signal can be described by three numbers at every instant:

### 1. Amplitude

**Definition:** The instantaneous value of the signal, measured in volts (V).

A signal $s(t)$ is simply a function that returns a voltage for every time $t$.

Example — a DC signal of 2 volts:
$$
s(t) = 2 \quad \text{for all } t
$$

### 2. Frequency

**Definition:** How often the signal repeats, measured in Hertz (Hz = cycles per second).

Example — a sine wave repeating 1000 times per second (1 kHz):
$$
s(t) = A \cdot \sin(2\pi \cdot 1000 \cdot t)
$$

### 3. Phase

**Definition:** Where in its cycle the signal is at time $t = 0$, measured in radians or degrees.

Two sine waves of the same frequency but different phase look like this:
$$
s_1(t) = \sin(2\pi f t)
$$
$$
s_2(t) = \sin(2\pi f t + \phi)
$$

If $\phi = \pi$ (180°), they are **out of phase** and cancel each other when added.

---

## Time Domain vs Frequency Domain

### Time Domain

A plot of **amplitude vs time**. This is what you see on an oscilloscope.

```
Amplitude
   1 |     /\        /\
     |    /  \      /  \
   0 |---/----\----/----\----> time
     |  /      \  /      \
  -1 | /        \/        \
```

### Frequency Domain

A plot of **amplitude (or power) vs frequency**. This is what you see on a spectrum analyzer or GNU Radio's QT GUI Frequency Sink.

```
Amplitude
   1 |    |
     |    |
     |    |
   0 |----+------------------> frequency
         1 kHz
```

The same signal can be viewed in both domains. Mathematically, the **Fourier Transform** converts a signal from time domain to frequency domain:

$$
S(f) = \int_{-\infty}^{\infty} s(t) \cdot e^{-j 2\pi f t} \, dt
$$

And the **Inverse Fourier Transform** converts back:

$$
s(t) = \int_{-\infty}^{\infty} S(f) \cdot e^{j 2\pi f t} \, df
$$

These equations are fundamental to all of SDR.

---

## Bandwidth

**Definition:** The range of frequencies a signal occupies.

A pure sine wave has **zero bandwidth** — it is a single line at frequency $f$.

A real-world signal like voice (300 Hz – 3.4 kHz) has **bandwidth = 3.1 kHz**.

An FM broadcast signal (mono) has bandwidth ≈ **150 kHz** (because of FM's wider footprint — more on this in FM theory).

An FM broadcast **stereo** signal has bandwidth ≈ **200 kHz**.

**Rule:** The higher the bandwidth, the higher the sample rate you need to digitize it (Nyquist-Shannon).

---

## Nyquist–Shannon Sampling Theorem

To faithfully digitize a signal of bandwidth $B$ Hz, you must sample it at a rate $f_s$ where:

$$
f_s > 2B
$$

For example, to digitize an FM broadcast signal (200 kHz bandwidth), you need a sample rate of **at least 400 kSPS**. In practice, we use 1 MSPS or higher to give headroom for filter roll-off.

> ⚠️ If you sample slower than $2B$, **aliasing** occurs — high frequencies masquerade as low frequencies, corrupting your signal.

---

## Decibels (dB) — The SDR's Native Language

Signal processing uses logarithmic units because signal strengths can vary by factors of **billions** (from thermal noise at -130 dBm to a nearby transmitter at 0 dBm).

### dB = 10 · log₁₀(P₂/P₁)

Common references:
- **dBm** = power relative to 1 milliwatt (e.g., 0 dBm = 1 mW)
- **dBFS** = power relative to full scale (the ADC's maximum)
- **dB** alone = a relative ratio (e.g., "this filter gives +6 dB gain")

### Rule of thumb
- +3 dB ≈ 2× power
- +10 dB = 10× power
- +20 dB = 100× power
- +30 dB = 1000× power

So going from -100 dBm to -40 dBm is a **60 dB** increase, which equals a **1,000,000×** increase in power.

---

## Summary of Key Terms

| Term | Symbol | Unit | Meaning |
|---|---|---|---|
| Amplitude | $A$ | Volts (V) | Instantaneous signal value |
| Frequency | $f$ | Hertz (Hz) | Cycles per second |
| Angular frequency | $\omega = 2\pi f$ | rad/s | Used in math formulas |
| Phase | $\phi$ | radians | Position in cycle at $t=0$ |
| Bandwidth | $B$ | Hz | Range of frequencies occupied |
| Sample rate | $f_s$ | Samples per second (SPS) | How often we measure the signal |
| Decibel | dB | — | Logarithmic power ratio |

---

**Next:** [Fundamentals 02 — IQ Sampling →](./02_iq_sampling.md)
