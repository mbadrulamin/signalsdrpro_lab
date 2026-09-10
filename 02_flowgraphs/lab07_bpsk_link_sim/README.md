# 💠 Lab 07 — BPSK Link Simulation with Live BER Measurement

> **Time:** 2 hours
> **Difficulty:** Advanced
> **Hardware:** **None.** This lab runs on any machine.
> **Theory needed:** [Fund. 08 Digital Modulation](../../01_fundamentals/08_digital_modulation.md) · [Fund. 09 Synchronization](../../01_fundamentals/09_synchronization.md)
> **New blocks:** Vector Source, Differential Encoder/Decoder, Chunks to Symbols, Interpolating FIR, Channel Model, Symbol Sync, Costas Loop, Binary Slicer, Embedded Python Block, Constellation Sink, Eye Sink
> **Blocks in flowgraph:** 34

---

## 🎯 Goal

Build a **complete digital communication link** — transmitter, channel, receiver — and then
**measure** its bit error rate and compare that measurement against the closed-form theory
from Fundamentals 08.

This is the first lab with no radio in it, and that is the point. When you can control the
noise, the frequency offset and the clock error *exactly*, you can verify that your receiver
is not merely working but working **optimally**. Once you have seen the measured curve land on
the theoretical one, you have a reference: any real-world receiver that falls short of it has
a bug you can go and find.

> **This lab has been run and verified.** At Eb/N0 = 8 dB the flowgraph converges to a measured
> BER of **3.9 × 10⁻⁴**; differentially-encoded BPSK theory predicts **3.82 × 10⁻⁴**. See
> [Verification](#-verification) below for the full table.

---

## 📖 Background: What a Digital Link Actually Is

```
    bits          symbols        waveform         waveform        symbols        bits
  ────────▶  map  ────────▶ shape ────────▶ CHANNEL ────────▶ sync ────────▶ slice ────────▶
             ▲                                                  ▲
        constellation                                    the hard part
```

Everything interesting happens in the "sync" box. The transmitter is a lookup table and a
filter. The channel is addition. **The receiver has to undo three unknowns simultaneously:**

| Unknown | Caused by | Undone by |
|---|---|---|
| Where does each symbol start? | Independent TX and RX clocks | Symbol Sync (Gardner TED) |
| What is the carrier frequency error? | LO mismatch, Doppler | Costas Loop |
| What is the carrier phase? | Propagation delay | Costas Loop |

And it must do this **while the noise is trying to make every measurement wrong**. That is why
loop bandwidth is the central design parameter, and why this lab puts it on a slider.

---

## 📐 Architecture

```
 TRANSMITTER
 ┌───────────────┐  bits   ┌──────────┐  ┌──────────────┐  ┌────────────────┐  ┌───────────┐
 │ Vector Source │────────▶│ Throttle │─▶│ Differential │─▶│ Chunks to      │─▶│ Interp    │
 │ 1023-bit PN   │ 100 kb/s│ sym_rate │  │ Encoder      │  │ Symbols        │  │ FIR (RRC) │
 └───────────────┘         └──────────┘  └──────────────┘  │ 0→−1  1→+1     │  │ interp=4  │
                                                            └────────────────┘  └─────┬─────┘
                                                                                      │ 400 kSPS
 CHANNEL                                                                              ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │ Channel Model:  AWGN (noise_volt)  +  freq offset  +  clock ratio epsilon               │
 └───────────────────────────────┬────────────────────────────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
      Freq Sink            Eye Sink        ┌──────────────────┐
      (spectrum)           (timing)        │ Symbol Sync      │ Gardner TED
                                           │ + PFB matched    │ sps 4 → 1
                                           │   filter         │
                                           └────────┬─────────┘
 RECEIVER                                           │ 100 kSPS, 1 sample/symbol
                                           ┌────────▼─────────┐
                                           │ Costas Loop      │──── freq ──▶ Time Sink
                                           │ order 2          │
                                           └────────┬─────────┘
                                    ┌───────────────┼───────────────┐
                                    ▼               ▼               │
                            Constellation    ┌─────────────┐        │
                                Sink         │ Complex→Real│◀───────┘
                                             └──────┬──────┘
                                             ┌──────▼──────┐  ┌──────────────┐
                                             │ Binary      │─▶│ Differential │
                                             │ Slicer      │  │ Decoder      │
                                             └─────────────┘  └──────┬───────┘
 MEASUREMENT                                                          │ bits
                                           ┌──────────────────────────▼─────────────────┐
                                           │ BER Monitor (Embedded Python Block)        │
                                           │  locks to the known pattern, counts errors │
                                           └──────────┬─────────────────┬───────────────┘
                                                      ▼                 ▼
                                                Number Sink        Time Sink
```

### Rate table

| Wire | Rate | Type | Note |
|---|---|---|---|
| Vector Source → Throttle | 100 kbit/s | byte | one bit per byte |
| Chunks to Symbols → RRC | 100 kbaud | complex | unit-energy BPSK symbols |
| RRC → Channel | 400 kSPS | complex | `sps = 4` |
| Symbol Sync → Costas | 100 kSPS | complex | `osps = 1`, one sample per symbol |
| Diff Decoder → BER | 100 kbit/s | byte | decoded bits |

Occupied bandwidth: $R_s(1+\alpha) = 100\text{k} \times 1.35 = 135$ kHz. You can read that
straight off the Frequency Sink.

---

## 📋 Block-by-Block

### Transmitter

#### `pattern` — the reference bit sequence

```python
pattern = [int(b) for b in np.random.RandomState(1).randint(0, 2, 1023)]
```

A **fixed, reproducible** 1023-bit pseudo-random sequence. It must be known to the receiver's
BER monitor (that is how errors get counted) and it must be pseudo-random (a repeating `0101`
would let the timing loop lock to the wrong phase, and would not exercise the differential
encoder). `RandomState(1)` guarantees you and everyone else get the same sequence.

#### `throttle` — Throttle
No hardware, so something must set the pace. See Lab 05: **exactly one rate limiter per
flowgraph.**

#### `diff_enc` — Differential Encoder

$$
d[n] = d[n-1] \oplus b[n]
$$

This exists solely to survive the Costas loop's 180° phase ambiguity (Fundamentals 09). It
costs about 3 dB — errors come in pairs, so the BER becomes $2p(1-p)$ instead of $p$.

> 🧪 **Try it:** right-click `diff_enc` and `diff_dec` → **Bypass** (both, together). Run.
> Roughly half the time the BER monitor will read ~0.5 because the Costas loop locked 180° out
> and every bit is inverted; the other half it reads the *lower*, non-differential BER. Restart
> a few times and watch it flip. That is the ambiguity, live.

#### `chunks_to_syms` — Chunks to Symbols
`symbol_table = [-1+0j, 1+0j]`. The simplest constellation there is: two points, maximally
separated, unit energy.

#### `rrc_tx` — Interpolating FIR Filter (`ccf`)

```python
rrc_tx_taps = firdes.root_raised_cosine(sps, sps, 1.0, excess_bw, 11*sps)
#                                        │    │    │      │          │
#                                      gain  fs  sym_rate roll-off  ntaps
```

`gain = sps` and `samp_rate = sps, sym_rate = 1.0` is the normalisation that makes the
transmitted signal have **unit average power**, which is what the Eb/N0 formula assumes. Check
it:

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

Doing interpolation **inside** the filter is not a convenience — it is the whole point. A
polyphase interpolating FIR never multiplies the inserted zeros, so shaping by RRC and
upsampling by 4 together cost the same as one filter.

### Channel

#### `channel` — Channel Model

| Parameter | Value | Simulates |
|---|---|---|
| `noise_voltage` | `noise_volt` | AWGN |
| `freq_offset` | slider, cycles/sample | LO error, Doppler |
| `epsilon` | slider, ~1.00005 | TX/RX sample-clock ratio (50 ppm) |
| `taps` | `[1.0+0j]` | flat channel (no multipath) |

**The Eb/N0 calibration.** `noise_volt` is derived, not typed:

$$
A = \sqrt{\frac{\text{sps}}{k \cdot 10^{(E_b/N_0)/10}}}
$$

GNU Radio's `noise_voltage` is the **total** complex standard deviation ($A^2/2$ per component,
verified empirically in [Fundamentals 08](../../01_fundamentals/08_digital_modulation.md)).
There is no extra factor of two. Get this wrong and your whole curve shifts 3 dB — which looks
exactly like a broken receiver, and sends people hunting for bugs that are not there.

> ⚠️ **The Channel Model's `epsilon` resampler adds a small fractional delay of its own.** This
> is realistic (so does a real channel), and Symbol Sync absorbs it. But it means you cannot
> use the Channel Model for a *perfect* open-loop calibration — for that, use a Noise Source
> plus an Add block, as the calibration script in `03_scripts/` does.

### Receiver

#### `sym_sync` — Symbol Sync (`cc`)

```
ted_type    = digital.TED_GARDNER
sps         = 4
loop_bw     = loop_bw          ← the slider
damping     = 1.0
max_dev     = 1.5
osps        = 1
resamp_type = digital.IR_PFB_MF
nfilters    = 32
pfb_mf_taps = pfb_mf_taps
```

Two things happen here, and both matter:

1. **Timing recovery** with the Gardner TED — chosen because it works **before** carrier lock
   (Fundamentals 09). That lets us recover timing first, then carrier, which is by far the
   easier order to debug.
2. **Matched filtering**, folded into the polyphase interpolator. `pfb_mf_taps` must be built
   at `nfilters × sps` resolution:

```python
pfb_mf_taps = firdes.root_raised_cosine(nfilts, nfilts*sps, 1.0, excess_bw, 11*sps*nfilts)
```

> 🐛 **The error everyone hits first:** passing ordinary `11*sps`-length RRC taps here produces
> `length of the prototype filter taps must be greater than or equal to the number of
> polyphase filter arms`. The taps are a *prototype* that gets sliced into `nfilters` arms, so
> it must be `nfilters` times longer than a normal matched filter.

#### `costas` — Costas Loop
`order = 2` for BPSK. Its error detector is $e = \Re\{y\}\Im\{y\}$, which cancels the data and
leaves the phase error — see Fundamentals 09 for the derivation.

The optional **`frequency` output (port 1)** is wired to a Time Sink. This is the single best
debugging tool in the whole flowgraph: you can literally watch the loop acquire. It should
settle at

$$
\omega_{\text{settled}} = 2\pi \cdot f_{\text{offset}} \cdot \text{sps}
$$

because the loop runs at the symbol rate, after decimation by `sps`. With `freq_offset = 0.0005`
that is $2\pi \times 0.0005 \times 4 = 0.0126$ rad/sample.

### Measurement — the Embedded Python Block

`ber_monitor` is a `gr.sync_block` written directly inside the `.grc`. Open it in GRC
(right-click → Properties) to read the source. Its job:

1. **Settle** — ignore the first 100,000 bits while the loops acquire.
2. **Acquire** — buffer two full pattern periods, then cross-correlate one period against
   **every cyclic shift** of the reference, using one `np.correlate` against a doubly-tiled
   copy. The largest |correlation| gives the alignment; a *negative* peak means the stream is
   inverted, which is exactly the residual 180° ambiguity.
3. **Track** — XOR against the rolled reference, accumulate errors, emit the running BER as a
   float (one per input bit) so it can drive a Number Sink.

It also prints a line to the terminal every 200,000 bits:

```
[BER Monitor] bits=  1,606,453  errors=     570  BER=3.548e-04
```

**Watch the terminal, not just the GUI.** The printed numbers are the real result.

---

## 🧪 Running the Lab

```bash
cd 02_flowgraphs/lab07_bpsk_link_sim
gnuradio-companion lab07_bpsk_link_sim.grc
```

Or headless, which is often more convenient:

```bash
python3 lab07_bpsk_link_sim.py
```

### Exercise 1 — See a healthy link

Defaults: Eb/N0 = 8 dB, `loop_bw` = 0.010, freq offset 0.0005, clock ratio 1.00005.

Look at each display in turn:

| Display | Healthy | Meaning |
|---|---|---|
| Channel Spectrum | 135 kHz raised-cosine hump | $R_s(1+\alpha)$ |
| Eye Diagram | wide open eye | Timing is recoverable |
| Constellation | two tight dots at ±1 | Both loops locked |
| Costas frequency | flat line at ~0.0126 | Loop has acquired |
| Measured BER | converging toward 4×10⁻⁴ | ✅ |

Give the BER at least 30 seconds. At 100 kbit/s, measuring a BER of $10^{-5}$ to 10 %
accuracy needs about $10^7$ bits ≈ 100 seconds — you cannot measure a rare event quickly.

### Exercise 2 — Sweep Eb/N0 and build the waterfall curve

Set `loop_bw` = 0.010. For each Eb/N0, restart the flowgraph, wait 60 s, and record the printed
BER:

| Eb/N0 (dB) | Theory (DBPSK) | Your measurement |
|---|---|---|
| 2 | 7.22 × 10⁻² | |
| 4 | 2.47 × 10⁻² | |
| 6 | 4.77 × 10⁻³ | |
| 8 | 3.82 × 10⁻⁴ | |
| 10 | 7.74 × 10⁻⁶ | |

The theoretical column comes from $P_b = 2p(1-p)$ where $p = Q(\sqrt{2E_b/N_0})$:

```bash
python3 -c "
from math import erfc, sqrt
for e in (2,4,6,8,10):
    p = 0.5*erfc(sqrt(10**(e/10)))
    print(f'{e:>3} dB   BPSK {p:.3e}   DBPSK {2*p*(1-p):.3e}')"
```

Notice the **cliff**: 8 dB of extra signal buys four orders of magnitude. Digital links do not
degrade gracefully — they work, and then they stop.

### Exercise 3 — The loop bandwidth experiment (the important one)

Set Eb/N0 to **2 dB** and try three loop bandwidths. These are measured results, reproducible
on your machine:

| `loop_bw` | Measured BER | Theory | Verdict |
|---|---|---|---|
| 0.045 | 4.8 × 10⁻¹ | 7.2 × 10⁻² | ❌ loops lost lock — output is noise |
| 0.010 | 7.5 × 10⁻² | 7.2 × 10⁻² | ✅ essentially optimal |
| 0.005 | 7.4 × 10⁻² | 7.2 × 10⁻² | ✅ optimal, but slower to acquire |

**A loop bandwidth that is perfectly fine at 8 dB completely destroys the link at 2 dB.** The
loop is being driven by its own noise. This is the Fundamentals 09 trade-off, measured:

$$
\text{jitter} \propto \frac{B_n}{\text{SNR}}
$$

Now do the opposite: set Eb/N0 to 12 dB and `loop_bw` to 0.001. Watch the Costas frequency
display — the loop takes visibly *seconds* to crawl to the right frequency. Narrow loops track
beautifully and acquire terribly.

### Exercise 4 — Break each thing on purpose

| Change | What you should see | Why |
|---|---|---|
| `freq_offset` → 0.008 | Constellation becomes a **ring** | Offset exceeds the loop's pull-in range |
| `timing_offset` → 1.0005 (500 ppm) | Constellation smears **radially** | Timing loop cannot track the drift |
| Costas `order` → 4 | BER ≈ 0.5 | Wrong error detector for BPSK |
| Bypass both differential blocks | BER flips between good and 0.5 on restart | 180° ambiguity |
| Eb/N0 → 0 dB | Eye closes, constellation is a blob | Noise dominates |

Each one of these is a bug you will meet in a real receiver. Meeting them here, where you know
the answer, is much cheaper.

---

## 🔬 Verification

This flowgraph was executed headlessly and its output compared against theory:

```
$ QT_QPA_PLATFORM=offscreen python3 lab07_bpsk_link_sim.py     # Eb/N0 = 8 dB
[BER Monitor] bits=  2,610,918  errors=   1,044  BER=3.999e-04
[BER Monitor] bits=  3,212,573  errors=   1,264  BER=3.935e-04
[BER Monitor] bits=  3,813,652  errors=   1,486  BER=3.897e-04
```

Differential BPSK theory at 8 dB: $2p(1-p)$ with $p = 1.909\times10^{-4}$ gives
$\mathbf{3.817\times10^{-4}}$. Measured **3.90 × 10⁻⁴** — agreement to within 2 %, which is
inside the statistical uncertainty of ~1500 error events.

The standalone script `03_scripts/simulate_bpsk_ber.py` runs the whole sweep automatically and
prints the comparison table.

---

## 🐛 Troubleshooting

### "`length of the prototype filter taps must be >= number of polyphase filter arms`"
`pfb_mf_taps` was built at the wrong resolution. It must use `nfilts` gain, `nfilts*sps` rate
and `11*sps*nfilts` taps — see the block-by-block section above.

### "BER sits at exactly 0.5 and never moves"
The BER monitor never locked. Causes, in order of likelihood: the loops are not locked (look at
the constellation first — fix that, not the monitor); `settle` is longer than your run;
`pattern` in the monitor does not match the `pattern` in the Vector Source.

### "BER is around 0.5 but the constellation looks perfect"
Classic 180° inversion with the differential blocks bypassed. The monitor's correlation should
catch this — if you also removed the polarity search, it will not.

### "The constellation is a ring"
No carrier lock. Either `freq_offset` is beyond the pull-in range, or `loop_bw` is too narrow
to acquire it, or the Costas `order` is wrong.

### "The constellation dots are smeared along the radius"
Timing, not carrier. Check `sps` matches between the modulator and Symbol Sync, and widen
Symbol Sync's `loop_bw`.

### "It runs far slower than real time / one core is at 100 %"
The polyphase matched filter with 32 arms at 400 kSPS is the expensive part. Reduce `nfilts` to
16, or lower `samp_rate` to 200000 (halving your bit rate, so BER measurements take twice as
long).

### "The BER is consistently ~2× the BPSK theory"
That is correct, and it is not a bug — you have differential encoding on. DBPSK BER is
$2p(1-p) \approx 2p$. Bypass the differential pair to see the raw BPSK curve.

---

## ❓ Questions to Ponder

1. **Why measure Eb/N0 rather than SNR?**
   SNR depends on the measurement bandwidth, so a wasteful modulation can flatter itself by
   quoting SNR in a narrow band. Eb/N0 normalises out both bandwidth and bit rate, which is the
   only way to compare a BPSK link with a 64QAM one honestly.

2. **The link is BPSK. Convert it to QPSK — what changes?**
   `symbol_table` becomes the four Gray-coded QPSK points; Costas `order` becomes 4; the slicer
   is replaced by a Constellation Decoder; `k` becomes 2 in the noise formula; the differential
   decoder's `modulus` becomes 4. The BER-vs-Eb/N0 curve should be **unchanged** — you get twice
   the bit rate for free, in the same bandwidth.

3. **Why does Gardner's TED not need carrier lock, when Mueller & Müller does?**
   M&M is decision-directed: it needs to know which symbol was sent, which needs a locked
   constellation. Gardner compares energy at the midpoint against the transition, which is a
   magnitude relationship and so is blind to absolute phase.

4. **You measured BER = 0 over 4 million bits at 12 dB. What can you claim?**
   Only that BER < ~1/4,000,000 ≈ 2.5 × 10⁻⁷ with modest confidence. **You cannot measure a
   BER you have not observed errors at.** A rule of thumb: you need ~100 error events for a
   ±10 % estimate, so measuring 10⁻⁹ needs 10¹¹ bits — 11 days at 100 kbit/s. This is why
   real BER testing uses hardware and why FEC performance is usually simulated, not measured.

5. **The Channel Model has a `taps` parameter set to `[1.0+0j]`. What if you set it to
   `[1.0, 0.0, 0.3]`?**
   You have added multipath: a delayed echo at 30 % amplitude. The constellation will smear and
   the BER will floor out no matter how much power you add — noise is no longer the limit, ISI
   is. Fixing that needs an equaliser, which is the natural next topic.

---

## 📚 Key Takeaways

- **A digital receiver is three feedback loops and a lookup table.** The loops are the hard part.
- **Loop bandwidth is the single most important receiver parameter**, and the right value
  depends on the SNR you are operating at. There is no universally good setting.
- **Recover timing before carrier** using a phase-blind TED like Gardner. It is far easier to
  debug.
- **Differential encoding costs ~3 dB and buys immunity to phase ambiguity.** Usually worth it.
- **Calibrate your noise before you trust your BER.** A factor of two in `noise_voltage` is a
  3 dB error that looks exactly like a broken receiver.
- **You cannot measure a BER faster than errors occur.** Budget the bits.

---

## 🚀 What's Next?

You now know how a digital receiver works in the clean room. Lab 08 applies it to a **real
signal off the air**: the RDS data subcarrier hidden at 57 kHz inside every FM broadcast you
have been listening to since Lab 01 — differentially encoded BPSK at 1187.5 bit/s, with the
self-synchronising CRC from Fundamentals 10.

**Next:** [Lab 08 — RDS Decoder →](../lab08_rds_decoder/README.md)

---

## 📖 References

1. GNU Radio Wiki: [Symbol Sync](https://wiki.gnuradio.org/index.php/Symbol_Sync) · [Costas Loop](https://wiki.gnuradio.org/index.php/Costas_Loop) · [Channel Model](https://wiki.gnuradio.org/index.php/Channel_Model)
2. GNU Radio Wiki: [Embedded Python Block](https://wiki.gnuradio.org/index.php/Embedded_Python_Block)
3. Rice, *Digital Communications: A Discrete-Time Approach* — the standard reference for Symbol Sync's TED algorithms
4. Gardner, F. M., "A BPSK/QPSK Timing-Error Detector for Sampled Receivers", IEEE Trans. Comm., 1986
