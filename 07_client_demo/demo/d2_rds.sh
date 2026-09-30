#!/usr/bin/env bash
# Demo 2 — Hidden data: read the station's name out of an FM broadcast.
#
#   ./d2_rds.sh          live, with the radio
#   ./d2_rds.sh test     no radio: a test signal made on this laptop
#
# In the window, type these three values (the sliders start somewhere else):
#   FM Station (Hz)      89.7e6
#   Channel Offset (Hz)  200e3
#   RF Gain (dB)         60        (55 to 65; lower it if the sound distorts)
#
# The name appears in THIS terminal as:  [RDS] ... PS='BFM 89.9'

source "$(dirname "$0")/common.sh"

if [ "${1:-}" = "test" ]; then
    say "Demo 2 fallback: a TEST signal, not a real station. Say so out loud."
    cd "$SCRIPTS" || exit 1
    python3 simulate_rds_decode.py --seconds 8 --snr 30 --ps "SDR LAB " \
        --rt "Hello from the SignalSDR Pro lab" --out /tmp/rds_test_2Msps_fc32.iq || exit 1
    cd "$LABS/lab08_rds_decoder" || exit 1
    exec python3 lab08_rds_from_file.py
fi

need_free_radio
say "Demo 2: RDS decoder"
echo "  Type into the window:  FM Station 89.7e6   Channel Offset 200e3   RF Gain 60"
echo "  Watch this terminal for:  [RDS] ... PS='BFM 89.9'"
cd "$LABS/lab08_rds_decoder" || exit 1
exec python3 lab08_rds_decoder.py
