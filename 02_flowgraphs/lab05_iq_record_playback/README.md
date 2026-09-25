# 💾 Lab 05 — Record and Play Back Radio

> **What you will build:** two flowgraphs. One **records** the radio signal to a file. The other
> **plays it back** as a radio — with no radio attached — and can tune to any station inside
> the recording.
> **What you will learn:** what is inside an IQ file, why a Throttle block is needed, how to
> measure signal level, and how software tunes with a **Frequency Xlating FIR Filter**.
> **Before this:** [Lab 04](../lab04_stereo_wbfm/README.md),
> [Fundamentals 05 — Sampling & Filters](../../01_fundamentals/05_sampling_and_filters.md),
> [Fundamentals 06 — Noise & SNR](../../01_fundamentals/06_noise_snr_and_gain.md).
> **Time:** about 1 hour. **Difficulty:** intermediate. **Needs the radio:** only to record.

---

## 🎯 Goal

Stop needing the radio.

In Labs 01–04 the radio had to be plugged in and receiving. That has two problems:

- It is slow to experiment: set up, tune, wait.
- It is **not repeatable.** The signal changes all the time. If the sound gets better after you
  change a block, you cannot tell if your change helped, or the station just got stronger.

In this lab you will:

1. **Record** the raw IQ samples from the radio into a file.
2. **Play** the file back through a receiver, with the radio unplugged.
3. **Tune inside the recording** — pick a different station from the *same* file, in software.

From Lab 06 on, you can develop everything using a recording. Professionals work this way.

---

## 1. What is inside an IQ file?

The recorder writes the samples exactly as they come from the radio. Each sample is two
numbers, I and Q ([Fundamentals 02](../../01_fundamentals/02_iq_sampling.md)), each stored as a
32-bit floating-point number (`float32`):

```
byte:    0        4        8        12       16      ...
        ┌────────┬────────┬────────┬────────┬────────┐
        │  I[0]  │  Q[0]  │  I[1]  │  Q[1]  │  I[2]  │ ...
        └────────┴────────┴────────┴────────┴────────┘
```

- **8 bytes per sample** (4 for I, 4 for Q). I comes first.
- **No header.** Nothing else is in the file. Just the numbers.

This simple format is good — every SDR tool can read it. But there is a trap:

> ⚠️ **The file does not record its own sample rate or frequency.** If you forget them, the
> recording is almost useless, and you cannot work them out from the samples. So **put them in
> the file name.** That is why the default name is `capture_100M0_2Msps_fc32.iq`:
> 100.0 MHz, 2 MSPS, format fc32 (complex float32).

### How big will the file be?

$$
\text{bytes} = \text{sample rate} \times 8 \times \text{seconds}
$$

| Sample rate | Per second | Per minute | Per hour |
|---|---|---|---|
| 250 kSPS | 2 MB | 120 MB | 7.2 GB |
| 1 MSPS | 8 MB | 480 MB | 28.8 GB |
| **2 MSPS** (this lab) | **16 MB** | **960 MB** | **57.6 GB** |
| 8 MSPS | 64 MB | 3.84 GB | 230 GB |

> ⚠️ **Check your free disk space first.** At 2 MSPS, a 100 GB disk is full in under two hours,
> and GNU Radio will not warn you.

### Making files half the size (`sc16`)

If you set the USRP Source's output type to `sc16`, each I and Q is a 16-bit whole number
instead of a 32-bit float: **4 bytes per sample** instead of 8. You lose nothing, because the
radio's ADC only has 12 bits anyway. The only cost: when you read the file, divide by 32768 to
get back to the −1…+1 range. This lab uses `fc32` because it is simpler. Use `sc16` for long
recordings.

---

## 2. The recorder

```bash
cd "02_flowgraphs/lab05_iq_record_playback"
gnuradio-companion lab05_iq_record.grc
```

```
   USRP Source (2 MSPS, complex)
        │
        ├──▶ Spectrum            "is the signal there?"
        ├──▶ Waterfall           "does it come and go?"
        │
        ├──▶ |x|² ──▶ Moving Average ──▶ 10·log10 ──▶ Number display
        │                                             "is the level right?"
        ▼
   Copy  (on only when Record = ON)
        ▼
   File Sink   /tmp/capture_100M0_2Msps_fc32.iq
```

### Controls

| Control | What it does |
|---|---|
| **Centre Frequency** | Where to tune (87.5–108 MHz) |
| **RF Gain** | Hardware gain (0–76 dB) |
| **Record** | **OFF** = watch only. **ON** = write to the file |

### The blocks

**USRP Source.** As before, plus `dev_args: "num_recv_frames=512"`. This gives the driver a
bigger buffer. When recording, a short USB hiccup loses data that you can never get back, so
extra buffer helps.

**Copy — the record switch.** This block passes samples through when it is **enabled**, and
passes nothing when it is **disabled**. Its `enabled` setting is `bool(recording)`, linked to
the **Record** button. So you can run the flowgraph, look at the spectrum, tune, set the gain —
and only *then* start recording. Without it, you would record everything, including the time
you spent adjusting.

**File Sink.** Writes the samples to the file. `unbuffered: False` means the computer collects
data and writes it in big pieces. This is much faster.

**The level meter.** Four blocks that measure how strong the signal is, in **dBFS** (decibels
compared with the ADC's maximum):

| Block | Does |
|---|---|
| Complex to Mag² | power of each sample: I² + Q² |
| Moving Average (length 100,000, scale 1/100,000) | average power over 0.05 s |
| Log10 (n = 10, k = 3.0103) | convert to decibels: 10·log₁₀(2 × power) |
| Number Sink | show it on screen |

> 💡 **Why k = 3.0103?** 0 dBFS is defined as a full-scale sine wave. Its average power is ½,
> not 1. So we multiply the power by 2 before taking the log, and 10·log₁₀(2) = 3.0103.
>
> ⚠️ **Why scale = 1/100,000?** The Moving Average block **adds up** the last N values. It
> only gives an *average* if you also divide by N. Forget the scale, and the meter reads 50 dB
> too high.

**What level to aim for:**

| Level | Meaning |
|---|---|
| above −3 dBFS | **clipping.** The recording is permanently damaged. Lower the gain |
| **−30 to −10 dBFS** | **good** |
| below −50 dBFS | too weak. You are wasting ADC resolution. Raise the gain |

### Step 1 — Record

1. Press **F5**.
2. Tune **Centre Frequency** so you see **several** FM stations on the spectrum. Around 100 MHz
   is usually busy. Put the centre **between** two stations, so there are stations on both
   sides.
3. Adjust **RF Gain** until the level display reads about **−20 dBFS**.
4. Switch **Record** to **ON**.
5. Wait **10 seconds**. Switch it back to **OFF**. Close the window.

Check the file:

```bash
ls -lh /tmp/capture_100M0_2Msps_fc32.iq
```

It should be about **160 MB** (10 s × 16 MB/s).

### Step 2 — Look at the file with Python

Before trusting a recording, look at the numbers:

```bash
python3 - <<'PY'
import numpy as np
x = np.fromfile('/tmp/capture_100M0_2Msps_fc32.iq', dtype=np.complex64)
fs = 2e6
print(f"samples      : {len(x):,}")
print(f"duration     : {len(x)/fs:.2f} s")
print(f"mean power   : {10*np.log10(2*np.mean(np.abs(x)**2)):.1f} dBFS")
print(f"peak         : {20*np.log10(np.max(np.abs(x))):.1f} dBFS")
print(f"DC offset    : {np.mean(x):.5f}")
clip = np.mean(np.abs(x) > 0.99)
print(f"clipped      : {clip*100:.4f} %  {'TOO HIGH' if clip > 1e-4 else 'OK'}")
PY
```

A good recording shows: mean power around **−20 dBFS**, peak below **−1 dBFS**, and almost
**0 %** clipped. A small DC offset is normal — it is the centre spike you have seen on every
spectrum.

---

## 3. The player

```bash
gnuradio-companion lab05_iq_playback.grc
```

```
   File Source (repeat = on)
        │
   Throttle (2 MSPS)              ← keeps it at real-time speed
        │
        ├──▶ Spectrum: the whole 2 MHz recording
        │
   Frequency Xlating FIR Filter   ← shift by −offset, filter to 100 kHz, keep 1 in 5
        │   2 MSPS → 400 kSPS
        ├──▶ Spectrum: just the chosen station
        │
   WBFM Receive (÷8)                400 kSPS → 50 kSPS
        │
   Volume ──▶ Audio Sink (50 kHz)
        └───▶ Audio waveform display
```

### Controls

| Control | What it does |
|---|---|
| **Offset from centre** | Which station to play, measured from the recording's centre (−900 to +900 kHz) |
| **Volume** | Loudness |

### Sample rates at each step

| Between | Rate | Why |
|---|---|---|
| File → Throttle | 2 MSPS | the rate it was recorded at |
| Throttle → Xlating filter | 2 MSPS | the whole ±1 MHz |
| Xlating filter → WBFM | 400 kSPS | 2,000,000 ÷ 5. More than the ~200 kHz an FM station needs |
| WBFM → Audio | 50 kSPS | 400,000 ÷ 8 |

Every step divides by a whole number. No resampler needed.

### The blocks

**File Source.** Reads the file. `repeat = True` means it starts again at the end, so the
10-second recording plays forever.

**Throttle — keeps real-time speed.** A file has no clock. Without a Throttle, GNU Radio would
read the file **as fast as the computer can** — hundreds of millions of samples per second.
One CPU core would run at 100 %, and the displays would freeze.

The Throttle holds the flow to 2 million samples per second, using the computer's clock.

> 💡 **The rule:** every flowgraph needs something that sets its speed. That is either real
> hardware (a radio or a sound card) or a Throttle. A flowgraph with no hardware at all **must**
> have a Throttle.
>
> This player has two speed-setters: the Throttle (the computer's clock) and the Audio Sink (the
> sound card's clock). These two clocks are never *exactly* equal, so once in a while you may
> see `aU` or `aO` in the terminal. That is harmless. If you remove the Audio Sink (for example
> to test without sound), the Throttle alone keeps real-time speed.

**Frequency Xlating FIR Filter — tuning in software.** The most important block in this lab.
"Xlating" is short for "translating", meaning shifting. It does three jobs in one:

1. **Shift** — moves the chosen station (`offset_freq`) to the centre (0 Hz).
2. **Filter** — keeps ±100 kHz around the new centre, removes the rest.
3. **Decimate** — keeps 1 sample in 5: 2 MSPS → 400 kSPS.

**Drag the Offset slider, and you retune the radio without touching any hardware.** The
recording is a frozen 2 MHz slice of the spectrum. You can visit any station inside it.

The filter's taps come from a **Low-Pass Filter Taps** variable: gain 1, sample rate 2 MHz,
cutoff 100 kHz, transition width 30 kHz, Hamming window. That gives **161 taps**. Check it
yourself:

```bash
python3 -c "
from gnuradio.filter import firdes
from gnuradio.fft import window
print(len(firdes.low_pass(1.0, 2e6, 100e3, 30e3, window.WIN_HAMMING, 6.76)), 'taps')"
```

[Fundamentals 05](../../01_fundamentals/05_sampling_and_filters.md) shows how to predict that
number.

<details>
<summary><b>Going deeper:</b> the xlating filter as one equation</summary>

$$
y[n] = \sum_k h[k]\;x[nM-k]\;e^{-j2\pi f_{\text{offset}}(nM-k)/f_s}
$$

where $h$ are the taps and $M = 5$ is the decimation. The block is fast because it only
calculates the outputs it keeps (every 5th), and it folds the frequency shift into the taps.
</details>

### Step 3 — Play it back with no radio

1. **Unplug the radio**, to prove the point.
2. Press **F5**. You should hear the station nearest the centre of your recording.
3. Drag **Offset from centre**. As you move through ±900 kHz, you land on the other stations in
   the recording. Same file, different station.

### Step 4 — The experiment that shows why recordings matter

Play the recording twice: once with the filter cutoff at 100 kHz, once at 50 kHz (change
`chan_taps`). Listen to the **same ten seconds** each time.

With a live radio you could never make this comparison fairly, because the signal would change
between the two tests. With a recording, the only thing that changed is your filter.

---

## 4. Test it without a recording

No radio yet? Make a test station and play it through the real player:

```bash
cd 03_scripts
python3 make_test_iq.py /tmp/capture_100M0_2Msps_fc32.iq --mono --seconds 10
```

Then open `lab05_iq_playback.grc` and press **F5**. You should hear a steady 1000 Hz + 1700 Hz
tone chord.

---

## 🔧 Troubleshooting

| Problem | Cause and fix |
|---|---|
| Playback sounds like a chipmunk, or a slow drone | The player's `samp_rate` does not match the recording. The file cannot tell you — check the file name |
| One CPU core at 100 %, audio stutters | The Throttle is missing, disabled, or set to the wrong rate |
| The file is 0 bytes | **Record** was never switched ON, or the folder is not writable (`/tmp` always is) |
| `O` printed while recording | The computer cannot save 16 MB/s fast enough. Record to an SSD, lower `samp_rate`, use `sc16`, close other programs |
| A big spike at exactly the centre | The radio's own leak (DC offset), not a station. This is why Lab 06 tunes beside the station |
| The spectrum looks mirrored (left and right swapped) | Something read the file as Q,I instead of I,Q. GNU Radio always writes I first |

---

## ✅ Summary

- An IQ file is just I, Q, I, Q… as `float32`. **No header** — put the rate and frequency in
  the file name.
- 2 MSPS fills **16 MB every second**. Check disk space.
- A flowgraph with no hardware **must** have a **Throttle**.
- The **Frequency Xlating FIR Filter** shifts, filters and decimates in one block. It is how
  software radios tune.
- **Recordings make tests repeatable.** Set the gain correctly before you record — it cannot be
  fixed afterwards.

## 🧠 Check yourself

1. You find an old file `capture.iq` with no other notes. What two numbers are you missing?
   <details><summary>Answer</summary>The sample rate and the centre frequency. The file
   does not contain them.</details>
2. How big is a 30-second recording at 2 MSPS in fc32 format?
   <details><summary>Answer</summary>2,000,000 × 8 × 30 = 480,000,000 bytes, about
   480 MB.</details>
3. What happens if you delete the Throttle and the Audio Sink from the player?
   <details><summary>Answer</summary>Nothing sets the speed, so the file is read as fast as
   possible and one CPU core runs at 100 %.</details>
4. You recorded at a gain that was too high, and the recording is clipped. Can you fix it by
   turning the volume down during playback?
   <details><summary>Answer</summary>No. The clipping happened in the ADC, before recording.
   It is permanent. Gain must be set correctly before recording.</details>
5. The xlating filter's output rate is 400 kSPS, but its cutoff is only 100 kHz. Why not a
   cutoff of 190 kHz?
   <details><summary>Answer</summary>The filter needs room to go from "pass" to "block" (the
   30 kHz transition). The limit after decimation is 200 kHz. A 190 kHz cutoff plus the
   transition would go past 200 kHz, and that part would alias. 100 kHz is also all an FM
   station needs.</details>

**Next:** [Lab 06 — One Radio, Many Modes →](../lab06_multimode_receiver/README.md)

---

## 📖 References

1. GNU Radio Wiki: [File Sink](https://wiki.gnuradio.org/index.php/File_Sink) ·
   [Frequency Xlating FIR Filter](https://wiki.gnuradio.org/index.php/Frequency_Xlating_FIR_Filter)
2. [SigMF](https://github.com/sigmf/SigMF) — a standard way to store the missing information
   (rate, frequency, time) in a small file next to the recording
3. [USRP B210 manual](https://files.ettus.com/manual/page_usrp_b200.html)
