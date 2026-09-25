# 📺 Lab 11 — Build a TV Receiver: Scan, Tune, Watch

> **What you will build:** a digital TV **receiver** in software — it scans the band, makes a
> channel list, tunes, shows signal quality, and puts the **picture on screen**.
> **What you will learn:** the eleven stages of a DVB-T receiver; how pilots undo echoes; how a
> band scanner decides "this is TV"; what **MER** is; and why digital TV fails over a one-decibel
> cliff.
> **Before this:** **[Fundamentals 11 — OFDM](../../01_fundamentals/11_ofdm_and_broadcast_systems.md)**
> and **[12 — Video Over the Air](../../01_fundamentals/12_video_over_the_air.md)**.
> **Time:** about 3 hours. **Difficulty:** expert.
> **Hardware:** one SignalSDR Pro, and something to receive: [Lab 12](../lab12_fullduplex_tv/README.md)'s
> transmitter, or a real DVB-T broadcast.

**Two ways to run it:**

| File | Use it to |
|---|---|
| `lab11_tv_receiver.grc` | **learn** the receive chain, block by block |
| `lab11_tv_station.py` | **use** the receiver: scan, channel list, quality meters, picture |

Lab 10 built a TV **transmitter** and proved its signal was correct by measuring it. It never
showed a picture itself. This lab closes the loop: it turns an 8 MHz TV channel back into the
transport stream, and plays the video.

---

## 🚦 First: this receives DVB-T, not DVB-T2

Lab 10 transmits **DVB-T2**. This lab receives **DVB-T** (the first generation). That is on
purpose.

GNU Radio's `gr-dtv` has a DVB-T2 **transmitter** but **no DVB-T2 receiver** — every DVB-T2 block
is transmit-side:

```
dvbt2_cellinterleaver   dvbt2_framemapper    dvbt2_freqinterleaver
dvbt2_interleaver       dvbt2_miso           dvbt2_modulator
dvbt2_p1insertion       dvbt2_paprtr         dvbt2_pilotgenerator
```

For DVB-T, it has **both** directions. So DVB-T is the one that can give you a picture in
software.

| Standard | Transmit | Receive | Where |
|---|---|---|---|
| **DVB-T2** | ✅ `gr-dtv` | ❌ nothing | Lab 10 — receive it with a real TV or a USB tuner |
| **DVB-T** | ✅ `gr-dtv` | ✅ `gr-dtv` | **this lab** — receive it in software, picture on screen |

You lose no theory. DVB-T2 is DVB-T with LDPC instead of convolutional coding, rotated
constellations and the P1 preamble. OFDM, pilots, the cyclic prefix, interleaving and the transport
stream all work the same way. And this lab's **scanner still finds and measures DVB-T2
broadcasts** — it just cannot decode their video.

> 🇲🇾 **In Malaysia,** MYTV broadcasts DVB-T2 in the UHF band this lab scans. You can find and
> measure those channels with the scanner and `scan_tv_band.py`. To **watch** them, use a TV or a
> USB DVB-T2 stick. See the [Malaysia reference](../../05_reference/04_malaysia.md).

---

## 🎯 Goal

Build a receiver that does what a TV does:

- **scan** the band and make a channel list,
- **tune** straight to a channel or a frequency — no scan needed,
- **show signal quality** — level, MER, constellation, spectrum, lock,
- **show the picture**,

and, unlike a TV, **explain every number** it shows.

> ✅ **Tested on real hardware, with a picture.** Through the transmitter and back through the
> receiver: **0 wrong bytes in 4,201,236**. Over the air, full duplex, 40 seconds of real 1080p
> video: **79,357,996 bytes received exactly — 0 wrong, 0 missing packets** — decoded into 975
> video frames and 39.45 s of audio, with the channel name read from the signal. See
> [Verification](#-verification).

---

## 1. The receive chain, stage by stage

The receiver is the transmitter **backwards**, plus two stages at the front that the transmitter
does not need. Each stage undoes one thing:

```
   radio signal
       →  OFDM Symbol Acquisition   find where each symbol starts; fix the frequency
       →  FFT                       back to separate carriers
       →  Demod Reference Signals   use the pilots to undo echoes; read the mode (TPS); remove pilots
       →  Demap                     constellation points → bits
       →  Symbol Deinterleaver      undo the scatter across carriers
       →  Bit Deinterleaver         undo the scatter within each symbol
       →  Viterbi Decoder           undo the convolutional code (fix scattered bit errors)
       →  Convolutional Deinterl.   undo the burst-spreading
       →  Reed–Solomon Decoder      fix up to 8 bad bytes per packet
       →  Energy Descramble         undo the scrambling; put the 0x47 sync bytes back
   →  MPEG-2 transport stream  →  ffplay  →  picture
```

### The two stages with no transmitter twin

**OFDM Symbol Acquisition** finds where each symbol starts. It compares the signal with itself one
FFT-length later. The cyclic prefix is a copy of the symbol's end, so the comparison peaks once
per symbol (the method you built by hand in
[Lab 10, Step 3](../lab10_dvbt2_tx_rx/README.md#step-3--watch-the-ofdm-structure-live)). The angle
of that peak also gives the small frequency error, which it corrects.

**FFT** turns the signal back into separate carriers, where the pilots are. `shift=True` puts 0 Hz
in the middle, which the next block expects.

### The stage that does the real work

**Demod Reference Signals** is where a DVB-T receiver succeeds or fails. The transmitter scatters
**known** values across the channel: **scattered pilots** that move every symbol, **continual
pilots** that do not, and **TPS** carriers that announce the mode. The receiver measures what
those known values arrived as, and divides every data carrier by its local channel estimate.

This is the payoff of the cyclic prefix
([Fundamentals 11 §3](../../01_fundamentals/11_ofdm_and_broadcast_systems.md#part-3--the-cyclic-prefix-the-key-trick)):
echoes become one multiplication per carrier, so undoing them is **one division per carrier**. No
adaptive equaliser, no training, no waiting to converge. That is why OFDM won.

---

## 2. Two ways to run it

### A. `lab11_tv_receiver.grc` — learn the chain

Open it in GNU Radio Companion. Every block has a `comment` explaining its job. Channel and gain are
sliders. The spectrum, waterfall, constellation, MER and level are on screen, and the decoded stream
is recorded and played.

### B. `lab11_tv_station.py` — use the receiver

```bash
cd "02_flowgraphs/lab11_tv_receiver"
./lab11_tv_station.py                  # tune channel 21, show quality and picture
./lab11_tv_station.py --scan-on-start  # scan the band first
./lab11_tv_station.py --no-video       # measure only, no picture window
./lab11_tv_station.py --channel 31 --gain 40
```

Other options: `--first`/`--last` (scan range, default 21–48), `--mode` (default
`16qam-2/3-1/32`), `--fft` (`2k` or `8k`), `--antenna` (default `RX2`), `--ts-file` (also record
the stream).

| You want to… | Do this |
|---|---|
| **Change channel** | use the UHF channel box, or double-click a row in the channel list |
| **Tune straight to a frequency, no scan** | type the frequency in MHz and press **Tune**. A scan is only a convenience |
| **See the channel list** | the table: channel, MHz, level, shoulder, standard, details |
| **Scan the band** | press **Scan band** — about **39 s** for channels 21–48 |
| **See signal quality** | lock state, level (dBFS), MER (dB) with a bar, continuity-error rate, live spectrum and constellation |
| **Watch the programme** | the ffplay window, fed straight from the decoded stream |

---

## 3. What the scanner measures

Four independent tests for each channel, in the order they can overrule each other:

| Test | Question | Empty channel | Real DVB-T |
|---|---|---|---|
| **Spectral shoulder** | Is the signal cut off sharply at the channel edges? | 0–4 dB | **31 dB** |
| **Burst fraction** | Is it on all the time, like broadcasting? | 0 % | 0 % |
| **P1 correlation** | Is it DVB-T2? | about 4× | — |
| **CP correlation** | Is it DVB-T, and in which mode? | about 2–4× | **24×** |

### Why the order matters — a false alarm worth studying

Scanning the UHF band here, channel 22 scored **P1 13.9×** and **cyclic prefix 31.4×**. Both far
above the threshold. Both say "TV". **Both wrong.**

Channel 22 carries a signal that switches **on and off**: 4 ms bursts, on 7.6 % of the time, off
to one side of the channel. It is not a TV station.

Why are both detectors fooled? Both ask: "does this signal repeat after a delay?" A short burst
overlaps itself at **any** delay you test — so it "matches" every time. **Correlation detectors
cannot see burstiness.**

Two simple tests fix it, and neither uses correlation:

- **Spectral shoulder** — an 8 MHz TV signal, sampled at 9.14 MHz, leaves empty edges in the
  display. Noise and bursts fill the whole window. Real DVB-T: **31 dB**. Channel 22: **1.2 dB**.
- **Burst fraction** — broadcasting never stops. Channel 22 spends 7.6 % of its time 6 dB above
  its own middle level.

`scan_tv_band.py --selftest` now **creates this false alarm on purpose** — a pulsed test signal
that scores 27.7× on the cyclic-prefix test — and checks the scanner still refuses to call it TV.

> **Lesson:** this is Lab 08's lesson the other way round. There, the spectrum said "no RDS" and the
> CRC found 287 good groups — trust the decoder. Here, two correlators say "TV" and the spectrum
> says "no". **Know how each test can be fooled, and pair it with one that is fooled the opposite
> way.**

### What was actually in the band here

Nothing. Channels 21–48, scanned with the FM whip from the earlier labs: **no DVB-T2, no DVB-T**,
one on-off signal on channel 22, and a noise floor that rises 14 dB from 474 to 618 MHz — the
antenna's behaviour, not the band's.

That does **not** prove the band is empty. It proves **this antenna** cannot hear it. A
quarter-wave antenna for 474 MHz is **158 mm**; the FM whip is cut for 100 MHz. See the
[Antennas reference](../../05_reference/03_antennas.md).

---

## 4. Signal quality: MER, and the cliff

**MER** (modulation error ratio) is the honest version of a TV's "signal quality" bar. It compares
each received point with the nearest correct constellation point:

$$\text{MER} = 10\log_{10}\frac{\sum |\text{ideal}|^2}{\sum |\text{received} - \text{ideal}|^2}$$

It needs **no knowledge of the data sent** — which is how real receivers do it. Measured against a
calibrated noise channel, this implementation follows the true SNR to within **0.9 dB**.

**Watch MER, not the picture.** Measured on this chain (8K, 16QAM, code rate 2/3):

| SNR | MER | Decoded | Verdict |
|---|---|---|---|
| 24 dB | 23.1 dB | 0 byte errors | perfect |
| 18 dB | 17.1 dB | 0 byte errors | perfect |
| 14 dB | 13.4 dB | 0 byte errors | perfect |
| **13 dB** | **12.6 dB** | **0 byte errors** | **perfect** |
| **12 dB** | **11.9 dB** | 1,274 continuity errors | **broken** |
| 10 dB | 10.5 dB | 75 % of packets lost | gone |

**One decibel** separates a perfect picture from no picture. The published DVB-T figure for this
mode is 13.5 dB, so the implementation agrees with the standard to within a decibel.

Analog TV got gradually worse: snow, then more snow. Digital TV does not get worse — it **stops**.
By the time you can see a problem, all your margin is gone.

---

## 🔬 Verification

### The transmitter and receiver are exact

A transport stream sent through `DvbtTx` and back through `DvbtRx`, with no noise:

```
noiseless : 4,298,432 TS bytes  MER 128.5 dB  null 99.6 %  CC errors 0
            compared 4,201,236 bytes against the source:
            0 mismatches -> 100.000000 % exact
```

Run it yourself: `03_scripts/dvbt_chain.py --snr 24 18 13 12 10`

> ⚠️ **How you compare matters.** The obvious way — search for the received bytes anywhere in the
> source file — can lie. This test stream is 99.6 % null packets (all 0xFF), which match
> **anywhere**. Comparing that way, a completely broken decode scored 99.89 % "correct". The
> comparison must anchor on a unique packet, such as a table packet.

### Over the air, full duplex, in real time

One SignalSDR Pro, transmitting on `TX/RX` and receiving on `RX2` at the same time, at 474 MHz:

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

40 seconds of real video — 1920×1080 H.264 at 15.1 Mbit/s with MP2 audio — received **exactly**,
then decoded into **975 video frames and 39.45 s of audio**. The receiver read the channel's own
name, `SDR LAB TV`, from the Service Description Table.

Run it yourself: `03_scripts/verify_tv_link.py` — but read [Lab 12](../lab12_fullduplex_tv/README.md)
first: **it transmits**.

### How fast it runs

The Viterbi decoder sets the limit. It must keep up with **9.14 million samples per second**:

| Mode | Bit rate | Decode speed | Spare |
|---|---|---|---|
| QPSK 1/2, GI 1/4 | 4.98 Mbit/s | 38.7 MSPS | 4.2× |
| QPSK 2/3, GI 1/32 | 8.04 Mbit/s | 29.1 MSPS | 3.2× |
| **16QAM 2/3, GI 1/32** | **16.09 Mbit/s** | **16.4 MSPS** | **1.8×** ← default |
| 64QAM 2/3, GI 1/32 | 24.13 Mbit/s | 11.2 MSPS | 1.2× — too tight |

*(Intel i7-10875H, 16 threads.)*

### The surprising number

**A receiver that has not locked runs at only 1.55 MSPS — about ten times slower than when
locked.**

With no signal, the acquisition block searches every position of every symbol for a peak. Once
locked, it only follows. So on an empty channel the receiver cannot keep up with the radio, and
the radio overflows (`O`) constantly. Usually harmless — there is nothing to decode — but see the
first row of Troubleshooting.

---

## 🔧 Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| **Nothing decodes; `O` printed constantly** | Normal on an empty channel: searching runs at 1.55 MSPS and cannot keep up | Check a signal is really there: the spectrum should show a flat 7.6 MHz block with steep edges |
| **Never locks, though the signal is visible** | Mode mismatch: FFT size, constellation, code rate and guard interval must **all four** match the transmitter | There is no error message — it just stays silent. Check all four |
| **Locks at GI 1/32, never at GI 1/4** | Real, and measured. The search covers the guard: GI 1/4 is 2048 samples, 8× the work of GI 1/32, and the CPU cannot keep up | Use GI 1/32 for real-time work. For a long guard, record to a file and decode afterwards |
| **Packets flow, all start with 0x47, but the contents are rubbish** | The **Symbol Deinterleaver** is missing, or set to Interleave | Sync bytes prove nothing — the descrambler writes 0x47 every time. Check the PIDs: you should see PAT (0), PMT, SDT (17) and your video/audio PIDs, with correct continuity counters |
| **The picture freezes, then the radio overflows** | A File Sink writing into a FIFO: when the player stalls, the write waits, and nothing drains the radio | Use the supplied `tv_out` block: a limited queue that drops data instead of waiting |
| **MER is good, but the picture still breaks up** | The stream's rate does not match the mode — not a radio problem | The stream must be exactly the mode's rate. `make_video_ts.py` calculates it; `--verify` checks it |
| `ffplay: not found` | ffmpeg is not installed | `sudo apt install ffmpeg`. Everything except the picture works without it |
| **Level rises with gain, but MER does not** | You are amplifying noise along with the signal | Stop raising the gain. The limit is signal-to-noise, not level — improve the antenna |

---

## ❓ Not yet tested

- **No real broadcast has been decoded here.** There is no TV signal at this location with this
  antenna, so every decode came from our own transmitter (Lab 12).
- **Nobody has watched it live.** The picture was checked by decoding frames from the received
  stream, not by a person watching `ffplay`.
- **DVB-T2 reception is impossible here**, not just untested — see the top of this page.
- **2K mode** decodes correctly from a file, but was not tested over the air.
- **Hierarchical modulation** (`alpha1/2/4`) is wired in, but never tested.
- **The scanner has never seen a real DVB-T2 broadcast.** Its P1 detector is tested against a
  synthetic P1 and Lab 10's signal, not against a broadcaster.

---

## ✅ Summary

- GNU Radio can **receive DVB-T** fully in software; for DVB-T2 you need a TV or a USB tuner.
- The receiver is the transmitter backwards, plus **symbol acquisition** and the **FFT**.
- **Pilots + cyclic prefix** turn echo removal into one division per carrier.
- Pair detectors that are fooled in **different** ways; correlation cannot see bursts.
- **MER** falls smoothly; the picture fails suddenly. **Watch MER.**
- Searching is ten times more expensive than tracking.

## 🧠 Check yourself

1. Why does this lab receive DVB-T instead of DVB-T2?
   <details><summary>Answer</summary>GNU Radio has a DVB-T2 transmitter but no DVB-T2 receiver.
   It has both for DVB-T.</details>
2. What does Demod Reference Signals do?
   <details><summary>Answer</summary>It measures the known pilots, estimates what the channel did
   to each carrier, divides it out, reads the mode from the TPS carriers, and removes the
   pilots.</details>
3. Channel 22 scored high on both correlation tests, but was not TV. How was it caught?
   <details><summary>Answer</summary>By tests that do not use correlation: the spectral shoulder
   (1.2 dB, not 31) and the burst fraction (7.6 % on-off, not continuous).</details>
4. MER is 12.6 dB, and the picture is perfect. Should you relax?
   <details><summary>Answer</summary>No. You are right at the cliff: 1 dB less and the picture
   is gone.</details>
5. Why does the receiver lock at GI 1/32 but not at GI 1/4?
   <details><summary>Answer</summary>The timing search compares across the guard; GI 1/4 is 8×
   more work, and the CPU cannot keep up in real time.</details>

**Next:** [Lab 12 — Send and Receive Video at Once →](../lab12_fullduplex_tv/README.md), where
this receiver gets something to watch.
