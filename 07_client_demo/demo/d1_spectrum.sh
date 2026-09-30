#!/usr/bin/env bash
# Demo 1 — See the invisible: a live picture of the FM band.
#
#   ./d1_spectrum.sh            FM band, 88 to 108 MHz
#   ./d1_spectrum.sh 945e6      any other centre frequency
#
# Close the window to stop.

source "$(dirname "$0")/common.sh"
need_free_radio

FREQ="${1:-98e6}"
GAIN="${GAIN:-50}"

say "Demo 1: live spectrum at $FREQ Hz, 20 MHz wide, gain $GAIN"
echo "  Type a new frequency into the window's Center Frequency box to move."
exec uhd_fft -f "$FREQ" -s 20e6 -g "$GAIN" -A TX/RX
