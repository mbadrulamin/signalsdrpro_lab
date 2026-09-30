# 🎤 Presenter Script — Client Briefing

> **What this page is:** what to say on every slide of [the deck](./client_brief.html), in full
> sentences. The deck's speaker view (press **S**) shows the same words.
> **Who it is for:** you, the presenter. The audience never sees this page.
> **Time:** 150 minutes. The deck tracks your pace against the plan.

**How to read each section.** *Why this slide is here* tells you its job. *Say it like this* is
the script: read it once aloud tonight, then say it in your own words. *Do* is an action.
*If someone asks* gives short, honest answers. Longer answers are in
[QA_MILITARY.md](./QA_MILITARY.md).

**The audience.** Military end users. They want to know what the box does and what they would
use it for. They will not build anything. Speak about **their** work, not about the software.
Never use a term without saying what it means.

**The one rule for this session:** if a sentence would interest an engineer but not an
operator, leave it out.

**After editing this file,** update the deck's speaker view:

```bash
cd 03_scripts
python3 sync_speaker_notes.py --notes ../07_client_demo/PRESENTER_SCRIPT.md \
                              --deck  ../07_client_demo/client_brief.html
```

---

# Welcome (5 minutes)

## S1 · Title (1 min)

**Why this slide is here.** It sets the tone: short, plain, and about them.

**Do.** Before people arrive, start the live spectrum on the second screen (or on the TV):
`./d1_spectrum.sh` from the `demo` folder. Leave it running. Close it before Demo 1.

**Say it like this:**

> "Good morning, and thank you for your time. Today is about one small box, the SignalSDR Pro.
> You do not need any background in radio engineering. I will explain for about half an hour,
> and then the box will do the talking."

**Next:** "Here is exactly what you will see today."

---

## S2 · What you will see today (4 min)

**Why this slide is here.** It tells them what success looks like, so they know the talking has
an end and the demonstrations are coming.

**Say it like this:**

> "Today you will watch this one box do four things. It will see every signal in this room. It
> will read hidden data out of a radio station. It will record the air and replay it with no
> antenna attached. And it will transmit television to a real TV."
>
> "The first half hour is explanation, in plain words. Then there is a short break. After that,
> the box does the talking. Please ask questions at any time."

**Do.** Reveal the four lines one at a time. Pause after "a real TV".

**If someone asks:**

- *"Will we get to try it?"* — "Today is a demonstration. A hands-on workshop is one of the
  options I will show you at the end."

**Next:** "Let us start with what every radio does."

---

# 1 · What is software-defined radio (18 minutes)

## S3 · Every radio does four jobs (3 min)

**Why this slide is here.** It gives a simple frame — four jobs — that the rest of the session
hangs on.

**Say it like this:**

> "Every radio ever built does four jobs. It *catches* the wave, with an antenna. It *selects* the
> one signal you want out of thousands in the air. It *extracts* what that signal carries — a
> voice, data or a picture. And it *presents* it to you — on a speaker, a screen, or in a file."
>
> "The handheld on your belt does these four jobs. So does your phone. So does a satellite
> ground station. Keep these four words in mind: catch, select, extract, present."

**Do.** Point at each circle as you name it.

**Next:** "Now, how were radios built until recently?"

---

## S4 · The old way: one sealed box per job (3 min)

**Why this slide is here.** It connects to their own experience: a bag of single-purpose
equipment.

**Say it like this:**

> "Until recently, each job needed its own box. A handheld for one band. A scanner that can
> listen but cannot send. A spectrum analyser that measures signals but cannot decode them. A test
> transmitter that sends but cannot listen."
>
> "Each job is built into the metal inside. If you want a new job, you buy a new box. And every
> box is something you carry, power, maintain and eventually replace."

**If someone asks:**

- *"Is our issued radio like that?"* — "Many modern military radios are partly software-defined
  inside. But they are locked to their approved waveforms. You cannot load your own."

**Next:** "Software-defined radio changes that picture."

---

## S5 · Software-defined radio (4 min) ★

**Why this slide is here.** This is the one idea they should remember next week.

**Say it like this:**

> "In a software-defined radio, the hardware does as little as possible. The antenna catches the
> wave. The box turns the wave into numbers. That is all the hardware does."
>
> "Everything after that — selecting, extracting, presenting — is done by software on a laptop.
> Load one program, and the box is an FM radio. Load another, and it is a data decoder, a
> spectrum analyser, or a television transmitter."
>
> "So: the box catches the wave. Software decides what radio it is."

**Do.** Reveal the three parts in order: hardware, software, the list of radios. Say the last
sentence slowly, then pause for three seconds.

**If someone asks:**

- *"Why not do everything in software?"* — "Something has to turn the wave into numbers. That
  part must be hardware. The trick is to make it small and general."

**Background for you.** Inside the box, one radio chip (an AD9361) filters, mixes and converts
the signal. It sends up to 61.44 million sample pairs per second to the laptop over USB 3.

**Next:** "The first consequence is that one box becomes many radios."

---

## S6 · One box becomes many radios (3 min)

**Why this slide is here.** It makes the idea concrete with what they will see this afternoon.

**Say it like this:**

> "Before, you had a bag of radios. Each one was tied to one standard. When the standard
> changed, the radio became scrap."
>
> "This afternoon, in this room, the same box will be a spectrum analyser, a data decoder, a
> recorder and a television transmitter. We will not change any hardware. Only the software."

**Next:** "The second consequence matters most for a military user."

---

## S7 · A new capability is a download (2 min)

**Why this slide is here.** It states the military value of SDR in one example.

**Say it like this:**

> "Imagine a new kind of signal appears in your area of operations. With fixed radios, you need
> new equipment. That means procurement, months, money."
>
> "With a software radio, you load new software onto the box you already have. That is why
> defence organisations adopted software radio before anyone else."

**If someone asks:**

- *"Who writes the new software?"* — "An engineer, usually. Some tools already exist and are
  free. For new signals, that is where a partner like us comes in."

**Next:** "To be fair, let me tell you what SDR is bad at."

---

## S8 · What SDR is bad at (2 min)

**Why this slide is here.** Honesty builds trust. A military audience distrusts a sales pitch
with no weaknesses.

**Say it like this:**

> "Three honest weaknesses. First, it needs a computer. A laptop, power, and someone who knows
> the software. Your handheld just switches on."
>
> "Second, a very strong transmitter nearby can drown the weak signal you are looking for.
> Purpose-built receivers are better at that."
>
> "Third, this box is not a field radio. It is not rugged, not waterproof, and not certified.
> It is a tool for the lab, for training and for building things."
>
> "So your issued handheld still wins in the field. This box wins on flexibility."

**Next:** "Here is the whole idea in one sentence."

---

## S9 · In one sentence (1 min)

**Why this slide is here.** It gives them one sentence to repeat to their commander.

**Say it like this:**

> "If you remember one sentence from today: a software-defined radio is a radio whose job is
> decided by software, so one box can be many radios."

**Do.** Read it once, slowly. Then move on.

**Next:** "Now, the box itself."

---

# 2 · The SignalSDR Pro (12 minutes)

## S10 · The SignalSDR Pro (2 min)

**Why this slide is here.** Holding the box makes it real.

**Say it like this:**

> "This is the SignalSDR Pro. It is smaller than your hand. It connects to a laptop with one
> USB cable. In the setup we use today, one antenna listens and one sends."
>
> "Please pass it round. Everything I just described — the part that turns waves into numbers —
> is on this board."

**Do.** Pass a **spare** board round if you have one. Do **not** pass round the one wired up for
the demos. If there is no spare, hold it up and offer it on the table afterwards.

**Background for you.** The board has four antenna connectors. In the B210 mode used here, only
two work: `TX/RX` (labelled TX2A) and `RX2` (labelled RX2A). The software calls the box "B210"
because it copies the commands of a well-known research radio, the Ettus USRP B210.

**Next:** "Here are its numbers, in plain words."

---

## S11 · The numbers, in plain words (3 min)

**Why this slide is here.** Specifications mean nothing until they are translated into use.

**Say it like this:**

> "Seventy megahertz to six gigahertz. That is from FM radio up to 5.8-gigahertz Wi-Fi and
> drone links. I will show you what lies in between on the next slide."
>
> "Fifty-six megahertz at once. That is how much of the air it sees in one go. Enough for a
> whole band."
>
> "Transmit and receive together. It can listen and send at the same moment."
>
> "A GPS-locked clock. Its frequency and time are corrected by satellites, so measurements are
> accurate anywhere."
>
> "And it connects to a laptop by USB 3. No rack, no lab bench."

**If someone asks:**

- *"How far can it receive?"* — "That depends on the antenna and the signal, not on the box. The
  same box hears nothing with the wrong antenna and a great deal with the right one."
- *"How much power does it transmit?"* — "Very little: well under a tenth of a watt. That is a
  feature for training and testing, not a weakness."
- *"What about below 70 MHz — HF?"* — "Not covered directly. It needs an extra converter."

**Next:** "What does 70 megahertz to 6 gigahertz actually cover?"

---

## S12 · What that range covers (2 min)

**Why this slide is here.** It shows that almost everything relevant to them is in range.

**Say it like this:**

> "This line runs from 70 megahertz on the left to 6 gigahertz on the right. FM radio. The
> aircraft voice band. Military UHF. Car keys and remote controls at 433. Television. Mobile
> phones. Aircraft identification at 1090. GPS. Wi-Fi and drone links at 2.4 and 5.8 gigahertz."
>
> "Almost everything your unit transmits, or faces, sits somewhere on this line."

**Do.** Point along the line from left to right.

**If someone asks:**

- *"Can it receive GPS?"* — "It can see the GPS band. Using it as a GPS receiver needs extra
  software. It also has its own GPS clock built in."

**Next:** "The most useful number is 56 megahertz. Here is why."

---

## S13 · 56 MHz wide: a window, not a keyhole (2 min)

**Why this slide is here.** Wide bandwidth is the box's biggest advantage over a scanner, and
it is hard to grasp without a picture.

**Say it like this:**

> "A normal radio is a keyhole. It shows you one channel. You only know what is on the channel
> you chose."
>
> "This box is a window. It sees up to 56 megahertz at once — every channel in a band, together.
> It can record all of it, too."
>
> "So a short burst on a channel you were not watching does not slip past you."

**Next:** "Where does it sit among other equipment?"

---

## S14 · Where it sits (2 min)

**Why this slide is here.** It sets expectations: more capable than a hobby dongle, far smaller
and cheaper than a rack system.

**Say it like this:**

> "On the left, a cheap USB dongle. It receives a narrow slice, cannot transmit, and stops below
> two gigahertz. Good for hobbyists."
>
> "On the right, rack-mounted systems. Very wide, very capable, and they live in a vehicle or a
> shelter."
>
> "The SignalSDR Pro sits in between. It is serious enough to train on real signals, and small
> enough to take anywhere."

**If someone asks:**

- *"How much does it cost?"* — Give the current price from your sales sheet. Do not guess.

**Next:** "Just as important is what it is not."

---

## S15 · What it is not (1 min)

**Why this slide is here.** It prevents the wrong expectations, which would cost trust later.

**Say it like this:**

> "It is not a certified electronic-warfare system. It is not a direction finder on its own: in
> this setup it has one receive channel, and finding direction needs at least two. And it is
> not a code-breaker. It cannot read encrypted traffic."
>
> "It is a flexible radio for learning, testing and building. That is its value."

**Next:** "So what can it do for you? Six things."

---

# 3 · What it can do (12 minutes)

## S16 · Six things it can do for you (1 min)

**Why this slide is here.** A map of the capabilities, and an honest note of which ones they will
see today.

**Say it like this:**

> "Here are six things this box can do for a military user. The green badges are things you will
> see working today. The amber one you will see in part. The red one needs more hardware, and I
> will explain why."

**Next:** "The first two go together."

---

## S17 · See the spectrum. Identify what is on it. (2 min)

**Why this slide is here.** Spectrum awareness is the capability most relevant to them, and the
easiest to understand.

**Say it like this:**

> "The first two capabilities are seeing the spectrum and identifying what is on it. You can
> survey a site before an exercise or a deployment. You can spot a transmitter that should not be
> there. And you can check your own emissions: what does your unit look like to someone else who
> is listening?"
>
> "You cannot protect, use or deny a frequency that you cannot see."

**If someone asks:**

- *"Can it tell us what a signal is automatically?"* — "For known signal types, yes: there are
  decoders that name them. For an unknown signal, it measures it — frequency, width, timing — and
  a trained person identifies it. You will see both today."

**Next:** "The next two are about time."

---

## S18 · Record now. Find it later. (2 min)

**Why this slide is here.** Recording is an unexpected capability for most users, and it
matters for evidence and training.

**Say it like this:**

> "Capabilities three and four. You can record a whole band — not just the sound, the raw signal
> — and study it indoors later, as many times as you like."
>
> "You can train operators on real signals from the field, without going back to the field."
>
> "And you can detect short bursts: a remote trigger, a tracker checking in, a telemetry link."
>
> "A signal you missed is gone — unless you recorded the band."

**If someone asks:**

- *"How big are the recordings?"* — "Large. At the settings we use today, about one gigabyte
  per minute. A normal laptop disk holds hours."

**Next:** "Capability five: it transmits."

---

## S19 · Transmit (2 min)

**Why this slide is here.** Transmitting is powerful and regulated. Frame it as testing and
training.

**Say it like this:**

> "Capability five: the box can transmit, anywhere from 70 megahertz to 6 gigahertz. That lets you
> test your receivers with a known, controlled signal. It lets you train operators against
> realistic target signals. And it lets engineers prototype a data link before buying dedicated
> hardware."
>
> "Always inside a licence, or inside a shielded room. I will come to the rules in a moment."

**If someone asks:**

- *"Can it jam?"* — "Technically, any transmitter can interfere. Jamming is a criminal offence
  outside authorised military use, and we do not demonstrate or support it. For authorised
  electronic-warfare training, the right place is a shielded range, under your own authority."

**Next:** "The sixth capability is one you will not see today."

---

## S20 · Locate a transmitter. Passive radar. (2 min)

**Why this slide is here.** They will ask about direction finding. Answer it before they ask,
honestly.

**Say it like this:**

> "Finding where a transmitter is — direction finding — and passive radar both need two or more
> receivers, locked to the same clock, looking at the same signal. In the setup we use, this box
> has one receive channel."
>
> "So this box can be one part of such a system, with more hardware and more engineering. It is
> possible as a project. It is not something to expect out of the box."

**If someone asks:**

- *"Could two boxes do it?"* — "In principle, yes. Two boxes, a shared clock and the right
  software. That would be a project, and we would scope it with you."

**Next:** "Before the demonstrations, the legal line."

---

## S21 · Listening is easy. Transmitting is licensed. (3 min)

**Why this slide is here.** A military audience respects rules. Saying them before the transmit
demo makes the demo credible, not careless.

**Say it like this:**

> "Receiving broadcast radio and television is allowed. Receiving other people's traffic needs
> care: under the Communications and Multimedia Act 1998, section 234, unauthorised interception
> is an offence. Decrypting encrypted traffic is prohibited."
>
> "Transmitting without an assignment from MCMC is an offence. Jamming or interfering is a
> criminal offence."
>
> "Your unit's authority to transmit comes from MCMC and your chain of command. It does not come
> from the box. The box will transmit on any frequency. The responsibility stays with the
> person at the keyboard."

**If someone asks:**

- *"Does military use change this?"* — "Your own authorities and assignments apply. I cannot
  advise on those. Everything I show today stays within civilian rules."
- *"Then how can you transmit TV today?"* — "At the lowest power that works, over a few metres,
  in a controlled room, for a few minutes. I will say that again before I do it."

**Next:** "Let us take ten minutes. After the break, the box does the talking."

---

# Break (10 minutes)

## S22 · Break (10 min)

**Why this slide is here.** It gives you ten minutes to set up the demos without an audience.

**Do.** During the break:

- Close the live spectrum from S1.
- Run `./preflight.sh` in the `demo` folder. It must not say FAIL.
- Make the terminal font large. Put the terminal where the room can see it.
- Check the TV box is on and showing its menu.
- Put the [run sheet](./DEMO_RUNSHEET.md) beside the laptop.

**Say it like this (at the end of the break):**

> "Welcome back. Everything you are about to see is this one box and this one laptop."

**Next:** "Six demonstrations."

---

# 4 · Demonstrations (70 minutes)

Every demo is on [the run sheet](./DEMO_RUNSHEET.md), with commands, fallbacks and resets. These
notes only give the opening line and the point to land. The planned minutes include spare time.

## S23 · Six demonstrations (2 min)

**Why this slide is here.** It shows the order, so the room can follow.

**Say it like this:**

> "Six demonstrations. First we see. Then we decode. Then we survey a few bands. Then we record,
> then we look at noise, and last, we transmit."
>
> "If something does not work in this building, I have a recording of it working last night, and
> I will say so."

**Do.** Remember the 30-second rule: no recovery in 30 seconds means the fallback.

**Next:** Demo 1.

---

## S24 · Demo 1 — See the invisible (7 min)

**Why this slide is here.** The first live picture. It is the foundation for every other demo.

**Do.** `./d1_spectrum.sh`. Run sheet: [Demo 1](./DEMO_RUNSHEET.md#demo-1--see-the-invisible).

**Say it like this:**

> "Before you can use, protect or deny a frequency, you have to see who is on it. This is
> 20 megahertz of the air in this room, right now. Every bright stripe is someone transmitting.
> A normal radio shows you one station. This shows you all of them at once."

**Point to land:** step one of any operation is knowing who is on the air.

**Next:** "Now let us pull something out of one of those signals."

---

## S25 · Demo 2 — Hidden data (12 min)

**Why this slide is here.** It turns "a signal" into "information". This is intercept and
identify, on a harmless target.

**Do.** `./d2_rds.sh`. Type `89.7e6`, `200e3`, gain `60`. Run sheet:
[Demo 2](./DEMO_RUNSHEET.md#demo-2--hidden-data-inside-a-radio-station).

**Say it like this:**

> "This is BFM, an ordinary radio station. Under the sound, it carries a slow data channel with
> its name. Watch the terminal."
>
> *(When the name appears.)* "That text came out of the air. The box found the signal, measured
> it and read it. The same idea finds the identity inside a drone link or a tracker."

**Point to land:** find a signal, pull out what it carries.

**If someone asks:**

- *"Could it read our radios?"* — "Not encrypted ones. And listening to other people's traffic
  has legal limits, as we saw. Broadcast stations like BFM are meant for the public."

**Next:** "Now a quick tour of the busiest bands."

---

## S26 · Demo 3 — Tour the busy bands (14 min)

**Why this slide is here.** It shows the width of the box's range and teaches that signals have
recognisable shapes.

**Do.** `./d3_bands.sh`, then `89.9e6` → `945e6` → `2.437e9`. Close it, then
`./d3_bands.sh scan`. Run sheet: [Demo 3](./DEMO_RUNSHEET.md#demo-3--tour-the-busy-bands).

**Say it like this:**

> "One box, from radio to Wi-Fi. FM radio is steady: always on, always in the same place. Mobile
> phone towers are dense blocks. Wi-Fi flickers: it only transmits when someone is using it."
>
> "An operator learns to recognise a signal by its shape, before decoding anything."
>
> *(During the scan.)* "This checks each TV channel and names what it finds. It also flags
> anything that is not TV. That is how you would look for an intruder in a band that should be
> quiet."

**Do (bonus).** If there is time and goodwill, the [car key](./DEMO_RUNSHEET.md#bonus--the-car-key).

**Next:** "Now, a signal that is no longer in the air."

---

## S27 · Demo 4 — Record now, analyse later (6 min)

**Why this slide is here.** It proves recording, and it gives the radio a rest if it has been
difficult.

**Do.** Unscrew the antenna in front of them. `./d4_replay.sh`, offset `200e3`. Run sheet:
[Demo 4](./DEMO_RUNSHEET.md#demo-4--record-now-analyse-later).

**Say it like this:**

> "No antenna. Last night I recorded twenty seconds of this band — not the sound, the whole raw
> signal. Now I can replay it and choose any station that was in the air at that moment."
>
> "Record a whole band today. Decide next week what you are looking for."

**Point to land:** evidence you can replay, training you can repeat.

**Do.** Screw the antenna back onto `TX/RX` before the next demo.

**Next:** "Why do links fail? Let me show you."

---

## S28 · Demo 5 — Noise against a signal (5 min)

**Why this slide is here.** It shows, in one picture, what range and jamming do to a digital
link. No radio is used, so it cannot fail.

**Do.** `./d5_bpsk.sh`. Drag **Eb/N0** from 8 down to 0, then back. Run sheet:
[Demo 5](./DEMO_RUNSHEET.md#demo-5--noise-against-a-clean-signal).

**Say it like this:**

> "This is a simulated digital link. Each dot is one symbol: a zero or a one. I will add noise."
>
> *(Drag down.)* "The dots swell into clouds. When the clouds touch, the receiver starts guessing
> wrong — watch the error count. That is the edge of your range, or the moment a jammer wins."
>
> *(Drag back.)* "Remove the noise, and the link recovers at once."

**Next:** "Last demonstration. This one transmits."

---

## S29 · Demo 6 — Television to your TV (20 min)

**Why this slide is here.** The strongest image of the day: their own kind of television, fed
by the box.

**Do.** `./d6_tv.sh`. TX digital amplitude `0.25`, then raise TX RF gain slowly. Scan the TV
box on channel 21, 474 MHz. Run sheet:
[Demo 6](./DEMO_RUNSHEET.md#demo-6--television-from-this-box-to-your-tv).

**Say it like this (before you start — do not skip):**

> "This is a licensed TV channel. So we transmit at the lowest power that works, over a few
> metres, in a controlled room, for a few minutes. Receiving is free. Transmitting needs a
> licence."

> *(While the TV scans.)* "This is a real digital television signal, the same standard MYTV uses.
> It was made entirely in software on this laptop. The box has no television chip inside."

> *(When the picture appears.)* "Your TV cannot tell the difference between this and a real
> broadcaster. That is the point. This box can make any signal in its range: a TV channel, a test
> signal, a training target."

**If it fails.** After 3 minutes, use `./d6_fallback_loop.sh`: the box sends TV to itself.
Say so honestly.

**Do (always).** Close the window. Run `./stop_all.sh`. Say out loud: "The transmitter is off."

**Next:** "Let me put the six demonstrations side by side."

---

## S30 · What you just saw (4 min)

**Why this slide is here.** It ties each demo back to a capability, so they leave with the
capability list, not with a memory of software windows.

**Say it like this:**

> "Six demonstrations, six capabilities. The air in this room: seeing the spectrum. A station's
> name: identifying and extracting data. Four bands and a scan: survey. No antenna: record and
> replay. Two dots becoming clouds: why links fail. Your TV: transmit."
>
> "One box. We did not change any hardware all afternoon."

**Do.** Take questions about the demos here. This slide absorbs spare time.

**Next:** "Which software would your people actually use?"

---

# 5 · The software (8 minutes)

## S31 · Three levels of user (3 min)

**Why this slide is here.** It answers their real question: "what would my operators use?"

**Say it like this:**

> "There are three levels of user. Level one: look and listen. Programs like gqrx or SDR++. Point
> and click. You tune, see, listen and record. This is where operators live."
>
> "Level two: ready-made decoders. One tool per signal type. For example, rtl_433 decodes
> hundreds of small wireless devices, and dump1090 shows aircraft positions."
>
> "Level three: build your own, with GNU Radio. Any signal, any process. That is for engineers."
>
> "Most users never go beyond level one. That is fine."

**If someone asks:**

- *"Do these cost money?"* — "All the programs named here are free and open source."

**Next:** "The easiest way to get all of them is one system: DragonOS."

---

## S32 · DragonOS: everything, already installed (3 min)

**Why this slide is here.** It gives them a practical next step for their own machines.

**Say it like this:**

> "DragonOS is a free Linux system built for software radio. All three levels of software come
> preinstalled and already work with this box. It can run from a USB stick without touching the
> laptop's own system, or be installed properly."
>
> "It is our recommendation for your own machines. Today's laptop runs ordinary Ubuntu Linux with
> the tools added by hand. We can prepare DragonOS for you."

**If someone asks:**

- *"Is it secure enough for our networks?"* — "It is a general-purpose Linux system. For a
  classified network, your own IT security team must approve it. For a stand-alone training
  laptop, it is ideal."

**Next:** "Where does GNU Radio fit in all this?"

---

## S33 · Where GNU Radio fits (2 min)

**Why this slide is here.** It removes any fear that operators must learn a programming tool.

**Say it like this:**

> "Demonstrations 2, 4, 5 and 6 were built in GNU Radio. You saw the result, never the inside.
> Engineers build the tools. Operators use them."
>
> "Your operators do not need to learn GNU Radio to use this box."

**If someone asks:**

- *"Can we see the inside?"* — "Yes, after the session. We have a full training course for
  engineers who want to build their own."

**Next:** "Finally: what you may do with it, and what we propose."

---

# 6 · Where next (15 minutes)

## S34 · What you may do with it (3 min)

**Why this slide is here.** A practical summary of the rules, for their own use of the box.

**Say it like this:**

> "Receiving broadcast radio and TV is allowed. Transmitting in licence-free bands, at low power,
> is allowed within the limits: 433 megahertz, 919 to 923 megahertz, and 2.4 gigahertz."
>
> "Transmitting into a cable or a shielded room is the safe default for training. Anywhere else
> needs an assignment. And aviation, maritime and emergency frequencies: never."

**Background for you.** Limits from MCMC's Class Assignment: 433–435 MHz at 100 mW EIRP; 919–923
MHz and 2400–2500 MHz at 500 mW EIRP. It is revised from time to time; check the current version
before quoting. See [the Malaysia reference](../05_reference/04_malaysia.md#4-licence-exempt-bands-class-assignment).

**Next:** "Here is how we suggest going further."

---

## S35 · What we propose (4 min)

**Why this slide is here.** It turns interest into a next step.

**Say it like this:**

> "Three options. A hands-on workshop: one or two days where your people drive the box, on your
> own laptops with DragonOS. A mission pilot: you pick one real problem, and we build and test
> the tool for it. Or a training package: recorded signals, exercises and instructor notes for
> your schools."
>
> "Our advice is to start small. One problem, one team, a few weeks."

**Do.** Ask: "Which of these is closest to what you need?" Then listen.

**Next:** "Questions."

---

## S36 · Questions (8 min)

**Why this slide is here.** It leaves the QR code and the one-line message on screen while you
answer.

**Say it like this:**

> "Thank you. Any questions?"

**Do.** Keep this slide on screen. Use [QA_MILITARY.md](./QA_MILITARY.md) for the questions you
expect. Hand out the [one-page handout](./client_handout.html).

**If you are asked something you cannot answer.** Say: "I do not know. I will find out and reply
to you by email." Write it down in front of them. Then do it.

**Finish with:**

> "One box, many radios. Thank you for your time."

<!-- end of slide notes -->

---

## ✅ Summary

- 36 slides, 150 minutes. The explanation is about 45 minutes; the demonstrations are 70.
- Every slide speaks about **their** work. No equations, no code on screen.
- The legal line is said twice: on S21, and again before Demo 6.
- Honest limits are part of the script: S8, S15 and S20.
- After changing this file, run `sync_speaker_notes.py` with `--notes` and `--deck`.

**Next:** [The run sheet →](./DEMO_RUNSHEET.md)
