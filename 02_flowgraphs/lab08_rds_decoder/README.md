# 📡 Lab 08 — Read a Station's Name (RDS Decoder)

> **What you will build:** a decoder for **RDS** — the small data signal hidden inside FM
> broadcasts that carries the **station name** and the **scrolling text** your car radio shows.
> **What you will learn:** how to get at hidden subcarriers, how to decode a real digital
> signal (timing, carrier, bits), and how a **CRC** can find where each message starts.
> **Before this:** [Lab 07](../lab07_bpsk_link_sim/README.md) (a digital receiver in a clean
> simulation), and [Fundamentals 08](../../01_fundamentals/08_digital_modulation.md),
> [09](../../01_fundamentals/09_synchronization.md) and
> [10 — Error Detection & Framing](../../01_fundamentals/10_error_detection_and_framing.md).
> **Time:** about 3 hours. **Difficulty:** expert.
> **Needs the radio:** optional — there is a second flowgraph that reads a file instead.

**Two flowgraphs:**

| File | Input | Use it to |
|---|---|---|
| `lab08_rds_from_file.grc` | a test file you generate | check the decoder works, with a signal you know |
| `lab08_rds_decoder.grc` | the live radio | decode real stations |

---

## 🎯 Goal

Read the **station name** (8 characters) and the **RadioText** (up to 64 characters) from a
normal FM broadcast. This data has been inside every station you have received since Lab 01.
You threw it away without knowing.

This lab uses almost everything you have learned so far:

| Fundamentals | Used for |
|---|---|
| 02 IQ sampling | the IQ signal from the radio |
| 04 FM | FM decoding, by hand, to get the MPX |
| 05 Filters | three filters, and planning the sample rates |
| 06 Noise | why RDS needs a strong station |
| 07 AM / DSB | RDS is a suppressed-carrier signal, like stereo L−R |
| 08 Digital modulation | differential BPSK and biphase coding |
| 09 Synchronisation | timing recovery and the Costas loop |
| 10 CRC | finding where each block starts |

> ✅ **Tested on real radio.** On a live SignalSDR Pro receiving **BFM 89.9 MHz**, this decoder
> received **287 good RDS groups in 30 seconds** (9.6 per second; the maximum possible is 11.4)
> and read the station's scrolling name. On an empty channel it found **zero** groups in 11,766
> tries. See [Verification](#-verification).

---

## 1. What RDS is

**RDS** (Radio Data System) started in 1984 and is used by FM stations all over the world. It
carries:

- the **station name** on your car radio's display (called **PS**, Programme Service name),
- **RadioText** — song titles or messages that scroll past,
- a **station ID** number (called **PI**),
- the programme type (news, pop, …), traffic flags, and a list of other frequencies for the
  same station.

### Where it lives

After FM decoding you get the **MPX** signal
([Fundamentals 04 §5](../../01_fundamentals/04_fm_theory.md#5-what-is-inside-an-fm-broadcast)).
RDS sits at the top, at 57 kHz:

```
  strength
    │  ███████████                                  ← L+R mono sound (0–15 kHz)
    │                  ▌                            ← 19 kHz pilot
    │                      ▄▄▄▄▄▄▄▄▄▄▄▄▄            ← L−R stereo, around 38 kHz
    │                                      ▂▂▂▂▂    ← RDS, around 57 kHz
    └──┬─────────┬────┬───┬───────────┬────┬───┬──  kHz
       0        15   19  23          53   57  60
```

Everything is locked to the 19 kHz pilot:

- stereo carrier = 2 × 19 kHz = **38 kHz**
- RDS carrier = 3 × 19 kHz = **57 kHz**
- RDS bit rate = 57,000 ÷ 48 = **1187.5 bits per second**

> 💡 **A shortcut in this lab.** We do not rebuild 57 kHz from the pilot. We just use a fixed
> 57 kHz, and let a Costas loop correct the small error. This works because the SignalSDR Pro's
> clock is very accurate (its error at 57 kHz is well under 1 Hz).

### How the bits are packed

Three layers, each solving one problem:

```
  data bits (1187.5 per second)
       │
       ▼  differential encoding: send "did the bit change?"
  solves: the Costas loop's upside-down (180°) problem — as in Lab 07
       │
       ▼  biphase coding: each bit becomes TWO opposite halves ("chips"): 1 → +−, 0 → −+
  solves: (a) leaves a gap exactly at 57 kHz, so RDS does not disturb stereo;
          (b) guarantees a change in every bit, so timing recovery always has something to lock to
       │
       ▼  smooth pulse shaping
  solves: keeps RDS inside 57 kHz ± 2.4 kHz
       │
       ▼  put onto 57 kHz, with the carrier suppressed (like stereo L−R)
```

RDS is sent **very quietly** — only about 2–4 % of the FM swing. So a station that *sounds*
perfect may still be too weak for RDS. You need a strong station.

### Blocks and groups

RDS data comes in **groups** of 104 bits. Each group has four **blocks** (A, B, C, D) of
26 bits:

```
  ┌───────────────── GROUP = 104 bits = 87.6 ms ─────────────────┐
  │  Block A  │  Block B  │  Block C  │  Block D  │
  │  26 bits  │  26 bits  │  26 bits  │  26 bits  │
  └───────────┴───────────┴───────────┴───────────┘
       │
       └─▶  16 data bits  +  10 check bits (a CRC, with an "offset word" added)
```

**Here is the clever part.** There is **no start marker** at the beginning of a group. So how
does the receiver know where a block begins?

Each block's 10 check bits are a **CRC** (a checksum — see
[Fundamentals 10](../../01_fundamentals/10_error_detection_and_framing.md)), with a special
**offset word** mixed in. There is a different offset word for A, B, C and D. The receiver
slides along the bits one at a time, and at each position does the CRC calculation:

- At a **wrong** position, the result is random.
- At the **right** position, the result is exactly one of the offset words — which also tells
  you **which** block it is (A, B, C or D).

So one small calculation finds the start **and** identifies the block, using no extra bits at
all.

<details>
<summary><b>Going deeper:</b> the CRC details</summary>

| | |
|---|---|
| Generator polynomial | $g(x) = x^{10}+x^8+x^7+x^5+x^4+x^3+1$ = `0x5B9` |
| Offset A | `0011111100` |
| Offset B | `0110011000` |
| Offset C | `0101101000` |
| Offset C′ | `1101010000` (used instead of C in "B" version groups) |
| Offset D | `0110110100` |

The check bits are the CRC of the 16 data bits, XORed with the block's offset word. Because
the code is cyclic, the syndrome of a correctly aligned received block equals the offset word:

$$
\text{syndrome}(r) = r(x) \bmod g(x) = \text{offset}_X
$$
</details>

### The groups this lab decodes

| Group type | Carries |
|---|---|
| **0A / 0B** | 2 characters of the 8-character station name (PS) |
| **2A** | 4 characters of the 64-character RadioText |
| **2B** | 2 characters of a 32-character RadioText |
| Every group, block A | the **PI** code: a number that identifies the station |
| Every group, block B | the programme type (**PTY**) and traffic flag (**TP**) |

---

## 2. The flowgraph

```
  USRP Source, 2 MSPS          (or: File Source + Throttle — no radio)
        │
  Freq Xlating FIR Filter      pick the station, filter to 110 kHz, ÷8  → 250 kSPS
        │
        ├─────────────────────────────────┐
        ▼                                 ▼
  Quadrature Demod (by hand)        WBFM Receive ÷5 → 50 kSPS
  → MPX, 250 kSPS float                   │
        │                           Volume → Audio Sink   (so you can listen too)
        ├──▶ MPX spectrum display   ← see the pilot and the RDS hump
        ▼
  Freq Xlating FIR Filter  (float in, complex out)
  shift −57 kHz, filter to 2.4 kHz, ÷25  → 10 kSPS
        ▼
  AGC                      RDS is tiny; bring it up to a usable level
        ▼
  Symbol Sync              find the timing of each chip: 10,000 ÷ 2375 = 4.21 samples per chip
        ▼
  Costas Loop (order 2)    fix frequency and phase ──▶ Constellation display
        ▼
  Complex to Real          ──▶ chip plot
        ▼
  RDS Decoder (Embedded Python Block)
     chips → bits → undo differential → find blocks with the CRC → read the groups
        │                                                           │
        ▼                                                           ▼
  number of groups (display)                              the text, printed in the terminal
```

### Rates

| Between | Rate | Type | Contents |
|---|---|---|---|
| USRP → first filter | 2 MSPS | complex | ±1 MHz of the FM band |
| first filter → demod | 250 kSPS | complex | one FM station |
| demod → RDS filter | 250 kSPS | **float** | the whole MPX, 0–110 kHz |
| RDS filter → Symbol Sync | 10 kSPS | complex | RDS only, ±2.4 kHz |
| Symbol Sync → Costas | 2375 chips/s | complex | one sample per chip |
| decoded | 1187.5 bits/s | — | up to 11.4 groups per second |

> 💡 10,000 ÷ 2375 = 4.2105… is **not** a whole number. That is fine: Symbol Sync can handle a
> fractional number of samples per symbol. Don't bend your whole rate plan just to make it a
> whole number.

---

## 3. The interesting blocks

### Quadrature Demod — FM decoding by hand

Lab 01 used the WBFM Receive block. It cannot be used here, because it **removes everything
above 15 kHz** (and applies de-emphasis). That throws away the 57 kHz RDS signal. So we FM-decode
ourselves, with a Quadrature Demod block:

$$
\text{gain} = \frac{f_s}{2\pi\Delta f} = \frac{250000}{2\pi \times 75000} = 0.5305
$$

> **Rule:** use WBFM Receive when you want **sound**. Decode by hand when you want the **MPX**:
> stereo (Lab 04), RDS (here), or other subcarriers.

### The RDS filter — type `fcf`

A Frequency Xlating FIR Filter with type **`fcf`**: **f**loat in, **c**omplex out, **f**loat
taps. The MPX is a real (float) signal. Shifting it down by 57 kHz gives a complex (IQ) result.

| Setting | Value |
|---|---|
| Decimation | 25 (250 kSPS → 10 kSPS) |
| Taps | low-pass, cutoff 2.4 kHz, transition 800 Hz → about 753 taps |
| Center frequency | 57000 |

> ⚠️ Type `ccf` would expect a complex input — wrong, the MPX is float. Type `fff` would give a
> float output and lose the Q half. It must be `fcf`.

### Symbol Sync — at the **chip** rate

Because of biphase coding, each bit is two chips. So there are **2375 chips per second**, not
1187.5. Symbol Sync finds the timing of the **chips**. Turning pairs of chips into bits is the
decoder's job.

### The RDS Decoder — an Embedded Python Block

The heart of the lab. In GRC, right-click it → Properties to read the code. Four steps:

**1. Pair the chips into bits.** Each bit is two opposite chips (+− or −+). But which chips
belong together? Chips 0+1, 2+3, … or chips 1+2, 3+4, …? Test both: with the right pairing,
the two chips in every pair are opposite (their product is negative). With the wrong pairing,
it is random. Pick the pairing where the products are most negative. Then each bit is the sign
of (first chip − second chip).

**2. Undo the differential encoding.** bit = this ⊕ previous.

**3. Find the blocks with the CRC.** Slide a 26-bit window along. At each position, calculate
the CRC and compare with the offset words. Accept a group **only** when four blocks in a row
come out as A, B, C (or C′), D. The chance of that happening by accident is about 1 in 2⁴⁰ —
**a group that passes can be trusted.**

**4. Read the group.** Type 0: two station-name characters. Type 2: RadioText characters.
PI, PTY and TP from every group.

It prints to the terminal whenever the text changes:

```
[RDS] PI=0x4D01  PS='SDR LAB '  PTY=Pop Music  TP=1  groups=19
[RDS] RadioText: Hello from the SignalSDR Pro lab
```

It can also **repair itself**: if 20,000 chips (about 8 s) pass with no good group, it swaps the
chip pairing and starts again. This recovers from a timing slip.

---

## 4. Running the lab

### Step 1 — Test with a signal you know (no radio)

**Do this first**, before touching the radio. Make a test FM station with RDS content that you
choose:

```bash
cd 03_scripts
python3 simulate_rds_decode.py --seconds 8 --snr 30 \
        --ps "SDR LAB " --rt "Hello from the SignalSDR Pro lab" \
        --out /tmp/rds_test_2Msps_fc32.iq
```

Then run the file version of the flowgraph:

```bash
cd ../02_flowgraphs/lab08_rds_decoder
python3 lab08_rds_from_file.py
```

Within a few seconds the terminal should show:

```
[RDS] PI=0x4D01  PS='  R     '  PTY=Pop Music  TP=1  groups=0
[RDS] PI=0x4D01  PS='  R LA  '  PTY=Pop Music  TP=1  groups=1
[RDS] PI=0x4D01  PS='  R LAB '  PTY=Pop Music  TP=1  groups=2
[RDS] RadioText: Hell
...
[RDS] RadioText: Hello from the SignalSDR Pro lab
[RDS] PI=0x4D01  PS='SDR LAB '  PTY=Pop Music  TP=1  groups=19
```

**If this does not work, the problem is in the flowgraph, not your antenna** — and you can
debug it with a signal that never changes. (This is the Lab 05 lesson again.)

### Step 2 — Live, on a real station

```bash
gnuradio-companion lab08_rds_decoder.grc
```

1. Tune to the **strongest** station you can find. RDS needs roughly 25 dB SNR. Default gain
   is 45 dB.
2. Look at the **MPX** display. You should see the sound (0–15 kHz), the sharp **pilot** at
   19 kHz, the **stereo** hump around 38 kHz, and a small **RDS** hump at 57 kHz.

   > If you cannot see a hump at 57 kHz, the station may have no RDS, or be too weak. **Try
   > another station first**, before changing anything else. (But see the note in
   > Verification: a small hump can still decode.)

3. Look at the **RDS Constellation**. **Two tight dots** = locked. A **ring** = no carrier lock.
4. Watch the terminal. A strong station gives about 10 groups per second, and the name appears
   within a second or two.

> 💡 **Tip:** to avoid the centre spike (Lab 06), set **FM Station** 200 kHz *above* the station
> you want, and **Channel Offset** to −200 kHz.

---

## 5. Exercises

### Exercise 1 — Watch the name build up

The 8-character name arrives **2 characters at a time**, in 4 pieces, in any order:

```
PS='  R     '     ← piece 1 arrived first
PS='  R LA  '     ← piece 2
PS='  R LAB '     ← piece 3
PS='SDR LAB '     ← piece 0 completes it
```

This is why a car radio sometimes shows a half-finished name just after you tune.

### Exercise 2 — Find the "cliff"

Make test files with less and less signal, and count the groups each time:

```bash
cd "02_flowgraphs/lab08_rds_decoder"
for snr in 30 20 15 12 10 8; do
  python3 ../../03_scripts/simulate_rds_decode.py --seconds 6 --snr $snr \
          --out /tmp/rds_test_2Msps_fc32.iq --quiet
  echo -n "SNR ${snr} dB: "
  QT_QPA_PLATFORM=offscreen timeout 20 python3 lab08_rds_from_file.py 2>/dev/null \
          | grep -o 'groups=[0-9]*' | tail -1
done
```

You will find a sudden threshold, like the BER cliff in Lab 07. Below it you get **nothing** —
not wrong text. The CRC rejects every damaged group. **A link that fails silently is much
better than one that shows rubbish.**

### Exercise 3 — Prove the CRC is doing its job

In the decoder block, weaken the test so that only block A must match:

```python
if s[0] == 'A':          # instead of: s[0]=='A' and s[1]=='B' and ...
```

Run it on a weak signal. Now rubbish names and nonsense text appear, because random matches get
through: a 1 in 2¹⁰ chance, instead of 1 in 2⁴⁰. **Put it back afterwards.**

### Exercise 4 — Read the PI code

The **PI** code identifies the station. Its first hex digit is a **country code**. The same
digit is shared by several countries, so RDS also sends an "extended country code" to tell them
apart. BFM 89.9 sends `0x6000`. Note the PI codes of your local stations: each station keeps
the same PI on all its transmitters.

### Exercise 5 — Add a new group type: the clock

Group **4A** carries the **time and date**, once a minute. Add this branch to `_group()` in the
decoder:

```python
elif gtype == 4 and not version_b:
    mjd = ((b & 0x3) << 15) | (c >> 1)
    hour = ((c & 0x1) << 4) | (d >> 12)
    minute = (d >> 6) & 0x3F
    offset = (d & 0x1F) * (-30 if (d >> 5) & 1 else 30)   # minutes
    print(f"[RDS] Clock: MJD {mjd}  {hour:02d}:{minute:02d} UTC  offset {offset:+d} min")
```

Then wait a minute (if the station sends group 4A). You have set a clock over the radio.

---

## 🔬 Verification

### On real radio

`lab08_rds_from_file.grc` was run on a live recording from a SignalSDR Pro (B210 mode, built-in
GPS clock), tuned 200 kHz beside **BFM 89.9 MHz**, 2 MSPS, gain 62 dB:

```
valid groups: 287   failed alignments: 8040
group types: {0: 287}
PI codes   : {'0x6000': 287}

  t(s)  grp  seg  chars
  0.00    0    0  'BU'
  0.00    0    1  'SI'
  0.00    0    2  'NE'
  0.00    0    3  'SS'          -> "BUSINESS"
  0.16    0    0  'BF'
  0.24    0    1  'M '
  0.33    0    2  '89'
  0.42    0    3  '.9'          -> "BFM 89.9"
  1.65    0    1  'NA'
  1.73    0    2  'NC'
  1.82    0    3  'E '
  1.91    0    0  'FI'          -> "FINANCE "
```

287 groups in 30 s = **9.6 per second**, out of a maximum of 11.4: **84 %**, on a real
broadcast. The PI code was `0x6000` in every group.

**The station scrolls its name.** BFM changes its 8 characters every few seconds
("BFM 89.9", "BUSINESS", "FINANCE "), so the name never settles. That is the station, not a
decoder fault: the pieces arrive in order 0→1→2→3, and each set makes a real word.

### The control test

Same flowgraph, same gain, on an **empty** channel (104.0 MHz):

| Recording | Tries | Good groups |
|---|---|---|
| BFM 89.9 MHz (10 s) | 9,164 | **25** |
| empty 104.0 MHz | 11,766 | **0** |

Zero false groups from pure noise, in almost 12,000 tries. The CRC check is working.

> ⚠️ **A lesson from testing.** Before running the decoder, we looked at the spectrum at 57 kHz
> to see which stations had RDS. On this very station, the RDS hump was only **1.9 dB** above
> the noise, and we wrongly decided "no RDS here". RDS is so quiet that it hardly shows on a
> spectrum, yet it decodes perfectly. **Trust the CRC, not your eyes.** To find out if a
> station has RDS, run the decoder.

Of five stations tested at this location, only 89.9 MHz gave RDS groups. It only sends group
type 0, so **RadioText has not been tested on real radio.**

### With test signals

The file flowgraph, on a test signal with known content, decodes `PI=0x4D01`,
`PS='SDR LAB '`, `PTY=Pop Music` and the full RadioText. `03_scripts/test_labs_offline.py lab08`
checks this automatically. The RDS code itself (CRC, biphase, differential, group reading) is
tested by `simulate_rds_decode.py --selftest`.

---

## 🔧 Troubleshooting

| Problem | Cause and fix |
|---|---|
| No hump at 57 kHz on the MPX display | No RDS, or too weak. Try the strongest music station. Fix this first — nothing later can help |
| A hump at 57 kHz, but the constellation is a ring | No carrier lock. Lower `loop_bw` towards 0.005 (RDS is slow and steady, so narrow is better) |
| Constellation looks fine, but zero groups | Usually the chip pairing. The decoder swaps it by itself after ~8 s. If it keeps swapping, the signal is too noisy |
| Groups decode, but the name keeps changing | Probably the station scrolls its name (as BFM does). Check the pieces arrive 0→1→2→3 and make real words. If they are random fragments, you weakened the CRC test (Exercise 3) |
| It worked yesterday, today nothing | Check the station first. Stations can switch RDS off |
| The audio stutters | The RDS chain and the audio chain share the CPU. Disable the waterfall and constellation displays |
| Type error on the RDS filter | It must be type `fcf` (float in, complex out) |

---

## ✅ Summary

- RDS is a quiet digital signal at **57 kHz** in the MPX: **1187.5 bits/s**, up to 11.4 groups
  per second.
- Use WBFM Receive for **sound**; decode FM **by hand** when you need the MPX.
- `fcf` = float in, complex out: for shifting a real signal down to IQ.
- Biphase coding makes **2 chips per bit**. Symbol Sync works on chips.
- A **CRC with offset words** finds where blocks start *and* checks them — with no extra bits.
- **Test with a known signal first.** Then go on air.

## 🧠 Check yourself

1. Why can't we use the WBFM Receive block here?
   <details><summary>Answer</summary>It removes everything above 15 kHz, including RDS at
   57 kHz.</details>
2. How many chips per second does RDS send, and why?
   <details><summary>Answer</summary>2375: each of the 1187.5 bits is sent as two opposite
   chips (biphase coding).</details>
3. How does the receiver find where a block starts, with no start marker?
   <details><summary>Answer</summary>It slides along and does the CRC at each position. Only
   at the right position does the result equal one of the offset words (A, B, C, C′, D).</details>
4. A 16-bit start marker in every group would cost how much of the channel?
   <details><summary>Answer</summary>16 × 11.4 = 182 bits/s out of 1187.5 — over 15 %. The
   offset-word trick costs nothing.</details>
5. A station sounds perfect, but RDS will not decode. Why might that be?
   <details><summary>Answer</summary>RDS is sent at only 2–4 % of the FM swing, so it needs a
   much stronger signal (about 25 dB SNR) than the sound does.</details>

**Next:** [Lab 09 — Track Aircraft (ADS-B) →](../lab09_adsb_receiver/README.md). A new band
(1090 MHz), a new kind of modulation (pulses), and a stronger CRC — with the same skills.

---

## 📖 References

1. IEC 62106 — the RDS standard
2. [RDS Forum](https://www.rds.org.uk/)
3. [Radio Data System](https://en.wikipedia.org/wiki/Radio_Data_System) (Wikipedia), including
   the PI country-code tables
4. [gr-rds](https://github.com/bastibl/gr-rds) — a complete GNU Radio RDS decoder by Bastian
   Bloessl. Worth reading after this lab
