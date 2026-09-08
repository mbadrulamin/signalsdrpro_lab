# 📻 Fundamentals 04 — FM Modulation Theory

> **Prerequisite:** RF Basics  
> **Time to read:** 40 minutes

---

## What Is Modulation?

**Modulation** is the process of encoding information onto a high-frequency **carrier** signal so it can be transmitted over the air.

Without modulation, we couldn't broadcast audio wirelessly because:
1. Audio frequencies (20 Hz – 20 kHz) can't radiate efficiently from antennas (you'd need antennas kilometers long).
2. Everyone's audio would overlap — no way to separate stations.

By modulating different stations onto different carrier frequencies, we can tune to one at a time.

---

## Amplitude Modulation (AM) — The Simple Way

In **AM**, the audio signal controls the **amplitude** of the carrier:

$$
s_{AM}(t) = \bigl[1 + m \cdot x(t)\bigr] \cdot \cos(2\pi f_c t)
$$

Where $x(t)$ is the audio and $f_c$ is the carrier frequency.

**Problems with AM:**
- Noise adds to amplitude → noisy reception
- Lightning, motors, etc. create AM noise
- Can't achieve high fidelity

**Still used for:** AM broadcast (530–1700 kHz), aviation VHF (118–137 MHz), shortwave.

---

## Frequency Modulation (FM) — The Better Way

In **FM**, the audio signal controls the **instantaneous frequency** of the carrier:

$$
f(t) = f_c + \Delta f \cdot x(t)
$$

Where:
- $f_c$ is the center (carrier) frequency
- $\Delta f$ is the **frequency deviation** (maximum frequency swing)
- $x(t)$ is the modulating audio, normalized to [-1, +1]

The transmitted signal is:

$$
s_{FM}(t) = A \cdot \cos\!\left(2\pi f_c t + 2\pi \Delta f \int_0^t x(\tau) \, d\tau\right)
$$

Notice the **integral of audio** — that's what makes FM work.

**Advantages of FM over AM:**
- Noise is mostly amplitude-based → FM ignores it → **cleaner sound**
- "Capture effect": strongest signal suppresses weaker ones → **no co-channel interference**
- Supports **stereo** and **subsidiary signals** (RDS, SCA)

---

## Frequency Deviation

The **frequency deviation** $\Delta f$ determines how much the carrier can swing from its center.

| FM Type | Deviation | Typical use |
|---|---|---|
| Narrowband FM (NBFM) | ±5 kHz | Amateur radio, police, aviation |
| Wideband FM (WBFM) | ±75 kHz | FM broadcast (88–108 MHz) |

For commercial FM broadcast, $\Delta f = 75$ kHz is the standard. This is why we call it **Wideband FM**.

---

## Carson's Rule — How Much Bandwidth Does FM Need?

An FM signal has theoretically **infinite** bandwidth (sidebands extend forever). But most of the power is in a finite bandwidth given by **Carson's rule**:

$$
\boxed{ B \approx 2(\Delta f + f_m) }
$$

Where $f_m$ is the **maximum audio frequency**.

For WBFM broadcast:
- $\Delta f = 75$ kHz
- $f_m = 15$ kHz (mono) or 53 kHz (with stereo + RDS)

Mono: $B \approx 2(75 + 15) = 180$ kHz  
Stereo + RDS: $B \approx 2(75 + 53) = 256$ kHz

That's why FM stations are spaced **200 kHz apart** (e.g., 100.1, 100.3, 100.5...).

---

## The FM Spectrum — MPX (Multiplex) Signal

After demodulating an FM broadcast signal, you don't get audio directly — you get the **MPX baseband**, which contains:

```
Amplitude
  |
  | [L+R]   [Pilot]    [L-R DSB-SC]   [RDS]
  | 0-15kHz  19kHz    23-53kHz        57kHz
  |____________________________________________________
  0    15    19    23        53        57    100  kHz
```

Components:
- **0–15 kHz:** Mono sum signal (L+R) — all FM radios play this
- **19 kHz:** Pilot tone (reference for stereo)
- **23–53 kHz:** L−R stereo difference signal, DSB-SC modulated at 38 kHz
- **57 kHz:** RDS (Radio Data System) — station name, song title, etc.

To get stereo L and R:
$$
L = \frac{(L+R) + (L-R)}{2} \quad\quad R = \frac{(L+R) - (L-R)}{2}
$$

This is what Lab 04 (Stereo WBFM) will decode manually!

---

## Pre-Emphasis and De-Emphasis

High audio frequencies are more susceptible to noise. To compensate, broadcasters **boost** (pre-emphasize) high frequencies before transmission, and receivers **cut** (de-emphasize) them afterward.

The filter is a simple first-order RC:

$$
H(s) = \frac{1}{1 + s\tau}
$$

Where $\tau$ (tau) is a time constant:
- **75 μs** in North America and South Korea (3 dB at 2.1 kHz)
- **50 μs** in most of the world (3 dB at 3.2 kHz)

If you skip de-emphasis, the FM audio sounds **tinny and harsh** (too much treble). GNU Radio's WBFM Receive block does this internally; in Lab 04 we'll add it manually.

---

## FM Demodulation — How to Recover Audio

The goal of demodulation is to extract the audio $x(t)$ from the FM signal $s_{FM}(t)$.

### Method 1: Quadrature Demodulator (What GNU Radio Uses)

If we have the IQ signal, the instantaneous frequency is just the **derivative of the phase**:

$$
f(t) = \frac{1}{2\pi} \frac{d\phi}{dt}
$$

The **Quadrature Demod** block in GNU Radio computes:

$$
y[n] = \frac{f_s}{2\pi \Delta f} \cdot \arg\!\bigl(s[n] \cdot s^*[n-1]\bigr)
$$

Where $s^*[n-1]$ is the complex conjugate of the previous sample.

This gives the **instantaneous frequency deviation**, which is exactly the audio signal.

### Method 2: Discriminator

A frequency-dependent circuit whose output voltage is proportional to input frequency. Older analog radios used this.

### Method 3: Phase-Locked Loop (PLL)

Lock an oscillator to the incoming FM signal; the control voltage needed to track it is the audio.

GNU Radio's WBFM Receive block uses Method 1 — the simplest for digital implementation.

---

## Mathematical Summary

FM signal:
$$
s_{FM}(t) = A \cos\!\left(2\pi f_c t + 2\pi \Delta f \int x(\tau)\,d\tau\right)
$$

Carson's rule (bandwidth):
$$
B \approx 2(\Delta f + f_m)
$$

Quadrature demodulator:
$$
y[n] \propto \arg(s[n] \cdot s^*[n-1])
$$

De-emphasis:
$$
H(s) = \frac{1}{1 + s\tau}, \quad \tau = 75\,\mu\text{s (US) or } 50\,\mu\text{s (world)}
$$

---

## 🧠 Self-Check

1. What is the maximum deviation of commercial WBFM? (**Answer:** ±75 kHz)
2. Why is FM more noise-resistant than AM? (**Answer:** Noise mainly affects amplitude; FM demodulators ignore amplitude.)
3. What is the purpose of the 19 kHz pilot tone? (**Answer:** Reference for recovering the 38 kHz subcarrier used for stereo.)
4. If your FM audio sounds "bright" and tinny, what filter is missing? (**Answer:** De-emphasis.)

---

Now that you have the fundamentals, you're ready to build real flowgraphs!

**Next:** [Lab 01 — Simplest WBFM Receiver →](../02_flowgraphs/lab01_simple_wbfm/README.md)
