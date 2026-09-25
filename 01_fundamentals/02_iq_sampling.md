# 🧠 Fundamentals 02 — IQ Sampling (The Heart of SDR)

> **What you will learn:** why every SDR gives you *two* numbers per sample (called **I** and
> **Q**), what "negative frequency" means, and how GNU Radio stores IQ data.
> **Before this:** [Fundamentals 01 — Signals Basics](./01_signals_basics.md).
> **Time:** about 45 minutes. Go slowly — this is the most important idea in SDR.

---

## 1. The question

Every SDR — a $40 RTL-SDR, your SignalSDR Pro, a $1500 USRP — gives you its data as
**pairs of numbers**, called **I** and **Q**. A sound card gives you just one number per sample.
Why does a radio need two?

**Short answer:** with one number, you cannot tell which *direction* a signal is turning. With
two, you can. And in radio, that direction tells you whether a signal is **above** or **below**
the frequency you tuned to.

The rest of this page explains that sentence, one step at a time.

---

## 2. A picture: the spinning wheel

Imagine a wheel with a single dot painted on its rim. The wheel spins at a steady speed.

**You look at it from the side.** From the side, you only see the dot move **up and down**.
If you draw its height over time, you get a sine wave.

```
 side view: the dot's height over time
   ^
   |   .-'-.       .-'-.
   |  /     \     /     \
 --+-'-------'---'-------'--> time
   |          \_/
```

Now a question: **is the wheel spinning clockwise or anticlockwise?**

From the side, **you cannot tell.** Both directions give exactly the same up-and-down movement.

**Now add a second viewer, looking from above.** They see the dot move **left and right**.
Put the two views together, and you know the dot's exact position on the circle at every
moment. Now you can see which way it spins.

| Viewer | Sees | In radio, this is called |
|---|---|---|
| From the side | Up and down | **I** — the "in-phase" part |
| From above | Left and right | **Q** — the "quadrature" part |
| Both together | The dot's exact position on the circle | one **IQ sample** |

**That is all IQ is: two views of the same spinning signal, a quarter-turn (90°) apart.**
"Quadrature" is an old word for "a quarter-turn apart".

---

## 3. Why the direction matters: negative frequency

### 3.1 What the SDR does when you tune

When you tune your SDR to 100.0 MHz, it shifts everything so that 100.0 MHz becomes **zero**.
The station you want now sits at "0 Hz" — the centre of the screen. This shift is called
**down-conversion**. ([Fundamentals 03](./03_rf_basics.md) explains how the hardware does it.)

What happens to the stations on either side?

| Real frequency | After tuning to 100.0 MHz | On screen |
|---|---|---|
| 100.1 MHz (0.1 MHz above) | +100 kHz | right of centre |
| 100.0 MHz | 0 Hz | centre |
| 99.9 MHz (0.1 MHz below) | **−100 kHz** | left of centre |

The station at 99.9 MHz now has a **negative frequency**: −100 kHz.

### 3.2 What negative frequency means

In the wheel picture, frequency is **how fast the dot goes round**.

- **Positive frequency:** the dot spins **anticlockwise**. The station is *above* where you tuned.
- **Negative frequency:** the dot spins **clockwise**. The station is *below* where you tuned.

Both spin at 100,000 turns per second. Only the direction is different.

```
          Q                            Q
          ↑   ↺                        ↑   ↻
       .-'|'-.                      .-'|'-.
      /   |   \                    /   |   \
   --+----+----+--→ I           --+----+----+--→ I
      \   |   /                    \   |   /
       '-.|.-'                      '-.|.-'
    anticlockwise                  clockwise
    +100 kHz (100.1 MHz)           −100 kHz (99.9 MHz)
```

### 3.3 Why one number is not enough

With only **I** (the side view), the stations at 100.1 MHz and 99.9 MHz look **exactly the
same**. They would land on top of each other and you could not separate them.

With **I and Q**, they are different, because they spin in different directions. So the SDR
can show you **both sides** of the tuned frequency, clearly separated.

> 🎯 **The big payoff:** with IQ, a sample rate of 1 MSPS shows you a full **1 MHz** of
> spectrum: from −500 kHz to +500 kHz around your tuned frequency. With only one number per
> sample, you would have to sample twice as fast (2 MSPS) to see the same 1 MHz.

---

## 4. How the hardware makes I and Q

Inside the SignalSDR Pro, the AD9361 chip splits the incoming radio signal into two paths:

```
                      ┌─────────┐
                ┌────▶│  mixer  │────▶ I  (the "side view")
                │     └────▲────┘
   antenna ─────┤          │ cos  ← tuning signal
   signal       │     ┌────┴────┐
                │     │ shift   │
                │     │  90°    │
                │     └────┬────┘
                │     ┌────▼────┐
                └────▶│  mixer  │────▶ Q  (the "top view")
                      └─────────┘
                           sin  ← same tuning signal, a quarter-turn later
```

- Both paths are multiplied (**mixed**) by an internal tuning signal at the frequency you chose.
  This internal signal is called the **local oscillator (LO)**.
- The Q path gets the same tuning signal, but shifted by **90°** — a quarter-turn later.
- Each path then goes to its own **ADC**, which turns it into numbers.

So each sample contains two numbers taken at the same instant: I and Q.

---

## 5. What you can calculate from I and Q

Think of each IQ sample as a point on a graph, with I across and Q up. It is also an arrow from
the centre to that point.

```
      Q
      ↑
      |      • (I, Q)
      |     /
      |  A /       A = length of the arrow  = amplitude (strength)
      |   /        φ = angle of the arrow   = phase
      |  / φ
  ----+---------→ I
```

From that one point you can get:

| What | How | Used for |
|---|---|---|
| **Amplitude** — how strong the signal is right now | the length of the arrow: $A = \sqrt{I^2 + Q^2}$ | AM radio, signal meters |
| **Phase** — the arrow's angle | $\phi = \text{atan2}(Q, I)$ | digital signals (PSK) |
| **Frequency** — how fast the angle changes | the change in angle from one sample to the next | FM radio |

This is why IQ is so powerful. **Every kind of radio signal is just a way of changing the
arrow:**

- **AM** changes the arrow's **length**.
- **FM** changes how fast the arrow **turns**.
- **PM / PSK** changes the arrow's **angle**.
- **QAM** (used in Wi-Fi and digital TV) changes **length and angle together**.

> 💡 All of modern wireless communication comes down to controlling I and Q.

<details>
<summary><b>Going deeper:</b> I and Q as a complex number</summary>

Mathematicians write an IQ sample as one **complex number**:

$$
s[n] = I[n] + j \cdot Q[n]
$$

Here $j = \sqrt{-1}$. Don't worry about what that "means". It is just a label that keeps I and
Q in separate slots, with the right rules for multiplying them.

The same number in "arrow" form:

$$
s = A \cdot e^{j\phi}, \qquad A = \sqrt{I^2 + Q^2}, \qquad \phi = \text{atan2}(Q, I)
$$

A pure tone at frequency $f$ is a spinning arrow:

$$
s(t) = e^{j 2\pi f t} = \cos(2\pi f t) + j\,\sin(2\pi f t)
$$

If $f > 0$ it spins anticlockwise; if $f < 0$, clockwise. The instantaneous frequency is the
rate of change of the angle:

$$
f(t) = \frac{1}{2\pi} \frac{d\phi}{dt}
$$

**Why real (single-number) samples cannot tell + from −.** A real signal $\cos(2\pi f t)$ is
the sum of two arrows spinning in opposite directions:

$$
\cos(2\pi f t) = \tfrac{1}{2}\left(e^{j2\pi f t} + e^{-j2\pi f t}\right)
$$

So a real signal always contains $+f$ and $-f$ equally. It carries no information about
direction. IQ keeps the two separate.
</details>

---

## 6. IQ in GNU Radio

In GNU Radio, IQ data is a stream of **complex** numbers. On screen, the ports of blocks are
coloured by data type:

| Data type | Port colour in GRC | What it holds | Size |
|---|---|---|---|
| **Complex** | blue | IQ samples (I and Q, as two 32-bit floats) | 8 bytes |
| **Float** | orange | Ordinary numbers: audio, measurements | 4 bytes |
| **Short** | yellow | Small whole numbers (e.g. 16-bit audio) | 2 bytes |
| **Byte** | purple | Bits and bytes of data | 1 byte |

- The **USRP Source** block (the radio) outputs **complex** (IQ).
- The **Audio Sink** block (your speakers) needs **float** (plain audio).
- Some block in between must turn IQ into audio. In Lab 01 that is the **WBFM Receive** block.

> ⚠️ If you connect a blue port to an orange port, GNU Radio shows the connection in **red**
> and will not run. The types must match.

**Data rate example:** at 1 MSPS, complex samples are 1,000,000 × 8 bytes = **8 MB every
second**. That is why the SDR needs USB 3.0.

---

## 7. Three things you will see on a real SDR

Real hardware is not perfect. Here is what that looks like on screen.

### 7.1 The centre spike (DC offset)

A small amount of the tuning signal (the LO) leaks through the mixers. It appears as a
**sharp spike exactly in the centre** of the spectrum (at 0 Hz). It is not a station.

**What to do:** tune a little to one side of the signal you want. Lab 06 shows how.
GNU Radio also has a **DC Blocker** block that removes it.

### 7.2 A lopsided spectrum (IQ imbalance)

If the I and Q paths are not *exactly* the same strength, or not *exactly* 90° apart, a faint
mirror copy of a strong signal can appear on the opposite side of the centre. The SignalSDR Pro
corrects this automatically in most cases.

### 7.3 No "image" problem

In older radios, a signal on the *wrong* side of the tuning frequency (called the **image**)
could leak in and needed an expensive filter to block it. Because IQ keeps the two sides
separate, an SDR mostly avoids this problem for free.

---

## ✅ Summary

- An IQ sample is **two numbers** taken at the same moment: I and Q, a quarter-turn (90°) apart.
- Together they give the signal's exact position on a circle. That shows which way it turns.
- **Positive frequency** = above the tuned frequency. **Negative frequency** = below it.
- With IQ, the **sample rate = the width of spectrum you see** (1 MSPS → 1 MHz).
- From I and Q you get **amplitude** (AM), **phase** (PSK) and **frequency** (FM).
- In GNU Radio, IQ is the **complex** type (blue ports). Audio is **float** (orange ports).
- The spike in the centre of the screen is the radio's own leak, not a station.

## 🧠 Check yourself

1. What do I and Q stand for, and how far apart are they?
   <details><summary>Answer</summary>In-phase and Quadrature. They are 90° (a quarter-turn)
   apart.</details>
2. You tune to 95.0 MHz. A station at 94.8 MHz appears at what frequency on screen?
   <details><summary>Answer</summary>−200 kHz (200 kHz to the left of centre).</details>
3. Your IQ sample rate is 2 MSPS. What range of frequencies can you see around the tuned
   frequency?
   <details><summary>Answer</summary>From −1 MHz to +1 MHz: 2 MHz in total.</details>
4. How do you get a signal's amplitude from I and Q?
   <details><summary>Answer</summary>$A = \sqrt{I^2 + Q^2}$ — the length of the arrow.</details>
5. Which of these changes the arrow's *speed of turning*: AM, FM or PSK?
   <details><summary>Answer</summary>FM.</details>

**Next:** [Fundamentals 03 — RF Basics →](./03_rf_basics.md)
