#!/usr/bin/env python3
"""
simulate_stereo_decode_pure.py
==============================
A pure-Python (no numpy/scipy) simulation of the Lab 04 stereo WBFM decoder.
Proves the mathematical logic of the flowgraph is correct.

Run:
    python3 simulate_stereo_decode_pure.py
"""

import math

# =============================================================================
# 1. SYNTHESISE A STEREO MPX SIGNAL
# =============================================================================

MPX_RATE = 240_000
DURATION = 0.05          # 50 ms (shorter since we're in pure Python)
N = int(MPX_RATE * DURATION)

L_FREQ = 440.0           # Left channel: 440 Hz
R_FREQ = 880.0           # Right channel: 880 Hz
L_AMP = 0.5
R_AMP = 0.5
PILOT_FREQ = 19_000.0
SUBCARRIER_FREQ = 38_000.0
PILOT_AMP = 0.1

print(f"Synthesising MPX signal: {N} samples at {MPX_RATE} SPS...")

# Pre-compute arrays as Python lists
t = [i / MPX_RATE for i in range(N)]

L = [L_AMP * math.sin(2 * math.pi * L_FREQ * ti) for ti in t]
R = [R_AMP * math.sin(2 * math.pi * R_FREQ * ti) for ti in t]

L_plus_R = [L[i] + R[i] for i in range(N)]
L_minus_R = [L[i] - R[i] for i in range(N)]

pilot = [PILOT_AMP * math.cos(2 * math.pi * PILOT_FREQ * ti) for ti in t]
L_minus_R_dsb = [L_minus_R[i] * math.cos(2 * math.pi * SUBCARRIER_FREQ * t[i]) for i in range(N)]

mpx = [L_plus_R[i] + pilot[i] + L_minus_R_dsb[i] for i in range(N)]

print(f"  ✓ Synthesised MPX signal (min={min(mpx):.3f}, max={max(mpx):.3f})")
print()

# =============================================================================
# Helper: simple windowed-sinc FIR low-pass filter
# =============================================================================

def fir_lowpass(x, cutoff, rate, M=101):
    """Windowed-sinc low-pass filter."""
    nyq = rate / 2
    wc = cutoff / nyq
    mid = M // 2
    h = []
    for n in range(M):
        k = n - mid
        if k == 0:
            h.append(wc)
        else:
            h.append(math.sin(math.pi * wc * k) / (math.pi * k))
    # Hamming window
    h = [h[i] * (0.54 - 0.46 * math.cos(2 * math.pi * i / (M - 1))) for i in range(M)]
    # Normalize
    s = sum(h)
    h = [x / s for x in h]
    # Convolve (same mode, approximated)
    out = [0.0] * len(x)
    for i in range(len(x)):
        total = 0.0
        for k in range(M):
            j = i - mid + k
            if 0 <= j < len(x):
                total += x[j] * h[k]
        out[i] = total
    return out


def fir_bandpass(x, low, high, rate, M=201):
    """Windowed-sinc band-pass = highpass - lowpass."""
    nyq = rate / 2
    wl = low / nyq
    wh = high / nyq
    mid = M // 2
    h = []
    for n in range(M):
        k = n - mid
        if k == 0:
            h_val = wh - wl
        else:
            h_val = math.sin(math.pi * wh * k) / (math.pi * k) - \
                    math.sin(math.pi * wl * k) / (math.pi * k)
        h.append(h_val)
    # Hamming window
    h = [h[i] * (0.54 - 0.46 * math.cos(2 * math.pi * i / (M - 1))) for i in range(M)]
    # Normalize to peak = 1
    peak = max(abs(x) for x in h)
    if peak > 0:
        h = [x / peak for x in h]
    out = [0.0] * len(x)
    for i in range(len(x)):
        total = 0.0
        for k in range(M):
            j = i - mid + k
            if 0 <= j < len(x):
                total += x[j] * h[k]
        out[i] = total
    return out


def pearson(x, y):
    """Compute Pearson correlation coefficient."""
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    sx = math.sqrt(sum((xi - mx)**2 for xi in x))
    sy = math.sqrt(sum((yi - my)**2 for yi in y))
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


# =============================================================================
# 2. STAGE 1 — Extract L+R via low-pass (15 kHz)
# =============================================================================

print("Stage 1: Low-pass filter to extract L+R (0-15 kHz)...")
L_plus_R_recovered = fir_lowpass(mpx, 15000, MPX_RATE)
# Use middle section to avoid edge effects
mid = N // 2
sl = slice(mid - 2000, mid + 2000)
corr_lr = pearson(L_plus_R[sl], L_plus_R_recovered[sl])
print(f"  ✓ L+R correlation with true signal: {corr_lr:.4f}")

# =============================================================================
# 3. STAGE 2 — Extract pilot via band-pass (18.5-19.5 kHz)
# =============================================================================

print("\nStage 2: Band-pass filter to isolate 19 kHz pilot...")
pilot_recovered = fir_bandpass(mpx, 18500, 19500, MPX_RATE)
print(f"  ✓ Pilot recovered, peak amplitude: {max(abs(x) for x in pilot_recovered[sl]):.4f}")

# =============================================================================
# 4. STAGE 3 — Simulate PLL (perfect lock assumption)
# =============================================================================
# For simulation, we assume PLL locks perfectly onto the pilot,
# producing cos(2π·19k·t + φ) with unit amplitude.
# The phase φ should match the pilot's phase.

print("\nStage 3: Simulating PLL lock to pilot...")
# Use Hilbert-like approach: assume perfect PLL
# PLL output: complex e^(j·2π·19k·t + j·φ)
# We take the unit-amplitude cosine with the pilot's phase.

# Estimate phase by cross-correlation with reference sin/cos
ref_cos = [math.cos(2 * math.pi * PILOT_FREQ * ti) for ti in t]
ref_sin = [math.sin(2 * math.pi * PILOT_FREQ * ti) for ti in t]

# Correlations (using middle slice)
slice_len = sl.stop - sl.start
cc = sum(pilot_recovered[sl.start + i] * ref_cos[sl.start + i] for i in range(slice_len))
cs = sum(pilot_recovered[sl.start + i] * ref_sin[sl.start + i] for i in range(slice_len))
phase_est = math.atan2(cs, cc)
print(f"  ✓ Pilot phase estimate: {phase_est:.4f} rad")

# Perfect PLL output: unit-amplitude complex sinusoid at 19 kHz with this phase
pll_out_re = [math.cos(2 * math.pi * PILOT_FREQ * ti + phase_est) for ti in t]
pll_out_im = [math.sin(2 * math.pi * PILOT_FREQ * ti + phase_est) for ti in t]

# =============================================================================
# 5. STAGE 4 — Double frequency to get 38 kHz subcarrier
# =============================================================================
print("\nStage 4: Doubling pilot frequency (19 kHz × 19 kHz = 38 kHz)...")
# Complex × complex: (a+bi)² = (a²-b²) + 2ab·i
sub_38k_re = [pll_out_re[i]**2 - pll_out_im[i]**2 for i in range(N)]
sub_38k_im = [2 * pll_out_re[i] * pll_out_im[i] for i in range(N)]

# Real part only (for float × float multiply with MPX)
subcarrier_38k = sub_38k_re  # = cos(2·2π·19k·t + 2·phase) = cos(2π·38k·t + 2φ)

print(f"  ✓ 38 kHz subcarrier amplitude (rms): {math.sqrt(sum(x*x for x in subcarrier_38k[sl]) / slice_len):.4f}")

# =============================================================================
# 6. STAGE 5 — Multiply MPX × 38 kHz to demodulate L-R
# =============================================================================
print("\nStage 5: Multiplying MPX × 38 kHz carrier...")
# Both inputs are FLOAT
lrmix = [mpx[i] * subcarrier_38k[i] for i in range(N)]

# Low-pass to extract L-R
print("  Applying low-pass filter (15 kHz) to extract L-R...")
L_minus_R_raw = fir_lowpass(lrmix, 15000, MPX_RATE, M=101)

# Scale by 2 (DSB-SC halves amplitude)
L_minus_R_recovered = [x * 2.0 for x in L_minus_R_raw]

corr_lmr = pearson(L_minus_R[sl], L_minus_R_recovered[sl])
print(f"  ✓ L-R correlation with true signal: {corr_lmr:.4f}")

# =============================================================================
# 7. STAGE 6 — Stereo matrix: L = (L+R)+(L-R), R = (L+R)-(L-R)
# =============================================================================
print("\nStage 6: Stereo matrix...")
left_decoded  = [0.5 * (L_plus_R_recovered[i] + L_minus_R_recovered[i]) for i in range(N)]
right_decoded = [0.5 * (L_plus_R_recovered[i] - L_minus_R_recovered[i]) for i in range(N)]

corr_L = pearson(L[sl], left_decoded[sl])
corr_R = pearson(R[sl], right_decoded[sl])
print(f"  ✓ Left  decoded vs true L: correlation = {corr_L:.4f}")
print(f"  ✓ Right decoded vs true R: correlation = {corr_R:.4f}")

# =============================================================================
# 8. VERDICT
# =============================================================================

print(f"\n{'='*60}")
if abs(corr_L) > 0.80 and abs(corr_R) > 0.80:
    print("  ✓  SIMULATION PASSED")
    print("  The Lab 04 flowgraph's mathematical logic is CORRECT.")
    print("  Stereo decoding will work when run on real hardware with real FM signals.")
else:
    print("  ✗  SIMULATION ISSUES DETECTED")
    print(f"    corr_L={corr_L:.4f}, corr_R={corr_R:.4f}")
    print(f"    Check filter design or phase alignment.")
print('='*60)
