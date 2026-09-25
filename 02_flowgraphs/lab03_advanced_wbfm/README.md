# 🟠 Lab 03 — An FM Radio That Sounds Good

> **What you will build:** an FM radio with a **channel filter**, a **squelch** (silence when
> there is no station), **automatic level control (AGC)** and a real **volume control**.
> **What you will learn:** why the *order* of blocks matters, and what each of these four
> standard receiver parts does.
> **Before this:** [Lab 02](../lab02_enhanced_wbfm/README.md).
> **Time:** about 1 hour. **Difficulty:** intermediate. **Needs the radio:** yes.

---

## 🎯 Goal

Lab 01 had problems. Neighbouring stations and noise reached the decoder. Between stations
there was loud hiss. And there was no volume knob, so a strong station could come out too loud
and distorted.

Real radios use four standard parts. In this lab you add all four:

| Problem | Part that fixes it | GNU Radio block |
|---|---|---|
| Other stations and noise get into the decoder | **Channel filter** — keep only our station | Low Pass Filter |
| Loud hiss between stations | **Squelch** — mute when there is no signal | Power Squelch |
| The signal level going into the decoder keeps changing | **AGC** — automatic gain control | AGC2 |
| No way to change the loudness | **Volume** | Multiply Const |

---

## 1. Run it first

```bash
cd "02_flowgraphs/lab03_advanced_wbfm"
gnuradio-companion lab03_advanced_wbfm.grc
```

Press **F5**. You now have **four** controls:

| Control | Range | What it does |
|---|---|---|
| **Frequency** | 87.5–108 MHz | Tunes the radio (changes the LO) |
| **RF Gain** | 0–76 dB | Amplification in the radio hardware, *before* the ADC |
| **Squelch** | −80 to 0 dB | The level below which the audio is muted |
| **Volume** | 0.0–5.0 | Loudness, *after* decoding. Starts at 0.5 (see Section 3.5) |

Tune to a station and listen. Then set the squelch as described in
[Section 5](#5-setting-the-squelch).

---

## 2. The flowgraph

```
┌─────────────┐   ┌────────────┐   ┌────────────┐   ┌─────────┐   ┌─────────┐   ┌─────┐   ┌──────────┐   ┌────────┐   ┌───────┐
│ USRP Source │──▶│ Low Pass   │──▶│ Rational   │──▶│   DC    │──▶│ Squelch │──▶│ AGC │──▶│   WBFM   │──▶│ Volume │──▶│ Audio │
│   2 MSPS    │   │ Filter     │   │ Resampler  │   │ Blocker │   │         │   │     │   │ Receive  │   │        │   │ Sink  │
└─────────────┘   └─────┬──────┘   └────────────┘   └─────────┘   └─────────┘   └─────┘   └──────────┘   └────────┘   └───────┘
                        │           2 M → 384 k                                             384 k → 48 k
                        ├──▶ Spectrum
                        └──▶ Waterfall
```

The displays now connect **after** the filter. So you see exactly what the decoder receives.

---

## 3. The new blocks

### 3.1 Low Pass Filter — the channel filter

The radio delivers 2 MHz of spectrum: our station **plus** several neighbours. The filter
keeps only the middle 200 kHz, where our station is, and removes the rest.

| Setting | Value | Meaning |
|---|---|---|
| Type | FIR, complex in / complex out, real taps | IQ in, IQ out |
| Decimation | 1 | Do not change the sample rate here |
| Sample Rate | `samp_rate` (2 MHz) | |
| Cutoff Freq | 100 kHz | Keep −100 to +100 kHz: one 200 kHz FM channel |
| Transition Width | 20 kHz | The filter goes from "pass" to "block" between 100 and 120 kHz |
| Window | Hamming | A standard filter design choice |

```
   pass              block
  ▇▇▇▇▇▇▇▇▇▇▅▃▁▁▁▁▁▁▁▁▁▁▁
  0      100 120           kHz (and the same on the negative side)
```

**Why it comes first:** without it, a strong neighbouring station would reach the squelch and
the AGC. The squelch would "hear" the neighbour and stay open even when our channel is empty.
The AGC would set its gain for the neighbour, not for our station. Filtering first means they
only see our station.

> 💡 This filter has about **241 taps** (241 numbers it multiplies and adds for every
> sample). [Fundamentals 05](../../01_fundamentals/05_sampling_and_filters.md) shows how to
> work that number out.

### 3.2 DC Blocker — removing the radio's own centre spike

Every SDR has a spike exactly at the frequency it is tuned to: a little of its own tuning signal
leaks in (**DC** or **LO leakage**). This lab tunes **straight onto** the station, so the spike
sits right in the middle of our channel. The **DC Blocker** removes anything that does not
change (the 0 Hz part), and lets the station through.

| Setting | Value | Meaning |
|---|---|---|
| Type | Complex → Complex | IQ in, IQ out |
| Length | 128 | How narrow the removed band is. At 384 kSPS, only the very centre is removed |
| Long Form | True | A cleaner (two-stage) version of the filter |

**Why it is needed — measured on a real SignalSDR Pro** (gain 40, 26 September 2026). This is
the power the squelch sees:

| | With the spike | The spike alone | Without the spike |
|---|---|---|---|
| BFM 89.9 MHz (a station) | −45.1 dB | −48.6 dB | **−47.8 dB** |
| 104.0 MHz (empty) | −46.9 dB | −47.6 dB | **−55.4 dB** |

With the spike, a station and an empty channel differ by only **1.8 dB** — the spike is as strong
as the station itself — so **no** squelch setting can tell them apart. Without it, they differ by
**7.6 dB**, and the squelch works. The first version of this lab had no DC Blocker; on the real
radio, its squelch let noise through on an empty channel. With it: **complete silence** on empty
channels, and the station's audio SNR slightly **better** (63.6 dB against 61.9 dB).

> 💡 Lab 06 avoids the spike another way: it tunes the radio 200 kHz *beside* the station and
> shifts back in software, so the spike falls outside the channel.

### 3.3 Power Squelch — silence when there is no station

A **squelch** watches the signal's power. If the power is **below the threshold**, it mutes
the output. If it is **above**, it lets the signal through. Walkie-talkies use a squelch so you
don't hear hiss between calls.

| Setting | Value | Meaning |
|---|---|---|
| Threshold | `squelch_threshold` slider, starts at −50 dB | Mute below this power (dBFS) |
| Alpha | 0.01 | How quickly it follows power changes (smaller = slower, smoother) |
| Ramp | 0 | Switch instantly (no fade in or out) |
| Gate | **False** | When muted, send **zeros** (silence) rather than nothing |

> ⚠️ **Why Gate must be False.** With Gate = True, a closed squelch sends *no samples at all*.
> The Audio Sink then runs out of data, and you get `aU` (audio underrun) errors and
> stuttering. Sending zeros keeps the audio flowing — as silence.

### 3.4 AGC — automatic gain control

Stations arrive at very different strengths. A nearby station might be 1,000 times stronger
than a distant one. The signal also **fades** up and down as you move, or as buses and
buildings reflect it.

The **AGC** (automatic gain control) constantly measures the IQ signal and adjusts its own
gain to keep its output at a steady level. Think of a person with a hand on a knob, turning it
down when the signal is strong and up when it is weak.

| Setting | Value | Meaning |
|---|---|---|
| Reference | 0.5 | The target output level (half of full scale) |
| Attack Rate | 0.01 | How fast it turns **down** when the signal gets stronger. Fast, to avoid clipping |
| Decay Rate | 0.001 | How fast it turns **up** when the signal gets weaker. Slow, to avoid "pumping" |
| Gain | 1.0 | Starting gain |
| Max Gain | 65536 | The most it may amplify (about 96 dB) |

**Why is attack fast and decay slow?** If a loud signal arrives, the AGC must turn down quickly,
or the sound clips. But if it turns *up* too quickly during a quiet moment in the music, the
background noise rushes up and falls again. That sounds like breathing, and is called
**pumping**. Slow decay avoids it.

> ⚠️ **An honest note: for FM, the AGC does not change the loudness.** An FM decoder only
> measures how fast the IQ arrow *turns*, not how *long* it is
> ([Fundamentals 04](../../01_fundamentals/04_fm_theory.md#7-how-software-gets-the-sound-back)).
> So FM stations already come out at the same loudness, strong or weak. We tested this: the
> audio level was **0.512** whether the IQ signal was 0.003 or 0.5 in size, with **and**
> without the AGC.
>
> So why is it here? Because it is a standard part of every receiver, and you need to know
> where it goes. It keeps the signal at a predictable level for the decoder and for any display
> you add. And for **AM**, where the sound *is* the arrow's length, the AGC is essential —
> you will rely on it in [Lab 06](../lab06_multimode_receiver/README.md).

<details>
<summary><b>Going deeper:</b> how the AGC updates its gain</summary>

For each sample, the output is $y[n] = g[n] \cdot x[n]$. The gain is nudged towards the value
that would make $|y|$ equal the reference $R$:

$$
g[n+1] = g[n] + \text{rate} \cdot \bigl(R - |y[n]|\bigr)
$$

`AGC2` uses the **attack rate** when $|y| > R$ (too loud) and the **decay rate** when
$|y| < R$ (too quiet). The gain is kept between 0 and Max Gain.
</details>

### 3.5 Multiply Const — the volume control

Multiplies every audio sample by the `volume` slider value. 0 = silent, 1 = unchanged,
2 = twice as loud.

**Why it starts at 0.5.** In Lab 01, a strong local station came out of the WBFM Receive block
peaking at **1.86**. The Audio Sink can only play −1.0 to +1.0, so those peaks were cut off
(clipped) and sounded distorted. This lab uses the same decoder, so the same station would clip
here too at volume 1.0. At 0.5, the peaks reach about 0.93 — just inside the limit.

It works on the **decoded audio**, so it cannot affect reception at all. This is the difference
between **volume** and **gain**:

| | RF Gain | Volume |
|---|---|---|
| Where | In the radio hardware, **before** the ADC | In software, **after** decoding |
| Changes the sound quality? | **Yes.** Too little = noisy, too much = distorted | **No.** It only scales the numbers |
| Use it to | Get a good signal level into the ADC | Set how loud it is in your ears |

---

## 4. Why this order? (the most important part of this lab)

Every block in a receiver has a job, and the **order matters**. Here is why each one sits
where it does:

1. **USRP Source** — the radio. Always first.
2. **Low Pass Filter** — straight after, to remove other stations **before** anything measures
   the signal level. Otherwise the squelch and AGC react to the neighbours, not to our station.
3. **Rational Resampler** — reduces 2 MSPS to 384 kSPS. Now the later blocks have 5 times
   fewer samples to process, so the CPU does less work. (The filter already removed everything
   the lower rate cannot hold, so there is no aliasing.)
4. **DC Blocker** — removes the radio's centre spike, so the squelch measures the station, not
   the spike.
5. **Squelch** — **before** the AGC, so it measures the **real** signal strength.
6. **AGC** — after the squelch, to set a steady level for the decoder.
7. **WBFM Receive** — decodes the filtered IQ into audio.
8. **Volume** — last, on the audio only.

### Why the squelch must come before the AGC

This is easy to get wrong. (An earlier version of this lab had them the other way round, and
its squelch never worked.)

The AGC's job is to make **everything** the same level — including plain noise. When there is
no station, the AGC simply turns its gain up until the noise reaches the reference level.
A squelch placed after it would see noise that looks exactly as strong as a station, and would
never mute.

We tested this by feeding pure noise (at −60 dBFS, a typical "no station" level) into both
arrangements, with the squelch set to −50 dB:

| Order | Output power | Squelch |
|---|---|---|
| AGC → Squelch | −12.9 dB (loud hiss) | **stays open — never mutes** |
| **Squelch → AGC** | **silence** | **closes correctly** |

> **Rule:** anything that *measures* signal strength (a squelch, a signal meter) must come
> **before** anything that *changes* signal strength automatically (an AGC) — and must not be
> fooled by the radio's own centre spike.

---

## 5. Setting the squelch

The best threshold depends on your antenna, your gain setting and your location. Set it like
this:

1. Set **Squelch** to **−80** (fully open). You hear everything.
2. Tune to an **empty** frequency, between stations. You hear hiss.
3. Raise **Squelch** slowly until the hiss **just stops**.
4. Raise it **3–5 dB more**, for a safety margin.
5. Tune back to a station. It should play normally.

| Threshold | Result |
|---|---|
| Too low (e.g. −80) | Squelch never closes. Hiss between stations |
| About right | Silence between stations, audio on stations |
| Too high (e.g. −20) | Weak stations are muted too |

> 💡 If you change the **RF Gain**, the noise level changes too, so you must set the squelch
> again.

---

## 6. What you should notice

**With the volume control:**

- The distortion from Lab 01 (audio peaking at 1.86 on a strong station) is gone, because the
  volume starts at 0.5.

**With the channel filter:**

- Cleaner sound. Neighbouring stations and wideband noise no longer reach the decoder.

**With the squelch:**

- Silence between stations, instead of hiss.
- Sound starts as soon as you tune onto a station.

**Measured on real hardware** (SignalSDR Pro, BFM 89.9 MHz): this lab's audio SNR was
**62.6 dB**, against **53.2 dB** for Lab 01. The channel filter is the main reason.

---

## 7. Experiments

1. **Squelch.** Tune off-station. Find the threshold where the hiss stops.
2. **FM ignores strength.** Compare a strong and a weak station. They are about equally
   loud — but the weak one is noisier. Loudness in FM comes from the transmitter's deviation,
   not from signal strength.
3. **Disable the AGC** (right-click → Bypass). Does the sound change? For FM it should not.
   Lower **RF Gain** to 10 dB: the station gets noisier, but not quieter.
4. **Volume.** Set it to 0: silence. Set it to 5: loud. Notice the sound *quality* does not
   change, only the loudness.
5. **Try the old order.** In GRC, rewire it as Resampler → AGC → Squelch → WBFM. Run it and
   tune off-station. Can you make the squelch close at *any* threshold below 0 dB? Put it back
   afterwards.

---

## 🔧 Troubleshooting

| Problem | Try this |
|---|---|
| Hiss between stations | Squelch threshold too low. Raise it (Section 5) |
| Squelch never closes, whatever the threshold | The DC Blocker is missing or disabled: the radio's centre spike keeps the squelch open (Section 3.2) |
| Weak stations are muted | Squelch threshold too high. Lower it by 5 dB |
| A neighbouring station can be heard underneath | Make the filter narrower (cutoff 80 kHz) |
| Audio distorted | Lower **Volume** (try 0.3) and turn up your computer's speakers instead. If still distorted, lower **RF Gain** |
| Stuttering, `aU` in the terminal | Check the squelch's **Gate** is **False** |

---

## ✅ Summary

- A good receiver adds a **channel filter**, a **squelch**, an **AGC** and a **volume** control.
- **Order matters.** Filter first. Remove the centre spike. Squelch **before** AGC. Volume last.
- When you tune straight onto a station, the radio's centre spike can be as strong as the
  station. A **DC Blocker** removes it.
- The AGC makes noise as loud as a station, so a squelch after it can never mute.
- **Gain** (before the ADC) affects sound quality. **Volume** (after decoding) does not.
- AGC attack is fast (avoid clipping); decay is slow (avoid pumping).
- FM loudness does not depend on signal strength. The AGC matters much more for AM (Lab 06).

## 🧠 Check yourself

1. Why does the channel filter come before the AGC?
   <details><summary>Answer</summary>So a strong neighbouring station cannot make the AGC
   turn down, which would make our station quieter.</details>
2. Why does the squelch come before the AGC?
   <details><summary>Answer</summary>The AGC raises noise to the same level as a real station.
   After the AGC, the squelch cannot tell them apart and never mutes.</details>
3. What is the difference between RF gain and volume?
   <details><summary>Answer</summary>RF gain acts in the hardware before the ADC and changes
   the signal-to-noise ratio. Volume scales the decoded audio in software and does not change
   the quality.</details>
4. A weak and a strong FM station come out equally loud. Is that because of the AGC?
   <details><summary>Answer</summary>No. An FM decoder ignores the signal's strength and only
   measures how fast it turns. They would be equally loud without the AGC too. (The weak one is
   noisier, though.)</details>
5. Why is the AGC's decay slower than its attack?
   <details><summary>Answer</summary>To avoid "pumping": fast increases in gain during quiet
   moments would make the background noise surge up and down.</details>
6. Why must the squelch's Gate setting be False here?
   <details><summary>Answer</summary>With Gate = True, a closed squelch sends no samples, so
   the Audio Sink runs out of data and stutters. With False, it sends zeros (silence).</details>

**Next:** [Lab 04 — Stereo FM →](../lab04_stereo_wbfm/README.md)
