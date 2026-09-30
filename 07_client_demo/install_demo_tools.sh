#!/usr/bin/env bash
# Install the point-and-click tools used as a bonus in the client briefing.
#
#   ./install_demo_tools.sh              gqrx only
#   ./install_demo_tools.sh --all        gqrx and inspectrum
#
# Needs the internet and your password (sudo). Nothing here transmits.
# gqrx is a BONUS. If it does not see the radio within 20 minutes, stop:
# the demos use uhd_fft, which already works on this machine.

set -e
pkgs="gqrx-sdr"
[ "${1:-}" = "--all" ] && pkgs="$pkgs inspectrum"

echo "Installing: $pkgs"
sudo apt-get update -qq
sudo apt-get install -y $pkgs

echo
command -v gqrx >/dev/null && echo "OK    gqrx installed: $(gqrx --version 2>/dev/null | head -1)"
command -v inspectrum >/dev/null && echo "OK    inspectrum installed"

cat <<'TXT'

How to open the radio in gqrx (first run only):
  1. Start gqrx. The "Configure I/O devices" window opens.
  2. Device: choose the Ettus / UHD entry. If none is listed, type in "Device string":
        uhd,type=b200
  3. Input rate: 2000000 (2 MHz) to start. Antenna: TX/RX.
  4. Click OK, then the power button (top left). Type 89.9 MHz in the frequency box.
     Set the mode to "WFM (stereo)" to hear BFM.

If gqrx says it found no device, or crashes when you press the power button,
the two UHD versions on this machine are the likely cause. Do not spend more
than 20 minutes on it. Use ./demo/d1_spectrum.sh instead.

inspectrum (only with --all) opens recordings. It needs the file name to end in
.cf32, and the sample rate typed in (2000000 for the Demo 4 recording):
  cp ~/sdr_demo/capture_100M0_2Msps_fc32.iq /tmp/capture.cf32 && inspectrum /tmp/capture.cf32
TXT
