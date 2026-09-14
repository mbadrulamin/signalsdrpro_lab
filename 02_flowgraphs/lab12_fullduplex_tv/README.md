# 📡📺 Lab 12 — Full-Duplex Video Link: Transmit and Receive at the Same Time

> **Time:** 4 hours
> **Difficulty:** Expert
> **Theory needed:** **[Fund. 11 OFDM](../../01_fundamentals/11_ofdm_and_broadcast_systems.md)** · **[Fund. 12 Video Over The Air](../../01_fundamentals/12_video_over_the_air.md)**
> **New blocks:** the full DVB-T transmit chain *and* receive chain in one flowgraph, USRP Sink and Source simultaneously
> **Files:** `lab12_fullduplex_tv.grc`
> **Hardware:** one SignalSDR Pro. **A cable and attenuator, or a Faraday cage.**
>
> ### 🚨 This lab transmits.

---

## 🚨 Before You Transmit Anything

DVB-T occupies **8 MHz of licensed broadcast spectrum**, and a DVB-T signal looks exactly like
a real broadcast — which is why interference from one is indistinguishable from a
broadcaster's own fault, and why regulators treat it harshly.

### The only acceptable setups

| | Setup | Notes |
|---|---|---|
| ✅ | **Cable: TX/RX → attenuator → RX2** | Best. No radiation at all, and it gives a *better* link than antennas |
| ✅ | **Faraday cage / shielded enclosure** | The whole radio inside |
| ✅ | **File only** — record with `verify_tv_link.py`, decode offline | Everything except the final demonstration |
| ❌ | "Low power should be fine" | It is not. A few mW at UHF carries for hundreds of metres |
| ❌ | "I scanned and the channel was empty" | **Empty to your antenna is not empty.** Scanning here found nothing at all across 470–694 MHz — because the antenna was cut for 100 MHz |

### The defaults are inert

`lab12_fullduplex_tv.grc` ships with **`tx_amplitude = 0.0` and `tx_gain = 0 dB`**. It radiates
nothing until you deliberately raise both. **Check what is on the TX/RX port before you touch
either slider** — the port is bidirectional and an antenna from an earlier lab is still
attached now.

Scan first, every time:

```bash
../../03_scripts/scan_tv_band.py --first 21 --last 48
```

---

## 🎯 Goal

Put a real video file on the air as digital television, and receive it back on the same radio,
at the same time, in one flowgraph — with the picture on screen.

```
  Bintang.mp4 → ffmpeg → MPEG-2 TS @ 16.086 Mbit/s
       → DVB-T modulator → TX/RX  ))))  RX2 → DVB-T demodulator
              → MPEG-2 TS → ffplay → picture
```

> **Verified on real hardware.** 25 seconds of continuous full duplex at 474 MHz:
> **267,104 packets decoded against 267,380 expected — 99.9 % of real time**, MER 17.7 dB,
> zero sync errors, continuity error rate 1.2 × 10⁻⁴, **99.9566 % byte-exact** against the
> transmitted file, and the service name read back off the air.

---

## 🔁 What "full duplex" actually buys, and what it hides

The B210 has independent transmit and receive chains. Channel A's **TX/RX** port transmits
while its **RX2** port receives, both at 9.142857 MSPS. Over USB 3.0 that is
2 × 9.14 M × 8 bytes = **146 MB/s**, sustained. (USB 2.0 cannot do this.)

**The catch, and it is a big one: there is no frequency offset.** Transmitter and receiver
share one reference oscillator, so the carrier the receiver hunts for is *exactly* where it
expects. A real receiver faces tens of kHz of offset from two independent crystals and must
search for it.

So this lab gives the synchroniser an unrealistically easy problem. That is fine — it isolates
everything else — but do not conclude from a working loopback that your receiver would lock to
a broadcaster. To make it honest, put a deliberate offset in: insert a
`Frequency Xlating FIR Filter` or a rotator between the modulator and the sink and give it a
few kHz. Watching where it stops locking is a better lesson than watching it work.

---

## 🎬 Making the video stream

```bash
sudo apt install ffmpeg          # the only external dependency in this repository

../../03_scripts/make_video_ts.py ~/Downloads/Bintang.mp4 /tmp/bintang.ts \
    --mode 16qam-2/3-1/32 --width 1280 --duration 300 --loop
```

Then point `ts_in` at `/tmp/bintang.ts` and run the flowgraph.

### For more than one pass of the file, use playout

`ts_in` pointing at a finished `.ts` with `repeat = True` is right for the byte-exact
verification below — you need something to compare against. It is **wrong for watching**. At
every lap the transport stream's PCR jumps backwards by the file's whole length (measured
−208.86 s in [Lab 10](../lab10_dvbt2_tx_rx/README.md#step-0--make-a-transport-stream-with-your-own-video-in-it)),
and a receiver's clock recovery never settles again. The picture stays perfect and goes
sluggish.

```bash
../../03_scripts/tv_playout.py ~/Downloads/Bintang.mp4 \
    --standard dvbt --mode 16qam-2/3-1/32 --fifo /tmp/tv.fifo
```

Then set `ts_in` to `/tmp/tv.fifo`. Playout loops the *video* inside ffmpeg, so the stream clock
counts upwards forever.

Without ffmpeg you can still exercise every part of the radio:

```bash
../../03_scripts/make_test_ts.py --out /tmp/lab.ts --seconds 10 --rate 16085561
```

That is a standards-valid multiplex with PAT/PMT/SDT/NIT and no video. A television will find
the service and list it by name; there is simply no picture.

### Why the bit rate is computed and not chosen

A DVB-T modulator is a **clock**, not a queue. Choose FFT size, constellation, code rate and
guard interval and the chain swallows transport bytes at one fixed rate forever:

$$T_u = N_{\text{FFT}} \cdot T, \qquad T_s = T_u\left(1 + \tfrac{1}{G}\right), \qquad
R = \frac{K_{\text{data}} \cdot b}{T_s} \cdot \frac{n}{d} \cdot \frac{188}{204}$$

with $T = 7/64$ µs for an 8 MHz channel. For 8K, 16QAM, CR 2/3, GI 1/32:

$$\frac{6048 \times 4}{924\,\mu s} \times \frac{2}{3} \times \frac{188}{204} = 16.086\ \text{Mbit/s}$$

Mux at a different rate and the picture drifts against its own clock until the receiver's
buffer gives up. `make_video_ts.py` computes the figure, passes it to ffmpeg as `-muxrate` so
null packets stuff the remainder exactly, and `--verify` checks the result by recovering the
rate from the PCR timestamps in the finished file.

`make_video_ts.py --list-modes` prints the whole table. It is derived from the equation above,
not copied, and it reproduces the published DVB-T figures exactly — 6.032, 16.086, 24.128,
31.668 Mbit/s.

---

## 📐 The link budget, and why the first attempt failed

The first over-the-air attempt decoded **nothing**. Working out why is the most useful hour in
this lab, because the answer is not a bug.

**Step 1 — is anything being transmitted?** A CW tone at the same settings rose **42 dB** above
the noise floor in its FFT bin. The transmitter works and an RF path exists.

**Step 2 — then why does DVB-T not arrive?** Because a tone and a television signal with the
same total power are not equally detectable. The tone puts everything into one 2.2 kHz bin.
DVB-T spreads it across 7.6 MHz — about 3,400 bins:

$$10\log_{10}(3400) \approx 35\ \text{dB}$$

Subtract that, and the 8.4 dB by which the test tone's total power exceeded the modulated
signal's, and 42 dB of tone becomes **−1.4 dB** of television. Measured in-band rise:
**+0.92 dB**. The prediction and the measurement agree.

**Step 3 — how much is needed?** 13 dB, measured in Lab 11's SNR sweep. The link was roughly
15 dB short.

**Step 4 — the fix.** Not more receive gain: raising RX gain lifts signal and noise together,
so C/N does not move. The answer was 19 dB more transmit gain, and then:

| TX gain | In-band rise | Shoulder | Result |
|---|---|---|---|
| 0 dB | 0.0 dB | 0.2 dB | nothing |
| 70 dB | 0.9 dB | 5.2 dB | still nothing |
| **89 dB** | **16.5 dB** | **21.3 dB** | **locks, decodes, picture** |

> **This is the whole reason to use a cable.** A short coax with a 20–30 dB attenuator gives a
> far better C/N than two antennas across a room, at a fraction of the transmit power, and
> radiates nothing at all. The setup that is safest is also the one that works best.

---

## 🔬 Verification

### Your own video, transmitted and received

40 seconds of `Bintang.mp4` — 1920×1080 H.264 at 15.1 Mbit/s with MP2 audio — through the
transmitter, over the air, and back through the demodulator:

```
$ 03_scripts/verify_tv_link.py --ts /tmp/bintang_dvbt.ts --seconds 40 \
      --channel 21 --tx-gain 89 --tx-amplitude 1.0 --rx-gain 20

  t=40.0s  level -19.8 dBFS  MER 15.7 dB  TS 79.39 MB  pkts 422,304  CC err 0

  packets decoded  : 422,304  (expect ~427,807 in 40 s)
  sync errors      : 0
  continuity errors: 0  (rate 0.00e+00)
  service names    : SDR LAB TV
  byte comparison  : 79,357,996 bytes, 0 mismatches -> 100.000000 % exact
  VERDICT: PASS - clean
```

**79 MB of video, byte-identical.** Then decoded:

```
$ ffmpeg -i /tmp/verify_rx.ts -map 0:v -f null -
  Stream #0:0[0x100]: Video: h264 (High), yuv420p, 1920x1080, 25 fps
  Stream #0:1[0x101]: Audio: mp2, 48000 Hz, stereo, 192 kb/s
  frame= 975      <- 39.4 s of video at 25 fps
```

975 video frames and 39.45 s of audio came out of the radio.

> **The control that makes this airtight.** The decoder still prints a few warnings, because the
> capture begins mid-GOP — a receiver tuning in has to wait for the next keyframe. To prove the
> radio was not responsible, the *identical byte range* was cut out of the source file and
> decoded alongside:
>
> ```
> $ cmp /tmp/rx_slice.ts /tmp/src_slice.ts
>   (no output - 78,995,720 bytes identical)
> warnings decoding the RECEIVED slice : 31
> warnings decoding the SOURCE  slice : 31
> ```
>
> Same bytes, same warnings. Every complaint the decoder makes is inherent to joining a stream
> in the middle, and none of them came from the channel.

### An earlier measurement, corrected

A first run reported 32 continuity errors and 2,400 byte mismatches at MER 17.7 dB, which was
blamed on phase noise. It was mostly **the test's own fault**: that run looped a 3-second
transport stream, and every wrap is a discontinuity in both the continuity counters and the PCR
— a fault the receiver reports honestly, in a stream that really is broken at the seam. Running
a 209-second file end to end gives **zero** of either.

If you loop a short stream, expect one burst of errors per lap and do not read it as a radio
problem.

The robust mode was measured too, and behaved in an instructive way:

| Mode | Bit rate | MER | Byte error rate | Locks live? |
|---|---|---|---|---|
| **16QAM 2/3 GI 1/32** | 16.09 Mbit/s | 15.7 dB | **0** (79 MB) | ✅ ← default |
| QPSK 1/2 GI 1/32 | 6.03 Mbit/s | 14.7 dB | 9.3 × 10⁻⁴ * | ✅ |
| QPSK 1/2 **GI 1/4** | 4.98 Mbit/s | — | — | ❌ **never locks** |

\* measured with a looping 3-second stream — see [the correction above](#an-earlier-measurement-corrected).

The last row is not a link problem — that mode decodes perfectly from a file. The acquisition
search window *is* the cyclic prefix, so GI 1/4 is 2048 samples of correlation per symbol
against GI 1/32's 256. Eight times the work, and real-time acquisition cannot keep up.

**The more robust mode was the one that failed.** Robustness against multipath and robustness
against your own CPU are different axes.

---

## 🧰 Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| **`RuntimeError: No devices found`** | A previous run still owns the radio. | Find it by PID and kill it. `pkill -f` is treacherous here — the pattern matches `pkill`'s own command line and kills the shell that launched it. |
| **Nothing decodes, RX level does not move with `tx_gain`** | No RF path, or the signal is spread below the noise floor. | Transmit a CW tone instead — a tone survives ~35 dB more path loss than an 8 MHz signal. If the tone appears and DVB-T does not, it is link budget, not wiring. |
| **`U` from `usrp_sink`** | Transmit chain starved. Usually the receive chain hogging the CPU while unlocked. | Make sure a signal is present; an unlocked receiver runs at 1.55 MSPS and starves everything else. |
| **`O` from `usrp_source`** | Receive chain not keeping up. | Expected while unlocked. If it persists after lock, drop to QPSK or 2K. |
| **Locks, then picture drifts or freezes** | Transport rate ≠ modulation rate. | `make_video_ts.py --verify` — it recovers the true rate from the PCR and compares. |
| **Constellation is a smeared blob at high gain** | Overload, not weakness. Over a short cable the usual failure is too much signal. | Lower `rx_gain` first, then `tx_gain`. |
| **Picture perfect, then suddenly gone** | You were on the cliff edge. | MER is the warning the picture cannot give you. Below ~15 dB you have no margin left. |

---

## ❓ What was not tested

- **No human has watched the picture live.** The stream was decoded frame by frame and stills
  were extracted from it, but `ffplay` was never left running in front of someone. Everything
  the decoder can check, checks out.
- **Two-radio operation** (one transmitting, one receiving, as Lab 10 describes) was not tried;
  everything here is one B210 talking to itself.
- **No deliberate frequency offset was introduced**, so the synchroniser has never been tested
  against the problem a real receiver faces. See [above](#-what-full-duplex-actually-buys-and-what-it-hides).
- **No real television was pointed at this transmitter.** For that, use Lab 10's DVB-T2
  transmitter — consumer sets do not decode DVB-T2-era muxes and DVB-T interchangeably.
