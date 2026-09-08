# 🩹 05 — Troubleshooting

A collection of common problems and solutions when setting up the SignalSDR Pro + UHD + GNU Radio.

---

## ⚠️ Most Common Issue: Missing UHD Firmware Images

### Problem: `Could not find path for image: usrp_b200_fw.hex`

**Error message:**
```
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
Using images directory: <no images directory located>
Set the environment variable 'UHD_IMAGES_DIR' appropriately or follow the below instructions to download the images package.
Please run: "/lib/x86_64-linux-gnu/uhd/utils/uhd_images_downloader.py"
No UHD Devices Found
```

**Cause:** UHD needs firmware (`usrp_b200_fw.hex`) and FPGA bitstream (`usrp_b210_fpga.bin`) files to upload to the device. These are NOT included with the PPA installation of UHD 4.10.0+.

**Fix (3 commands):**
```bash
# 1. Download the B200/B210 firmware images
sudo uhd_images_downloader -t b2xx

# 2. Verify the images were downloaded
ls /usr/share/uhd/4.10.0/images/ | grep b2
# Should show: usrp_b200_fw.hex and usrp_b210_fpga.bin

# 3. Test again
uhd_find_devices
```

**Why this happens:** The SignalSDR Pro (like a real USRP B210) is a "blank slate" when powered on. UHD must upload the USB firmware and FPGA bitstream every time the device powers on. This allows the same hardware to be reconfigured for different purposes.

**Detailed guide:** [QUICK_FIX_UHD_IMAGES.md](../QUICK_FIX_UHD_IMAGES.md)

---

## ⚠️ Second Most Common Issue: UHD Version Conflict

### Problem: `uhd_find_devices` works but GNU Radio fails with missing images

**Symptoms:**
- `uhd_find_devices` shows UHD 4.10.0.0 and works fine
- GNU Radio flowgraphs fail with: `Could not find path for image: usrp_b200_fw.hex`
- GNU Radio logs show UHD 4.6.0.0

**Error message:**
```
[INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
[WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
Using images directory: <no images directory located>
```

**Cause:** You have TWO UHD versions installed:
- UHD 4.10.0 from the PPA (used by command-line tools)
- UHD 4.6.0 from Ubuntu repos (used by GNU Radio, which was compiled against it)

**Quick Fix (1 command):**
```bash
export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images
gnuradio-companion
```

**⚠️ IMPORTANT:** This only works if you launch `gnuradio-companion` from the **SAME terminal** where you ran the export. If you close the terminal or open GRC from the desktop shortcut, it won't work!

**⭐ BEST FIX - Bulletproof System-Wide Solution (3 commands):**
```bash
# 1. Create system-wide environment variable (requires sudo password)
echo 'export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images' | sudo tee /etc/profile.d/uhd_images.sh

# 2. Make it executable
sudo chmod +x /etc/profile.d/uhd_images.sh

# 3. Load it NOW (or just reboot)
source /etc/profile.d/uhd_images.sh
```

**Why this is better:** The `/etc/profile.d/` method creates a system-wide variable that works in ALL terminals AND desktop launchers. It survives reboots automatically.

**Automated Bulletproof Fix:**
```bash
chmod +x bulletproof_fix.sh
./bulletproof_fix.sh
```

**Why this happens:** GNU Radio 3.10.9 from Ubuntu's repos was compiled against UHD 4.6.0. When you later installed UHD 4.10.0 from the PPA, command-line tools started using the newer version, but GNU Radio still uses the old UHD 4.6.0 libraries.

**Detailed guide:** [07_bulletproof_uhd_fix.md](07_bulletproof_uhd_fix.md)

---

## 🔌 USB Issues

### Problem: `uhd_find_devices` returns nothing

**Diagnose:**
```bash
lsusb | grep -iE "cypress|2500"
dmesg | tail -30
```

**Solutions:**
1. Try a different USB 3.0 port (must be blue).
2. Try a different USB-B cable (preferably short and shielded).
3. Run `sudo uhd_find_devices` — may be a permission issue.
4. Check udev rules:
   ```bash
   sudo cp /usr/lib/uhd/utils/uhd-usrp.rules /etc/udev/rules.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

### Problem: Device shows as "WestBridge" forever

This means the Zynq never successfully loaded the B210 firmware from the SD card.

**Solutions:**
1. Re-flash the SD card with a fresh `BOOT.BIN`.
2. Confirm the jumper is set to "SD card boot".
3. Perform a full power cycle (unplug both USB-C and USB-B for 5 seconds).
4. Connect to the serial console and read boot messages:
   ```bash
   sudo screen /dev/ttyUSB1 115200
   ```

---

## 📡 Signal Issues

### Problem: No audio from FM receiver

**Diagnose:** Add a **QT GUI Frequency Sink** right after the USRP Source. You should see a bump at the station's center frequency.

**Solutions:**
1. Increase RF gain (try 60 dB).
2. Verify your antenna is connected and appropriate for the frequency.
3. Check you are tuning to an actual FM station (use a conventional radio to verify).
4. Make sure audio decimation is correct: WBFM audio rate = USRP rate / decimation.

### Problem: Audio is distorted or "underflow/overflow"

UHD will print `O` (overflow — samples dropped on RX) or `U` (underflow — samples dropped on TX).

**Solutions:**
1. Lower the USRP sample rate (try 500 kSPS instead of 2 MSPS).
2. Use a USB 3.0 port, not 2.0.
3. Enable real-time scheduling: `sudo sysctl -w kernel.sched_rt_runtime_us=-1`
4. Increase buffer sizes in the USRP Source: set `Num Mboards: 1`, try different `Stream Args`.

---

## 🖥️ GNU Radio Issues

### Problem: `ModuleNotFoundError: No module named 'gnuradio'`

Your Python environment is not using the system GNU Radio.

**Solution:**
```bash
# Check which Python GRC uses
which gnuradio-companion

# Make sure you're not in a venv
deactivate 2>/dev/null

# Use system Python
python3 -c "import gnuradio; print(gnuradio.__version__)"
```

### Problem: "qt_gui" blocks don't appear

You're missing PyQt5.

```bash
sudo apt install -y python3-pyqt5 python3-pyqtgraph
```

---

## 🔊 Audio Issues

### Problem: "Audio sink: failed to open audio device"

**Solutions:**
1. Install PulseAudio utilities: `sudo apt install -y pulseaudio-utils`
2. Make sure PulseAudio is running: `pulseaudio --start`
3. Try specifying a device in the Audio Sink: `default` or `pulse`.
4. For ALSA-only systems: `sudo apt install -y alsa-utils`

---

## 🛰️ GPSDO Issues (SignalSDR Pro has one!)

The SignalSDR Pro includes a GPS-disciplined oscillator (GPSDO). To use it:

```bash
# In the USRP Source block:
#   Clock Source: "gpsdo"
#   Time Source: "gpsdo"
```

If GPS doesn't lock:
- Take the device near a window (GPS signals are weak indoors).
- Wait 5–10 minutes for initial satellite acquisition.
- Check `uhd_usrp_probe` — you should see `Found an internal GPSDO: GPSTCXO v3.2`.

---

## 🧪 When All Else Fails

1. Run a known-good flowgraph from the community. The user's own files `ex08_live_fm.grc` and `usrp_fm_receiver.grc` are great smoke tests.
2. Ask on the Signalens GitHub issues page: https://github.com/signalens/signalsdrpro/issues
3. Search the GNU Radio mailing list: https://chat.gnuradio.org/

---

**Next:** [Fundamentals — Signals & Systems Basics →](../01_fundamentals/01_signals_basics.md)
