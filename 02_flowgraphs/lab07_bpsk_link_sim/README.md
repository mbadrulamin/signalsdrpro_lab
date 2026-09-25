# 💠 Lab 07 — A Digital Link, Simulated (BPSK)

> **What you will build:** a complete digital radio link — transmitter, channel and receiver —
> entirely in software, plus a meter that counts the **bit errors**.
> **What you will learn:** how bits become a radio signal and back again, the three things a
> digital receiver must work out, what **loop bandwidth** does, and how to compare a measured
> **bit error rate (BER)** with theory.
> **Before this:** [Fundamentals 08 — Digital Modulation](../../01_fundamentals/08_digital_modulation.md)
> and [09 — Synchronisation](../../01_fundamentals/09_synchronization.md).
> **Time:** about 2 hours. **Difficulty:** advanced. **Needs the radio:** **no** — this lab runs
> on any computer.

---

## 🎯 Goal

Build a digital link, measure how many bits it gets wrong, and check that number against the
theory from Fundamentals 08.

Why simulate? Because here **you** control the noise, the frequency error and the clock error
exactly. If your measured error rate matches the theory, your receiver is not just "working" —
it is working **as well as possible**. That gives you a reference for every real receiver later.

> ✅ **Tested:** at the default setting (Eb/N0 = 8 dB), this flowgraph measured a BER of
> **3.89 × 10⁻⁴**. Theory says **3.82 × 10⁻⁴**. See [Verification](#-verification).

---

## 1. Background: what a digital link does

```
  bits ──▶ map to ──▶ shape the ──▶ CHANNEL ──▶ find timing ──▶ decide ──▶ bits
           symbols    pulses        (noise,     and carrier     0 or 1
                                     errors)    ▲
                                                the hard part
```

Some words first:

- **Bit** — a 0 or a 1.
- **Symbol** — one "mark" the transmitter sends. In **BPSK** (binary phase-shift keying) there
  are two symbols: **+1** for a 1 and **−1** for a 0. Each symbol carries one bit.
- **Pulse shaping** — smoothing each symbol so the signal uses less bandwidth.
- **BER** (bit error rate) — the fraction of bits received wrongly. BER = 10⁻³ means 1 wrong
  bit in every 1000.
- **Eb/N0** — the energy per bit compared with the noise level, in dB. It is the fair way to
  say "how strong is the signal" for digital links. Higher Eb/N0 → fewer errors.

The transmitter is easy: a lookup table and a filter. The channel just adds problems. **The
receiver must work out three unknown things at the same time:**

| Unknown | Why it happens | Which block solves it |
|---|---|---|
| **When** does each symbol start? | The transmitter's and receiver's clocks run at slightly different speeds | **Symbol Sync** |
| **What frequency error** is there? | The two radios' tuning is never exactly equal | **Costas Loop** |
| **What phase** is the signal at? | The signal's travel time | **Costas Loop** |

And it must do this while noise tries to spoil every measurement. That is why **loop
bandwidth** — how quickly these blocks react — is the key setting, and why it is on a slider.

---

## 2. Run it first

```bash
cd "02_flowgraphs/lab07_bpsk_link_sim"
gnuradio-companion lab07_bpsk_link_sim.grc      # with the displays
# or, without GRC:
python3 -u lab07_bpsk_link_sim.py
```

Watch the **terminal**. After a few seconds you should see:

```
[BER Monitor] locked to the pattern at shift 770; stream inverted: no
[BER Monitor] bits=   200,011  errors=      76  BER=3.800e-04
[BER Monitor] bits=   400,712  errors=     152  BER=3.793e-04
...
[BER Monitor] bits= 3,815,700  errors=   1,486  BER=3.894e-04
```

**The printed BER is the real result.** The shift number will be different each run.

---

## 3. The flowgraph

```
 TRANSMITTER
 Vector Source ─▶ Throttle ─▶ Differential ─▶ Chunks to ─▶ Interpolating FIR
 1023 known bits  100 kbit/s   Encoder         Symbols      (RRC pulse shape, ×4)
                                               0→−1, 1→+1          │ 400 kSPS
 CHANNEL                                                           ▼
 Channel Model: add noise + a frequency error + a clock-speed error
                                                                   │
                  ┌────────────────────┬───────────────────────────┤
                  ▼                    ▼                           ▼
             Spectrum             Eye diagram                 Symbol Sync
                                                         (finds symbol timing,
 RECEIVER                                                  4 samples → 1)
                                                                   │ 100 kSPS
                                                              Costas Loop ──▶ frequency plot
                                                        (removes frequency and phase error)
                                                         ┌─────────┴─────────┐
                                                         ▼                   ▼
                                                   Constellation      Complex to Real
                                                                             │
                                                                      Binary Slicer (0 or 1)
                                                                             │
                                                                   Differential Decoder
 MEASUREMENT                                                                 │ bits
                                                     BER Monitor (Embedded Python Block)
                                                     compares with the known bits, counts errors
                                                             │                  │
                                                        Number display     BER over time
```

### Rates

| Between | Rate | Type | Note |
|---|---|---|---|
| Vector Source → Throttle | 100 kbit/s | byte | one bit per byte |
| Chunks to Symbols → pulse filter | 100 k symbols/s | complex | ±1 |
| pulse filter → Channel | 400 kSPS | complex | 4 samples per symbol (`sps = 4`) |
| Symbol Sync → Costas | 100 kSPS | complex | 1 sample per symbol |
| Differential Decoder → BER Monitor | 100 kbit/s | byte | the received bits |

The signal is **135 kHz** wide: symbol rate × (1 + roll-off) = 100 k × 1.35. You can check
this on the spectrum display.

---

## 4. The blocks

### Transmitter

**Vector Source — the known bits.** 1023 random-looking bits, the same every time:

```python
pattern = [int(b) for b in np.random.RandomState(1).randint(0, 2, 1023)]
```

The BER Monitor has the same list, so it can compare. The bits must look random: a simple
repeating 0101 pattern would let the timing loop lock in the wrong place and would not test the
receiver properly.

**Throttle.** No hardware, so something must set the speed (see Lab 05).

**Differential Encoder.** Instead of sending each bit directly, it sends "did the bit change?":

$$
d[n] = d[n-1] \oplus b[n] \qquad (\oplus = \text{XOR})
$$

**Why?** The Costas loop in the receiver cannot tell +1 from −1 on its own. Half the time it
locks "upside down" (180° wrong), and every bit comes out inverted. With differential encoding,
only *changes* matter, and an upside-down signal has the same changes. The cost: one wrong
symbol spoils two bits, so the BER roughly **doubles** (exactly $2p(1-p)$ instead of $p$).

**Chunks to Symbols.** Turns each bit into a symbol: 0 → −1, 1 → +1.

**Interpolating FIR Filter — pulse shaping.** Makes 4 samples per symbol, and shapes each pulse
with a **root-raised-cosine (RRC)** filter so the signal stays inside 135 kHz:

```python
rrc_tx_taps = firdes.root_raised_cosine(sps, sps, 1.0, excess_bw, 11*sps)
#                                        gain  rate  sym_rate  roll-off  taps
```

The gain of `sps` makes the transmitted signal have an **average power of exactly 1**, which the
Eb/N0 formula below assumes.

<details>
<summary><b>Check it:</b> measure the transmitted power</summary>

```bash
python3 -c "
from gnuradio import gr, blocks, digital, filter as f
from gnuradio.filter import firdes
import numpy as np
sps = 4
tb = gr.top_block()
bits = np.random.RandomState(3).randint(0,2,20000).astype(np.uint8)
vs  = blocks.vector_source_b(bits.tolist(), False)
c2s = digital.chunks_to_symbols_bc([-1+0j, 1+0j], 1)
rf  = f.interp_fir_filter_ccf(sps, firdes.root_raised_cosine(sps, sps, 1.0, 0.35, 11*sps))
vk  = blocks.vector_sink_c()
tb.connect(vs, c2s, rf, vk); tb.run()
y = np.array(vk.data())[200:-200]
print('TX mean power = %.4f  (want 1.0)' % np.mean(np.abs(y)**2))"
```
</details>

### Channel

**Channel Model** adds the real-world problems:

| Setting | Value | Imitates |
|---|---|---|
| `noise_voltage` | `noise_volt` (from Eb/N0) | Background noise |
| `freq_offset` | slider, default 0.0005 cycles/sample | The two radios tuned slightly differently |
| `epsilon` | slider, default 1.00005 | The two clocks differ by 50 parts per million |
| `taps` | `[1.0+0j]` | A clean path, no echoes |

**Setting the noise from Eb/N0.** The flowgraph calculates the noise level from the Eb/N0
slider:

$$
\text{noise\_volt} = \sqrt{\frac{\text{sps}}{k \cdot 10^{(E_b/N_0)/10}}}, \qquad k = 1 \text{ bit per symbol}
$$

> ⚠️ Get this formula wrong by a factor of 2, and the whole BER curve moves by 3 dB. That looks
> exactly like a broken receiver, and you will waste hours looking for a bug that is not there.
> [Fundamentals 08](../../01_fundamentals/08_digital_modulation.md) checks the formula.

> 💡 The Channel Model's clock-error feature adds a tiny delay of its own. Symbol Sync handles
> it, just as it would in real life. For a *perfect* test with no sync at all, the script
> `03_scripts/simulate_bpsk_ber.py` uses a plain Noise Source and Add block instead.

### Receiver

**Symbol Sync — finding the timing.**

| Setting | Value | Meaning |
|---|---|---|
| TED type | Gardner | The method used to measure timing error |
| Samples per symbol | 4 in, 1 out | Picks the best sample from each symbol |
| Loop bandwidth | `loop_bw` slider (0.010) | How quickly it reacts |
| Resampler | polyphase matched filter, 32 arms | Also does the receiver's matching RRC filter |

Why **Gardner**? It can find the timing **before** the frequency and phase are fixed. So timing
is solved first, then carrier. That order is much easier to debug.

The matched filter's taps must be made **32 times finer** than normal, because they are split
into 32 "arms" (one for each fine timing step):

```python
pfb_mf_taps = firdes.root_raised_cosine(nfilts, nfilts*sps, 1.0, excess_bw, 11*sps*nfilts)
```

> 🐛 **The first error almost everyone hits:** using normal RRC taps here gives
> `length of the prototype filter taps must be greater than or equal to the number of polyphase
> filter arms`. Use the line above.

**Costas Loop — fixing frequency and phase.** `order = 2` for BPSK. It spins the constellation
until the two points sit on the horizontal axis at ±1.

Its second output is the **frequency it has measured**. It is connected to a plot — the best
debugging tool in this flowgraph, because you can **watch it lock**. It should settle at:

$$
2\pi \times \text{freq\_offset} \times \text{sps} = 2\pi \times 0.0005 \times 4 = 0.0126 \text{ rad/sample}
$$

(×4 because the loop runs at the symbol rate, after the 4× reduction.)

**Complex to Real → Binary Slicer → Differential Decoder.** Take the real part, decide 0 or 1
(below or above zero), and undo the differential encoding.

### Measurement — the BER Monitor

An **Embedded Python Block**: Python code stored inside the `.grc` file. In GRC, open it with
right-click → Properties to read the code. It does three things:

1. **Waits** for 100,000 bits while the loops lock.
2. **Lines up** the received bits with the known 1023-bit pattern. It tries every possible
   starting point and picks the best match. If the best match is *negative*, the stream is
   upside down (the 180° problem), and it notes that. It prints one line when it locks.
3. **Counts** wrong bits from then on, and prints the running BER every 200,000 bits.

---

## 5. Exercises

### Exercise 1 — A healthy link

Defaults: Eb/N0 = 8 dB, loop bandwidth 0.010, frequency offset 0.0005, clock ratio 1.00005.

| Display | What healthy looks like | What it tells you |
|---|---|---|
| Channel Spectrum | a smooth hump 135 kHz wide | the pulse shaping works |
| Eye Diagram | a wide-open "eye" | the timing can be found |
| Constellation | two tight dots at −1 and +1 | both loops are locked |
| Costas frequency | a flat line at about 0.0126 | the frequency error is found |
| BER | settling near 4 × 10⁻⁴ | ✅ |

Give it **at least 30 seconds**. Rare events take time to count. To measure a BER of 10⁻⁵ to
±10 %, you need about 10 million bits: 100 seconds at 100 kbit/s.

### Exercise 2 — Build the BER curve

Keep loop bandwidth at 0.010. For each Eb/N0, restart, wait 60 s, and write down the BER:

| Eb/N0 | Theory (differential BPSK) | Your result |
|---|---|---|
| 2 dB | 7.22 × 10⁻² | |
| 4 dB | 2.47 × 10⁻² | |
| 6 dB | 4.77 × 10⁻³ | |
| 8 dB | 3.82 × 10⁻⁴ | |
| 10 dB | 7.74 × 10⁻⁶ | |

The theory numbers come from $P_b = 2p(1-p)$ with $p = Q(\sqrt{2E_b/N_0})$:

```bash
python3 -c "
from math import erfc, sqrt
for e in (2,4,6,8,10):
    p = 0.5*erfc(sqrt(10**(e/10)))
    print(f'{e:>3} dB   BPSK {p:.3e}   DBPSK {2*p*(1-p):.3e}')"
```

Notice the **cliff**: going from 2 dB to 10 dB (8 dB more signal) cuts the errors by about
**10,000 times**. Digital links do not fade gently. They work, and then suddenly they don't.

### Exercise 3 — Loop bandwidth (the most important one)

Set Eb/N0 to **2 dB** (very noisy) and try three loop bandwidths. Measured results:

| Loop bandwidth | Measured BER | Theory | Result |
|---|---|---|---|
| 0.045 | 4.8 × 10⁻¹ | 7.2 × 10⁻² | ❌ the loops lost lock; the output is random |
| 0.010 | 7.5 × 10⁻² | 7.2 × 10⁻² | ✅ as good as possible |
| 0.005 | 7.4 × 10⁻² | 7.2 × 10⁻² | ✅ as good as possible, but slower to lock |

**A setting that is fine at 8 dB destroys the link at 2 dB.** A fast (wide) loop reacts to the
noise itself, and wanders off.

Now the opposite: Eb/N0 **12 dB**, loop bandwidth **0.001**. Watch the Costas frequency plot:
it takes **seconds** to crawl to the right value. Narrow loops ignore noise well, but lock
slowly.

> **Rule:** there is no single best loop bandwidth. Wide = locks fast, but noisy. Narrow =
> smooth, but locks slowly. Choose for the SNR you expect.

### Exercise 4 — See the 180° problem

The Costas loop cannot tell +1 from −1 by itself. If the signal arrives with an extra half-turn
of phase (as a different path length can cause), it locks "upside down". Let's cause that on
purpose.

**Step 1.** First, **bypass** both `diff_enc` and `diff_dec` (right-click → Bypass, both
together). Run it. The BER **halves** — about 1.8 × 10⁻⁴ at 8 dB, which is plain BPSK. That is
the price differential encoding normally costs.

**Step 2.** Keep them bypassed. Open the **Channel Model** and set **Taps** to `[-1.0+0j]`.
Multiplying by −1 is a 180° phase shift. Run it. The first terminal line now says:

```
[BER Monitor] locked to the pattern at shift 770; stream inverted: YES (180-degree ambiguity)
```

Every bit is coming out inverted. The monitor can correct this only because it knows the
pattern. **A real receiver does not know the data**, so it would give you every bit wrong.

**Step 3.** Now **un-bypass** the two differential blocks (keep the taps at −1). Run again:

```
[BER Monitor] locked to the pattern at shift 770; stream inverted: no
```

With differential encoding, only the *changes* between bits carry information — and an
upside-down signal has exactly the same changes. The problem disappears. The cost is the
doubled BER from Step 1 (measured 4.1 × 10⁻⁴ here).

Measured results, 8 dB:

| Differential blocks | Channel taps | Monitor says | BER |
|---|---|---|---|
| on | `[1.0]` | inverted: no | 3.9 × 10⁻⁴ |
| bypassed | `[1.0]` | inverted: no | 1.8 × 10⁻⁴ |
| bypassed | `[-1.0]` | **inverted: YES** | 1.9 × 10⁻⁴ (only because the monitor fixes it) |
| on | `[-1.0]` | inverted: no | 4.1 × 10⁻⁴ |

> 💡 The simulation is repeatable: the same settings give the same result every run. That is
> why you have to *cause* the 180° problem with the taps; on a real radio, the phase is random
> and it happens by itself.

### Exercise 5 — Break it on purpose

| Change | What you see | Why |
|---|---|---|
| `freq_offset` → 0.008 | The constellation becomes a **ring** | The frequency error is too big for the Costas loop to catch |
| `timing_offset` → 1.0005 (500 ppm) | The dots smear **along the line** | The timing loop cannot keep up with the clock drift |
| Costas `order` → 4 | BER ≈ 0.5 | That order is for QPSK, not BPSK |
| Eb/N0 → 0 dB | The eye closes; the constellation is a cloud | Noise wins |

You will meet every one of these in real receivers. It is much cheaper to meet them here, where
you know the right answer.

---

## 🔬 Verification

The flowgraph was run without a screen, and its BER compared with theory:

```
$ python3 -u lab07_bpsk_link_sim.py          # Eb/N0 = 8 dB
[BER Monitor] locked to the pattern at shift 770; stream inverted: no
...
[BER Monitor] bits= 3,815,700  errors=   1,486  BER=3.894e-04
```

Theory for differential BPSK at 8 dB: $p = 1.909 \times 10^{-4}$, so
$2p(1-p) = \mathbf{3.82 \times 10^{-4}}$. Measured **3.89 × 10⁻⁴**: within 2 %, which is inside
the counting uncertainty for about 1500 errors.

The script `03_scripts/simulate_bpsk_ber.py` runs a sweep automatically:

```
  Eb/N0   noise_v     measured    BPSK theory    ratio
    2.0    1.5887    3.790e-02      3.751e-02     1.01
    4.0    1.2619    1.276e-02      1.250e-02     1.02
    6.0    1.0024    2.513e-03      2.388e-03     1.05
RESULT: measurement tracks theory.
```

---

## 🔧 Troubleshooting

| Problem | Cause and fix |
|---|---|
| `length of the prototype filter taps must be >= number of polyphase filter arms` | `pfb_mf_taps` made at the wrong resolution. Use the formula in Section 4 |
| BER stays at exactly 0.5 | The monitor never locked. First check the constellation: are the loops locked? Also check the monitor's `pattern` matches the Vector Source's |
| The constellation is a ring | No carrier lock: frequency offset too big, loop too narrow, or wrong Costas order |
| The dots are smeared along the line | A timing problem, not a carrier problem. Check `sps` is 4 in both places; widen Symbol Sync's loop |
| Runs slower than real time, one CPU at 100 % | The 32-arm matched filter is the expensive part. Try `nfilts = 16` |
| BER is always about 2× the BPSK theory | Correct! Differential encoding doubles it. Compare with the DBPSK column |

---

## ✅ Summary

- A digital receiver must find **timing**, **frequency** and **phase**. Symbol Sync and the
  Costas loop do this with feedback loops.
- **Loop bandwidth** is the most important receiver setting, and the right value depends on
  the noise level.
- Find **timing first** (Gardner does not need the carrier), then the carrier.
- **Differential encoding** doubles the BER but removes the 180° problem.
- **Check your noise formula** before trusting a BER. A factor of 2 is a 3 dB error.
- You cannot measure a BER faster than errors happen. Plan how many bits you need.

## 🧠 Check yourself

1. Why do we use Eb/N0 instead of SNR?
   <details><summary>Answer</summary>SNR depends on the bandwidth you measure it in. Eb/N0
   measures energy per bit, so it compares different modulations and bit rates fairly.</details>
2. The Costas loop locks 180° wrong. What happens without differential encoding? And with it?
   <details><summary>Answer</summary>Without it, every bit comes out inverted, and a real
   receiver cannot notice. With it, nothing goes wrong, because only the changes between bits
   matter.</details>
3. At 2 dB, why does a loop bandwidth of 0.045 fail?
   <details><summary>Answer</summary>A wide loop reacts quickly — including to noise. At
   2 dB the noise pushes it around so much that it loses lock.</details>
4. You measured 0 errors in 4 million bits. What is the BER?
   <details><summary>Answer</summary>You can only say it is probably below about
   1 in 4 million (2.5 × 10⁻⁷). You need about 100 errors for a ±10 % measurement.</details>
5. You change the constellation to QPSK (4 points, 2 bits per symbol). What happens to the
   BER-vs-Eb/N0 curve?
   <details><summary>Answer</summary>It stays the same — but you send twice as many bits in
   the same bandwidth. (You would need Costas order 4, a Constellation Decoder, k = 2 and a
   modulus-4 differential decoder.)</details>

**Next:** [Lab 08 — Read a Station's Name (RDS) →](../lab08_rds_decoder/README.md). Lab 08 uses
what you learned here on a **real** signal: the RDS data hidden at 57 kHz inside FM broadcasts —
differential BPSK at 1187.5 bits per second.

---

## 📖 References

1. GNU Radio Wiki: [Symbol Sync](https://wiki.gnuradio.org/index.php/Symbol_Sync) ·
   [Costas Loop](https://wiki.gnuradio.org/index.php/Costas_Loop) ·
   [Channel Model](https://wiki.gnuradio.org/index.php/Channel_Model) ·
   [Embedded Python Block](https://wiki.gnuradio.org/index.php/Embedded_Python_Block)
2. M. Rice, *Digital Communications: A Discrete-Time Approach* — the standard book on timing
   recovery
3. F. M. Gardner, "A BPSK/QPSK Timing-Error Detector for Sampled Receivers", IEEE Trans.
   Communications, 1986
