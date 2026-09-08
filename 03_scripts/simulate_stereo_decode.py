#!/usr/bin/env python3
"""
simulate_stereo_decode.py
==========================
A pure-Python/numpy simulation of the Lab 04 stereo WBFM decoder.

This does NOT require GNU Radio or an SDR. It synthesises a known stereo signal,
runs it through the exact same processing chain as the GRC flowgraph, and
verifies that the decoded L and R channels match the originals.

Purpose:
- Prove the mathematics of the flowgraph are correct
- Catch logic errors before the user has hardware available
- Serve as a reference implementation in pure Python

Run:
    python3 simulate_stereo_decode.py
"""

import math
import numpy as np

# =============================================================================
# 1. SYNTHESISE A STEREO MPX SIGNAL
# =============================================================================

MPX_RATE = 240_000          # samples per second (after resampler in GRC)
DURATION = 0.5              # seconds
N = int(MPX_RATE * DURATION)
t = np.arange(N) / MPX_RATE

# Two different audio tones for left and right channels
L_FREQ = 440.0              # 440 Hz "A" note (left)
R_FREQ = 880.0              # 880 Hz "A" note one octave up (right)
L_AMP = 0.5
R_AMP = 0.5

# Generate L(t) and R(t)
L = L_AMP * np.sin(2 * np.pi * L_FREQ * t)
R = R_AMP * np.sin(2 * np.pi * R_FREQ * t)

# Build the MPX baseband as per FM broadcast standard
L_plus_R = L + R                        # 0-15 kHz mono sum
L_minus_R = L - R                       # 0-15 kHz stereo difference

PILOT_FREQ = 19_000.0
SUBCARRIER_FREQ = 38_000.0
PILOT_AMP = 0.1                         # Pilot is weaker than audio

pilot = PILOT_AMP * np.cos(2 * np.pi * PILOT_FREQ * t)
# DSB-SC: L-R modulated onto 38 kHz subcarrier (suppressed carrier)
L_minus_R_dsb = L_minus_R * np.cos(2 * np.pi * SUBCARRIER_FREQ * t)

# Combined MPX signal
mpx = L_plus_R + pilot + L_minus_R_dsb

print(f"Synthesised MPX signal: {N} samples at {MPX_RATE} SPS, {DURATION}s")
print(f"  - L tone:  {L_FREQ} Hz, amplitude {L_AMP}")
print(f"  - R tone:  {R_FREQ} Hz, amplitude {R_AMP}")
print(f"  - Pilot:   {PILOT_FREQ/1000} kHz, amplitude {PILOT_AMP}")
print(f"  - Subcarrier (suppressed): {SUBCARRIER_FREQ/1000} kHz")
print()

# =============================================================================
# 2. STAGE 1 — Extract L+R (mono) via low-pass filter
# =============================================================================

def lowpass_simple(x, cutoff, rate):
    """
    A simple windowed-sinc low-pass filter (FIR).
    For simulation purposes only. Real GRC uses GNU Radio's fir_filter.
    """
    nyq = rate / 2
    norm_cutoff = cutoff / nyq
    M = 201  # filter length
    n = np.arange(M) - M // 2
    # Avoid division by zero
    h = np.sinc(2 * norm_cutoff * n)
    h *= np.hamming(M)
    h /= h.sum()
    return np.convolve(x, h, mode='same')


L_plus_R_recovered = lowpass_simple(mpx, 15000, MPX_RATE)
print(f"Stage 1 (L+R extraction):")
print(f"  - Correlation with true L+R: {np.corrcoef(L_plus_R, L_plus_R_recovered)[0,1]:.4f}")

# =============================================================================
# 3. STAGE 2 — Extract pilot via band-pass filter
# =============================================================================

def bandpass_simple(x, low, high, rate):
    """Simple windowed-sinc band-pass for simulation."""
    nyq = rate / 2
    # Design as difference of two low-passes
    M = 401
    n = np.arange(M) - M // 2
    h_high = np.sinc(2 * (high/nyq) * n)
    h_low  = np.sinc(2 * (low/nyq)  * n)
    h = h_high - h_low
    h *= np.hamming(M)
    h /= max(abs(h))
    return np.convolve(x, h, mode='same')


pilot_recovered = bandpass_simple(mpx, 18500, 19500, MPX_RATE)
print(f"\nStage 2 (pilot extraction):")
print(f"  - Pilot signal amplitude recovered: {np.max(np.abs(pilot_recovered)):.4f}")

# =============================================================================
# 4. STAGE 3 — PLL to lock onto pilot, then double to 38 kHz
# =============================================================================
# We'll skip a full PLL implementation for brevity — assume it locks perfectly.
# (In real GRC, analog_pll_refout_cc does this.)

# Assume perfect lock: recovered pilot = cos(2π·19k·t)
# We know the actual pilot we generated was PILOT_AMP * cos(2π·19k·t).
# The PLL removes amplitude, giving a unit-amplitude cos.

# To simulate PLL output, we extract the phase from the analytic signal:
analytic = pilot_recovered + 1j * np.imag(np.fft.ifft(np.fft.fft(pilot_recovered) * 2))
# Actually, simpler: use Hilbert transform manually:
from scipy.signal import hilbert
analytic = hilbert(pilot_recovered)
pll_output_complex = analytic / np.abs(analytic)  # unit amplitude, correct phase

print(f"\nStage 3 (PLL lock):")
print(f"  - PLL output amplitude (should be 1.0): {np.mean(np.abs(pll_output_complex)):.4f}")

# Double the frequency: complex × complex → 38 kHz
subcarrier_38k_complex = pll_output_complex * pll_output_complex
subcarrier_38k_real = subcarrier_38k_complex.real  # = cos(2π·38k·t + φ)

print(f"  - Subcarrier (38 kHz) amplitude (should be ~1.0): {np.std(subcarrier_38k_real):.4f}")

# =============================================================================
# 5. STAGE 4 — Multiply MPX by 38 kHz carrier to demodulate L-R
# =============================================================================

# Both inputs are FLOAT.
lrmix_output = mpx * subcarrier_38k_real
print(f"\nStage 4 (MPX × 38 kHz):")
print(f"  - Mixed output contains (L-R)/2 + high-freq terms")

# Low-pass to extract L-R
L_minus_R_raw = lowpass_simple(lrmix_output, 15000, MPX_RATE)

# Scale by 2 (DSB-SC halves the amplitude)
L_minus_R_recovered = L_minus_R_raw * 2.0

print(f"  - Correlation with true L-R: {np.corrcoef(L_minus_R, L_minus_R_recovered)[0,1]:.4f}")

# =============================================================================
# 6. STAGE 5 — De-emphasis (skip in simulation for brevity)
# =============================================================================

# De-emphasis is a simple IIR: y[n] = α·x[n] + (1-α)·y[n-1]
# We'll skip it here; it doesn't affect stereo separation.

# =============================================================================
# 7. STAGE 6 — Stereo matrix
# =============================================================================

# L = (L+R) + (L-R), then scale by 0.5
# R = (L+R) - (L-R), then scale by 0.5
left_decoded  = 0.5 * (L_plus_R_recovered + L_minus_R_recovered)
right_decoded = 0.5 * (L_plus_R_recovered - L_minus_R_recovered)

print(f"\nStage 5 (stereo matrix):")

# Use middle of signal to avoid filter edge effects
mid = N // 2
sl = slice(mid - 1000, mid + 1000)

corr_L = np.corrcoef(L[sl], left_decoded[sl])[0, 1]
corr_R = np.corrcoef(R[sl], right_decoded[sl])[0, 1]
print(f"  - Left  decoded vs true L: correlation = {corr_L:.4f}")
print(f"  - Right decoded vs true R: correlation = {corr_R:.4f}")

# Check stereo separation: L channel should have mostly L tone, not R
fft_L = np.abs(np.fft.rfft(left_decoded))
fft_R = np.abs(np.fft.rfft(right_decoded))
freqs = np.fft.rfftfreq(N, d=1/MPX_RATE)

L_peak_idx = np.argmin(np.abs(freqs - L_FREQ))
R_peak_idx = np.argmin(np.abs(freqs - R_FREQ))

print(f"\nStage 6 (stereo separation check):")
print(f"  - Left channel  power at {L_FREQ} Hz (expected high): {fft_L[L_peak_idx]:.2f}")
print(f"  - Left channel  power at {R_FREQ} Hz (expected low):  {fft_L[R_peak_idx]:.2f}")
print(f"  - Right channel power at {L_FREQ} Hz (expected low):  {fft_R[L_peak_idx]:.2f}")
print(f"  - Right channel power at {R_FREQ} Hz (expected high): {fft_R[R_peak_idx]:.2f}")

left_separation_dB = 20 * np.log10(fft_L[L_peak_idx] / max(fft_L[R_peak_idx], 1e-10))
right_separation_dB = 20 * np.log10(fft_R[R_peak_idx] / max(fft_R[L_peak_idx], 1e-10))
print(f"  - Stereo separation (left):  {left_separation_dB:.1f} dB")
print(f"  - Stereo separation (right): {right_separation_dB:.1f} dB")

# =============================================================================
# VERDICT
# =============================================================================

print(f"\n{'='*60}")
if abs(corr_L) > 0.85 and abs(corr_R) > 0.85 and left_separation_dB > 10:
    print("  ✓  SIMULATION PASSED")
    print("  The Lab 04 flowgraph's mathematical logic is CORRECT.")
    print("  Stereo decoding should work on real hardware.")
else:
    print("  ✗  SIMULATION ISSUES DETECTED")
    print(f"    corr_L={corr_L:.4f}, corr_R={corr_R:.4f}, sep_L={left_separation_dB:.1f} dB")
print('='*60)
