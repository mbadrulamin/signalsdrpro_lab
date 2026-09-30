#!/usr/bin/env bash
# Demo 5 — Noise against a clean digital signal. No radio needed.
#
#   ./d5_bpsk.sh
#
# The constellation starts as two tight dots.
# Drag the "Eb/N0 (dB)" slider down from 8 towards 0: the dots smear into clouds,
# and the error count in THIS terminal starts to climb.

source "$(dirname "$0")/common.sh"

say "Demo 5: a digital link, simulated. Drag Eb/N0 down; watch the dots and the errors."
cd "$LABS/lab07_bpsk_link_sim" || exit 1
exec python3 lab07_bpsk_link_sim.py
