# 📻 Fundamentals 04 — How FM Works

> **What you will learn:** what modulation is; how AM and FM carry sound; why an FM station is
> 200 kHz wide; what is hidden inside an FM broadcast (stereo and RDS); de-emphasis; and how
> software gets the sound back.
> **Before this:** [Fundamentals 03 — RF Basics](./03_rf_basics.md).
> **Time:** about 40 minutes.

---

## 1. What is modulation?

**Modulation** means putting information (like sound) onto a radio wave so it can travel
through the air.

Why not just send the sound directly? Two reasons:

1. **Sound frequencies are too low.** Music is 20 Hz to 20 kHz. An antenna for 20 kHz would
   need to be kilometres long.
2. **Everyone would be on top of each other.** If every station sent plain sound, they would all
   use the same frequencies. You could not pick one.

So each station uses a high-frequency wave called a **carrier**, at its own frequency (for
example 98.0 MHz). The sound is carried *on* that wave. Your radio tunes to one carrier and
ignores the rest.

There are two simple ways to put sound on a carrier: change its **size** (AM) or change its
**speed** (FM).

---

## 2. AM — change the size

In **AM** (amplitude modulation), the sound makes the carrier's **amplitude** go up and down.
The louder the sound at that moment, the bigger the wave.

```
 sound:      ~~~~~/\~~~~~/\~~~~~

 AM carrier: ||||||||||||||||||||    ← the outline ("envelope") of the fast
             |||||||||||||||||||||      carrier follows the shape of the sound
```

**The problem with AM:** noise also changes the size of the wave. Lightning, motors and
electronics all add "crackle" to the amplitude. The receiver cannot tell that crackle from the
sound.

**Still used for:** AM radio (530–1700 kHz), **aircraft voice (118–137 MHz)**, and shortwave.
[Fundamentals 07](./07_am_and_narrowband_fm.md) covers AM in detail.

---

## 3. FM — change the speed

In **FM** (frequency modulation), the sound makes the carrier's **frequency** change a little.
The size stays the same.

- When the sound goes **up**, the carrier speeds up (frequency rises a bit).
- When the sound goes **down**, the carrier slows down (frequency falls a bit).

```
 sound:      low ........ high ......... low

 FM carrier: \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/   ← same height,
             wider  →   tighter   →   wider    but the spacing changes
```

In the IQ picture from [Fundamentals 02](./02_iq_sampling.md): the arrow stays the same length,
but it **turns faster and slower** with the sound.

### 3.1 Deviation — how far the frequency swings

The largest change in frequency is called the **deviation** (written Δf, "delta f").

| Type of FM | Deviation | Used for |
|---|---|---|
| **Narrow FM** (NBFM) | ±2.5 to ±5 kHz | Walkie-talkies, amateur radio, marine radio |
| **Wide FM** (WBFM) | **±75 kHz** | FM broadcast radio (87.5–108 MHz) |

An FM broadcast station at 98.0 MHz actually moves between 97.925 and 98.075 MHz as the music
plays. That big swing is why it is called **wide** FM.

### 3.2 Why FM sounds better than AM

- **Noise mostly changes the size of a wave.** An FM receiver ignores size and only looks at
  frequency. So much of the noise is simply ignored. The sound is cleaner.
- **The capture effect.** If two FM stations are on the same frequency, the receiver locks on
  to the stronger one and mostly ignores the weaker one. (With AM you would hear both mixed.)
  This works best when one station is clearly stronger.
- **Room for extras.** The wide channel has space for stereo and data (see Section 5).

<details>
<summary><b>Going deeper:</b> the FM equations</summary>

The instantaneous frequency is:

$$
f(t) = f_c + \Delta f \cdot x(t)
$$

where $f_c$ is the carrier frequency and $x(t)$ is the audio, scaled to between −1 and +1.

The transmitted signal is:

$$
s_{FM}(t) = A \cdot \cos\!\left(2\pi f_c t + 2\pi \Delta f \int_0^t x(\tau)\, d\tau\right)
$$

The **integral** appears because phase is the running total of frequency. For comparison, AM is:

$$
s_{AM}(t) = \bigl[1 + m \cdot x(t)\bigr] \cdot \cos(2\pi f_c t)
$$

where $m$ is the modulation depth.
</details>

---

## 4. Why an FM station is 200 kHz wide

An FM station uses much more space than the sound it carries. How much? A handy rule called
**Carson's rule** estimates it:

$$
\text{bandwidth} \approx 2 \times (\text{deviation} + \text{highest audio frequency})
$$

For mono FM broadcast: deviation = 75 kHz, highest audio = 15 kHz:

$$
2 \times (75 + 15) = 180 \text{ kHz}
$$

That is why FM stations are placed about **200 kHz apart** (for example 98.0, 98.2, 98.4 MHz).
The 20 kHz left over is a gap, so neighbouring stations do not overlap.

> 💡 Stereo and RDS add higher-frequency parts (up to about 60 kHz, see below). By Carson's
> rule that would suggest about 270 kHz. In practice, broadcasters share the 75 kHz deviation
> between all the parts, so the station still fits in its 200 kHz channel. Carson's rule is a
> rough guide, not an exact limit.

---

## 5. What is inside an FM broadcast

When you decode an FM station, you do not get plain audio straight away. You get a signal
called **MPX** (multiplex). It contains several parts, side by side:

```
 strength
    │
    │ ████████      │     ▓▓▓▓▓▓▓▓▓ ▓▓▓▓▓▓▓▓▓    ░
    │ ████████      │     ▓▓▓▓▓▓▓▓▓ ▓▓▓▓▓▓▓▓▓    ░
    └─┴───────┴───┴─┴───┴─────────┴─────────┴──┴─┴──── frequency (kHz)
      0       15    19   23        38        53   57
      └─L+R──┘   pilot  └──────── L−R ────────┘  RDS
```

| Part | Where | What it is | Who uses it |
|---|---|---|---|
| **L+R** | 0–15 kHz | Left + right added together: normal mono sound | Every FM radio |
| **Pilot tone** | exactly 19 kHz | A steady tone. It says "this station is stereo" and is used as a timing reference | Stereo radios |
| **L−R** | 23–53 kHz | Left minus right, shifted up around 38 kHz (twice the pilot) | Stereo radios |
| **RDS** | around 57 kHz | Digital data: station name, song title (57 kHz = 3 × the pilot) | Radios with a text display |

A stereo radio gets left and right back by adding and subtracting:

$$
L = \frac{(L+R) + (L-R)}{2} \qquad R = \frac{(L+R) - (L-R)}{2}
$$

This clever design means old mono radios still work: they just play L+R and ignore the rest.

You will build all of this yourself:

- **Lab 01–03:** play L+R (mono).
- **Lab 04:** decode stereo by hand — pilot, L−R and the maths above.
- **Lab 08:** decode RDS and read the station's name.

---

## 6. Pre-emphasis and de-emphasis

High-pitched sounds are more affected by FM noise (you hear it as hiss). So broadcasters use a
trick:

1. **Before sending**, the station **boosts** the high-pitched sounds. This is
   **pre-emphasis**.
2. **After receiving**, your radio **cuts** them back down by the same amount. This is
   **de-emphasis**. The music sounds normal again, and the hiss is cut down too.

The amount is set by a **time constant**, written τ ("tau"):

| Where | τ |
|---|---|
| **Malaysia, Europe, most of the world** | **50 µs** |
| USA and South Korea | 75 µs |

> ⚠️ **If you skip de-emphasis**, FM sounds thin, sharp and hissy (too much treble).
> **If you use the wrong value**, it still works, but the treble is a little wrong.

> 💡 **A note for Malaysia.** GNU Radio's ready-made **WBFM Receive** block (used in
> Labs 01–03) always uses **75 µs**. With Malaysian stations (50 µs) this makes the sound
> slightly dull — a little too much treble is removed. It is a small effect. Lab 04 builds
> de-emphasis by hand and uses the correct 50 µs.

<details>
<summary><b>Going deeper:</b> the de-emphasis filter</summary>

De-emphasis is a simple first-order low-pass filter (like one resistor and one capacitor):

$$
H(s) = \frac{1}{1 + s\tau}
$$

Its −3 dB point is $f = 1/(2\pi\tau)$: **3.2 kHz** for 50 µs and **2.1 kHz** for 75 µs.
</details>

---

## 7. How software gets the sound back

We want to recover the sound from the FM signal. Since the sound is stored in **how fast the
IQ arrow turns**, we just need to measure that speed.

### 7.1 The method GNU Radio uses: the quadrature demodulator

For each new IQ sample, compare its angle with the previous sample's angle.

- A big change in angle → the arrow is turning fast → high frequency → the sound is "up".
- A small change → turning slowly → the sound is "down".

The **change in angle between two samples is the sound**. That is all an FM demodulator does.
GNU Radio's **Quadrature Demod** block does exactly this, and the **WBFM Receive** block uses it
inside.

<details>
<summary><b>Going deeper:</b> the demodulator formula</summary>

The instantaneous frequency is the rate of change of the phase:

$$
f(t) = \frac{1}{2\pi} \frac{d\phi}{dt}
$$

In discrete samples, the angle change between samples $n-1$ and $n$ is:

$$
\Delta\phi[n] = \arg\!\bigl(s[n] \cdot s^*[n-1]\bigr)
$$

where $s^*$ is the complex conjugate (flip the sign of Q). Multiplying by the conjugate of the
previous sample *subtracts* its angle. The Quadrature Demod block outputs:

$$
y[n] = \frac{f_s}{2\pi \Delta f} \cdot \arg\!\bigl(s[n] \cdot s^*[n-1]\bigr)
$$

The scale factor $\frac{f_s}{2\pi \Delta f}$ makes full deviation come out as ±1.
</details>

### 7.2 Older methods (for interest)

- **Discriminator** — an analog circuit whose output voltage depends on the frequency. Used in
  most older FM radios.
- **Phase-locked loop (PLL)** — a circuit that follows the signal's frequency. The effort
  needed to follow it *is* the sound. [Fundamentals 09](./09_synchronization.md) explains PLLs.

The quadrature method is the simplest in software, so that is what SDRs use.

---

## ✅ Summary

- **Modulation** puts sound on a high-frequency **carrier** so it can travel and be tuned.
- **AM** changes the carrier's size. **FM** changes its frequency. FM ignores most noise.
- FM broadcast uses **±75 kHz deviation**, and each station takes about **200 kHz**.
- An FM broadcast contains **L+R** (mono), a **19 kHz pilot**, **L−R** (stereo) and **RDS** (data).
- **De-emphasis** undoes the treble boost. Malaysia uses **50 µs**.
- An FM demodulator measures **how much the IQ angle changes** from one sample to the next.

## 🧠 Check yourself

1. What is the maximum deviation of FM broadcast?
   <details><summary>Answer</summary>±75 kHz.</details>
2. Why does FM have less crackle than AM?
   <details><summary>Answer</summary>Most noise changes a wave's size (amplitude). An FM
   receiver ignores size and only measures frequency.</details>
3. What is the 19 kHz pilot tone for?
   <details><summary>Answer</summary>It tells the radio the station is in stereo, and gives
   it a timing reference to rebuild the 38 kHz signal needed to decode L−R.</details>
4. Your FM audio sounds thin, sharp and hissy. What is probably missing?
   <details><summary>Answer</summary>De-emphasis.</details>
5. Using Carson's rule, how wide is a narrow-FM signal with ±5 kHz deviation and audio up to
   3 kHz?
   <details><summary>Answer</summary>2 × (5 + 3) = 16 kHz.</details>

You now have the theory you need. Time to build a radio!

**Next:** [Lab 01 — The Simplest FM Receiver →](../02_flowgraphs/lab01_simple_wbfm/README.md)
