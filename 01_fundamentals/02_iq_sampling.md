# 🧠 Fundamentals 02 — IQ Sampling (The Heart of SDR)

> **Prerequisite:** Signals & Systems Basics  
> **Time to read:** 45 minutes (read slowly — this is the most important concept in SDR)

---

## The Big Question: Why I and Q?

Every SDR — from your $20 RTL-SDR to the SignalSDR Pro to the $5000 USRP B210 — outputs data as **pairs of numbers called I and Q**. Why not just a single number like a sound card does?

**Answer:** A single sequence of real samples cannot represent both **positive and negative frequencies** unambiguously. IQ sampling solves this by using **complex numbers**.

This concept is so fundamental that if you don't understand it, the rest of SDR will feel like magic. Let's build it up carefully.

---

## Step 1: The Problem with Real Sampling

Imagine you sample a signal $x(t)$ with a pure analog-to-digital converter (ADC), getting real numbers:

$$
x[n] = x(n \cdot T_s) \quad \text{where } T_s = \frac{1}{f_s}
$$

By the sampling theorem, the spectrum of $x[n]$ is periodic with period $f_s$. If the original signal had both positive and negative frequencies, they **overlap** in the sampled version and become indistinguishable.

```
Original spectrum:
       |           |
  -----+-----------+-----  frequency
      -B           B

After real sampling:
  |           |           |           |
--+-----------+-----------+-----------+--  frequency
 -B          +B         fs-B        fs+B
```

For a **real** signal, the negative-frequency part is just the complex conjugate of the positive part — so nothing is lost. But for a **complex** signal (which is what we want to represent in an SDR), the positive and negative halves carry **different information**.

---

## Step 2: The Solution — Complex Sampling

Instead of one real number per sample, we record **two real numbers**: the **In-phase** component $I$ and the **Quadrature** component $Q$. Together they form a complex number:

$$
s[n] = I[n] + j \cdot Q[n]
$$

Mathematically, this is equivalent to mixing the incoming RF signal with **two local oscillators 90° out of phase**:

```
                    ┌─────┐
                    │ cos │───→ I(t)
RF in ───→  Mixer ──┤     │
                    └─────┘
         │
         │         ┌─────┐
         └→ Mixer ─┤ sin │───→ Q(t)
                    └─────┘
```

The two local oscillators are:
$$
\cos(2\pi f_c t) \quad \text{and} \quad \sin(2\pi f_c t) = \cos(2\pi f_c t - \tfrac{\pi}{2})
$$

The **Q** oscillator is **90° delayed** relative to the **I** oscillator. Hence the name *quadrature*.

---

## Step 3: Complex Numbers as Rotating Vectors

Every IQ sample $I + jQ$ is a point in the complex plane. As the signal evolves over time, this point traces out a path.

For a **pure sine wave** at frequency $f$, the IQ samples trace a **circle**:

$$
s(t) = e^{j 2\pi f t} = \cos(2\pi f t) + j \sin(2\pi f t)
$$

- If $f > 0$, the vector rotates **counterclockwise**.
- If $f < 0$, the vector rotates **clockwise**.

🎯 **This is why IQ sampling can distinguish positive and negative frequencies!**

```
   Q                     Q
   |  ●                  |   ●
   | /                   | \
   |/  (f > 0)           |  \ (f < 0)
   I                     I
```

---

## Step 4: Negative Frequencies Are Real

You were probably taught in school that "frequency is always positive." That's true for **real** signals (a real cosine has only one positive-frequency line, but mathematically it's the sum of a positive and negative frequency).

But with **complex** (IQ) signals, positive and negative frequencies are distinct. This is extremely useful in SDR because:

- A signal above the LO frequency becomes a **positive** frequency
- A signal below the LO frequency becomes a **negative** frequency

Both can coexist in the same bandwidth without interfering.

### Example: Tuning 100 MHz with an LO at 100 MHz

A station at 100.1 MHz → appears at +100 kHz in the IQ signal.
A station at 99.9 MHz → appears at −100 kHz in the IQ signal.

The total visible bandwidth of ±500 kHz gives us **1 MHz of effective bandwidth** — even though we only sample at 1 MSPS.

> 🤯 **Mind-blowing fact:** By using IQ sampling, we get **twice** the usable bandwidth for the same sample rate, compared to real sampling.

---

## Step 5: What IQ Looks Like in GNU Radio

In GNU Radio, IQ data flows as a stream of **complex numbers** (`gr_complex`, which is `std::complex<float>` in C++ or `numpy.complex64` in Python).

Every block that operates on IQ data consumes and produces complex numbers. The blocks that convert complex to real (or vice versa) are explicitly marked.

| Data Type | GRC Name | Used for |
|---|---|---|
| Complex | `complex` | IQ signals throughout the chain |
| Float | `float` | Audio, demodulated baseband, control values |
| Short | `short` | Compact audio (16-bit PCM) |
| Byte | `byte` | Digital data (e.g., decoded bits) |

The USRP Source block outputs **complex**. The Audio Sink expects **float**. You must convert somewhere — and that's what the WBFM Receive block does for us.

---

## Step 6: Practical IQ Pitfalls

### DC Offset

Mixers are imperfect — some of the LO signal "leaks" into the output, producing a **constant (DC) spike** at frequency 0 in the IQ spectrum. In GNU Radio, you can remove this with a `DC Blocker` filter.

### IQ Imbalance

If the I and Q paths have slightly different gains or aren't exactly 90° apart, the spectrum looks lopsided. GNU Radio's USRP Source has an `IQ Balance` parameter to correct this.

### Image Rejection

Thanks to IQ sampling, the "image" (the unwanted frequency) is **naturally suppressed**. With a real-only sampler, you'd need an expensive analog image-reject filter.

---

## Mathematical Summary

$$
\boxed{ s(t) = I(t) + j \cdot Q(t) = A(t) \cdot e^{j\phi(t)} }
$$

Where:
- $A(t) = \sqrt{I^2 + Q^2}$ is the **instantaneous amplitude** (envelope)
- $\phi(t) = \arctan(Q/I)$ is the **instantaneous phase**
- The instantaneous frequency is $f(t) = \frac{1}{2\pi} \frac{d\phi}{dt}$

> 💡 **FM** modulates the **instantaneous frequency**.  
> **AM** modulates the **instantaneous amplitude**.  
> **PM** modulates the **instantaneous phase**.  
> **QAM** modulates both amplitude and phase simultaneously.

All of modern telecommunications reduces to controlling $I$ and $Q$.

---

## 🧠 Self-Check

Answer these before moving on:
1. What does "Q" stand for, and why is it 90° out of phase with I?
2. Can an IQ signal have a negative frequency? What does that mean physically?
3. If the IQ sample rate is 2 MSPS, what is the maximum usable bandwidth?
4. What is the relationship between $I$, $Q$, and the amplitude $A$?

**Answers:** (1) Quadrature, to allow distinguishing + and − frequencies. (2) Yes, it represents a signal rotating the opposite direction, i.e., below the LO. (3) ±1 MHz = 2 MHz of real bandwidth (or 1 MHz if real). (4) $A = \sqrt{I^2 + Q^2}$.

---

**Next:** [Fundamentals 03 — RF Basics →](./03_rf_basics.md)
