# 🧰 Setup 03 — Install GNU Radio

> **What you will do:** install **GNU Radio**, the software you build radios in, and check it
> works by playing a test tone.
> **Before this:** [Setup 01 — Install UHD](./01_install_uhd.md).
> **Time:** about 10–20 minutes. **Difficulty:** easy.

---

## 1. What is GNU Radio?

**GNU Radio** is free, open-source software for building radios. It gives you:

- hundreds of ready-made **blocks** — filters, decoders, displays, and more,
- **GNU Radio Companion (GRC)** — a drawing program where you connect blocks with arrows. When
  you press **Run**, it writes a Python program from your drawing and runs it,
- a Python and C++ interface, for when you want to write code yourself.

Most SDR tutorials, books and university courses use GNU Radio. This course uses
**version 3.10**.

---

## 2. Install it (Ubuntu's own packages — recommended)

```bash
sudo apt update
sudo apt install -y gnuradio gnuradio-dev
```

On Ubuntu 24.04 this installs GNU Radio **3.10.9**. It is built for the UHD 4.6.0 from Ubuntu,
so if you followed [Setup 01, Option A](./01_install_uhd.md#3-option-a--ubuntus-own-packages-recommended),
everything matches.

### What you get

| Program | What it is |
|---|---|
| `gnuradio-companion` | GRC, the graphical editor |
| `grcc` | Turns a `.grc` file into a `.py` file from the command line |
| `gnuradio-config-info` | Shows the version |
| `uhd_fft`, `uhd_rx_cfile` | Ready-made tools that use the radio (used in [Setup 04](./04_verify_setup.md)) |
| Python modules | `gnuradio`, `pmt`, and all the block libraries |

### Check the version

```bash
gnuradio-config-info --version
```

✅ You should see `3.10.9.2` (or another 3.10.x).

---

## 3. Useful extras

```bash
# Qt support for the graphical displays (usually installed already)
sudo apt install -y python3-pyqt5

# sound tools
sudo apt install -y pulseaudio-utils alsa-utils

# optional: support for other SDRs (RTL-SDR, HackRF, bladeRF...)
sudo apt install -y gr-osmosdr

# optional: a ready-made receiver app, and a tool for studying recordings
sudo apt install -y gqrx-sdr inspectrum
```

---

## 4. Test it: play a tone

This proves GNU Radio and your sound card work, before any radio is involved.

1. Start GRC:

   ```bash
   gnuradio-companion
   ```

   A window opens: the **block library** on the right, an empty **canvas** in the middle.
2. Double-click the **`samp_rate`** variable block (top left of the canvas). Set its value to
   `48000`. Every new flowgraph has this variable; many blocks use it by default.
3. Find blocks by pressing **Ctrl+F** and typing their name. Add these two to the canvas:
   - **Signal Source**
   - **Audio Sink**
4. Double-click **Signal Source** and set:
   - **Output Type:** Float (its port turns orange)
   - **Waveform:** Sine
   - **Frequency:** `1000`
   - **Amplitude:** `0.3`
   - leave **Sample Rate** as `samp_rate`
5. Double-click **Audio Sink** and set **Sample Rate** to `48KHz`.
6. Drag from Signal Source's output (its right side) to Audio Sink's input (its left side).
   An arrow appears.
7. Press **F5** (or click ▶). GRC asks you to save first — save it anywhere as `tone.grc`.

🎵 **You should hear a steady 1 kHz tone.** Close the window to stop it.

> 💡 If the arrow is **red**, the port types do not match: Signal Source must be set to
> **Float** (orange), because Audio Sink needs float.

---

## 5. Other ways to install (advanced)

| Method | When | How |
|---|---|---|
| GNU Radio PPA | Ubuntu 22.04, to get a newer 3.10.x | `sudo add-apt-repository ppa:gnuradio/gnuradio-releases`, then `sudo apt install gnuradio`. Check afterwards which UHD it uses ([Setup 06](./06_fix_uhd_version_conflict.md)) |
| Build from source | You need GNU Radio 3.11 / the newest code, or a non-Ubuntu Linux | Follow the official [installation guide](https://wiki.gnuradio.org/index.php/InstallingGR). Build UHD from source first, so both match |
| Conda / radioconda | Windows or macOS, or a self-contained setup | [radioconda](https://github.com/ryanvolz/radioconda) |

> ⚠️ **PyBOMBS**, mentioned in older tutorials, is no longer maintained. Don't use it.

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `gnuradio-companion: command not found` | The install failed. Run the `apt install` again and read the error |
| GRC opens but the displays fail with Qt errors | `sudo apt install python3-pyqt5` |
| No sound, no errors | Check your computer's volume and output device (Settings → Sound) |
| `aU` printed in the terminal | "Audio underrun": the sound card ran out of samples. Harmless if rare. Check both sample rates are 48000 |
| The connection arrow is red | The port types do not match (colours must match) |

More: [Setup 05 — Troubleshooting](./05_troubleshooting.md).

---

## ✅ Summary

- Install GNU Radio **from Ubuntu**, like UHD, so both match: `sudo apt install gnuradio`.
- GRC is the graphical editor. **F5** runs a flowgraph.
- Port colours show data types: **orange = float**, **blue = complex**. Arrows between
  different colours turn red.
- A 1 kHz tone through Audio Sink proves GNU Radio and sound work.

**Next:** [Setup 04 — Check that everything works →](./04_verify_setup.md)
