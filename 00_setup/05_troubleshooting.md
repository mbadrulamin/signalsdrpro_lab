# 🩹 Setup 05 — Troubleshooting

> **What this page is:** a list of problems and fixes, grouped by **where** the problem is.
> Find your symptom, try the fixes in order.
> **Tip:** run the four checks in [Setup 04](./04_verify_setup.md) first. The first check that
> fails tells you which section below to read.

---

## Contents

1. [The radio does not appear at all](#1-the-radio-does-not-appear-at-all)
2. [`Could not find path for image`](#2-could-not-find-path-for-image)
3. [No signal, or bad sound](#3-no-signal-or-bad-sound)
4. [`O` or `U` in the terminal (overflow / underflow)](#4-o-or-u-in-the-terminal-overflow--underflow)
5. [GNU Radio problems](#5-gnu-radio-problems)
6. [Sound card problems](#6-sound-card-problems)
7. [The GPS clock (GPSDO)](#7-the-gps-clock-gpsdo)
8. [Still stuck?](#8-still-stuck)

---

## 1. The radio does not appear at all

**Symptom:** `uhd_find_devices` says `No UHD Devices Found`, with the radio plugged in.

First, find out **how far** the radio got. Watch the system messages while you plug in the data
cable:

```bash
sudo dmesg -w
```

Then find your case below.

### Case A — Nothing appears in `dmesg` at all

The computer does not see the radio's USB connection.

1. Is the **power** (USB Type-C) connected? Signalens says to use a **USB-A to USB-C** cable.
2. Is the **microSD card** inserted, with `BOOT.BIN` on it, and the jumper set to SD boot?
   ([Setup 02](./02_flash_b210_firmware.md))
3. Did you wait **30 seconds** after power before plugging in the data cable?
4. Try another USB 3.0 **cable** for the data.

### Case B — `device not accepting address` or `unable to enumerate USB device`

```
usb 1-8.2.3: device descriptor read/64, error -110
usb 1-8.2.3: device not accepting address 12, error -62
usb 1-8.2-port3: unable to enumerate USB device
```

The computer noticed *something* was plugged in, but could not talk to it. The problem is
**electrical** — power, cable or port — not software.

1. **Power-cycle both cables:** unplug Type-C **and** Type-B, wait 2 s, plug in power, wait 30 s,
   then plug in data.
2. **Try a USB 3.0 port on the computer itself**, not a hub, dock or adapter. (In the example
   above, `1-8.2.3` means port 3 of a hub, which is plugged into port 8 of the computer.)
3. Try another data cable.
4. Power the board from a separate 5 V phone charger (with an A-to-C cable) instead of from the
   computer.

### Case C — `dmesg` shows `Product: WestBridge`, but UHD finds nothing

```
usb 1-8.2.3: New USB device found, idVendor=2500, idProduct=0020
usb 1-8.2.3: Product: WestBridge
usb 1-8.2.3: Manufacturer: Cypress
```

"WestBridge" is **normal**. It means the board started correctly from the SD card and the USB
chip is waiting for UHD to send its firmware. If UHD still finds nothing:

1. **Permissions.** Try `sudo uhd_find_devices`. If that works, your user is not allowed to use
   the radio. Fix it:

   ```bash
   sudo usermod -aG usrp,plugdev $USER
   ```

   then **log out and back in**. (The `uhd-host` package installs the rule that grants access:
   `/lib/udev/rules.d/60-uhd-host.rules`.)
2. **Missing images.** If `uhd_find_devices` prints `Could not find path for image`, see
   [Section 2](#2-could-not-find-path-for-image).

### Case D — `dmesg` shows `Product: USRP B200` before you ran any UHD program

The board kept old firmware from last time, because it was **not fully power-cycled**. UHD may
then fail in strange ways. Unplug **both** cables, wait 2 seconds, and reconnect.

### Case E — It works, but `uhd_usrp_probe` says `Operating over USB 2`

Only low sample rates will work. Use a USB 3.0 port (blue, or marked `SS`) and a USB 3.0 cable.
`lsusb -t` shows the speed: `5000M` is USB 3.0, `480M` is USB 2.0.

---

## 2. `Could not find path for image`

```
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
Using images directory: <no images directory located>
```

UHD must send two **image** files to the radio each time it starts
([Setup 01 §6](./01_install_uhd.md#6-why-does-the-radio-need-images-every-time)). It cannot
find them. There are two causes. Look at the **first line** UHD prints, which shows its version:

```
[INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
```

### Cause 1 — the images were never downloaded

```bash
sudo uhd_images_downloader -t b2xx
```

Then try again.

### Cause 2 — two UHD versions (the most common case)

**Clue:** `uhd_find_devices` works (and prints a newer version, like `UHD_4.10.0` or
`UHD_4.11.0`), but GNU Radio fails (and prints `UHD_4.6.0`).

Your computer has UHD from Ubuntu (4.6.0, used by GNU Radio) **and** a newer UHD from the Ettus
PPA (used by the command-line tools). They look for images in different folders.

**The fix:** [Setup 06 — Fix the two-UHD-versions problem](./06_fix_uhd_version_conflict.md).
There is a script that does it for you:

```bash
cd 00_setup
./fix_uhd_version_conflict.sh
```

---

## 3. No signal, or bad sound

**First, look before you listen.** Add a **QT GUI Frequency Sink** after the USRP Source (or
run `uhd_fft`, see [Setup 04 Check 3](./04_verify_setup.md#check-3--can-you-see-real-signals)).
You should see humps where stations are.

| Symptom | Try this |
|---|---|
| No humps at all, only a flat line | Antenna not connected, or on the wrong connector (use `TX/RX`). Try near a window. Raise gain to 50–60 |
| Humps, but only hiss | You are between stations. Tune so a hump is in the centre (or at your chosen offset) |
| Loud, harsh, distorted sound on strong stations | Too much gain, or too much volume. Lower the **volume** first (Lab 03), then the gain |
| False "stations" appear when you raise the gain | The radio is overloaded (intermodulation). Lower the gain |
| Sound plays at the wrong speed or pitch | A sample rate mismatch. The audio rate must equal the rate going into the Audio Sink (Lab 01, question 2) |
| A thin spike exactly in the centre | Normal: the radio's own leak (DC offset). Tune a little beside the signal (Lab 06) |

---

## 4. `O` or `U` in the terminal (overflow / underflow)

UHD prints single letters when samples are lost:

| Letter | Name | Meaning |
|---|---|---|
| `O` | Overflow | **Receiving:** the computer did not take the samples fast enough, and some were dropped |
| `U` | Underflow | **Transmitting:** the computer did not supply samples fast enough |
| `aU` / `aO` | Audio underrun / overrun | The **sound card** ran out of, or had too many, samples |

A few, now and then, are harmless. A constant stream means the computer cannot keep up:

1. **Lower the sample rate** (for example 1 MSPS instead of 2).
2. **Close the heavy displays.** The waterfall uses the most CPU (right-click → Disable).
3. Use a **USB 3.0** port on the computer itself.
4. Close other programs (web browsers can use a lot of CPU).
5. When recording, give the driver more buffer: in the USRP Source, set **Device Arguments** to
   `"num_recv_frames=512"` (Lab 05 does this).

---

## 5. GNU Radio problems

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'gnuradio'` | You are inside a Python virtual environment. Run `deactivate`, then try `python3 -c "import gnuradio"` |
| Qt display blocks fail, or are missing | `sudo apt install python3-pyqt5` |
| A connection arrow is **red** | The two ports have different data types. Colours must match: blue = complex, orange = float |
| `IndexError: input_index must be < ninputs` (Lab 06) | You set the Selector's input before the flowgraph started. Start it first |
| A flowgraph with no radio uses 100 % CPU | It needs a **Throttle** block (Lab 05) |

---

## 6. Sound card problems

| Symptom | Fix |
|---|---|
| `audio_alsa_sink ... failed to open` or similar | Install the sound tools: `sudo apt install pulseaudio-utils alsa-utils`. Then set the Audio Sink's **Device Name** to `pulse` or `default` |
| No sound, no errors | Check the volume and output device in Ubuntu's Settings → Sound |
| `aU` now and then | Harmless. If constant, see [Section 4](#4-o-or-u-in-the-terminal-overflow--underflow) |

---

## 7. The GPS clock (GPSDO)

The SignalSDR Pro has a built-in **GPSDO**: a clock corrected by GPS satellites. You do not
need it for the labs, but it makes the frequency more accurate.

To use it, in the USRP Source block set:

- **Clock Source:** `gpsdo`
- **Time Source:** `gpsdo`

It needs a GPS antenna with a view of the sky. If it does not lock:

- Move the GPS antenna near a window, or outside.
- Wait **5–10 minutes** the first time.
- `uhd_usrp_probe` should show `Found an internal GPSDO: GPSTCXO v3.2 for SDRPro`. Its sensor
  `gps_locked` tells you whether it has locked.

---

## 8. Still stuck?

1. Run the four checks in [Setup 04](./04_verify_setup.md) and note the **first** one that
   fails. That tells you where the problem is.
2. Run the very first radio in [QUICKSTART](../QUICKSTART.md) — it is known to work.
3. Signalens' own setup guide:
   [Transforming into compatible mode](https://github.com/signalens/signalsdrpro_docs/blob/main/transform.md).
4. Ask Signalens: [GitHub issues](https://github.com/signalens/signalsdrpro/issues).
5. Ask the GNU Radio community: [chat.gnuradio.org](https://chat.gnuradio.org/) or the
   [mailing list](https://lists.gnu.org/mailman/listinfo/discuss-gnuradio).

When you ask for help, include: your Ubuntu version, the **first line** UHD prints (with its
version), the full error message, and what `sudo dmesg | tail -20` shows after plugging in.

**Next:** [Setup 06 — Fix the two-UHD-versions problem](./06_fix_uhd_version_conflict.md)
(only if you need it), or [Fundamentals 01 →](../01_fundamentals/01_signals_basics.md)
