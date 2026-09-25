# 📡📺 Lab 12 — Send and Receive Video at the Same Time (Full Duplex)

> **What you will build:** one flowgraph that **transmits** a real video as digital TV and
> **receives it back** on the same radio, **at the same time** — with the picture on screen.
> **What you will learn:** full-duplex operation; making a video stream at the exact rate the
> modulator needs; a **link budget** that explains a failed first attempt; and how to prove a link
> is perfect, byte for byte.
> **Before this:** **[Fundamentals 11](../../01_fundamentals/11_ofdm_and_broadcast_systems.md)**,
> **[12](../../01_fundamentals/12_video_over_the_air.md)**, and [Lab 11](../lab11_tv_receiver/README.md).
> **Time:** about 4 hours. **Difficulty:** expert.
> **Hardware:** one SignalSDR Pro, and **a cable with attenuators, or a Faraday cage**.
> **File:** `lab12_fullduplex_tv.grc`

---

## 🚨 Before you transmit anything

**This lab transmits.** DVB-T uses **8 MHz of spectrum licensed to TV broadcasters**, and a DVB-T
signal looks exactly like a real broadcast. In Malaysia, 470–694 MHz is live MYTV digital TV.

### The only safe ways to do this lab

| | Setup | Notes |
|---|---|---|
| ✅ | **A cable: `TX/RX` → attenuators → `RX2`** | **The best choice.** Nothing is radiated — and the link works *better* than with antennas (see Section 4) |
| ✅ | **Faraday cage** (a shielded box) | the whole radio inside |
| ✅ | **Files only** — record with `verify_tv_link.py`, decode afterwards | everything except the live demonstration |
| ❌ | "Low power should be fine" | It is not. A few milliwatts at UHF can travel hundreds of metres |
| ❌ | "I scanned and the channel was empty" | **Empty to your antenna is not empty.** A scan here found nothing across 470–694 MHz — because the antenna was cut for 100 MHz |

### The transmitter starts switched off

`lab12_fullduplex_tv.grc` starts with **`tx_amplitude = 0.0`** and **`tx_gain = 0 dB`**. It sends
nothing until you raise **both**. **Look at the `TX/RX` port before you touch either slider** — it
is used for transmitting, and an antenna from an earlier lab may still be on it.

Before every session, scan the channels you might use:

```bash
../../03_scripts/scan_tv_band.py --first 21 --last 48
```

And after every session, check nothing is still transmitting:

```bash
ps -eo pid,args | grep -E "[l]ab12|[v]erify_tv_link"
```

Stop anything you find by its PID (`kill 12345`) — not with `pkill -f`.

---

## 🎯 Goal

Put a real video on the air as digital TV, and receive it back on the same radio, at the same
time, in one flowgraph — with the picture on screen.

```
  Bintang.mp4 → ffmpeg → MPEG-2 TS at exactly 16.086 Mbit/s
       → DVB-T transmitter → TX/RX  ═══cable═══  RX2 → DVB-T receiver
              → MPEG-2 TS → ffplay → picture
```

> ✅ **Tested on real hardware.** 40 seconds of full-duplex 1080p video at 474 MHz:
> **79,357,996 bytes received, 0 wrong — 100.000000 %**; 422,304 packets, **0 sync errors, 0
> continuity errors**; MER 15.7 dB; decoded into **975 video frames and 39.45 s of audio**; and
> the channel name `SDR LAB TV` read back from the signal. See [Verification](#-verification).

---

## 1. What "full duplex" gives you — and what it hides

The SignalSDR Pro (as a B210) has **separate** transmit and receive chains. Here, channel A's
**`TX/RX`** port transmits while its **`RX2`** port receives, both at 9.142857 MSPS. Over USB 3.0
that is 2 × 9.14 million × 8 bytes = **146 MB per second**, non-stop. (USB 2.0 cannot do this.)

> ⚠️ **The catch: there is no frequency error.** The transmitter and receiver share **one** clock,
> so the signal arrives at **exactly** the expected frequency. A real receiver faces an error of
> tens of kHz between two separate crystals, and must search for it.
>
> So this lab gives the receiver an unrealistically easy job. That is useful — it tests everything
> else — but **a working loopback does not prove the receiver would lock to a real broadcaster**.
>
> **Make it honest:** add a deliberate frequency error. Put a **Frequency Xlating FIR Filter** (or
> a rotator) between the modulator and the USRP Sink, and set it to a few kHz. Find where it stops
> locking. That teaches more than watching it work.

---

## 2. Making the video stream

```bash
sudo apt install ffmpeg          # the only extra software this course needs

../../03_scripts/make_video_ts.py ~/Downloads/Bintang.mp4 /tmp/bintang.ts \
    --mode 16qam-2/3-1/32 --width 1280 --duration 300 --loop
```

The flowgraph's `ts_in` already points at `/tmp/bintang.ts`. Run it.

**No ffmpeg?** You can still test every part of the radio:

```bash
../../03_scripts/make_test_ts.py --out /tmp/bintang.ts --seconds 10 --rate 16085561
```

That stream has the tables (PAT, PMT, SDT, NIT) and a channel name, but no video. A TV lists the
channel by name; there is just no picture.

### For watching, use playout — not a looping file

`ts_in` reading a finished `.ts` in a loop is right for the **byte-for-byte test** below (you need
the original to compare with). It is **wrong for watching**: at each loop, the stream's clock
(PCR) jumps backwards by the file's length, and the receiver's clock never settles again. The
picture stays perfect but goes **sluggish**
([Lab 10](../lab10_dvbt2_tx_rx/README.md#step-0--make-a-transport-stream-the-tv-programme) found
this on a real TV).

For watching, loop the **video** instead, with playout:

```bash
../../03_scripts/tv_playout.py ~/Downloads/Bintang.mp4 \
    --standard dvbt --mode 16qam-2/3-1/32 --fifo /tmp/tv.fifo
```

Then set `ts_in` to `/tmp/tv.fifo`. The stream's clock now counts upwards forever.

### Why the bit rate is calculated

A DVB-T modulator is a **clock**, not a queue. Once you choose the FFT size, constellation, code
rate and guard interval, it eats transport-stream bytes at **one fixed rate**
([Fundamentals 12 §3](../../01_fundamentals/12_video_over_the_air.md#3-why-the-rate-is-calculated-not-chosen)).
For 8K, 16QAM, rate 2/3, guard 1/32:

$$\frac{6048 \times 4}{924\,\mu s} \times \frac{2}{3} \times \frac{188}{204} = 16.086\ \text{Mbit/s}$$

Use a different rate, and the picture drifts against its own clock until the receiver gives up.
`make_video_ts.py` calculates the rate, tells ffmpeg to pad exactly to it with null packets, and
`--verify` checks the result from the stream's own clock.

`make_video_ts.py --list-modes` prints every mode, calculated from the formula. It matches the
published DVB-T figures: 6.032, 16.086, 24.128, 31.668 Mbit/s.

---

## 3. Running it

1. Connect **`TX/RX` → 20–30 dB attenuator → `RX2`** with a short coax cable. No antennas.
2. Make the stream (Section 2).
3. Open and run the flowgraph:

   ```bash
   gnuradio-companion lab12_fullduplex_tv.grc
   ```

4. Raise **`tx_gain`** and **`tx_amplitude`** slowly. Watch the receive side's **level**, **MER**
   and **constellation**.
5. When MER is above about **15 dB**, the receiver locks, the continuity-error count stays at
   zero, and the picture appears.

> 💡 **Too much signal is the usual problem on a cable.** If the constellation is a smeared blob at
> high gain, lower `rx_gain` first, then `tx_gain`.

---

## 4. The link budget: why the first attempt failed

The first over-the-air attempt decoded **nothing**. Working out why is the most useful hour of
this lab — because it was not a bug.

**Step 1 — is anything being sent?** A plain test tone (CW) at the same settings stood **42 dB**
above the noise. So the transmitter works, and a radio path exists.

**Step 2 — then why does the TV signal not arrive?** Because a tone and a TV signal **with the same
total power** are not equally easy to see. The tone puts all its power into one narrow 2.2 kHz
slot. DVB-T spreads the same power over 7.6 MHz — about 3,400 slots:

$$10\log_{10}(3400) \approx 35\ \text{dB}$$

```
   42    dB   how strong the tone looked
 − 35    dB   spreading over 7.6 MHz
 −  8.4  dB   the tone's total power was higher than the TV signal's
 ────────
 ≈ −1.4  dB   how strong the TV signal should look
```

Measured: **+0.92 dB**. Prediction and measurement agree.

**Step 3 — how much is needed?** About **13 dB** (Lab 11's cliff). The link was about **15 dB
short**.

**Step 4 — the fix.** **Not** more receive gain: that lifts the signal and the noise together, so
the signal-to-noise ratio does not change. The answer was **19 dB more transmit gain**:

| TX gain | Rise above noise, in band | Shoulder | Result |
|---|---|---|---|
| 0 dB | 0.0 dB | 0.2 dB | nothing |
| 70 dB | 0.9 dB | 5.2 dB | still nothing |
| **89 dB** | **16.5 dB** | **21.3 dB** | **locks, decodes, picture** |

> **This is the whole reason to use a cable.** A short coax with a 20–30 dB attenuator gives a far
> cleaner signal than two antennas across a room, with much less transmit power, and radiates
> nothing. **The safest setup is also the one that works best.**

---

## 🔬 Verification

### Your own video, sent and received

40 seconds of `Bintang.mp4` (1920×1080 H.264 at 15.1 Mbit/s, with MP2 audio), through the
transmitter, over the air, and back through the receiver:

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

(`verify_tv_link.py` **transmits**. It asks you to confirm first; its transmit gain starts at 0.)

**79 MB of video, byte-identical.** Then decoded:

```
$ ffmpeg -i /tmp/verify_rx.ts -map 0:v -f null -
  Stream #0:0[0x100]: Video: h264 (High), yuv420p, 1920x1080, 25 fps
  Stream #0:1[0x101]: Audio: mp2, 48000 Hz, stereo, 192 kb/s
  frame= 975      <- 39.4 s of video at 25 fps
```

> **The control test.** The decoder printed a few warnings, because the recording starts in the
> middle of a group of pictures (a receiver tuning in must wait for the next keyframe). To prove
> the radio did not cause them, the **same byte range** was cut from the original file and decoded
> too:
>
> ```
> $ cmp /tmp/rx_slice.ts /tmp/src_slice.ts
>   (no output - 78,995,720 bytes identical)
> warnings decoding the RECEIVED slice : 31
> warnings decoding the SOURCE  slice : 31
> ```
>
> Same bytes, same warnings. Every warning comes from joining a stream in the middle; none came
> from the radio.

### An earlier result, corrected

A first run (25 s) reported **32 continuity errors** and 99.96 % byte accuracy, at MER 17.7 dB. It
was blamed on phase noise. It was mostly **the test's own fault**: that run looped a 3-second test
stream, and every loop is a real break in the continuity counters and the clock. The receiver
reported it honestly. Playing a 209-second file straight through gave **zero** errors.

**If you loop a short stream, expect a burst of errors at every loop — it is not the radio.**

### Three modes compared

| Mode | Bit rate | MER | Byte error rate | Locks live? |
|---|---|---|---|---|
| **16QAM 2/3, GI 1/32** | 16.09 Mbit/s | 15.7 dB | **0** (79 MB) | ✅ ← default |
| QPSK 1/2, GI 1/32 | 6.03 Mbit/s | 14.7 dB | 9.3 × 10⁻⁴ * | ✅ |
| QPSK 1/2, **GI 1/4** | 4.98 Mbit/s | — | — | ❌ **never locks** |

\* measured with the looping 3-second stream — see the correction above.

The last row is not a radio problem: that mode decodes perfectly from a file. The receiver's
timing search covers the guard interval — 2048 samples at GI 1/4, against 256 at GI 1/32, eight
times the work — and in real time the CPU cannot keep up. **The "more robust" mode was the one
that failed.** Robustness against echoes and robustness against your own CPU are different things.

---

## 🔧 Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `RuntimeError: No devices found` | An earlier run still has the radio | Find it by PID and stop it. Avoid `pkill -f` (it kills the terminal that runs it) |
| Nothing decodes, and the receive level does not change with `tx_gain` | No radio path, or the signal is spread below the noise | Send a test tone instead: a tone survives about 35 dB more loss than an 8 MHz signal. If the tone shows and DVB-T does not, it is the link budget, not the wiring |
| `U` from the USRP Sink | The transmit side is not getting samples fast enough — usually because the unlocked receiver is using the CPU | Make sure a signal is present; an unlocked receiver runs at 1.55 MSPS and starves everything |
| `O` from the USRP Source | The receive side is not keeping up | Expected while unlocked. If it continues after lock, use QPSK or 2K |
| Locks, then the picture drifts or freezes | The stream's rate is not the mode's rate | `make_video_ts.py --verify` reads the real rate from the stream's clock and compares |
| The constellation is a smeared blob at high gain | Overload — too **much** signal, the usual problem on a cable | Lower `rx_gain` first, then `tx_gain` |
| Perfect picture, then suddenly nothing | You were at the cliff edge | Watch MER: below about 15 dB there is no margin |

---

## ❓ Not yet tested

- **Nobody has watched the picture live.** The stream was decoded frame by frame, and still images
  were taken from it, but no person sat in front of `ffplay`.
- **Two radios** (one sending, one receiving) were not tried. Everything here is one radio talking
  to itself.
- **No deliberate frequency error was added**, so the receiver has never faced the problem a real
  receiver faces (Section 1).
- **No TV was pointed at this transmitter.** Lab 12 sends **DVB-T**. Every Malaysian TV receives
  DVB-T2, and many also receive DVB-T — but this was not tested. For a TV test, use
  [Lab 10](../lab10_dvbt2_tx_rx/README.md)'s DVB-T2 transmitter.

---

## ✅ Summary

- Full duplex: one radio transmits on `TX/RX` and receives on `RX2` at the same time — 146 MB/s
  over USB 3.0.
- Sharing one clock hides the frequency-error problem. Add an offset to make the test honest.
- The stream's **rate** is calculated from the mode, and must be exact. Loop the **video**, not the
  finished file.
- A narrow test tone looks ~35 dB stronger than an 8 MHz signal of the same power.
- More **receive** gain cannot fix a weak link; more **transmit** gain (or a cable) can.
- **A cable with attenuators is the safest and the best-performing setup.**
- Result: **79,357,996 bytes, 0 wrong.**

## 🧠 Check yourself

1. Why is a full-duplex loopback on one radio an unrealistically easy test for the receiver?
   <details><summary>Answer</summary>Transmitter and receiver share one clock, so there is no
   frequency error to find. A real receiver must search for tens of kHz of error.</details>
2. A test tone stands 42 dB above the noise, but the DVB-T signal cannot be decoded. How can both
   be true?
   <details><summary>Answer</summary>The tone's power is in one narrow slot; DVB-T spreads the
   same power over ~3,400 slots (35 dB), and the tone also had 8.4 dB more total power. So the TV
   signal was only about −1.4 dB above the noise.</details>
3. Why doesn't raising the receive gain fix a weak link?
   <details><summary>Answer</summary>It raises the signal and the noise together, so the
   signal-to-noise ratio stays the same.</details>
4. You loop a 3-second test stream and see errors every 3 seconds. Is the radio faulty?
   <details><summary>Answer</summary>No. Every loop breaks the continuity counters and the clock.
   The receiver is correctly reporting a real break in the stream.</details>

**Congratulations — you have finished the labs.** For what to do next, see
[the Applications Catalogue](../../04_applications/README.md): 589 more signals and projects.
