# 💾 Lab 05 — IQ Recording & Offline Playback

> **Time:** 1 hour
> **Difficulty:** Intermediate
> **Theory needed:** [Fundamentals 05 — Sampling & Filters](../../01_fundamentals/05_sampling_and_filters.md), [Fundamentals 06 — Noise & SNR](../../01_fundamentals/06_noise_snr_and_gain.md)
> **New blocks:** File Sink, File Source, Throttle, Copy, Frequency Xlating FIR Filter, Moving Average, Log10, Number Sink, Note
> **Flowgraphs:** two — `lab05_iq_record.grc` and `lab05_iq_playback.grc`

---

## 🎯 Goal

Stop needing the radio.

Labs 01–04 all required the SignalSDR Pro to be plugged in, tuned, and receiving. That makes
experimentation slow and **irreproducible** — the signal changes between runs, so you can never
tell whether your DSP change helped or the station just got stronger.

This lab breaks that dependency. You will:

1. **Capture** raw complex baseband from the SDR to a file.
2. **Replay** it through a full receiver chain with no hardware attached.
3. **Retune inside the recording** — pick a different station from the *same* file, purely in
   software, using a Frequency Xlating FIR Filter.

Everything from Lab 06 onward can be developed against a recording. This is how professional
SDR work is actually done.

---

## 📖 Background: What Is in an IQ File?

A `.iq` file written by `blocks_file_sink` with `type: complex` is the simplest possible
format:

```
byte offset:  0        4        8        12       16      ...
             ┌────────┬────────┬────────┬────────┬────────┐
             │  I[0]  │  Q[0]  │  I[1]  │  Q[1]  │  I[2]  │ ...
             └────────┴────────┴────────┴────────┴────────┘
              float32   float32  float32  float32
```

Interleaved little-endian `float32`, I first. **8 bytes per sample.** No header, no magic
number, no metadata. That simplicity is a virtue (every tool reads it) and a trap:

> ⚠️ **The file does not know its own sample rate or centre frequency.** If you lose those two
> numbers, the recording is worthless — you cannot recover them from the samples. **Encode them
> in the filename.** That is why the default path in both flowgraphs is
> `capture_100M0_2Msps_fc32.iq`.

### File size arithmetic

$$
\text{bytes} = f_s \times 8 \times t_{\text{seconds}}
$$

| Sample rate | Per second | Per minute | Per hour |
|---|---|---|---|
| 250 kSPS | 2.0 MB | 120 MB | 7.2 GB |
| 1 MSPS | 8.0 MB | 480 MB | 28.8 GB |
| **2 MSPS** | **16.0 MB** | **960 MB** | **57.6 GB** |
| 8 MSPS | 64.0 MB | 3.84 GB | 230 GB |

**Check your free disk space before you press Execute.** A 2 MSPS capture fills a 100 GB disk
in under two hours, and GNU Radio will not warn you.

### Halving the size with `sc16`

Setting `type: sc16` on the USRP Source gives interleaved `int16` — 4 bytes per sample instead
of 8. You lose nothing in practice: the AD9361's ADC is 12-bit, so 16-bit integers already
carry more precision than the hardware produces. The cost is that you must scale by
$1/32768$ when reading the file back. This lab uses `fc32` for clarity; use `sc16` for long
captures.

---

## 📐 Architecture

### Flowgraph A — the recorder

```
   ┌──────────────┐
   │ USRP Source  │  fc32, 2 MSPS
   └──────┬───────┘
          │
          ├──────────────▶ Frequency Sink   ← "is the signal there?"
          ├──────────────▶ Waterfall Sink   ← "is it bursty?"
          │
          ├──▶ Complex→Mag² ──▶ Moving Avg ──▶ Log10 ──▶ Number Sink
          │                                             ← "am I clipping?"
          ▼
   ┌──────────────┐
   │ Copy         │  enabled = bool(recording)   ← the arm/disarm switch
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ File Sink    │  /tmp/capture_100M0_2Msps_fc32.iq
   └──────────────┘
```

### Flowgraph B — the player

```
   ┌──────────────┐
   │ File Source  │  repeat = True
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │ Throttle     │  2 MSPS   ← MANDATORY: nothing else paces the graph
   └──────┬───────┘
          │
          ├──────────────▶ Frequency Sink (full 2 MHz span)
          ▼
   ┌───────────────────────────┐
   │ Frequency Xlating FIR     │  mix by -offset, LPF 100 kHz, decim 5
   │ Filter (ccf)              │  2 MSPS → 400 kSPS
   └──────┬────────────────────┘
          │
          ├──────────────▶ Frequency Sink (selected channel)
          ▼
   ┌──────────────┐
   │ WBFM Receive │  quad_rate 400k, audio_decim 8 → 50 kSPS
   └──────┬───────┘
          ▼
   ┌──────────────┐      ┌────────────┐
   │ Multiply     │─────▶│ Audio Sink │ 50 kHz
   │ Const (vol)  │──┐   └────────────┘
   └──────────────┘  └──▶ Time Sink
```

### Rate chain

| Wire | Rate | Type | Why |
|---|---|---|---|
| File → Throttle | 2 MSPS | complex | Matches the recording |
| Throttle → Xlating | 2 MSPS | complex | ±1 MHz of spectrum |
| Xlating → WBFM | 400 kSPS | complex | $2\text{M}/5$; > 200 kHz Carson bandwidth |
| WBFM → Audio | 50 kSPS | float | $400\text{k}/8$; a rate every sound card supports |

Every division is exact. This is the Fundamentals 05 discipline in practice.

---

## 📋 Block-by-Block

### Recorder

#### `usrp_source` — UHD: USRP Source
`dev_args: "num_recv_frames=512"` enlarges the driver's receive ring buffer. Recording is one
of the few situations where a USB hiccup costs you data you can never get back, so give the
driver room. If you still see `O` characters in the terminal, the host cannot keep up — lower
`samp_rate` or write to a faster disk (an SSD, or a tmpfs, not a USB stick).

#### `record_gate` — Copy
A one-line block that does something surprisingly useful. `blocks.copy` with
`enabled = False` **consumes its input and produces nothing**, so the File Sink downstream
sees no samples and writes no bytes.

```python
self.record_gate.set_enabled(bool(self.recording))
```

Because `recording` is a QT GUI Chooser, you get a live **arm/disarm radio button**: run the
flowgraph, watch the spectrum, tune, set the gain, and only *then* start writing. Without this
you would be recording garbage while you fiddle with the tuning slider.

#### `file_sink` — File Sink
`unbuffered: False` is correct here — buffered writes are far faster, and the OS flushes on
close. Set `unbuffered: True` only if you intend to kill the process with `SIGKILL` and still
want the data.

#### The level meter chain
```
Complex→Mag²  →  Moving Average  →  Log10  →  Number Sink
   |x|²          mean over 100k     10·log₁₀(2P)
```

The `Log10` block computes $n \log_{10}(x) + k$. With `n = 10` and `k = 3.0103`:

$$
10\log_{10}(\bar P) + 10\log_{10}(2) = 10\log_{10}(2\bar P) = P_{\text{dBFS}}
$$

which is the dBFS definition from [Fundamentals 06](../../01_fundamentals/06_noise_snr_and_gain.md).
The factor of two is there because 0 dBFS is defined as a full-scale *sine*, whose mean power
is $\frac{1}{2}$, not 1.

**Target: −30 to −10 dBFS.** Above −3 dBFS you are clipping and the recording is permanently
damaged. Below −50 dBFS you are throwing away ADC bits.

> Note the `Moving Average` `scale` parameter is `1.0/100000` — the block sums, it does not
> average, unless you tell it the scale. Forget this and your meter reads +50 dB.

### Player

#### `throttle` — Throttle
**The single most important block in this flowgraph.** A File Source with no hardware
downstream will read the file as fast as the disk allows — hundreds of MSPS — and the flowgraph
will consume 100 % of a CPU core while the audio sink drowns.

The rule:

> **Every flowgraph needs exactly one rate-limiting element.** Hardware source, hardware sink,
> or a Throttle. Never zero. Never two.

Here we technically have two (Throttle and Audio Sink), which is tolerated because the audio
sink is downstream of a decimating chain and merely provides gentle back-pressure. If you
remove the Audio Sink for a headless test, the Throttle still holds the graph at real time.

#### `chan_filter` — Frequency Xlating FIR Filter
The star of this lab, and the block Lab 06 is built around. In one pass it:

$$
y[n] = \sum_k h[k]\;x[nM-k]\;e^{-j2\pi f_{\text{offset}}(nM-k)/f_s}
$$

1. **Mixes** the input down by `center_freq` (our `offset_freq` slider),
2. **Low-passes** with `taps`,
3. **Decimates** by `decim`.

The taps come from a `Low-pass Filter Taps` variable:

```
gain=1.0, samp_rate=2e6, cutoff=100e3, width=30e3, Hamming
```

By the tap-count equation from Fundamentals 05:

$$
N = \frac{53 \times 2{,}000{,}000}{22 \times 30{,}000} = 160.6 \rightarrow 161 \text{ taps}
$$

Verify it:

```bash
python3 -c "
from gnuradio.filter import firdes
from gnuradio.fft import window
print(len(firdes.low_pass(1.0, 2e6, 100e3, 30e3, window.WIN_HAMMING, 6.76)), 'taps')"
```

**Drag the `offset_freq` slider and you retune the receiver without touching the radio.** The
recording is a frozen 2 MHz slice of the spectrum, and you can visit any station inside it.

---

## 🧪 Running the Lab

### Step 1 — Record

```bash
cd 02_flowgraphs/lab05_iq_record_playback
gnuradio-companion lab05_iq_record.grc
```

1. Press **F5** (Execute).
2. Tune `freq` to a spot with several FM stations visible in the spectrum — around 100 MHz is
   usually busy. **Aim the centre between two stations** so the playback flowgraph has
   somewhere to tune to.
3. Adjust `gain` until the Wideband Level reads about **−20 dBFS**.
4. Flip **Record** to **ON**.
5. Wait **10 seconds**, then flip it back to **OFF** and close the window.

```bash
ls -lh /tmp/capture_100M0_2Msps_fc32.iq
# should be ~160 MB for 10 seconds at 2 MSPS
```

### Step 2 — Verify the file in NumPy

Before trusting any flowgraph, look at the data directly:

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
print(f"clipped      : {clip*100:.4f} %  {'⚠️ TOO HIGH' if clip > 1e-4 else 'OK'}")
PY
```

A healthy capture has mean power around −20 dBFS, peak below −1 dBFS, and essentially zero
clipped samples. A small DC offset is normal for a direct-conversion receiver like the AD9361
— it shows up as a spike at exactly 0 Hz in the playback spectrum. (The `Correct IQ` block
removes it if it bothers you.)

### Step 3 — Play it back, with no hardware

```bash
gnuradio-companion lab05_iq_playback.grc
```

**Unplug the SDR first** to prove the point. Press F5. You should hear the station that was at
the centre of your recording.

Now drag **Offset from centre**. As you sweep through ±900 kHz you will land on the other
stations in the capture — same file, different radio.

### Step 4 — The experiment that proves the point

Run the playback flowgraph twice with two different `cutoff_freq` values in `chan_taps` — say
100 kHz and 50 kHz — and listen to the *same ten seconds of audio* both times. With a live
radio you could never make that comparison honestly, because the signal would have changed.

That is what recordings are for.

---

## 🐛 Troubleshooting

### "The playback audio is a chipmunk / a drone"
`samp_rate` in the playback flowgraph does not match the recording. The file has no idea what
rate it was captured at; you must tell it. Check the filename.

### "One CPU core is pinned at 100 % and the audio stutters"
The Throttle is missing, disabled, or set to the wrong rate. Nothing else in the playback
flowgraph limits the rate.

### "The file is 0 bytes"
You never flipped **Record** to **ON**, or the path is not writable. `/tmp` always is.

### "`O` characters stream past in the terminal while recording"
USB or disk overflow — the host cannot absorb 16 MB/s. In order of effectiveness: record to an
SSD or tmpfs, lower `samp_rate`, switch the USRP Source to `sc16`, close other applications.

### "Recording sounds fine but the spectrum has a big spike at exactly the centre"
That is the LO leakage / DC offset of the direct-conversion front end, not a station. It is a
property of the hardware, and it is why you should never centre-tune *directly* on the signal
you care about — offset by a few hundred kHz and use the xlating filter to come back. This is
standard practice and Lab 06 does it by default.

### "Playback works but the spectrum looks mirrored"
You read the file as `float32` pairs in the wrong order somewhere, or a tool interpreted it as
`Q,I`. GNU Radio always writes `I,Q`.

---

## ❓ Questions to Ponder

1. **Why does the recording contain no metadata, when SigMF exists?**
   Because `blocks_file_sink` predates SigMF and writes bare samples. SigMF (`.sigmf-data` plus
   a `.sigmf-meta` JSON) fixes exactly this problem and is worth adopting for anything you keep.
   For a lab, the filename convention is enough.

2. **The xlating filter mixes, filters and decimates. Could you do those as three separate
   blocks?**
   Yes — Signal Source + Multiply, then Low Pass Filter with `decim`. It would produce identical
   output and cost several times more CPU, because the mixer would run at the full input rate
   instead of being folded into the taps.

3. **Why is the anti-alias filter's cutoff 100 kHz when the output rate is 400 kSPS?**
   Nyquist for the output is 200 kHz, so 100 kHz leaves a 100 kHz guard band — the transition
   region (30 kHz wide) finishes well before anything can fold. Setting the cutoff to 190 kHz
   would technically fit but would alias the transition skirt.

4. **You recorded at 40 dB gain. Can you "turn the gain down" in playback?**
   Only in the trivial sense of scaling the samples. If the front end was compressing at 40 dB,
   that distortion is baked in permanently. **Gain is a record-time decision.**

---

## 📚 Key Takeaways

- **An IQ file is just interleaved float32 I,Q.** No header. The filename is the metadata.
- **Throttle every flowgraph that has no hardware in it.** Exactly one rate limiter, always.
- **The Frequency Xlating FIR Filter is how software radios tune.** Mix, filter, decimate — one
  block, one pass, output rate.
- **Recordings make experiments repeatable.** You cannot do controlled DSP comparisons against
  a live signal.
- **Set gain before you record.** Everything downstream is software and reversible; the front
  end is not.

---

## 🚀 What's Next?

Lab 06 uses the frequency-translating filter you just met to build a **multimode receiver** —
AM, NBFM and WBFM, with a channel selector, S-meter and squelch. And because of this lab, you
can develop it entirely against a recording.

**Next:** [Lab 06 — Multimode Receiver →](../lab06_multimode_receiver/README.md)

---

## 📖 References

1. GNU Radio Wiki: [File Sink](https://wiki.gnuradio.org/index.php/File_Sink) · [Frequency Xlating FIR Filter](https://wiki.gnuradio.org/index.php/Frequency_Xlating_FIR_Filter)
2. [The SigMF specification](https://github.com/sigmf/SigMF) — metadata done properly
3. Ettus Research: [USRP B210 Manual](https://files.ettus.com/manual/page_usrp_b200.html)
