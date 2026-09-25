# 📻 Lab 06 — One Radio, Many Modes (AM / NBFM / WBFM)

> **What you will build:** one receiver that can decode **three** kinds of signal — AM, narrow
> FM and wide FM — tune anywhere inside a 2 MHz window **without retuning the hardware**, and
> show how strong the signal is.
> **What you will learn:** tuning in software vs. hardware, filtering in two stages, switching
> between parallel paths with a **Selector**, and building a signal meter (**S-meter**).
> **Before this:** [Lab 05](../lab05_iq_record_playback/README.md),
> [Fundamentals 05](../../01_fundamentals/05_sampling_and_filters.md),
> [06](../../01_fundamentals/06_noise_snr_and_gain.md) and
> [07 — AM & Narrow FM](../../01_fundamentals/07_am_and_narrowband_fm.md).
> **Time:** about 2 hours. **Difficulty:** advanced. **Needs the radio:** yes (or a test file).

---

## 🎯 Goal

Until now, each flowgraph was one straight line: an FM radio. This lab has **branches**. The
signal splits into three decoders running side by side, and a switch picks which one you hear.
Most real SDR programs are built this way.

Three new ideas:

1. **Two-stage filtering** — a wide filter first, then a narrow one.
2. **Parallel decoders with a Selector** — change mode instantly, without restarting.
3. **Measurement** — an S-meter that measures *your channel*, not the whole band.

---

## 1. Background: one tuner, many channels

The radio delivers **2 MHz** of spectrum at once. Inside that 2 MHz there might be ten FM
stations, or dozens of aircraft or marine channels. A normal radio must retune its hardware to
reach each one. **We don't have to** — we pick a channel in software, with the Frequency
Xlating FIR Filter you met in Lab 05.

```
        2 MHz, received all at once
   ┌──────────────────────────────────────────────────┐
   │   ▲          ▲       ▲            ▲        ▲     │
   │ 99.3       99.7    100.1        100.5    100.9   │
   └────┬─────────┬────────┬────────────┬────────┬────┘
        └─────────┴────────┼────────────┴────────┘
                           │
              Frequency Xlating FIR Filter
              (shift by the offset, filter, keep 1 in 5)
                           │
                  one channel at 400 kSPS
```

### Two ways to tune — and they are not the same

| | **Hardware tuning** (`freq`) | **Software tuning** (`offset_freq`) |
|---|---|---|
| What changes | The radio's LO (its internal tuning signal) | A multiplication in the computer |
| Range | 70 MHz – 6 GHz | Only inside the 2 MHz you are receiving |
| Speed | The hardware must re-lock: a gap of a few milliseconds | Instant, from the very next sample |
| Clicks or gaps? | Yes, briefly | No |

Use hardware tuning to choose a **band**. Use software tuning to choose a **channel** inside
it. A scanner that retunes the hardware for every channel will miss short transmissions during
the gaps.

### Why the default offset is −200 kHz

Every SDR has a small spike exactly at the frequency the hardware is tuned to. It comes from
the radio's own LO leaking into its input. It is **not** a signal.

```
       ┌ LO leakage (the radio's own spike, NOT a signal)
       │
   ────┴────  ▁▂▃█▇▃▂▁
       0 Hz     your station
```

If you tune the hardware exactly onto your station, the spike lands in the middle of it. The
fix, used by almost every SDR program: tune the hardware **beside** the signal, then use
software tuning to come back.

So the defaults are: hardware `freq` = **100.1 MHz**, `offset_freq` = **−200 kHz**. You listen
to 99.9 MHz, and the spike is 200 kHz away, outside your channel.

> **Measured: this is worth 8.8 dB.** This flowgraph on a real SignalSDR Pro, BFM 89.9 MHz:
>
> | Setup | Audio SNR |
> |---|---|
> | hardware at 90.1 MHz, offset −200 kHz | **75.7 dB** |
> | hardware at 89.9 MHz, offset 0 | **66.9 dB** |
>
> Same station, gain, antenna and 6-second window. Only the position of the spike changed.

---

## 2. The flowgraph

```
                           USRP Source  (2 MSPS)
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
         Spectrum           Waterfall        Freq Xlating FIR Filter
        (full 2 MHz)       (full 2 MHz)      shift by offset_freq,
                                             low-pass 150 kHz, ÷5
                                                    │ 400 kSPS
                          ┌─────────────────────────┴─────────────┐
                 WIDE PATH│                              NARROW PATH│
                          ▼                                         ▼
                        AGC                              Low Pass Filter
                          │                              cutoff narrow_bw, ÷8
                          ▼                                  │ 50 kSPS
                    WBFM Receive ÷8                ┌─────────┼──────────────┐
                          │ 50 kSPS                ▼         ▼              ▼
                          │                    Squelch   Channel        S-METER
                          │                        │     spectrum   |x|² → average
                          │                        ▼                → dB → number
                          │                       AGC
                          │                     ┌──┴──────┐
                          │                     ▼         ▼
                          │                 AM Demod   NBFM Receive
                          │                     │         │
                          ▼                     ▼         ▼
                    ┌──────────────────────────────────────────┐
                    │ Selector: input 0 = AM, 1 = NBFM, 2 = WBFM │
                    └───────────────────┬──────────────────────┘
                                        ▼
                                     Volume
                                   ┌────┴────┐
                                   ▼         ▼
                              Audio Sink   Audio display
                               50 kHz
```

### Sample rates

| Between | Rate | Type | Width carried |
|---|---|---|---|
| USRP → xlating filter | 2 MSPS | complex | ±1 MHz |
| xlating → both paths | 400 kSPS | complex | ±150 kHz |
| narrow filter → decoders | 50 kSPS | complex | ±`narrow_bw` |
| all decoders → Selector | 50 kSPS | **float** | audio |
| Selector → Audio Sink | 50 kSPS | float | audio |

2,000,000 ÷ 5 = 400,000 ÷ 8 = 50,000. Whole numbers all the way down, as
[Fundamentals 05](../../01_fundamentals/05_sampling_and_filters.md) recommends.

### Controls

| Control | Range | Default | What it does |
|---|---|---|---|
| **Hardware Centre** | 70 MHz – 6 GHz | 100.1 MHz | Hardware tuning: picks the band |
| **Channel Offset** | −900 to +900 kHz | −200 kHz | Software tuning: picks the channel |
| **RF Gain** | 0–76 dB | 40 | Hardware gain |
| **Demodulator** | AM / NBFM / WBFM | WBFM | Which decoder you hear |
| **Narrow Channel BW** | 3–18 kHz | 8 kHz | Width of the narrow filter (AM and NBFM only) |
| **Squelch** | −90 to 0 dBFS | −70 | Mute level (AM and NBFM only) |
| **Volume** | 0–5 | 1.0 | Loudness |

---

## 3. The blocks

### Stage 1 — the wide filter (both paths)

**Frequency Xlating FIR Filter** — shift, filter, decimate:

| Setting | Value |
|---|---|
| Decimation | 5 (2 MSPS → 400 kSPS) |
| Taps | low-pass, cutoff **150 kHz**, transition 30 kHz → **161 taps** |
| Center frequency | `offset_freq` — the software tuning knob |

**Why 150 kHz and not 100 kHz?** This stage must pass a whole wide-FM station, about 200 kHz
wide (±100 kHz), with some room to spare. The output rate is 400 kSPS, so the limit is
±200 kHz. The filter goes from "pass" at 150 kHz to "block" by 180 kHz — still inside 200 kHz,
so there is no aliasing.

Because the block decimates, its 161 taps are worked out only 400,000 times per second, not
2,000,000. That is 5 times less work, for free.

### Stage 2a — the wide path (WBFM)

**AGC** — reference 0.5, attack 0.01, decay 0.001, max gain 4096.
Placed after the channel filter, so a strong neighbour cannot control it. (Remember from
Lab 03: for FM the AGC does not change the loudness. It keeps the level predictable.)

**WBFM Receive** — 400 kSPS in, ÷8, 50 kSPS audio out. The same block as Lab 01.

> 💡 The wide path has **no squelch**. The squelch below only affects AM and NBFM.

### Stage 2b — the narrow path (AM and NBFM)

**Low Pass Filter** — cutoff = `narrow_bw` slider (3–18 kHz), transition 2 kHz, decimate by 8
(400 kSPS → 50 kSPS). About **481 taps**, but worked out only 50,000 times per second, so it is
cheap.

**This filter decides how well you reject neighbouring channels.** Suggested settings:

| Signal | `narrow_bw` | Why |
|---|---|---|
| Aircraft voice (AM) | 4000 Hz | Voice is 300–3000 Hz. 4 kHz keeps the next channel out |
| Marine, amateur, walkie-talkie (NBFM) | 8000 Hz | Carson's rule: 2 × (5 + 3) = 16 kHz wide, i.e. ±8 kHz |
| Experimenting | 12000–18000 Hz | More audio, less rejection of neighbours |

A narrower filter also lets in **less noise**, so weak signals become clearer. See Exercise 5.

**Power Squelch** — mutes when the channel is empty.

| Setting | Value | Meaning |
|---|---|---|
| Threshold | `squelch_threshold` (dBFS) | Mute below this |
| Alpha | 0.01 | How fast it follows the signal level |
| Ramp | 20 | Fade in and out over 20 samples, so there is no click |
| Gate | **False** | When muted, send zeros (silence), not nothing |

It sits **before** the AGC, so it measures the real signal level (see
[Lab 03 §4](../lab03_advanced_wbfm/README.md#4-why-this-order-the-most-important-part-of-this-lab)).

**AGC** — reference **1.0**, attack 0.02, decay 0.0005, max gain 4096. For AM, the sound *is*
the size of the signal, so here the AGC really matters: it keeps strong and weak AM stations at
a similar loudness.

> 🔎 **Why reference 1.0?** GNU Radio's AM Demod block takes the size of the signal, then
> **subtracts exactly 1.0** to remove the carrier. That only works if the carrier arrives at
> exactly 1.0. An earlier version of this lab used 0.3, which left a constant **−0.35** offset
> on the AM audio, and a loud pop every time you switched mode. Found with
> `test_labs_offline.py`; fixed by setting the reference to 1.0.

**AM Demod** — takes the **envelope** (the size of each IQ sample, √(I² + Q²)), removes the
carrier, and low-pass filters to 5 kHz. Audio decimation 1, because we are already at 50 kSPS.

A useful property: **AM does not care about small tuning errors.** The size of the arrow does
not change when it rotates. Mistune by 2 kHz and AM still sounds fine — until the signal slides
out of the channel filter. (Try it in Exercise 4.)

**NBFM Receive**

| Setting | Value | Meaning |
|---|---|---|
| Audio rate | 50000 | Output rate |
| Quadrature rate | 50000 | Input rate (so no further decimation) |
| Tau | 75e-6 | De-emphasis. Many two-way radios use a stronger emphasis; if voices sound thin and sharp, try 750e-6 |
| Max deviation | **5e3** | Sets the output scale: full deviation (±5 kHz) comes out as ±1 |

> ⚠️ **`max_dev` is the setting people get wrong.** If you set it to 75e3 (the wide-FM value) by
> mistake, NBFM audio comes out **15 times too quiet** (75 ÷ 5 = 15).

### Stage 3 — the Selector

A **Selector** block has several inputs and one output. Its `input_index` setting (here, the
**Demodulator** buttons) chooses which input goes to the output.

**All three decoders run all the time.** The Selector only chooses which one you hear. This
uses more CPU (three decoders instead of one), but switching modes is **instant** and cannot
break anything. That is usually a good trade on a modern computer.

> ⚠️ **All inputs to a Selector must have the same sample rate and type.** It cannot resample.
> That is why every decoder was designed to output float audio at exactly 50 kSPS.

### Stage 4 — the S-meter

```
narrow filter → Complex to Mag² → Moving Average (5000) → Log10 (n = 10, k = 3.0103) → number
```

It measures the power **after** the channel filter, so it shows the strength of the channel you
are listening to — not the strongest signal somewhere in the 2 MHz. 5000 samples at 50 kSPS is
a 0.1 s window: fast enough to follow speech, slow enough to read.

`k = 3.0103` converts power to dBFS, as in Lab 05.

**Use the S-meter to set the squelch:** tune to an empty channel, read the number, and set the
squelch about **5 dB higher**.

---

## 4. Exercises

```bash
cd "02_flowgraphs/lab06_multimode_receiver"
gnuradio-companion lab06_multimode_receiver.grc
```

### Exercise 1 — Wide FM, and software tuning

1. Mode **WBFM**. Hardware Centre 100.1 MHz, offset −200 kHz → you hear 99.9 MHz.
2. Look at the full-span spectrum. You should see several FM stations, each about 200 kHz wide.
3. Read the offset of another station on the spectrum, and set **Channel Offset** to it.
   **Listen: it switches instantly.** No click, no gap.
4. Now change **Hardware Centre** by 200 kHz instead. You hear a short break while the hardware
   re-locks. Two ways to tune, two very different behaviours.

### Exercise 2 — Narrow FM: marine or amateur radio

1. Mode **NBFM**, Narrow Channel BW **8000**.
2. **Marine VHF:** Hardware Centre **157.0 MHz**, offset **−200 kHz** → **156.800 MHz**,
   channel 16, the international calling and distress channel. Best near the coast or a port.
3. **Amateur 2 m:** Hardware Centre around **145.5 MHz**. Watch the waterfall for short
   transmissions, then set the offset to them. Local repeaters are listed by
   [MARTS](https://marts.org.my/).
4. Watch the **S-Meter** jump when someone transmits.
5. Set the squelch 5 dB above the empty-channel reading. Now you hear silence between
   transmissions, and speech when someone talks.

> 🚨 Listening to marine and amateur radio is fine. **Never transmit** on these frequencies
> without the right licence.

### Exercise 3 — Aircraft voice (AM)

1. Mode **AM**, Narrow Channel BW **4000**.
2. Hardware Centre **120.0 MHz**. Watch the **waterfall**, not the spectrum. Aircraft messages
   are short, and a 3-second call is easy to miss on the spectrum but easy to see on the
   waterfall.
3. When you see a burst, read its offset and tune to it.
4. Use the squelch. Without it, you listen to noise 95 % of the time.

Nothing heard? You may be too far from an airport (KLIA, Subang, Penang and Kota Kinabalu are
the busiest), or your antenna is indoors. The aircraft band (118–137 MHz) is close to the FM
band, so the same antenna works for both.

### Exercise 4 — AM ignores small tuning errors; NBFM does not

On an AM signal, move the offset by ±2 kHz. The speech stays clear.

Do the same on an NBFM signal. It sounds much worse. The NBFM decoder measures frequency, so a
tuning error adds a constant offset to its output, and the signal also moves towards the edge
of the channel filter.

This is [Fundamentals 07](../../01_fundamentals/07_am_and_narrowband_fm.md) made audible.

### Exercise 5 — See the processing gain

1. Tune to a weak NBFM signal.
2. Set Narrow Channel BW to **18000**. Read the S-meter on an empty channel next to it.
3. Set it to **4000**. Read again.

The **noise** drops by about 10·log₁₀(18000 ÷ 4000) = **6.5 dB**. The signal hardly changes.
That is the "narrower filter = less noise" rule from
[Fundamentals 06](../../01_fundamentals/06_noise_snr_and_gain.md), measured on your own radio.

---

## 5. Test it without a radio

```bash
cd 03_scripts
python3 make_test_iq.py /tmp/am.cfile --mode am --offset=-200e3 --snr 40
python3 run_offline.py ../02_flowgraphs/lab06_multimode_receiver/lab06_multimode_receiver.py \
        /tmp/am.cfile --out /tmp/lab06 --after mode=0
```

(`--offset=-200e3` needs the `=` sign because the value starts with a minus.)
`--after mode=0` selects AM **after** the flowgraph starts — see the Troubleshooting note
about `IndexError` below. `python3 test_labs_offline.py lab06` checks all three modes and the
squelch automatically.

---

## 🔧 Troubleshooting

| Problem | Cause and fix |
|---|---|
| A big spike in the middle of the full-span display | The radio's own LO leak, not a signal. That is why the default offset is −200 kHz |
| NBFM much quieter than WBFM | NBFM Receive's `max_dev` must be `5e3`, not `75e3` |
| Audio cuts in and out on a strong signal | Squelch too high. Read the S-meter during the signal and set the squelch 5–10 dB below |
| The flowgraph freezes a few seconds after starting | Squelch `gate` was set to True. Set it to False |
| `IndexError: input_index must be < ninputs` from `set_mode()` | You called it before `start()`. A Selector only counts its inputs when the flowgraph starts. Start first, then set the mode. (The GUI is not affected) |
| GRC complains about the Selector's types | Every decoder output must be float, at the same rate. If you change `audio_rate`, change `wbfm_rcv` decimation, `nbfm_rcv` audio rate and `am_demod` decimation too |
| CPU very high | Three decoders plus three displays. Set FFT size to 1024, or disable the waterfall (right-click → Disable) |

---

## ✅ Summary

- **Hardware tuning** picks the band (slow, with a gap). **Software tuning** picks the channel
  (instant).
- Tune the hardware **beside** your signal to avoid the centre spike. Worth 8.8 dB here.
- **Two-stage filtering** (wide, then narrow) is far cheaper than one big filter.
- A **Selector** switches between decoders that all run at once. Its inputs must match in
  rate and type.
- For AM, the AGC matters, and its level must suit the decoder (here, 1.0).
- Measure signal strength **after** the channel filter.

## 🧠 Check yourself

1. You want to scan 20 channels inside 2 MHz quickly. Hardware or software tuning?
   <details><summary>Answer</summary>Software tuning (the offset). It is instant and has no
   gaps.</details>
2. One filter from 2 MSPS straight to 50 kSPS, with an 8 kHz cutoff and 2 kHz transition, needs
   about 2409 taps. How many do the two stages here need?
   <details><summary>Answer</summary>161 + 481 = 642 — about a quarter, and the second stage
   runs at a much lower rate.</details>
3. Why does the S-meter connect after the narrow filter, not to the USRP Source?
   <details><summary>Answer</summary>At the source it would measure all 2 MHz — mostly the
   strongest station in the band — and tell you nothing about your channel.</details>
4. Why is AM not affected by a small tuning error?
   <details><summary>Answer</summary>AM is the size (envelope) of the signal. A tuning error
   only rotates the IQ arrow; it does not change its size.</details>
5. What goes wrong if the narrow AGC's reference is 0.3 instead of 1.0?
   <details><summary>Answer</summary>AM Demod subtracts 1.0, so the audio gets a constant
   −0.35 offset, less headroom, and a pop when you switch mode.</details>

**Next:** [Lab 07 — A Digital Link, Simulated →](../lab07_bpsk_link_sim/README.md). Read
[Fundamentals 08](../../01_fundamentals/08_digital_modulation.md) and
[09](../../01_fundamentals/09_synchronization.md) first.

---

## 📖 References

1. GNU Radio Wiki: [Frequency Xlating FIR Filter](https://wiki.gnuradio.org/index.php/Frequency_Xlating_FIR_Filter) ·
   [Selector](https://wiki.gnuradio.org/index.php/Selector) · [AM Demod](https://wiki.gnuradio.org/index.php/AM_Demod)
2. [Malaysia reference](../../05_reference/04_malaysia.md) — local bands and clubs
3. ITU-R: aircraft band channel spacing (25 kHz and 8.33 kHz)
