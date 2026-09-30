#!/usr/bin/env bash
# Demo 3 — Tour the busy bands.
#
#   ./d3_bands.sh         part 1: the live spectrum, starting on the FM band
#   ./d3_bands.sh scan    part 2: the TV band scanner (close part 1 first)
#   ./d3_bands.sh test    part 2 with no radio: the scanner's own self-test
#
# Part 1, type each into the window's Center Frequency box in turn:
#   89.9e6      FM radio          wide, steady humps
#   945e6       mobile phones     dense, busy blocks (towers talking to phones)
#   2.437e9     Wi-Fi channel 6   short bursts that come and go
#   433.92e6    car keys          quiet until someone presses a key (bonus)

source "$(dirname "$0")/common.sh"

case "${1:-}" in
    scan)
        need_free_radio
        say "Demo 3 part 2: scanning TV channels 21 to 36 (about 20 seconds)"
        cd "$SCRIPTS" || exit 1
        exec python3 scan_tv_band.py --first 21 --last 36 --dwell 0.4
        ;;
    test)
        say "Demo 3 fallback: the scanner's self-test. No radio is used."
        cd "$SCRIPTS" || exit 1
        exec python3 scan_tv_band.py --selftest
        ;;
    *)
        need_free_radio
        say "Demo 3 part 1: the band tour"
        echo "  89.9e6 -> 945e6 -> 2.437e9  (bonus: 433.92e6 with a car key)"
        exec uhd_fft -f 89.9e6 -s 20e6 -g "${GAIN:-50}" -A TX/RX
        ;;
esac
