# 🗓️ Session Plan — Client Briefing

> **What this page is:** the shape of the 2½-hour session: what happens when, what to cut if you
> run late, and what to do if the radio fails.
> **Who it is for:** the presenter, and anyone helping on the day.
> **Time:** 150 minutes, one 10-minute break.

---

## Contents

1. [Who and why](#1-who-and-why)
2. [Run of show](#2-run-of-show)
3. [If you run late: the cut order](#3-if-you-run-late-the-cut-order)
4. [Risks and what to do](#4-risks-and-what-to-do)
5. [If the radio fails completely](#5-if-the-radio-fails-completely)
6. [What the room needs](#6-what-the-room-needs)

---

## 1. Who and why

**The audience:** military end users. Not engineers. They will not build anything.

**Their question:** *"What is this box, and what would we use it for?"*

**Our answer:** mostly shown, not told. About 45 minutes of plain explanation, then 70 minutes
of live demonstrations.

**How this differs from [the training course](../06_training/README.md):**

| | Training course (`06_training`) | This briefing (`07_client_demo`) |
|---|---|---|
| Audience | People who will build radios | People who will use them |
| Length | 4 hours | 2½ hours |
| Slides | 63, with theory | 36, no equations, no code |
| GNU Radio | Built live, block by block | Never opened on screen |
| Goal | "You can start" | "We know what it is for" |

---

## 2. Run of show

The clock column is time from the start. Write your real start time beside it on the day.

| Clock | Min | Block | Slides | What happens |
|---|---|---|---|---|
| 0:00 | 5 | **Welcome** | S1–S2 | Live spectrum already on the second screen |
| 0:05 | 18 | **What is software-defined radio** | S3–S9 | Four jobs · old way · the one picture · honest weaknesses |
| 0:23 | 12 | **The SignalSDR Pro** | S10–S15 | Pass a spare box round · numbers in plain words · what it is not |
| 0:35 | 12 | **Six capabilities** | S16–S21 | What they will and will not see · the legal line |
| 0:47 | 10 | **Break** | S22 | You: `./preflight.sh`, TV box on, big terminal font |
| 0:57 | 70 | **Demonstrations** | S23–S30 | Six demos from [the run sheet](./DEMO_RUNSHEET.md), then the recap |
| 2:07 | 8 | **The software** | S31–S33 | Three levels of user · DragonOS · where GNU Radio fits |
| 2:15 | 15 | **Where next** | S34–S36 | Rules · what we propose · questions |
| 2:30 | | **End** | | Handout on the table |

### Inside the demonstration block

| Clock | Min | Demo | Radio? |
|---|---|---|---|
| 0:57 | 2 | Six demonstrations (S23) | — |
| 0:59 | 7 | 1 · See the invisible | receive |
| 1:06 | 12 | 2 · Hidden data | receive |
| 1:18 | 14 | 3 · Tour the busy bands | receive |
| 1:32 | 6 | 4 · Record now, analyse later | none |
| 1:38 | 5 | 5 · Noise against a signal | none |
| 1:43 | 20 | 6 · Television to your TV | 🚨 transmits |
| 2:03 | 4 | What you just saw (S30) | — |

The planned minutes include about 15 minutes of spare time, spread across the demos. The
[run sheet](./DEMO_RUNSHEET.md) gives the time each demo takes when it goes well.

💡 **Tip:** the speaker view (press **S** in the deck) shows a clock and says "on time",
"behind" or "ahead" against this plan.

---

## 3. If you run late: the cut order

Cut in this order. Each line says how much time it saves.

| # | Cut | Saves | Why this is safe |
|---|---|---|---|
| 1 | The car-key bonus in Demo 3 | 3 min | It was never promised |
| 2 | The TV scanner (Demo 3, part 2) | 4 min | The band tour already makes the point |
| 3 | S13 and S14 (window, where it sits) | 4 min | S11 already says "56 MHz at once" |
| 4 | Demo 5 (noise) | 5 min | It is a simulation; the story works without it |
| 5 | S33 (where GNU Radio fits) | 2 min | Say its one sentence on S31 instead |
| 6 | Demo 4 (record and replay) | 6 min | Mention it on S30: "we can also record" |

**Never cut:** S5 (the one picture), S21 (the legal line), Demo 2 (hidden data), Demo 6
(television), S35 (what we propose).

If you are **early**, spend it on questions at S30 and S36. Do not add content.

---

## 4. Risks and what to do

| Risk | How likely | What you do |
|---|---|---|
| The radio is not found | Low | Unplug both cables. Power first, wait 30 s, then data. Do Demo 5 while it starts |
| Demo 2 shows no station name | Medium | Raise gain to 65. After 30 s: `./d2_rds.sh test`, and say it is a test signal |
| Signals are weak indoors | Medium | Move to a window. Signal here changed by about 30 dB between morning and evening on 26 Sep 2026 |
| The TV box will not find the channel | Medium | After 3 min: `./d6_fallback_loop.sh` (the box sends TV to itself) |
| The Lab 12 video window does not open | Unknown | Nobody has watched it live yet. Point at the `[TV] LOCKED` line and the 16 dots instead |
| Only one screen in the room | Medium | The TV box must share the projector. Switch the input for Demo 6 only |
| No sound in the room | High | Every demo's payoff is on screen. Sound is a bonus |
| gqrx does not work | Medium | It is not used unless it was tested last night. `uhd_fft` does the same job |
| A transmitter is left running | Low | `./stop_all.sh` after Demo 6. Every time. Say "the transmitter is off" |
| A question you cannot answer | High | "I do not know. I will reply by email." Write it down. See [QA_MILITARY.md](./QA_MILITARY.md) |

---

## 5. If the radio fails completely

If the radio is dead and a power cycle does not fix it, the session still works. It becomes
about 15 minutes shorter. Do this:

| Demo | Instead | Command |
|---|---|---|
| 1 | Play the recording | `fallbacks/d1_spectrum.webm` |
| 2 | Decode a test signal made on the laptop | `./d2_rds.sh test` |
| 3 | The scanner's self-test | `./d3_bands.sh test` |
| 4 | **Runs normally** — it never used the radio | `./d4_replay.sh` |
| 5 | **Runs normally** — it never used the radio | `./d5_bpsk.sh` |
| 6 | Play the recording | `fallbacks/d6_television.webm` |

**Say it once, at the start of the block, and not again:**

> "The radio is not cooperating in this building. So for some demos I will show you a recording
> of it working last night, and say which ones. Two of the demos never needed the radio, so you
> will see those live."

Then use the saved time for questions. Do not apologise again.

---

## 6. What the room needs

| Need | Why |
|---|---|
| A projector or large screen, 1920×1080 | The deck is 16:9 |
| A **second** screen or the TV itself, with HDMI | For the TV box in Demo 6 |
| Two power sockets near the table | Laptop, radio, TV box |
| A seat near a window, if possible | Stronger signals indoors |
| A table the audience can gather round | For Demo 6 and the box itself |
| Printed [handouts](./client_handout.html), one per person | They leave with something |

Tick everything off in [the setup checklist](./SETUP_CHECKLIST.md) the morning before.

---

## ✅ Summary

- **150 minutes:** about 45 explaining, 70 demonstrating, 10 break, the rest software and next
  steps.
- **Cut from the top of the cut order** if late. Never cut the SDR picture, the legal line,
  Demo 2, Demo 6 or the proposal.
- **Every demo has a fallback.** Demos 4 and 5 need no radio at all.
- **If the radio dies,** the session still works: say it once, use the recordings, move on.

**Next:** [The setup checklist →](./SETUP_CHECKLIST.md)
