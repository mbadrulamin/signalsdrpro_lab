# 📊 Fundamentals 01 — Signals Basics

> **What you will learn:** what a signal is; amplitude, frequency and phase; the two ways to
> look at a signal (time and frequency); bandwidth; sampling; and decibels.
> **Before this:** nothing. (New to SDR? Read the [Introduction](./00_introduction_to_sdr.md) first.)
> **Time:** about 30 minutes.

---

## 1. What is a signal?

A **signal** is something that changes over time and carries information.

Examples:

- The voltage from a microphone. It goes up and down with the sound.
- The tiny voltage on an antenna. It goes up and down with the radio waves passing it.
- The brightness of the pixels across a photo. (This one changes over *space*, not time.)

In radio, the signal we care about is almost always a **voltage** that changes over time.
That is what an antenna produces, and what an SDR measures.

---

## 2. The sine wave — the basic building block

The simplest signal is a smooth, repeating wave called a **sine wave**:

```
   +1 |     .-'''-.             .-'''-.
      |   .'       '.         .'       '.
    0 |--'-----------'-------'-----------'----> time
      |                '.   .'
   -1 |                  '-'
      |<------ one cycle ------>|
```

Radio waves, sound waves and the mains electricity in your wall are all built from sine waves.
A sine wave is described by **three numbers**:

### 2.1 Amplitude — how big

**Amplitude** is the height of the wave: how far it swings up and down. For a voltage, it is
measured in **volts (V)**. A louder sound or a stronger radio signal has a bigger amplitude.

### 2.2 Frequency — how fast

**Frequency** is how many complete cycles the wave makes in one second. It is measured in
**hertz (Hz)**. 1 Hz = one cycle per second.

| Prefix | Meaning | Example |
|---|---|---|
| **k**Hz (kilohertz) | thousand cycles per second | Human voice: about 0.3–3.4 kHz |
| **M**Hz (megahertz) | million cycles per second | FM radio: 87.5–108 MHz |
| **G**Hz (gigahertz) | billion cycles per second | Wi-Fi: 2.4 GHz and 5 GHz |

When you tune a radio to "98.0 FM", you are choosing a signal with a frequency of 98.0 MHz:
98 million cycles every second.

### 2.3 Phase — where in the cycle

**Phase** says *where in its cycle* the wave is at a given moment. It is measured in
**degrees** (0° to 360° for one full cycle) or **radians** (0 to 2π).

Think of the hands of two clocks that run at the same speed. If one clock is set 15 minutes
ahead, it is always a quarter-turn (90°) in front. The two clocks have the same speed
(frequency) but a different **phase**.

Two waves with the same frequency but a phase difference of **180°** are exact opposites. When
you add them, they cancel out to zero. Noise-cancelling headphones work this way.

<details>
<summary><b>Going deeper:</b> the sine wave as an equation</summary>

A sine wave with amplitude $A$, frequency $f$ and phase $\phi$ is:

$$
s(t) = A \cdot \sin(2\pi f t + \phi)
$$

- $t$ is time in seconds.
- $2\pi f$ is often written $\omega$ ("omega"), the **angular frequency**, in radians per second.
- Two waves $\sin(2\pi f t)$ and $\sin(2\pi f t + \pi)$ are 180° ($\pi$ radians) apart and cancel.
</details>

---

## 3. Two ways to look at a signal

### 3.1 The time domain — like an oscilloscope

A **time-domain** view shows the signal's value (up the side) against time (along the bottom).
It is the wiggly line you just saw. An **oscilloscope** shows signals this way.

### 3.2 The frequency domain — like a spectrum analyser

A **frequency-domain** view shows **how much of each frequency** the signal contains. Frequency
goes along the bottom, strength goes up the side. A **spectrum analyser** shows signals this
way — and so does the spectrum display in GNU Radio (the "QT GUI Frequency Sink").

A pure 1 kHz sine wave looks like this:

```
 strength
     |        |
     |        |       ← all the energy is at exactly 1 kHz
     |        |
     +--------+----------------> frequency
             1 kHz
```

A real radio band looks more like this — many stations side by side, each one a "hump":

```
 strength
     |     ▂▄█▄▂          ▃▆█▆▃        ▂▅▂
     |  ▁▂▃█████▃▂▁▁▁▁▁▂▃███████▃▂▁▁▁▂▃███▃▂▁
     +------------------------------------------> frequency
         station A        station B     station C
```

> 💡 **Why this matters.** In the time domain, many stations added together look like one
> messy wiggle. You cannot see where one ends and the next begins. In the frequency domain, each
> station sits in its own place. **This is why the frequency view is the most useful view in
> radio.** You will use it in every lab.

### 3.3 Moving between the two views

A mathematical tool called the **Fourier transform** converts a signal from the time view to
the frequency view. The computer version is the **FFT** (Fast Fourier Transform). You do not
need to calculate it by hand — GNU Radio does it for you every time it draws a spectrum.

The key idea: **any signal, however complicated, can be built by adding up sine waves** of
different frequencies, amplitudes and phases. The Fourier transform tells you which sine waves
you need, and how much of each.

<details>
<summary><b>Going deeper:</b> the Fourier transform equations</summary>

From time to frequency:

$$
S(f) = \int_{-\infty}^{\infty} s(t) \cdot e^{-j 2\pi f t} \, dt
$$

From frequency back to time (the inverse transform):

$$
s(t) = \int_{-\infty}^{\infty} S(f) \cdot e^{j 2\pi f t} \, df
$$

The $e^{j 2\pi f t}$ term is a spinning arrow. You will meet it properly in
[Fundamentals 02](./02_iq_sampling.md).
</details>

---

## 4. Bandwidth — how wide a signal is

**Bandwidth** is the range of frequencies a signal takes up. It is the *width* of its hump on
the frequency view.

| Signal | Bandwidth |
|---|---|
| A pure sine wave | 0 Hz — a single thin line |
| Telephone voice (300 Hz to 3.4 kHz) | 3.1 kHz |
| Walkie-talkie voice (narrow FM) | about 10–15 kHz |
| One FM broadcast station | about **200 kHz** (FM stations are 200 kHz apart) |
| One digital TV channel (DVB-T2) | about 7.6 MHz, inside an 8 MHz channel |

Wider signals can carry more information. A TV channel is about 40 times wider than an FM
station, because video needs far more data than sound.

> 💡 You will learn in [Fundamentals 04](./04_fm_theory.md) why an FM station is so much wider
> than the music it carries.

---

## 5. Sampling — turning a wave into numbers

A computer cannot store a smooth wave. It can only store a list of numbers. So an SDR
**measures** the signal many times per second, and stores each measurement. Each measurement
is called a **sample**.

```
 value
   |    •   •                     • = one sample
   |  •       •
   |•           •           •
 --+--------------•-------•------> time
   |                •   •
   |                  •
```

The **sample rate** is how many samples are taken each second. It is measured in
**samples per second** (S/s or SPS). You will often see:

- **kSPS** — thousand samples per second
- **MSPS** — million samples per second. "2 MSPS" = 2,000,000 samples every second.

### 5.1 How fast must you sample? (the Nyquist rule)

If you sample too slowly, you miss the wiggles, and you get a **wrong** signal. The rule is
called the **Nyquist–Shannon sampling theorem**:

> **For ordinary (single-number) samples, the sample rate must be more than twice the highest
> frequency in the signal.**

Example: CD audio goes up to 20 kHz. CDs use 44.1 kSPS, which is a bit more than 2 × 20 kHz.

An SDR is a little different. It records **two** numbers per sample, called **I and Q**
([Fundamentals 02](./02_iq_sampling.md) explains why). With I and Q, the rule becomes simpler:

> **For IQ samples, the sample rate equals the width of spectrum you can see.**
> 2 MSPS lets you see a 2 MHz-wide slice of the radio spectrum.

So to receive one 200 kHz FM station, you need at least 200 kSPS of IQ samples. In practice,
the labs use 1 or 2 MSPS. The extra room makes the filters easier to build, and lets you see
the neighbouring stations too.

### 5.2 What goes wrong if you sample too slowly: aliasing

If a signal is faster than the sampling can follow, it does not simply disappear. It shows up
**at the wrong frequency**, pretending to be a slower signal. This is called **aliasing**.

You have seen aliasing in films: a car's wheels sometimes seem to turn slowly backwards. The
camera takes pictures (samples) too slowly to follow the fast-turning wheel.

> ⚠️ **Aliasing cannot be undone.** Once a false signal is mixed in, there is no way to tell it
> apart from a real one. The only cure is to filter out the fast signals *before* sampling.
> Every SDR has a hardware filter for exactly this reason (the `bw0` setting you will meet in
> Lab 01).

---

## 6. Decibels (dB) — the language of signal strength

### 6.1 Why we need decibels

Radio signals cover a huge range of strengths. A signal next to a transmitter can be
**a million million times** stronger than a weak one far away. Numbers like 0.000000000001
are hard to read and easy to get wrong.

The **decibel (dB)** fixes this. It uses a **logarithm**, which turns "how many times bigger"
into "how many steps bigger". Multiplying becomes adding.

### 6.2 The five numbers to remember

| Change in power | Change in dB |
|---|---|
| ×2 (double) | **+3 dB** |
| ×10 | **+10 dB** |
| ×100 | **+20 dB** |
| ×1000 | **+30 dB** |
| ÷2 (half) | **−3 dB** |

Every extra **+10 dB** means **ten times** more power. So:

- +20 dB = 10 × 10 = **100 times** more power.
- +60 dB = 10 × 10 × 10 × 10 × 10 × 10 = **1,000,000 times** more power.

Going from −100 dBm to −40 dBm is a rise of 60 dB, which is a million times more power.

### 6.3 dB, dBm and dBFS

A plain **dB** is always a **comparison** between two things ("this is 10 dB stronger than
that"). Add letters to compare against a fixed reference:

| Unit | Compared with | Where you see it |
|---|---|---|
| **dB** | another signal | "The filter removes 40 dB", "gain = 30 dB" |
| **dBm** | 1 milliwatt (0.001 W) | Real power at an antenna. 0 dBm = 1 mW. A usable FM station is about −90 dBm |
| **dBFS** | the largest number the ADC can output ("full scale") | GNU Radio's displays. 0 dBFS is the maximum. Everything is negative below it |

> ⚠️ **GNU Radio's spectrum display shows dBFS, not dBm.** It tells you how strong a signal is
> *compared with the radio's maximum*, not its real power in watts. Use it to compare signals
> with each other, not to measure absolute power.

<details>
<summary><b>Going deeper:</b> the decibel formulas</summary>

For power:

$$
\text{dB} = 10 \cdot \log_{10}\!\left(\frac{P_2}{P_1}\right)
$$

For voltage or amplitude (because power is proportional to voltage squared):

$$
\text{dB} = 20 \cdot \log_{10}\!\left(\frac{V_2}{V_1}\right)
$$

So doubling the **power** is +3 dB, but doubling the **voltage** is +6 dB. Mixing up the 10
and the 20 is the most common beginner mistake. [Fundamentals 06](./06_noise_snr_and_gain.md)
covers this in detail.
</details>

---

## ✅ Summary

| Word | Symbol | Unit | Plain meaning |
|---|---|---|---|
| Amplitude | $A$ | volts (V) | How big the wave is |
| Frequency | $f$ | hertz (Hz) | How many cycles per second |
| Phase | $\phi$ | degrees or radians | Where in its cycle the wave is |
| Bandwidth | $B$ | Hz | How wide the signal is on the frequency view |
| Sample rate | $f_s$ | samples per second (SPS) | How many measurements per second |
| Decibel | dB | — | A ratio of powers on a log scale. +10 dB = ×10 |

- A signal can be viewed over **time** (oscilloscope) or over **frequency** (spectrum). Radio
  mostly uses the frequency view.
- With IQ samples, the sample rate equals the width of spectrum you can see.
- Sampling too slowly causes **aliasing**: false signals that cannot be removed later.
- +3 dB doubles the power. +10 dB multiplies it by ten.

## 🧠 Check yourself

1. An FM station is at 98.0 MHz. How many cycles per second is that?
   <details><summary>Answer</summary>98 million (98,000,000).</details>
2. Two sine waves have the same frequency and amplitude, but are 180° apart. What do you get
   when you add them?
   <details><summary>Answer</summary>Zero — they cancel.</details>
3. Your SDR samples IQ at 2 MSPS. How wide a slice of spectrum can you see?
   <details><summary>Answer</summary>2 MHz.</details>
4. Signal A is 30 dB stronger than signal B. How many times more power does A have?
   <details><summary>Answer</summary>1000 times (10 × 10 × 10).</details>
5. The spectrum display says a station is at −40 dBFS. Does that mean the station's real power
   is −40 dBm?
   <details><summary>Answer</summary>No. dBFS is relative to the radio's maximum level, not
   to 1 milliwatt. It depends on the gain setting too.</details>

**Next:** [Fundamentals 02 — IQ Sampling →](./02_iq_sampling.md)
