# 🔬 How This Repository Was Tested

> **What you will learn:** how each lab was checked, the real measurements, the lessons that
> real hardware and careful testing taught us, and what is still **not** tested.
> **Before this:** nothing. But the lessons make more sense after Labs 01–06.
> **Time:** about 20 minutes.

---

## Why this page exists

It is easy to write a tutorial that *looks* right. It is harder to prove that it *is* right.
Every claim in this repository was checked, and the checks are included, so you can run them
again yourself.

---

## 1. Six levels of checking

Each level catches mistakes the level above it cannot.

| Level | Question it answers | How to run it |
|---|---|---|
| **Structure** | Is the `.grc` file written correctly? | `validate_flowgraph.py --structural-only` |
| **Deep** | Does every block, setting and connection exist in the installed GNU Radio 3.10? | `validate_flowgraph.py <folder>` |
| **Compile** | Does GNU Radio turn it into Python that runs? | `validate_flowgraph.py <folder> --compile` |
| **Maths** | Does the signal processing give the right answer? | the `simulate_*.py` scripts |
| **Run** | Does the real flowgraph produce the right output from a test signal with a known answer? | `test_labs_offline.py` |
| **Hardware** | Does it work on a real radio, with real stations? | run it on a live SignalSDR Pro |

**Status:** all 17 flowgraphs pass Structure, Deep and Compile. Labs 01–04 pass Run
(`test_labs_offline.py`). Labs 01, 03, 04, 05, 06 and 08 were also run on live radio signals.

---

## 2. Measurements from real hardware

Radio used: a **SignalSDR Pro** in B210 mode (serial 194431, built-in GPS clock).
Station used: **BFM 89.9 MHz**, Kuala Lumpur, a real FM broadcast.
Every result below came from the flowgraphs in this repository, not a special test version.

> **What "audio SNR" means here.** SNR is *signal-to-noise ratio*: how much louder the wanted
> sound is than the background hiss, in decibels (dB). Higher is better. Every 10 dB means
> ten times less noise power. As a rough guide: 20 dB is listenable, 40 dB is clean,
> 60 dB and above is excellent.
>
> We measured it as the loudest part of the speech band (0.1–5 kHz) compared with the average
> level in a band where there should be no sound at all.

| Lab | What we measured | Result | What it means |
|---|---|---|---|
| 01 | Audio SNR, 3-block radio | **53.2 dB** | Clean audio from the simplest possible radio |
| 03 | Audio SNR, with channel filter + AGC + squelch | **62.6 dB** | Better again — mostly thanks to the channel filter |
| 04 | Frequency the stereo circuit locked to | **18999.79 Hz** (target 19000) | Off by only 11 parts per million |
| 04 | How clean the rebuilt 38 kHz tone was | **47.8 dB** above nearby noise | A very clean reference for stereo |
| 04 | How similar left and right channels are | **0.78** (1.0 = identical) | ⚠️ **Not proof of stereo** — see Lesson 9. The decoder was in fact almost mono at the time |
| 05 | Record 6 s, then play back | **79.7 dB** audio SNR | Recording loses nothing |
| 06 | Audio SNR, tuned 200 kHz to the side | **75.7 dB** | The best result of all |
| 06 | Audio SNR, tuned exactly on the station | **66.9 dB** | 8.8 dB worse — see Lesson 2 |
| 08 | RDS data messages received in 30 s | **287** (9.6 per second) | 84 % of the maximum possible (11.4 per second) |
| 08 | RDS messages on an **empty** channel | **0** out of 11,766 tries | The error check rejects noise correctly |
| 09 | Aircraft messages at 1090 MHz | **0** | Wrong antenna — see Lesson 4 |
| 11 | DVB-T test, bytes sent vs bytes received | **0 wrong in 4,201,236** | Perfect |
| 11 | Weakest signal that still works (standard says 13.5 dB) | **works at 13 dB, fails at 12 dB** | Matches the standard |
| 11 | Receiver speed, locked / not locked (needs 9.14) | **16.4 / 1.55 million samples/s** | Fast enough once locked |
| 11 | Scan of TV channels 21–48 with an FM antenna | **no TV found**; one on/off signal on ch 22 | No TV reaches this location — see Lesson 5 |
| 10 | DVB-T2 structure checks (the mode Malaysian TV uses) | **5 of 5 pass** | The signal matches the standard |
| 10 | Video data rate vs transmitter data rate | **40.000737 vs 40.000738 Mbit/s** | Matched almost exactly |
| 10 | Transmitter speed / gaps after start-up | **7.8× faster than needed**, 0 gaps in 70 s | Keeps up easily |
| 10 | **A real TV found the station and played the video** | reported by the lab owner | The whole chain works |
| 10 | Clock jumps backwards in 4.2 loops of the video | **0** in 83.9 s | Fixes the jerky video — see Lesson 7 |
| 12 | Full-duplex, 40 s of 1080p video: packets received | **422,304**, 0 sync errors, 0 missing | Perfect |
| 12 | Video received over the air, byte for byte | **79,357,996 bytes, 0 wrong** | 100.000000 % correct |
| 12 | Frames decoded from what was received | **975 video frames + 39.45 s of audio** | Real, playable video |
| 12 | Station name read back from the signal | **`SDR LAB TV`** | The TV service information works too |

---

## 3. Nine lessons

Simulation is useful, but it only tests what you thought of. Lessons 1–7 were found only by
using a real radio. Lessons 8 and 9 were found later, by running the real flowgraphs on test
signals with known answers. Each one is now fixed or documented where it matters.

### Lesson 1 — One missing setting cost up to 43 dB

**What happened.** In Labs 01–04, the radio block did not set its **analog bandwidth**
(the setting called `bw0`). When you leave it empty, the radio's hardware filter opens to its
widest value, **56 MHz**. That lets in a lot of unwanted energy — mostly a strong spike at the
centre of the screen (called **DC** or **LO leakage**; see
[Fundamentals 06](./01_fundamentals/06_noise_snr_and_gain.md)).

**The numbers.** Measured at 89.9 MHz, gain 55, twice:

| `bw0` setting | Filter width | Unwanted centre spike (share of the signal) | Wanted signal |
|---|---|---|---|
| not set | 56 MHz | **84 %** | 0.0160 |
| set to `samp_rate` | 2 MHz | **16 %** | 0.0149 |

The wanted station is the same size in both rows. Only the junk changed.

**Why it matters.** The next blocks cannot tell junk from signal. The AGC adjusts itself to
the junk, and the FM decoder gets a tiny wanted signal sitting on a big unwanted one.

**The fix:** one line, `bw0: samp_rate`.

| Lab | Before | After |
|---|---|---|
| 01 | 34.6 dB | **53.2 dB** (18.6 dB better) |
| 03 | 19.4 dB | **62.6 dB** (43.2 dB better) |

Labs 05–09 already had this setting. After the fix, each lab sounds better than the one before:
01 (53.2) → 03 (62.6) → 06 (75.7). That is what the course promises, and now it is measured.

> **Rule:** always set the analog bandwidth to your sample rate.

### Lesson 2 — Tuning beside the station is 8.8 dB better

Every SDR has a small spike exactly at the centre of its screen. It comes from the radio's own
tuning oscillator leaking into its input. If you tune exactly onto a station, the spike sits on
top of it.

Lab 06 tuned 200 kHz *beside* the station and moved it back in software: **75.7 dB**.
Tuned exactly on the station: **66.9 dB**. The difference, **8.8 dB**, is the cost of the spike.
That is why Lab 06 uses `offset_freq = −200 kHz` by default.

> **Rule:** tune a little to one side of the signal you want, then shift it back in software.

### Lesson 3 — Trust the error check, not your eyes

Lab 08 reads RDS, the small data signal that carries a station's name. At first, we looked at
the spectrum near 57 kHz (where RDS lives) and saw only a tiny bump, 1.9 dB. We decided
"there is no RDS here". That was **wrong**.

The decoder found it easily: **287 good messages in 30 seconds**. Each message has a built-in
error check (a **CRC**), so a good message cannot happen by accident. As a control, we pointed
the decoder at an empty channel: **0 messages** out of 11,766 tries.

BFM 89.9 changes its 8-letter name every few seconds, so we saw it scroll:

```
"BUSINESS"  →  "BFM 89.9"  →  "FINANCE "
```

The station ID code (**PI**) stayed at `0x6000` the whole time. Of five local stations tested,
only 89.9 MHz sends RDS we could decode.

> **Rule:** a decoder with an error check is far more sensitive than looking at a spectrum.

### Lesson 4 — Lab 09 heard nothing, because of the antenna

Lab 09 received **zero** aircraft messages, on both antenna ports.

How we knew the antenna was the problem: raising the gain from 70 to 76 dB (+6 dB) raised the
background noise by exactly 6.0 dB too. When noise rises one-for-one with gain, the receiver is
only hearing **itself**. More gain cannot help.

The antenna was made for FM (around 100 MHz). At 1090 MHz it is about ten times too long.
This is item one in Lab 09's troubleshooting list.

> **Rule:** for ADS-B, build the simple 69 mm antenna described in Lab 09.

### Lesson 5 — Two detectors agreed, and both were wrong

While scanning the TV band, channel 22 looked like digital TV to **both** of our detectors.
One scored 13.9 (threshold far lower), the other 31.4. But it was **not** TV. It was a signal
that switched on and off: 4 ms bursts, on only 7.6 % of the time.

**Why the detectors were fooled.** Both detectors ask: "does this signal repeat itself after a
fixed delay?" A short burst overlaps with itself at *any* delay you test. So a burst always
looks like a match.

**The fix.** Add two simple checks that work a different way:

| Check | Real DVB-T | Channel 22 |
|---|---|---|
| Steep edges on the spectrum (TV has them) | **31 dB** | 1.2 dB |
| Share of time the signal is off | **0 %** | 7.6 % |

`scan_tv_band.py --selftest` now creates a fake burst signal and checks the scanner rejects it.

> **Rule:** know how each detector can be fooled. Pair it with a check that is fooled in a
> different way. (Compare Lesson 3: there, the spectrum said "nothing" and the error check was
> right. Here, the detectors said "TV" and the spectrum was right.)

### Lesson 6 — A test tone can make a weak link look strong

Lab 12's first over-the-air test decoded **nothing**. Yet a plain test tone, sent with the same
settings, stood **42 dB** above the noise. How can both be true?

A tone puts all its power into one very narrow slot (one 2.2 kHz FFT bin). A TV signal spreads
the same power over 7.6 MHz — about 3,400 slots. Spreading it that thin costs about **35 dB**.
So:

```
   42 dB   how strong the tone looked
 − 35 dB   loss from spreading over 7.6 MHz
 −  8.4 dB the tone's total power was higher than the TV signal's
 ───────
 ≈ −1.4 dB how strong the TV signal really was
```

We measured +0.92 dB. The receiver needs about 13 dB. So it could never work.

**More receive gain cannot fix this** — it lifts the signal and the noise together. **More
transmit gain** did: 19 dB more, and the signal rose 16.5 dB, and the receiver locked at once.

> **Rule:** when you test a wide signal with a narrow tone, remember the tone looks much
> stronger than the wide signal will be.

### Lesson 7 — Every byte was correct, but the video was not smooth

The first long DVB-T2 broadcast played on a real TV in high quality, but it was **jerky**.
Nothing was broken or missing. Every byte arrived correctly.

**The cause.** We looped the finished `.ts` video file. A TV stream carries its own clock,
called the **PCR** (Program Clock Reference). At the end of each loop, the clock jumped
**backwards by 208.86 seconds**. The TV lost track of time every lap. Over 26 minutes this
happened 7.5 times.

**The fix.** Loop the *original video* instead, and let the encoder keep counting forward.
This is what real TV stations do. `tv_playout.py` does this. Tested for 4.2 laps:
**0 backward clock jumps** in 83.9 s.

> **Rule:** TV is a timing system that happens to carry data. Correct bytes are not enough;
> the timing must be correct too. Only watching a real TV found this bug.

### Lesson 8 — A squelch placed after an AGC can never close

*Found in the September 2026 review, by testing the real flowgraph on known signals.*

Lab 03 promised "silence between stations". It could not deliver it. Its squelch came
**after** the AGC. The AGC's job is to lift every signal to the same level — including plain
noise. So the squelch always saw a "strong" signal and never muted.

Pure noise at −60 dBFS (a typical empty channel), squelch set to −50 dB:

| Order | What came out | Squelch |
|---|---|---|
| AGC → Squelch (old) | −12.9 dB of hiss | never closes |
| **Squelch → AGC (fixed)** | silence | closes correctly |

Lab 06 already had the right order. Lab 03 now matches it.

> **Rule:** anything that *measures* signal strength must come before anything that
> *changes* it automatically.

### Lesson 9 — "It plays music" hid a stereo decoder that was really mono

*Found in the September 2026 review.*

Lab 04's stereo decoder played music in both ears, and a hardware test showed the left and
right channels were different (correlation 0.78). It looked like stereo. It was not.

A test signal with a **1000 Hz tone only on the left** and a **1700 Hz tone only on the right**
showed about **1 dB** of separation — the left channel had almost as much of the right tone as
its own. A working decoder gives 30 dB or more.

Two mistakes caused it (Lab 04, Section 5 explains both):

1. The narrow pilot filter delays the pilot by 578 samples, but the MPX it is multiplied with
   was not delayed to match. The rebuilt 38 kHz carrier had the wrong phase.
2. The standard uses a **sine** carrier. The decoder took the real part (a cosine) of the
   rebuilt carrier — a quarter-turn wrong.

| Version (real flowgraph, same test signal) | Left | Right |
|---|---|---|
| Before | 1.2 dB | −0.4 dB |
| **After** | **32.5 dB** | **31.0 dB** |

The two simulation scripts that were meant to check Lab 04 did not catch this. They used
perfect zero-delay filters and a cosine pilot, so they never met either problem. One of them
was also quietly failing. They have been replaced by `test_labs_offline.py`, which runs the
lab's **real** generated code.

> **Rule:** test with a signal whose right answer you know exactly — and test the real code,
> not a copy of it. Real music is partly different in each ear anyway, so a correlation number
> cannot tell stereo from mono.

---

## 4. Known issue

**Lab 06: `set_mode()` fails before the flowgraph starts.**
If you call `set_mode()` in Python **before** `start()`, you get:

```
IndexError: input_index must be < ninputs
```

This is because GNU Radio only counts a Selector block's inputs when the flowgraph starts.
It does not affect normal use — you change mode with the GUI while it runs.
If you control Lab 06 from your own Python code, call `start()` first, then `set_mode()`.

---

## 5. Not tested yet

Being clear about what is **not** proven is as important as what is.

- **The TV result was reported by a person, not measured by a tool.** A real TV found the
  station and played the video well. But no recording was made. The fix for the jerky video
  (Lesson 7) is proven by measurement, but nobody has watched the fixed version yet.
- **Nobody has watched the received picture live.** Labs 11–12 were checked by decoding frames
  and audio from the received data, and by comparing files byte by byte — not by watching
  `ffplay`.
- **No real broadcast TV was received here.** There is no TV signal at this location with this
  antenna. All TV decoding used our own transmitter. For DVB-T2 there is currently no free,
  real-time software receiver at all.
- **Lab 12 never had a frequency error to correct.** It sends and receives on the same radio,
  so both sides share one clock. A real receiver always has a small frequency error. This case
  is not tested.
- **Lab 07** is a simulation by design. "Over the air" does not apply. Its error rate was
  checked against theory.
- **Lab 09** has only decoded test messages, never a real aircraft here. The decoder matches the
  official Mode S test examples, but real reception is not proven (see Lesson 4).
- **Lab 06's AM and narrow-FM modes** were not tested on real signals. No aircraft or marine
  voice could be heard with this antenna. Only the wide-FM mode was measured.
- **The Lab 03 and Lab 04 fixes (Lessons 8 and 9) have not yet been re-run on the radio.**
  The radio was not available during the review. Both fixes are proven on test signals by
  `test_labs_offline.py`, which runs the real flowgraphs.
- **Lab 04 on a mono station:** there is no pilot detector, so a little of the mono sound
  leaks into L−R (measured about 10 dB below L+R on a test signal). Real radios switch to mono.
- **Lab 08's RadioText** (the scrolling song title) was not tested. The only RDS station here
  sends only the station name (group type 0), never RadioText (group type 2).

---

## ✅ Summary

- Every flowgraph is checked automatically. Most labs were also run on a real radio.
- Always set `bw0` (the analog bandwidth) to the sample rate. It is worth up to 43 dB.
- Tune a little beside the signal, not exactly on it. It is worth 8.8 dB.
- Pair detectors that fail in different ways. Trust error checks over your eyes.
- Test the real code with a signal whose right answer you know. "It works" is not a test.
- A squelch must come before an AGC.
- The antenna is usually the problem when you hear nothing at all.
- For TV, correct timing matters as much as correct data.

**Back to:** [README →](./README.md)
