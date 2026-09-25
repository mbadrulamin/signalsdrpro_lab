# 🛩️ Fundamentals 07 — AM, SSB and Narrow FM

> **What you will learn:** the other voice modes — **AM**, **DSB**, **SSB** and **narrow FM** —
> how each one looks on the waterfall, how an SDR decodes each one, and why aircraft still use AM.
> **Before this:** [Fundamentals 04 — FM](./04_fm_theory.md) and
> [06 — Noise and SNR](./06_noise_snr_and_gain.md).
> **Time:** about 40 minutes. **Used by:** Lab 06.

---

## Why this chapter exists

Fundamentals 04 covered one mode: wide FM, for broadcast radio. But most of the interesting
voice signals on the air use other modes. Lab 06 builds a receiver for several of them.

| Band | Mode | What is there |
|---|---|---|
| 118–137 MHz | **AM** | Aircraft talking to control towers |
| 144–148 MHz | **Narrow FM**, SSB | Amateur radio, "2 m" band |
| 156–162 MHz | **Narrow FM** | Marine radio (channel 16 = 156.800 MHz) |
| 380–470 MHz | **Narrow FM** | Business radio, walkie-talkies, amateur "70 cm" |
| 3–30 MHz | **SSB**, AM, Morse | Shortwave and amateur HF — *below the SignalSDR Pro's 70 MHz limit; needs an upconverter* |

> ⚖️ **The law.** Listening is allowed in most places. But recording, sharing or acting on some
> of these (especially aircraft, marine distress, and emergency services) may be restricted.
> Check the rules where you live ([Malaysia reference](../05_reference/04_malaysia.md)). Everything
> in this course only receives.

---

## Part 1 — AM (amplitude modulation)

### How it works

The sound changes the **size** of the carrier. A small, steady part stays the carrier; the
sound rides on top:

$$
s_{AM}(t) = A_c \bigl[1 + m \cdot x(t)\bigr] \cos(2\pi f_c t)
$$

- *x*(*t*) is the sound, scaled to between −1 and +1.
- *m* is the **modulation index** (how deep the modulation is), from 0 to 1.

### What it looks like on a spectrum

An AM signal has three parts: the **carrier** in the middle, and two **sidebands** — mirror
images of the sound — on each side:

```
        carrier
           │
   LSB  ───┼───  USB          LSB = lower sideband, USB = upper sideband
    ▁▁▂▃  ███  ▃▂▁▁
  ────────┼────────────  frequency
        f_c
   ◄── width = 2 × highest audio frequency ──►
```

**Width = 2 × the highest sound frequency.** Aircraft voice goes up to about 3 kHz, so an aircraft
channel is about 6–8 kHz wide. (Channels are 25 kHz apart, or 8.33 kHz apart in Europe.)

### AM's big weakness: wasted power

Most of the power goes into the carrier, which carries **no information**. Even at full
modulation (*m* = 1), only **one third** of the power is in the sidebands (the part carrying the
sound):

| *m* | Share of power carrying sound | Notes |
|---|---|---|
| 0.5 | 11 % | typical for broadcasting |
| 1.0 | 33 % | the maximum possible |
| more than 1 | — | **over-modulation**: badly distorted |

This waste is why DSB and SSB (Part 2) were invented.

<details>
<summary><b>Going deeper:</b> the power formula</summary>

For a single tone, the carrier has power $A_c^2/2$ and the two sidebands together $A_c^2 m^2/4$:

$$
\eta = \frac{P_{\text{sidebands}}}{P_{\text{total}}} = \frac{m^2}{2 + m^2}
$$
</details>

### Why aircraft still use AM today

Three good reasons, all about safety:

1. **You can hear two at once.** If two aircraft talk at the same time, FM would lock onto the
   stronger one and the weaker would **disappear silently** (the capture effect). AM plays
   **both**, with a whistle — so the controller knows something went wrong.
2. **It fades gently.** AM slowly gets noisier as the signal gets weaker. FM falls off a cliff.
3. **Simple receivers.** An AM detector is a diode and a capacitor. Simple equipment is easier to
   certify as safe.

### Decoding AM, method 1: the envelope

The sound is the **size** of the signal. In IQ terms, that is the length of the arrow
([Fundamentals 02](./02_iq_sampling.md)):

$$
\text{audio} = \sqrt{I^2 + Q^2} \quad \text{(then remove the constant carrier level)}
$$

In GNU Radio: **Complex to Mag**, then remove the constant (DC) part. The **AM Demod** block does
all of this, plus an audio filter. (It removes the carrier by subtracting exactly 1.0, so the
signal must arrive with the carrier at 1.0 — see Lab 06.)

**Good:** very simple, and **not affected by small tuning errors** — the arrow's length does not
change when it rotates.
**Bad:** in very weak signals, about 3 dB worse than method 2.

### Decoding AM, method 2: coherent detection

Multiply by a copy of the carrier made in the receiver, with exactly the right frequency **and
phase**. It is 3 dB better in noise, but needs a PLL to make that copy, and any phase error
makes the sound weaker. Lab 06 uses method 1. Stereo (Lab 04) and RDS (Lab 08) need method 2,
because their carriers are not sent at all (next section).

---

## Part 2 — DSB-SC and SSB: not wasting power

### DSB-SC: remove the carrier

**DSB-SC** (double sideband, suppressed carrier) sends only the two sidebands — no carrier:

$$
s_{DSB}(t) = x(t)\cos(2\pi f_c t)
$$

Now **all** the power carries sound. The cost: the envelope method no longer works (the envelope
loses the sign of the sound). You **must** use coherent detection — and rebuild a carrier that
was never sent.

**You have already met DSB-SC:** the **L−R stereo signal** in Lab 04 (at 38 kHz), and **RDS** in
Lab 08 (at 57 kHz). The 19 kHz pilot exists so receivers can rebuild those missing carriers.

### SSB: remove one sideband too

The two sidebands are **mirror images**: they carry the same information. So throw one away.
**SSB** (single sideband) sends only the upper (**USB**) or the lower (**LSB**) sideband:

| Mode | Width | Power carrying sound |
|---|---|---|
| AM | 2 × audio | 33 % at most |
| DSB-SC | 2 × audio | 100 % |
| **SSB** | **1 × audio** | **100 %** |

SSB uses half the bandwidth of AM and puts all its power into the sound — roughly a **9 dB**
advantage. That is why amateur and marine shortwave voice uses SSB.

### How an SDR receives SSB — the easy way

With IQ, the two sides of 0 Hz are separate ([Fundamentals 02](./02_iq_sampling.md)). So to
receive USB, you simply **keep only the positive side**:

```
  After tuning to where the carrier would be:

     LSB          USB
   ▓▓▓▓▓▓░░░░│░░░░▓▓▓▓▓▓
  -3k     -300  +300   +3k     Hz

  USB: keep +300 Hz … +3000 Hz      ← a filter on ONE side of zero:
  LSB: keep −3000 Hz … −300 Hz         only possible with IQ!
```

Then take the real part. That is the whole SSB receiver. A filter on one side of zero makes no
sense for ordinary (real) signals, but is natural for IQ.

<details>
<summary><b>Going deeper:</b> the SSB equation</summary>

$$
s_{SSB}(t) = x(t)\cos(2\pi f_c t) \mp \hat{x}(t)\sin(2\pi f_c t)
$$

where $\hat{x}(t)$ is the **Hilbert transform** of the audio (every frequency shifted by −90°).
Minus gives USB, plus gives LSB. The IQ receiver above avoids calculating it.
</details>

---

## Part 3 — Narrow FM

### The same as FM broadcast, with a smaller swing

Narrow FM (**NBFM**) works exactly like the FM in [Fundamentals 04](./04_fm_theory.md). The only
difference is the **deviation** — how far the frequency swings. The **modulation index** β
compares the swing with the highest audio frequency:

$$
\boxed{\beta = \frac{\Delta f}{f_m}} \qquad \text{(deviation ÷ highest audio frequency)}
$$

| Mode | Deviation | Audio up to | β | Width (Carson) |
|---|---|---|---|---|
| **NBFM** voice | 5 kHz | 3 kHz | 1.67 | 16 kHz |
| **NBFM** (narrower) | 2.5 kHz | 3 kHz | 0.83 | 11 kHz |
| **WBFM** broadcast | 75 kHz | 15 kHz | 5.0 | 180 kHz |

(Carson's rule: width ≈ 2 × (deviation + highest audio frequency).)

### Why β matters

The bigger β is, the more FM cleans up the noise
([Fundamentals 06 §3](./06_noise_snr_and_gain.md#part-3--snr-and-how-much-each-mode-needs)):

| Mode | β | Noise improvement from FM |
|---|---|---|
| NBFM | 1.67 | about 9 dB |
| WBFM | 5.0 | about 19 dB |

**Wide FM gets about 10 dB cleaner sound by using 11 times more bandwidth.** A broadcaster has
plenty of bandwidth and wants quality. A walkie-talkie has little bandwidth and only needs
understandable speech. Both choices are right for their job. Trading bandwidth for quality is
the central decision in every radio system.

### Decoding narrow FM

Exactly the same as wide FM: the **Quadrature Demod** block measures how fast the IQ arrow
turns. Only its **gain** setting changes. For the audio to come out between −1 and +1:

$$
\boxed{\text{gain} = \frac{f_s}{2\pi \Delta f}} \qquad \text{(sample rate ÷ (2π × deviation))}
$$

| Sample rate | Deviation | Gain |
|---|---|---|
| 48 kHz | 5 kHz | 1.528 |
| 384 kHz | 75 kHz | 0.815 |
| 240 kHz | 75 kHz | 0.509 |

> ⚠️ **The most common narrow-FM mistake** is keeping the wide-FM gain. The sound still works —
> FM quality does not depend on the gain — but it comes out about **15 times** too loud or too
> quiet. People then search for a broken filter, when the problem is one number.

The **NBFM Receive** block does the demodulation, de-emphasis and audio filtering in one step.
You give it `max_dev` (the deviation) directly. Lab 06 uses it.

### CTCSS — the low hum

Many narrow-FM radios send a steady, very low tone (67–250 Hz) under the voice. A receiver can
stay silent unless it hears the *right* tone, so a group only hears its own radios. This is
called **CTCSS**. If you hear a low hum on narrow FM, it is probably CTCSS. A high-pass filter
at 300 Hz removes it.

---

## Part 4 — Which decoder? A decision table

| If the signal… | It is probably | Decode with | GNU Radio block |
|---|---|---|---|
| has a strong, steady carrier line in the middle | AM | the envelope | AM Demod |
| is symmetric, with **no** carrier line | DSB-SC | coherent (PLL) | PLL Carrier Tracking + Multiply |
| is only on one side, and sounds like a duck when mistuned | SSB | filter one side, take the real part | Freq Xlating filter + Complex to Real |
| is a steady block about 12–16 kHz wide | narrow FM | quadrature demod | NBFM Receive |
| is a steady block about 200 kHz wide | wide FM | quadrature demod | WBFM Receive |

### Recognising them on the waterfall

```
AM:      ▁▁▂▅█████▅▂▁▁     a bright line in the middle (the carrier), even on both sides
DSB-SC:  ▁▁▅███ ███▅▁▁     even on both sides, a gap in the middle
SSB:     ▁▁▁▁▁▁████▅▂▁     only on one side, uneven (shaped like speech)
NBFM:    ▁▂▅█████▅▂▁       a block of constant width, no bright centre line
WBFM:    ▂▅███████████▅▂   about 200 kHz wide
```

[Signal identification](../05_reference/02_signal_identification.md) has many more examples.

---

## ✅ Summary

- **AM** changes the size of the carrier. Simple and safe, but wastes at least two thirds of its
  power. Aircraft use it so two stations can be heard at once.
- Decode AM with the **envelope** (the arrow's length). It ignores small tuning errors.
- **DSB-SC** and **SSB** remove the wasted parts. They need a rebuilt carrier. In an SDR, SSB is
  just "keep one side of zero".
- **Narrow FM** is FM with a small swing (±5 kHz). Same decoder, different **gain**:
  *f*ₛ ÷ (2π × deviation).

## 🧠 Check yourself

1. An AM transmitter uses 100 W at *m* = 0.8. How much power carries the sound?
   <details><summary>Answer</summary>0.64 ÷ (2 + 0.64) = 24.2 %, so 24.2 W.</details>
2. Narrow FM with 5 kHz deviation and audio up to 3 kHz. How wide is it?
   <details><summary>Answer</summary>2 × (5 + 3) = 16 kHz.</details>
3. A Quadrature Demod at 96 kHz for narrow FM with 5 kHz deviation. What gain?
   <details><summary>Answer</summary>96,000 ÷ (2π × 5,000) = 3.056.</details>
4. Why do aircraft use AM, when FM would sound better?
   <details><summary>Answer</summary>If two transmit at once, both must be heard. FM's
   capture effect would silently hide one. Safety matters more than sound quality.</details>
5. Why can't the envelope method decode DSB-SC?
   <details><summary>Answer</summary>The envelope is the size of the sound, |x(t)|. It loses
   the sign, so every negative part comes out positive.</details>
6. How does an SDR receive USB without complicated maths?
   <details><summary>Answer</summary>Tune to where the carrier would be, keep only the positive
   side (+300 to +3000 Hz) of the IQ signal, and take the real part.</details>

**Next:** [Fundamentals 08 — Digital Modulation →](./08_digital_modulation.md)
