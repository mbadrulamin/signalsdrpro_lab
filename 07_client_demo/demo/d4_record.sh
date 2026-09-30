#!/usr/bin/env bash
# Demo 4, TONIGHT ONLY — make the recording that Demo 4 plays back.
#
#   ./d4_record.sh
#
# In the window:
#   1. Type 89.7e6 into Centre Frequency. Set RF Gain so the stations are clear (about 50).
#   2. Click Record: ON. Count 20 seconds. Click Record: OFF.   (20 s = 320 MB)
#   3. Close the window.
# This script then saves the file to ~/sdr_demo, where a reboot cannot delete it.

source "$(dirname "$0")/common.sh"
need_free_radio

FILE=capture_100M0_2Msps_fc32.iq
say "Demo 4 preparation: record 20 seconds of the FM band"
echo "  Centre Frequency 89.7e6 -> Record ON -> 20 s -> Record OFF -> close the window"
cd "$LABS/lab05_iq_record_playback" || exit 1
python3 lab05_iq_record.py

if [ -s "/tmp/$FILE" ]; then
    mkdir -p "$STORE"
    cp "/tmp/$FILE" "$STORE/$FILE"
    ok "Saved $(du -h "$STORE/$FILE" | cut -f1) to $STORE/$FILE"
else
    bad "No recording found in /tmp/$FILE. Did you click Record: ON?"
    exit 1
fi
