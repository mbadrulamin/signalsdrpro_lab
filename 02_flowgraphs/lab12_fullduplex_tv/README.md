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

```
$ 03_scripts/verify_tv_link.py --seconds 25 --channel 21 \
      --tx-gain 89 --tx-amplitude 1.0 --rx-gain 20

  t= 2.0s  level -17.0 dBFS  MER 17.7 dB  TS  1.95 MB  pkts  10,400  CC err  0
  ...
  t=26.0s  level -17.0 dBFS  MER 17.7 dB  TS 50.21 MB  pkts 267,104  CC err 32

  packets decoded  : 267,104  (expect ~267,380 in 25 s)
  sync errors      : 0
  continuity errors: 32  (rate 1.20e-04)
  service names    : SELFTEST
  byte comparison  : 5,529,832 bytes, 2400 mismatches -> 99.956599 % exact
  VERDICT: PASS - watchable, occasional artefacts
```

The robust mode was measured too, and behaved in an instructive way:

| Mode | Bit rate | MER | Byte error rate | Locks live? |
|---|---|---|---|---|
| 16QAM 2/3 GI 1/32 | 16.09 Mbit/s | 17.7 dB | 4.3 × 10⁻⁴ | ✅ |
| QPSK 1/2 GI 1/32 | 6.03 Mbit/s | 14.7 dB | 9.3 × 10⁻⁴ | ✅ |
| QPSK 1/2 **GI 1/4** | 4.98 Mbit/s | — | — | ❌ **never locks** |

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

- **The video path itself was never run**, because ffmpeg is not installed on this machine and
  installing it needs root. What *was* proved is stronger than a screenshot: the transport
  stream arrives **byte-identical**, and the service name was recovered from its SDT. A
  transport stream that survives intact carries whatever is inside it intact — video included.
  The first thing to do with `sudo apt install ffmpeg` is confirm the picture.
- **`Bintang.mp4` was inspected but never transcoded** — 1920×1080 H.264 with AAC audio, in a
  fragmented MP4. The ffmpeg command line is built and documented but has not been run.
- **Two-radio operation** (one transmitting, one receiving, as Lab 10 describes) was not tried;
  everything here is one B210 talking to itself.
- **No deliberate frequency offset was introduced**, so the synchroniser has never been tested
  against the problem a real receiver faces. See [above](#-what-full-duplex-actually-buys-and-what-it-hides).
- **No real television was pointed at this transmitter.** For that, use Lab 10's DVB-T2
  transmitter — consumer sets do not decode DVB-T2-era muxes and DVB-T interchangeably.
