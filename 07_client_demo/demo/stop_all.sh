#!/usr/bin/env bash
# Stop every demo program that may be holding the radio, by its process number.
#
#   ./stop_all.sh
#
# Use this after the television demo, or when a demo says the radio is busy.
# It never uses "pkill -f": that pattern can match the terminal that ran it.

source "$(dirname "$0")/common.sh"

users="$(radio_users)"
if [ -z "$users" ]; then
    ok "Nothing is running. The radio is free."
    exit 0
fi

say "Stopping:"
echo "$users" | sed 's/^/  /'
pids="$(echo "$users" | awk '{print $1}')"
kill $pids 2>/dev/null
sleep 3

left="$(radio_users)"
if [ -n "$left" ]; then
    warn "Still running after 3 seconds. Forcing:"
    echo "$left" | sed 's/^/  /'
    kill -9 $(echo "$left" | awk '{print $1}') 2>/dev/null
    sleep 1
fi

if [ -z "$(radio_users)" ]; then
    ok "All stopped. The radio is free."
else
    bad "Something is still running. Unplug the radio's USB cable."
    exit 1
fi
