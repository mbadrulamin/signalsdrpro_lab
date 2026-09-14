# 📺 Lab 11 — Digital Television Receiver: Scan, Tune, Watch

> **Time:** 3 hours
> **Difficulty:** Expert
> **Theory needed:** **[Fund. 11 OFDM](../../01_fundamentals/11_ofdm_and_broadcast_systems.md)** · **[Fund. 12 Video Over The Air](../../01_fundamentals/12_video_over_the_air.md)**
> **New blocks:** the eleven-stage gr-dtv DVB-T *receive* chain, OFDM Symbol Acquisition, Viterbi Decoder, Reed-Solomon Decoder
> **Files:** `lab11_tv_receiver.grc` (learn the chain) · `lab11_tv_station.py` (the full receiver)
> **Hardware:** one SignalSDR Pro. A transmitter — [Lab 12](../lab12_fullduplex_tv/) — or a real broadcast to point it at.

Lab 10 built a television **transmitter** and proved the waveform was correct by measuring it.
It never showed a picture. This lab closes that loop: a receiver that demodulates an 8 MHz
terrestrial channel all the way down to MPEG-2 transport stream and puts the video on screen.

---

## 🚦 Read this first: DVB-T, not DVB-T2

Lab 10 transmits **DVB-T2**. This lab receives **DVB-T**. That is not an oversight, and it is
worth understanding before you go looking for the block you think is missing.

`gr-dtv` ships a DVB-T2 *modulator* and no demodulator. Look at the block list:

```
dvbt2_cellinterleaver   dvbt2_framemapper    dvbt2_freqinterleaver
dvbt2_interleaver       dvbt2_miso           dvbt2_modulator
dvbt2_p1insertion       dvbt2_paprtr         dvbt2_pilotgenerator
```

Every one of them is transmit-side. There is no `dvbt2_demod`, no LDPC decoder, no P1
detector. **No open-source real-time DVB-T2 receiver exists in GNU Radio.** For DVB-T it ships
both directions, so DVB-T is what can actually produce a picture.

| Standard | Transmit | Receive | Where it lives |
|---|---|---|---|
| **DVB-T2** | ✅ `gr-dtv` | ❌ nothing | Lab 10 — decode it with a real TV or USB tuner |
| **DVB-T** | ✅ `gr-dtv` | ✅ `gr-dtv` | **This lab** — decode it in software, picture on screen |

Nothing in the theory is lost. DVB-T2 is DVB-T plus LDPC instead of convolutional coding,
rotated constellations, and the P1 preamble. Everything about OFDM, pilots, the cyclic prefix,
interleaving and the transport stream is identical — and this lab's **scanner still detects and
measures real DVB-T2 broadcasts**, it just cannot decode their video.

> **Malaysia note.** MYTV broadcasts DVB-T2 on the UHF raster this lab scans. You can find,
> measure and characterise those muxes with `scan_tv_band.py` and with this lab's channel
> scanner. To *watch* them you need a TV or a USB DVB-T2 stick. See
> [Part 5 — Malaysia](../../05_reference/04_malaysia.md).

---

## 🎯 Goal

Build a receiver that does what a television does:

- **Scan** the band and produce a channel list
- **Tune** directly to a channel or a frequency, with no scan needed
- **Show signal quality** — level, MER, constellation, spectrum, lock state
- **Show the picture**

And, unlike a television, explain every number it displays.

> **Verified on real hardware, with a picture.** Transport stream through the modulator and back
> out of the demodulator: **0 mismatches in 4,201,236 bytes**. Over the air, full duplex, 40
> seconds of a real 1080p video: **79,357,996 bytes recovered byte-identical — 0 mismatches, 0
> continuity errors, 0 sync errors** — decoded to 975 video frames and 39.45 s of audio, with
> the service name read out of the SDT. See [Verification](#-verification).

---

## 📖 The chain, stage by stage

The receiver is the transmitter reversed, plus two blocks at the front that have no transmit
counterpart. Each stage undoes exactly one thing.

```
   RF  →  OFDM Symbol Acquisition   find the symbol boundary, correct frequency
       →  FFT                       back to the frequency domain
       →  Demod Reference Signals   equalise using pilots, read TPS, strip pilots
       →  Demap                     constellation points → bits
       →  Symbol Deinterleaver      undo the across-carriers scatter
       →  Bit Deinterleaver         undo the within-symbol bit scatter
       →  Viterbi Decoder           undo the convolutional code
       →  Convolutional Deinterl.   undo the burst-spreading
       →  Reed-Solomon Decoder      correct up to 8 bad bytes per packet
       →  Energy Descramble         undo the PRBS, restore sync bytes
   →  MPEG-2 transport stream  →  ffplay  →  picture
```

### The two blocks with no transmit twin

**OFDM Symbol Acquisition** finds where each symbol starts. It correlates the stream against
itself delayed by the FFT length: because the cyclic prefix is a copy of the symbol's tail,
that correlation peaks once per symbol. The phase of the peak also gives the fractional
frequency offset, which it corrects.

**The FFT** returns the signal to the frequency domain, where the pilots live. `shift=True`
puts DC in the middle, which is what the pilot demodulator expects.

### The stage that does the real work

**Demod Reference Signals** is where a DVB-T receiver is won or lost. The transmitter salts
known symbols across the channel — *scattered pilots* that move every symbol and *continual
pilots* that do not — plus TPS carriers announcing the mode. The receiver measures what those
known symbols came out as, and divides every data carrier by the local channel estimate.

This is the whole payoff of the cyclic prefix. Because the guard interval turns the channel's
linear convolution into a *circular* one, multipath becomes a single complex multiply per
carrier — so undoing it is a single complex divide per carrier. No adaptive equaliser, no
training sequence, no convergence time. That is why OFDM won.

---

## 🖥️ Two ways to run it

### 1. `lab11_tv_receiver.grc` — see the chain

Open it in GNU Radio Companion. Every block carries a `comment` explaining its job. Channel and
gain are sliders; spectrum, waterfall, constellation, MER and level are on screen; the decoded
stream is recorded and played.

Use this one to **understand** the receiver.

### 2. `lab11_tv_station.py` — use the receiver

```bash
./lab11_tv_station.py                 # tune ch 21, show quality and picture
./lab11_tv_station.py --scan-on-start # scan the band first
./lab11_tv_station.py --no-video      # measure only, no ffplay
./lab11_tv_station.py --channel 31 --gain 40
```

| What you asked for | Where it is |
|---|---|
| **Change channel** | UHF channel spin box, or double-click a row in the channel list |
| **Seek directly, no scan** | Type a frequency in MHz and press Tune. A scan is a convenience, never a prerequisite |
| **List of available channels** | The table — channel, MHz, level, shoulder, standard, detail |
| **Scan available channels** | *Scan band*. About **39 s** for channels 21–48 |
| **Signal quality** | Lock state, level in dBFS, MER in dB with a bar, continuity-error rate, live spectrum and constellation |
| **Real-time TV programme** | ffplay window, fed straight from the decoded transport stream |

---

## 📡 What the scanner actually measures

Four independent measurements per channel, in the order they can veto each other.

| Measurement | What it answers | Empty UHF channel | Real DVB-T |
|---|---|---|---|
| **Spectral shoulder** | Is it band-limited at all? | 0–4 dB | **31 dB** |
| **Burst fraction** | Is it continuous, like broadcasting? | 0 % | 0 % |
| **P1 correlation** | Is it DVB-T2? | ~4× | — |
| **CP correlation** | Is it DVB-T, and in which mode? | ~2–4× | **24×** |

### Why the order matters — a false positive worth studying

Scanning the UHF band here, channel 22 scored **P1 13.9×** and **cyclic prefix 31.4×**. Both
are far over threshold. Both say "television". Both are wrong.

Channel 22 carries an **intermittent** signal: 4 ms bursts, 7.6 % duty cycle, energy sitting at
+2 to +5 MHz rather than centred. It is not a television station.

The reason it fools both detectors is the same reason for both: a correlator asked "does this
signal repeat at lag *L*?" sees the burst overlap itself at *whatever* lag you test, so it
fires at every lag. Correlation detectors are blind to burstiness by construction.

Two cheap tests fix it, and neither involves correlation:

- **Spectral shoulder** — an 8 MHz television signal sampled at 9.14 MHz leaves an empty skirt
  at the edges of the window. Noise and wideband bursts fill the window evenly. Real DVB-T
  measured 31 dB here; channel 22 measured **1.2 dB**.
- **Burst fraction** — broadcasting is continuous. Channel 22 spends 7.6 % of its time 6 dB
  above its own median.

`scan_tv_band.py --selftest` now *reproduces this false positive synthetically* — it builds a
pulsed signal, shows it scoring 27.7× on the cyclic-prefix test, and asserts that the
classifier still refuses to call it television.

> **The general lesson, which is the same one Lab 08 taught in reverse.** There, an FFT said
> "no RDS" and the CRC said "287 valid groups" — trust the decoder. Here two correlators say
> "television" and the spectrum says "no" — trust the measurement that can be wrong in only one
> direction. A detector that can only be fooled *into* firing needs a veto that can only be
> fooled into staying silent.

### What was in the band here

Nothing. Channels 21–48 scanned with the FM whip from the earlier labs: **no DVB-T2, no DVB-T**,
one bursty non-television carrier on ch22, and a noise floor that rises 14 dB from 474 MHz to
618 MHz — which is the antenna's response, not the band's contents.

That absence is not proof the band is empty. It is proof that *this antenna* cannot hear it.
A quarter-wave for 474 MHz is 158 mm; the FM whip is cut for 100 MHz. See
[Part 5 — Antennas](../../05_reference/03_antennas.md).

---

## 📊 Signal quality: MER, and the cliff

MER is the honest version of a television's "signal quality" bar:

$$\text{MER} = 10\log_{10}\frac{\sum |\text{ideal}|^2}{\sum |\text{received} - \text{ideal}|^2}$$

where *ideal* is the nearest legal constellation point. No knowledge of the transmitted data is
needed, which is exactly how a real receiver does it. Measured against a calibrated AWGN
channel, this implementation tracks true SNR to within **0.9 dB**.

**Watch MER, not the picture.** Measured on this chain, 8K 16QAM CR 2/3:

| SNR | MER | Decoded | Verdict |
|---|---|---|---|
| 24 dB | 23.1 dB | 0 byte errors | perfect |
| 18 dB | 17.1 dB | 0 byte errors | perfect |
| 14 dB | 13.4 dB | 0 byte errors | perfect |
| **13 dB** | **12.6 dB** | **0 byte errors** | **perfect** |
| **12 dB** | **11.9 dB** | 1,274 continuity errors | **broken** |
| 10 dB | 10.5 dB | 75 % of packets lost | gone |

**One decibel** separates a flawless picture from no picture. The published DVB-T figure for
16QAM CR 2/3 in a Gaussian channel is 13.5 dB C/N, so the implementation lands within a
decibel of the standard.

This is the defining behaviour of digital television, and why analogue viewers found the
switchover so strange. Analogue degraded: snow, then more snow. Digital does not degrade, it
*expires*. By the time you can see a problem, all your margin is already gone.

---

## 🔬 Verification

### The modulator and demodulator are exact

A transport stream pushed through `DvbtTx` and back through `DvbtRx`, no noise:

```
noiseless : 4,298,432 TS bytes  MER 128.5 dB  null 99.6 %  CC errors 0
            compared 4,201,236 bytes against the source:
            0 mismatches -> 100.000000 % exact
```

Run it yourself: `03_scripts/dvbt_chain.py --snr 24 18 13 12 10`

> **How that comparison is anchored matters.** The obvious way — find the received bytes
> somewhere in the source file — silently lies. 99.6 % of a television multiplex is null
> packets, all 0xFF, which match *anywhere*. Anchoring on them made a completely broken decode
> score 99.89 % correct. The comparison anchors on a PSI table packet instead, which is unique.

### Over the air, full duplex, in real time

One SignalSDR Pro transmitting on TX/RX and receiving on RX2 simultaneously, 474 MHz:

```
  MER              : 15.7 dB
  level            : -19.8 dBFS
  packets decoded  : 422,304  (expect ~427,807 in 40 s)
  sync errors      : 0
  continuity errors: 0  (rate 0.00e+00)
  service names    : SDR LAB TV
  byte comparison  : 79,357,996 bytes, 0 mismatches -> 100.000000 % exact
  VERDICT: PASS - clean
```

That was 40 seconds of real video — 1920×1080 H.264 at 15.1 Mbit/s with MP2 audio — recovered
**byte-identical**, then decoded into **975 video frames and 39.45 s of audio**. The service
name came out of the Service Description Table: the receiver read the channel's own name off
the air.

Run it yourself: `03_scripts/verify_tv_link.py` (see [Lab 12](../lab12_fullduplex_tv/) first —
it transmits).

### Real-time cost, measured

The Viterbi decoder sets the limit. Needed: **9.14 MSPS**.

| Mode | Bit rate | Decode speed | Margin |
|---|---|---|---|
| QPSK 1/2 GI 1/4 | 4.98 Mbit/s | 38.7 MSPS | 4.2× |
| QPSK 2/3 GI 1/32 | 8.04 Mbit/s | 29.1 MSPS | 3.2× |
| **16QAM 2/3 GI 1/32** | **16.09 Mbit/s** | **16.4 MSPS** | **1.8×** ← default |
| 64QAM 2/3 GI 1/32 | 24.13 Mbit/s | 11.2 MSPS | 1.2× — too tight |

*(Intel i7-10875H, 16 threads.)*

### The number that surprised me

**An unlocked receiver runs at 1.55 MSPS — six times slower than a locked one.**

With no signal present, `dvbt_ofdm_sym_acquisition` searches the full symbol for a correlation
peak on every symbol. Once locked it merely tracks. Pointed at an empty channel the receiver
cannot keep up with the radio at all, and the USRP overflows continuously.

That is mostly harmless — an empty channel has nothing to decode — but it has one sharp
consequence, in [Troubleshooting](#-troubleshooting) below.

---

## 🧰 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| **Nothing decodes, USRP prints `O` continuously** | Normal on an empty channel: unlocked acquisition runs at 1.55 MSPS and cannot drain the radio. | Confirm a signal is actually there — spectrum should show a flat 7.6 MHz slab with steep shoulders. |
| **Never locks even though the signal is visible** | Mode mismatch. All four of FFT size, constellation, code rate and guard interval must agree with the transmitter. | There is no error message for this — it just stays silent. Check all four. |
| **Locks with GI 1/32 but never with GI 1/4** | Real, and measured. The acquisition search window is the cyclic-prefix length; GI 1/4 is 2048 samples, 8× the work of GI 1/32, and the search cannot keep up. | Use GI 1/32 for real-time work. Record to a file and decode offline if you need a long guard. |
| **Transport stream flows, every packet starts 0x47, payload is garbage** | The **Symbol Deinterleaver is missing or set to Interleave**. | The energy descrambler writes 0x47 unconditionally, so sync bytes prove nothing. Check PIDs: a healthy multiplex is ~99.6 % PID 8191. |
| **Picture freezes, radio starts overflowing** | A File Sink pointed at a FIFO: when the player stalls, the write blocks and the scheduler stops draining the USRP. | Use the supplied `PipeSink`/`tv_out` block — bounded queue, drops rather than blocks. |
| **MER good, picture still breaks up** | Transport rate mismatch, not a radio problem. | The stream must be muxed at exactly the mode's bit rate. `make_video_ts.py` computes it; `--verify` checks it against the PCR. |
| **`ffplay: not found`** | ffmpeg not installed. | `sudo apt install ffmpeg`. Everything except the picture works without it. |
| **Level rises with gain but MER does not** | You are amplifying the noise floor along with the signal. | Stop raising gain. The limit is C/N, not level — see [Antennas](../../05_reference/03_antennas.md). |

---

## ❓ What was not tested

- **No real broadcast was ever decoded here.** The band is empty at this location with this
  antenna, so every decode in this lab came from our own transmitter (Lab 12). The receiver has
  never been proved against a third-party DVB-T station.
- **Nobody has sat and watched it.** The picture was verified by decoding frames out of the
  received stream, not by a person watching `ffplay` run.
- **DVB-T2 reception is impossible**, not untested — see the top of this page.
- **2K mode** decodes correctly in file loopback but was not run over the air.
- **Hierarchical modulation** (`alpha1/2/4`) is wired through the API but never exercised.
- **The scanner has never seen a real DVB-T2 broadcast.** Its P1 detector is verified against a
  synthetic P1 and against the DVB-T2 waveform Lab 10 generates, not against a broadcaster.

---

## ➡️ Next

**[Lab 12 — Full-Duplex Video Link](../lab12_fullduplex_tv/)** — transmit a real video file and
receive it back on the same radio at the same time, which is where this receiver gets something
to watch.
