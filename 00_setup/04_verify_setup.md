# ✅ 04 — Verifying the Full Setup

> **Estimated time:** 10 minutes  
> **Difficulty:** Easy  
> **Prerequisites:** UHD installed, SignalSDR Pro flashed with B210 image, GNU Radio installed

---

## Goal

By the end of this step, you will have:

1. A SignalSDR Pro successfully recognized as USRP B210
2. GNU Radio Companion talking to the SDR
3. Your first real radio signal playing through your speakers

---

## Step 1 — Confirm UHD Sees the Device

Open a terminal and run:

```bash
uhd_find_devices
```

Expected output:

```
[INFO] [UHD] linux; GNU C++ version 13.x.x; UHD_4.6.0.0
--------------------------------------------------
-- UHD Device 0
--------------------------------------------------
Device Address:
    serial: XXXXXX
    name: MyB210
    product: 2
    type: b200
```

Then do a full probe:

```bash
uhd_usrp_probe
```

Look for these key lines:
- `Mboard: B210`
- `FW Version: 8.0` (or newer)
- `FPGA Version: 16.0`
- `RX Frontend: FE-RX2` with `Freq range: 50.000 to 6000.000 MHz`
- `Found an internal GPSDO` (SignalSDR Pro has one)

---

## Step 2 — Test RF Reception in Terminal

Before launching GRC, let's verify the RF chain works using the UHD command-line tool `uhd_rx_cfile`, which simply dumps raw I/Q samples to a file:

```bash
# Capture 1 second of I/Q at 100 MHz FM band, 1 MSPS, gain 40 dB
uhd_rx_cfile --args "type=b200" \
             --freq 100e6 \
             --rate 1e6 \
             --gain 40 \
             --samples 1000000 \
             /tmp/test_capture.cfile

ls -lh /tmp/test_capture.cfile
# Should be ~8 MB (1M samples × 8 bytes per complex float)
```

If this command runs without errors, the RF chain is working. The file contains raw I/Q samples from your antenna at 100 MHz.

---

## Step 3 — Build Your First FM Receiver in GRC

Open GNU Radio Companion:

```bash
gnuradio-companion
```

Create this minimal flowgraph:

### Blocks

1. **UHD: USRP Source**
   - Output Type: `Complex float32`
   - Device Address: `""` (empty — auto-detect)
   - Sample Rate: `1e6` (1 MSPS)
   - Ch0: Center Freq = `100e6` (or a local FM station), Gain = `40`, Antenna = `TX/RX`

2. **Analog: WBFM Receive**
   - Quadrature Rate: `1e6`
   - Audio Decimation: `20` → audio rate = 50 kHz (mono)

3. **Audio: Sink**
   - Sample Rate: `50000` (matches audio output of WBFM Receive)

### Connections

```
USRP Source → WBFM Receive → Audio Sink
```

### Run

1. Save as `hello_sdr.grc`
2. Click ▶ Execute
3. Tune the station frequency until you hear audio

🎉 **Congratulations — you have just built a real FM radio with an SDR!**

---

## Step 4 — Interpret What You Built

Let's trace what's happening at every step:

```
Antenna → AD9361 (downconvert 100 MHz to baseband I/Q)
       → USB 3.0 stream → UHD → USRP Source block (1 MSPS complex)
       → WBFM Receive (FM demodulation, 20× decimation)
       → Audio Sink (50 kHz mono audio) → Speaker
```

You've successfully captured, digitized, downconverted, demodulated, and played a real-world broadcast radio signal. That's exactly what a commercial FM radio does, but now you **understand every step**.

---

## Step 5 — Sanity-Check Your Numbers

| Parameter | Value | Why |
|---|---|---|
| RF center frequency | 87.5 – 108 MHz | Commercial FM broadcast band |
| Sample rate (USRP) | 1 MSPS | 2× Nyquist for 500 kHz FM bandwidth |
| WBFM audio decimation | 20 | 1 MSPS / 20 = 50 kHz audio rate |
| Audio sink rate | 50000 Hz | Must match audio output of WBFM Receive |
| RF gain | 40 dB | Good starting point for local stations |

If your numbers match and you hear audio, your lab is ready.

---

## 📝 Summary Checklist

- [ ] `uhd_find_devices` shows the B200
- [ ] `uhd_usrp_probe` returns full device info
- [ ] `uhd_rx_cfile` captures I/Q samples without errors
- [ ] GRC launches successfully
- [ ] Your 3-block FM receiver plays real audio
- [ ] You can explain every stage of the signal chain

---

**Next:** [05 — Troubleshooting →](./05_troubleshooting.md)  
Or jump straight to [Fundamentals →](../01_fundamentals/01_signals_basics.md)
