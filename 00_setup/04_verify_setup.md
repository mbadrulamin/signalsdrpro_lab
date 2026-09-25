# ✅ Setup 04 — Check That Everything Works

> **What you will do:** four short checks that prove the whole chain works — driver, radio,
> GNU Radio, and a real signal.
> **Before this:** [Setup 01](./01_install_uhd.md), [02](./02_flash_b210_firmware.md) and
> [03](./03_install_gnuradio.md).
> **Time:** about 10 minutes. **Difficulty:** easy.

Each check tests one more part of the chain. If one fails, you know exactly where the problem
is.

```
  Check 1: driver sees radio   Check 2: radio details   Check 3: live spectrum   Check 4: record samples
        uhd_find_devices   →      uhd_usrp_probe     →        uhd_fft          →     uhd_rx_cfile
```

---

## Check 1 — Does the driver see the radio?

Power-cycle the radio (unplug both cables, wait 2 s, power first, then data — see
[Setup 02](./02_flash_b210_firmware.md#4-connect-the-cables--in-this-order)). Then:

```bash
uhd_find_devices
```

✅ **Pass:**

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

(Your serial number will be different.)

❌ **`No UHD Devices Found`** → [Setup 05 — "No devices found"](./05_troubleshooting.md).

---

## Check 2 — Can the radio start properly?

```bash
uhd_usrp_probe
```

This loads the firmware and FPGA image and prints a long description. Look for these lines:

| Look for | Meaning |
|---|---|
| `Loading FPGA image: .../usrp_b210_fpga.bin` | UHD found the images |
| `Operating over USB 3.` | ✅ USB 3.0 — good. `USB 2` means only low sample rates will work |
| `Found an internal GPSDO: GPSTCXO v3.2 for SDRPro` | The SignalSDR Pro's GPS clock |
| `Mboard: B210` | It is acting as a B210 |
| `FW Version: 8.0`, `FPGA Version: 16.0` | Firmware and FPGA versions (numbers may differ) |
| `Freq range: 50.000 to 6000.000 MHz` | What UHD allows (the SignalSDR Pro is specified from 70 MHz) |

❌ **`Could not find path for image`** → [Setup 06](./06_fix_uhd_version_conflict.md).

---

## Check 3 — Can you see real signals?

`uhd_fft` is a ready-made spectrum display that comes with GNU Radio. Screw the antenna onto
`TX/RX`, then:

```bash
uhd_fft -f 98e6 -s 2e6 -g 40 -A TX/RX
```

| Option | Meaning |
|---|---|
| `-f 98e6` | tune to 98 MHz, the middle of the FM band |
| `-s 2e6` | 2 MSPS, so you see 2 MHz of spectrum |
| `-g 40` | gain 40 dB |
| `-A TX/RX` | use the `TX/RX` antenna connector |

✅ **Pass:** a window opens with a live spectrum. You see **humps** about 200 kHz wide — FM
stations — standing above a flat, grassy **noise floor**. A thin spike exactly in the centre is
the radio's own leak, not a station.

❌ **Only a flat line:** the antenna is not connected, or you are in a building that blocks
signals. Check the connector and try near a window.

> 💡 This also proves **GNU Radio** can use the radio. `uhd_fft` uses the same UHD library as
> your flowgraphs will. If `uhd_find_devices` works but `uhd_fft` fails with
> `Could not find path for image`, you have two UHD versions: see
> [Setup 06](./06_fix_uhd_version_conflict.md).

Close the window when you are done.

---

## Check 4 — Can you record samples?

`uhd_rx_cfile` saves raw IQ samples to a file. Record one second (1 million samples at 1 MSPS):

```bash
uhd_rx_cfile -f 98e6 --samp-rate 1e6 -g 40 -A TX/RX -N 1000000 /tmp/test_capture.cfile
ls -lh /tmp/test_capture.cfile
```

✅ **Pass:** the file is about **7.7 MB** (1,000,000 samples × 8 bytes = 8,000,000 bytes).

Now check the level with Python:

```bash
python3 -c "
import numpy as np
x = np.fromfile('/tmp/test_capture.cfile', dtype=np.complex64)
print(f'{len(x):,} samples, level {10*np.log10(2*np.mean(abs(x)**2)):.1f} dBFS, '
      f'peak {20*np.log10(abs(x).max()):.1f} dBFS')"
```

✅ **Pass:** a level somewhere around **−50 to −10 dBFS**, and a peak **below 0 dBFS**.
If the peak is 0 dBFS, the gain is too high (the signal is clipping) — try `-g 25`.

---

## All four passed?

🎉 **Your setup is complete.** Every part works: driver, radio, GNU Radio and antenna.

Go and build your first radio: **[Lab 01 — The Simplest FM Receiver](../02_flowgraphs/lab01_simple_wbfm/README.md)**.
(Or, if you have not yet, read [Fundamentals 01–04](../01_fundamentals/01_signals_basics.md)
first.)

> 💡 **Keep these four checks.** Whenever something stops working later, run them again. If they
> all pass, the problem is in your flowgraph, not in the setup.

---

## ✅ Summary

| Check | Command | Proves |
|---|---|---|
| 1 | `uhd_find_devices` | UHD can see the radio |
| 2 | `uhd_usrp_probe` | the radio starts, over USB 3, with its GPS clock |
| 3 | `uhd_fft -f 98e6 -s 2e6 -g 40 -A TX/RX` | GNU Radio + radio + antenna show real signals |
| 4 | `uhd_rx_cfile ... -N 1000000 file` | samples can be recorded, at a sensible level |

**Next:** [Setup 05 — Troubleshooting](./05_troubleshooting.md) (if you need it), or
[Lab 01 →](../02_flowgraphs/lab01_simple_wbfm/README.md)
