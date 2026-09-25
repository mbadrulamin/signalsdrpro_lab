# 🔒 Fundamentals 09 — Synchronisation: PLLs, Costas Loops and Timing

> **What you will learn:** the three things every digital receiver must lock on to; the feedback
> loop that does it; **loop bandwidth**; the PLL; the Costas loop; symbol timing recovery; the
> right order of blocks; and how to diagnose problems from the constellation display.
> **Before this:** [Fundamentals 08 — Digital Modulation](./08_digital_modulation.md).
> **Time:** about 50 minutes. **Used by:** Lab 04 (looking back), Labs 07 and 08.

---

## Why this chapter exists

In Lab 04 you used a **PLL Refout** block with a loop bandwidth of `0.05`, and it worked. But why
0.05? What would 0.5 do? What do you do when it will not lock?

Synchronisation is the part of a receiver that people skip — and then spend a week debugging. A
digital receiver must lock on to **three** things. Each is solved by the same kind of feedback
loop:

| # | What must be found | If it is wrong, the constellation… | Solved by |
|---|---|---|---|
| 1 | **Carrier frequency** | spins into a **ring** | Costas loop (or an FLL) |
| 2 | **Carrier phase** | is **rotated** by a fixed angle | Costas loop |
| 3 | **Symbol timing** | is **smeared** along lines; the eye is closed | Symbol Sync |

Get all three right, and the constellation snaps into tight dots.

---

## Part 1 — One feedback loop, used everywhere

Every block in this chapter is built from the same three parts:

```
             ┌──────────────┐
  input ────▶│   Error      │──── error ───┐
        ┌───▶│  detector    │              │
        │    └──────────────┘              ▼
        │                           ┌─────────────┐
        │                           │ Loop filter │
        │                           │ (α and β)   │
        │                           └──────┬──────┘
        │    ┌──────────────┐              │
        └────┤ Adjustable   │◀─────────────┘
             │ oscillator   │
             └──────────────┘
```

1. **Error detector** — measures how wrong we are right now. This is the only part that changes
   from one block to another.
2. **Loop filter** — decides how much to correct. It has two parts: α corrects the **phase**
   now; β slowly builds up a correction for the **frequency**.
3. **Adjustable oscillator** — applies the correction (a numbered oscillator, "NCO", or a timing
   interpolator).

Think of steering a car to stay in the middle of a lane. You look at how far off you are (error),
decide how much to turn (loop filter), and turn the wheel (oscillator). Turn too hard, and you
zig-zag. Turn too gently, and you drift off before you correct.

### The one setting that matters: loop bandwidth

You do not choose α and β yourself. You choose:

- **Loop bandwidth** *B* — how quickly the loop reacts, as a fraction of the sample rate (a small
  number like 0.01).
- **Damping** ζ — how smoothly it settles. GNU Radio uses ζ = 1/√2 ≈ 0.707, which is almost
  always right.

### The trade-off behind every loop

$$
\boxed{\text{wide loop} \Rightarrow \text{locks fast, but noisy}}
\qquad
\boxed{\text{narrow loop} \Rightarrow \text{smooth, but locks slowly — or never}}
$$

A wide loop follows the signal quickly — but it also follows the **noise**, so its output
wobbles (called **jitter**). A narrow loop ignores the noise, but may be too slow to catch a
large frequency error. **Choosing between these is loop design.**

| Where | Loop bandwidth used | Why |
|---|---|---|
| FM stereo pilot (Lab 04) | 0.05 | The pilot is very steady and strong; a clean ±500 Hz filter comes first |
| BPSK link (Lab 07) | 0.010 (slider) | Must follow a frequency error and clock drift, in noise |
| RDS (Lab 08) | 0.010 (slider) | A weak signal, but steady: narrow is good |
| At Eb/N0 = 2 dB (Lab 07, Exercise 3) | 0.045 **fails**, 0.010 works | At low SNR a wide loop follows the noise and loses lock |

**A practical method:** start wide to lock on quickly, then narrow it to track cleanly. Labs 07
and 08 put the loop bandwidth on a slider, so you can watch the constellation tighten and loosen.

<details>
<summary><b>Going deeper:</b> how GNU Radio turns the bandwidth into α and β</summary>

GNU Radio's loops (Costas, PLL, FLL) all use the same `control_loop` code:

$$
\alpha = \frac{4\zeta B}{1 + 2\zeta B + B^2}, \qquad
\beta = \frac{4B^2}{1 + 2\zeta B + B^2}
$$

and update, each sample:

$$
\text{freq} \leftarrow \text{freq} + \beta\, e, \qquad \text{phase} \leftarrow \text{phase} + \text{freq} + \alpha\, e
$$

Check it against a real block:

```bash
python3 -c "
from gnuradio import digital
for bw in (0.001, 0.01, 0.045):
    c = digital.costas_loop_cc(bw, 2); z = c.get_damping_factor()
    d = 1 + 2*z*bw + bw*bw
    print(f'bw={bw:<6} GNU Radio alpha={c.get_alpha():.6f} beta={c.get_beta():.8f} | '
          f'formula alpha={4*z*bw/d:.6f} beta={4*bw*bw/d:.8f}')"
```

The two columns agree exactly. (Some textbooks first convert *B* with
θ = *B* / (ζ + 1/4ζ). GNU Radio's `control_loop` does **not**; Symbol Sync uses its own timing
loop.)
</details>

---

## Part 2 — The PLL

A **PLL** (phase-locked loop) makes its own clean tone and keeps adjusting it to match an incoming
tone. Its error detector is simply the **phase difference** between the input and its own tone.

### GNU Radio's three PLL blocks

| Block | Outputs | Use it to |
|---|---|---|
| **PLL Refout** | a clean tone at the locked frequency | **rebuild a carrier** — Lab 04's 19 kHz pilot |
| **PLL Carrier Tracking** | the input, with its phase corrected | coherent AM or DSB decoding |
| **PLL Freq Det** | the frequency it measures | another way to decode FM |

Settings: `w` = loop bandwidth; `max_freq` and `min_freq` = the search range, in **radians per
sample**:

$$
\omega = \frac{2\pi \times f_{\text{Hz}}}{f_s}
$$

> **Example — Lab 04's pilot PLL.** Lock to 19 kHz at *f*ₛ = 240 kHz, searching ±500 Hz:
>
> $$\omega_{\max} = \frac{2\pi \times 19500}{240000} = 0.5105, \qquad \omega_{\min} = \frac{2\pi \times 18500}{240000} = 0.4843$$
>
> **A narrow search range is the best cure for a PLL that locks onto the wrong thing.**

### Knowing when it is locked

A PLL that has lost lock still outputs a tone — but the wrong one. A good receiver checks: it
compares the input with the PLL's tone over a short time. If they do not match, it is not locked.
For stereo, a real radio then switches to mono (Lab 04 does not — see its Section 6).

---

## Part 3 — The Costas loop: a carrier with no carrier

BPSK and QPSK have **no carrier** to lock to: the data keeps flipping the phase by 180°. A plain
PLL is confused. The **Costas loop** has an error detector that **removes the data first**.

### For BPSK (order 2)

$$
e = \text{Re}\{y\} \times \text{Im}\{y\}
$$

Why this works: flipping the phase by 180° changes the sign of **both** Re and Im, so their
product does not change. The data cancels out, and only the phase error is left.

### For QPSK (order 4)

$$
e = \text{sign}(\text{Re}\{y\}) \cdot \text{Im}\{y\} - \text{sign}(\text{Im}\{y\}) \cdot \text{Re}\{y\}
$$

The sign decisions remove the QPSK data in the same way.

### The price: which way up?

Because the data cancels, the loop is equally happy at several angles: order 2 (BPSK) at 0° or
**180°**; order 4 (QPSK) at 0°, 90°, 180° or 270°. The loop cannot tell which is right. Two cures:

1. **Differential encoding** ([Fundamentals 08 §5](./08_digital_modulation.md#part-5--differential-encoding))
   — the problem cancels out; the BER roughly doubles (about 0.5 dB). RDS uses this (Lab 08).
2. **A known pattern** — send a known sync word, and rotate the constellation until the sync word
   comes out right. Many digital TV and Wi-Fi systems do this with known "pilot" symbols.

Lab 07 shows you the problem and cure 1 (its Exercise 4).

### GNU Radio's Costas Loop block

| Setting | Meaning |
|---|---|
| `w` | loop bandwidth (e.g. 0.010) |
| `order` | **2** for BPSK, **4** for QPSK, 8 for 8PSK |

It also has optional outputs: **frequency**, phase and error. Connect **frequency** to a time
plot, and you can **watch the loop lock** — the best debugging tool you have (Lab 07 does this).

---

## Part 4 — Symbol timing recovery

The transmitter's clock and the receiver's clock are never exactly the same. So:

- the receiver may sample at the **wrong moment** inside each symbol, and
- even if it starts right, the sampling moment slowly **drifts**.

Sampling away from the centre of each pulse makes the symbol weaker **and** mixes in parts of its
neighbours (ISI).

### The eye diagram

Draw every two-symbol stretch of the signal on top of each other. The picture looks like an eye.
**The widest point of the eye is the right moment to sample.**

```
   good timing, clean signal       bad timing, or noisy
   ╲                    ╱         ╲   ╱╲   ╱
    ╲                  ╱           ╲ ╱  ╲ ╱
     ╲________________╱             X    X
     ╱                ╲            ╱ ╲  ╱ ╲
    ╱                  ╲          ╱   ╲╱   ╲
   ╱      ← open →      ╲            closed
```

GNU Radio has a **QT GUI Eye Sink**. Lab 07 uses one.

### Timing error detectors

| Method | Needs the carrier locked first? | Notes |
|---|---|---|
| **Mueller & Müller** | yes | efficient; uses decisions about which symbol was sent |
| **Gardner** | **no** | works **before** carrier lock — very useful |
| Zero crossing | yes | simple; needs frequent changes in the data |
| Early–late | yes | easy to understand, more work |

**Gardner** looks at the sample **half-way between** two symbols. If the timing is right, and the
symbol changed, that middle sample is near zero. It only uses sizes and signs, not the carrier
phase — so timing can be found **before** the carrier. That order is much easier to debug.
Labs 07 and 08 use Gardner.

<details>
<summary><b>Going deeper:</b> the two formulas</summary>

Mueller & Müller:

$$
e[n] = \text{Re}\{\hat{a}[n-1]^* \, y[n] - \hat{a}[n]^* \, y[n-1]\}
$$

Gardner:

$$
e[n] = \text{Re}\bigl\{\bigl(y[n] - y[n-1]\bigr)^* \, y[n - \tfrac{1}{2}]\bigr\}
$$
</details>

### GNU Radio's Symbol Sync block

| Setting | Typical | Meaning |
|---|---|---|
| `ted_type` | `digital.TED_GARDNER` | which timing error detector |
| `sps` | 4 | input samples per symbol (may be a fraction, like 4.21 in Lab 08) |
| `loop_bw` | 0.010 | loop bandwidth |
| `damping` | 1.0 | |
| `max_dev` | 1.5 | the largest timing correction allowed |
| `osps` | 1 | output samples per symbol |
| `resamp_type` | `digital.IR_PFB_MF` | a polyphase **matched filter** — the best choice |
| `pfb_mf_taps` | your RRC taps (made 32× finer — see Lab 07) | |

With `IR_PFB_MF`, the block does the **matched filtering and** the timing recovery together. That
is faster and more accurate than two separate blocks.

---

## Part 5 — The right order

```
IQ in
  │
  ▼
[ AGC ]                          bring the level to about 1 — the loops expect it
  │
  ▼
[ rough frequency correction ]   (optional) bring a big frequency error within the Costas range
  │
  ▼
[ Symbol Sync + matched filter ] Gardner works without carrier lock
  │
  ▼
[ Costas Loop ]                  now fix phase and frequency, one sample per symbol
  │
  ▼
[ Slicer / Constellation Decoder ]
  │
  ▼
[ Differential decoder ] → bits
```

### Diagnose from the constellation

This table will save you hours:

| What you see | What is wrong | Try |
|---|---|---|
| A **ring** | frequency error; Costas not locked | widen `w`; add a rough frequency correction; check `sps` |
| Tight dots, but **rotated** | a fixed phase error | normal before Costas; after it, check `order` |
| Dots **smeared into lines** from the centre | timing error | check `sps`; widen Symbol Sync's `loop_bw` |
| A fuzzy **cloud** | too much noise | better antenna, more gain, narrower filter |
| Good dots that sometimes **jump** | "cycle slips" — the loop is too wide | narrow `w` |
| **Two** dots where you expect **four** | wrong Costas `order` | set `order = 4` for QPSK |
| Everything at the **centre** | no signal, or muted | check the blocks before |

---

## ✅ Summary

- A digital receiver must find **frequency**, **phase** and **timing**.
- Each is found by a **feedback loop**: error detector → loop filter → adjustable oscillator.
- **Loop bandwidth** is the key setting: wide = fast but noisy; narrow = clean but slow.
- A **PLL** follows a real tone (the Lab 04 pilot). A **Costas loop** follows a carrier that is not
  sent, by removing the data first — which leaves a 180° (or 90°) ambiguity.
- **Gardner** timing recovery works before carrier lock, so do timing first.
- **The constellation tells you what is wrong.** Learn the table in Part 5.

## 🧠 Check yourself

1. What loop bandwidth suits a very steady tone, and why?
   <details><summary>Answer</summary>Narrow. The tone does not move, so speed does not matter;
   a narrow loop gives the least jitter.</details>
2. Why can a plain PLL not lock onto BPSK?
   <details><summary>Answer</summary>The data keeps flipping the phase by 180°, so there is no
   steady phase to follow. A Costas loop removes the data first.</details>
3. Your QPSK constellation is a turning ring. Give two possible causes.
   <details><summary>Answer</summary>(a) The Costas loop is too narrow to catch the frequency
   error. (b) Its <code>order</code> is 2 instead of 4.</details>
4. Why does Gardner not need the carrier to be locked?
   <details><summary>Answer</summary>It only compares sizes and signs of samples between
   symbols, which do not depend on the carrier's phase.</details>
5. What does a 90° ambiguity mean for your data?
   <details><summary>Answer</summary>Your bits may come out in any of four rotations. Fix it
   with differential encoding or a known sync word.</details>
6. In GNU Radio, a Costas loop with bandwidth 0.001 and ζ = 0.707: what are α and β?
   <details><summary>Answer</summary>d = 1 + 2(0.707)(0.001) + 0.001² = 1.001415.
   α = 4 × 0.707 × 0.001 / d ≈ 2.824 × 10⁻³; β = 4 × 0.001² / d ≈ 3.99 × 10⁻⁶. (Check with
   <code>digital.costas_loop_cc(0.001, 2).get_alpha()</code>.)</details>

**Next:** [Fundamentals 10 — Error Detection and Framing →](./10_error_detection_and_framing.md)
