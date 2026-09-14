# 12 — Video Over The Air: Transport Streams, Timing, and Receivers

> **Read before:** [Lab 11](../02_flowgraphs/lab11_tv_receiver/) and [Lab 12](../02_flowgraphs/lab12_fullduplex_tv/)
> **Assumes:** [Fund. 10 Error Detection & Framing](./10_error_detection_and_framing.md) and [Fund. 11 OFDM](./11_ofdm_and_broadcast_systems.md)

[Fundamentals 11](./11_ofdm_and_broadcast_systems.md) got a digital television signal onto a
carrier. This document is about what is *inside* it, why the bit rate is not negotiable, and
why building the receiver is so much harder than building the transmitter.

---

## 1. The problem television has that a data link does not

A file transfer can pause. A television cannot. The picture must appear at 25 frames a second
whatever happens, on a receiver whose clock is not the transmitter's, over a link with no
return path — so the receiver can never say "please repeat that".

Three consequences run through everything below:

1. **The stream is constant bit rate**, padded if necessary, because the modulator is a clock.
2. **Timing is carried in the stream itself**, because the receiver must reconstruct the
   transmitter's clock from nothing but the bits.
3. **Errors are corrected forward or not at all**, because there is nobody to ask.

---

## 2. The MPEG-2 Transport Stream

Everything — video, audio, subtitles, the channel list, the clock — travels as a stream of
**188-byte packets**. That number comes from ATM: 4 ATM cells of 47 bytes, chosen when it
looked as though broadcasting would ride on telecoms networks. It didn't, and 188 stayed.

```
 ┌──────┬───┬───┬───┬────────────┬──────────────────────────────────┐
 │ 0x47 │TEI│PUS│Pri│  PID (13)  │ scr │AF│CC│  payload (184 bytes) │
 └──────┴───┴───┴───┴────────────┴──────────────────────────────────┘
   byte0        byte1-2            byte3        bytes 4..187
```

| Field | Bits | Job |
|---|---|---|
| Sync byte | 8 | Always `0x47`. Framing, nothing more |
| Transport Error Indicator | 1 | The demodulator sets it when FEC gave up |
| Payload Unit Start | 1 | A new PES packet or table section begins here |
| **PID** | 13 | Which stream this packet belongs to |
| Scrambling | 2 | Conditional access |
| Adaptation field ctrl | 2 | Is there an adaptation field, a payload, or both |
| **Continuity counter** | 4 | Increments per PID. **The only in-band way to notice loss** |

### The continuity counter is the number that matters

Four bits, incrementing modulo 16 on every packet carrying payload for that PID. If the
receiver sees 7 followed by 9, a packet is gone.

This is the honest measure of link health, and the reason is worth stating plainly:

> **A sync byte proves nothing.** Every packet leaving a DVB-T demodulator starts with `0x47`
> whether or not the decode worked, because the energy descrambler writes that byte
> unconditionally. Omit the symbol deinterleaver from a receiver — one block out of eleven —
> and you get a stream with a perfect `0x47` on all 100 % of packets and pure noise in every
> payload byte.

Judge a receiver by its PIDs and its continuity counters. In a real multiplex roughly 99.6 % of
packets are PID 8191, the null packet.

### PIDs and the tables that explain them

A receiver arriving mid-stream knows nothing. It bootstraps:

| PID | Table | Says |
|---|---|---|
| 0 | **PAT** Program Association | "Programme 1's map is on PID 4096" |
| 4096 | **PMT** Program Map | "Video on PID 256, audio on 257, clock on 256" |
| 17 | **SDT** Service Description | "Programme 1 is called *BFM 89.9 TV*" |
| 16 | **NIT** Network Information | "This network also uses channels 22, 25, 31" |
| 8191 | null | Padding. Discard |

That is what "scanning for channels" on a television actually is: tune, lock, read the PAT,
follow it to the PMT, read the SDT for a name, store it. Lab 11's receiver does exactly this —
the name `SELFTEST` in its verification output was read off the air from the SDT.

Every one of these tables carries a **CRC-32**, so a receiver never acts on a corrupted channel
list. Same idea as RDS's CRC in [Fundamentals 10](./10_error_detection_and_framing.md), on a
larger scale.

---

## 3. Why the rate is computed, not chosen

A DVB-T modulator consumes transport bytes at a rate fixed entirely by the modulation
parameters. From the elementary period $T$ (7/64 µs for an 8 MHz channel):

$$T_u = N_{\text{FFT}} \cdot T \qquad\qquad T_s = T_u\left(1 + \frac{1}{G}\right)$$

$$\boxed{R = \frac{K_{\text{data}} \cdot b}{T_s} \times \frac{n}{d} \times \frac{188}{204}}$$

- $K_{\text{data}}$ — data cells per symbol: 1512 (2K) or 6048 (8K)
- $b$ — bits per cell: 2 (QPSK), 4 (16QAM), 6 (64QAM)
- $n/d$ — inner convolutional code rate
- $188/204$ — the outer Reed-Solomon overhead

**Worked example**, 8K / 16QAM / CR 2/3 / GI 1/32:

$$T_u = 8192 \times \tfrac{7}{64}\,\mu s = 896\,\mu s, \qquad T_s = 896 \times \tfrac{33}{32} = 924\,\mu s$$

$$R = \frac{6048 \times 4}{924\,\mu s} \times \frac{2}{3} \times \frac{188}{204}
    = 26.182 \times 0.6667 \times 0.9216 = \mathbf{16.086\ \text{Mbit/s}}$$

Feed that modulator 15 Mbit/s and it starves. Feed it 17 and the buffer overruns. So the
multiplex is **stuffed with null packets** up to exactly $R$ — which is why a real broadcaster
quotes its multiplex capacity to the bit per second, and why 99.6 % of a lightly-loaded
multiplex is padding.

> `03_scripts/make_video_ts.py --list-modes` prints this table from the equation above. It
> reproduces the published DVB-T figures exactly: 6.032, 16.086, 24.128, 31.668 Mbit/s.

---

## 4. Timing: how the receiver rebuilds a clock it never had

The receiver's crystal is not the transmitter's. Left alone it will drift — a few parts per
million is several frames an hour — and the picture will either run dry or pile up.

So the transmitter samples its own 27 MHz clock and writes the value into the stream as the
**Programme Clock Reference**, in an adaptation field, at least every 100 ms:

$$\text{PCR} = 300 \times \text{PCR}_{\text{base}} + \text{PCR}_{\text{ext}}$$

The receiver runs a phase-locked loop — the same idea as Lab 08's PLL, at 27 MHz instead of
19 kHz — comparing each arriving PCR against its own counter and steering its oscillator.
Once locked, its clock *is* the transmitter's.

This also gives a neat trick used in `make_video_ts.py --verify`: two PCRs and the number of
bytes between them recover the mux rate directly,

$$R = \frac{(i_1 - i_0) \times 188 \times 8}{(\text{PCR}_1 - \text{PCR}_0)/27\times10^6}$$

so you can check a file really is muxed at the rate it claims, without trusting the muxer.

Presentation timing rides on top: each **PES** packet carries a **PTS** (when to show it) and,
for out-of-order frames, a **DTS** (when to decode it), both in 90 kHz units derived from the
same clock.

---

## 5. What is inside: why frames are not independent

Video compression exploits the fact that consecutive frames are nearly identical.

| Frame | Encodes | Size | Decodable alone? |
|---|---|---|---|
| **I** | A whole picture | ~10× | ✅ |
| **P** | Difference from the previous | ~3× | ❌ |
| **B** | Difference from previous *and next* | 1× | ❌ |

A **GOP** — say `I B B P B B P B B P` — repeats every 12 to 50 frames. Three consequences:

1. **Channel change is slow.** The receiver must wait for the next I-frame. A 2-second GOP
   means up to 2 seconds of black. Broadcasters shorten GOPs to feel responsive, and pay for it
   in bit rate.
2. **Errors persist.** Corrupt an I-frame and every frame referencing it is wrong until the
   next one. This is why digital breakup smears and freezes rather than flickering.
3. **B-frames arrive out of order**, which is exactly why DTS exists alongside PTS.

---

## 6. The receiver's problem, which is not the transmitter's

A transmitter knows everything. A receiver arrives mid-stream knowing nothing and must
establish, in order:

| # | Unknown | How it is found | Cost |
|---|---|---|---|
| 1 | Where symbols start | Correlate the cyclic prefix against the symbol tail | **Expensive while searching** |
| 2 | Fractional frequency offset | Phase of that same correlation peak | Free once (1) works |
| 3 | Integer carrier offset | Correlate against the continual pilot pattern | Moderate |
| 4 | Channel response | Divide by the scattered pilots | Cheap |
| 5 | Mode, if unknown | Read the TPS carriers | Cheap |
| 6 | Frame boundary | TPS again | Cheap |

Step 1 is the expensive one, and it produces a result measured in Lab 11 that is worth
remembering:

> **An unlocked DVB-T receiver ran at 1.55 MSPS; the same receiver, locked, ran at 16.4 MSPS.
> Searching costs six times what tracking costs.**

The search window is the cyclic prefix, so the cost scales with the guard interval — which
produces a genuinely counter-intuitive result. GI 1/4 is 2048 samples of correlation per
symbol against GI 1/32's 256: eight times the work. Measured live, **the receiver locked
reliably in GI 1/32 and never locked at all in GI 1/4**, even though GI 1/4 is the *more robust*
mode against multipath and decodes perfectly from a recorded file.

Robustness against the channel and robustness against your own processor are different axes,
and they can point in opposite directions.

---

## 7. Why forward error correction is layered

DVB-T uses two codes in series, which looks redundant until you ask what each is for.

```
   TS packet 188 B
        │  Reed-Solomon (204,188)     ← corrects up to 8 wrong BYTES
   204 B│  Convolutional interleaver  ← spreads a burst over 12 RS blocks
        │  Convolutional code n/d     ← corrects scattered BIT errors
        ▼  (Viterbi-decoded)
```

The **inner** convolutional code runs against the raw channel and fixes the dense, random bit
errors that thermal noise produces. It fails in *bursts*: when a Viterbi decoder loses the
path, it emits a run of wrong bits, not isolated ones.

The **outer** Reed-Solomon code is a byte-oriented block code, which is exactly the right shape
for burst errors — eight wrong bytes are correctable whether they are scattered or adjacent.

The **interleaver between them** is what makes the pairing work. Without it, one Viterbi burst
lands inside one RS block and overwhelms it. Spread across 12 blocks, the same burst puts a few
correctable bytes into each.

DVB-T2 keeps the structure and swaps the codes for LDPC + BCH, buying roughly 30 % more
capacity in the same 8 MHz — see [Fundamentals 11](./11_ofdm_and_broadcast_systems.md).

---

## 8. The cliff

The defining property of digital television, measured on this repository's own chain
(8K, 16QAM, CR 2/3, in AWGN):

| SNR | Result |
|---|---|
| 14 dB | 0 byte errors |
| **13 dB** | **0 byte errors — flawless** |
| **12 dB** | 1,274 continuity errors — **broken** |
| 10 dB | 75 % of packets lost |

**One decibel.** The published DVB-T threshold for this mode is 13.5 dB C/N, so the measurement
sits within a decibel of the standard.

Why so sharp? Concatenated FEC has a threshold. Below it the inner decoder's burst rate exceeds
what Reed-Solomon can absorb, RS fails too, and the failure is total. Above it, essentially
every error is corrected and the output is *bit-identical* to the input. There is no useful
region in between — which is precisely the point. All the margin that analogue spent on a
visibly degraded picture, digital spends on more programmes.

The practical consequence for anyone operating a link:

> **Watch MER, never the picture.** MER falls smoothly and predictably as conditions worsen.
> The picture is perfect right up until it is gone. By the time you can see a problem you have
> already lost all your margin.

---

## 9. DVB-T against DVB-T2

| | DVB-T (1997) | DVB-T2 (2009) |
|---|---|---|
| Inner FEC | Convolutional, Viterbi | **LDPC** |
| Outer FEC | Reed-Solomon (204,188) | **BCH** |
| FFT sizes | 2K, 8K | 1K … **32K** |
| Constellations | QPSK, 16QAM, 64QAM | … **256QAM**, rotated |
| Pilots | one pattern | **8 patterns**, chosen to fit |
| Preamble | none | **P1** — carries the mode itself |
| 8 MHz capacity | ~24 Mbit/s | **~36–40 Mbit/s** |
| In GNU Radio | **TX and RX** | **TX only** |

The last row is the one that shapes these labs. DVB-T2's P1 preamble is a gift to a
*scanner* — it announces "DVB-T2 here, and here is the mode" before any demodulation — which is
why Lab 11's scanner can find and measure DVB-T2 broadcasts it has no hope of decoding.

---

## 10. What to take away

1. **188 bytes, and a 4-bit counter that tells you the truth.** Sync bytes lie; continuity
   counters do not.
2. **The bit rate is arithmetic, not a preference.** Derive it, stuff nulls up to it, verify it
   from the PCR.
3. **Timing travels in the stream.** PCR rebuilds the clock; PTS/DTS place the pictures.
4. **Frames depend on each other**, so channel change is slow and errors smear.
5. **Acquisition is the expensive part of a receiver**, and its cost scales with the guard
   interval — sometimes in the opposite direction to robustness.
6. **Two codes and an interleaver**, because burst errors and random errors need different
   medicine.
7. **The cliff is one decibel wide.** Measure MER.

---

**Next:** [Lab 11 — Television Receiver](../02_flowgraphs/lab11_tv_receiver/) ·
[Lab 12 — Full-Duplex Video Link](../02_flowgraphs/lab12_fullduplex_tv/)
