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

**Status:** all 17 flowgraphs pass Structure, Deep and Compile. Labs 01–06, 08 and 09 pass
Run (`test_labs_offline.py`, 9 checks); Lab 07 and Lab 10 were run headless against theory and
the standard. Labs 01, 03, 04, 05, 06 and 08 were also run on live radio signals.

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

### Re-checked on the radio, 26 September 2026

After the review's fixes, the receive labs were run again on the live radio with
`03_scripts/test_labs_live.py` (receive only; BFM 89.9 MHz, gain 40, 8 s each):

| Lab | Result |
|---|---|
| 01 | audio SNR **64.1 dB** |
| 02 | audio SNR **63.4 dB** |
| 03 | audio SNR **61.4 dB**; squelch on an empty channel (104.0 MHz): **silent** |
| 04 | stereo decoded (on music stations the fix recovers 4–8 dB more L−R — see Lesson 9) |
| 06 | audio SNR **68.2 dB** |

Later the same day (after Lesson 13's fixes), more labs on the radio:

| Lab | Result |
|---|---|
| 05 | recorded 8 s (128 MB, no samples lost) and played it back: audio SNR **68.4 dB** |
| 07 | (no radio needed) BER 4.0 × 10⁻⁴ at 8 dB; theory 3.8 × 10⁻⁴ |
| 08 | **182 RDS groups** in 30 s from BFM 89.9 (PI `0x6000`), names "BFM 89.9", "MUSIC", "FINANCE" |
| 09 | no aircraft — still no 1090 MHz antenna (Lesson 4) |
| 12 | the flowgraph itself, `TX/RX` → `RX2`: **16.13 Mbit/s, 0 continuity errors**, MER 19.7 dB, 1,381 frames decoded |
| 06 AM | not possible: no signal in the aircraft band (118–137 MHz) during the test |

The audio SNRs are close to the original measurements (which were taken at higher gain: 55–62).

---

## 3. Fourteen lessons

Simulation is useful, but it only tests what you thought of. Lessons 1–7 were found only by
using a real radio. Lessons 8–11 were found later, by running the real flowgraphs on test
signals with known answers. Lesson 12 was found by running the fixed labs on the real radio again, Lesson 13 by running
Lab 12 the way a student does, and Lesson 14 by questioning a status reading.
Each one is now fixed or documented where it matters.

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

**Confirmed on the air afterwards.** A survey of Kuala Lumpur FM stations measured the phase of
each station's stereo signal against its own pilot: every station with real stereo content had
it at **90°** — the sine phase the standard specifies, and what the fixed decoder uses. On two
music stations, the new decoder recovered **4–8 dB more** of the stereo difference than the old
one (97.6 MHz: L−R 8.3 dB below L+R instead of 12.7; 92.9 MHz: 6.9 instead of 14.7), and left and
right became clearly more different (correlation 0.92 → 0.74 and 0.96 → 0.66).

> **Rule:** test with a signal whose right answer you know exactly — and test the real code,
> not a copy of it. Real music is partly different in each ear anyway, so a correlation number
> cannot tell stereo from mono. (And BFM 89.9, used for most tests here, is a talk station: its
> stereo content is almost empty. Test stereo on a music station.)

### Lesson 10 — An AGC level must suit the block after it

*Found in the September 2026 review.*

GNU Radio's **AM Demod** block takes the size of the signal and then **subtracts exactly 1.0**, to
remove the carrier. That assumes the carrier arrives at 1.0. In Lab 06, the AGC before it held the
signal at **0.3**. The result, measured on an AM test station through the real flowgraph: the AM
audio sat at a constant **−0.354**, with a pop every time you switched mode.

Setting the AGC's reference to **1.0** removed it: DC **−0.000**, and the AM audio now peaks at
0.41, as the maths predicts. (The fast AGC attack was also checked: distortion only 0.1 %.)

> **Rule:** when two blocks work together, check what each one assumes about the other.

### Lesson 11 — When you change a mode, change every tool that measures it

*Found in the September 2026 review.*

Lab 10 moved from the 1K test mode to the 32K mode broadcasters use. The transmitter and the file
generator were updated. Two measuring tools were not:

- `lab10_dvbt2_analyze.grc` still looked for symbols 1024 samples apart. On a real 32K signal it
  showed **no symbol peaks at all** (only a 4.6× bump from the 1K-sized P1 preamble).
- `analyze_dvbt2.py` still **defaulted** to 1K, so the command in the README would have failed
  every check on the lab's own output.

Both now default to 32K. On a freshly generated 32K signal, the analyser flowgraph found **1,105
peaks spaced exactly 33,024 samples apart**, and `analyze_dvbt2.py` passed **5 of 5** with no
options.

> **Rule:** a mode change is not finished until the tools that check it have changed too — and
> have been run on the new output.

### Lesson 12 — The radio's centre spike can hide an empty channel

*Found by re-running the fixed Lab 03 on the real radio, 26 September 2026.*

With Lesson 8 fixed, the test signals said Lab 03's squelch worked. On the real radio, it still
let a little noise through on an empty channel. Measuring what the squelch sees (gain 40):

| | Channel power | The centre spike alone | Without the spike |
|---|---|---|---|
| BFM 89.9 MHz (a station) | −45.1 dB | −48.6 dB | **−47.8 dB** |
| 104.0 MHz (empty) | −46.9 dB | −47.6 dB | **−55.4 dB** |

Lab 03 tunes straight onto the station, so the radio's own centre spike (DC / LO leakage) sits
inside the channel — and it was **as strong as the station**. A station and an empty channel
differed by only 1.8 dB, so no squelch setting could separate them. Without the spike, they
differ by 7.6 dB.

**The fix:** a **DC Blocker** block before the squelch. On the real radio: empty channels
**completely silent**, and the station's audio SNR slightly better (63.6 dB against 61.9 dB).
`test_labs_offline.py` now adds a centre spike of the measured size to its test signals — and it
fails on the old Lab 03, so the mistake cannot come back unnoticed.

Two related findings from the same session:

- **`uhd_rx_cfile` cannot set the analog bandwidth.** A recording made with it had the 56 MHz
  filter problem of Lesson 1: BFM's stereo pilot was buried. Recorded with `bw0` set, it was clean.
  Setup 04 now warns about this.
- **Gain matters for stereo.** With the FM whip, gain 40 left the stereo pilot only 11 dB above
  the noise; gain 55 gave 27 dB.

> **Rule:** test signals must include the real radio's flaws (here, the centre spike), or the
> test passes where the radio fails. And re-test on the radio after every fix.

### Lesson 13 — The test passed, but it was not the program students run

*Found on 26 September 2026, after the lab owner reported that Lab 12 "showed nothing".*

Lab 12's best result — 422,304 packets, 79,357,996 bytes, no errors — was real. But it was
measured by `03_scripts/verify_tv_link.py`, a separate script that builds its own receiver. The
flowgraph in the Lab 12 folder, the one students open, had never received a signal.

Run with the radios replaced by a simulated cable, it failed in two ways:

- **It stopped before any window appeared** if the video stream `/tmp/bintang.ts` did not exist,
  with only `RuntimeError: can't open file`. (`/tmp` is emptied at every restart.) It now says
  which file is missing and prints the command that makes it.
- **Its signal-quality (MER) block crashed on the first signal** (`self.decimation()` does not
  exist for Python blocks in GNU Radio 3.10.9). A crashed block stops consuming data, so the whole
  receiver stalled after 48 packets: **no video, ever**. Lab 11 had the same block. After the fix:
  397,376 packets, 0 continuity errors, 911 decoded video frames.

It also starts with the transmitter off (on purpose), so the video appears only after TX gain and
TX amplitude are raised. The terminal now says so, and the README explains what to expect.

A third problem only showed on the real radio: the flowgraph was **too slow**. With a strong
signal (MER 21.9 dB) only 6.7 of 16.09 Mbit/s arrived. Measured without a radio, the whole
flowgraph ran at exactly 1.00× real time — no spare time at all — because the MER block measured
every one of 6.5 million points per second. Measuring 1 in 8 gives 1.3–1.6× real time, and on the
real radio: 16.13 Mbit/s, zero continuity errors.

> **Rule:** test the program people actually run, the way they run it — from a restarted
> computer, with the default settings. A test script that shares the idea but not the code proves
> the idea, not the program.

### Lesson 14 — A status reading said "broken"; the measurements said "fine"

*Found on 26 September 2026 — by getting it wrong first.*

That morning the radio's `lo_locked` sensor said `unlocked` on every frequency, on receive and
transmit, and stations looked weak. We concluded the radio had a hardware fault and asked for a
power supply check. Then we measured instead of trusting the reading: stations sat within 2 kHz of
their frequencies, and BFM's stereo pilot measured **19,000.0 Hz** at 58 dB above the noise. A
tuner that is really unlocked cannot do that. The transmit side rose exactly 10 dB for every 10 dB
of gain. The radio was fine. What had changed was how much signal reached `TX/RX` (about 30 dB
less than in the morning) — so at low gain the converter's own noise hid everything, and changing
the gain seemed to do nothing.

> **Rule:** a status flag is a claim, not a measurement. Before you blame the hardware, measure
> something you know the answer to — a station's frequency, a pilot tone. (This is Lesson 3 again:
> trust the check that actually measures.)

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

- **The TV result was reported by a person, not measured by a tool.** A real DVB-T2 TV found
  the Lab 10 station and played the video well — confirmed again by the lab owner on 26 September
  2026 (the transmitter flowgraph is unchanged since). But no recording was made. The fix for the jerky video
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
- **Lab 06's AM fix (Lesson 10) and Lab 10's analyser fix (Lesson 11) have not been tested on the
  radio.** There was no AM signal to receive, and Lab 10's analyser needs a transmitter, which was
  not switched on. Both are proven on test signals. (Lessons 8, 9 and 12 were re-checked on the
  radio — see above.)
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
- A squelch must come before an AGC, and must not be fooled by the centre spike. An AGC's level
  must suit the block after it.
- When you change a mode, update and re-run every tool that measures it.
- The antenna is usually the problem when you hear nothing at all.
- For TV, correct timing matters as much as correct data.

**Back to:** [README →](./README.md)
