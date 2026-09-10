# 📻 Lab 06 — Multimode Receiver: AM / NBFM / WBFM

> **Time:** 2 hours
> **Difficulty:** Advanced
> **Theory needed:** [Fund. 05 Sampling & Filters](../../01_fundamentals/05_sampling_and_filters.md) · [Fund. 06 Noise & SNR](../../01_fundamentals/06_noise_snr_and_gain.md) · [Fund. 07 AM & NBFM](../../01_fundamentals/07_am_and_narrowband_fm.md)
> **New blocks:** Frequency Xlating FIR Filter, AM Demod, NBFM Receive, Selector, Chooser, Moving Average, Log10, Number Sink
> **Blocks in flowgraph:** 35

---

## 🎯 Goal

Build one receiver that handles **three modulation schemes**, tunes **anywhere in a 2 MHz
window without touching the hardware**, and tells you how strong the signal is.

This is the lab where the flowgraph stops being "an FM radio" and becomes a **radio**. Lab 03
gave you one signal path with knobs on it. Lab 06 gives you a *branching* signal path with a
runtime switch — which is how every real SDR application is structured.

Three new ideas:

1. **Two-stage channelisation** — coarse selection at high rate, fine selection at low rate.
2. **Parallel demodulator branches with a Selector** — switching modes without restarting.
3. **Measurement** — an S-meter that reads the *channel*, not the band.

---

## 📖 Background: One Tuner, Many Channels

Your SignalSDR Pro delivers 2 MHz of spectrum. Inside that 2 MHz there might be ten FM
stations, or forty marine channels, or a hundred airband channels. A hardware radio would have
to retune its local oscillator to reach each one. **We don't have to.**

```
        2 MHz captured in one shot from the AD9361
   ┌──────────────────────────────────────────────────┐
   │   ▲          ▲       ▲            ▲        ▲     │
   │ 99.3       99.7    100.1        100.5    100.9   │
   └────┬─────────┬────────┬────────────┬────────┬────┘
        │         │        │            │        │
        └─────────┴────────┼────────────┴────────┘
                           │
              Frequency Xlating FIR Filter
              ( mix by -offset, filter, decimate )
                           │
                           ▼
                  one channel at 400 kSPS
```

Moving the `offset_freq` slider changes a complex multiply. It takes effect on the **next
sample** — no PLL settling, no gap in the stream, no clicks. Moving the `freq` slider retunes
the AD9361 and interrupts the stream for milliseconds. **They are not the same operation**, and
knowing which one you are using is the difference between a scanner that works and one that
misses transmissions.

### Why the default offset is −200 kHz

A direct-conversion receiver leaks its own local oscillator into its own input. The result is a
permanent spike at **exactly** the tuned frequency — the "DC spike" or "LO leakage".

```
       ┌ LO leakage / DC offset (hardware artifact, NOT a signal)
       │
   ────┴────  ▁▂▃█▇▃▂▁
       0 Hz     your station
```

If you tune the hardware directly onto the station you want, that spike sits right in the
middle of your channel. The standard cure — used by every serious SDR application — is to tune
the hardware **beside** the signal and use the xlating filter to come back. That is why `freq`
defaults to 100.1 MHz and `offset_freq` to −200 kHz, putting the actual reception at 99.9 MHz
with the DC spike safely 200 kHz away.

> **This is worth 8.8 dB, measured.** Running this exact flowgraph on a live SignalSDR Pro
> against BFM 89.9 MHz:
>
> | Configuration | Audio SNR |
> |---|---|
> | hardware at 90.1 MHz, `offset_freq` = −200 kHz | **75.7 dB** |
> | hardware at 89.9 MHz, `offset_freq` = 0 | **66.9 dB** |
>
> Same station, same gain, same antenna, same 6-second window. The only difference is where the
> LO sits relative to the signal.

---

## 📐 Architecture

```
                          ┌──────────────┐
                          │ USRP Source  │ 2 MSPS complex
                          └──────┬───────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
        Freq Sink          Waterfall      ┌───────────────────────┐
        (full span)        (full span)    │ Freq Xlating FIR      │
                                          │ mix -offset_freq      │
                                          │ LPF 150 kHz, decim 5  │
                                          └───────────┬───────────┘
                                                      │  400 kSPS
                        ┌─────────────────────────────┴───────────┐
                        │                                         │
              WIDE PATH ▼                             NARROW PATH ▼
                  ┌───────────┐                        ┌────────────────┐
                  │ AGC2 (c)  │                        │ Low Pass Filter│
                  │ ref 0.5   │                        │ cutoff narrow_bw│
                  └─────┬─────┘                        │ decim 8        │
                        │                              └───┬─────┬──────┘
                  ┌─────▼──────┐                           │     │  50 kSPS
                  │ WBFM Recv  │                    ┌──────┘     └──────┐
                  │ /8 → 50 k  │                    │                   │
                  └─────┬──────┘             ┌──────▼──────┐   ┌────────▼───────┐
                        │                    │ Pwr Squelch │   │ S-METER        │
                        │                    │ gate=False  │   │ |x|² → avg     │
                        │                    └──────┬──────┘   │ → 10log10      │
                        │                           │          │ → Number Sink  │
                        │                    ┌──────▼──────┐   └────────────────┘
                        │                    │ AGC2 (c)    │
                        │                    │ ref 0.3     │
                        │                    └──┬───────┬──┘
                        │                       │       │
                        │              ┌────────▼──┐ ┌──▼──────────┐
                        │              │ AM Demod  │ │ NBFM Receive│
                        │              │ envelope  │ │ dev 5 kHz   │
                        │              └────┬──────┘ └──────┬──────┘
                        │                   │ 50k           │ 50k
                        │        ┌──────────┴───────────────┘
                        │        │
                  ┌─────▼────────▼─────────┐
                  │  Selector (float)      │  in0=AM  in1=NBFM  in2=WBFM
                  │  input_index = mode    │
                  └───────────┬────────────┘
                              ▼
                    ┌──────────────────┐
                    │ Multiply (volume)│
                    └────┬────────┬────┘
                         ▼        ▼
                  Audio Sink   Time Sink
                   50 kHz
```

### The rate table

| Wire | Rate | Type | Bandwidth carried |
|---|---|---|---|
| USRP → xlating | 2 MSPS | complex | ±1 MHz |
| xlating → wide path | 400 kSPS | complex | ±150 kHz |
| xlating → narrow LPF | 400 kSPS | complex | ±150 kHz |
| narrow LPF → demods | 50 kSPS | complex | ±`narrow_bw` |
| all demods → selector | 50 kSPS | **float** | 0–5 kHz (AM), 0–15 kHz (FM) |
| selector → audio | 50 kSPS | float | audio |

$2\text{M} \div 5 = 400\text{k} \div 8 = 50\text{k}$. Exact integers all the way down, as
[Fundamentals 05](../../01_fundamentals/05_sampling_and_filters.md) insists.

---

## 📋 Block-by-Block

### Stage 1 — Coarse channelisation

#### `xlating_wide` — Frequency Xlating FIR Filter (`ccf`)

```
decim       = 5
taps        = wide_taps   (LPF 150 kHz cutoff, 30 kHz transition)
center_freq = offset_freq  ← the software tuning knob
samp_rate   = 2000000
```

Tap count, from the Fundamentals 05 equation:

$$
N = \frac{53 \times 2{,}000{,}000}{22 \times 30{,}000} = 160.6 \rightarrow 161 \text{ taps}
$$

Because the block is decimating, those 161 taps are only evaluated 400,000 times per second,
not 2,000,000 — a 5× saving that comes free with `decim`.

Why 150 kHz cutoff and not 100 kHz? Because the wide path must pass a complete WBFM channel,
which by Carson's rule is 180–256 kHz wide. 150 kHz cutoff gives ±150 kHz = 300 kHz of
passband. The output Nyquist is 200 kHz, so the transition band (150→180 kHz) finishes with
20 kHz to spare.

### Stage 2a — the wide path (WBFM)

#### `agc_wide` — AGC2, complex
Placed **after** the channel filter, per Fundamentals 06. `reference = 0.5`, fast attack
(0.01), slow decay (0.001). `max_gain = 4096` stops the AGC from amplifying pure noise by a
factor of 65536 when you tune to an empty frequency.

#### `wbfm_rcv` — WBFM Receive
`quad_rate = 400000`, `audio_decimation = 8` → 50 kSPS. Same block as Lab 01; it just gets a
cleaner input now.

### Stage 2b — the narrow path (AM, NBFM)

#### `narrow_lpf` — Low Pass Filter (`fir_filter_ccf`)

```
samp_rate   = 400000
cutoff_freq = narrow_bw   ← slider, 3–18 kHz
width       = 2000
decim       = 8           → 50 kSPS out
```

$N = 53 \times 400{,}000 / (22 \times 2000) = 481$ taps — but again running at the 50 kSPS
output rate, so only ~24 million MACs/second. Cheap.

**This is the filter that decides your selectivity.** Set `narrow_bw` to:

| Service | Setting | Why |
|---|---|---|
| Airband AM | 4000 Hz | Voice is 300–3000 Hz; 4 kHz keeps the adjacent 25 kHz channel out |
| Marine / PMR NBFM | 8000 Hz | Carson: $2(5+3) = 16$ kHz total, i.e. ±8 kHz |
| NOAA weather | 8000 Hz | Same as marine |
| Wide NBFM / experimenting | 12000–18000 Hz | More audio bandwidth, less adjacent rejection |

Narrowing this filter is also how you buy SNR — see the processing-gain formula in
[Fundamentals 06](../../01_fundamentals/06_noise_snr_and_gain.md).

#### `squelch` — Power Squelch, complex

```
threshold = squelch_threshold   ← slider, dBFS
alpha     = 0.01                 running-average constant
ramp      = 20                   samples of fade-in/out — kills the click
gate      = False                ← IMPORTANT
```

> ⚠️ **`gate` must be `False` here.** With `gate = True` the block produces *no samples at all*
> when the squelch is closed. Downstream, the Audio Sink starves and the flowgraph stalls.
> `gate = False` emits zeros — which is what "silence" means to a sound card.

#### `am_demod` — AM Demod (`analog_am_demod_cf`)

Envelope detection: $\hat{x} = |I + jQ|$, followed by a 5 kHz audio low-pass (`audio_pass`
5000, `audio_stop` 5500). `audio_decim = 1` because we are already at 50 kSPS.

Envelope detection's practical superpower: **it does not care about frequency offset.** Get the
tuning wrong by 2 kHz and AM still works, because $|\cdot|$ is invariant under the rotation
that a frequency error produces. Try it — mistune `offset_freq` by 5 kHz on an airband signal
and it stays intelligible until the signal falls outside the channel filter.

#### `nbfm_rcv` — NBFM Receive

```
audio_rate = 50000
quad_rate  = 50000     → internal audio decimation of 1
tau        = 75e-6     → de-emphasis (use 50e-6 outside the Americas)
max_dev    = 5e3       → sets the quad demod gain: fs/(2π·Δf)
```

`max_dev` is the parameter people get wrong. It sets the demodulator's output scaling to
$f_s / (2\pi \Delta f) = 50000/(2\pi \times 5000) = 1.59$. Set it to 75 kHz by accident and
your NBFM audio comes out 15× too quiet. See
[Fundamentals 07](../../01_fundamentals/07_am_and_narrowband_fm.md).

### Stage 3 — the Selector

#### `mode_selector` — Selector (float, 3 in, 1 out)

```python
self.mode_selector.set_input_index(self.mode)   # called by the radio buttons
```

**All three demodulator branches run all the time.** The Selector only chooses which one
reaches the audio sink. This costs CPU — you are demodulating AM, NBFM and WBFM
simultaneously — and buys **instant, glitch-free mode switching**.

That trade is usually right for a lab and often right in production: modern CPUs have the
cycles, and the alternative (reconfiguring the graph at runtime with `lock()`/`unlock()`) is
much harder to get right.

> **Why all three branches must produce the same sample rate:** the Selector is a stream block.
> It cannot resample. This constraint is why `audio_rate` is fixed at 50 kHz and why every
> branch was designed backwards from it.

### Stage 4 — the S-meter

```
narrow_lpf → Complex to Mag² → Moving Average(5000) → Log10(n=10, k=3.0103) → Number Sink
```

Tapped **after** the channel filter, so it measures the channel you are listening to and not
the loudest thing in the 2 MHz span. 5000 samples at 50 kSPS is a 100 ms window — fast enough
to follow speech syllables, slow enough that the number is readable.

The `k = 3.0103` constant is $10\log_{10}2$, converting mean power to dBFS (see Lab 05).

**This meter is the tool you use to set the squelch.** Tune to an empty channel, read the
number, set `squelch_threshold` about 5 dB higher.

---

## 🧪 Running the Lab

```bash
cd 02_flowgraphs/lab06_multimode_receiver
gnuradio-companion lab06_multimode_receiver.grc
```

### Exercise 1 — WBFM, and prove software tuning works

1. Mode = **WBFM**. `freq` = 100.1 MHz, `offset_freq` = −200 kHz → you are on 99.9 MHz.
2. Look at the **Full Span** sink. You should see several FM stations as ~200 kHz blocks.
3. Note the offset of a station you can see, and dial `offset_freq` to it.
   **Listen to how instantly it switches.** No click, no gap.
4. Now change `freq` by 200 kHz instead. Notice the momentary interruption — that is the
   AD9361 PLL relocking. Two different tuning mechanisms, two very different behaviours.

### Exercise 2 — NOAA Weather Radio (NBFM)

North America only, but it is the easiest NBFM signal to find because it transmits 24/7.

1. Mode = **NBFM**, `narrow_bw` = 8000.
2. `freq` = 162.600 MHz, then sweep `offset_freq` from −200 kHz to +200 kHz in 25 kHz steps.
   The seven channels are at 162.400, 162.425, 162.450, 162.475, 162.500, 162.525, 162.550.
3. Watch the **S-Meter** jump when you land on an active channel.
4. Set `squelch_threshold` 5 dB above the empty-channel reading, then sweep again — silence
   between channels, audio on them.

### Exercise 3 — Airband AM

1. Mode = **AM**, `narrow_bw` = 4000.
2. `freq` = 120.0 MHz. Watch the **waterfall** rather than the FFT — airband is bursty, and a
   3-second transmission is invisible on an averaged FFT but obvious on a waterfall.
3. When you see a burst, note its offset and tune to it.
4. Squelch is essential here: without it you listen to noise 95 % of the time.

Nothing on airband? You are probably not near an airport, or your antenna is indoors. Airband
is a good test of your antenna, because 118–137 MHz is close enough to the FM broadcast band
that the *same* antenna works.

### Exercise 4 — Prove the AM frequency-offset immunity

On an AM signal, deliberately mistune `offset_freq` by ±2 kHz. The audio stays intelligible.
Now do the same on an NBFM signal: the audio distorts badly, because the quadrature
demodulator's output is the *frequency* error and a constant tuning offset adds a DC term that
drives the audio off-centre.

This is [Fundamentals 07](../../01_fundamentals/07_am_and_narrowband_fm.md) made audible.

### Exercise 5 — Watch the processing gain

1. Tune to a weak NBFM signal.
2. Set `narrow_bw` to 18000 and read the S-meter.
3. Set it to 4000 and read again.

The signal level barely changes; the *noise* drops by roughly
$10\log_{10}(18000/4000) = 6.5$ dB. That is the processing gain equation from Fundamentals 06,
measured on your own hardware.

---

## 🐛 Troubleshooting

### "There is a huge spike in the middle of the Full Span display"
LO leakage / DC offset — a hardware artifact, not a signal. That is exactly why the default
`offset_freq` is −200 kHz. If it bothers you visually, add a `Correct IQ` block after the USRP
Source.

### "NBFM audio is very quiet compared to WBFM"
Check `max_dev` on the NBFM Receive block. It must be `5e3`, not `75e3`.

### "The audio cuts in and out even on a strong signal"
Squelch threshold is too high. Read the S-meter while the signal is present and set the
threshold 5–10 dB below that.

### "The flowgraph stalls a few seconds after starting"
You set `gate = True` on the squelch. Set it back to `False`.

### "Switching modes produces a loud pop"
Normal — the three demodulators have different DC levels. A high-pass at 50 Hz after the
Selector removes it. (Worth adding as an exercise.)

### "`IndexError: input_index must be < ninputs` when I call `set_mode()`"
You called it **before** `tb.start()`. A Selector's input count is not resolved until the
flowgraph is flattened, which happens at start. This never bites you in the GUI — you change
modes while it is running — but it will if you drive the flowgraph from a script. Start first,
then set the mode.

### "The Selector will not connect / GRC complains about types"
All three demodulator outputs must be `float` at the same rate. If you change `audio_rate` you
must re-derive every branch: `wbfm_rcv.audio_decimation`, `nbfm_rcv.audio_rate`, and
`am_demod.audio_decim`.

### "CPU usage is very high"
You are running three demodulators plus two FFT sinks plus a waterfall. Reduce `fftsize` to
1024, raise `update_time` to 0.25, or disable the waterfall (right-click → Disable). The
waterfall is usually the most expensive block in any flowgraph.

---

## ❓ Questions to Ponder

1. **Why two filter stages instead of one 400 kHz-to-50 kHz filter straight from 2 MSPS?**
   A single-stage filter from 2 MSPS to 50 kSPS with an 8 kHz cutoff and a 2 kHz transition
   would need $53 \times 2{,}000{,}000/(22 \times 2000) = 2409$ taps. Two stages need
   $161 + 481 = 642$. Multi-stage decimation is almost always cheaper — the standard result is
   that cost scales roughly with the *logarithm* of the total decimation when staged well.

2. **Could you use one Frequency Xlating FIR Filter per channel and listen to several at once?**
   Yes, and that is exactly how a real scanner works. Add a second xlating filter fed from the
   same USRP Source with a different `center_freq`. This is also what a Polyphase Channelizer
   does, far more efficiently, for many channels at once.

3. **Why does the S-meter tap the channel filter output and not the USRP Source?**
   Because a meter on the source measures the total power in 2 MHz — dominated by whatever the
   strongest station in the band happens to be. It would tell you nothing about your channel.

4. **AM Demod ignores frequency offset. Why is that not true for SSB?**
   Envelope detection discards phase entirely. SSB reconstruction needs the exact carrier
   phase, so a frequency error shifts every audio component by the same absolute amount —
   producing the characteristic "Donald Duck" sound.

5. **The Selector runs all three demodulators. What would you do on a Raspberry Pi?**
   Use `lock()` / `disconnect()` / `connect()` / `unlock()` to rebuild the graph on mode change,
   or use `blocks.copy` gates on each branch as in Lab 05 to stop the unused branches from
   consuming CPU. The Selector approach trades CPU for simplicity.

---

## 📚 Key Takeaways

- **Hardware tuning and software tuning are different operations** with different costs. Use
  the hardware to choose a *band* and the xlating filter to choose a *channel*.
- **Never tune the hardware directly onto your signal** — offset it to dodge the DC spike.
- **Filter, then AGC, then demodulate.** Any other order lets a neighbouring signal control
  your gain.
- **Multi-stage decimation is dramatically cheaper** than doing it all in one filter.
- **`gate = False` on squelch feeding audio.** Always.
- **Measure the channel, not the band.** An S-meter is only meaningful after the channel filter.

---

## 🚀 What's Next?

Everything so far has been analog: waveform in, waveform out. Lab 07 crosses into **digital** —
a complete BPSK link built in simulation, with timing recovery, carrier recovery, and a bit
error rate you measure and compare against theory. No hardware required.

**Next:** [Lab 07 — BPSK Link Simulation →](../lab07_bpsk_link_sim/README.md)

Before you start it, read [Fundamentals 08 — Digital Modulation](../../01_fundamentals/08_digital_modulation.md)
and [09 — Synchronization](../../01_fundamentals/09_synchronization.md).

---

## 📖 References

1. GNU Radio Wiki: [Frequency Xlating FIR Filter](https://wiki.gnuradio.org/index.php/Frequency_Xlating_FIR_Filter) · [Selector](https://wiki.gnuradio.org/index.php/Selector) · [AM Demod](https://wiki.gnuradio.org/index.php/AM_Demod)
2. NOAA: [Weather Radio frequencies](https://www.weather.gov/nwr/)
3. ITU-R: airband channel spacing (25 kHz / 8.33 kHz)
