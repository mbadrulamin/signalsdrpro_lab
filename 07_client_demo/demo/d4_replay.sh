#!/usr/bin/env bash
# Demo 4 — Record and replay: play back a recording with no antenna.
#
#   ./d4_replay.sh
#
# Does not use the radio. Unplug the antenna in front of the room first.
# In the window, type 200e3 into "Offset from centre" to play BFM 89.9.
# Move the offset to hear the other stations that are inside the same file.

source "$(dirname "$0")/common.sh"

restore capture_100M0_2Msps_fc32.iq || {
    echo "  Make the recording tonight with ./d4_record.sh"
    exit 1
}
say "Demo 4: playing back the recording. The radio is not used."
echo "  Type 200e3 into 'Offset from centre' for BFM 89.9"
cd "$LABS/lab05_iq_record_playback" || exit 1
exec python3 lab05_iq_playback.py
