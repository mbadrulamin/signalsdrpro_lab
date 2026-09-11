# ⏱️ Your First 30 Minutes

> **Goal: hear a real radio station through your SignalSDR Pro, today.**
>
> No theory. No flowgraphs. Just plug it in and prove the whole chain works — because
> everything else in this repository is easier once you have heard *something*.
>
> **You need:** the SignalSDR Pro, its cables, an antenna, and a Linux PC.
> **You do not need:** any knowledge of radio. That comes later.

---

## Before the clock starts

Lay these out on the desk:

| Item | Notes |
|---|---|
| SignalSDR Pro | with its **microSD card inserted** |
| USB 3.0 cable (Type-B) | the chunky blue one — this carries data |
| USB-C cable | power |
| Antenna | anything with an SMA plug. Even a 1 m piece of wire works for FM |
| A Linux PC | Ubuntu 22.04 or 24.04. 8 GB RAM, a free USB 3.0 port |

> 💡 **No antenna at all?** For this first test, FM broadcast is so strong that a **30 cm
> piece of wire pushed into the SMA centre** will usually work indoors near a window. It is a
> terrible antenna. It will still hear something. That is the point of this exercise.

---

## Minutes 0–10: Install the software

Open a terminal (`Ctrl+Alt+T`) and paste these four lines. They will ask for your password.

```bash
sudo apt update
sudo apt install -y gnuradio gnuradio-dev uhd-host libuhd-dev python3-numpy
sudo uhd_images_downloader
sudo usermod -aG usrp,dialout,plugdev $USER
```

**Then log out and log back in.** (The last line adds you to the groups that are allowed to
talk to USB hardware; the change only takes effect on a new login.)

<details>
<summary><b>What did that just do?</b> (click to expand — not needed to continue)</summary>

- `gnuradio` — the signal-processing toolkit every lab in this repo uses
- `uhd-host` — the driver for USRP-family radios. Your SignalSDR Pro pretends to be a USRP B210
- `uhd_images_downloader` — fetches the FPGA firmware the driver loads into the radio at startup
- `usermod` — lets you use the radio without `sudo`

Full detail: [Setup 01](./00_setup/01_install_uhd.md) and [Setup 03](./00_setup/03_install_gnuradio.md).
</details>

---

## Minutes 10–15: Plug it in

**Order matters.**

1. **Power first** — USB-C cable from the SDR to a USB port or a 5 V charger.
2. **Wait about 30 seconds.** The board is booting Linux from the microSD card. Let it finish.
3. **Then data** — USB 3.0 Type-B cable from the SDR to a **blue** USB 3.0 port on your PC.
4. **Screw the antenna onto the `TX/RX` connector.** Finger-tight. Do not force it.

Now ask the driver whether it can see the radio:

```bash
uhd_find_devices
```

### ✅ Success looks like this

```
--------------------------------------------------
-- UHD Device 0
--------------------------------------------------
Device Address:
    serial: 194431
    name: MyB210
    product: B210
    type: b200
```

The serial number will be different. `product: B210` is the emulation doing its job.

### ❌ If it says "No UHD Devices Found"

Work down this list — it is almost always one of the first three:

| Check | Fix |
|---|---|
| Did you wait 30 s after powering on? | Unplug, replug, count to thirty, try again |
| Is the microSD card inserted? | It holds the firmware. Without it, nothing boots |
| Did you log out and back in? | The group membership does not apply until you do |
| Is it a **USB 3.0** port? | Blue connector, or marked `SS`. USB 2.0 may not enumerate |
| `lsusb \| grep -i ettus` shows nothing? | Power or cable problem, not software |

Still stuck: [Setup 05 — Troubleshooting](./00_setup/05_troubleshooting.md).

<details>
<summary><b>"Could not find path for image: usrp_b200_fw.hex"</b> — a very common one</summary>

Two versions of UHD are installed and they disagree about where the firmware lives. Run:

```bash
cd 00_setup && ./fix_uhd_version_conflict.sh
```

Explanation: [Setup 06](./00_setup/06_fix_uhd_version_conflict.md).
</details>

---

## Minutes 15–20: Look at the radio spectrum

Before listening, **look**. Paste this whole block into the terminal:

```bash
cat > /tmp/look.py <<'PY'
from gnuradio import gr, uhd, qtgui
from PyQt5 import Qt; import sys, sip
class T(gr.top_block, Qt.QWidget):
    def __init__(s):
        gr.top_block.__init__(s, "Spectrum"); Qt.QWidget.__init__(s)
        s.setWindowTitle("Your first look at the radio spectrum")
        s.setLayout(Qt.QVBoxLayout())
        u = uhd.usrp_source("", uhd.stream_args(cpu_format="fc32", channels=[0]))
        u.set_samp_rate(2e6)
        u.set_center_freq(uhd.tune_request(98e6), 0)   # middle of the FM band
        u.set_bandwidth(2e6, 0)                        # ALWAYS set this - see Fundamentals 06
        u.set_gain(40, 0); u.set_antenna("TX/RX", 0)
        f = qtgui.freq_sink_c(2048, 0, 98e6, 2e6, "Spectrum", 1)
        w = qtgui.waterfall_sink_c(2048, 0, 98e6, 2e6, "Waterfall", 1)
        f.set_y_axis(-130, 0)
        for g in (f, w): s.layout().addWidget(sip.wrapinstance(g.qwidget(), Qt.QWidget))
        s.connect(u, f); s.connect(u, w)
app = Qt.QApplication(sys.argv); t = T(); t.start(); t.show(); app.exec_()
PY
python3 /tmp/look.py
```

A window opens with two panels. **This is the radio spectrum around 98 MHz, live.**

```
   power
     │        ▂▄█▆▃         ▃▅█▇▄        ← each hump is one FM station,
     │   ▁▂▃▄███████▃▂▁▁▂▃▅███████▃▂▁      about 200 kHz wide
     │ ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁   ← the noise floor
     └──────────────────────────────────▶ frequency
       97 MHz          98 MHz        99 MHz
```

**Things to try right now** (this is the whole point of an SDR):

- Each **hump** is a radio station. Count them.
- The flat carpet underneath is the **noise floor** — the thermal noise of the universe plus
  your receiver's own noise.
- There is probably a **sharp spike dead centre**. That is *not* a station. It is your radio's
  own local oscillator leaking into its own input. You will learn to dodge it in
  [Lab 06](./02_flowgraphs/lab06_multimode_receiver/README.md).

Close the window when you are done (`Ctrl+C` in the terminal if it sticks).

> 😐 **Flat line, no humps?** Your antenna is not connected, or not connected properly. Check
> the SMA is screwed on. Try holding the antenna near a window.

---

## Minutes 20–30: Hear a station

Now the payoff. Run the very first lab:

```bash
cd 02_flowgraphs/lab01_simple_wbfm
python3 lab01_simple_wbfm.py
```

A window opens with two sliders.

1. Drag **FM Station (Hz)** to a frequency where you saw a hump. If you have no idea, try a
   round number near the middle of the band.
2. Adjust **RF Gain** — start around 40.
3. **Turn up your computer's volume.**

🎧 **You should hear music or speech.**

That is a radio you assembled from three software blocks, receiving a real broadcast.

### If you hear only hiss

| Symptom | Cause | Fix |
|---|---|---|
| Hiss everywhere | Between stations | Move the frequency slider |
| Hiss, and the spectrum was flat | Antenna | Check the SMA connection |
| Distorted, harsh audio | Gain too high, or a very strong station | Lower gain to ~25 |
| Very quiet | Gain too low | Raise gain to ~55 |
| No sound at all, no errors | PC audio | Check the volume and the output device |

---

## 🎉 What you just proved

In half an hour, without writing any code, you confirmed that **every link in the chain works**:

```
  antenna → SDR hardware → USB → driver → GNU Radio → your speakers
```

Everything from here is building more interesting things on top of a chain you now know is good.
When something stops working later, **come back and re-run these two steps** — if they still
work, the problem is in what you changed.

---

## Where to go next

You have two sensible routes. Both are correct; pick the one that suits you.

### 🐢 "I want to understand it"

The order this repository was designed for:

1. **[Introduction to SDR](./01_fundamentals/00_introduction_to_sdr.md)** — what you just did, and why it works
2. **[Fundamentals 01–04](./01_fundamentals/01_signals_basics.md)** — signals, IQ, RF, FM
3. **[Lab 01](./02_flowgraphs/lab01_simple_wbfm/README.md)** — the flowgraph you just ran, explained block by block
4. Then Labs 02, 03, 04… each adds one idea

### 🐇 "I want to see what it can do"

Skim, then come back for the theory when something confuses you:

1. **[Lab 02](./02_flowgraphs/lab02_enhanced_wbfm/README.md)** — add a waterfall and sliders
2. **[Lab 03](./02_flowgraphs/lab03_advanced_wbfm/README.md)** — a receiver that sounds good
3. **[Part 4 — Applications](./04_applications/README.md)** — 589 things you could point this at

### 📖 Two references to bookmark now

- **[Glossary](./05_reference/01_glossary.md)** — every acronym in this repo, in plain English.
  You will need this on page one of anything.
- **[Antennas](./05_reference/03_antennas.md)** — the single biggest improvement available to
  you, and it costs almost nothing.

### 🇲🇾 In Malaysia?

**[Malaysia reference](./05_reference/04_malaysia.md)** — what is on the air here, which bands
you may legally transmit in, how to get licensed, and the local clubs.

---

## The one rule

> **Receiving is passive and mostly unrestricted. Transmitting is neither.**
>
> Your SignalSDR Pro can transmit from 70 MHz to 6 GHz. Nine of the ten labs here are
> receive-only by design. Do not transmit until you have read
> [Law & Ethics](./04_applications/README.md#-law--ethics) and, in Malaysia,
> [the licensing section](./05_reference/04_malaysia.md#3-getting-licensed-to-transmit).

---

**Next:** [Introduction to SDR →](./01_fundamentals/00_introduction_to_sdr.md)
