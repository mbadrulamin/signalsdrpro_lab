# ❓ Questions They Will Ask — Honest Answers

> **What this page is:** about 30 questions a military audience is likely to ask, with short,
> honest answers you can say out loud.
> **How to use it:** read it once tonight. On the day, keep it printed beside the run sheet.
> **The rule:** never claim more than we have shown. "I do not know, I will find out" is a good
> answer. A wrong answer to this audience costs more than no answer.

---

## Contents

1. [What it can and cannot do](#1-what-it-can-and-cannot-do)
2. [Specific military uses](#2-specific-military-uses)
3. [Legal and security](#3-legal-and-security)
4. [Practical questions](#4-practical-questions)
5. [Is what we saw real?](#5-is-what-we-saw-real)

---

## 1. What it can and cannot do

**Can it find where a transmitter is (direction finding)?**
Not on its own. Direction finding needs two or more receivers locked to the same clock. In the
setup we use, this box offers one receive channel. Two or more boxes with a shared clock could
do it. That is a project we would scope with you.

**Can it read encrypted traffic?**
No. It receives the signal, not the meaning. If the content is encrypted, the box shows you
that a signal exists, how strong it is and how it behaves — not what it says. Decrypting
traffic is also prohibited under Malaysian law.

**How much of the spectrum can it watch at once?**
Up to 56 MHz at once. That covers a whole band, such as the entire FM broadcast band, in one
view. To watch more, it steps across bands one after another.

**How far away can it hear a signal?**
That depends on the antenna, the signal's power and the ground between, not on the box. Today's
small indoor antenna picks up FM stations whose transmitters are many kilometres away. A proper
outdoor antenna reaches much further, and weaker signals. Aircraft identification signals are often heard 200 km away with a good
antenna.

**How much power does it transmit?**
Very little: well under a tenth of a watt. That is right for testing and training. It is not a
long-range transmitter, and it is not meant to be one.

**Does it cover HF (below 30 MHz)?**
No. Its range starts at 70 MHz. HF needs an extra converter in front of it.

**Can it follow frequency-hopping radios?**
It can *see* a hopping radio across up to 56 MHz at once: the hops show as short bursts jumping
around the waterfall. Following and decoding it is a much harder, specialist job, and not
something this box does out of the box.

**Is it rugged enough for the field?**
No. It is a bare board or small case, not sealed, not tested to military standards. Use it in a
vehicle, an office or a classroom, or put it in a suitable rugged enclosure.

**What is it bad at?**
Three things. It needs a laptop and someone who knows the software. A very strong transmitter
close by can drown the weak signal you want. And it is not rugged or certified. Your issued
equipment still wins in the field; this box wins on flexibility.

---

## 2. Specific military uses

**Can it detect drones?**
It can see the radio links many consumer drones use, at 2.4 GHz and 5.8 GHz, as bursts on the
waterfall. Telling a drone apart from Wi-Fi needs a trained eye or specific software. It is a
good tool for learning and testing detection. It is not a certified counter-drone system.

**Can it stop a drone?**
We do not demonstrate or support jamming. Interfering with a radio link is a criminal offence
outside authorised use. For authorised counter-drone work, you need certified equipment and
your own legal authority.

**Can it detect remote triggers, like those used for improvised devices?**
It can detect short bursts in the bands those triggers commonly use, such as 433 MHz — that is
the car-key demonstration. That makes it useful for training operators to recognise such
signals. It is not a certified protection system, and must not be relied on as one.

**Can it jam?**
Technically, any transmitter can interfere with others. Jamming is a criminal offence under
Malaysian law outside authorised use. We do not demonstrate or supply jamming. Authorised
electronic-warfare training belongs on a shielded range, under your own authority.

**Can it track ships and aircraft?**
Yes, in principle. Aircraft send identification on 1090 MHz, and ships on about 162 MHz. Free
decoders exist for both. We have a working aircraft decoder, but indoors at our lab no aircraft
signal reached us, so we did not show it live today. With an outdoor antenna, it is routine.

**Can it see mobile phones?**
It can see the mobile network's signals — you saw the phone-tower band in Demo 3. It cannot
read calls or messages, which are encrypted. Pretending to be a phone tower is illegal, and we
do not do it.

**Can it read our own radios?**
It can see them: frequency, strength, timing. If they are encrypted, it cannot read them. It is
useful for checking your own emissions: what your unit looks like to someone listening.

**Can it fake GPS?**
Transmitting on GPS frequencies is illegal and dangerous. We do not do it. The box has its own
GPS receiver for its clock, and can receive the GPS band for study.

**Could it be used for training our signals operators?**
Yes. This is its strongest use. Record real signals once, then train on them indoors, as many
times as you like. Transmit known test signals into a shielded room. Show students what noise
and interference do. That is exactly what the training package would build.

**Could several boxes work together?**
Yes, with engineering work. Several boxes can share a clock and be controlled from one laptop.
That is how direction finding or wider coverage would be built. It would be a project, not a
product.

---

## 3. Legal and security

**Is it legal to own?**
Yes. Owning a receiver and transmitter is legal. What matters is how you use it: what you listen
to, and where you transmit.

**What may we listen to?**
Broadcast radio and TV are free for anyone. Other people's traffic needs care: under the
Communications and Multimedia Act 1998, section 234, unauthorised interception, and disclosing
what you intercepted, is an offence. Your own authorities may differ; I cannot advise on those.

**Where may we transmit?**
In licence-free bands at low power (433–435 MHz, 919–923 MHz, 2.4 GHz, within MCMC's limits),
into a cable or shielded room, or under an assignment from MCMC or your own authority. Never on
aviation, maritime or emergency frequencies.

**You transmitted TV today. Was that legal?**
It was a licensed channel, at the lowest power that worked, over a few metres, for a few minutes,
in a controlled room. The correct setup for regular use is a cable or a shielded room. We said
so before we started.

**Does any data leave the laptop?**
No. Everything runs on the laptop. Nothing needs the internet. The software is open source, so
your own team can inspect it.

**Is the software from a trusted source?**
GNU Radio and the radio driver are open-source projects used by universities, industry and
defence worldwide. Your IT security team can review them. For classified networks, their
approval is needed.

**Is the box subject to export control?**
I will confirm this with our supplier and reply in writing. Do not answer from memory.

---

## 4. Practical questions

**What do we need to run it?**
The box, two antennas, a USB 3 cable, and a laptop with Linux and 8 GB of memory. We recommend
DragonOS: free, with all the software preinstalled.

**Does it work with Windows?**
Some tools do. Most software-radio tools are best on Linux. DragonOS avoids the problem: it runs
from a USB stick without touching Windows.

**How long does it take to learn?**
An operator can use a point-and-click tool like gqrx in an afternoon. Using ready-made decoders
takes a few days. Building new tools in GNU Radio takes weeks to months, and is for engineers.

**How much does it cost?**
Quote from the current price list. Do not guess.

**What support do we get?**
Say what our company offers: the workshop, the mission pilot, the training package. Also the
full course material, which is free and on GitHub.

**Can we keep the recordings as evidence?**
The recordings are exact copies of what the radio received, with the time and frequency in the
file name. Whether they are accepted as evidence is a legal question for your own advisers.

---

## 5. Is what we saw real?

Someone may ask whether a demo was staged. Be precise. These are the honest facts from the
[verification record](../VERIFICATION.md).

**Everything in Demos 1, 2 and 3 was live**, received in the room. The station name in Demo 2
was decoded from BFM 89.9's real broadcast.

**Demo 4 was a real recording**, made the night before on this radio, and replayed.

**Demo 5 is a simulation**, and we said so. Its error rate was checked against theory.

**Demo 6 was real transmission.** The TV result was also confirmed by the lab owner on a DVB-T2
television on 26 September 2026. One honest gap: no recording of that earlier test was made.

**Where we were wrong once.** On 26 September 2026 a status reading on the radio said "unlocked",
and we first concluded the radio was faulty. Measurements then showed it was working perfectly;
the reading is unreliable on this board. We wrote that down
([Lesson 14](../VERIFICATION.md#lesson-14--a-status-reading-said-broken-the-measurements-said-fine)).
If asked, say it: it shows we measure rather than assume.

**What we have not shown:** real aircraft decoded at our location, direction finding, and
anything below 70 MHz.

---

## ✅ Summary

- **Say what it does, and what it does not.** DF, decryption, jamming and ruggedness are the
  four "no" answers. Say them plainly.
- **Legal answers are short:** receive broadcast freely; take care with other traffic; transmit
  only with authority; never decrypt or jam.
- **Training is the strongest use case.** Steer towards it.
- **Never guess** prices, export status or your client's own rules. Write the question down and
  reply in writing.

**Next:** [The one-page handout →](./client_handout.html)
