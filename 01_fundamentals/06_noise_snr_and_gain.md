# 📉 Fundamentals 06 — Noise, Signal Strength and Gain

> **What you will learn:** decibels properly (dB, dBm, dBFS); where noise comes from; noise
> figure; SNR and how much each mode needs; how to set the **gain** correctly; why you must set
> the analog bandwidth; processing gain; AGC; squelch; and how to work out a **link budget**.
> **Before this:** [Fundamentals 05 — Sampling & Filters](./05_sampling_and_filters.md).
> **Time:** about 45 minutes. **Used by:** Labs 05, 06, 08, 09.

---

## Why this chapter exists

Every question that starts with *"why can't I hear it?"* is answered here:

- Why does turning the gain above about 50 dB make reception **worse**?
- What does "sensitivity −110 dBm" actually mean?
- How clean must a signal be before FM sounds good?
- Why does a weak station suddenly appear when you narrow the filter?

These are not opinions. They are simple arithmetic, and this chapter shows you the arithmetic.

---

## Part 1 — Decibels, properly

### The definition

A **decibel** compares two **powers** on a logarithmic scale:

$$
\text{dB} = 10 \log_{10}\frac{P_2}{P_1}
$$

For **voltages** or **amplitudes**, use 20 instead of 10 (because power is proportional to
voltage squared):

$$
\text{dB} = 20 \log_{10}\frac{V_2}{V_1}
$$

> ⚠️ **10 or 20?** This is the most common mistake in SDR.
> **Power → 10. Voltage or amplitude → 20.**
> GNU Radio's spectrum displays show **power**, so they use 10. AGC levels and filter gains are
> **amplitudes**, so they use 20.

### Numbers worth remembering

| Ratio | As power | As amplitude |
|---|---|---|
| ×2 | 3 dB | 6 dB |
| ×4 | 6 dB | 12 dB |
| ×10 | 10 dB | 20 dB |
| ×100 | 20 dB | 40 dB |
| ×1000 | 30 dB | 60 dB |

### Fixed references: dBm, dBW, dBFS and others

A plain **dB** is only a comparison. Add letters to compare with a fixed reference:

| Unit | Compared with | Used for |
|---|---|---|
| **dBm** | 1 milliwatt | Real power at an antenna or connector |
| **dBW** | 1 watt | Transmitter power (0 dBW = 30 dBm) |
| **dBFS** | the ADC's maximum ("full scale") | The level inside the SDR |
| **dBc** | the carrier | How strong unwanted signals are, next to the wanted one |
| **dBi** | a perfect "isotropic" antenna | Antenna gain |

Some real signal levels:

| Signal | Power | dBm |
|---|---|---|
| A strong local FM station at your antenna | 1 µW (a millionth of a watt) | −30 dBm |
| A normal, usable FM station | 1 pW (a million-millionth) | −90 dBm |
| A weak but decodable narrow signal | 10 fW | −110 dBm |
| GPS at the Earth's surface | 0.1 fW | −130 dBm |

### dBFS — levels inside the SDR

Inside GNU Radio, IQ samples are numbers between about −1 and +1. **0 dBFS** is defined as a
full-scale sine wave (amplitude 1.0). Everything else is negative.

> ⚠️ **GNU Radio's spectrum display shows dBFS, not dBm.** To turn dBFS into real power you need
> a calibration of your receiver, which consumer SDRs do not come with. Use the display to
> **compare** signals, not to measure their real power.

<details>
<summary><b>Going deeper:</b> the dBFS formula</summary>

A full-scale sine has amplitude 1.0 and average power ½ (RMS $1/\sqrt2$). So:

$$
P_{dBFS} = 10 \log_{10}\!\left(2 \cdot \overline{|x[n]|^2}\right)
$$

This is the "+3.0103 dB" (10·log₁₀2) you see in the level meters of Labs 05 and 06.
</details>

---

## Part 2 — Where noise comes from

### Thermal noise: the floor nothing can go below

Every object warmer than absolute zero makes a tiny, random electrical noise, because its atoms
are moving. At room temperature this noise is:

$$
\boxed{-174 \text{ dBm per Hz of bandwidth}}
$$

**Remember −174 dBm/Hz.** It is the noise floor of the universe at room temperature. No
receiver can do better.

The wider your bandwidth, the more noise you collect:

$$
N_{dBm} = -174 + 10\log_{10}(\text{bandwidth in Hz})
$$

| Bandwidth | 10·log₁₀(B) | Thermal noise |
|---|---|---|
| 1 Hz | 0 dB | −174 dBm |
| 3 kHz (SSB voice) | 34.8 dB | −139.2 dBm |
| 15 kHz (narrow FM) | 41.8 dB | −132.2 dBm |
| 200 kHz (FM broadcast) | 53.0 dB | −121 dBm |
| 2 MHz (the whole SDR span) | 63.0 dB | −111 dBm |

> 💡 **This table explains why filtering helps.** Narrowing from 2 MHz to 15 kHz lets in
> 10·log₁₀(2,000,000 ÷ 15,000) = **21 dB less noise** — while the wanted signal stays the same.
> That 21 dB is free. It is why every receiver in this course filters and decimates, and why a
> station you cannot see on the 2 MHz waterfall can still be clear after the channel filter.

<details>
<summary><b>Going deeper:</b> where −174 comes from</summary>

Noise power in bandwidth $B$ at temperature $T$ is $N = kTB$, with Boltzmann's constant
$k = 1.38 \times 10^{-23}$ J/K. At $T_0 = 290$ K:

$$
kT_0 = 4.00 \times 10^{-21} \text{ W/Hz} = -174 \text{ dBm/Hz}
$$
</details>

### Noise figure: how much noise the receiver adds

A real receiver adds its own noise on top. The **noise figure (NF)** says how much, in dB. The
receiver's real noise floor is:

$$
\boxed{N_{dBm} = -174 + 10\log_{10}B + NF}
$$

| Receiver | Typical NF |
|---|---|
| Cooled radio-astronomy amplifier | 0.3 dB |
| Good external low-noise amplifier (LNA) | 1–2 dB |
| AD9361 (SignalSDR Pro / B210) | 4–8 dB, depending on gain and band |
| RTL-SDR | 6–10 dB |
| Any receiver with its gain turned right **down** | 20 dB or more |

### The first amplifier decides everything (Friis)

In a chain of amplifiers, the **first** one's noise counts in full. Every later amplifier's noise
is divided by all the gain in front of it. So **the first amplifier sets your noise figure.**

> **Example.** The SDR alone: NF = 8 dB. Now put a small LNA (NF 1 dB, gain 20 dB) **at the
> antenna**, in front of it. The total NF becomes about **1.2 dB** — nearly 7 dB better, from
> one small part.
>
> But put the same LNA at the *other* end of a long cable, and the cable's loss comes first.
> Then you gain almost nothing.

<details>
<summary><b>Going deeper:</b> the Friis formula and the numbers</summary>

With linear gains $G_i$ and noise factors $F_i = 10^{NF_i/10}$:

$$
F_{\text{total}} = F_1 + \frac{F_2 - 1}{G_1} + \frac{F_3 - 1}{G_1 G_2} + \cdots
$$

LNA: $F_1 = 10^{0.1} = 1.26$, $G_1 = 100$. SDR: $F_2 = 10^{0.8} = 6.31$.

$$
F_{\text{total}} = 1.26 + \frac{6.31 - 1}{100} = 1.312 \Rightarrow NF = 1.18\text{ dB}
$$
</details>

---

## Part 3 — SNR, and how much each mode needs

**SNR** (signal-to-noise ratio) is how far the signal stands above the noise, in dB:

$$
\text{SNR (dB)} = \text{signal (dBm)} - \text{noise (dBm)}
$$

| Mode | SNR to understand it | SNR for good quality |
|---|---|---|
| FM broadcast, mono | 12 dB | 30 dB |
| FM broadcast, **stereo** | 25 dB | 40 dB |
| Narrow FM voice | 10 dB | 20 dB |
| AM voice (aircraft) | 6 dB | 15 dB |
| BPSK data, BER 10⁻³ | 7 dB (Eb/N0) | 10 dB |
| ADS-B | 8 dB | 15 dB |

> 💡 **Stereo needs about 20 dB more.** The stereo part (L−R) sits around 38 kHz, where FM noise is
> much stronger, and the stereo matrix adds that noise to the sound. That is why Lab 04 hisses on
> a distant station that sounds fine in Lab 01 — and why car radios switch to mono when the
> signal gets weak.

### FM's threshold

FM has a **threshold** at about 10 dB. Below it, the sound collapses into a roar. Above it, the
output gets clean **faster** than the input improves. For FM broadcast, this "FM improvement"
is about **+18.8 dB**. That is why FM sounds so much cleaner than AM at the same signal
strength. The price is bandwidth: FM uses far more of it.

<details>
<summary><b>Going deeper:</b> the FM improvement formula</summary>

$$
\text{SNR}_{\text{out}} \approx \text{SNR}_{\text{in}} + 20\log_{10}\!\left(\frac{\Delta f}{f_m}\right) + 4.8 \text{ dB}
$$

For broadcast FM, $\Delta f / f_m = 75/15 = 5$: $20\log_{10}5 + 4.8 = 18.8$ dB.
</details>

---

## Part 4 — Gain: how to set it

The SignalSDR Pro has **one gain setting** in GNU Radio (0–76 dB). Inside, it controls several
amplifiers. What matters is the balance:

```
   too little gain              just right              too much gain
 ┌────────────────┐        ┌────────────────┐       ┌────────────────┐
 │ signal lost in │        │ signal well    │       │ amplifiers     │
 │ the ADC's own  │        │ above noise,   │       │ overloaded:    │
 │ noise          │        │ far from the   │       │ false signals  │
 │                │        │ maximum        │       │ everywhere     │
 └────────────────┘        └────────────────┘       └────────────────┘
```

### A method that always works

1. Set the gain to **0 dB**. Look at the spectrum display.
2. Raise the gain in **5 dB steps**. Watch the **noise floor** (the grassy line at the bottom).
3. At first the noise floor hardly moves. **Stop when it starts rising together with the gain.**
   From that point, you are only amplifying the radio's own noise. More gain just risks
   overload.
4. **Turn it back down 5 dB.** That is your setting. For FM with a decent antenna, it is usually
   **30–45 dB**.

### Set the analog bandwidth first — or none of this works

Before you touch the gain, tell the radio how wide a signal you want. In the USRP Source, that is
the **`bw0`** setting (`set_bandwidth()` in Python). **Set it to your sample rate.**

If you leave it empty, the radio's analog filter opens to its widest: **56 MHz**. You then collect
28 times more noise and unwanted signals than you asked for. Worse, the radio's automatic
correction of its centre spike works poorly with the filter wide open, so the **centre spike**
(DC / LO leakage) becomes huge.

Measured on a SignalSDR Pro at 89.9 MHz, 2 MSPS, gain 55 dB, twice:

| `bw0` | Analog filter | Centre spike (share of the signal) | Wanted station |
|---|---|---|---|
| not set | 56 MHz | **84 %** | 0.0160 |
| set to `samp_rate` | 2 MHz | **16 %** | 0.0149 |

The wanted station is the same. **All** the extra is the spike and junk — 84 % of everything the
ADC sees.

**Why that ruins FM:** the FM decoder measures how the IQ arrow turns. A large, still spike is
added to the small, turning station. Their sum no longer turns cleanly, so the decoded sound is
squashed and distorted.

Adding this one setting improved the measured audio SNR of Lab 01 from 34.6 to **53.2 dB**, and
of Lab 03 from 19.4 to **62.6 dB**.

> **Rule: always set `bw0` to your sample rate.** One setting, no cost, up to 40 dB better.

### Signs of too much gain

| You see | It means |
|---|---|
| Evenly spaced "ghost" signals that move when you change the gain | **Intermodulation** — the amplifiers are overloaded and mixing strong signals together |
| The noise floor rises **1 dB for every 1 dB** of gain | The radio is only hearing itself. More gain cannot help. (Measured at 1090 MHz: 70 → 76 dB of gain raised the noise by exactly 6.0 dB. The antenna was the real problem.) |
| One strong station appears at several frequencies | The front end is **compressed** (overloaded) |
| Sound distorts on strong stations only | **Clipping** in the ADC |
| `O` printed in the terminal | Not a gain problem! That is USB overflow — lower the sample rate |

### Dynamic range

**Dynamic range** is the gap between the weakest signal you can hear (the noise floor) and the
strongest you can handle (before overload). For an ideal ADC with *b* bits:

$$
\text{SNR}_{ADC} = 6.02\,b + 1.76 \text{ dB}
$$

| Bits | Ideal dynamic range |
|---|---|
| 8 (RTL-SDR) | 49.9 dB |
| **12 (AD9361, SignalSDR Pro)** | **74.0 dB** |
| 14 | 86.0 dB |
| 16 | 98.1 dB |

---

## Part 5 — Processing gain: getting SNR back with software

**Narrowing the bandwidth** in software improves SNR by:

$$
\boxed{G_p = 10\log_{10}\frac{B_{\text{wide}}}{B_{\text{narrow}}}}
$$

The signal stays the same; the noise is cut.

**The same idea explains FFT displays.** An FFT with *N* bins splits the noise into *N* pieces,
but a pure tone stays in one bin. So a bigger FFT shows weak tones that a small FFT hides. A
4096-point FFT shows tones that a 256-point FFT cannot.

**And it explains GPS.** GPS signals arrive about 20 dB **below** the noise. The receiver
correlates each signal with a known 1023-chip code, which gives
10·log₁₀(1023) = **30 dB** of processing gain — enough to lift the signal above the noise.

---

## Part 6 — AGC: automatic gain control

An **AGC** keeps a signal at a steady level. It measures the output, and turns its own gain up
or down to bring it towards a target (the **reference**). GNU Radio's block is `AGC2`
(Labs 03, 06, 08).

| Setting | Meaning | Typical |
|---|---|---|
| `reference` | Target output level | 0.5 (1.0 before AM Demod — see Lab 06) |
| `attack_rate` | How fast it turns **down** when too loud | 0.01 (fast) |
| `decay_rate` | How fast it turns **up** when too quiet | 0.001 (slow) |
| `max_gain` | The most it may amplify | 65536 |

**Attack fast, decay slow.** Fast attack stops a sudden strong signal from clipping. Slow decay
stops the noise from swelling up in every pause ("pumping").

The time it takes to react is roughly 1 ÷ (rate × sample rate). At 384 kSPS: attack 0.01 →
about **0.26 ms**; decay 0.001 → about **2.6 ms**.

> ⚠️ **Where the AGC goes matters.**
> - **After the channel filter**, never before. Otherwise the strongest signal anywhere in the
>   2 MHz controls the gain, and a strong neighbour turns *your* station down.
> - **After the squelch**, never before. The AGC lifts plain noise to the reference level, so a
>   squelch after it would see "a signal" all the time and never mute (Lab 03).
>
> **The order: channel filter → squelch → AGC → demodulate.**

> 💡 **For FM, the AGC does not change the loudness.** The FM decoder ignores the signal's size.
> For **AM**, the loudness *is* the signal's size, so there the AGC really matters.

<details>
<summary><b>Going deeper:</b> the AGC update rule</summary>

$$
y[n] = g[n]\,x[n], \qquad g[n+1] = g[n] + \mu \,\bigl(\text{reference} - |y[n]|\bigr)
$$

where $\mu$ is `attack_rate` when $|y| >$ reference, and `decay_rate` otherwise. The time
constant is about $\tau \approx 1/(\mu f_s)$.
</details>

---

## Part 7 — Squelch

A **squelch** mutes the output when the signal is too weak, so you hear silence instead of hiss.

GNU Radio's `Power Squelch` keeps a running average of the power, and opens only when it is above
the **threshold** (in dB, compared with full scale).

| Setting | Meaning | Notes |
|---|---|---|
| `threshold` | Mute below this (dBFS) | Depends on your gain and antenna — measure it |
| `alpha` | How quickly the average follows | 0.01; smaller = steadier but slower |
| `ramp` | Samples to fade in and out | More than 0 avoids clicks |
| `gate` | True = send **nothing** when muted | Use **False** before an Audio Sink |

> ⚠️ **`gate` matters.** With `gate = True`, a closed squelch sends no samples at all. The Audio
> Sink runs out of data and the flowgraph can stall. With `gate = False` it sends zeros, which is
> silence.

**Setting the threshold:** tune to an empty frequency, read the power on a level meter (Complex
to Mag² → Moving Average → Log10 → Number Sink, as in Lab 06's S-meter), and set the threshold
about **5 dB above** that.

---

## Part 8 — The link budget

A **link budget** adds up everything between a transmitter and your receiver:

$$
P_{\text{received}} = P_{\text{transmitted}} + G_{\text{tx antenna}} - L_{\text{path}} + G_{\text{rx antenna}} - L_{\text{cable}}
$$

The loss over open space (**free-space path loss**) is:

$$
\boxed{L_{\text{fs}}\,(\text{dB}) = 20\log_{10}(d \text{ in km}) + 20\log_{10}(f \text{ in MHz}) + 32.45}
$$

> **Example — can I hear an FM station 30 km away?**
>
> | Item | Value |
> |---|---|
> | Transmitter: 50 kW | +77 dBm |
> | Path loss: 20·log₁₀(30) + 20·log₁₀(100) + 32.45 | −102 dB |
> | Whip antenna (0 dBi), 1 dB cable loss | −1 dB |
> | **Received** | **−26 dBm** |
> | Noise in 200 kHz with NF 8 dB: −174 + 53 + 8 | −113 dBm |
> | **SNR** | **87 dB** |
>
> Plenty for stereo. Buildings and hills may take 20–40 dB of that, and you still have 50 dB
> spare. That is why FM is easy — and why ADS-B (Lab 09), at 1090 MHz from an aircraft 100 km
> away, is hard.

---

## ✅ Summary

- **Power → 10·log₁₀. Amplitude → 20·log₁₀.** dBm is real power; dBFS is relative to the ADC's
  maximum.
- Thermal noise is **−174 dBm/Hz**. Noise grows with bandwidth. **Narrowing the filter is free SNR.**
- The **first amplifier** sets the noise figure. Put any LNA at the antenna.
- Set **gain** by raising it until the noise floor starts to rise, then back off 5 dB.
- **Always set `bw0` = sample rate.**
- Receiver order: **channel filter → squelch → AGC → demodulate**.
- A **link budget** tells you, before you start, whether a signal can be received.

## 🧠 Check yourself

1. What is the thermal noise floor in a 15 kHz channel, with a 6 dB noise figure?
   <details><summary>Answer</summary>−174 + 10·log₁₀(15,000) + 6 = −174 + 41.8 + 6 =
   −126.2 dBm.</details>
2. You decimate from 2 MSPS to 250 kSPS (with a proper filter). How much SNR do you gain?
   <details><summary>Answer</summary>10·log₁₀(2,000,000 / 250,000) = 9.0 dB.</details>
3. One signal's amplitude is 4 times another's. How many dB?
   <details><summary>Answer</summary>20·log₁₀(4) = 12.04 dB (amplitude → 20).</details>
4. Why put an LNA at the antenna, not next to the receiver?
   <details><summary>Answer</summary>The first stage sets the noise figure. Cable loss in front
   of the LNA adds directly to the noise figure and cannot be recovered.</details>
5. Your AGC makes the background noise swell up between words. Which setting do you change?
   <details><summary>Answer</summary><code>decay_rate</code> is too high. Lower it, so the gain
   rises more slowly.</details>
6. You raise the gain by 5 dB and the noise floor also rises by 5 dB. What does that tell you?
   <details><summary>Answer</summary>The receiver is already limited by its own noise. More gain
   will not help — improve the antenna, or add an LNA at the antenna.</details>
7. A 12-bit ADC: what is its ideal dynamic range?
   <details><summary>Answer</summary>6.02 × 12 + 1.76 = 74 dB.</details>

**Next:** [Fundamentals 07 — AM, SSB and Narrow FM →](./07_am_and_narrowband_fm.md)
