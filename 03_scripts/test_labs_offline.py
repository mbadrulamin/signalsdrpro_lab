#!/usr/bin/env python3
"""
test_labs_offline.py — check that the labs' real flowgraphs give the right answer.

No radio is needed. For each lab it:
  1. makes a test signal whose correct output is known (make_fm_test_iq.py),
  2. runs the lab's generated .py on it, with the radio swapped for that file
     (run_offline.py), and
  3. measures the audio and compares it with what it should be.

This catches mistakes that "does it compile?" cannot: a squelch that never
closes, a stereo decoder that is really mono, a wrong audio rate.

Usage:
    python3 test_labs_offline.py            # all tests
    python3 test_labs_offline.py lab04      # only tests whose name contains "lab04"

Exit code 0 = all passed.
"""
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.join(HERE, '..', '02_flowgraphs')
sys.path.insert(0, HERE)
from make_fm_test_iq import make  # noqa: E402


def run_lab(lab_py, iq, workdir, sets=()):
    """Run a lab on IQ samples; return {channel: audio array} and the audio rate."""
    cfile = os.path.join(workdir, 'in.cfile')
    iq.astype(np.complex64).tofile(cfile)
    out = os.path.join(workdir, 'out')
    cmd = [sys.executable, os.path.join(HERE, 'run_offline.py'), os.path.join(LABS, lab_py), cfile, '--out', out]
    for s in sets:
        cmd += ['--set', s]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if res.returncode != 0:
        raise RuntimeError(res.stderr[-2000:])
    rate = None
    for line in res.stdout.splitlines():
        if line.startswith('channel 0:'):
            rate = float(line.split(' at ')[1].split(' Hz')[0])
    chans = {}
    for i in range(8):
        f = os.path.join(out, f'audio_ch{i}.f32')
        if os.path.exists(f):
            chans[i] = np.fromfile(f, np.float32)
            os.remove(f)
    return chans, rate


def tone_level(x, rate, hz):
    x = x[len(x) // 3:]                      # skip the start-up transient
    spec = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    freqs = np.fft.rfftfreq(len(x), 1 / rate)
    k = np.argmin(abs(freqs - hz))
    return spec[max(k - 3, 0):k + 4].max()


def db(a, b):
    return 20 * np.log10(a / b)


# ---------------------------------------------------------------- the tests
# Each returns (passed, message).

def lab01_tone(tmp):
    chans, rate = run_lab('lab01_simple_wbfm/lab01_simple_wbfm.py',
                          make(rate=1e6, seconds=2, stereo=False), tmp)
    a = chans[0]
    ok = rate == 50000 and tone_level(a, rate, 1000) > 20 * tone_level(a, rate, 3000)
    return ok, f'audio rate {rate:g} Hz (want 50000); 1 kHz tone recovered, rms {np.std(a):.3f}'


def lab02_tone(tmp):
    chans, rate = run_lab('lab02_enhanced_wbfm/lab02_enhanced_wbfm.py',
                          make(rate=2e6, seconds=2, stereo=False), tmp)
    a = chans[0]
    ok = rate == 48000 and tone_level(a, rate, 1000) > 20 * tone_level(a, rate, 3000)
    return ok, f'audio rate {rate:g} Hz (want 48000); 1 kHz tone recovered, rms {np.std(a):.3f}'


def lab03_squelch(tmp):
    station, rate = run_lab('lab03_advanced_wbfm/lab03_advanced_wbfm.py',
                            make(rate=2e6, seconds=2, stereo=False, snr_db=40), tmp)
    rng = np.random.default_rng(2)
    n = int(2e6 * 2)
    noise = 0.001 * (rng.standard_normal(n) + 1j * rng.standard_normal(n)) / np.sqrt(2)
    empty, _ = run_lab('lab03_advanced_wbfm/lab03_advanced_wbfm.py', noise, tmp)
    s_rms = np.std(station[0][len(station[0]) // 2:])
    e_rms = np.std(empty[0][len(empty[0]) // 2:])
    ok = s_rms > 0.05 and e_rms < 1e-6
    return ok, (f'station: audio rms {s_rms:.3f} (want > 0.05);  '
                f'empty channel at -60 dBFS: audio rms {e_rms:.2e} (want silence)')


def lab04_separation(tmp):
    chans, rate = run_lab('lab04_stereo_wbfm/lab04_stereo_wbfm.py',
                          make(rate=2e6, seconds=3, left_hz=1000, right_hz=1700, snr_db=40), tmp)
    left, right = chans[0], chans[1]
    sep_l = db(tone_level(left, rate, 1000), tone_level(left, rate, 1700))
    sep_r = db(tone_level(right, rate, 1700), tone_level(right, rate, 1000))
    ok = sep_l > 25 and sep_r > 25
    return ok, f'stereo separation: left {sep_l:.1f} dB, right {sep_r:.1f} dB (want > 25 dB each)'


TESTS = [lab01_tone, lab02_tone, lab03_squelch, lab04_separation]


def main():
    pick = sys.argv[1] if len(sys.argv) > 1 else ''
    failed = 0
    for test in TESTS:
        if pick not in test.__name__:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            try:
                ok, msg = test(tmp)
            except Exception as e:                       # report, keep going
                ok, msg = False, f'ERROR: {e}'
        failed += not ok
        print(f'{"PASS" if ok else "FAIL"}  {test.__name__:18s} {msg}')
    print(f'\n{"all passed" if not failed else f"{failed} failed"}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
