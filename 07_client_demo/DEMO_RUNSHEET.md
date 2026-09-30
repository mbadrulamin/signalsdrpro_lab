# 🎬 Demo Run Sheet — Client Briefing

> **What this page is:** the six live demonstrations, one card each. Print it and keep it beside
> the laptop.
> **How to use it:** each card says what to type, what the room will see, what to say, and what
> to do if it fails.
> **Time:** about 55 minutes of demos, inside a 70-minute block. The spare 15 minutes is for
> questions and for anything that goes wrong.

---

## Contents

- [The three rules](#the-three-rules)
- [The six demos at a glance](#the-six-demos-at-a-glance)
- [Demo 1 — See the invisible](#demo-1--see-the-invisible)
- [Demo 2 — Hidden data inside a radio station](#demo-2--hidden-data-inside-a-radio-station)
- [Demo 3 — Tour the busy bands](#demo-3--tour-the-busy-bands)
- [Bonus — the car key](#bonus--the-car-key)
- [Demo 4 — Record now, analyse later](#demo-4--record-now-analyse-later)
- [Demo 5 — Noise against a clean signal](#demo-5--noise-against-a-clean-signal)
- [Demo 6 — Television from this box to your TV](#demo-6--television-from-this-box-to-your-tv)
- [If the radio behaves strangely](#if-the-radio-behaves-strangely)

---

## The three rules

1. **Close each window before the next demo.** Only one program can use the radio at a time.
   If a demo says the radio is busy, run `./stop_all.sh`.
2. **The 30-second rule.** If a demo has not recovered in 30 seconds, open its recording from
   [`fallbacks/`](./fallbacks/) and say: *"The radio is not cooperating in this building. Here is
   the same thing working last night."* Then move on. Never debug in front of the room.
3. **Talk about them, not about the software.** Every card starts with a *"Why you care"* line.
   Say that line first.

All commands are run from the `demo` folder:

```bash
cd "/home/ubuntu/GNU Radio/signalsdrpro_lab/07_client_demo/demo"
```

---

## The six demos at a glance

| # | Min | Demo | Command | Radio? | Fallback |
|---|---|---|---|---|---|
| 1 | 6 | See the invisible | `./d1_spectrum.sh` | receive | `fallbacks/d1_spectrum.*` |
| 2 | 10 | Hidden data inside a radio station | `./d2_rds.sh` | receive | `./d2_rds.sh test` |
| 3 | 12 | Tour the busy bands | `./d3_bands.sh`, then `./d3_bands.sh scan` | receive | `./d3_bands.sh test` |
| 4 | 5 | Record now, analyse later | `./d4_replay.sh` | **none** | `fallbacks/d4_replay.*` |
| 5 | 4 | Noise against a clean signal | `./d5_bpsk.sh` | **none** | — (cannot fail on the radio) |
| 6 | 18 | Television to your TV | `./d6_tv.sh` 🚨 | **transmits** | `./d6_fallback_loop.sh` 🚨 |

Demos 4 and 5 use no radio at all. They sit in the middle on purpose: if the radio misbehaves
in Demo 3, they buy you time to fix it quietly.

---

## Demo 1 — See the invisible

**Why you care:** *"Before you can use, jam or protect a frequency, you have to see who is on
it. This is the first thing an operator does anywhere new."*

| | |
|---|---|
| **Time** | 6 minutes |
| **Command** | `./d1_spectrum.sh` |
| **Settings** | 98 MHz centre, 20 MHz wide, gain 50, antenna on `TX/RX` |

**What the room sees:** a window with two pictures.

- The **top** is a graph: left to right is frequency, up is strength. Every hump is a radio
  station.
- The **bottom** is a **waterfall**: the same graph, stacked over time, so it scrolls downwards.
  Bright stripes are signals that stay on the air.

**Say it like this:**

1. *"This is 20 megahertz of the sky, right now, in this room. Everything bright is someone
   transmitting."*
2. Point at a hump. *"That is a radio station. You cannot hear it, but the box sees it."*
3. *"A normal radio shows you one station. This shows you all of them at once."*

**Do:** type `89.9e6` into the **Center Frequency** box. The stations move sideways. *"I just
retuned it by typing. No knobs, no new hardware."*

**If it fails**

| What you see | Do this, within 30 seconds |
|---|---|
| `No devices found` | Something else holds the radio: `./stop_all.sh`, then try again once. Then the fallback |
| A flat line, no humps | Type `60` into the gain box. Still flat: the antenna is on the wrong port — it must be `TX/RX` |
| Letters `O` stream in the terminal | The laptop is too slow for 20 MHz. Ignore it; the picture still works |

**Reset:** close the window.

💡 **Tip:** if gqrx was installed and tested last night, you may use it here instead. It looks
friendlier. If it was not tested, do not try it today.

---

## Demo 2 — Hidden data inside a radio station

**Why you care:** *"Most signals carry more than you can hear. Here we pull text out of a signal
that sounds like music. The same idea finds the ID inside a drone link, a tracker or a data
burst."*

| | |
|---|---|
| **Time** | 10 minutes |
| **Command** | `./d2_rds.sh` |
| **Settings to type** | FM Station `89.7e6` · Channel Offset `200e3` · RF Gain `60` (range 55–65) |
| **Wait** | up to 30 seconds for the first name |

**What the room sees:**

- A window with the station's spectrum and a small dot diagram.
- In the **terminal**, lines like `[RDS] ... PS='BFM 89.9'`. The name changes while you watch:
  `BUSINESS`, then `BFM 89.9`, then `FINANCE`.

Put the terminal where the room can see it. **The text is the payoff, not the sound.**

**Say it like this:**

1. *"This is BFM, a normal radio station. You hear music or talk."*
2. *"Hidden under the sound is a slow data channel called RDS. It carries the station's name."*
3. When the name appears: *"That text came out of the air. Nobody told the box the name. It
   found the signal, measured it, and read it."*
4. *"This is what 'intercept and identify' means. Find a signal, pull out what it carries."*

**If it fails**

| What you see | Do this, within 30 seconds |
|---|---|
| Sound, but no `[RDS]` lines after 30 s | Raise RF Gain to 65. Check the offset is `200e3`, not `-200e3` |
| Distorted, crackly sound | Lower RF Gain to 50 |
| No sound and no text | Check the station field says `89.7e6`. Then close it and run the fallback |
| Still nothing | Close it. Run `./d2_rds.sh test` and **say it is a test signal made on this laptop** |

> ⚠️ **Warning:** the signal here changed by about 30 dB between morning and evening on
> 26 September 2026. Use the gain you wrote down in tonight's rehearsal, not the one above.

**Reset:** close the window.

---

## Demo 3 — Tour the busy bands

**Why you care:** *"One box, from 70 MHz to 6 GHz. Radio, phones, Wi-Fi, television — the same
box sees all of it. Every one of these is a band your equipment shares with other people."*

| | |
|---|---|
| **Time** | 12 minutes (8 tour + 4 scan) |
| **Part 1** | `./d3_bands.sh` — the live spectrum |
| **Part 2** | close Part 1, then `./d3_bands.sh scan` — the TV channel scanner |

### Part 1 — the tour

Type each frequency into the **Center Frequency** box. Stop for about 90 seconds at each one.

| Type | What it is | What the room sees | Say |
|---|---|---|---|
| `89.9e6` | FM radio | Wide, steady humps | *"Broadcast: always on, always in the same place."* |
| `945e6` | Mobile phone towers | Dense, flat-topped blocks | *"Towers talking to phones. This is the network everybody in this room is on."* |
| `2.437e9` | Wi-Fi channel 6 | Short bursts that flicker on and off | *"Wi-Fi. It only transmits when there is data. That flicker is people using it."* |

Then say: *"Three signals, three shapes. An operator learns to recognise a signal by its shape,
before decoding anything."*

### Part 2 — the TV scanner

Close the window. Run `./d3_bands.sh scan`. It takes about 20 seconds.

**What the room sees:** a table in the terminal, one line per TV channel from 21 to 36. Each line
says whether the channel is empty, carries television, or carries **something else**.

**Say it like this:** *"This is the first step of automatic survey. The box checks each channel
and names what it finds. It also flags signals that are not TV, which is exactly what you would
look for in a band that should be quiet."*

> 💡 **Tip:** indoors, most channels may show as empty. That is fine. Say: *"Indoors, behind
> concrete, most are too weak. Outside with a proper antenna, this table fills up."*

**If it fails**

| What you see | Do this, within 30 seconds |
|---|---|
| Nothing visible at 945 MHz or 2.437 GHz | The FM antenna is weak at these frequencies. Raise gain to 65. Still nothing: say so honestly and move on |
| The scanner says the radio is busy | Part 1 is still open. Close it, or `./stop_all.sh` |
| The scanner fails | Run `./d3_bands.sh test`. It uses no radio and shows the scanner rejecting a false alarm |

**Reset:** close the window.

### Bonus — the car key

**Only if the room is warm and you have time.** Its absence costs nothing.

1. Run `./d3_bands.sh` again and type `433.92e6`.
2. Ask: *"Did anyone drive here? May I borrow your car key for ten seconds?"*
3. Hold the key near the antenna and press the lock button.
4. **The room sees:** a sudden bright burst on the waterfall, then silence.
5. **Say:** *"That is a remote trigger. Garage doors, alarms, and some improvised devices use this
   same band. This is how you would know one was pressed nearby."*

💡 **Tip:** some newer cars use 315 MHz or 868 MHz. If nothing appears, try the other key, then
move on. Never say why a particular key did not show.

---

## Demo 4 — Record now, analyse later

**Why you care:** *"A signal you missed is gone forever — unless you recorded it. This is how you
keep evidence, and how you train people on real signals without going back to the field."*

| | |
|---|---|
| **Time** | 5 minutes |
| **Command** | `./d4_replay.sh` |
| **Needs** | the recording made last night with `./d4_record.sh` |
| **Setting to type** | Offset from centre `200e3` |

**Do first, in front of them:** **unscrew the antenna** from the radio and put it on the table.

**What the room sees:** the same FM band as Demo 1, and BFM playing from the speakers — with no
antenna attached.

**Say it like this:**

1. *"No antenna. The radio is not even being used."*
2. *"Last night I recorded 20 seconds of this band. Not the sound — the whole raw signal."*
3. Move the offset slider. A different station plays. *"I only recorded once, but I can go back
   and listen to any station that was in the air at that moment."*
4. *"Record a whole band today, and decide next week what you are looking for."*

**If it fails**

| What you see | Do this |
|---|---|
| `recording ... missing` | The recording was not made. Open `fallbacks/d4_replay.*` |
| Picture but no sound | Sound has moved to HDMI. Settings → Sound → Output. Or say *"no sound in this room"* — the picture makes the point |

**Reset:** close the window. **Screw the antenna back on `TX/RX`.**

---

## Demo 5 — Noise against a clean signal

**Why you care:** *"Every digital link fails the same way: when noise gets too close to the
signal. This is what jamming does, and what a long range does. Here you can watch it happen."*

| | |
|---|---|
| **Time** | 4 minutes |
| **Command** | `./d5_bpsk.sh` |
| **Needs** | nothing. It is a simulation. Say so |

**What the room sees:**

- A **dot diagram** (a *constellation*) with two tight dots. Each dot is one of the two symbols
  the link sends: a 0 or a 1.
- In the terminal, `[BER Monitor] ... errors=0` counting up bits with no errors.

**Do:** drag the **Eb/N0 (dB)** slider slowly from 8 down to 0. *Eb/N0* is how strong the signal
is compared with the noise.

- The dots swell into clouds.
- The clouds touch.
- The error count in the terminal starts to climb.

**Say it like this:** *"Nothing about the signal changed. Only the noise. When the two clouds
touch, the receiver starts guessing wrong. That point is the edge of your range — or the moment
a jammer wins."*

Drag it back to 8. The dots snap back. *"Remove the noise, and the link recovers at once."*

**Reset:** close the window.

---

## Demo 6 — Television from this box to your TV

**Why you care:** *"So far the box has only listened. It can also transmit. The same box that
surveys a band can put a signal into it: for communications, for testing, or for training."*

🚨 **Danger / legal:** this demo transmits on UHF channel 21 (474 MHz). TV channels are licensed
to MYTV. Use the **lowest power that works**, keep the range to a few metres, and **never leave it
running unattended**. Say this out loud before you start — see *Say it like this*, step 1.

| | |
|---|---|
| **Time** | 18 minutes (about 5 of them are the TV box scanning) |
| **Command** | `./d6_tv.sh` |
| **Frequency** | UHF channel 21 = **474 MHz**, DVB-T2 |
| **Starts at** | zero power. You raise it |
| **Target level** | the lowest **TX RF gain** at which the TV box finds the channel |

### Set up before the session

- TV box connected to the TV (or the projector) by HDMI, and switched on.
- If you bought a cable: `TX/RX` → attenuators (30 + 30 dB) → adapter → TV box aerial socket.
- If not: the TV box's small aerial a few centimetres from the radio's `TX/RX` antenna.
- Find out last night whether the TV box can scan **one channel manually**. If it can, have its
  manual-scan menu open at channel 21 / 474 MHz before you start.

### Steps

1. Run `./d6_tv.sh`. It starts the video playout first, then opens the transmitter window by
   itself. The window title says *"Faraday cage or dummy load ONLY"*. That is on purpose.
2. In the window, set **TX digital amplitude** to `0.25`.
3. Raise **TX RF gain (dB)** slowly from 0, about 10 at a time.
4. On the TV box, run the channel scan (manual on 474 MHz if it can, otherwise automatic).
5. When it finds the channel, the video plays on the TV.
6. Lower **TX RF gain** again until the picture starts to break up, then raise it by 5. That is the
   minimum. Say so.

**What the room sees:** first a scan bar on the TV. Then **the TV finds a channel** and plays the
video — sent from the small box on the table.

**Say it like this:**

1. Before you start: *"This is a licensed TV channel, so we transmit at the lowest power that
   works, over a few metres, in a controlled room. Receiving is free. Transmitting needs a
   licence. We take that seriously, and so should any unit using this box."*
2. While the TV scans: *"This is a real digital TV signal, the same standard MYTV uses — made
   entirely in software on this laptop. The box has no TV chip inside."*
3. When the picture appears: *"Your TV cannot tell the difference between this and a real
   broadcaster. That is the point: this box can make any signal in its range — a TV channel, a
   test signal, a training target."*

### If it fails

| What you see | Do this |
|---|---|
| The window never appears | Playout did not start. Close the terminal, run `./stop_all.sh`, then `./d6_tv.sh` again |
| TV box finds nothing | In order: **TX digital amplitude** is still 0 · raise **TX RF gain** 10 more · TV set to channel 21 / 474 MHz · TV box set to DVB-T2 (not DVB-T only) |
| TV finds it but the picture breaks up | Too **strong** (common on a cable): lower **TX RF gain** by 10. Or too weak: raise it by 5 |
| The picture is smooth but sound drifts out of sync | Ignore it for the demo |
| Still nothing after 3 minutes | Close the window. Run the fallback below |

### The fallback — the box sends TV to itself

`./d6_fallback_loop.sh` 🚨 — no TV box needed. The radio transmits and receives at the same time,
on channel 31 (554 MHz).

1. Raise **TX gain (dB)** to 80–89, then **TX amplitude** to about 0.25. Keep **RX gain (dB)** at 20.
2. **The room sees:** a cloud of dots settle into **16 tight dots**, a signal-quality reading
   above 15 dB, `[TV] LOCKED` in the terminal, and then a video window opening by itself.
3. **Say:** *"The TV box would not play today, so the radio is being both the transmitter and the
   TV. Every dot you see was sent and received by this one box, at the same time."*

Measured at the lab, antennas a few centimetres apart (26 September 2026): RX gain 20, TX gain 89
gave a level of −12.4 dBFS, signal quality 19.7 dB, and zero errors.

### Reset — do not skip

1. Close the transmitter window.
2. Run `./stop_all.sh`. It must say **"All stopped. The radio is free."**
3. Say out loud: *"The transmitter is off."*

---

## If the radio behaves strangely

| Symptom | What it means | Do this |
|---|---|---|
| `No UHD Devices Found` | The radio is not answering | Unplug **both** cables. Power first, wait 30 s, then data. Takes a minute — do Demo 5 meanwhile |
| Stations are weak, and gain changes nothing | Very little signal reaches the radio | Check the antenna is on `TX/RX`. Move nearer a window |
| The radio says `LO: unlocked` | On this board that reading is **not reliable** | Ignore it. Judge by whether stations appear in the right place |
| `O` letters stream in the terminal | The laptop cannot keep up | Close other programs. Plug the laptop into power |
| A demo says the radio is busy | A window from an earlier demo is still open | `./stop_all.sh` |

---

## ✅ Summary

- Six demos: **see**, **decode**, **survey**, **record**, **noise**, **transmit**. Each card
  starts with why a soldier should care.
- **Close each window** before the next demo. `./stop_all.sh` frees the radio.
- **30 seconds** without recovery means: open the fallback, say so, move on.
- Demos 4 and 5 need no radio. They are your breathing space.
- Demo 6 transmits. Say the legal line out loud, use the lowest power that works, and
  **always finish with `./stop_all.sh`.**

**Next:** [The session plan →](./SESSION_PLAN.md)
