# Introduction to SDR — 4-Hour Classroom Session
## Presentation plan, timings and speaker notes

**Audience: beginner to intermediate.** They have *used* radios — walkie-talkies, scanners, car
radios, maybe a base station — as **users, not designers**. Assume they can tune a radio and read
a signal-strength bar. Do **not** assume they can name the parts inside a radio, read a block
diagram, calculate with decibels, or write code. A few will know much more. Teaching both groups
at once is the main challenge of this session (see §2).

**Goal:** by the end of the session they can (a) say what SDR replaces and why in their own words, (b) set up a
SignalSDR Pro from cold and prove it works, (c) build one working flowgraph, and (d) name,
from having *seen* it, roughly ten things SDR does that their existing radios cannot.

**Not a goal:** covering everything. Four hours cannot teach this whole repository. The session
is a guided preview. Success is a person who knows **what to read next, and in what order.**

---

## 1. The design decisions behind this plan

| # | Decision | Why |
|---|---|---|
| 1 | **Explain the superhet — don't ask the room to name its parts.** Slide 8 *tells* them what is inside their radio; slide 9 moves one line through it. | A beginner cannot name the stages of a superheterodyne receiver. Asking them to try in front of others makes them feel foolish in the first twenty minutes, and you lose them. The "one line moved" picture still works — you just give it to them. |
| 2 | **Only two pieces of theory: sampling and I/Q — each with a simple "first step" slide before it.** | Filters, PLLs, error correction and OFDM can all be *watched* without understanding them. I/Q cannot: without it, every screen in the room means nothing. Beginners need "what is a wave, what is frequency" first, so Segment 3 gets 25 minutes, and other theory gets none. |
| 3 | **Setup is shown live, from the start, including a planned failure.** | This audience will judge SDR on whether they can make it work on Monday. The most valuable 25 minutes of the day is watching a radio start up — *and* watching the "UHD images" error get fixed, because every one of them will meet it. |
| 4 | **Lab 01 is built in front of them, slowly, explaining every click.** | One complete flowgraph turns "software radio" from a claim into something they have seen a person do. Labs 02–12 then look like *the same thing, bigger*. Hands-on version in §5. |
| 5 | **The lab tour is 40 minutes for 8 labs.** | Go deeper and you only show three labs instead of eight, and people leave without seeing how much SDR can do. For beginners, that range *is* the message — this is the part they will talk about afterwards. |
| 6 | **The transmit segment demos over a cable, not over the air.** | Legal, technical and pedagogical reasons — see §7. |

### What changed from the expert-audience version

Segment 2 gained a slide on *what a radio actually does*, before any block diagram. Segment 3
grew from 20 to 25 minutes and gained two "first step" slides. Segment 4 (hardware) shrank from
20 to 15 minutes — comparing SDR products interests intermediates, not beginners. Segment 8
(transmit) shrank from 30 to 25 minutes and now tells two real problem stories instead of three.
Overall: **more time on the two ideas that must be understood, less on material beginners cannot
use yet.**

---

## 2. Teaching a mixed-level room

A mixed room is harder than a room of only beginners or only intermediates. It can fail both
ways: aim at beginners, and the intermediates are bored by the first break; aim at
intermediates, and the beginners quietly decide SDR is not for them and never open the
repository. Five ways to handle it:

1. **Teach at the beginners' speed; demo at the intermediates' speed.** Segments 2–3 go slowly
   and skip nothing. Segment 7's demos are new to *everyone* — nobody in the room has seen
   aircraft positions decoded from raw samples — so the tour puts everyone at the same level
   again. That is why the lab tour is the longest segment.
2. **"Depth boxes".** A marked corner on technical slides with one line of real detail and a
   pointer into the repository — *"the discriminator is `atan2` on consecutive samples →
   fundamentals/04."* Read it aloud only if the room seems ready. Beginners can ignore it without
   feeling talked down to; intermediates get the detail they want, and a place to read more.
3. **A "parking lot", used openly.** A whiteboard column for questions you will answer later. It
   stops the session going off track for beginners, *and* shows intermediates their questions
   were not ignored. Answer them in Segment 9 — that is what the Q&A time is for.
4. **If there are laptops, work in pairs.** Seat people who have written code next to people who
   have not. The intermediates become your assistants, and stay interested by helping.
5. **Never say three phrases:** *"as you all know"*, *"this is trivial"*, *"obviously"*. Each one
   tells half the room they do not belong. Say *"some of you will know this"* instead — it is
   true, and it is comfortable for both groups.

> **Check the room at S4, and adjust.** If almost nobody raises a hand for "written any code",
> slow down S38's live build and explain every field. If more than a third do, go faster, and
> spend the saved minutes on S39's planned faults, which intermediates enjoy much more.

---

## 3. Time budget at a glance

| Segment | Content | Slides | Min | Cumulative |
|---|---|---|---|---|
| 1 | Why you are here — scope, promise, map | 1–6 | 15 | 0:15 |
| 2 | What a radio does, and what SDR changes | 7–15 | 30 | 0:45 |
| 3 | The two ideas you cannot skip | 16–23 | 25 | 1:10 |
| 4 | The hardware: SignalSDR Pro | 24–29 | 15 | 1:25 |
| — | **BREAK** | — | 10 | 1:35 |
| 5 | Making it work, live, from cold | 31–36 | 25 | 2:00 |
| 6 | Your first flowgraph, built in front of you | 37–40 | 25 | 2:25 |
| — | **BREAK** | — | 10 | 2:35 |
| 7 | What it can do — the lab tour | 42–51 | 40 | 3:15 |
| 8 | Transmitting: a television station | 52–58 | 25 | 3:40 |
| 9 | Where to go next, Q&A | 59–63 | 15 | 3:55 |
| — | Buffer / overrun | — | 5 | 4:00 |

**63 slides, 4:00 with two breaks** (60 content + 2 break cards + a title card). Taught slides run ~3 min each — slower than a normal
technical talk, deliberately. Demo slides are one slide plus live screen. The buffer is real:
do not plan to spend it, and do not let Segment 2 eat it.

---

## 4. Slide by slide

**The full notes for every slide are in [`PRESENTER_NOTES.md`](./PRESENTER_NOTES.md)** — in full
sentences: why the slide is there, words to say, what to do, likely questions with answers, and
background for you. The speaker view (press <kbd>S</kbd>) shows the same notes.

This table is the one-page run of show: why each slide is there. ★ = never cut.


**Segment 1 — Why you are here (15 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S1 | Title | 1 min | The room should see a radio working before you say a word. |
| S2 | The promise | 3 min | It tells people what success looks like, so they can relax. |
| S3 | What this session is not | 2 min | It removes fear. |
| S4 | Who is in the room | 3 min | You learn the level of the room, and you adjust the rest of the day to it. |
| S5 | The shape of the day | 3 min | People relax when they know the plan — especially when the breaks are. |
| S6 | Today is the trailer. This is the course. | 3 min | It tells people where everything lives, so they stop worrying about taking notes and start watching. |

**Segment 2 — What a radio does, and what SDR changes (30 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S7 | What every radio has to do | 3 min | It gives beginners a simple frame — four jobs — to hang everything else on. |
| S8 | Inside the radio on your desk | 5 min | It shows the classic radio as a chain of physical parts. |
| S9 | The whole idea, in one picture ★ | 5 min | This is the most important idea of the whole session. |
| S10 | Same jobs. Different material. | 3 min | It reassures people that SDR is not new physics. |
| S11 | Consequence 1 — one box, many radios | 3 min | It connects SDR to the audience's own experience: a shelf of single-purpose devices. |
| S12 | Consequence 2 — you fix it with a download | 2 min | One real example that everybody lived through makes the idea concrete. |
| S13 | Consequence 3 — radio becomes visible | 4 min · live | This is the most powerful minute of the segment. |
| S14 | What SDR is genuinely bad at | 3 min | Honesty builds trust. |
| S15 | The one-sentence version | 2 min | It summarises Segment 2 in one sentence that people can repeat to a colleague. |

**Segment 3 — The two ideas you cannot skip (25 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S16 | A wave, and three numbers | 3 min | Before talking about sampling, people need the words for describing a wave: amplitude, frequency and phase. |
| S17 | Turning a wave into numbers | 4 min | It explains *sampling* — the first of the two big ideas — with a picture everyone understands: a film camera. |
| S18 | Too few frames, wrong answer | 3 min | It explains *aliasing* — the danger of sampling too slowly — with the wagon-wheel effect from old films. |
| S19 | The problem one number cannot solve | 4 min | It creates a question in the audience's mind, so that the next slide — I and Q — feels like the answer, not like extra theory. |
| S20 | I and Q — two numbers, and now you know ★ | 5 min | This is the concept the rest of the day depends on. |
| S21 | What your sample rate buys you | 3 min | It connects sample rate to the amount of spectrum you can see — the key to Lab 05 (recording a whole slice of the band). |
| S22 | Three units you will see all afternoon | 2 min | dB, dBm and dBFS appear on every display. |
| S23 | Gain is not volume | 1 min | It prevents the most common beginner mistake — turning the gain to maximum — before people see a gain slider in the next segments. |

**Segment 4 — The hardware: SignalSDR Pro (15 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S24 | The SignalSDR Pro — pass it round | 3 min | Holding the radio makes it real. |
| S25 | Two chips do everything | 3 min | It connects the real board to the "shortened chain" of slide 9. |
| S26 | The numbers, translated | 3 min | Specifications mean nothing to beginners until they are translated into things they can do. |
| S27 | Why your screen will say "B210" | 2 min | It prevents confusion when the software shows a different name, and gives people the most useful search word. |
| S28 | Two things that will bite you | 3 min | It warns about the two most common set-up problems *before* people meet them, so the error in ten minutes looks expected. |
| S29 | The cheapest part that matters most | 1 min | Antennas decide what you can receive. |
| S30 | Break | 10 min | People need rest, and you need time to prepare Segment 5. |

**Segment 5 — Making it work, live, from cold (25 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S31 | Four commands | 3 min | It shows that installing everything is short. |
| S32 | Order matters | 2 min | Repeats the boot order as four clear steps, because it is the first thing that goes wrong at home. |
| S33 | Live — the radio answers | 6 min | Watching a machine introduce itself turns it from a mystery box into something understandable. |
| S34 | Live — the failure, and the fix ★ | 8 min | Every person in the room will meet this error alone, at night, with nobody to ask. |
| S35 | Take this with you | 3 min | The handout card is what people will actually use on Monday. |
| S36 | It is all written down | 3 min | It tells people where the full setup documents are, and removes the pressure to remember. |

**Segment 6 — Your first flowgraph, built in front of you (25 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S37 | GNU Radio Companion | 3 min | It introduces the tool before you use it, so people know where to look on the screen. |
| S38 | Live build — three blocks and a radio ★ | 13 min | This is the emotional peak of the day: a radio, built from nothing, plays music. |
| S39 | Break it on purpose | 8 min | Hearing what each mistake sounds like teaches people to diagnose problems by ear. |
| S40 | Three blocks | 1 min | A short, memorable summary before the break. |
| S41 | Break | 10 min | Rest, and time for you to prepare eight demos in a row. |

**Segment 7 — What it can do: the lab tour (40 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S42 | Twelve labs, one ladder | 2 min | It shows the whole course as one ladder, so the repository feels finishable, not enormous. |
| S43 | Labs 02–03 — instruments, then control | 5 min · live | It shows how Lab 01 grows. |
| S44 | Lab 04 — stereo, built from scratch | 4 min · live | It reveals a hidden part of a familiar signal (the 19 kHz pilot), and shows that a whole chip in their car radio is just a few blocks here. |
| S45 | Lab 05 — record once, experiment forever | 5 min · live | Recording raw signals is the habit that separates people who make progress from people who keep going back outside. |
| S46 | Lab 06 — one tuner, many modes | 4 min · live | It connects SDR to the scanners many people in the room use, and shows that a "mode" is just a different set of blocks. |
| S47 | Lab 07 — crossing into digital | 5 min · no radio | It introduces the constellation — the picture used for every digital signal — and shows that measured results match theory exactly. |
| S48 | Lab 08 — hidden data | 5 min · live | It is usually the best "I had no idea" moment of the day: text data hidden inside ordinary FM radio. |
| S49 | Lab 09 — aircraft | 5 min | Decoding real aircraft positions is exciting, and it shows the same board working in a completely different band and modulation. |
| S50 | What did all of those have in common? | 3 min | It ties the tour back to the one-sentence version from slide 15. |
| S51 | And 589 more | 2 min | It shows the size of the field, and — if you prepare — connects it to the audience's own work. |

**Segment 8 — Transmitting: a television station (25 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S52 | Receiving is legal almost everywhere. Transmitting is not. | 4 min | It sets the rules *before* the exciting part. |
| S53 | We built a television station | 2 min | It states the headline result simply, so the audience knows where this segment is going. |
| S54 | From a video file to a radio wave | 3 min | One quick look at the chain, so the demo makes sense. |
| S55 | Demo — scan the band | 5 min · receive only | It shows a real measuring tool — and a great story about an instrument that was confidently wrong. |
| S56 | Demo — a picture, down a cable | 5 min · transmits | The live result: video sent by one software radio and received and played by software, in real time. |
| S57 | Two things that went wrong ★ | 4 min | Two stories with lessons that apply far beyond radio. |
| S58 | What you may actually do | 2 min | It ends the transmit segment with a clear, legal path, so people leave with the right habit. |

**Segment 9 — Where to go next (15 minutes)**

| Slide | Title | Time | Why it is there |
|---|---|---|---|
| S59 | The path, in order | 3 min | Order matters. |
| S60 | Your first week ★ | 4 min | A dated plan turns "that was interesting" into "I opened the laptop on Monday". |
| S61 | The five mistakes everyone makes | 3 min | A quick checklist that covers most "my SDR does not work" problems. |
| S62 | When you get stuck | 2 min | It points to the reference material, especially the glossary, so people are never stopped by an unknown word. |
| S63 | Questions | 3 min or more | You promised to answer the parking-lot questions. |

---

## 5. Hands-on variant for Segments 5–6

If attendees bring laptops, the session can become participatory — but **only** under these
conditions, and the plan above stays the default:

| Requirement | Why |
|---|---|
| **Software pre-installed before they arrive** | Installing GNU Radio for 20 people on venue wifi will consume an hour and you will not get it back. Send instructions a week ahead and offer a pre-session clinic. |
| **One radio per 3–4 people, minimum** | Below that, most of the room watches someone else's screen, which is worse than watching yours — it is the same passivity with a worse view. |
| **+15 minutes**, taken from Segment 7 (drop S44 and S46) | Everything takes longer when 20 people do it. This is not pessimism, it is arithmetic. |
| **A floating assistant** | One person who does nothing but unstick individuals. Without this, you stop presenting and start doing desk support, and the schedule dies. |
| **Pair beginners with intermediates** | §2, mechanism 4. |

**Recommendation: do not try hands-on the first time you teach this.** Run it as demos, learn
where this audience really gets stuck, then build the hands-on version with that knowledge. A
smooth demo session wins over more beginners than a chaotic hands-on one.

---

## 6. Demo risk management

Live SDR demos fail in front of an audience for reasons that never happen at your desk. In order
of how much they help:

1. **Every live demo has a recorded fallback** — a screen capture of that same demo working,
   full-screen, one keystroke away. If a demo has not recovered in **30 seconds**, switch to the
   recording, say "here's one I prepared earlier", and keep moving. Never debug in front of a
   classroom: you lose the schedule, and with beginners you lose the belief that this is doable.
   *(The one exception is S34, where the failure is the lesson.)*
2. **Pre-flight every demo in the actual room**, on the actual power and network, within an hour
   of starting. Laptop on mains, performance power profile, sleep disabled, notifications off.
3. **Rank demos by dependence on the outside world:**
   | Demo | Depends on | Risk |
   |---|---|---|
   | Labs 01–04, 06 (FM) | a strong local FM station | **low** — FM is everywhere |
   | Lab 07 (BPSK) | nothing at all | **none** — no radio needed |
   | Lab 05 (record/playback) | a file you made earlier | **none** if recorded beforehand |
   | Lab 04 (stereo) | a *music* station | low — talk stations carry almost no stereo |
   | Lab 08 (RDS) | a station actually transmitting RDS | medium — **verify the exact station the day before** |
   | Lab 09 (ADS-B) | a 1090 MHz antenna *and* aircraft in range | **high** — never yet received at the lab; keep the test capture loaded |
   | Labs 10–12 (TV) | your own transmitter + cable | medium — pre-build the transport stream; the cable setup must be rehearsed |
4. **Pre-build every artefact**: the IQ recording for Lab 05, the transport stream for the TV
   demo, the synthetic captures for Labs 08 and 09. Generating live is slow, boring to watch,
   and is where failures hide.
5. **Two machines if you can.** One drives the projector, one stays on the terminal — and a
   single crash then does not end the session.
6. **Leave the radio powered from the first break onward.** Re-plugging costs 30 seconds of dead
   air every time.
7. **Run the offline test suite the day before**, on the presenting laptop:

   ```bash
   cd 03_scripts && python3 test_labs_offline.py
   ```

   It runs the real flowgraphs of Labs 01–06, 08 and 09 on test signals with known answers (about
   a minute, no radio needed) and would have caught both demo-breaking bugs found in September
   2026: Lab 03's squelch that could never close (S43 leads with squelch) and Lab 04's stereo
   decoder that was effectively mono (S44). All nine checks should say PASS.

---

## 7. The transmit demo — a recommendation, not a preference

Segment 8 is the most exciting part of the day — and the only part with legal risk.

**Demonstrate over a cable — SMA from transmitter to receiver through a 30–40 dB attenuator,
with no antenna on the transmitter.** (Lab 12's README allows 20–30 dB. In a classroom, start
with 40 dB: the transmitter has plenty of spare gain, and the receiver cannot be overloaded.) Three independent reasons:

- **Legal.** Labs 10 and 12 use frequencies licensed to TV broadcasters (in Malaysia, MYTV). A
  classroom is not a shielded room, and a room full of people is not the place to find out how
  far "five metres" really reaches.
- **Technical.** Over the air, the first attempt decoded nothing; it needed 19 dB more transmit
  gain before it delivered 79,357,996 bytes with zero errors (Lab 12). A cable with an attenuator
  gives the receiver a strong, steady signal with far less transmit power. (That perfect result
  was measured over a short, controlled air path; **rehearse the cable version before the day** —
  DEMO_RUNSHEET.md has the steps.)
- **Teaching.** It shows the professional habit at the moment the audience is most impressed.
  **Beginners copy what they see the expert do** — so they should see an attenuator, not an
  antenna.

If the venue genuinely has a screened enclosure, an over-the-air run is a fine finale — but
schedule the cable demo and treat the other as a bonus.

---

## 8. Materials to prepare

| Item | Notes |
|---|---|
| **Slide deck** | [`intro_to_sdr.html`](./intro_to_sdr.html) — 63 slides, speaker notes built in. One file, no internet needed. |
| **Setup checklist card** | Ready to print: [`handout_cards.html`](./handout_cards.html), page 1 — the four commands, plug-in order, the firmware-image fix, the five mistakes, the first week. The thing they keep. |
| **Glossary card** | Page 2 of the same file — the 15 terms actually used today, not all 248: IQ, dBFS, MSPS, bandwidth, sample rate, gain, AGC, squelch, FFT, waterfall, constellation, flowgraph, block, duplex, transport stream. |
| **QR code** | To the repository. Already on S6, on the last slide, and on both cards. |
| **Demo run sheet** | [`DEMO_RUNSHEET.md`](./DEMO_RUNSHEET.md) — the exact command and settings for every live moment, what the room should see or hear, and the fallback. |
| **Fallback recordings** | One per live demo (§6). |
| **Pre-built artefacts** | IQ recording, transport stream, synthetic ADS-B and RDS captures. |
| **Hardware** | SignalSDR Pro ×1 (×2 preferred), FM antenna, **1090 MHz antenna** (for Lab 09), USB-B 3.0 + USB-A-to-C cables, SMA cable, 30–40 dB attenuator, spare SD card. |
| **Room** | 1080p projector; audio the whole room can hear (**test this — half the demos are sound**); power strips; a whiteboard with a parking-lot column. |

---

## 9. What was deliberately cut, and where it went

State this at S3 so nobody feels short-changed:

| Cut | Lives in |
|---|---|
| Fourier transforms, filter design, window functions | `01_fundamentals/01`, `05` |
| Noise figure, Friis, link budgets | `01_fundamentals/06` |
| PLLs, Costas loops, timing recovery | `01_fundamentals/09` |
| CRC, Reed–Solomon, convolutional codes, LDPC | `01_fundamentals/10` |
| OFDM theory, cyclic prefix, PAPR | `01_fundamentals/11` |
| Writing Python blocks, hierarchical blocks | Labs 08–12 source |
| Labs 10–12 in operational detail | their READMEs |

---

## 10. If you have to cut for time

In this order, and no further:

1. **S54** (the chain diagram) — S57's two failure stories carry the segment without it.
2. **S44** (Lab 04 stereo) — fold one sentence into S43.
3. **S46** (Lab 06 multimode) — the least *new* idea after S43.
4. **S12** (fix it with a download) — merge into S11.
5. **S29** (antennas + comparison) — it is on the handout card anyway.

**Never cut:** **S9** (the line through the superhet), **S20** (I and Q), **S34** (the failure
fixed live), **S38** (the live build), **S60** (your first week). These five *are* the session:
the first two are the only ideas that must be understood; the middle two are the proof that it
can be done; and the last one is what turns a good afternoon into someone who actually starts.
