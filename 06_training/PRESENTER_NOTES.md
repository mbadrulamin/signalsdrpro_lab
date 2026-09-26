# 🎤 Presenter Notes — Introduction to Software-Defined Radio

> **What this is:** the full notes for every one of the 63 slides — what the slide is for, the
> words you can say, what to do, the questions people ask, and the background you need to answer
> them. Read it through once, slowly, a few days before you present.
> **Before this:** [`README.md`](./README.md) (how to run the deck) and
> [`SESSION_PLAN.md`](./SESSION_PLAN.md) (why the session is shaped this way).
> **Also:** [`DEMO_RUNSHEET.md`](./DEMO_RUNSHEET.md) has the exact commands for every live demo.
> **Time:** about 90 minutes to read. Reading it aloud once is the best rehearsal you can do.

---

## How to use these notes

Every slide has the same parts:

| Part | What it gives you |
|---|---|
| **Why this slide is here** | The one job of the slide. If you remember nothing else, remember this |
| **Say it like this** | Words you can say, in full sentences. Use them as they are, or put them in your own words. Your own words are better, as long as the meaning stays |
| **Do** | What to click, show, or wait for |
| **If someone asks** | The questions people really ask here, with short answers |
| **Background for you** | The deeper explanation, for you only — so you are confident. Do not read it out |
| **Next** | A sentence that takes you smoothly to the next slide |

Some parts are left out when a slide does not need them.

**The same notes appear in the speaker view.** Press <kbd>S</kbd> in the deck, and the notes for
the current slide appear in a second window, with a clock that tells you if you are early or
late. The speaker view and this file are always the same, because
`03_scripts/sync_speaker_notes.py` copies this file into the deck. If you change these notes,
run that script afterwards.

**Three habits that make any session better:**

1. **Pause after the important sentences.** Beginners need two or three seconds to think. Silence
   feels long to you; it does not feel long to them.
2. **Point at the screen when you say "this".** Half the room is looking at you, not the slide.
3. **Repeat every question before you answer it.** The back of the room did not hear it, and it
   gives you three seconds to think.

---

# Segment 1 — Why you are here (15 minutes)

## S1 · Title (1 min)

**Why this slide is here.** The room should see a radio working before you say a word. A moving
picture does more for a beginner audience than any sentence.

**Do.** Before people arrive, start the live waterfall on the second screen (or switch to it
while people settle):

`uhd_fft -f 98e6 -s 20e6 -g 40 -A TX/RX`

Leave it running. Do not explain it yet — slide 13 explains it.

**Say it like this:**

> "Good morning, and welcome. Today is an introduction to software-defined radio — building radios
> out of software. You do not need any experience in radio design, mathematics or programming.
> There is nothing to memorise: everything you see today is written down for you to take home.
> The moving picture on the other screen is a real radio, receiving right now, in this room. By the
> end of today you will know what it is showing."

**Background for you.** The picture is a *waterfall*: frequency goes across, time goes down, and
brightness is signal strength. The bright vertical stripes are FM stations between 88 and 108 MHz.
A thin line exactly in the middle is the radio's own leakage, not a station (Lesson 12 in
`VERIFICATION.md`).

**Next:** "Let me tell you exactly what you will be able to do by the end of today."

---

## S2 · The promise (3 min)

**Why this slide is here.** It tells people what success looks like, so they can relax. For a
beginner, knowing that nobody expects them to become an expert today is permission to try.

**Say it like this:**

> "By the end of today you will be able to do four things. First, set one up — go from a box to a
> working radio, including the error message that almost everybody meets, and how to fix it.
> Second, build one — you will watch me draw a complete radio receiver as a diagram, and it will
> play music. Third, break one — you will hear what the common mistakes sound like, so you can
> recognise them at home. And fourth, know what to read next, and in what order."
>
> "I want to be honest about one thing. You will not be an SDR engineer at the end of today. You
> will be someone who can start. That is the goal — and it is enough."

**Do.** Reveal the last line only after the four points. Pause after "someone who can start".

**If someone asks:**

- *"Do I need to know programming?"* — "No. Today there is no coding at all. The labs use a
  drawing tool. Later, some labs show Python, but you can go a long way without it."

**Next:** "Just as important is what we will *not* do today."

---

## S3 · What this session is not (2 min)

**Why this slide is here.** It removes fear. Beginners worry about mathematics; saying clearly
that there is none today keeps them listening. It also shows that the material exists, so nobody
feels short-changed.

**Say it like this:**

> "Today there is no mathematics on the slides, no filter design, and no coding. And I will not try
> to cover everything — four hours cannot. Instead, today is a map. Everything behind the map is
> written down: twelve fundamentals documents that teach the theory from zero, twelve labs where
> each one adds exactly one new idea, and a catalogue of 589 other things you can do with this
> radio. Today is the map. The territory takes months — and it is all written down for you."

**If someone asks:**

- *"Where is the mathematics, then?"* — "In the fundamentals documents, in folders
  `01_fundamentals`. Each one explains the idea in plain words first, and puts the mathematics in
  a 'Going deeper' section you can open when you are ready."

**Next:** "Before we go on, I would like to know who is in the room."

---

## S4 · Who is in the room (3 min)

**Why this slide is here.** You learn the level of the room, and you adjust the rest of the day
to it. People also feel included when they are asked.

**Say it like this:**

> "Three quick questions — just raise your hand. There are no wrong answers. First: who has used a
> scanner, a walkie-talkie, or a shortwave radio? … Thank you. Second: who has looked at a radio
> signal on any instrument — a spectrum analyser, an oscilloscope, anything? … Thank you. Third: who
> has written any code, in any language, even a little? … Thank you."
>
> "Every answer is the right answer. This session is built for all three groups."

**Do.** Ask the questions in this order — the easiest first, so nobody is embarrassed by the first
one. Count the hands out loud ("about ten … about half"). **Remember the answer to question 3:**

- If almost nobody writes code, slow down at slide 38 (the live build) and explain every field.
- If more than a third write code, go faster at slide 38 and spend the saved minutes on slide 39,
  breaking the radio on purpose. People who code enjoy that part most.

**Next:** "Here is how the day is shaped."

---

## S5 · The shape of the day (3 min)

**Why this slide is here.** People relax when they know the plan — especially when the breaks
are. A relaxed person asks questions.

**Say it like this:**

> "The day has four parts. First, the ideas: what a radio does, and the two ideas you cannot skip.
> Second, the hardware: what is on this board and what the numbers mean. Third, making it work: I
> will set up a radio from cold, in front of you, and then build a receiver. And fourth, what it can
> do: eight labs, and finally a television station."
>
> "There are two breaks — after about one and a half hours, and after about two and a half hours.
> Please ask questions at any time. If a question would take us too far from the plan, I will write
> it on the whiteboard, in the 'parking lot', and I promise to answer everything there before we
> finish."

**Do.** Point to the whiteboard column where you will write parked questions.

**Next:** "The most important thing to know about today is that nothing you see will be lost."

---

## S6 · Today is the trailer. This is the course. (3 min)

**Why this slide is here.** It tells people where everything lives, so they stop worrying about
taking notes and start watching.

**Say it like this:**

> "Everything I show you today is a folder in one repository — a shared collection of files on
> GitHub. Every command I type is written down in a README file next to it. So you do not need to
> write anything down today. Please take out your phone now and photograph this QR code — now, not at
> the end, because at the end everyone is packing up. It is on the last slide too, and on your
> handout card."

**Do.** Wait until most phones are down before moving on. It takes about 20 seconds.

**If someone asks:**

- *"What is a repository?"* — "A folder of files that is kept online, with its whole history. You
  can download it as a ZIP file from the GitHub page — you do not need to learn Git to use it."
- *"Is it free?"* — "Yes. GNU Radio and the driver are free and open source too."

**Next:** "Let us start with the question behind everything: what does a radio actually do?"

---

# Segment 2 — What a radio does, and what SDR changes (30 minutes)

## S7 · What every radio has to do (3 min)

**Why this slide is here.** It gives beginners a simple frame — four jobs — to hang everything
else on. Nothing here is about SDR yet.

**Say it like this:**

> "Every radio ever built does four jobs. It *catches* the wave, with an antenna. It *selects* the
> one signal you want out of the thousands in the air. It *extracts* the information — the voice,
> the music, the data. And it *presents* it to you — through a speaker, or a screen."
>
> "A crystal set from a hundred years ago does these four jobs. The walkie-talkie on your belt does
> them. Your phone does them. A space probe billions of kilometres away does them. Keep these four
> jobs in mind — catch, select, extract, present — because everything today fits into one of them."

**Do.** Go slowly. Point to each job on the diagram as you say it.

**Background for you.** "Select" is the hard job. The air is full of signals at once; a radio
must reject all of them except one, often a million times weaker than its neighbours. Much of
radio engineering is about selecting well.

**Next:** "Now let us look inside a normal radio and see how it does these jobs."

---

## S8 · Inside the radio on your desk (5 min)

**Why this slide is here.** It shows the classic radio as a chain of physical parts. The next
slide changes one thing in this picture, so the audience must understand this picture first.

**Say it like this:**

> "This is what is inside almost every radio you have owned. The signal goes from left to right.
> The antenna catches the wave. A filter keeps roughly the right band and throws the rest away. Then
> comes the clever part, the *mixer*. The mixer moves the station you want to one fixed, in-between
> frequency. Why? Because it is much easier to build one very good filter for one fixed frequency
> than a filter that can move. That fixed frequency is called the *intermediate frequency*, or *IF*,
> and the *IF filter* is a very sharp filter that keeps only your station. Then the *detector* pulls
> out the sound, and the speaker plays it."
>
> "Here is the important point. Every one of these boxes is a physical part — metal, crystal,
> copper — chosen and soldered for one purpose. If you want the radio to do something different, you
> have to change the metal."

**Do.** Walk the chain left to right, and link each box to a job from slide 7: antenna = catch;
filter, mixer and IF filter = select; detector = extract; speaker = present. **Do not ask the room
to name the boxes** — it embarrasses beginners.

**If someone asks:**

- *"What is a typical IF?"* — "For FM radios it is usually 10.7 MHz; for AM radios, 455 kHz."
- *"Why is it called superheterodyne?"* — "'Heterodyne' means mixing two frequencies to make a new
  one. Edwin Armstrong invented this design in 1918, and it is still inside most car radios."

**Background for you.** The mixer multiplies the incoming signal by a tone from the *local
oscillator* (LO). The result contains the difference frequency. Turning the tuning knob changes the
LO, so a different station lands on the IF. This is why the tuning knob is labelled "the tuning
knob" on the mixer in the diagram.

**Next:** "Now watch what happens when we move just one line in this picture."

---

## S9 · The whole idea, in one picture ★ (5 min)

**Why this slide is here.** This is the most important idea of the whole session. If people
remember one picture next week, it should be this one.

**Say it like this:**

> "First, one new word: *ADC*, the analogue-to-digital converter. It is the part that turns the wave
> into numbers. In your normal radio, if there is an ADC at all, it is at the far right, after all
> the filtering is done."
>
> "In a software-defined radio, we move that one line — the ADC — far to the left, to just after the
> mixer. Everything to the right of it stops being metal and becomes software: the filter, the
> detector, the decoder. They are now lines of code. If you want the radio to do something new, you
> do not change the metal. You edit a file."
>
> "So here is the sentence I would like you to remember: *the hardware didn't get smarter. It got
> shorter.*"

**Do.** Say the last sentence slowly, then **stop talking for three seconds.** Let it land.

**If someone asks:**

- *"Why not put the ADC right at the antenna?"* — "Some very expensive radios nearly do. But
  converting billions of samples per second costs a lot of power and money. A short analogue front
  end first, then the ADC, is the practical compromise."

**Background for you.** In the SignalSDR Pro, one chip (the AD9361) contains the "front end",
the mixer and the ADC. It outputs up to 61.44 million sample pairs per second, and everything after
that — filtering, demodulating, decoding — is done by GNU Radio on the laptop.

**Next:** "So what exactly did the software replace?"

---

## S10 · Same jobs. Different material. (3 min)

**Why this slide is here.** It reassures people that SDR is not new physics. The radio they know
is still there — just written differently.

**Say it like this:**

> "Let us take the parts that disappeared, one by one. The IF filter used to be a lump of crystal.
> Now it is a list of numbers — change the list, and you change the filter. The detector used to be a
> circuit soldered for AM or for FM. Now it is a function in software, and the same computer can run
> an AM function, an FM function, or anything else. The tuning knob used to turn a variable capacitor.
> Now it is a number in a box: you type 100.5 and press Enter."
>
> "These are the same operations as before. Nothing you already know about radio is wrong. It is the
> radio you know, written down differently."

**If someone asks:**

- *"How can a list of numbers be a filter?"* — "Each output sample is a weighted average of the
  last few input samples. The list is the weights. Different weights let different frequencies
  through. Fundamentals 05 explains it with pictures."

**Background for you.** The "for the curious" box on the slide says the FM detector is
`atan2` on consecutive samples: the angle between two IQ samples in a row is how fast the phase is
turning, which *is* the frequency — and FM puts the sound in the frequency. It really is about two
lines of code (Fundamentals 04).

**Next:** "This change has three big consequences. Here is the first."

---

## S11 · Consequence 1 — one box, many radios (3 min)

**Why this slide is here.** It connects SDR to the audience's own experience: a shelf of
single-purpose devices.

**Say it like this:**

> "Think about the radios you use. A scanner for one band. A handheld for one service. A receiver
> for one kind of broadcast. Each one does one job, and each one becomes useless when the standard
> changes."
>
> "This afternoon, you will watch one board be an FM receiver, a data decoder, an aircraft tracker,
> and a television transmitter. The board never changes. Only the file changes."

**Next:** "The second consequence follows directly from that."

---

## S12 · Consequence 2 — you fix it with a download (2 min)

**Why this slide is here.** One real example that everybody lived through makes the idea
concrete.

**Say it like this:**

> "Remember when television in Malaysia switched from analogue to digital? Every analogue-only
> television needed a new decoder box, or had to be replaced. With a software radio, that change
> would have been a software update, like updating an app on your phone."

**If someone asks:**

- *"Why is not every radio an SDR, then?"* — "Cost and power. A dedicated chip for one job is
  cheaper and uses less battery. SDR wins when you need flexibility — which is why the military,
  research labs and mobile-phone base stations used it first."

**Next:** "The third consequence is the one you can see — and it is on the screen right now."

---

## S13 · Consequence 3 — radio becomes visible (4 min · live)

**Why this slide is here.** This is the most powerful minute of the segment. People see the
whole FM band at once for the first time.

**Do.** Switch the projector to the live waterfall (it has been running since slide 1). **Say
nothing for 20–30 seconds.** Let people look. Then slowly change the frequency across the band if
your display allows it.

**Say it like this (after the silence):**

> "Your radio showed you one number: the frequency you were tuned to. This shows you the whole
> band at once — every station — and the last few seconds of history, scrolling down the screen.
> Each bright vertical stripe is a station. The dark gaps are empty air. The picture moves downward,
> so the top is 'now' and the bottom is a few seconds ago."
>
> "The thin line exactly in the middle is not a station. It is a small leak from the radio itself.
> Every radio of this type has one, and you will learn to ignore it — or to tune beside it."

**If someone asks:**

- *"Can it record this?"* — "Yes. That is Lab 05, later today."
- *"Which station is which?"* — "We can tune to any stripe and listen. We will do that in the
  lab tour."

**Background for you.** At 20 million samples per second, the display covers 20 MHz — from 88 to
108 MHz, the whole FM band. Each FM station is about 200 kHz wide.

**Next:** "SDR sounds wonderful so far. To be fair, let me tell you what it is bad at."

---

## S14 · What SDR is genuinely bad at (3 min)

**Why this slide is here.** Honesty builds trust. If you only praise SDR, people stop believing
you the first time something fails.

**Say it like this:**

> "SDR has real weaknesses. First, it needs a computer. Your handheld runs for a day on a battery
> and starts instantly. This needs a laptop, an operating system and memory. Second, it struggles
> when a very strong signal sits right next to the weak one you want. The strong one can overload
> the front end and swamp the weak one. Purpose-built radios filter it out with metal before it can
> do damage. Third, it is slower to react. Samples travel to the computer and back, and for some jobs
> — like a repeater, or radar — that delay matters."
>
> "So your handheld still wins on the roadside. And that is fine. The right tool depends on the job."

**Background for you.** The overload problem is called *blocking* or *intermodulation*. A
strong signal drives the amplifier or the ADC out of its straight-line region, and false signals
appear. Lowering the gain usually helps (Fundamentals 06).

**Next:** "Let me put the whole idea into one sentence."

---

## S15 · The one-sentence version (2 min)

**Why this slide is here.** It summarises Segment 2 in one sentence that people can repeat to a
colleague.

**Say it like this:**

> "If you remember one sentence from today, make it this one: *turn the radio wave into numbers as
> early as you can — then do everything else in software.* Everything in the next three hours is a
> consequence of that sentence."

**Do.** Read it slowly, once. Then check the room:

> "Quick question for everyone — just call out. In the picture a few slides ago, what moved?"

Wait for someone to say "the converter" or "the ADC". If nobody does, go back to slide 9 for thirty
seconds and point at the moved line again. The next segment depends on it.

**Next:** "Now the two ideas you cannot skip. This is the only part of today where I will ask you
to concentrate hard — and it is only 25 minutes."

---

# Segment 3 — The two ideas you cannot skip (25 minutes)

> **Slow down in this whole segment.** It is the only place where a beginner can get lost for the
> rest of the day. Every screen later — every waterfall, constellation and recording — is a picture
> of what happens here.

## S16 · A wave, and three numbers (3 min)

**Why this slide is here.** Before talking about sampling, people need the words for describing
a wave: amplitude, frequency and phase.

**Say it like this:**

> "Every radio signal is a wave, and every wave is described by three numbers. *Amplitude* is how
> big it is — how tall the wave is. *Frequency* is how fast it repeats — how many times per second.
> *Phase* is where in its cycle the wave is at a given moment — at the top, at the bottom, or
> somewhere in between."
>
> "You already know one of these very well. Frequency is the number on your radio dial. 89.9 MHz
> means the wave repeats 89.9 million times every second."
>
> "Every kind of radio signal works by changing one or more of these three numbers over time. AM
> changes the amplitude. FM changes the frequency. Many digital signals change the phase."

**Do.** Point at each part of the drawn sine wave as you name it.

**If someone asks:**

- *"What is hertz?"* — "Hertz means 'per second'. One hertz is one cycle per second. Mega means
  million, so megahertz is million cycles per second."

**Next:** "So how does a computer hold a wave? It measures it."

---

## S17 · Turning a wave into numbers (4 min)

**Why this slide is here.** It explains *sampling* — the first of the two big ideas — with a
picture everyone understands: a film camera.

**Say it like this:**

> "A computer cannot store a smooth, continuous wave. What it can do is measure the wave, write the
> number down, wait a tiny moment, and measure again. The dots on the wave are those measurements. We
> call each one a *sample*. The analogue-to-digital converter does exactly this, millions of times
> every second."
>
> "Think of a film camera. A film is not continuous motion — it is 24 still pictures every second.
> But because the pictures come fast enough, your eyes see smooth movement. Sampling is the same: if
> the samples come fast enough, the numbers hold everything that was in the wave."
>
> "From now on, those numbers *are* the radio signal. Everything we do later is done to lists of
> numbers."

**If someone asks:**

- *"How many samples per second?"* — "It depends on the job. Today we use between one and twenty
  million per second. We write that as 'MSPS' — million samples per second."

**Next:** "But what happens if the camera is too slow?"

---

## S18 · Too few frames, wrong answer (3 min)

**Why this slide is here.** It explains *aliasing* — the danger of sampling too slowly — with the
wagon-wheel effect from old films.

**Say it like this:**

> "You have probably seen this in old films. A wagon or a car speeds up, and its wheels seem to
> slow down, stop, and even turn backwards. The wheel is not really going backwards. The camera is
> simply not taking pictures often enough to follow it."
>
> "Exactly the same thing happens with radio signals. If you sample too slowly, you get a
> perfectly convincing wave that was never really there — at the wrong frequency. There is no way to
> tell afterwards that it is wrong. So the rule is simple: sample fast enough, or you will recover
> the wrong wave."

**If someone asks:**

- *"How fast is fast enough?"* — "More than twice the width of the band you want to capture. It is
  called the Nyquist rate. Fundamentals 05 explains it. With the I and Q trick I am about to show
  you, it becomes 'at least the width of the band'."

**Background for you.** A signal at frequency *f*, sampled at rate *fs*, is indistinguishable from
one at *f − k·fs* for any whole number *k*. That is why radios filter out everything outside the
wanted band *before* the ADC (the anti-aliasing filter) — and why setting the radio's analogue
bandwidth matters (Lesson 1 in `VERIFICATION.md`).

**Next:** "Now there is one more problem, and it is the reason for the most important idea of today."

---

## S19 · The problem one number cannot solve (4 min)

**Why this slide is here.** It creates a question in the audience's mind, so that the next slide
— I and Q — feels like the answer, not like extra theory.

**Say it like this:**

> "Imagine a photograph of a fan. The photo shows you where the blade is. But can it tell you which
> way the fan is turning? No. One picture — one number — cannot tell the direction."
>
> "A radio has exactly this problem. Suppose you are tuned to 100 MHz. A signal at 100.01 MHz — 10 kHz
> above you — and a signal at 99.99 MHz — 10 kHz below you — look *identical* if you only measure one
> number. They are like a fan turning clockwise and a fan turning anticlockwise at the same speed."
>
> "Your normal radios solved this with hardware you never had to think about. A software radio needs
> a different answer."

**Do.** After the last sentence, **pause for a few seconds.** Let people feel the problem before
you solve it.

**Background for you.** Mathematically, a single real sample stream cannot tell positive from
negative frequencies: cos(+ωt) = cos(−ωt). A complex (I/Q) stream can: e^{+jωt} and e^{−jωt} rotate
in opposite directions.

**Next:** "The answer is to take two measurements instead of one."

---

## S20 · I and Q — two numbers, and now you know ★ (5 min)

**Why this slide is here.** This is the concept the rest of the day depends on. Every screen
from now on shows a stream of I and Q pairs.

**Say it like this:**

> "Picture the signal as an arm going round in a circle, like the hand of a clock. To describe where
> the arm is, we take two measurements at the same moment. *I* is how far across the arm points.
> *Q* is how far up it points. Together, I and Q tell you exactly where the arm is — and if you watch
> a few samples in a row, which way it is turning, and how fast."
>
> "So the fan problem is solved. A signal above your tuning turns one way; a signal below turns the
> other way. With I and Q, the radio can tell them apart."
>
> "That is the whole trick. Every sample from the SignalSDR Pro is one pair of numbers: an I and a
> Q. When you see a waterfall, a constellation or a recording today, you are looking at a stream of
> these pairs."
>
> "If you read only one thing from the repository, read Fundamentals 02, about I/Q sampling."

**Do.** Trace a circle in the air with your finger while you explain. Point across for I, up for
Q.

**If someone asks:**

- *"What do I and Q stand for?"* — "In-phase and Quadrature. 'Quadrature' means a quarter of a
  cycle apart — 90 degrees. The two measurements are taken a quarter-cycle apart."
- *"Is Q the 'imaginary' part?"* — "Yes. Mathematically each pair is written as a complex number,
  I + jQ. But you never need the word 'imaginary' to use it."

**Background for you.** Inside the radio chip, the incoming signal is mixed with two copies of the
local oscillator, 90° apart (cosine and sine). One path gives I, the other Q. The complex sample
I + jQ tells you amplitude (√(I² + Q²)) and phase (atan2(Q, I)). A signal above the LO rotates
anticlockwise, one below rotates clockwise.

**Next:** "Two numbers per sample has one more big benefit."

---

## S21 · What your sample rate buys you (3 min)

**Why this slide is here.** It connects sample rate to the amount of spectrum you can see —
the key to Lab 05 (recording a whole slice of the band).

**Say it like this:**

> "Because every sample has two numbers, I and Q, a useful rule follows: the width of spectrum you
> can see is about equal to your sample rate. Twenty million samples per second shows you 20 MHz of
> spectrum, all at once."
>
> "Twenty megahertz is the whole FM band, from 88 to 108. So at that rate you capture every station
> in the band in one go. Your normal radio listened to one station. This listens to the whole band,
> and you decide later which station you want."

**If someone asks:**

- *"Why not always use the highest rate?"* — "More samples means more data. At 20 million samples
  per second the laptop receives about 160 MB every second. Use the lowest rate that covers what you
  need."

**Background for you.** With real sampling you can see up to fs/2 (Nyquist). With complex (I/Q)
sampling you see from −fs/2 to +fs/2 around the tuned frequency — a total width of fs. In practice
the edges are a little weaker because of the radio's filters.

**Next:** "Three units will appear on screen all afternoon. Let me explain them now."

---

## S22 · Three units you will see all afternoon (2 min)

**Why this slide is here.** dB, dBm and dBFS appear on every display. Beginners mix them up.
dBFS matters most, because it warns of clipping.

**Say it like this:**

> "First, *dB* — the decibel. It is a comparison: how much bigger one thing is than another. Three
> dB more means twice the power. Ten dB more means ten times the power. A dB number is always
> relative to something."
>
> "Second, *dBm*. This is an actual power, compared with one milliwatt. A strong FM station at your
> antenna might be around minus 40 dBm — a very small power."
>
> "Third, and most important today: *dBFS* — decibels relative to 'full scale'. It tells you how
> full the converter is. Zero dBFS means completely full. This is a ceiling you must not hit. If the
> signal reaches zero dBFS, the tops of the wave are cut off — we say it is *clipped* — and the damage
> cannot be undone. Your car radio never warned you about this. Today, you watch for it."

**If someone asks:**

- *"So minus numbers are normal?"* — "Yes. On a dBFS scale everything is below zero. Minus 20 to
  minus 50 dBFS is a comfortable place to be."

**Next:** "Which brings us to the mistake almost everybody makes on day one."

---

## S23 · Gain is not volume (1 min)

**Why this slide is here.** It prevents the most common beginner mistake — turning the gain to
maximum — before people see a gain slider in the next segments.

**Say it like this:**

> "When you see a slider called 'gain', you will want to turn it up. Please be careful. Gain is not
> volume. Turning gain up makes the signal bigger — but it makes the noise bigger too. And past a
> certain point it makes nothing better, only distortion, because the converter clips. The classic
> day-one mistake is gain at maximum, and then wondering why it sounds worse. Start in the middle —
> around 40 — and adjust."

**Do.** If the pacing indicator shows you are on time, check understanding before the hardware
segment. Ask, hands up or call out, no wrong answers:

1. "Why does an SDR measure two numbers, I and Q, not one?" — *So it can tell a signal above where
   it is tuned from one below.*
2. "What happens at zero dBFS?" — *The converter is full; the signal is clipped.*
3. "Does more gain always help?" — *No. It raises the noise too, then distorts.*

If a question gets silence, answer it yourself in one sentence and point to the slide. Do not
teach the segment again.

**Background for you.** The receiver's own electronics add noise. Gain before the ADC helps only
until that noise is above the ADC's noise; after that, more gain lifts signal and noise together,
and eventually the ADC clips. That point is usually around the middle of the range
(Fundamentals 06).

**Next:** "Enough theory. Let me show you the actual hardware."

---

# Segment 4 — The hardware: SignalSDR Pro (15 minutes)

## S24 · The SignalSDR Pro — pass it round (3 min)

**Why this slide is here.** Holding the radio makes it real. For beginners, touching it does more
than three slides of specifications.

**Say it like this:**

> "This is the SignalSDR Pro. I am going to pass one round — please handle it gently and pass it on.
> Everything we talked about in the last hour — the front end, the mixer, the converter that turns
> the wave into numbers — is on this board. If you brought a radio today, hold them side by side."

**Do.** Hand the board into the room **without its cables** and keep talking — do not wait for
it to come back. Keep a second board (or a photo) at the front.

**Next:** "On this board, two chips do almost everything."

---

## S25 · Two chips do everything (3 min)

**Why this slide is here.** It connects the real board to the "shortened chain" of slide 9.

**Say it like this:**

> "The first chip is the AD9361, made by Analog Devices. It is the radio: the front end, the mixer
> and both converters — one for receiving and one for transmitting. It is the entire left-hand part
> of this morning's diagram, on one small piece of silicon."
>
> "The second chip is a Zynq, made by AMD — a small computer joined to reconfigurable logic. Its job is
> plumbing: it moves millions of samples every second to your laptop without dropping any, and keeps
> everything on time. Almost everything else on the board is connectors and power."
>
> "So this is the shortened chain from slide 9, made real and sold in a box."

**If someone asks:**

- *"What is reconfigurable logic?"* — "An FPGA: a chip whose wiring is loaded as a file at start-up.
  That file is one of the 'images' you will hear about in a few minutes."

**Next:** "Here are the numbers on the specification sheet, and what they mean for you."

---

## S26 · The numbers, translated (3 min)

**Why this slide is here.** Specifications mean nothing to beginners until they are translated
into things they can do.

**Say it like this:**

> "Seventy megahertz to six gigahertz. That covers broadcast FM, aircraft, ships, satellites, mobile
> phones and Wi-Fi. Shortwave is *below* 70 MHz, so it is not covered without an extra converter."
>
> "Up to 56 MHz at once. That is how wide a slice it can see or record at one time — enough for a
> whole band, which you can pick through later, indoors, with the antenna unplugged."
>
> "Two receive, two transmit. It has two receive channels and two transmit channels, so you can use
> two antennas at the same time — for example to find which direction a signal comes from."
>
> "Full duplex. It can transmit and receive at the same instant. That is what makes the last demo of
> the day possible, and it is unusual at this price."

**If someone asks:**

- *"How far can it receive?"* — "That depends on the antenna, the signal and the location, not on
  the radio. The same radio hears aircraft 200 km away with a good antenna and nothing with the
  wrong one — we will see that in Lab 09."

**Next:** "You will notice your screen calls this radio a 'B210'. Here is why."

---

## S27 · Why your screen will say "B210" (2 min)

**Why this slide is here.** It prevents confusion when the software shows a different name, and
gives people the most useful search word.

**Say it like this:**

> "When you start it, your computer will say 'USRP B210', not 'SignalSDR Pro'. That is on purpose.
> The board loads start-up software that makes it answer to exactly the same commands as the Ettus
> USRP B210 — a well-known research radio with more than ten years of tutorials, examples and code.
> All of that works on this board, unchanged."
>
> "So here is a practical tip: when you search the internet for help tonight, search for 'B210'."

**Next:** "Two things will catch you out when you first set it up. Let me warn you now."

---

## S28 · Two things that will bite you (3 min)

**Why this slide is here.** It warns about the two most common set-up problems *before* people
meet them, so the error in ten minutes looks expected.

**Say it like this:**

> "First, the order you plug things in. This board is not a USB stick. It boots its own small
> operating system from an SD card. So: power cable first. Wait about 30 seconds while it starts.
> Then plug in the data cable. Then the antenna. If you plug in the data cable first, the computer
> often simply does not see it."
>
> "Second, an error message you are going to see in about ten minutes: 'Could not find path for
> image: usrp_b200_fw.hex'. When you see it, do not panic. It is not your fault, and nothing is broken.
> We will fix it live, together."

**If someone asks:**

- *"What is an 'image' here?"* — "A file the driver sends into the radio every time it starts: the
  firmware for the USB chip and the wiring file for the FPGA. The driver must know which folder they
  are in."

**Next:** "The last hardware point is the cheapest part of the whole system — and the one that
matters most."

---

## S29 · The cheapest part that matters most (1 min)

**Why this slide is here.** Antennas decide what you can receive. Also a quick comparison with
other SDRs people may know. This is the first slide to cut if you are late.

**Say it like this:**

> "A good antenna on a cheap radio beats a bad antenna on an expensive radio, every time. The
> antenna must suit the frequency. The FM antenna we use this morning will hear almost nothing at the
> aircraft frequency, 1090 MHz. For comparison: an RTL-SDR costs about 150 ringgit and receives 2.4 MHz
> at a time, but cannot transmit. A HackRF sees 20 MHz and transmits, but not at the same time as it
> receives. The SignalSDR Pro sees up to 56 MHz and does both at once."

**Do.** Show the table briefly — do not read every number. It is on the handout card too.

**Background for you.** A simple quarter-wave antenna is about 75 mm long for 1 GHz, and about
75 cm for 100 MHz: the length must match the wavelength (Reference 03, Antennas).

**Next:** "Let us take a ten-minute break."

---

## S30 · Break (10 min)

**Why this slide is here.** People need rest, and you need time to prepare Segment 5.

**Say it like this:**

> "Ten minutes' break. When we come back, I will start a radio from cold, in front of you — and yes,
> it will break, and we will fix it."

**Do during the break:**

- Leave the FM waterfall running on the projector, so people come back to a moving screen.
- Prepare Segment 5: a terminal, large font, history cleared, in the repository folder, and the
  commands from `DEMO_RUNSHEET.md` (S33 and S34) ready.
- Walk around. The break is when shy beginners ask their question.

---

# Segment 5 — Making it work, live, from cold (25 minutes)

## S31 · Four commands (3 min)

**Why this slide is here.** It shows that installing everything is short. The most important
point is the last line: logging out and in again.

**Say it like this:**

> "Setting up the software is four commands. The first installs three things: GNU Radio, the
> toolkit we build radios with; UHD, the driver that talks to the radio; and a maths library. The
> second downloads the 'image' files the radio loads each time it starts. The third gives your user
> account permission to use the radio without typing 'sudo' every time."
>
> "And then — this is the one everybody forgets — you must log out and log back in. The permission
> from the third command does nothing until you do. This single step is the most common reason a
> correct setup looks broken. People lose a whole evening to it."

**If someone asks:**

- *"Which Linux?"* — "This course is tested on Ubuntu 24.04. Other versions work, but the
  commands may differ slightly. Setup 01 and 03 have the details."
- *"Does it work on Windows?"* — "GNU Radio has a Windows installer (radioconda), but this course is
  written and tested for Linux. For a first attempt, Linux is much easier."

**Next:** "With the software in place, the plug-in order matters."

---

## S32 · Order matters (2 min)

**Why this slide is here.** Repeats the boot order as four clear steps, because it is the first
thing that goes wrong at home.

**Say it like this:**

> "Four steps, in this order, every time. One: the power cable — a USB-A to USB-C cable into the
> board's power socket. Two: wait about 30 seconds. The board is starting Linux from its own SD card,
> so let it finish. Three: the data cable — the thick USB 3.0 cable — into a blue USB port on your
> laptop. Four: the antenna, finger-tight, onto the connector marked TX/RX. Do not force it."
>
> "Remember: you are starting a small computer, not plugging in a memory stick. If the laptop does
> not see the radio, unplug both cables, wait, and start again from step one."

**If someone asks:**

- *"Why a blue port?"* — "Blue usually means USB 3.0. On USB 2.0 the radio works, but only at
  low sample rates."

**Next:** "Let us ask the radio if it is there."

---

## S33 · Live — the radio answers (6 min)

**Why this slide is here.** Watching a machine introduce itself turns it from a mystery box into
something understandable.

**Do.** Terminal, full screen, large font. Type (do not paste — typing slowly lets people read):

`uhd_find_devices`

then

`uhd_usrp_probe`

**Say it like this:**

> "The first command asks: is there a radio connected? It answers with the serial number and the
> product — B210, as I told you. The second command opens the radio properly. It loads the image
> files, checks it is on USB 3, and then prints a long description of itself. I will not read all of
> it. Let us look at one part: here it tells us its own receive gain range, and here the sample
> rates it supports. The radio is describing itself."

**Do.** Read the serial number aloud. Scroll to **one** section only — the RX gain range, or the
sample rates. Do not walk through the whole tree; it loses beginners.

**If something goes wrong.** If the radio is not found: unplug both cables, power first, wait
30 s, then data. If it still fails after 30 seconds, switch to your recorded fallback and continue.
`DEMO_RUNSHEET.md` §4 lists what the symptoms mean.

**Next:** "Now — let me show you the error I promised."

---

## S34 · Live — the failure, and the fix ★ (8 min)

**Why this slide is here.** Every person in the room will meet this error alone, at night, with
nobody to ask. The difference between someone who gives up and someone who continues is having
watched it fixed calmly, once. **Never cut this slide.**

**Do.** Trigger the error on purpose. This method is tested and changes nothing on the laptop:

`mkdir -p /tmp/no_images`

`UHD_IMAGES_DIR=/tmp/no_images uhd_usrp_probe`

**Say it like this (while the error is on screen):**

> "Here it is. 'Could not find path for image: usrp_b200_fw.hex' — or, in newer versions, 'Could not
> find the image usrp_b200_fw.hex in the image directory'. The wording changes; the meaning does not."
>
> "I will be honest about what I did: I told the driver to look in an empty folder. That is exactly
> what happens on many computers by accident. When you install GNU Radio, it brings its own copy of
> the driver. If you also install a newer driver, you now have two versions. Each version looks for
> its image files in its own folder — and one of them looks in a folder where the files are not.
> Nothing is broken. Nothing is your fault. It is simply looking in the wrong place."
>
> "Here is the fix. The repository has a script that checks every installed version of the driver
> and makes sure each one can find the files."

**Do.** Run the fix, then try again without the variable:

`cd 00_setup`

`./fix_uhd_version_conflict.sh`

`uhd_usrp_probe`

The script may ask for your password — say so out loud ("it needs my password because it changes
system folders"). When the probe works:

> "It works. You will probably meet this alone one evening. Now you have seen it fixed, and you know
> where the script is: the folder 00_setup, document 06."

**If someone asks:**

- *"How do I know which versions I have?"* — "The first line the driver prints shows its version,
  for example 'UHD_4.6.0'. If `uhd_find_devices` and GNU Radio print different versions, you have
  two. Setup 06 explains it fully."
- *"Can the script damage anything?"* — "It only creates links between folders. You can run it
  with `--dry-run` first — it then only shows what it would do."

**Background for you.** Ubuntu's GNU Radio uses the Ubuntu UHD library (4.6 here). The Ettus PPA
installs a newer UHD (4.11 here) for the command-line tools. Each looks for images in
`/usr/share/uhd/<version>/images`. `uhd_images_downloader` from the newer version puts files in
only one place. The script makes every version's folder point to where the images really are.
The error has two wordings: "Could not find path for image" when the folder does not exist at
all, and "Could not find the image … in the image directory" when the folder exists but is empty.

**Next:** "So you do not have to remember any of this, here is a card to take home."

---

## S35 · Take this with you (3 min)

**Why this slide is here.** The handout card is what people will actually use on Monday.

**Say it like this:**

> "Here is a card for each of you. One side is the setup: the four commands, the plug-in order, the
> fix you just watched, and the five mistakes everyone makes. The other side explains the fifteen
> words we use today in plain English. Everything else, you can look up. This card is for the
> moment when there is nobody to ask."

**Do.** Hand out the cards (`handout_cards.html`, printed double-sided). Give people ten seconds to
look at them.

**Next:** "And behind the card, everything is written down in detail."

---

## S36 · It is all written down (3 min)

**Why this slide is here.** It tells people where the full setup documents are, and removes the
pressure to remember.

**Say it like this:**

> "The folder 00_setup has six documents. One installs the driver and explains what it does. Two
> covers the SD card, the jumper, the cables and the start-up order. Three installs GNU Radio. Four is
> a set of checks that prove everything works. Five is troubleshooting, organised by symptom. And six
> is the fix you just watched — the one you are most likely to need."
>
> "You are not expected to remember any of this. That is why it is written down."

**Do.** Say the last sentence slowly. For beginners, it is the most reassuring line of the
segment.

**Next:** "Now for my favourite part: let us build a radio."

---

# Segment 6 — Your first flowgraph, built in front of you (25 minutes)

## S37 · GNU Radio Companion (3 min)

**Why this slide is here.** It introduces the tool before you use it, so people know where to
look on the screen.

**Say it like this:**

> "GNU Radio Companion — people call it GRC — is a drawing program that produces a working radio.
> On the right is the list of every block you can use: filters, decoders, displays, the radio itself.
> In the middle is the canvas, where you place blocks and draw arrows between them. At the top is the
> play button. A diagram in GRC is called a *flowgraph*: samples flow along the arrows from block to
> block."
>
> "You are about to watch me draw this morning's block diagram — and then it will play music."

**Do.** Open `gnuradio-companion` with an empty canvas. Point at the three areas. Thirty seconds
each — no menu tour.

**Background for you.** In GNU Radio 3.10 the block list is on the right. <kbd>Ctrl+F</kbd>
searches it: type part of a block's name, then drag the block onto the canvas. Double-click a block
to change its settings.

**Next:** "Let us build it."

---

## S38 · Live build — three blocks and a radio ★ (13 min)

**Why this slide is here.** This is the emotional peak of the day: a radio, built from nothing,
plays music. It proves that "software radio" is real and that the audience could do it too.

**Do.** Build Lab 01 from an empty canvas, using exactly these values (so people can repeat it
tonight):

| Block | Settings |
|---|---|
| **UHD: USRP Source** | Sample Rate `1e6` · Center Freq = your station, e.g. `89.9e6` · Gain `40` · Antenna `TX/RX` · **Bandwidth `1e6`** |
| **WBFM Receive** | Quadrature Rate `1e6` · Audio Decimation `20` |
| **Audio Sink** | Sample Rate `50000` |

Connect them left to right, and press play.

**Say it like this (block by block):**

> "First, the radio itself: the USRP Source block. This block *is* the antenna, the front end and
> the mixer from this morning's diagram. I set the sample rate to one million samples per second —
> '1e6' is how we write one million. I set the frequency to our station, 89.9 megahertz. Gain 40,
> the middle, not the maximum. Antenna TX/RX, where the antenna is screwed on."
>
> "And one more box that looks unimportant: Bandwidth. I set it to one million as well, the same as
> the sample rate. If you leave it empty, the radio opens its filter to 56 megahertz and lets in a lot
> of rubbish. When we tested this course, that one empty box cost 18 decibels of sound quality in this
> very lab. So — always fill it in."
>
> "Second block: WBFM Receive — wideband FM. This replaces the detector. It turns FM into sound. It
> takes one million samples per second in, and keeps one in twenty, so fifty thousand per second come
> out. One million divided by twenty is fifty thousand. That is the only arithmetic in this build,
> and it is the thing people get wrong at home."
>
> "Third block: Audio Sink — the speaker. I tell it to expect fifty thousand samples per second,
> because that is what the previous block gives it."
>
> "Three blocks. Two arrows. Let us press play."

**Do.** Press play. **Music comes out. Stop talking for three seconds.** Let the room enjoy it.

Then open the generated Python file for about ten seconds:

> "GRC turned my drawing into this Python program. The diagram *is* the program. You never have to
> read this — but it is there if you want to."

**Pace check.** If few people code (slide 4), go slower and explain every field. If many code, go
faster and use the saved time on slide 39.

**If something goes wrong.** No sound: check the Audio Sink rate is 50000 and the speaker volume.
"Could not find…image": you already fixed it on S34. Still nothing after 30 seconds: open the
finished file `02_flowgraphs/lab01_simple_wbfm/lab01_simple_wbfm.grc` and press play.

**If someone asks:**

- *"Why 50,000 and not 48,000 like a CD or a sound card?"* — "Because WBFM Receive can only divide by
  a whole number, and one million is not a whole-number multiple of 48,000. Most sound cards accept
  50,000 without complaint."

**Background for you.** WBFM Receive does three things: FM demodulation (measuring how fast the
phase turns), a low-pass filter to keep the audio band, and *de-emphasis* — undoing the treble
boost that FM stations add before transmitting. Malaysian stations use 50 µs; this block always
uses the American 75 µs, so the treble sounds slightly dull. It is a small effect, and Lab 04 does
de-emphasis by hand with the right value (Lab 01 README, "Malaysia note").

**Next:** "Now let us break it — on purpose."

---

## S39 · Break it on purpose (8 min)

**Why this slide is here.** Hearing what each mistake sounds like teaches people to diagnose
problems by ear. It is also the best use of spare time with an experienced room.

**Do.** Three faults, one at a time. **Fix each one before the next**, so the last thing people
hear is a working radio. Rehearse all three the day before — the exact sound depends on your station
and laptop.

**Fault 1 — wrong audio rate.** Change the Audio Sink from `50000` to `25000`.

> "Listen. It is slow, deep, and it jumps. The radio makes fifty thousand numbers a second, but I
> told the speaker to play only twenty-five thousand. The speaker plays them at half speed, and the
> extra numbers pile up and are thrown away — see the letter 'O' appearing in the terminal? 'O' means
> overflow: samples were lost. When you hear slow or fast, squeaky sound at home, check the rates."

Put it back to `50000`.

**Fault 2 — no station there.** Change the frequency to an empty spot (find one in rehearsal).

> "Now there is no station at this frequency. This loud rushing noise is pure noise. Your car radio
> hides this sound from you — it mutes the audio when there is no station. That feature is called
> *squelch*, and we will see it in Lab 03."

Put the station back.

**Fault 3 — gain wrong, both ways.** Gain to the maximum, then to 0.

> "Gain at maximum: the radio is overloaded. You may hear distortion, or other stations leaking in.
> Now gain at zero: the station sinks into hiss, because the signal is too small compared with the
> radio's own noise. Somewhere in the middle is right."

Put the gain back to 40.

**Say to finish:**

> "Learn the sound of each mistake, and you will be able to fix them without any measuring
> equipment."

**Next:** "Let us look at what you just watched."

---

## S40 · Three blocks (1 min)

**Why this slide is here.** A short, memorable summary before the break.

**Say it like this:**

> "Three blocks. That was a complete FM radio. Everything else we do today is just more blocks.
> Let us take a ten-minute break."

**Do.** Do not add anything. Go straight into the break — the simplicity is the point.

---

## S41 · Break (10 min)

**Why this slide is here.** Rest, and time for you to prepare eight demos in a row.

**Say it like this:**

> "Ten minutes. When we come back: eight things this radio can do — and one thing it probably should
> not do."

**Do during the break:**

- Open every lab for the tour in order (Labs 02–09), each ready to press play.
- Check the aircraft demo (Lab 09): if no aircraft appear with your 1090 MHz antenna, load the test
  capture instead — and say so honestly when you show it.
- Check the RDS station for Lab 08 is showing its name.

---

# Segment 7 — What it can do: the lab tour (40 minutes)

> **Rule for this segment: 4–5 minutes per lab, and stop on time.** You are showing *range*, not
> depth. If someone asks a deep question, answer in one sentence, name the document, write it in the
> parking lot, and move on. This segment brings a mixed room back together: nobody has seen most of
> this before.

## S42 · Twelve labs, one ladder (2 min)

**Why this slide is here.** It shows the whole course as one ladder, so the repository feels
finishable, not enormous.

**Say it like this:**

> "The repository has twelve labs, and they form a ladder. Each lab adds exactly one new idea to the
> one before. Labs 1 to 4 stay with one FM signal and grow your skills: instruments, control,
> stereo. Labs 5 and 6 teach you to record, so you stop needing the radio for every experiment.
> Labs 7 to 9 cross into digital: real data, and real aircraft. And Labs 10 to 12 transmit — they
> build a small television station."
>
> "You are here, now, at the point where we can look at all of them. I will show you eight labs in
> about forty minutes — about five minutes each. This is a tour, not a lesson."

**Next:** "We start with the radio you watched me build — plus instruments."

---

## S43 · Labs 02–03 — instruments, then control (5 min · live)

**Why this slide is here.** It shows how Lab 01 grows. Squelch is the feature the audience
already knows from their own radios, so it creates a moment of recognition.

**Do.** Open Lab 02, press play. Then Lab 03. Commands in `DEMO_RUNSHEET.md` (S43).

**Say it like this:**

> "This is Lab 02. It is the same radio you watched me build, with instruments added: a spectrum,
> which shows signal strength against frequency; a waterfall, which is the spectrum scrolling over
> time; and a slider that retunes the radio while it plays. Watch the stripe move when I move the
> slider."
>
> "And this is Lab 03. It adds control. Here is something you all know from your own radios. What
> is this knob called?" — *wait for someone to say "squelch"* — "Yes, squelch. Let me tune to an empty
> frequency. Silence. Without squelch, you would hear the loud hiss from earlier. Now back to the
> station — the sound returns. Lab 03 also adds automatic gain control, which keeps the level steady,
> and a proper channel filter. No new hardware — just more blocks on the canvas."

**If someone asks:**

- *"How does squelch decide?"* — "It measures the power in the channel. Below a threshold you set,
  it outputs silence."

**Background for you (a real story, if the room is ready).** When we tested Lab 03 on the real
radio, the squelch at first would not go quiet on an empty channel. The radio's own leak at the
centre frequency — the thin line from slide 13 — was as strong as the station itself, so "empty" and
"station" looked almost the same to the squelch (1.8 dB apart). One extra block, a *DC Blocker*,
removed the leak, and then they were 7.6 dB apart and the squelch worked. Tests with a perfect,
simulated signal had missed this; only the real radio showed it (`VERIFICATION.md`, Lesson 12). The
order of blocks also matters: squelch must come *before* automatic gain control, because an AGC
lifts the noise back up (Lesson 8).

**Next:** "The next lab shows something that has been hiding in every FM broadcast you have ever
heard."

---

## S44 · Lab 04 — stereo, built from scratch (4 min · live)

**Why this slide is here.** It reveals a hidden part of a familiar signal (the 19 kHz pilot), and
shows that a whole chip in their car radio is just a few blocks here.

**Do.** Open Lab 04. Tune to a **music** station (not a talk station — they carry almost no
stereo), RF gain about **55**. Headphones or two speakers help people hear the separation.

**Say it like this:**

> "An FM stereo broadcast has a secret. Look at this spectrum of what comes out of the FM decoder.
> This sharp line is a tone at 19 kilohertz. It has been in every stereo FM broadcast you have ever
> heard, but you cannot hear it — it is above normal hearing and your radio filters it out. It is
> called the *pilot tone*. The radio locks onto it, doubles it to 38 kilohertz, and uses that to
> separate left from right."
>
> "In your car radio this is done by a stereo decoder chip. Here, nobody bought a chip. It is a few
> blocks on a canvas."

**If someone asks:**

- *"How does the pilot separate left and right?"* — "The station sends left-plus-right as normal
  mono sound, and left-minus-right shifted up to 38 kHz. The pilot tells the receiver exactly
  where 38 kHz is. Add the two and you get left; subtract and you get right. Fundamentals 04 explains
  it."

**Background for you.** At the lab (Kepong), gain 40 left the pilot only 11 dB above the noise,
while gain 55 gave 27 dB. And a talk station such as BFM 89.9 has almost no stereo content, so left
and right sound the same — use a music station. When this lab was tested with a signal whose right
answer was known, the original decoder turned out to be almost mono; it was fixed and then
confirmed on music stations (Lesson 9).

**Next:** "The next lab is the most practically useful in the whole repository."

---

## S45 · Lab 05 — record once, experiment forever (5 min · live)

**Why this slide is here.** Recording raw signals is the habit that separates people who make
progress from people who keep going back outside. The antenna-unplugging moment makes the point.

**Do.** Use a recording you made the day before (10 s at 2 MSPS is 160 MB). Play it in
`lab05_iq_playback.grc`. **Unplug the antenna visibly** before you press play.

**Say it like this:**

> "Lab 05 records the raw radio signal — not the sound, but the I and Q numbers themselves — to a
> file. This recording is 2 megahertz wide, so it contains several stations at once. Watch: I am
> unplugging the antenna. The radio now hears nothing. And I press play…"
>
> "…and we still have the stations. I can move this slider and tune between them, *inside the
> recording*. Everything happens exactly as if the antenna were connected."
>
> "Why does this matter? Three reasons. You go outside once, with a good antenna, and record
> twenty seconds; then you can work indoors for as long as you like. You get the same data every
> time, so you can change your mind about what you are looking for. And you can compare two
> decoders fairly, on identical input. This is the habit of people who make progress."

**If someone asks:**

- *"How big are the files?"* — "Eight bytes per sample. At 2 million samples per second, that is
  16 MB every second — about 1 GB per minute. Check your disk space."

**Next:** "Now one tuner, many modes — your scanner, in software."

---

## S46 · Lab 06 — one tuner, many modes (4 min · live)

**Why this slide is here.** It connects SDR to the scanners many people in the room use, and
shows that a "mode" is just a different set of blocks.

**Do.** Open Lab 06, set the frequency **0.2 MHz above** your station (e.g. `90.1e6` for 89.9 MHz).
Start in WBFM. Switch modes with the **Mode** box.

**Say it like this:**

> "Lab 06 is a scanner in software. It has three modes: AM, for aircraft voice; narrow FM, for
> handhelds, marine and business radio; and wide FM, for broadcast. It has a signal meter, and squelch
> again. Notice one detail: I tuned the radio 200 kilohertz *beside* the station, and then picked the
> station in software. That keeps the radio's own leak — the thin centre line — away from our signal.
> In our measurements, it made the sound almost 9 dB cleaner."
>
> "Switching mode is just switching which blocks the signal goes through. Ask me for a mode, and I
> will switch it now."

**Do.** Switch to AM and NBFM to show the controls, then back to WBFM. **Do not promise a voice**
in AM or NBFM — it needs someone transmitting nearby at that moment.

**If someone asks:**

- *"Can it hear the airport?"* — "Aircraft voice is AM between 118 and 137 MHz. With a suitable
  antenna and aircraft in range, yes. Indoors with this FM antenna, probably not."

**Next:** "Now we cross into digital — and for this one, we do not even need the radio."

---

## S47 · Lab 07 — crossing into digital (5 min · no radio)

**Why this slide is here.** It introduces the constellation — the picture used for every digital
signal — and shows that measured results match theory exactly.

**Do.** Open Lab 07 (it needs no radio). Start at the default Eb/N0 of 8 dB, then lower the
**Eb/N0** slider slowly.

**Say it like this:**

> "Digital signals are sent as *symbols*. This lab uses the simplest kind, BPSK, where each symbol
> is one of two values: plus one or minus one. On this display — a *constellation* — each received
> symbol is a dot. With a clean signal, you see two tight dots."
>
> "This slider, Eb/N0, is how strong the signal is compared with the noise. As I lower it, the dots
> smear into clouds. When the clouds reach the middle line, the receiver starts guessing wrong — those
> are bit errors, and the counter in the terminal goes up."
>
> "Here is the remarkable part. The error rate this lab measures lands exactly on the curve in the
> textbook. At the default setting it measures about four errors in ten thousand bits, and theory says
> the same. The mathematics is not an approximation of this system. It *is* this system."
>
> "And because it needs no radio, you can run this one tonight."

**If someone asks:**

- *"What does Eb/N0 mean?"* — "Energy per bit divided by noise. It is signal-to-noise ratio,
  measured per bit, so different systems can be compared fairly."

**Background for you.** Lab 07 simulates the transmitter, a noisy channel with frequency and
timing errors, and a complete receiver (timing recovery and a Costas loop). Because a Costas loop
can lock upside-down, the data is sent *differentially* (as changes), so the theory to compare with
is differential BPSK: about 3.8 × 10⁻⁴ at 8 dB, and the lab measures about 4.0 × 10⁻⁴.

**Next:** "Now real digital data, hidden inside a signal you have heard all your life."

---

## S48 · Lab 08 — hidden data (5 min · live)

**Why this slide is here.** It is usually the best "I had no idea" moment of the day: text data
hidden inside ordinary FM radio.

**Do.** Open Lab 08, tuned **0.2 MHz below** your RDS station, with the channel offset set to
`+200e3` and RF gain about 60. The decoded name appears in the terminal (`[RDS] … PS='…'`). Check
the day before which station sends RDS — at the lab only BFM 89.9 did.

**Say it like this:**

> "You know the station name that appears on your car radio's display? Where does it come from? It
> is sent inside the FM broadcast itself, on a quiet extra signal called a *subcarrier*, at 57
> kilohertz — three times the stereo pilot. The system is called RDS, the Radio Data System. It has
> been there for decades, and most people never think about it."
>
> "Let me decode it." — *wait for the name to appear* — "There it is: the station's name, read
> directly from the radio waves by our software."

**Do.** Let the name appear and stay for a few seconds **before** you explain anything.

**If someone asks:**

- *"Can it show the song title?"* — "Yes, if the station sends it — that is called RadioText. At the
  lab, the only RDS station sends just its name, so we have not seen song titles here."
- *"How does it know the data is correct?"* — "Every block of 16 bits carries 10 check bits. The
  decoder accepts data only when the check matches. On an empty channel it accepted nothing out of
  almost 12,000 tries."

**If it does not work.** Use the test-signal fallback in `DEMO_RUNSHEET.md` (S48) and say
honestly: "the local station is not sending it right now, so here is a test signal — the decoder is
the same."

**Background for you.** RDS sends 1187.5 bits per second in groups of four 26-bit blocks. The
station name (PS) is eight characters, sent two at a time. BFM 89.9 changes its PS text every few
seconds ("BFM 89.9", "BUSINESS", "FINANCE"). The first live test decoded 287 groups in 30 seconds
(84 % of the maximum possible).

**Next:** "From data in the FM band to aircraft at 1090 megahertz."

---

## S49 · Lab 09 — aircraft (5 min)

**Why this slide is here.** Decoding real aircraft positions is exciting, and it shows the same
board working in a completely different band and modulation.

**Do.** This demo needs a **1090 MHz antenna** by a window — the FM antenna hears nothing here.
Check in rehearsal whether aircraft really appear. If not, use the test capture (`DEMO_RUNSHEET.md`,
S49) **and say that it is a test.**

**Say it like this:**

> "Every airliner overhead is broadcasting who it is, how high it is and where it is — several times
> every second, unencrypted, on 1090 megahertz. The system is called ADS-B. Websites that show live
> flight maps are built mostly from volunteers' receivers like this one."
>
> "A different band, a different kind of modulation — short pulses instead of FM — and yet: the same
> board, the same toolkit, just a different flowgraph."

If you are using the test capture:

> "These aircraft come from a test program, so you can see exactly what the decoder does. With a
> 1090 MHz antenna and a clear view of the sky, the same decoder shows real aircraft."

**If someone asks:**

- *"Is this legal?"* — "Receiving is legal. Publishing or misusing the data may have rules — check
  before you share it."
- *"How far can it hear?"* — "With a good antenna outdoors, often 200 km or more. Indoors, much less."

**Background for you.** ADS-B messages are 112 bits long, sent at 1 megabit per second as pulses
(pulse-position modulation). The decoder checks a 24-bit CRC. At the lab, with the FM whip, Lab 09
received nothing — not a fault of the decoder, but of the antenna: a 1090 MHz signal needs an
antenna about 69 mm long (Lesson 4). The decoder is proven on the official test messages.

**Next:** "Let us step back. What did all of those demos have in common?"

---

## S50 · What did all of those have in common? (3 min)

**Why this slide is here.** It ties the tour back to the one-sentence version from slide 15. The
audience should now *feel* what it means.

**Say it like this:**

> "FM with instruments. Squelch. Stereo. Recording. A multimode scanner. Digital data. Hidden text.
> Aircraft. What did they have in common?" — *pause* — "One board. One driver. One toolkit. Only the
> files were different."
>
> "Remember the sentence from before the first break? *Turn the radio wave into numbers as early as
> you can — then do everything else in software.* I suspect it sounds different now than it did this
> morning."

**Do.** After reading the sentence, pause for a few seconds. This recognition is the payoff of
the first half of the day.

**Next:** "And these eight are only the beginning."

---

## S51 · And 589 more (2 min)

**Why this slide is here.** It shows the size of the field, and — if you prepare — connects it
to the audience's own work.

**Say it like this:**

> "The repository has a catalogue of 589 more signals and projects, in sixteen areas: pictures from
> weather satellites, ship tracking, weather balloons, amateur radio, sensors like tyre pressure and
> smart meters, GPS and time signals, radar, and even radio astronomy — you can detect hydrogen in our
> galaxy with a small dish. Each entry says the frequency, how difficult it is, and which labs prepare
> you for it."

**Do.** **Prepare three examples that match this particular audience's work**, and name them.
For example, for telecom staff: LTE cell identification and GSM; for aviation staff: ADS-B and VHF
airband; for maritime staff: AIS ship tracking. A generic list impresses nobody; three examples from
their own job always land.

**Next:** "Now for the last lab — and the only one that transmits. Before the fun part, one
important slide."

---

# Segment 8 — Transmitting: a television station (25 minutes)

## S52 · Receiving is legal almost everywhere. Transmitting is not. (4 min)

**Why this slide is here.** It sets the rules *before* the exciting part. Beginners have no
instinct yet for the law and the risk, and they will copy what they see you do.

**Say it like this:**

> "Before the fun part, an important slide. Receiving is legal almost everywhere. Listening is
> passive: it affects nobody. Transmitting is different. When you transmit, you put energy into
> shared space that is licensed to someone. The television channels belong to licensed broadcasters.
> Interference is not a theory: the signal you disturb might be somebody else's emergency call."
>
> "In Malaysia, the regulator is the MCMC — the Malaysian Communications and Multimedia Commission.
> It publishes a *Class Assignment*: a list of bands that anyone may use without a licence, at low
> power, under set conditions. Television channels are not on that list."
>
> "So today's demo runs down a cable. The transmitter goes into a 40 decibel attenuator — a small
> metal part that reduces the signal ten thousand times — and then into the receiver. No antenna is
> fitted anywhere. Not because we are timid, but because it is legal — and a cable gives a cleaner,
> steadier signal than two antennas across a room."

**Do.** Hold up the cable and the attenuator so everyone sees them. Beginners copy what the expert
does — let them see an attenuator, not an antenna.

**If someone asks:**

- *"But the power is tiny — surely it does not matter?"* — "Even small power can reach further than
  you expect, and the law does not have a 'small' exception for licensed channels. The cable removes
  the question completely."
- *"How do I become allowed to transmit?"* — "Slide 58 answers that."

**Background for you.** 40 dB means the power is divided by 10⁴ = 10,000. Lab 12's README allows
20–30 dB; in a classroom start with 40 dB: the transmitter has plenty of spare gain, and the
receiver cannot be overloaded.

**Next:** "With that said — we built a television station."

---

## S53 · We built a television station (2 min)

**Why this slide is here.** It states the headline result simply, so the audience knows where
this segment is going.

**Say it like this:**

> "The last labs build a digital television transmitter. We used an ordinary television — the
> kind you have at home — and did an ordinary channel scan. The television found our channel and
> played our video. Not a simulation: an actual TV, in an actual room, with a transmitter made of
> software. The television could not tell the difference."

**Do.** Say the key sentence twice: "The television found our channel and played our video."

**Background for you.** This was Lab 10: a DVB-T2 transmitter — the same standard as MYTV, which
Malaysian televisions receive. It was run in a controlled, short-range setup, and the lab owner
confirmed on a real DVB-T2 television that it found the channel and played the video. (The
transmitter's code has not changed since that test.)

**Next:** "How do you get from a video file to a radio wave? Very briefly…"

---

## S54 · From a video file to a radio wave (3 min)

**Why this slide is here.** One quick look at the chain, so the demo makes sense. **This is the
first slide to cut in this segment if you are late.**

**Say it like this (about ten seconds per box):**

> "We start with a normal video file. It is cut into small packets of 188 bytes each — the format
> all digital television uses, called a *transport stream*. Then we *protect* it: we add extra check
> data, so the receiver can repair errors. Then we *shuffle* it, so that a short burst of noise damages
> a little of many packets instead of destroying one packet completely. Then we *spread* it across
> 32,768 separate carriers — many small radio signals side by side. Finally it goes out as one radio
> signal at a TV frequency, here 474 megahertz."
>
> "I am skipping the theory of the last two boxes. They are a whole document on their own —
> Fundamentals 11 — which you can read another day."

**If someone asks:**

- *"Why so many carriers?"* — "Because radio signals bounce off buildings and arrive several times,
  slightly late. Many slow carriers are much less affected by those echoes than one fast one. It is
  called OFDM."

**Background for you.** "Protect" is the error correction (in DVB-T2: BCH and LDPC codes), "shuffle"
is interleaving, and "spread" is OFDM with a 32K FFT: 32,768 carrier positions, of which 27,841 are
used in the 8 MHz extended mode Lab 10 uses (7.77 MHz wide). 474 MHz is UHF channel 21.

**Next:** "Before we transmit anything, let us look at what is already in the band."

---

## S55 · Demo — scan the band (5 min · receive only)

**Why this slide is here.** It shows a real measuring tool — and a great story about an instrument
that was confidently wrong.

**Do.** Run the scanner (about 40 seconds for channels 21–48):

`python3 scan_tv_band.py --first 21 --last 48 --dwell 0.4` (in `03_scripts`)

**Your venue will differ from the slide.** The slide shows the result at the lab (an apartment in
Kepong, with an FM whip): no TV at all, because the surrounding buildings block it. If MYTV channels
appear in your room, point at them — even better.

**Say it like this:**

> "This scanner visits every TV channel and asks: is anything here, and is it television? At the
> lab, it found no television at all — the buildings around it block the signal. But it did find
> something on channel 22. And here is a story about that."
>
> "The scanner has a detector for television. Television signals repeat a small piece of
> themselves at regular times — that is how a TV finds them. The detector looks for that repetition.
> On channel 22 it scored 13.9 — far above the threshold. It said: television! It was not television.
> It was a signal that switches on and off in short bursts."
>
> "Why was the detector fooled? It asks, 'does this signal look like itself a little later?' A short
> burst *always* looks like itself, at any delay you test — so it passed every time. The detector
> was confidently wrong. Two extra, simple checks fixed it: does the signal have the sharp edges of a
> TV channel, and is it on all the time, like a broadcast? The burst failed both."
>
> "The lesson goes far beyond radio: a confident instrument can still be wrong. Know how each test can
> be fooled, and check it with another test that is fooled in a different way."

**If it does not work.** `python3 scan_tv_band.py --selftest` runs without a radio. It creates the
same false alarm on purpose and shows the scanner refusing it.

**Next:** "Now let us transmit — down the cable."

---

## S56 · Demo — a picture, down a cable (5 min · transmits)

**Why this slide is here.** The live result: video sent by one software radio and received and
played by software, in real time.

**Do.** 🚨 **Cable and attenuator only. No antenna on either port.** The full steps are in
`DEMO_RUNSHEET.md` (S56). In short:

1. Cable: `TX/RX` → 40 dB attenuator → `RX2`. The video stream `/tmp/bintang.ts` made the day
   before.
2. Open `lab12_fullduplex_tv.grc` and press play. The terminal reminds you that the transmitter
   starts **off**.
3. Raise **TX gain** slowly, then **TX amplitude** to about 0.5, while watching **Signal quality**
   (MER).
4. When MER rises above about 15 dB, the receiver locks, the constellation shows 16 clean dots, and
   a few seconds later the video window opens.

**Say it like this (while you raise the sliders):**

> "The transmitter starts at zero, on purpose. I raise it slowly and watch this number: 'signal
> quality', called MER. It is the same kind of number your television shows in its signal menu. Below about
> 12 dB, nothing works. From about 13 dB, the picture is perfect. There is almost nothing in between —
> digital TV is either perfect or gone. We call that the *cliff*."
>
> "And here is the picture: sent by one side of this radio, through the cable, received by the other
> side, and decoded by software — at the same time."
>
> "Why the cable? When we first tried this over the air, we received nothing. A test tone at the
> same settings came through strongly — so why not the TV signal? Because a TV signal spreads its
> power over thousands of carriers. Each one is tiny. That costs about 35 dB compared with a single
> tone. We needed 19 dB more transmit power than anyone guessed. With it, 79 million bytes arrived
> with not one wrong. A cable gets there with far less power — and sends nothing into the room."

**If someone asks:**

- *"Is this the same as the TV at home?"* — "Almost. This demo uses DVB-T, the older standard,
  because free software can decode DVB-T in real time but not yet DVB-T2. The home-TV test in Lab 10
  used DVB-T2, the standard MYTV uses."
- *"What are the 16 dots?"* — "16-QAM: each symbol carries 4 bits, so there are 16 possible
  positions."

**If something goes wrong.**

- No window at all, and a message about the video stream: make the stream (the terminal prints
  the exact command).
- The window appears but no video: the transmitter is still at zero — raise TX gain and TX
  amplitude.
- The constellation is a smeared blob: too much signal on the cable. Lower RX gain first, then TX
  gain.
- **Rehearse this exact setup the day before.** The lab's perfect result was measured over a short,
  controlled air path; the cable version must be checked on your equipment.

**Background for you.** Lab 12 transmits DVB-T (8K, 16-QAM, code rate 2/3, guard 1/32) on UHF
channel 31 (554 MHz) at 9.14 million samples per second in each direction, and needs exactly
16.086 Mbit/s of video. The same radio transmits on `TX/RX` and receives on `RX2` at the same time
— that is full duplex. MER is the ratio of the ideal constellation points' power to the error power.

**Next:** "Two things went wrong while we built this, and they teach more than the success."

---

## S57 · Two things that went wrong ★ (4 min)

**Why this slide is here.** Two stories with lessons that apply far beyond radio. Keep this slide
even if you are late — cut slide 54 instead.

**Say it like this — story 1:**

> "The first story: the green light that could not go red. Our television receiver reported that
> it was 100 % healthy. Every packet had the correct start marker. But the video was complete garbage."
>
> "Why? Digital TV packets all start with the same marker byte. We used that marker as our health
> check. But the part of the receiver that writes the marker writes it *always* — whether the data
> behind it was decoded correctly or not. So our check could never fail. It had never been able to
> tell us anything."
>
> "The lesson: a health indicator can be built in a way that makes it structurally impossible to
> report the fault. Before you trust a green light, ask: could it ever go red?"

**Story 2:**

> "The second story: perfect data, bad picture. Every byte arrived correctly, and the television
> played the video in high quality — but it was jerky and sluggish."
>
> "The cause: to keep broadcasting, we played the same video file in a loop. But a TV stream carries
> its own clock. At the end of each loop, the clock jumped back by three and a half minutes. The
> television believed the clock, and lost its timing on every lap."
>
> "The fix was to loop the *original video* instead, and let the clock keep counting forward — which
> is what real TV stations do. The lesson: broadcasting is a timing system that happens to carry
> data. Correct bytes are not enough; the timing must be correct too."

**Background for you.** Story 1: every transport-stream packet starts with the sync byte 0x47. In
the DVB-T receiver, the energy descrambler writes 0x47 unconditionally, so counting sync bytes
measures nothing. The honest measure is the *continuity counter* — a 4-bit counter in each packet
that must increase by one; a jump means a packet was lost or corrupted. Lab 12 counts those (the
"CC err" figure). Story 2: the stream clock is the PCR (Program Clock Reference). The loop made it
jump back 208.86 seconds each time; `03_scripts/tv_playout.py` loops the source video instead
(`VERIFICATION.md`, Lesson 7).

**Next:** "So what are *you* allowed to transmit?"

---

## S58 · What you may actually do (2 min)

**Why this slide is here.** It ends the transmit segment with a clear, legal path, so people leave
with the right habit.

**Say it like this:**

> "Three things. First: receive. You can receive anything, anywhere, all afternoon — listening
> affects nobody. Second: the licence-exempt bands in MCMC's Class Assignment. You may transmit
> there at low power, under the published conditions — read them first. Third: get licensed. An
> amateur radio licence from MCMC is the real route to transmitting properly, and the exam teaches
> you why the rules exist."
>
> "And for testing your own transmitter, use a cable and an attenuator, or a dummy load, like today."
>
> "In one line: receive freely. Transmit only where you are permitted."

**Do.** Say the last line firmly, and do not soften it. A clear close is what people will repeat to
others.

**Background for you.** `05_reference/04_malaysia.md` summarises the Malaysian bands, the Class
Assignment and amateur licensing, with links.

**Next:** "The last part of today: where you go from here."

---

# Segment 9 — Where to go next (15 minutes)

## S59 · The path, in order (3 min)

**Why this slide is here.** Order matters. Skipping ahead is the most common reason people stall.

**Say it like this:**

> "Here is the path, in order. First, the Quickstart: thirty minutes to plug in and hear a station.
> Then the introduction document — everything from this morning, in writing, at your own pace. Then
> Fundamentals 1 to 4: signals, I and Q, radio basics, and FM. Then Labs 1 to 4: build what you
> watched me build. After that, each lab tells you which document it needs. Read that document then,
> not before."
>
> "The order matters. The usual reason people stall is that they jump ahead to something exciting,
> get stuck on an idea they skipped, and give up."

**Next:** "To make it concrete, here is your first week."

---

## S60 · Your first week ★ (4 min)

**Why this slide is here.** A dated plan turns "that was interesting" into "I opened the laptop on
Monday". After the live fix (S34), this is the most important slide for beginners.

**Say it like this:**

> "Five evenings, one hour each. Monday: set it up, follow the Quickstart, and hear one station.
> Tuesday: read Fundamentals 1 and 2 — signals, and I and Q properly. Wednesday: Labs 1 and 2 — build
> the radio yourself, and add the waterfall. Thursday: Lab 3, then Fundamentals 3 and 4 to explain
> what you just built. Friday: Lab 5 — record your own piece of the radio band. Something that is
> yours."
>
> "Five evenings. One hour each. That is the whole ask. The plan is on the back of your card."

**Do.** Read all five days aloud, slowly. Point out that Friday produces something personal: their
own recording.

**Next:** "Along the way, you will make mistakes. Here are the five everyone makes."

---

## S61 · The five mistakes everyone makes (3 min)

**Why this slide is here.** A quick checklist that covers most "my SDR does not work" problems.

**Say it like this:**

> "Five mistakes, and almost every 'my radio does not work' message on the internet is one of them.
> One: gain at maximum — it amplifies the noise too. Two: no antenna, or the wrong one — the antenna
> is the cheapest part that matters most. Three: the wrong sample rate — if the rates do not match,
> everything after is wrong; remember one million divided by twenty is fifty thousand. Four:
> expecting a weak signal indoors — buildings block radio; try near a window. And five: skipping the
> fundamentals, and then blaming the radio."

**Do.** Read them quickly. This is a checklist, not a lesson. They are on the handout card.

**Next:** "And when you get stuck, here is where to look."

---

## S62 · When you get stuck (2 min)

**Why this slide is here.** It points to the reference material, especially the glossary, so
people are never stopped by an unknown word.

**Say it like this:**

> "When you get stuck, four documents help. The glossary: 248 terms, each explained in plain
> English first. A beginner's worst hour is the one spent stuck on an acronym nobody explained — this
> is for that. The signal identification guide: 'what is that thing on my waterfall?' The antenna
> guide: read it early, because it matters more than the radio. And the local guide for Malaysia:
> bands, law, licensing, and a measured survey of the FM band."
>
> "The QR code is on the last slide again, for anyone who did not photograph it."

**Next:** "Let us finish with your questions."

---

## S63 · Questions (3 min or more)

**Why this slide is here.** You promised to answer the parking-lot questions. Doing it first
shows you were listening. This slide also absorbs the 5-minute buffer.

**Say it like this:**

> "Before new questions, let me answer the ones on the whiteboard that I promised to come back to."
> — *answer each parked question briefly* — "Now, any other questions?"

**Do.** Leave this slide (with the QR code) on screen during questions. When you finish, say the
last line and mean it:

> "Everything you saw today is a folder you now have. Thank you."

**If you are asked something you cannot answer.** Say: "I do not know — but here is where I
would look," and point to the relevant document, or offer to reply later. That is a perfectly good
answer, and it shows them how to learn on their own.

<!-- end of slide notes -->

---

## ✅ Summary

- Every slide has a purpose, words to say, actions, likely questions and background — read them
  once, aloud, before the day.
- The speaker view (<kbd>S</kbd>) shows these same notes. After editing this file, run
  `python3 03_scripts/sync_speaker_notes.py`.
- The five slides you must never cut: **S9** (the line that moved), **S20** (I and Q), **S34** (the
  error fixed live), **S38** (the live build), **S60** (your first week).
- Commands for every demo are in [`DEMO_RUNSHEET.md`](./DEMO_RUNSHEET.md).
