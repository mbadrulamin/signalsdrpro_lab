# 💾 Setup 02 — Prepare the SignalSDR Pro (B210 Mode)

> **What you will do:** put the **USRP B210** start-up file on a microSD card, set the board to
> start from it, connect the cables, and check that your computer sees the radio.
> **Before this:** [Setup 01 — Install UHD](./01_install_uhd.md). You need the SignalSDR Pro,
> a microSD card, a card reader, a **USB-A to USB-C** cable (power) and a **USB 3.0 Type-B**
> cable (data).
> **Time:** about 10–15 minutes. **Difficulty:** easy.

This page follows Signalens' own guide:
[Transforming into compatible mode](https://github.com/signalens/signalsdrpro_docs/blob/main/transform.md).

---

## 1. How the SignalSDR Pro starts up

The SignalSDR Pro starts from its **microSD card**. The card holds one file, `BOOT.BIN`, that
contains everything the board needs: a small start-up program, the FPGA design, and the
software for its ARM processor.

**Which file you put on the card decides what the board pretends to be:**

| Mode | Looks like | Used with |
|---|---|---|
| **USRP B210** | an Ettus USRP B210 | **UHD and GNU Radio — this course** |
| ADALM-Pluto | an Analog Devices Pluto | IIO tools, some apps like GQRX |

In B210 mode, your computer sees a USRP B210. All B210 software works unchanged.

---

## 2. Prepare the microSD card

### Step 1 — Format the card as FAT32

You need a microSD card of **8 GB or more** (Class 10 is best).

> 🚨 **Be very careful here.** Formatting the wrong disk erases it. Check the size shown by
> `lsblk` matches your card before you continue.

```bash
lsblk
```

Find your card by its size — for example `sdb` with 7.4G or 14.8G. Its partition is usually
`sdb1`. In the commands below, **replace `sdX1` with your card's partition**:

```bash
sudo umount /dev/sdX1                          # un-mount it if Ubuntu opened it
sudo mkfs.vfat -F 32 -n SIGNALSDR /dev/sdX1    # format as FAT32, name it SIGNALSDR
```

> 💡 Prefer a graphical tool? Ubuntu's **Disks** app can format a card as FAT (FAT32) too.

### Step 2 — Download the B210 file

```bash
mkdir -p ~/signalsdr_fw && cd ~/signalsdr_fw
wget -O BOOT.BIN https://github.com/signalens/signalsdrpro/raw/main/bin/b210/v3/BOOT.bin
ls -l BOOT.BIN
```

✅ The file should be **3,073,968 bytes** (about 3 MB).

> ⚠️ On GitHub the file is called `BOOT.bin`. The `-O BOOT.BIN` part saves it with the name
> the board expects, **`BOOT.BIN`**, as Signalens' guide says.

### Step 3 — Copy it to the card

```bash
sudo mount /dev/sdX1 /mnt
sudo cp ~/signalsdr_fw/BOOT.BIN /mnt/BOOT.BIN
sync                    # make sure it is really written
sudo umount /mnt
```

The file must be in the **top folder** of the card (not inside another folder).

---

## 3. Set the jumper

The board has a **jumper** — a tiny plastic cap on two pins — that chooses where it starts from:
its internal memory, or the microSD card.

👉 **Set it to boot from the SD card.** The exact position is shown in Signalens' pictures:

- [How to set the jumpers](https://github.com/signalens/signalsdrpro/blob/main/img/transform/boot_ins.png)
- [Where the connectors are](https://github.com/signalens/signalsdrpro/blob/main/img/transform/layout.png)

---

## 4. Connect the cables — in this order

1. **Insert the microSD card.**
2. **Screw the antenna** onto the `TX/RX` connector. Finger-tight only.
3. **Power:** connect the **USB Type-C** port to your computer or a 5 V charger, using a
   **USB-A to USB-C** cable. Signalens says it *must* be A-to-C. A C-to-C cable may not work.
   Charge-only cables are fine for power.
4. **Wait about 30 seconds** while the board starts.
5. **Data:** connect the **USB Type-B** port to a **USB 3.0** port on your computer (usually
   blue, or marked `SS`), with a USB 3.0 cable.

> 💡 A USB 3.0 port **on the computer itself** is the most reliable. Some hubs, docks and
> adapters work (this course was tested through a Dell USB-C adapter), but if the radio does not
> appear, try a port on the computer first.

---

## 5. Check that the computer sees it

### Step 1 — Look at what Linux sees

Open a terminal and watch the system messages:

```bash
sudo dmesg -w
```

(Press `Ctrl+C` to stop watching.) When you plug in the data cable, you should see:

```
usb 1-8.2.3: New USB device found, idVendor=2500, idProduct=0020, bcdDevice= 1.00
usb 1-8.2.3: Product: WestBridge
usb 1-8.2.3: Manufacturer: Cypress
```

✅ **This is correct.** "WestBridge" means the radio's USB chip is waiting for UHD to send it
its firmware. (The numbers like `1-8.2.3` depend on your USB port.)

> ⚠️ If it says **`USRP B200`** straight away, before you have run any UHD program, the board
> was **not fully power-cycled** and still has old firmware from last time. Unplug **both**
> cables, wait 2 seconds, and plug them in again (power first).

### Step 2 — Let UHD find it

```bash
uhd_find_devices
```

UHD sends the firmware to the radio. The radio restarts its USB connection, now as a USB 3.0
device. `sudo dmesg` will show it come back with a new name:

```
usb 8-1.2.3: new SuperSpeed USB device number 6 using xhci_hcd
usb 8-1.2.3: Product: USRP B200
usb 8-1.2.3: Manufacturer: Ettus Research LLC
usb 8-1.2.3: SerialNumber: 194431
```

And `uhd_find_devices` reports:

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

Your serial number will be different.

### Step 3 — Get the full details

```bash
uhd_usrp_probe
```

This loads the FPGA image and prints everything about the radio. Near the top, look for:

```
[INFO] [B200] Loading firmware image: .../usrp_b200_fw.hex...
[INFO] [B200] Detected Device: B210
[INFO] [B200] Loading FPGA image: .../usrp_b210_fpga.bin...
[INFO] [B200] Operating over USB 3.
[INFO] [B200] Detecting internal GPSDO....
[INFO] [GPS] Found an internal GPSDO: GPSTCXO v3.2 for SDRPro
...
|   |       Mboard: B210
```

✅ **`Operating over USB 3.`** — good. If it says USB 2, move the data cable to a USB 3.0 port.
✅ **`Found an internal GPSDO`** — the SignalSDR Pro's built-in GPS clock.

In the long list you will also see:

| Line | Meaning |
|---|---|
| `Freq range: 50.000 to 6000.000 MHz` | What UHD allows. The SignalSDR Pro is **specified from 70 MHz**; below that, performance is not guaranteed |
| `Gain range PGA: 0.0 to 76.0` (RX) | Receive gain, in dB |
| `Gain range PGA: 0.0 to 89.8` (TX) | Transmit gain, in dB |
| `Bandwidth range: 200000.0 to 56000000.0` | The analog filter: 200 kHz to 56 MHz |
| `Antennas: TX/RX, RX2` | The two receive connectors |

---

## 6. Important habits

1. **Always power-cycle fully between sessions.** Unplug **both** the Type-C (power) and
   Type-B (data) cables, wait **2 seconds**, then plug in again: power first, then data.
   Signalens' guide says this is required.
2. **After power-up it should be "WestBridge".** It only becomes "USRP B200" after a UHD
   program runs. That is normal.
3. **The Type-C port is also a console.** With the power cable to your computer, you can watch
   the board start: `screen /dev/ttyUSB1 115200`. A good start ends with
   `SDRPRO B210 Hello World`. (The device may be `ttyUSB0` on your computer.)

---

## 🔧 Troubleshooting

| Problem | What to check |
|---|---|
| Nothing appears in `dmesg` at all | Is the power (Type-C) connected, with an **A-to-C** cable? Is the card in? Wait 30 s after power before connecting data |
| `dmesg` shows `device not accepting address` or `unable to enumerate USB device` | The USB connection failed before the radio could even say its name. Usually power or cable: power-cycle both cables; try a different USB 3.0 cable; try a port on the computer instead of a hub or dock |
| It says "USRP B200" before running UHD, and then UHD fails | Not fully power-cycled. Unplug both cables, wait 2 s, reconnect |
| `uhd_find_devices` finds nothing, but `dmesg` shows WestBridge | Permissions: try `sudo uhd_find_devices`. If that works, redo [Setup 01, Step 3](./01_install_uhd.md#step-3--allow-your-user-to-use-the-radio) and log out/in |
| `Could not find path for image: usrp_b200_fw.hex` | Images not downloaded, or two UHD versions: see [Setup 06](./06_fix_uhd_version_conflict.md) |
| `Operating over USB 2` | Use a USB 3.0 port and cable. On USB 2 only low sample rates work |
| The console shows the board stuck at `SIGNALSDR>` (U-Boot) | See "Reset SPI" in [Signalens' guide](https://github.com/signalens/signalsdrpro_docs/blob/main/transform.md) |

More: [Setup 05 — Troubleshooting](./05_troubleshooting.md).

---

## ✅ Summary

- Put `BOOT.BIN` (downloaded as `BOOT.bin`, saved as `BOOT.BIN`) in the top folder of a FAT32
  microSD card.
- Set the jumper to boot from the SD card.
- Power with a **USB-A to C** cable first, wait 30 s, then connect the **USB 3.0 Type-B** data
  cable.
- After power-up the radio shows as **WestBridge**. After UHD runs, it shows as **USRP B200**.
- `uhd_usrp_probe` should say **Operating over USB 3** and **Found an internal GPSDO**.
- Always unplug **both** cables between sessions.

## 🧠 Check yourself

1. You plug in the radio and `dmesg` says "WestBridge". Is something wrong?
   <details><summary>Answer</summary>No. That is the normal state before UHD sends the
   firmware.</details>
2. Before you run any UHD program, `dmesg` already says "USRP B200". What should you do?
   <details><summary>Answer</summary>Power-cycle fully: unplug both cables, wait 2 seconds,
   plug in again.</details>
3. `uhd_usrp_probe` prints `Operating over USB 2`. What does that mean for you?
   <details><summary>Answer</summary>You will only get low sample rates. Move to a USB 3.0
   port and cable.</details>

**Next:** [Setup 03 — Install GNU Radio →](./03_install_gnuradio.md)
