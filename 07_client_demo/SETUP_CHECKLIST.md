# ✅ Setup Checklist — Client Briefing

> **What this page is:** everything to buy, test and check before the briefing.
> **Read it in order.** Section 1 is today. Section 5 is the last ten minutes before they walk in.
> **Time:** about 3 hours tonight, 1 hour on the morning.

---

## Contents

1. [Buy or borrow today](#1-buy-or-borrow-today)
2. [Tonight — the rehearsal](#2-tonight--the-rehearsal)
3. [Tomorrow morning — the room](#3-tomorrow-morning--the-room)
4. [One hour before](#4-one-hour-before)
5. [The ten-minute smoke test](#5-the-ten-minute-smoke-test)

---

## 1. Buy or borrow today

These are in order of how much they matter.

| # | Item | Why you need it | If you cannot get it |
|---|---|---|---|
| 1 | **SMA male-to-male coax cable**, 50 Ω, any length | Sends the TV signal down a wire instead of through the air. This is the legal way to do the transmit demo | The demo runs antenna-to-antenna at a few centimetres. It works, but you are radiating. See the [legal note](#the-legal-problem-in-one-paragraph) |
| 2 | **Attenuators, 30 dB + 30 dB, SMA** | A cable carries far more signal than air does. Without attenuators the TV box and the radio's own receiver both overload | Start at the lowest gain and raise it slowly. You have less margin for error |
| 3 | **SMA-to-F adapter** (check your TV box's socket first — it may be F-type or IEC) | Connects the cable to the TV box | The TV box demo can only be done through the air |
| 4 | **Any Bluetooth or USB speaker** | There is no sound system in the room. Laptop speakers are too quiet for a meeting room | The listening part of Demo 2 will be weak. The demo still works, because the payoff is text on the screen |
| 5 | **A second HDMI cable** | So the TV box and the projector can both be connected | You will unplug and replug during Demo 6, which looks untidy |

> 💡 **Tip:** item 6 is free. A car key is a radio transmitter. Anyone who drove to the meeting
> has one in their pocket. See [Demo 3's bonus](./DEMO_RUNSHEET.md#bonus--the-car-key).

### ⚠️ Check the TV box socket before you buy

Look at the back of your DVB-T2 box. The aerial socket is one of these:

- **F-type** — a screw thread with a bare wire in the middle. Needs an **SMA-to-F** adapter.
- **IEC** — a smooth push-fit socket, common on European and Asian sets. Needs an **SMA-to-IEC**
  adapter.

Buy the one that matches. Take a photo of the socket to the shop.

### The legal problem, in one paragraph

Your radio can transmit from 70 MHz to 6 GHz. TV channels — 470 to 694 MHz — belong to MYTV.
Transmitting there without an assignment from MCMC is an offence under the Communications and
Multimedia Act 1998. See [the Malaysia reference](../05_reference/04_malaysia.md#8-the-short-legal-summary).

This matters more than usual on Thursday. You will stand in front of military officers, tell them
that transmitting without permission is an offence, and then transmit. If the signal goes down a
cable, that sentence is consistent. If it goes through the air, an officer in the room may notice.

A cable is also technically better. It gives a stronger, cleaner signal than two small antennas
across a desk, so the picture locks faster and looks better.

🚨 **Danger / legal:** if you have no cable, keep the antennas a few centimetres apart, keep the
transmit gain at the lowest setting that works, and say out loud what you are doing and why. Never
fit a full-size antenna to the transmit port.

---

## 2. Tonight — the rehearsal

**You must have the radio plugged in for this.** Nothing in this section works without it.

### 2.1 First, clear the decks (10 minutes)

| ✔ | Step | Command | What you should see |
|---|---|---|---|
| ☐ | Close the old GNU Radio window that has been open since yesterday | — | It holds nothing, but it confuses you later |
| ☐ | Check nothing else is holding the radio | `ps -eo pid,args \| grep -E "[l]ab1[012]\|[u]hd_fft"` | No output |
| ☐ | Plug in: **USB-C power first**, wait 30 seconds, **then USB 3.0 data** | — | — |
| ☐ | Find the radio | `uhd_find_devices` | One device, `type: b200` |
| ☐ | Check the USB speed | `uhd_usrp_probe 2>&1 \| grep -i "USB 3"` | A line saying USB 3 |

### 2.2 Run the preflight script (2 minutes)

```bash
cd 07_client_demo/demo
./preflight.sh
```

It checks the radio, the video files, the disk, and every program the demos need.
**Everything must say OK before you go further.**

### 2.3 Run all six demos, in order, on the clock (90 minutes)

Use [the run sheet](./DEMO_RUNSHEET.md). For each demo, write down in the run sheet:

- The **exact numbers that worked** — frequency, gain, offset, level.
- **How long it took**, from typing the command to the room seeing the result.
- Anything that went wrong.

> ⚠️ **Warning:** signal strength at this location changed by about 30 dB between morning and
> evening on 26 September 2026. Do not assume tonight's gain setting will work on Thursday
> afternoon. Write down a range, not one number.

### 2.4 Record a fallback for every demo (35 minutes)

This is the step people skip, and it is the one that saves the session.

For each demo, once it is working, record 30 to 60 seconds of the screen:

```bash
# Install once
sudo apt install -y gnome-screenshot

# Record the screen (Ubuntu built-in): Ctrl + Alt + Shift + R starts and stops
# Or take a still:
gnome-screenshot -w -f 07_client_demo/fallbacks/d1_spectrum.png
```

Save them into [`fallbacks/`](./fallbacks/) with these names:

```
d1_spectrum.png / .webm
d2_rds.png / .webm
d3_bands.png / .webm
d4_replay.png / .webm
d5_bpsk.png / .webm
d6_television.png / .webm
```

**The rule on Thursday:** if a demo has not recovered in **30 seconds**, open the recording
instead. Say "the radio is not cooperating in this building — here is the same thing working an
hour ago". Then move on. Never debug in front of the room.

### 2.5 Optional, only if time remains (20 minutes)

```bash
cd 07_client_demo
./install_demo_tools.sh
```

This installs **gqrx** (a point-and-click radio, nicer to look at than `uhd_fft`) and
**inspectrum** (a tool for looking inside a recording).

> ⚠️ **Warning:** gqrx is a bonus, not a requirement. If it does not see the radio within about
> 20 minutes of trying, stop and use `uhd_fft` instead. `uhd_fft` is already proven on this
> machine and shows the same picture. Do not spend Thursday morning fixing gqrx.

---

## 3. Tomorrow morning — the room

| ✔ | Check | Why |
|---|---|---|
| ☐ | How many screens are there? | If the TV box and the projector share one screen, Demo 6 takes your slides away. Find out before, not during |
| ☐ | Does the projector do 1920×1080? | The deck is built for 16:9 |
| ☐ | Is there a power socket near the table? | The radio needs two USB cables and the laptop needs power |
| ☐ | Can you sit near a **window**? | Signal indoors is much weaker. A window seat can be worth 20 dB |
| ☐ | Does the TV box do a **manual** channel scan, or only a full auto-scan? | A full auto-scan of 470–694 MHz takes 1 to 3 minutes. If it is auto-only, plan to talk over it |
| ☐ | Print the [run sheet](./DEMO_RUNSHEET.md) and the [handout](./client_handout.html) | Do not read a run sheet off the screen you are presenting from |

---

## 4. One hour before

| ✔ | Step | Command |
|---|---|---|
| ☐ | Plug the radio in, power first, then data | — |
| ☐ | Run the preflight | `cd 07_client_demo/demo && ./preflight.sh` |
| ☐ | **Fix the sound.** Plugging in a TV or projector moves the sound to HDMI | Settings → Sound → Output → the laptop speakers (or your Bluetooth speaker) |
| ☐ | Play any audio to confirm the room can hear it | `speaker-test -c2 -l1` |
| ☐ | Open the deck and press **F** for fullscreen | `xdg-open 07_client_demo/client_brief.html` |
| ☐ | Open a second window with the speaker view — press **S** | — |
| ☐ | Open a terminal, make the font **big** (Ctrl + Shift + +, about 6 times) | — |
| ☐ | Start the TV playout so Demo 6 is ready to go | see [run sheet Demo 6](./DEMO_RUNSHEET.md#demo-6--television-from-this-box-to-your-tv) |
| ☐ | Open the `fallbacks/` folder in a file manager, ready | — |
| ☐ | Turn off notifications, email and chat | Nothing worse than a message popping up on a projector |
| ☐ | Put your phone on silent, and plug the laptop into power | — |

---

## 5. The ten-minute smoke test

Run this last, from cold, exactly as written. If all five pass you are ready.

```bash
cd "/home/ubuntu/GNU Radio/signalsdrpro_lab"

# 1. The radio answers                          (10 s)
uhd_find_devices

# 2. The spectrum appears and has signals in it  (60 s, close the window)
uhd_fft -f 98e6 -s 20e6 -g 50 -A TX/RX

# 3. The station name decodes                    (60 s)
cd 02_flowgraphs/lab08_rds_decoder && gnuradio-companion lab08_rds_decoder.grc

# 4. The safe demos work with no radio at all    (90 s)
cd ../../03_scripts && python3 test_labs_offline.py

# 5. The TV chain is ready                       (30 s)
ls -lh ~/sdr_demo/bintang.ts ~/sdr_demo/bintang_dvbt2.ts
```

**What you should see**

| # | Pass looks like |
|---|---|
| 1 | One device found, `type: b200` |
| 2 | Humps across the FM band, not a flat line |
| 3 | `[RDS] ... PS=` with a name in it, inside 30 seconds |
| 4 | `9 passed, 0 failed` |
| 5 | Both files listed, 576M and 997M |

If number 2 shows a flat line, the antenna is on the wrong port or the gain is too low. Raise the
gain to 60 and check the antenna is on **TX2A**
([which connector is which](../00_setup/02_flash_b210_firmware.md#which-connector-is-txrx)).

---

## ✅ Summary

- Buy a **cable, attenuators and an adapter** today. They turn the transmit demo from awkward into
  clean.
- Rehearse **all six demos tonight**, with the radio, and write down the numbers that worked.
- **Record every demo** while it works. A recording turns a failure into a 30-second detour.
- Check the **room, the screens and the sound** in the morning. Sound moves to HDMI on its own.
- Run the **ten-minute smoke test** from cold before they walk in.

**Next:** [The run sheet →](./DEMO_RUNSHEET.md)
