# 🔧 Setup 06 — Fix the "Two UHD Versions" Problem

> **What you will do:** fix `Could not find path for image: usrp_b200_fw.hex` when your
> computer has two versions of UHD.
> **Only read this if** `uhd_find_devices` works but GNU Radio fails with that error — or GNU
> Radio works from a terminal but not from the app menu.
> **Time:** about 5 minutes.

---

## 1. The symptoms

One or more of these:

- `uhd_find_devices` finds the radio, but every GNU Radio flowgraph fails.
- GNU Radio works when started from a **terminal**, but fails when started from the **app menu**
  (or a desktop icon).
- The error looks like this. Note the version on the first line — **4.6.0**:

  ```text
  [INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
  [WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
  Using images directory: <no images directory located>
  RuntimeError: LookupError: KeyError: No devices found for -----> Empty Device Address
  ```

---

## 2. Why it happens

Your computer has **two** UHD versions:

| Who uses it | UHD version | Came from | Looks for images in |
|---|---|---|---|
| GNU Radio | **4.6.0** | Ubuntu | `/usr/share/uhd/4.6.0/images/` |
| `uhd_find_devices` and other tools | **newer** (4.10, 4.11, …) | the Ettus PPA | `/usr/share/uhd/<that version>/images/` |

GNU Radio from Ubuntu is built for UHD 4.6.0, so it always uses 4.6.0 — even when a newer UHD is
also installed. When you run `sudo uhd_images_downloader`, the **newer** version's downloader
puts the images in the **newer** version's folder. GNU Radio's UHD looks in its own folder, finds
nothing, and stops.

**Why does it work from a terminal but not the menu?** A common half-fix is to add
`export UHD_IMAGES_DIR=...` to `~/.bashrc`. Terminals read `~/.bashrc`. Programs started from
the app menu **do not**. So the fix only works in terminals.

> 💡 **How to avoid this completely:** install UHD from Ubuntu, like GNU Radio — see
> [Setup 01, Option A](./01_install_uhd.md#3-option-a--ubuntus-own-packages-recommended).
> Then there is only one version.

---

## 3. The fix

The reliable fix is to make each UHD version's images folder **point to** the one real copy of
the images, with a **symbolic link** (a shortcut in the file system). This works however the
program is started, and survives restarts.

### Option A — run the script (recommended)

```bash
cd 00_setup
./fix_uhd_version_conflict.sh --dry-run     # first, just see what it would do
./fix_uhd_version_conflict.sh               # then do it (asks for your password)
```

The script works out the versions by itself. On the computer this course was tested on, the
dry run printed:

```
==> Finding the installed UHD versions...
     GNU Radio uses UHD      : 4.6.0
     command-line tools use  : 4.11.0
==> Looking for the image files (usrp_b200_fw.hex)...
[OK] Images are in: /usr/share/uhd/4.10.0/images
==> Making sure every UHD version can find them...
[OK] UHD 4.6.0 already finds them (/usr/share/uhd/4.6.0/images)
     would run: sudo mkdir -p /usr/share/uhd/4.11.0
     would run: sudo ln -sfn /usr/share/uhd/4.10.0/images /usr/share/uhd/4.11.0/images
```

What the script does:

1. Finds which UHD version GNU Radio uses, and which the tools use.
2. Finds the image files. If there are none, downloads them.
3. For each version that cannot see them, creates a link from its images folder to the real
   copy.
4. Warns you if `/etc/environment` sets `UHD_IMAGES_DIR` to a folder that does not have the
   images.
5. Tests that GNU Radio can start the radio without any environment variable.

It is safe to run more than once. If there is only one UHD version, it says so and changes
nothing.

### Option B — do it by hand

First find the versions and the images:

```bash
python3 -c "from gnuradio import uhd; print(uhd.get_version_string())"   # GNU Radio's UHD, e.g. 4.6.0...
uhd_config_info --version                                                # the tools' UHD, e.g. 4.11.0...
ls -d /usr/share/uhd/*/images                                            # where images folders are
ls /usr/share/uhd/*/images/usrp_b200_fw.hex                              # which one has the files
```

Then link GNU Radio's folder to the one that has the files. For example, if GNU Radio uses
4.6.0 and the files are in `4.10.0`:

```bash
sudo ln -sfn /usr/share/uhd/4.10.0/images /usr/share/uhd/4.6.0/images
```

> ⚠️ If `/usr/share/uhd/4.6.0/images` already exists as a **real folder** (not a link), `ln`
> would put the link *inside* it. In that case, remove the empty folder first
> (`sudo rmdir /usr/share/uhd/4.6.0/images`) — or use the script, which handles this.

---

## 4. Check that it worked

**1. The file can be found through GNU Radio's folder:**

```bash
ls -la /usr/share/uhd/4.6.0/images/usrp_b200_fw.hex
```

✅ The file is listed.

**2. GNU Radio can start the radio with no environment variable** (this is what a program started
from the app menu sees). With the radio plugged in:

```bash
env -u UHD_IMAGES_DIR python3 -c "from gnuradio import uhd; s = uhd.usrp_source('', uhd.stream_args(cpu_format='fc32', channels=[0]))"
```

✅ Expected:

```text
[INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
[INFO] [B200] Detected Device: B210
[INFO] [B200] Operating over USB 3.
[INFO] [B200] Initialize Radio control...
```

**3. From the app menu:** start GNU Radio Companion from the menu, open
`02_flowgraphs/lab01_simple_wbfm/lab01_simple_wbfm.grc`, and press **F5**.

---

## 5. Comparing the ways to fix it

| Method | Terminal | App menu | After restart | Notes |
|---|:---:|:---:|:---:|---|
| `export UHD_IMAGES_DIR=...` in a terminal | ✅ | ❌ | ❌ | Lost when the terminal closes |
| the same line in `~/.bashrc` | ✅ | ❌ | ✅ | The app menu does not read `.bashrc` |
| `UHD_IMAGES_DIR=...` in `/etc/environment` | ✅ | ✅ | ✅ | Read at login. Must be updated if you upgrade UHD |
| **links in the file system (the script)** | ✅ | ✅ | ✅ | **Best** — works however the program starts |

---

## ✅ Summary

- The error means GNU Radio's UHD (4.6.0) cannot find images downloaded by a newer UHD.
- **Fix:** run `./fix_uhd_version_conflict.sh`. It links every version's images folder to one copy.
- **Avoid it next time:** install UHD from Ubuntu, like GNU Radio.

**Back to:** [Setup 05 — Troubleshooting](./05_troubleshooting.md) ·
[Setup 04 — Check that everything works](./04_verify_setup.md)
