# 🔒 Fundamentals 09 — Synchronization: PLLs, Costas Loops & Timing Recovery

> **Prerequisite:** Digital Modulation (Fundamentals 08)
> **Time to read:** 50 minutes
> **Used by:** Lab 04 (retroactively!), Lab 07, Lab 08

---

## Why This Chapter Exists

In Lab 04 you dropped a **PLL Refout** block into the flowgraph, set a bandwidth of `0.001`,
and it worked. You did not know *why* 0.001, or what would have happened at 0.1, or what to do
when it refuses to lock.

Synchronization is the part of a digital receiver that people skip and then spend a week
debugging. There are exactly **three** things a receiver must synchronise, and every one of
them is a feedback loop with the same structure:

| # | Problem | Symptom if wrong | Solution |
|---|---|---|---|
| 1 | **Carrier frequency** | Constellation spins into a ring | Costas loop / FLL |
| 2 | **Carrier phase** | Constellation rotated at a fixed angle | Costas loop |
| 3 | **Symbol timing** | Constellation smeared radially; eye closed | Symbol Sync (M&M, Gardner) |

Get all three and the constellation snaps into tight dots. This chapter is how.

---

## Part 1 — The Universal Feedback Loop

Every synchroniser in this chapter is the same three boxes:

```
             ┌──────────────┐
  input ────▶│   Error      │──── e[n] ───┐
        ┌───▶│  Detector    │             │
        │    └──────────────┘             ▼
        │                          ┌─────────────┐
        │                          │ Loop Filter │
        │                          │ (PI: α, β)  │
        │                          └──────┬──────┘
        │                                 │
        │    ┌──────────────┐              │
        └────┤  Controlled  │◀─────────────┘
             │  Oscillator  │
             │ (NCO / interp)│
             └──────────────┘
```

1. **Error detector** — measures how wrong we currently are. This is the only box that changes
   between applications.
2. **Loop filter** — a proportional-plus-integral (PI) controller. The proportional term
   reacts to phase error; the integral term accumulates and eliminates *frequency* error.
3. **Controlled oscillator** — applies the correction.

$$
\text{PI: } \quad \phi_{\text{acc}}[n+1] = \phi_{\text{acc}}[n] + \beta \, e[n]
$$
$$
\phi[n+1] = \phi[n] + \phi_{\text{acc}}[n+1] + \alpha \, e[n]
$$

### The two gains, from two design parameters

You never choose $\alpha$ and $\beta$ directly. You choose:

- **$\zeta$ — damping factor.** $\zeta = 1/\sqrt{2} \approx 0.707$ is critically damped and
  almost always right. Below 0.5 the loop rings; above 2 it crawls.
- **$B_n$ — loop bandwidth**, normalised to the sample rate (so a dimensionless number like
  0.01).

Then, with $\theta = \frac{B_n}{\zeta + 1/(4\zeta)}$ and $\Delta = 1 + 2\zeta\theta + \theta^2$:

$$
\alpha = \frac{4\zeta\theta}{\Delta}, \qquad \beta = \frac{4\theta^2}{\Delta}
$$

This is precisely what GNU Radio's `control_loop::set_loop_bandwidth()` computes. Every loop
block in GNU Radio — Costas, Symbol Sync, PLL, FLL — inherits it.

```bash
python3 -c "
import math
def gains(bw, zeta=0.707):
    t = bw/(zeta + 1/(4*zeta)); d = 1 + 2*zeta*t + t*t
    return 4*zeta*t/d, 4*t*t/d
for bw in (0.001, 0.01, 0.045, 0.1):
    a,b = gains(bw); print(f'Bn={bw:<6} alpha={a:.6f}  beta={b:.8f}')
"
```

### The one trade-off that governs all of them

$$
\boxed{\text{wide loop} \Rightarrow \text{fast lock, noisy tracking}}
$$
$$
\boxed{\text{narrow loop} \Rightarrow \text{slow lock, clean tracking, may never acquire}}
$$

The loop's own output noise (jitter) is proportional to $B_n / \text{SNR}$, while its ability
to acquire a frequency offset $\Delta f$ requires roughly $B_n > \Delta f / f_s$. Those two
requirements pull in opposite directions, and choosing between them **is** loop design.

| Application | Typical $B_n$ | Why |
|---|---|---|
| FM stereo pilot (Lab 04) | 0.001 | Pilot is rock-steady; want minimum jitter |
| RDS carrier (Lab 07) | 0.005 | Weak subcarrier, still steady |
| Costas on a clean link (Lab 08) | 0.02–0.06 | Must chase real oscillator drift |
| Symbol timing (Lab 08) | 0.045 | Clock offsets are larger than you expect |

**Practical acquisition strategy:** start wide to acquire, then narrow to track. Some GNU
Radio blocks let you retune `loop_bw` at runtime — Lab 08 puts it on a slider so you can watch
the constellation tighten and loosen in real time.

---

## Part 2 — The Classical PLL

The error detector is simply the phase difference between input and NCO:

$$
e[n] = \arg\bigl(x[n]\bigr) - \phi_{\text{NCO}}[n]
$$

or, avoiding the `arg` computation, $e[n] = \Im\{x[n] \cdot e^{-j\phi_{\text{NCO}}[n]}\}$,
which for small errors $\approx |x| \sin(\Delta\phi) \approx |x|\Delta\phi$.

### GNU Radio's three PLL blocks

| Block | Output | Use |
|---|---|---|
| `analog_pll_refout_cc` | Clean complex sinusoid at the locked frequency | **Regenerate a carrier** — Lab 04's pilot |
| `analog_pll_carriertracking_cc` | The input, phase-corrected | Coherent AM / DSB demodulation |
| `analog_pll_freqdet_cf` | The instantaneous frequency | An alternative FM demodulator |

Parameters: `w` = loop bandwidth (normalised), `max_freq` / `min_freq` = the search range in
radians/sample.

$$
\omega_{\text{rad/sample}} = \frac{2\pi f_{\text{Hz}}}{f_s}
$$

> **Worked example — Lab 04's pilot PLL.** We want to lock 19 kHz at $f_s = 240$ kHz, allowing
> ±100 Hz of drift:
> $$\omega_{\text{center}} = \frac{2\pi \times 19000}{240000} = 0.4974 \text{ rad/sample}$$
> $$\omega_{\pm} = \frac{2\pi \times 100}{240000} = 0.0026$$
> so `max_freq = 0.5000`, `min_freq = 0.4948`. **A tight search range is the single most
> effective cure for a PLL that locks to the wrong thing.**

### Lock detection

A PLL that has lost lock produces confident garbage. Detect it: correlate the input with the
NCO output over a window and threshold the magnitude. If the pilot vanishes (mono station),
lock is lost — and a good receiver mutes the stereo path rather than emitting noise.

---

## Part 3 — Costas Loop: Carrier Recovery Without a Carrier

BPSK and QPSK are suppressed-carrier: there is nothing for a plain PLL to lock to, because the
data flips the phase by 180° constantly. The **Costas loop** removes the data first.

### BPSK Costas (order 2)

$$
e[n] = \Re\{y[n]\} \cdot \Im\{y[n]\}
$$

where $y[n]$ is the phase-corrected sample. Why this works: write $y = A e^{j(\pm\pi \cdot b + \Delta\phi)}$.

- $\Re\{y\}\Im\{y\} = \frac{A^2}{2}\sin(2(\pm\pi b + \Delta\phi)) = \frac{A^2}{2}\sin(2\Delta\phi)$

The data term $\pm\pi b$ enters doubled, i.e. as $\pm 2\pi$ — which is **invisible**. The data
cancels itself out and only the phase error remains.

### QPSK Costas (order 4)

$$
e[n] = \operatorname{sgn}(\Re\{y\})\cdot\Im\{y\} - \operatorname{sgn}(\Im\{y\})\cdot\Re\{y\}
$$

The hard decisions strip the QPSK modulation the same way.

### The price: phase ambiguity

Order 2 has a **180° ambiguity**; order 4 has a **90° ambiguity**. The loop is equally stable
at each. This is not a bug you can fix in the loop — it is a consequence of the modulation
being symmetric. The two cures:

1. **Differential encoding** (Fundamentals 08) — ambiguity cancels, costs 3 dB.
2. **A known sync word** — correlate, and rotate the constellation to whichever of the $M$
   hypotheses makes the sync word appear.

ADS-B uses a preamble (option 2). RDS uses differential encoding (option 1). Lab 08 lets you
try both.

### GNU Radio's Costas Loop block

```
digital_costas_loop_cc:
  w     = loop bandwidth (normalised, e.g. 0.045)
  order = 2 (BPSK) | 4 (QPSK) | 8 (8PSK)
```

Optional outputs `frequency`, `phase`, `error` are wonderful debugging tools — wire
`frequency` to a QT GUI Time Sink and you can *watch* the loop acquire.

---

## Part 4 — Symbol Timing Recovery

The transmitter's clock and the receiver's clock are never identical. Two errors result:

- **Timing offset** $\tau$ — we are sampling at the wrong point within each symbol.
- **Clock frequency offset** $\epsilon$ — the sampling instant slowly slides, so even a
  perfect initial $\tau$ decays.

Both are fatal: sampling away from the peak of the pulse both reduces amplitude and picks up
ISI from neighbouring symbols.

### The eye diagram

Overlay the waveform on a 2-symbol window. The eye's **widest opening** is the correct
sampling instant.

```
   good timing, high SNR         bad timing / low SNR
   ╲                    ╱         ╲   ╱╲   ╱
    ╲                  ╱           ╲ ╱  ╲ ╱
     ╲________________╱             X    X
     ╱                ╲            ╱ ╲  ╱ ╲
    ╱                  ╲          ╱   ╲╱   ╲
   ╱      ← open →      ╲            closed
```

GNU Radio has a **QT GUI Eye Sink** — use it. Lab 08 includes one.

### Timing error detectors

| TED | Needs carrier lock? | Samples/symbol | Notes |
|---|---|---|---|
| **Mueller & Müller** | Yes | 1 (decision-directed) | Very efficient; the default |
| **Gardner** | **No** | 2 | Works before carrier recovery — very useful |
| Zero crossing | Yes | 2 | Simple, needs transitions |
| Early-late | Yes | ≥ 2 | Intuitive, more computation |

**Mueller & Müller:**

$$
e[n] = \Re\{\hat{a}[n-1]^* \, y[n] - \hat{a}[n]^* \, y[n-1]\}
$$

**Gardner** (the one to reach for when things will not lock):

$$
e[n] = \Re\bigl\{\bigl(y[n] - y[n-1]\bigr)^* \, y[n - \tfrac{1}{2}]\bigr\}
$$

Gardner uses the *midpoint* sample and is completely independent of carrier phase — so you can
recover timing first, then carrier. That ordering is usually the easier one to debug.

### GNU Radio's Symbol Sync block

```
digital_symbol_sync_xx:
  ted_type    = digital.TED_MUELLER_AND_MULLER  (or TED_GARDNER)
  sps         = input samples per symbol (e.g. 4)
  loop_bw     = 0.045
  damping     = 1.0
  max_dev     = 1.5     ← clamp on the timing correction
  osps        = 1       ← output samples per symbol
  resamp_type = digital.IR_PFB_MF   ← polyphase matched filter (best)
  pfb_mf_taps = your RRC taps
```

Using `IR_PFB_MF` with your RRC taps folds the matched filter **into** the interpolator, so
one block does matched filtering and timing recovery together. That is both faster and more
accurate than doing them separately.

---

## Part 5 — Putting It in the Right Order

The canonical receiver chain, and the order matters:

```
IQ in
  │
  ▼
[ AGC ]              normalise amplitude — loops assume unit-ish scale
  │
  ▼
[ Coarse freq correction / FLL ]   pull |Δf| below the Costas capture range
  │
  ▼
[ Symbol Sync + matched filter ]   Gardner TED works without carrier lock
  │
  ▼
[ Costas Loop ]                    now fine phase & frequency, 1 sample/symbol
  │
  ▼
[ Slicer / Constellation Decoder ]
  │
  ▼
[ Differential decode ] → bits
```

### Debugging by looking at the constellation

This table will save you hours:

| What you see | Diagnosis | Fix |
|---|---|---|
| Solid ring | Frequency offset, Costas not locked | Widen `w`; add FLL; check `sps` |
| Rotated but tight dots | Static phase offset | Normal — differential decode or sync word |
| Radial smear (dots into lines) | Timing error | Check `sps`, widen Symbol Sync `loop_bw` |
| Fuzzy blob | Low SNR | More gain / better antenna / narrower filter |
| Dots at the right places, occasional jumps | Cycle slips — loop too wide | Narrow `w` |
| Two dots when you expect four | Wrong Costas `order` | Set `order = 4` for QPSK |
| Everything at the origin | No signal, or squelched | Check upstream |

---

## 🧠 Self-Check

1. What loop bandwidth would you choose to track a very stable 19 kHz pilot, and why?
   **Answer:** Very narrow, ~0.001. The pilot does not move, so minimise jitter; acquisition
   speed is irrelevant for a continuous broadcast.

2. Why can a plain PLL not lock to a BPSK signal?
   **Answer:** The data flips the carrier phase by 180° at the symbol rate, so the average
   phase carries no information. A Costas loop removes the modulation first.

3. Your QPSK constellation is a rotating ring. Two possible causes?
   **Answer:** (a) Costas loop bandwidth too narrow to capture the frequency offset;
   (b) `order` set to 2 instead of 4, so the error detector is wrong.

4. Why does Gardner's TED not need carrier lock?
   **Answer:** It compares energy at the midpoint versus the transition, which is a magnitude
   relationship independent of the constellation's absolute phase.

5. What does a 90° phase ambiguity mean practically?
   **Answer:** Your decoded bits may be one of four rotations of the truth. Resolve with
   differential encoding or a known sync word.

6. Loop bandwidth 0.001 with $\zeta = 0.707$ — what are $\alpha$ and $\beta$?
   **Answer:** $\theta = 0.001/(0.707+0.3536) = 9.43\times10^{-4}$, giving
   $\alpha \approx 2.66\times10^{-3}$, $\beta \approx 3.55\times10^{-6}$.

---

**Next:** [Fundamentals 10 — Error Detection & Framing →](./10_error_detection_and_framing.md)
