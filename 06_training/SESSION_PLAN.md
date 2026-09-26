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

## 4. Slide-by-slide with speaker notes

> Notes are what to **say**, not what is on the slide. Slides carry one picture and at most six
> words. Anything with a paragraph on it belongs in the repo, not on a wall.

### Segment 1 — Why you are here (15 min)

**S1 · Title — "Introduction to Software-Defined Radio"** *(1 min)*
> Subtitle names the hardware and the date. While people settle, have a waterfall already
> running on the second screen. The room should see a radio working before you say a word —
> and for a beginner audience that first image does more than any slide can.

**S2 · The promise: what you will be able to do by the end of today** *(3 min)*
> Four bullets, all verbs: *set one up, build one, break one, know what to read next.* Then say
> plainly: "You will not be an SDR engineer by the end of today. You will be someone who can start."
> **For a beginner room this sentence is not modesty, it is permission** — it removes the fear
> of being the person who doesn't keep up.

**S3 · What this session is not** *(2 min)*
> Name the cuts out loud: no mathematics, no filter design, no coding required today. Then
> show the repo's scale — 12 fundamentals documents, 12 labs, 589 catalogued applications.
> "Today is the map. The territory takes months, and it is all written down for you."

**S4 · Who is in the room** *(3 min)*
> Show of hands, three questions, asked in ascending order so nobody is exposed by the first:
> *(i)* who has used a scanner, walkie-talkie or shortwave set? *(ii)* who has looked at a
> radio's spectrum on any instrument? *(iii)* who has written any code, in any language?
> **Act on answer (iii) per §2.** Thank every hand; count out loud; move on quickly.

**S5 · The shape of the day** *(3 min)*
> Walk the four blocks: *ideas → hardware → make it work → what it can do.* Tell them where
> the breaks are. People relax once they know when they can check their phone, and a relaxed
> beginner asks questions.

**S6 · The repository is the course; today is the trailer** *(3 min)*
> QR code up. Tell them to photograph it **now**, not later. Everything demonstrated today is a
> folder they can open tonight, and every command is in a README. For a beginner this is the
> single most reassuring slide of the morning: nothing they see will be lost.

---

### Segment 2 — What a radio does, and what SDR changes (30 min)

**S7 · What every radio has to do — four jobs** *(3 min)*
> Before any block diagram. *Catch* the wave, *select* the one you want out of thousands,
> *extract* the information, *present* it. Every radio ever built does these four things —
> a crystal set, their handheld, a phone, a satellite terminal. **Nothing here is SDR yet.**
> This slide exists so that the next two have somewhere to attach.

**S8 · Inside the radio on your desk — six boxes of metal** *(5 min)*
> Now the superheterodyne chain: antenna → filter → amplifier → mixer → IF filter → detector →
> speaker. Walk it left to right and tie each box to one of the four jobs from S7. Say the key
> property out loud: **each box is a physical part, chosen and soldered for one purpose, and
> changing what the radio does means changing the metal.** Do not ask them to name the boxes.
> *Depth box: "this is a superheterodyne receiver, 1918, and it is still in your car."*

**S9 · The same radio, with one line moved — `images/sdr_vs_superhet.svg`** *(5 min)*
> **The keystone slide of the whole session.** The analogue-to-digital converter slides from
> the far right of the chain to just after the mixer. Everything to its right stops being
> copper and becomes code. Say it slowly: **"The hardware didn't get smarter. It got shorter."**
> Then pause. If one idea survives to next week, this is the one you want it to be.

**S10 · What the software actually replaces** *(3 min)*
> Map each deleted box to its software equivalent, one line each — IF filter becomes a list of
> numbers; the detector becomes a function; the tuning knob becomes a variable. Stress the
> reassuring part for a beginner: **these are the same operations, not new physics.** SDR is
> the radio they already know, written down differently.

**S11 · Consequence 1 — one box, many radios** *(3 min)*
> Their world today: one device per job, each one obsolete when the standard changes. Today
> they will watch one board be an FM receiver, a data decoder, an aircraft tracker and a
> television transmitter — with no soldering iron anywhere near it.

**S12 · Consequence 2 — you fix it with a download** *(2 min)*
> One example they lived through: when television went from analogue to DVB-T, every receiver
> in the country became scrap. With SDR that is a software update. Keep it to the example; the
> industry-economics argument is for the intermediates and belongs in a depth box.

**S13 · Consequence 3 — radio becomes visible** *(4 min · live)*
> Live waterfall on the projector, no explanation, just look at it. Tune slowly across the FM
> band. Their radio told them *one number*; this shows the whole band at once, with history
> scrolling down the screen. **Highest-impact minute in the segment — do not talk over it.**
> Then name what they are seeing: bright vertical stripe = a station, dark gaps = empty air.

**S14 · What SDR is genuinely bad at** *(3 min)*
> Credibility slide; do not skip it. It needs a whole computer. It struggles when a very strong
> signal sits next to a very weak one. It is slower to respond than purpose-built hardware.
> **"Your handheld still wins on the roadside, and that is fine."** A beginner who is told only
> the good parts stops trusting you the first time something fails.

**S15 · The one-sentence version** *(2 min)*
> *"Turn the radio wave into numbers as early as you can, then do everything else in software."*
> Everything in the remaining three hours is a consequence of that sentence. Come back to it
> at S50.
> **Check the room (1 min):** "In the picture a few slides ago, what moved?" Wait for *the
> converter* (or *the ADC*). If nobody says it, show S9 again for thirty seconds.

---

### Segment 3 — The two ideas you cannot skip (25 min)

> **Slow down here.** This is the only segment where a beginner can be permanently lost, and
> the only one where being lost matters — every later screen is a picture of what happens here.

**S16 · A wave, and the three numbers that describe it** *(3 min)*
> Amplitude (how big), frequency (how fast), phase (where in the cycle it starts). Draw a sine.
> Connect to something they own: **frequency is the number on the dial.** No mathematics.

**S17 · Turning a wave into numbers — sampling** *(4 min)*
> Dots on the sine at regular intervals. That is all an ADC does: measure, write down, repeat,
> millions of times a second. The numbers *are* the radio signal now. For beginners, the
> analogy that works is a film camera: frames, not continuous motion.

**S18 · When there are too few dots** *(3 min)*
> Aliasing, via the wagon wheel in old films that appears to spin backwards. Same effect, same
> cause. Conclusion only: **sample fast enough or you will recover the wrong wave.**
> *Depth box: "sample rate > 2× bandwidth — Nyquist → fundamentals/05."* Do not derive it.

**S19 · The problem one number cannot solve** *(4 min)*
> A photograph of a fan blade tells you where the blade is — **not which way it is spinning.**
> A single measured number has exactly this problem: a signal 10 kHz above where you are tuned
> and one 10 kHz below look identical. Their existing radios solved this with hardware they
> never had to think about. **Let the discomfort sit for a beat before S20 resolves it.**

**S20 · I and Q — two numbers, and now you know** *(5 min)*
> Two measurements taken a quarter-cycle apart: together they give position *and* direction of
> rotation. Draw the rotating vector; animate it if you can. I is the horizontal part, Q the
> vertical. **This is the concept the entire day rests on** — every screen from here on is a
> stream of these pairs. Say explicitly: "If you only read one thing from the repo, read
> `01_fundamentals/02_iq_sampling.md`."

**S21 · What your sample rate buys you** *(3 min)*
> Because there are two numbers per sample, bandwidth ≈ sample rate. 20 million samples per
> second means 20 MHz of spectrum, all at once. Translate for the room: **"that is the entire
> FM band, every station in it, captured in one go."**

**S22 · The units on every screen today** *(2 min)*
> dB is a comparison. dBm is an actual power. dBFS is *how full the ADC is.* The one to hammer
> is **dBFS: a ceiling you must not hit**, because clipping is a failure mode they have never
> had to watch for on an ordinary radio.

**S23 · Gain is not volume** *(1 min)*
> Turning gain up amplifies the noise too, and past a point only adds distortion. It is the
> mistake every newcomer makes on day one. Beginners especially need this said before Segment 5,
> because they will reach for the slider.
> **Check the room before the hardware** (2 min, only if the pacing indicator says you are on
> time). Hands up, no wrong answers: *Why two numbers, I and Q?* (to tell a signal above the
> tuning from one below) · *What happens at 0 dBFS?* (clipping) · *Does more gain always help?*
> (no). If a question gets silence, answer it in one sentence and point at the slide. Do not
> re-teach the segment.

---

### Segment 4 — The hardware: SignalSDR Pro (15 min)

**S24 · The board — and pass one round** *(3 min)*
> Hand a unit into the room while you talk. Credit-card sized. Let them hold it next to any
> radio they brought. Physical contact does more for a beginner audience than three slides.

**S25 · Two chips do everything — `images/signalsdr_pro_block_diagram.svg`** *(3 min)*
> The AD9361 is the entire radio front end — both the tuning and the analogue-to-digital
> conversion from S17 — on one chip. The Zynq moves the data and keeps time. **Everything else
> on the board is connectors and power.** Point back to S9: this is that shortened chain, real.

**S26 · The numbers that matter, translated** *(3 min)*
> 70 MHz–6 GHz, up to 56 MHz at once, two channels, **full duplex**. Translate every one:
> the tuning range runs from just below the FM band (70 MHz) to Wi-Fi (6 GHz) — shortwave is
> below it, and someone will ask; full duplex means transmit and receive at
> the same instant, which is what makes the last demo of the day possible at all.

**S27 · Why it says "B210"** *(2 min)*
> It loads firmware that makes it answer as a USRP B210, so every existing tutorial, block and
> example works unmodified. For a beginner the point is practical, not clever: **when you
> search the internet for help tonight, search for "B210".**

**S28 · Two things that will bite you** *(3 min)*
> (1) **Boot order** — power first, wait 30 seconds while it boots an operating system from its
> SD card, *then* the data cable. (2) **The firmware-image error**, which you will meet in ten
> minutes. Foreshadowing it now means that when it appears on screen it reads as competence
> rather than a live failure.

**S29 · Antennas, and how this compares** *(1 min)*
> A good antenna on a cheap radio beats a bad antenna on an expensive one, every time. Flash
> the comparison table (RTL-SDR / HackRF / B210 / SignalSDR Pro) without dwelling —
> *depth box → `01_fundamentals/00` §5 and `05_reference/03_antennas.md`.*

---

### ☕ BREAK — 10 minutes
> **Use it.** Leave the FM receiver running with the waterfall up so people drift back to a
> moving screen. Pre-flight the Segment 5 terminal now. Circulate — this is where beginners ask
> the question they were too shy to raise.

---

### Segment 5 — Making it work, live, from cold (25 min)

**S31 · Four commands** *(3 min)*
> `apt install`, `uhd_images_downloader`, `usermod`, log out and back in. Say what each did in
> one line — especially that group membership only takes effect on a fresh login, which is the
> number-one "it worked yesterday" support call.

**S32 · Plug-in order** *(2 min)*
> Power → 30 seconds → data → antenna. Say why: **it is booting a computer, not powering a
> peripheral.** Treating it like a USB stick is what makes it "not detected".

**S33 · 🖥️ LIVE — the radio answers** *(6 min)*
> Terminal, full screen, large font. `uhd_find_devices`, then `uhd_usrp_probe`. Read the serial
> number aloud. Walk **one** branch of the probe output so they see the radio describing its own
> gain range and sample rates — for a beginner, seeing a machine introduce itself is the moment
> it stops being a mystery box. Do not walk the whole tree.

**S34 · 🖥️ LIVE — and now the failure** *(8 min)*
> **Deliberately induce `Could not find path for image: usrp_b200_fw.hex`.** The tested way,
> which changes nothing on the laptop, is to point the driver at an empty folder:
> `mkdir -p /tmp/no_images` then `UHD_IMAGES_DIR=/tmp/no_images uhd_usrp_probe`. Say honestly
> that you did this — "I sent the driver to the wrong folder, which is exactly what having two
> versions does." (Your screen may show the newer wording, *Could not find the image
> 'usrp_b200_fw.hex' in the image directory*. Same problem.) Then run
> `00_setup/fix_uhd_version_conflict.sh`, which checks that every installed driver version can
> find the files, and re-run `uhd_usrp_probe` without the variable. It works.
> **The most valuable slide in the deck and the one most likely to be cut for time. Do not cut
> it.** Every person in the room will meet this error alone, at night, with nobody to ask — and
> the difference between someone who quits and someone who continues is having watched it fixed
> once, calmly, by a person who expected it.

**S35 · The setup checklist card** *(3 min)*
> Hand out the one-page card (§6). It is the artefact that outlives the session, and for a
> beginner it is the difference between trying again on Monday and not.

**S36 · Where the setup documents live** *(3 min)*
> `00_setup/01` through `06`, plus troubleshooting. Tell them document 06 exists and is the one
> they will need. Say the sentence: **"You are not expected to remember any of this."**

---

### Segment 6 — Your first flowgraph, built in front of you (25 min)

**S37 · What GNU Radio Companion is** *(3 min)*
> A diagram editor that produces a working radio. Block list on the left, canvas in the middle,
> run button at the top. Thirty seconds each, no menu tour. Frame it in their terms: **"you are
> going to draw the block diagram from slide 8, and it will play music."**

**S38 · 🖥️ LIVE BUILD — Lab 01 from an empty canvas** *(13 min)*
> Build it in front of them, narrating every single choice, with Lab 01's exact values so they can
> repeat it tonight: **USRP Source** (sample rate `1e6`, your station's frequency, gain `40`,
> antenna `TX/RX`, **bandwidth `1e6`**) → **WBFM Receive** (quadrature rate `1e6`, audio
> decimation `20`) → **Audio Sink** (`50000`). Three blocks. Say the only arithmetic aloud:
> 1,000,000 ÷ 20 = 50,000. While typing the bandwidth, tell the story: this one empty box cost the
> course 18.6 dB in Lab 01 until it was measured (VERIFICATION Lesson 1). Name each block's job by
> pointing back at S8's metal box that it replaces. Press play. **Music comes out of the laptop.**
> Stop talking for three seconds. This is the emotional peak of the day.
> Then show the generated Python for ten seconds only: *"the diagram is the program"* — enough
> to intrigue the intermediates, not enough to frighten anyone else.

**S39 · 🖥️ LIVE — break it on purpose** *(8 min)*
> Three deliberate faults, each with a sound they can learn to recognise: Audio Sink `25000`
> instead of `50000` → slow, deep and jumpy, with `O` letters in the terminal; tune to an empty
> frequency → a loud rushing hiss (which leads straight to *squelch* in Lab 03); gain to maximum →
> overload and distortion, then gain to zero → hiss. **Rehearse all three** — how each sounds
> depends a little on the station and the laptop. **Teaching the *sound* of each mistake is worth more than any slide about it**, and it
> is the single best use of recovered time if S4 told you the room is more capable than expected.

**S40 · What you just watched** *(bridging, ~0 min)*
> Three blocks. Everything after this is more blocks. Say it and move straight into the break.

---

### ☕ BREAK — 10 minutes

---

### Segment 7 — What it can do: the lab tour (40 min)

> **Rule for this segment: 4–5 minutes per lab, hard-stopped.** You are demonstrating *range*,
> not depth. Deep question → one sentence, name the document, parking lot, move.
> This is the segment that re-levels a mixed room: nobody has seen most of this.

**S42 · The arc** *(2 min)*
> The ladder diagram from the README. Analogue → recorded → many modes → digital → real data →
> other bands → transmit. Each lab adds exactly one new idea to the one before.

**S43 · Labs 02–03 — instruments, then control** *(5 min · live)*
> Spectrum, waterfall, sliders; then automatic gain control and squelch. "The same radio you
> watched me build, plus instruments." **Squelch is the one they will recognise from their own
> equipment** — lead with it and let them name it.
> *Depth box: on the real radio, Lab 03's squelch first would not go quiet — the radio's own
> centre spike was as strong as the station. A DC Blocker fixed it (VERIFICATION Lesson 12).*

**S44 · Lab 04 — stereo, built from scratch** *(4 min · live)*
> Point at the 19 kHz pilot tone on the spectrum. Then the punchline: **nobody bought a stereo
> decoder chip.** That part of their car radio is, here, a few blocks on a canvas.
> **Use a music station at gain about 55** — talk stations carry almost no stereo, and at gain 40
> the pilot stood only 11 dB above the noise here (27 dB at 55).

**S45 · Lab 05 — record once, experiment forever** *(5 min · live)*
> Record 2 MHz of raw signal (several stations, 16 MB a second), then **unplug the antenna** and
> retune inside the recording. Pitch it as the most practically useful lab in the repository: it separates going
> outside from working on the data, and it is the habit that distinguishes people who make
> progress from people who keep re-collecting.

**S46 · Lab 06 — one tuner, many modes** *(4 min · live)*
> AM, narrowband FM, wideband FM, channel selection, signal meter. **Their scanner, in
> software** — and now they can see on screen why it does what it does. Only wide FM is sure to
> have a signal in the room; show the other modes' controls, but do not promise a voice.

**S47 · Lab 07 — crossing into digital** *(5 min · no hardware)*
> Constellation diagram: two dots (BPSK sends +1 or −1). Add noise, watch the dots smear into clouds. Then the
> punchline for the intermediates, stated simply enough for everyone: the measured error rate
> lands exactly on the textbook curve. **"The mathematics is not an approximation of this
> system. It is this system."** No radio needed — say so, because it means they can try it
> tonight with no hardware.

**S48 · Lab 08 — hidden data in a signal they have heard all their lives** *(5 min)*
> RDS. The station name appears — carried on a subcarrier inside a broadcast they have listened
> to for years without knowing it was there. **Best "I had no idea" moment of the day for a
> beginner audience.** Check the station the day before: at the lab only BFM 89.9 sent RDS, and
> only its name (no song titles). Tune 200 kHz beside it with the matching offset. Run from file
> if the band is weak in the room.

**S49 · Lab 09 — aircraft** *(5 min)*
> 1090 MHz: aircraft identity, altitude, position, decoded from raw samples. A crowd-pleaser —
> **but only with a 1090 MHz antenna and aircraft in range.** The FM whip heard nothing at
> 1090 MHz (VERIFICATION Lesson 4), and no real aircraft has been decoded at the lab yet. Check in
> rehearsal; if none appear, use the test capture **and say so** — the decoding is the same.

**S50 · What all of those had in common** *(3 min)*
> One board. One driver. One toolkit. Different *files*. Re-read S15's sentence aloud and let
> the room notice they now hear it differently than they did before the first break.

**S51 · And 589 more** *(2 min)*
> Flash the applications catalogue: weather satellite images, ships, GPS, LoRa sensors, radio
> astronomy. **Name three that suit this specific room's day job** — prepare them in advance.

---

### Segment 8 — Transmitting: a television station (25 min)

**S52 · Receiving is legal almost everywhere. Transmitting is not.** *(4 min)*
> Open on the constraint, not the capability — especially with beginners, who will not yet have
> an instinct for this. Spell out the words the first time: **MCMC** (the Malaysian
> Communications and Multimedia Commission, the regulator); licensed broadcast spectrum; the
> **Class Assignment** (MCMC's list of bands anyone may use at low power, without a licence). Then state what
> today's demo does: **a cable from transmitter to receiver through an attenuator, no antenna
> fitted**, and one line on why (see S56).

**S53 · What we built** *(2 min)*
> A DVB-T2 television transmitter that a consumer television found on a channel scan and played.
> Not a simulation — an ordinary TV, an ordinary channel scan, a picture.

**S54 · From a video file to a radio wave** *(3 min)*
> Ten seconds per stage, no more. Say honestly that the theory behind the last two boxes is a
> whole document (`01_fundamentals/11`) they should read another day — admitting what you are
> skipping is what keeps a beginner from feeling lost. **First slide to cut in this segment.**

**S55 · 🖥️ DEMO — scan the band** *(5 min)*
> `scan_tv_band.py` (about 40 s for channels 21–48): a table classifying each channel as
> television, some other signal, or empty. The slide shows the lab's real result — no TV reached
> the FM whip, only a bursty signal on channel 22. Your venue will differ; if MYTV appears, point at it. Then tell the false-positive story — a non-TV signal scored 13.9× on the detector,
> because **a burst of noise overlaps itself at any delay you test.** Two extra checks fixed it.
> Good beginner-accessible teaching about instruments that lie confidently.

**S56 · 🖥️ DEMO — a picture on the screen** *(5 min)*
> Transmit over the cable, video window on the projector. Then the measurement behind it:
> spreading the same power across thousands of carriers costs about **35 dB** versus a single
> tone, so over the air this needed **19 dB more gain** than intuition suggested — and then
> delivered 79 million bytes with none wrong. A cable does the same with far less power, and
> sends nothing into the room. **Rehearse the cable setup end to end:** the lab's perfect result
> was measured over a short, controlled air path, not yet over a cable.

**S57 · Two things that went wrong, and what they taught us** *(4 min)*
> Keep this even if you are late — cut S53 instead. Two stories, ~2 minutes each:
> - A receiver whose output looked **100 % healthy and was complete garbage inside**, because the
>   part that writes the "this is fine" marker writes it no matter what. *A green light can be
>   structurally incapable of reporting the fault.*
> - A picture that played perfectly but **sluggishly**, because replaying a finished file sent
>   the broadcast clock backwards three and a half minutes every lap. *A perfect stream of bits
>   is not a working television service — broadcasting is a timing system that happens to carry
>   bits.*

**S58 · What you may actually do** *(2 min)*
> Licence-exempt bands; amateur licensing as the legitimate route to transmitting; dummy loads
> and attenuators; `05_reference/04_malaysia.md`. Close firmly: **receive freely, transmit only
> where you are permitted.**

---

### Segment 9 — Where to go next (15 min)

**S59 · The path, in order** *(3 min)*
> QUICKSTART → introduction → fundamentals 01–04 → Labs 01–04 → then each lab pulls in the
> document it needs. Stress that the order carries weight and that skipping ahead is the usual
> reason people stall and give up.

**S60 · Your first week** *(4 min)*
> A concrete five-evening plan: *Mon* setup + QUICKSTART; *Tue* fundamentals 01–02; *Wed* Labs
> 01–02; *Thu* Lab 03 + fundamentals 03–04; *Fri* Lab 05 — record your own band.
> **For a beginner audience this is the most important slide after S34.** Vague encouragement
> produces nothing; a dated plan produces someone who actually opens the laptop on Monday.

**S61 · The five mistakes everyone makes** *(3 min)*
> Gain at maximum. No antenna, or the wrong one. Wrong sample rate. Expecting a weak signal
> indoors. Skipping the fundamentals and then blaming the radio.

**S62 · Resources** *(2 min)*
> The 248-term glossary — tell them explicitly it is written plain-English-first, because a
> beginner's worst hour is the one spent stuck on an acronym. Signal identification guide,
> antenna reference, applications catalogue, local community. QR code again.

**S63 · Q&A** *(3 min+, absorbs the buffer)*
> Clear the parking lot first — it proves you were listening and it is what you promised the
> intermediates. Last line: **"Everything you saw today is a folder you now have."**

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
