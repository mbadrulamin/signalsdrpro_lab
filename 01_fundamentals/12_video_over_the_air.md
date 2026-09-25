# 📼 Fundamentals 12 — Video Over the Air: Transport Streams, Timing and Receivers

> **What you will learn:** what is **inside** a digital TV signal (the MPEG-2 **transport
> stream**); why its bit rate is calculated, not chosen; how a TV rebuilds the transmitter's
> **clock**; why video frames depend on each other; why a TV **receiver** is much harder to build
> than a transmitter; and why digital TV fails over a **one-decibel cliff**.
> **Before this:** [Fundamentals 10](./10_error_detection_and_framing.md) and
> [11 — OFDM](./11_ofdm_and_broadcast_systems.md). Read it before
> [Lab 11](../02_flowgraphs/lab11_tv_receiver/README.md) and
> [Lab 12](../02_flowgraphs/lab12_fullduplex_tv/README.md).
> **Time:** about 45 minutes.

[Fundamentals 11](./11_ofdm_and_broadcast_systems.md) explained how a digital TV signal is put
on the air. This chapter is about **what it carries**, and about the receiving end.

---

## 1. TV has a problem that file transfers do not

A file download can pause. Television cannot. The picture must appear 25 times a second,
whatever happens — on a TV whose clock is **not** the transmitter's clock, over a link with **no
way back**. The TV can never say "please send that again".

Three rules follow from that, and you will see them everywhere below:

1. **The bit rate is constant.** Empty "padding" is added if needed, because the transmitter runs
   like a clock.
2. **The timing travels inside the stream**, so the TV can rebuild the transmitter's clock from
   the data alone.
3. **Errors are corrected on arrival, or not at all** (forward error correction), because there
   is nobody to ask.

---

## 2. The MPEG-2 transport stream

Everything — video, sound, subtitles, the channel list, the clock — travels as a stream of
**packets of exactly 188 bytes**. (Why 188? It fitted neatly into 4 cells of the ATM telephone
network, back when TV was expected to travel over telephone networks. It didn't, but 188
stayed.)

```
 ┌──────┬───┬───┬───┬────────────┬──────────────────────────────────┐
 │ 0x47 │TEI│PUS│Pri│  PID (13)  │ scr │AF│CC│  payload (184 bytes) │
 └──────┴───┴───┴───┴────────────┴──────────────────────────────────┘
   byte 0       bytes 1–2          byte 3       bytes 4–187
```

| Field | Bits | What it does |
|---|---|---|
| **Sync byte** | 8 | always `0x47`. Marks the start of a packet, nothing more |
| Transport error indicator | 1 | the demodulator sets it when error correction failed |
| Payload unit start | 1 | a new video/audio piece or table starts in this packet |
| **PID** | 13 | **which stream** this packet belongs to (video, audio, a table…) |
| Scrambling | 2 | for pay-TV encryption |
| Adaptation field | 2 | whether there is extra information (like the clock) as well as data |
| **Continuity counter** | 4 | counts up by 1 for each packet of the same PID. **The only way to notice a lost packet** |

### The continuity counter tells the truth

It counts 0, 1, 2 … 15, 0, 1 … for each PID. If the receiver sees 7 followed by 9, packet 8 was
lost.

> ⚠️ **The sync byte proves nothing.** Every packet coming out of a DVB-T demodulator starts with
> `0x47` **whether or not decoding worked**, because the last stage (the energy descrambler)
> writes that byte every time. Leave out one of the eleven receiver stages (the symbol
> de-interleaver) and you get 100 % perfect `0x47` bytes — followed by pure noise.

**Judge a receiver by its PIDs and continuity counters, not by its sync bytes.**

### PIDs, and the tables that explain them

A TV that tunes in half-way through knows nothing. It works it out in steps:

| PID | Table | What it says |
|---|---|---|
| 0 | **PAT** (Program Association Table) | "programme 1's map is on PID 4096" |
| 4096 | **PMT** (Program Map Table) | "video on PID 256, audio on 257, the clock on 256" |
| 17 | **SDT** (Service Description Table) | "programme 1 is called *SDR LAB TV*" |
| 16 | **NIT** (Network Information Table) | "this network also uses channels 22, 25 and 31" |
| 8191 | null packets | padding — throw away |

**This is what "scanning for channels" means on a TV:** tune, lock, read the PAT, follow it to the
PMT, read the name from the SDT, save it. Lab 11's receiver does exactly this.

Each table carries a **32-bit CRC**, so a TV never acts on a damaged channel list — the same idea
as RDS's CRC ([Fundamentals 10](./10_error_detection_and_framing.md)), bigger.

**How much is padding?** In Lab 10's real video stream, **74.6 %** of packets are null (12 Mbit/s
of video in a 40 Mbit/s multiplex). In a test stream with no video at all, it is over 99 %.

---

## 3. Why the rate is calculated, not chosen

A DVB-T transmitter eats transport-stream bytes at a speed set completely by its modulation
settings:

$$\boxed{R = \frac{K_{\text{data}} \times b}{T_s} \times \frac{n}{d} \times \frac{188}{204}}$$

| Symbol | Meaning |
|---|---|
| $K_{\text{data}}$ | data carriers per symbol: 1512 (2K mode) or 6048 (8K mode) |
| $b$ | bits per carrier: 2 (QPSK), 4 (16QAM), 6 (64QAM) |
| $T_s$ | symbol length, including the guard interval |
| $n/d$ | the inner code rate (e.g. 2/3) |
| $188/204$ | the Reed–Solomon outer code's overhead |

**Example: 8K, 16QAM, code rate 2/3, guard 1/32.** The useful symbol is 8192 × 7/64 µs = 896 µs;
with the guard, 896 × 33/32 = 924 µs:

$$R = \frac{6048 \times 4}{924\,\mu s} \times \frac{2}{3} \times \frac{188}{204}
    = 26.182 \times 0.6667 \times 0.9216 = \mathbf{16.086\ \text{Mbit/s}}$$

Feed it 15 Mbit/s and it runs dry. Feed it 17 and it overflows. So the multiplex is **padded with
null packets** to exactly *R*. That is why broadcasters state their multiplex capacity to the
last bit per second.

> 💡 `03_scripts/make_video_ts.py --list-modes` prints this table from the formula. It matches the
> published DVB-T figures exactly: 6.032, 16.086, 24.128, 31.668 Mbit/s.

---

## 4. Timing: how the TV rebuilds a clock it never had

The TV's crystal is not the transmitter's. Left alone, it drifts — a few parts per million is
several frames an hour — and the TV would either run out of pictures or pile them up.

So the transmitter reads its own 27 MHz clock and writes the value into the stream, at least every
100 ms. This is the **PCR** (Program Clock Reference).

The TV runs a **PLL** — the same idea as Lab 04's stereo pilot PLL, but at 27 MHz instead of
19 kHz. It compares each PCR that arrives with its own counter, and adjusts its oscillator. Once
locked, the TV's clock **is** the transmitter's clock.

A useful trick (used by `make_video_ts.py --verify`): two PCRs, and the number of bytes between
them, give the multiplex rate directly — so you can check a file really has the rate it claims.

<details>
<summary><b>Going deeper:</b> PCR, PTS and DTS formulas</summary>

$$\text{PCR} = 300 \times \text{PCR}_{\text{base}} + \text{PCR}_{\text{ext}} \quad (\text{in 27 MHz ticks})$$

$$R = \frac{(i_1 - i_0) \times 188 \times 8}{(\text{PCR}_1 - \text{PCR}_0)/27\times10^6}$$

where $i$ is the packet number. On top of the PCR, each piece of video or audio (a **PES**
packet) carries a **PTS** — *when to show it* — and, for frames sent out of order, a **DTS** —
*when to decode it*. Both are in 90 kHz units of the same clock.
</details>

### What happens when the clock goes backwards

This was found the hard way, on a real TV, in [Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md).

The obvious way to broadcast a video non-stop is to encode it once and play the file in a loop.
Every byte is perfect. But at each loop, the PCR jumps **backwards** by the length of the file —
on Lab 10's 209-second stream, **−208.86 s** — and the show-times (PTS) jump with it.

The TV is not told. (There is a warning flag for this, `discontinuity_indicator`, but a file
simply looping does not set it.) So the TV's clock, carefully locked for three minutes, is
suddenly handed a time three minutes in the past, and frames stamped long ago.

What you see is **not** break-up. Error correction still works; every packet arrives intact. The
picture is **sluggish** — slightly wrong rhythm, never settling — and stays that way, because the
clock never gets a steady reference again. In 26 minutes of a 209-second loop, this happened
7.5 times.

**The fix: loop the input, not the output.** Let the encoder keep counting upwards forever. That
is what real TV playout does, and what `03_scripts/tv_playout.py` does.

> **The lesson.** Correct bytes are not the same as a working TV service. Lab 12 delivers 79 MB
> with zero byte errors; that is necessary, and nowhere near enough. **Broadcasting is a timing
> system that happens to carry data.**

---

## 5. Why video frames depend on each other

Video compression uses the fact that one frame is almost the same as the next.

| Frame type | Stores | Size (relative) | Can be shown on its own? |
|---|---|---|---|
| **I** (intra) | a whole picture | about 10× | ✅ yes |
| **P** (predicted) | the difference from an earlier frame | about 3× | ❌ no |
| **B** (bi-directional) | the difference from an earlier *and* a later frame | 1× | ❌ no |

A **GOP** (group of pictures), such as `I B B P B B P B B P`, repeats every 12–50 frames. Three
results:

1. **Changing channel is slow.** The TV must wait for the next I-frame. A 2-second GOP means up
   to 2 seconds of black. (Lab 10 uses a 1-second GOP of 25 frames.)
2. **Errors spread.** Damage an I-frame, and every frame built from it is wrong until the next
   I-frame. That is why digital TV break-up smears and freezes instead of flickering.
3. **B-frames are sent out of order** (a later frame must arrive first). That is why DTS exists
   as well as PTS.

---

## 6. Why the receiver is the hard part

A transmitter knows everything. A receiver arrives half-way through, knowing nothing, and must
find out, in this order:

| # | Unknown | How it is found | Cost |
|---|---|---|---|
| 1 | where each symbol starts | compare the cyclic prefix with the end of the symbol | **high while searching** |
| 2 | the small frequency error | the angle of that same comparison | free once 1 works |
| 3 | the whole-carrier frequency error | match the fixed pilot pattern | moderate |
| 4 | what the channel did | divide by the scattered pilots | low |
| 5 | the mode, if unknown | read the TPS signalling carriers | low |
| 6 | the frame boundary | TPS again | low |

Step 1 is the expensive one. Measured in Lab 11:

> **Searching, the DVB-T receiver ran at 1.55 million samples/s. Locked, the same receiver ran at
> 16.4 million samples/s. Searching costs about ten times more than tracking.**

The search compares across the guard interval, so its cost grows with the guard. That leads to a
surprising result: guard 1/4 is 2048 samples of comparison per symbol, eight times guard 1/32's
256. Measured live, **the receiver locked reliably at guard 1/32, and never locked at guard 1/4**
— even though 1/4 copes better with echoes, and decodes perfectly from a recorded file.

**Coping with the channel and coping with your own processor are different things — and they can
pull in opposite directions.**

---

## 7. Why two error-correcting codes

DVB-T uses two codes one after the other. That looks wasteful until you see what each one does:

```
   TS packet, 188 bytes
        │  Reed–Solomon (204,188)        ← fixes up to 8 wrong BYTES per packet
   204 B│  interleaver                   ← spreads a burst over 12 packets
        │  convolutional code            ← fixes scattered wrong BITS
        ▼  (Viterbi decoder)
```

- The **inner** convolutional code faces the raw channel and fixes scattered bit errors from noise.
  When it fails, it fails in **bursts**: a run of wrong bits together.
- The **outer** Reed–Solomon code works on **bytes**, which is the right tool for bursts: 8 wrong
  bytes can be fixed whether they are spread out or all together.
- The **interleaver between them** makes the pair work. Without it, one burst lands in one packet
  and overwhelms it. Spread over 12 packets, each gets only a few fixable bytes.

DVB-T2 keeps this design but swaps in LDPC and BCH, giving about 30 % more capacity in the same
8 MHz ([Fundamentals 11 §7](./11_ofdm_and_broadcast_systems.md#part-7--two-error-correcting-codes-one-inside-the-other)).

---

## 8. The cliff

The most important property of digital TV, measured on this course's own DVB-T chain (8K,
16QAM, rate 2/3, with added noise):

| SNR | Result |
|---|---|
| 14 dB | 0 byte errors |
| **13 dB** | **0 byte errors — perfect** |
| **12 dB** | 1,274 continuity errors — **broken** |
| 10 dB | 75 % of packets lost |

**One decibel** separates perfect from broken. The published DVB-T threshold for this mode is
13.5 dB, so the measurement agrees with the standard to within a decibel.

Why so sharp? Above the threshold, the two codes fix essentially every error, and the output is
**bit-for-bit identical** to the input. Below it, the inner decoder's bursts are too many for
Reed–Solomon, which then fails too — completely. There is almost nothing in between. Analog TV
spent its margin on a picture that got gradually worse; digital TV spends it on more channels.

> **Watch MER, never the picture.** MER (modulation error ratio) falls smoothly as conditions get
> worse. The picture stays perfect until it suddenly disappears. By the time you *see* a problem,
> you have no margin left.

---

## 9. DVB-T versus DVB-T2

| | DVB-T (1997) | DVB-T2 (2009) |
|---|---|---|
| Inner code | convolutional (Viterbi) | **LDPC** |
| Outer code | Reed–Solomon (204,188) | **BCH** |
| FFT sizes | 2K, 8K | 1K … **32K** |
| Constellations | QPSK, 16QAM, 64QAM | … **256QAM**, rotated |
| Pilots | one pattern | **8 patterns** |
| Preamble | none | **P1** — announces the mode |
| Capacity in 8 MHz | ~24 Mbit/s | **~36–40 Mbit/s** |
| In GNU Radio | **transmit and receive** | **transmit only** |

The last row shapes Labs 10–12. DVB-T2's P1 preamble shouts "DVB-T2 here, in this mode" before
any decoding — so Lab 11's scanner can **find and measure** DVB-T2 broadcasts that it cannot
decode.

---

## ✅ Summary

1. **188-byte packets, and a 4-bit counter that tells the truth.** Sync bytes can lie; continuity
   counters don't.
2. **The bit rate is arithmetic.** Calculate it, pad with nulls up to it, check it from the PCR.
3. **The clock travels in the stream.** PCR rebuilds it; PTS and DTS place the pictures. Make it
   jump backwards (by looping a finished file) and the picture goes sluggish while every byte is
   perfect.
4. **Frames depend on each other**, so channel changes are slow and errors spread.
5. **Finding the signal is the expensive part** of a receiver, and its cost grows with the guard
   interval.
6. **Two codes and an interleaver**, because bursts and scattered errors need different fixes.
7. **The cliff is one decibel wide. Watch MER.**

## 🧠 Check yourself

1. A receiver outputs 100 % perfect `0x47` sync bytes. Does that prove it works?
   <details><summary>Answer</summary>No. The descrambler writes <code>0x47</code> every time.
   Check the PIDs and continuity counters instead.</details>
2. What does a TV do when it "scans for channels"?
   <details><summary>Answer</summary>For each frequency: tune, lock, read the PAT, follow it to
   the PMT, read the service name from the SDT, and save it.</details>
3. Why must the transport stream rate exactly match the modulator?
   <details><summary>Answer</summary>The modulator consumes bytes at a fixed speed set by its
   settings. Too slow and it runs dry; too fast and it overflows. Pad with null packets to the
   exact rate.</details>
4. Why does looping a finished `.ts` file make the picture sluggish?
   <details><summary>Answer</summary>At each loop the PCR clock jumps backwards, and the TV's
   clock recovery never settles again.</details>
5. Why can a longer guard interval make a software receiver fail to lock?
   <details><summary>Answer</summary>The timing search compares across the guard, so a longer
   guard means much more work. The CPU may not keep up.</details>
6. Why watch MER instead of the picture?
   <details><summary>Answer</summary>MER falls gradually; the picture is perfect until it
   suddenly fails. MER warns you while you still have margin.</details>

**Next:** [Lab 11 — Build a TV Receiver →](../02_flowgraphs/lab11_tv_receiver/README.md) ·
[Lab 12 — Send and Receive Video at Once →](../02_flowgraphs/lab12_fullduplex_tv/README.md)
