# Fix UHD Version Conflict (Terminal vs GUI Launcher)

## 1. Problem Description

### Symptoms
- **From Terminal:** Running `gnuradio-companion` works, and the USRP B210 is detected without issue.
- **From GUI Launcher (Desktop Icon / App Menu):** Flowgraphs fail immediately with:
  ```text
  [INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
  [WARNING] [B200] EnvironmentError: IOError: Could not find path for image: usrp_b200_fw.hex
  Using images directory: <no images directory located>
  RuntimeError: LookupError: KeyError: No devices found for -----> Empty Device Address
  ```

---

## 2. Root Cause: Why Terminal Works but GUI Fails

The problem stems from having two UHD library versions installed on the same system, combined with how Linux handles desktop application environments:

| Component | Version | Source | Default Search Path |
|---|---|---|---|
| CLI Tools (`uhd_find_devices`) | **UHD 4.10.0** | Ettus Research PPA | `/usr/share/uhd/4.10.0/images/` |
| GNU Radio (`libgnuradio-uhd`) | **UHD 4.6.0** | Ubuntu Noble standard repo | `/usr/share/uhd/images/` |

### Why GUI Launches Fail
1. The firmware downloader (`uhd_images_downloader`) installs images into `/usr/share/uhd/4.10.0/images/`.
2. A common workaround is adding `export UHD_IMAGES_DIR=/usr/share/uhd/4.10.0/images` to `~/.bashrc`.
3. In a **terminal session**, `~/.bashrc` is automatically sourced, so GNU Radio knows where to find the firmware.
4. When launched from the **Desktop GUI** (GNOME Application Menu, desktop shortcut, or `.desktop` entry), applications are launched directly by the desktop manager / systemd user session. **GUI launchers never execute `~/.bashrc`**.
5. In GUI mode, `UHD_IMAGES_DIR` is empty. GNU Radio's UHD 4.6.0 library falls back to `/usr/share/uhd/images/`, which does not exist by default. Without `usrp_b200_fw.hex`, the B210's Cypress FX3 USB controller cannot initialize, and the device remains undetected.

---

## 3. The Solution

The cleanest and most reliable fix is to link the images at the **filesystem level** rather than relying on shell environment variables. Symlinks are permanent and work regardless of how an application is started.

### Option A: Automated Fix (Recommended)

Run the automated fix script included in this repository:

```bash
cd "/home/ubuntu/GNU Radio/signalsdrpro_lab/00_setup"
./fix_uhd_version_conflict.sh
```

### Option B: Manual Fix

If you prefer to apply the fix manually, run the following commands:

#### Step 1: Create Filesystem Symlinks
Create symbolic links so that UHD's default compiled-in search paths point directly to the downloaded 4.10.0 images:

```bash
sudo ln -sfn /usr/share/uhd/4.10.0/images /usr/share/uhd/images
sudo ln -sfn /usr/share/uhd/4.10.0/images /usr/share/uhd/4.6.0/images
```

#### Step 2: Configure System-Wide Environment (for PAM / GUI Sessions)
Add the environment variable to `/etc/environment`. PAM reads this file for all user sessions (including graphical desktop logins):

```bash
echo 'UHD_IMAGES_DIR="/usr/share/uhd/4.10.0/images"' | sudo tee -a /etc/environment
```

---

## 4. Verification

### 1. Verify Symlinks in the Filesystem
```bash
ls -la /usr/share/uhd/images/usrp_b200_fw.hex
```
*Expected result:* The file exists and resolves to `/usr/share/uhd/4.10.0/images/usrp_b200_fw.hex`.

### 2. Test Device Detection Without Environment Variables
Simulate a GUI launch environment by stripping `UHD_IMAGES_DIR` and running a probe through GNU Radio:

```bash
env -u UHD_IMAGES_DIR python3 -c "from gnuradio import uhd; s = uhd.usrp_source('', uhd.stream_args('fc32', '', [0]))"
```

*Expected output:*
```text
[INFO] [UHD] linux; GNU C++ version 13.2.0; Boost_108300; UHD_4.6.0.0+ds1-5.1ubuntu0.24.04.1
[INFO] [B200] Detected Device: B210
[INFO] [B200] Operating over USB 3.
[INFO] [B200] Initialize Radio control...
```

### 3. Test GNU Radio Companion GUI
1. Launch GNU Radio Companion from the application menu (GUI).
2. Open any lab flowgraph (e.g., `02_flowgraphs/lab01_simple_wbfm/lab01_simple_wbfm.grc`).
3. Press **F5** (Run). The flowgraph will now initialize the USRP B210 and execute cleanly.

---

## 5. Summary: Fix Methods Comparison

| Method | Terminal Support | GUI Launcher Support | Survives Reboot | Notes |
|---|:---:|:---:|:---:|---|
| `export` in terminal | ✅ | ❌ | ❌ | Lost when terminal is closed. |
| `~/.bashrc` | ✅ | ❌ | ✅ | Desktop launchers do not source `.bashrc`. |
| `/etc/environment` | ✅ | ✅ | ✅ | Loaded by PAM on login; covers graphical sessions. |
| **Filesystem Symlinks** | ✅ | ✅ | ✅ | **Best**: Operates at OS level; 100% independent of shell or launch method. |
