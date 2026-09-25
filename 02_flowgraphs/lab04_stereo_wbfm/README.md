# 🔴 Lab 04 — Stereo FM, Built by Hand

> **What you will build:** a stereo FM receiver, **without** the ready-made WBFM Receive block.
> You build every step yourself: the FM decoder, the pilot tone recovery, the 38 kHz
> subcarrier, and the left/right matrix.
> **What you will learn:** how stereo is hidden inside an FM broadcast, what a **PLL** does,
> why **filter delay** matters, and how to check a design with a test signal.
> **Before this:** [Lab 03](../lab03_advanced_wbfm/README.md) and
> [Fundamentals 04 §5](../../01_fundamentals/04_fm_theory.md#5-what-is-inside-an-fm-broadcast).
> **Time:** about 2 hours. **Difficulty:** advanced. **Needs the radio:** yes (or a test file).

---

## 🎯 Goal

Hear a music station in **real stereo**: instruments on the left, others on the right.
Use headphones.

To get there, you will rebuild what a stereo FM radio does inside, block by block.

---

## 1. How stereo hides inside FM (a quick reminder)

After FM decoding, you do not get left and right audio. You get the **MPX** signal
([Fundamentals 04](../../01_fundamentals/04_fm_theory.md#5-what-is-inside-an-fm-broadcast)):

```
 strength
    │ ████████      │     ▓▓▓▓▓▓▓▓▓ ▓▓▓▓▓▓▓▓▓    ░
    └─┴───────┴───┴─┴───┴─────────┴─────────┴──┴─┴──── frequency (kHz)
      0       15    19   23        38        53   57
      └─ L+R ─┘   pilot  └──────── L−R ────────┘  RDS
```

| Part | Where | What it is |
|---|---|---|
| **L+R** | 0–15 kHz | Left plus right: the normal mono sound |
| **Pilot** | 19 kHz | A steady tone, sent so receivers can rebuild the 38 kHz carrier |
| **L−R** | 23–53 kHz | Left minus right, moved up to sit around 38 kHz |
| **RDS** | 57 kHz | Data (Lab 08). Ignored here |

Once you have L+R and L−R, getting left and right is simple arithmetic:

```
 (L+R) + (L−R) = 2L      →  left
 (L+R) − (L−R) = 2R      →  right
```

**The hard part is L−R.** It was moved up to 38 kHz by multiplying it with a 38 kHz carrier.
To move it back down, you multiply by the *same* 38 kHz carrier again. But the station does
**not send** the 38 kHz carrier (this saves power). It only sends the 19 kHz **pilot**. So the
receiver must **rebuild** the 38 kHz carrier from the pilot — and get its timing (phase) exactly
right. Most of this lab is about that.

---

## 2. Run it first

```bash
cd "02_flowgraphs/lab04_stereo_wbfm"
gnuradio-companion lab04_stereo_wbfm.grc
```

Press **F5**. Tune to a **music** station (talk stations are often mono). Put on headphones.

| Control | Range | What it does |
|---|---|---|
| **Frequency** | 87.5–108 MHz | Tunes the radio |
| **RF Gain** | 0–76 dB | Hardware gain. Stereo needs a stronger signal than mono |
| **Volume** | 0.0–3.0 | Loudness of both channels |

The **MPX Spectrum** display shows the decoded MPX. Look for the thin **pilot line at 19 kHz**.
If you can see it, the station is in stereo.

> 💡 **No radio?** Make a stereo test signal and run the real flowgraph on it — see
> [Section 7](#7-test-it-with-a-signal-you-know).

---

## 3. The flowgraph

```
 USRP Source (2 MSPS)
      │
 Low Pass Filter (±100 kHz)          keep one station
      │
 Rational Resampler (×12 ÷100)       2 MSPS → 240 kSPS
      │
 Quadrature Demod                    FM → MPX (a float signal)
      │
      ├─────────────────────────────────────────┐
      │                                         │
 Delay (578 samples)                    Band Pass Filter, COMPLEX out
      │                                  (18.5–19.5 kHz): the pilot
      │                                         │
      │                                 PLL Refout: a clean 19 kHz tone
      │                                         │
      │                                 Multiply by itself: 38 kHz
      │                                         │
      │                                 Complex to Imag
      │                                         │
      ├──────────────┐                          │
      │              ▼                          │
      │          Multiply ◀─────────────────────┘   L−R comes down to audio
      │              │
 Low Pass (15 kHz, ÷5)   Low Pass (15 kHz, ÷5)
      │              │
      │          ×(−2)
      │              │
 De-emphasis     De-emphasis          50 µs (Malaysia)
   (L+R)           (L−R)
      │              │
      ├──── Add ─────┤──▶ ×0.5×volume ──▶ Audio Sink, left
      └── Subtract ──┘──▶ ×0.5×volume ──▶ Audio Sink, right
```

Rates: 240,000 samples/s until the two 15 kHz low-pass filters, which also decimate by 5, to
**48,000** samples/s audio.

---

## 4. The steps, one by one

### Step 1 — From IQ to MPX

| Block | Settings | Job |
|---|---|---|
| USRP Source | 2 MSPS, `bw0` = 2 MHz | The radio |
| Low Pass Filter | cutoff 100 kHz, width 20 kHz | Keep only our station |
| Rational Resampler | ×12 ÷100 | 2,000,000 × 12/100 = **240,000** samples/s |
| Quadrature Demod | gain = 240000 / (2π × 75000) | FM decoder. Full deviation (±75 kHz) comes out as ±1 |

Why 240 kSPS? The MPX goes up to about 60 kHz. By the Nyquist rule, a real (float) signal
needs more than 2 × 60 = 120 kSPS. 240 kSPS gives plenty of room.

The output of the Quadrature Demod is the **MPX**: a float signal containing L+R, the pilot
and L−R.

### Step 2 — L+R (the mono sound)

A **low-pass filter at 15 kHz** keeps only 0–15 kHz of the MPX. That is L+R. The filter also
**decimates by 5**: 240,000 ÷ 5 = 48,000 samples/s, the audio rate.

### Step 3 — Recover the pilot, and clean it up with a PLL

**Band Pass Filter (18.5–19.5 kHz).** Keeps only the 19 kHz pilot.
It is set to **Float → Complex** (complex taps). This keeps only the *positive* 19 kHz, and
throws away the −19 kHz mirror image that every real signal has
([Fundamentals 02](../../01_fundamentals/02_iq_sampling.md)). The next block works much better
with a single clean tone.

**PLL Refout.** A **PLL** (phase-locked loop) is a circuit — here, code — that produces its own
tone and constantly adjusts it to match an incoming tone in **frequency and phase**. Think of
someone clapping along to music: they listen, and speed up or slow down until their claps land
exactly on the beat.

Why not just use the filtered pilot directly? Because it is noisy and it wobbles. The PLL's
output is a **perfectly clean** 19 kHz tone that follows the pilot exactly.

| Setting | Value | Meaning |
|---|---|---|
| Loop bandwidth `w` | 0.05 | How quickly it follows changes |
| Min / max frequency | 18.5 / 19.5 kHz | It will only lock inside this range |

[Fundamentals 09](../../01_fundamentals/09_synchronization.md) explains PLLs in detail.

### Step 4 — Double the pilot to make 38 kHz

**Multiply** the PLL's output by itself. For a spinning IQ arrow, multiplying by itself
**doubles the angle**, so 19 kHz becomes **38 kHz**, with the phase also doubled — exactly
locked to the pilot, as the standard requires.

**Complex to Imag.** Take the imaginary part (Q) of the 38 kHz tone. Why the imaginary part and
not the real part? See the box below.

> 🔎 **Why "Imag" and "−2"? (the sine rule)**
>
> The FM stereo standard sends the pilot as a **sine** wave, and the 38 kHz carrier as a
> **sine** wave too, both crossing zero at the same moment.
>
> The PLL copies the pilot's phase. Doubling a sine-phase tone gives:
>
> ```
>  (PLL output)²  =  −cos(2ωt)  −  j·sin(2ωt)
> ```
>
> The carrier we need is **+sin(2ωt)**. That is **minus the imaginary part**. So we take the
> imaginary part here, and the minus sign goes into the ×(−2) block in Step 5.
>
> If you take the **real part** instead (−cos), it is a quarter-turn out of step. Multiplying
> L−R by a carrier a quarter-turn out of step gives **zero** — no stereo at all.

<details>
<summary><b>Going deeper:</b> the maths</summary>

The standard MPX (ITU-R BS.450) is:

$$
m(t) = 0.9\left[\frac{L+R}{2} + \frac{L-R}{2}\sin(2\omega_p t)\right] + 0.1\sin(\omega_p t),
\qquad \omega_p = 2\pi \cdot 19\,\text{kHz}
$$

The PLL output follows the pilot's phase: $\sin(\omega_p t) = \cos(\omega_p t - \tfrac{\pi}{2})$,
so the PLL gives $e^{j(\omega_p t - \pi/2)}$. Squared:

$$
e^{j(2\omega_p t - \pi)} = -\cos(2\omega_p t) - j\sin(2\omega_p t)
$$

$-\,\text{Imag} = \sin(2\omega_p t)$. Multiplying the MPX by it and low-pass filtering:

$$
m(t)\sin(2\omega_p t) \;\xrightarrow{\text{LPF}}\; 0.9\,\frac{L-R}{2}\cdot\frac{1}{2}
$$

because $\sin^2\theta = \tfrac12 - \tfrac12\cos 2\theta$. The ×2 restores the lost half, giving
$0.9\,\frac{L-R}{2}$ — the same scale as the L+R path, $0.9\,\frac{L+R}{2}$. So the matrix gives
$0.9L$ and $0.9R$.
</details>

### Step 5 — Bring L−R down to audio

**Multiply** the MPX by the rebuilt 38 kHz carrier. This moves L−R from around 38 kHz down to
0–15 kHz (and makes some copies at around 76 kHz, which we throw away).

**Low-pass filter at 15 kHz, decimate by 5** — the same as the L+R path. It removes everything
except L−R and brings it to 48 kHz.

**Multiply Const ×(−2).** The multiplication halved the size of L−R, so ×2 restores it. The
minus sign is the one from the box above.

### Step 6 — The delay: keeping the two paths in step

This is the subtle part, and the most important lesson in this lab.

Every filter **delays** the signal a little. A filter with many taps delays it more. The pilot's
band-pass filter is very narrow (only 1 kHz wide), so it needs many taps — **1,157** — and delays
the pilot by **578 samples**, about 2.4 ms.

So the rebuilt 38 kHz carrier is 2.4 ms **late** compared with the MPX. At 38 kHz, 2.4 ms is
about 91.5 cycles. The ".5" means the carrier arrives half a cycle out of step — completely
wrong. Any other delay would give some other wrong phase.

**The fix:** delay the MPX by the **same** 578 samples before it is used. Then everything lines
up again. In the flowgraph, the **Delay** block does this. Its value is not typed by hand; it is
calculated from the filter itself:

```python
(len(firdes.complex_band_pass(1, mpx_rate, 18500, 19500, 500, window.WIN_HAMMING, 6.76)) - 1) // 2
```

A symmetric FIR filter with N taps delays by (N−1)/2 samples. If you change the filter, the
delay follows automatically.

> 💡 The delayed MPX feeds **both** the L+R path and the L−R multiplier. That keeps L+R and L−R
> in step with each other too. If only one path were delayed, left and right would be mixed
> up again.

### Step 7 — De-emphasis

Both L+R and L−R go through a de-emphasis filter
([Fundamentals 04 §6](../../01_fundamentals/04_fm_theory.md#6-pre-emphasis-and-de-emphasis)).
Here it is a **Single Pole IIR Filter**, with:

$$
\alpha = 1 - e^{-1/(\text{audio\_rate} \times \tau)} = 1 - e^{-1/(48000 \times 50\times10^{-6})} \approx 0.341
$$

The variable `deemph_tau` is **50e-6** (50 µs, the Malaysian standard). Change it to 75e-6 for
the USA.

### Step 8 — The stereo matrix

- **Add:** (L+R) + (L−R) = 2L → left.
- **Subtract:** (L+R) − (L−R) = 2R → right.
- **Multiply Const:** × 0.5 × volume on each, to undo the factor of 2 and apply the volume.
- **Audio Sink** with 2 inputs: input 0 = left, input 1 = right.

---

## 5. What went wrong in the first version (and how it was found)

The first version of this lab had **two** mistakes. Together, they made it almost exactly mono:
about **1 dB** of stereo separation, when a good receiver gives 30 dB or more.

1. **No delay** on the MPX path (Step 6). The rebuilt carrier had the wrong phase.
2. **The real part** was used instead of the imaginary part (Step 4). Wrong by a quarter-turn.

It also fed the PLL a real (float) pilot, with its −19 kHz mirror, which cost more separation.

It sounded fine — music played, in both ears. A test on real radio even showed the left and
right channels were different (correlation 0.78). But normal music is partly different in each
channel anyway. That number could not tell "stereo" from "mono plus noise".

What found the bug was a **test signal with known content**: a 1000 Hz tone on the left only
and a 1700 Hz tone on the right only. A working decoder must put almost no 1700 Hz in the left
channel. Results, running the real flowgraph:

| Version | Left separation | Right separation |
|---|---|---|
| First version | 1.2 dB | −0.4 dB |
| Delay added, still real part | about 1 dB | about 1 dB |
| Imag part, no delay | −20 dB (left and right **swapped**!) | −14 dB |
| Delay + imag part, float pilot | 19.8 dB | 14.4 dB |
| **Delay + imag part + complex pilot filter (this version)** | **32.5 dB** | **31.0 dB** |
| An ideal decoder, for comparison | 146 dB | 155 dB |

About 30 dB is typical for a real FM stereo receiver.

> **Lesson:** "it plays music" is not a test. Test with a signal whose right answer you know.

---

## 6. Limitation: mono stations

Real radios have a **pilot detector**. If there is no 19 kHz pilot, they switch to mono.

This lab does not. On a **mono** station, the PLL has no pilot to follow, so the rebuilt
carrier is wrong, and some of the mono sound leaks into L−R. Measured with a mono test signal,
the leftover L−R was about **10 dB** below L+R. You may hear the sound pulled slightly to one
side. It is still easy to listen to.

**Challenge:** add a pilot detector. Measure the power coming out of the pilot band-pass filter
(a **Complex to Mag²** block and a **Moving Average**). When it is too low, multiply L−R by 0.

---

## 7. Test it with a signal you know

You can check this lab with **no radio at all**, using two helper scripts:

```bash
cd 03_scripts

# 1. make 3 seconds of stereo FM: 1000 Hz on the left only, 1700 Hz on the right only
python3 make_test_iq.py /tmp/stereo.cfile

# 2. run the real Lab 04 flowgraph on it, and save the audio
python3 run_offline.py ../02_flowgraphs/lab04_stereo_wbfm/lab04_stereo_wbfm.py \
        /tmp/stereo.cfile --out /tmp/lab04_out
```

Expected output:

```
channel 0: 143992 samples at 48000 Hz (3.00 s)  rms 0.2370
channel 1: 143992 samples at 48000 Hz (3.00 s)  rms 0.2195
```

To hear it: `play -t f32 -r 48000 -c 1 /tmp/lab04_out/audio_ch0.f32` (from the `sox` package).
You should hear only the lower tone in the left file, and only the higher tone in the right.

`test_labs_offline.py` (in the same folder) runs this check automatically and fails if the
separation drops below 25 dB.

---

## 8. Experiments

1. **Remove the delay.** Set the Delay block's value to 0 and run the test in Section 7. What
   happens to the separation? (Look at the table in Section 5.)
2. **Swap to the real part.** Replace Complex to Imag with Complex to Real. What happens?
3. **Watch the pilot.** On the MPX Spectrum, find the 19 kHz pilot and the L−R humps either side
   of 38 kHz. On a mono station, the pilot is missing.
4. **Talk vs music.** Many talk stations are mono. Compare them.
5. **De-emphasis.** Change `deemph_tau` to 75e-6. The treble becomes slightly duller.

---

## 🔧 Troubleshooting

| Problem | Try this |
|---|---|
| A whine or buzz in the audio | The PLL is not locked. Is there a pilot at 19 kHz on the MPX display? Is the station stereo? |
| Sounds mono on a music station | Check the pilot is visible. Raise the gain — stereo needs a stronger signal than mono |
| Stereo is hissy but mono was clean | Normal: stereo needs about 20 dB more signal than mono. Find a stronger station |
| Left and right are swapped | Check the ×(−2) block still has the minus sign |
| Everything is twice as loud | The ×0.5 in the final Multiply Const blocks is missing |

---

## ✅ Summary

- Stereo FM sends **L+R** normally and **L−R** on a 38 kHz carrier that is **not transmitted**.
- The receiver rebuilds 38 kHz by **doubling** the 19 kHz **pilot**, using a **PLL**.
- The standard uses **sine** phase, so the carrier is −Imag of the doubled PLL output.
- **Every filter delays the signal.** Paths that meet again must be delayed equally. A narrow
  filter delays a lot: here 578 samples.
- Test with a **known** signal. "It plays music" hid a decoder that was really mono.

## 🧠 Check yourself

1. Why does the station send a 19 kHz pilot instead of the 38 kHz carrier itself?
   <details><summary>Answer</summary>Not sending the 38 kHz carrier saves transmitter power,
   and a 19 kHz tone sits in an empty gap between L+R and L−R where it is easy to filter out.
   Doubling it gives exactly 38 kHz.</details>
2. What does a PLL do?
   <details><summary>Answer</summary>It makes its own clean tone and keeps adjusting it until it
   matches an incoming tone in frequency and phase.</details>
3. Why is there a Delay block of 578 samples?
   <details><summary>Answer</summary>The narrow pilot filter delays the pilot by 578 samples.
   The MPX must be delayed by the same amount so the rebuilt carrier lines up with it.</details>
4. A station is mono. What happens to the L−R path in real radios, and in this lab?
   <details><summary>Answer</summary>Real radios detect the missing pilot and switch to mono.
   This lab does not, so a little of the mono sound leaks into L−R.</details>
5. You measure left/right correlation 0.78 on real music. Does that prove the decoder works?
   <details><summary>Answer</summary>No. Real music is partly different in each channel anyway.
   You need a test signal where you know exactly what should come out of each channel.</details>

**Next:** [Lab 05 — Record and Play Back Radio →](../lab05_iq_record_playback/README.md)

---

## 📖 References

1. [FM broadcasting](https://en.wikipedia.org/wiki/FM_broadcasting) (Wikipedia)
2. ITU-R Recommendation BS.450 — Transmission standards for FM sound broadcasting
3. GNU Radio's own stereo decoder: `gr-analog/python/analog/wfm_rcv_pll.py`, which uses the
   same delay and −Imag approach
4. [USRP B210 manual](https://files.ettus.com/manual/page_usrp_b200.html)
