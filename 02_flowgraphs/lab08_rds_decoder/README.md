# 📡 Lab 08 — RDS Decoder: Reading Data Off the FM Broadcast Band

> **Time:** 3 hours
> **Difficulty:** Expert
> **Theory needed:** [Fund. 08 Digital Modulation](../../01_fundamentals/08_digital_modulation.md) · [Fund. 09 Synchronization](../../01_fundamentals/09_synchronization.md) · [Fund. 10 Error Detection & Framing](../../01_fundamentals/10_error_detection_and_framing.md)
> **Prerequisite lab:** [Lab 07](../lab07_bpsk_link_sim/README.md) — you need to have seen a digital receiver work in the clean room first
> **New blocks:** Quadrature Demod (manual), Frequency Xlating FIR `fcf`, Embedded Python Block (RDS Decoder)
> **Flowgraphs:** two — `lab08_rds_decoder.grc` (live) and `lab08_rds_from_file.grc` (offline)
> **Blocks in flowgraph:** 34

---

## 🎯 Goal

Extract the **station name and RadioText** from an ordinary FM broadcast — data that has been
sitting in every signal you have received since Lab 01, hidden at 57 kHz inside the MPX
baseband, and which you have been silently discarding.

This is the lab where all ten fundamentals meet. To read those eight characters you need:

| Fundamental | Used for |
|---|---|
| 02 IQ Sampling | the complex baseband |
| 04 FM Theory | quadrature demodulation to MPX |
| 05 Sampling & Filters | three cascaded channel filters, exact rate planning |
| 06 Noise & SNR | why RDS needs a strong station |
| 07 AM/NBFM | DSB-SC — RDS is suppressed-carrier, like the L−R subcarrier |
| 08 Digital Modulation | differentially encoded BPSK, biphase coding |
| 09 Synchronization | Gardner timing recovery, Costas carrier recovery |
| 10 CRC & Framing | the self-synchronising CRC that finds the block boundaries |

Nothing is left over. That is why this is the last analog-radio lab.

> **This lab has been verified.** The flowgraph was run against a synthetic FM+RDS capture with
> known contents and recovered `PI=0x4D01`, `PS='SDR LAB '`, `PTY=Pop Music` and the full
> RadioText — 90 CRC-valid groups from 8 seconds of signal, against a theoretical maximum of
> ~91. See [Verification](#-verification).

---

## 📖 Background: What RDS Is

RDS (Radio Data System; RBDS in North America) was standardised in 1984 and is in essentially
every FM broadcast worldwide. It carries the station name on your car radio's display, the
"traffic announcement" interrupt, the alternative-frequency list your radio uses to follow a
station as you drive, and the song title scrolling past.

### Where it lives

```
 MPX baseband after FM demodulation (0 - 100 kHz)

  power
    │  ███████████                                       ← L+R mono (0-15 kHz)
    │                  ▌                                 ← 19 kHz pilot
    │                      ▄▄▄▄▄▄▄▄▄▄▄▄▄                 ← L-R stereo, DSB-SC at 38 kHz
    │                                      ▂▂▂▂▂         ← RDS, DSB-SC at 57 kHz
    └──┬─────────┬────┬───┬───────────┬────┬───┬───────  kHz
       0        15   19  23          53   57  60
```

**Everything in that picture is locked to one 19 kHz reference:**

$$
f_{\text{stereo}} = 2 \times 19\,\text{kHz} = 38\,\text{kHz}, \qquad
f_{\text{RDS}} = 3 \times 19\,\text{kHz} = 57\,\text{kHz}
$$

$$
R_b = \frac{57000}{48} = 1187.5 \text{ bit/s}
$$

Even the *bit rate* is a division of the subcarrier. This coherence is not decoration — it
means a receiver that has recovered the pilot has recovered everything. (We take a shortcut and
mix with a fixed 57 kHz oscillator plus a Costas loop, which works because our sample-clock
error is only a few ppm — see the Questions section.)

### How the bits are carried

Three layers, each solving a specific problem:

```
   data bits (1187.5 bit/s)
        │
        ▼  differential encoding      d[n] = d[n-1] XOR b[n]
   solves: the Costas loop's 180 degree phase ambiguity
        │
        ▼  biphase (Manchester) coding   1 bit -> 2 opposite chips
   solves: puts a spectral NULL at the subcarrier frequency, so RDS
           does not interfere with the stereo decoder, and guarantees
           a transition every bit for timing recovery
        │
        ▼  100% cosine roll-off shaping
   solves: keeps the whole thing inside 57 kHz +/- 2.4 kHz
        │
        ▼  DSB-SC amplitude modulation onto 57 kHz
   at only ~2-4% of peak deviation - RDS is a very quiet guest
```

That last point is why RDS needs a strong signal: the subcarrier is tiny compared with the
audio, so a station that sounds perfect can still be far too weak to decode.

### The block and group structure

```
  ┌──────────────────── GROUP = 104 bits = 87.6 ms ────────────────────┐
  │  Block A  │  Block B  │  Block C  │  Block D  │
  │  26 bits  │  26 bits  │  26 bits  │  26 bits  │
  └───────────┴───────────┴───────────┴───────────┘
       │
       └─▶  ┌── 16 information bits ──┬── 10 check bits ──┐
            │                          │  CRC-10 XOR offset│
            └──────────────────────────┴───────────────────┘
```

**There is no preamble and no sync word.** Synchronisation comes from the CRC itself, using the
trick from [Fundamentals 10](../../01_fundamentals/10_error_detection_and_framing.md): each
block's checkword is the CRC **XOR a block-specific offset word**. Because the code is cyclic,

$$
\text{syndrome}(r) = r(x) \bmod g(x) = \text{offset}_X
$$

so computing one syndrome tells you **both** that the alignment is right **and** which of the
four blocks you are looking at. Sync and identification, at zero overhead. It is a genuinely
elegant design.

| | |
|---|---|
| Generator | $g(x) = x^{10}+x^8+x^7+x^5+x^4+x^3+1$ = `0b10110111001` = `0x5B9` |
| Offset A | `0011111100` |
| Offset B | `0110011000` |
| Offset C | `0101101000` |
| Offset C′ | `1101010000` |
| Offset D | `0110110100` |

### The groups we decode

| Group | Carries | Our use |
|---|---|---|
| **0A / 0B** | 2 characters of the 8-char Programme Service name | Station name |
| **2A** | 4 characters of the 64-char RadioText | Song / programme info |
| 2B | 2 characters of a 32-char RadioText | Same, shorter variant |
| Block A (always) | PI code — a unique station identifier | Country + station |
| Block B (always) | PTY (programme type), TP (traffic programme) | Genre |

---

## 📐 Architecture

```
  USRP Source 2 MSPS                (or File Source + Throttle — no hardware)
        │
        ▼
  ┌──────────────────────┐
  │ Freq Xlating FIR ccf │  mix -offset, LPF 110 kHz, decim 8
  └──────────┬───────────┘  → 250 kSPS complex
             │
     ┌───────┴────────────────────────────────┐
     ▼                                        ▼
 ┌───────────────┐                    ┌─────────────────┐
 │ Quadrature    │  gain = fs/(2πΔf)  │ WBFM Receive    │  audio_decim 5
 │ Demod         │  = 0.5305          │ (monitoring)    │  → 50 kSPS
 └───────┬───────┘                    └────────┬────────┘
         │ MPX, float, 250 kSPS                ▼
         ├──────────▶ Freq Sink  ← SEE the pilot and the RDS hump
         │                                Volume → Audio Sink
         ▼
 ┌──────────────────────┐
 │ Freq Xlating FIR fcf │  FLOAT in, COMPLEX out
 │ mix −57 kHz          │  LPF 2.4 kHz, decim 25
 └──────────┬───────────┘  → 10 kSPS complex
            ▼
 ┌──────────────┐   the subcarrier is only a few % of the MPX
 │ AGC2         │
 └──────┬───────┘
        ▼
 ┌──────────────────────┐
 │ Symbol Sync (cc)     │  Gardner TED, sps = 10000/2375 = 4.2105
 │ + PFB matched filter │  → 2375 chips/s
 └──────────┬───────────┘
            ▼
 ┌──────────────┐
 │ Costas order 2│────────▶ Constellation Sink   ← two dots = decodable
 └──────┬───────┘
        ▼
 ┌──────────────┐
 │ Complex→Real │────────▶ Time Sink (chips)
 └──────┬───────┘
        ▼
 ┌────────────────────────────────────────────────┐
 │ RDS Decoder  (Embedded Python Block)           │
 │   biphase pair → differential decode →         │───▶ Number Sink (group count)
 │   CRC block sync → group parse → PS + RT       │───▶ terminal output
 └────────────────────────────────────────────────┘
```

### Rate table

| Wire | Rate | Type | Contents |
|---|---|---|---|
| USRP → xlating | 2 MSPS | complex | ±1 MHz of band |
| xlating → quad demod | 250 kSPS | complex | one FM channel |
| quad demod → RDS xlating | 250 kSPS | **float** | the whole MPX, 0–110 kHz |
| RDS xlating → sync | 10 kSPS | complex | RDS baseband, ±2.4 kHz |
| Symbol Sync → Costas | 2375 chips/s | complex | one sample per chip |
| decoder input | 2375 chips/s | float | ±1 chips |
| decoded | 1187.5 bit/s | — | 11.4 groups/second |

$250000/25 = 10000$, and $10000/2375 = 4.2105\ldots$ — **not an integer, and that is fine.**
Symbol Sync's `sps` is a real number; the polyphase interpolator handles fractional rates by
construction. Insisting on integer `sps` here would force an awkward front-end sample rate for
no benefit.

---

## 📋 The Interesting Blocks

### `quad_demod` — Quadrature Demod, by hand

Lab 01 used the `WBFM Receive` black box. Here we need the **raw MPX**, before de-emphasis and
before the 15 kHz audio filter — both of which would destroy the 57 kHz subcarrier. So we do FM
demodulation ourselves:

$$
y[n] = \text{gain} \cdot \arg\bigl(s[n]\,s^*[n-1]\bigr), \qquad
\text{gain} = \frac{f_s}{2\pi\Delta f} = \frac{250000}{2\pi \times 75000} = 0.5305
$$

> **This is the whole reason the lab needs a manual demodulator.** `WBFM Receive` is a
> convenience wrapper that throws away everything above 15 kHz. Any time you need the MPX —
> stereo (Lab 04), RDS (here), or SCA subcarriers — you must demodulate yourself.

### `rds_xlate` — Frequency Xlating FIR Filter, type `fcf`

The type matters and is easy to get wrong: **`fcf` = float input, complex output.** The MPX is
real; mixing a real signal down by 57 kHz produces a complex baseband. Using `ccf` here would
be a type error; using `fff` would throw away the quadrature component you need.

```
decim       = 25          250 kSPS → 10 kSPS
taps        = rds_taps    LPF 2.4 kHz cutoff, 800 Hz transition
center_freq = 57000
samp_rate   = 250000
```

$N = 53 \times 250{,}000/(22 \times 800) = 753$ taps — large, but evaluated only 10,000 times
a second because the block decimates. About 7.5 MMAC/s. Free, in practice.

### `sym_sync` — Symbol Sync at the **chip** rate

The subtlety that catches people: because of biphase coding there are **2375 chips per second,
not 1187.5**. Symbol Sync recovers *chip* timing. Turning chips into bits is the decoder
block's job.

`sps = rds_rate / chip_rate = 10000/2375 = 4.2105`. Gardner TED again, because it works before
carrier lock.

### `rds_decoder` — the Embedded Python Block

Open it in GRC (right-click → Properties) and read it; it is the heart of the lab. Four stages:

**1. Biphase pairing.** Each data bit is two chips of *opposite* sign. So we must decide whether
to pair `(c0,c1),(c2,c3),…` or `(c1,c2),(c3,c4),…`. The discriminator is beautifully simple:

$$
\text{score}(\varphi) = -\frac{1}{M}\sum_k c[2k+\varphi]\,c[2k+1+\varphi]
$$

For the **correct** pairing every product is negative, so the score is ≈ +1. For the wrong
pairing the pairs straddle bit boundaries and are equally likely to agree or disagree, so the
score is ≈ 0. A completely reliable one-bit decision.

Then $b = \operatorname{sign}(c_0 - c_1)$.

**2. Differential decode.** $b[n] = d[n] \oplus d[n-1]$ — cancels the Costas loop's 180°
ambiguity.

**3. CRC block synchronisation.** Slide a 26-bit window, compute the syndrome, compare against
the five offset words. Accept a group only when four consecutive 26-bit windows give
`A, B, C-or-C′, D` in order. That is a $2^{-40}$ false-alarm probability — **a group that
passes is a group you can trust.**

**4. Group parsing.** Type 0 → two PS characters at the segment address in block B. Type 2 →
four RadioText characters. PI, PTY and TP come from every group.

It prints to the terminal whenever the text changes:

```
[RDS] PI=0x4D01  PS='SDR LAB '  PTY=Pop Music  TP=1  groups=19
[RDS] RadioText: SignalSDR Pro Lab RDS test
```

There is also a self-healing path: if 20,000 chips go by with no valid group, it flips the
biphase pairing and resets. That recovers automatically from a cycle slip.

---

## 🧪 Running the Lab

### Step 1 — Prove it works, offline, against a known signal

Do this **first**, before touching the radio. Generate a synthetic FM broadcast whose RDS
content you already know:

```bash
cd 03_scripts
python3 simulate_rds_decode.py --seconds 8 --snr 30 --out /tmp/rds_test_2Msps_fc32.iq
```

Then run the file-based flowgraph:

```bash
cd ../02_flowgraphs/lab08_rds_decoder
python3 lab08_rds_from_file.py
```

Within a couple of seconds the terminal should print the station name and RadioText the
generator put in. **If this does not work, nothing is wrong with your antenna — something is
wrong with the flowgraph, and you can debug it deterministically.**

This is the Lab 05 lesson applied: never debug a decoder against a signal you do not control.

### Step 2 — Live, on a real station

```bash
gnuradio-companion lab08_rds_decoder.grc
```

1. Tune to the **strongest** station you can find. RDS needs roughly 25 dB SNR. A station that
   sounds fine may still be far too weak.
2. Look at the **MPX Baseband** display. This is the money shot:

```
   ████████                                        ← L+R audio, 0-15 kHz
              ▌                                    ← 19 kHz pilot (sharp spike)
                   ▄▄▄▄▄▄▄▄▄▄                      ← L-R stereo, 23-53 kHz
                              ▂▂▂▂                 ← RDS at 57 kHz
```

   **If you cannot see a hump at 57 kHz, this station has no RDS or is too weak.** Try another
   before changing anything else.

3. Check the **RDS Constellation**. Two tight dots means locked. A ring means no carrier lock.
4. Watch the terminal. A strong station produces ~11 groups/second and the PS name fills in
   within a second or two.

### Exercise 1 — Watch the PS name assemble

The 8-character name arrives **two characters at a time**, in four segments, and the segments
can arrive in any order. Watch the printout:

```
PS='  R     '     ← segment 1 arrived first
PS='  R LA  '     ← segment 2
PS='  R LAB '     ← segment 3
PS='SDR LAB '     ← segment 0 completed it
```

This is why car radios sometimes show a garbled name for a moment after you tune.

### Exercise 2 — Find the SNR cliff

Regenerate the test file at decreasing SNR and count the groups:

```bash
for snr in 30 20 15 12 10 8; do
  python3 03_scripts/simulate_rds_decode.py --seconds 6 --snr $snr \
        --out /tmp/rds_test_2Msps_fc32.iq --quiet
  echo -n "SNR ${snr} dB: "
  QT_QPA_PLATFORM=offscreen timeout 20 python3 \
        02_flowgraphs/lab08_rds_decoder/lab08_rds_from_file.py 2>/dev/null \
        | grep -o 'groups=[0-9]*' | tail -1
done
```

You will find a sharp threshold, exactly like the BER cliff in Lab 07 — and for the same
reason. Below it, the CRC rejects everything and you get *silence rather than garbage*. That is
the CRC doing its job: **a data link that fails safe is worth far more than one that fails
loudly.**

### Exercise 3 — Prove the CRC is really working

In the decoder block, change the group acceptance test to require only block A:

```python
if s[0] == 'A':          # instead of: s[0]=='A' and s[1]=='B' and ...
```

Run it on a weak signal. You will now see garbage PS names and nonsense RadioText, because
false syndrome matches sneak through at $2^{-10}$ instead of $2^{-40}$. Put it back.

### Exercise 4 — Read the PI code

The PI code identifies the station and its country. `0x4D01`: the top nibble is the country
code (`4` = Germany in the RDS tables, `E`/`F` ranges are used elsewhere), the rest identifies
the programme. Look up your local stations' PI codes and check them against
[the RDS country tables](https://en.wikipedia.org/wiki/Radio_Data_System).

### Exercise 5 — Add a new group type

Group **4A** carries **Clock Time and Date** — UTC plus a local offset, transmitted once a
minute. Add a branch to `_group()`:

```python
elif gtype == 4 and not version_b:
    mjd = ((b & 0x3) << 15) | (c >> 1)
    hour = ((c & 0x1) << 4) | (d >> 12)
    minute = (d >> 6) & 0x3F
    offset = (d & 0x1F) * (-30 if (d >> 5) & 1 else 30)   # minutes
    print(f"[RDS] Clock: MJD {mjd}  {hour:02d}:{minute:02d} UTC  offset {offset:+d} min")
```

Then wait a minute. You have just synchronised a clock over the radio.

---

## 🔬 Verification

The generated flowgraph was executed headlessly against a synthetic capture with known
contents (PI `0x4D01`, PS `SDR LAB `, RadioText `SignalSDR Pro Lab RDS test`, 30 dB SNR,
8 seconds):

```
$ QT_QPA_PLATFORM=offscreen python3 lab08_rds_from_file.py
[RDS] PI=0x4D01  PS='  R     '  PTY=Pop Music  TP=1  groups=0
[RDS] PI=0x4D01  PS='  R LA  '  PTY=Pop Music  TP=1  groups=1
[RDS] PI=0x4D01  PS='  R LAB '  PTY=Pop Music  TP=1  groups=2
[RDS] RadioText: SignalSDR Pro Lab RDS test
[RDS] PI=0x4D01  PS='SDR LAB '  PTY=Pop Music  TP=1  groups=19
groups: 90   (theoretical maximum for 8 s: 8 x 11.4 = 91)
```

Every field recovered correctly, and essentially every transmitted group passed CRC. The
codec itself is separately round-trip tested by `03_scripts/simulate_rds_decode.py --selftest`,
which checks the CRC syndromes for all five offset words, the biphase and differential codecs,
and the group parser.

---

## 🐛 Troubleshooting

### "No 57 kHz hump in the MPX display"
The station has no RDS, or the signal is too weak. Not all stations transmit it (community and
some talk stations often do not). Try the strongest music station you can find. **Fix this
before changing anything else** — nothing downstream can help.

### "I see the 57 kHz hump but the constellation is a ring"
No carrier lock. Reduce `loop_bw` toward 0.005; RDS is slow and steady, so narrow wins. Also
confirm the AGC is bringing the level up — the subcarrier is tiny.

### "Constellation looks fine but zero groups"
Almost always the **biphase pairing**. The decoder should flip it automatically after 20,000
chips (~8 s). If it oscillates between pairings, your chips are noisy — improve the signal.

### "Groups decode but the PS name is garbage"
Two possibilities: (a) you weakened the CRC acceptance test (see Exercise 3), or (b) the
station is transmitting a scrolling "dynamic PS", which some stations do to display song titles
in the 8-character field. That is not a bug — it is a (frowned-upon) broadcaster habit.

### "It worked yesterday and now decodes nothing"
Check the station first, not the code. RDS transmission is entirely at the broadcaster's
discretion and some stations turn it off outside certain hours.

### "The audio monitoring is stuttering"
The RDS chain and the audio chain compete for CPU. Right-click the waterfall/constellation
sinks → Disable, or raise their `update_time`.

### "`freq_xlating_fir_filter` type error on `rds_xlate`"
It must be **`fcf`** — float in, complex out. `ccf` expects a complex input; the MPX is real.

---

## ❓ Questions to Ponder

1. **Why is the RDS subcarrier at 57 kHz specifically?**
   It is $3 \times 19$ kHz, so it can be regenerated coherently from the stereo pilot with a
   simple frequency tripler — no separate reference needed. And biphase coding puts a spectral
   *null* exactly at 57 kHz, so RDS energy does not leak into the 23–53 kHz stereo band.

2. **We mix with a fixed 57 kHz oscillator rather than tripling the pilot. Why does that work?**
   FM demodulation preserves baseband frequencies exactly, scaled only by our sample-clock
   error. At 10 ppm, 57 kHz is off by 0.57 Hz — about 0.05 of a cycle over one 87.6 ms group.
   The Costas loop absorbs that trivially. On a very cheap SDR with a 50+ ppm drifting clock,
   pilot-locked regeneration becomes worth the extra blocks.

3. **Why biphase coding, when it doubles the bandwidth?**
   Three reasons at once: a spectral null at the subcarrier (no interference with stereo), a
   guaranteed transition every bit (so timing recovery never starves on a run of identical
   bits), and no DC content (so the DSB-SC modulator sees a zero-mean signal).

4. **The CRC finds the block boundaries. What would a preamble have cost?**
   RDS transmits 11.4 groups/second. A 16-bit sync word per group would cost
   $16 \times 11.4 = 182$ bit/s out of 1187.5 — over **15 % of the entire channel**. The
   offset-word trick costs zero bits.

5. **Why does RDS need a much stronger signal than the audio does?**
   The subcarrier is transmitted at only 2–4 % of peak deviation, so it sits ~30 dB below the
   audio. Combined with the stereo/high-frequency noise penalty from Fundamentals 06, RDS
   effectively needs 25 dB SNR where mono audio is fine at 12 dB.

6. **How would you decode the alternative-frequency list in group 0A block C?**
   Each byte is a frequency code: values 1–204 map to $87.5 + 0.1 \times n$ MHz; 224+ are
   special codes indicating list length. Decoding it would let your receiver automatically
   re-tune to the strongest transmitter for the same programme — which is exactly what a car
   radio does.

---

## 📚 Key Takeaways

- **Use `WBFM Receive` when you want audio; demodulate by hand when you want the MPX.** Every
  subcarrier — stereo, RDS, SCA — lives above the 15 kHz that the convenience block discards.
- **`fcf` is the type for real-in, complex-out frequency translation.** Real signal, complex
  baseband.
- **Symbol Sync's `sps` may be fractional.** Do not distort your rate plan to force an integer.
- **Biphase coding means the chip rate is twice the bit rate**, and the pairing decision is a
  separate, easy problem — solved with one sign test.
- **A CRC can do synchronisation as well as validation.** The RDS offset-word scheme gets block
  sync, block identification and error detection from one 10-bit field.
- **Develop against a known signal.** The synthetic generator turned an "is my antenna bad or
  my code bad?" problem into a deterministic test.

---

## 🚀 What's Next?

Lab 09 leaves the broadcast band entirely: **ADS-B at 1090 MHz**, where aircraft broadcast
their identity, altitude and position twice a second in 1 Mbit/s pulse-position modulation with
a 24-bit CRC. Different frequency, different modulation, different framing — and every skill
from this lab carries straight over.

**Next:** [Lab 09 — ADS-B Aircraft Receiver →](../lab09_adsb_receiver/README.md)

---

## 📖 References

1. IEC 62106 — *Radio data system (RDS) specification* (the normative document)
2. [RDS Forum](https://www.rds.org.uk/) — the standard's custodians
3. Wikipedia: [Radio Data System](https://en.wikipedia.org/wiki/Radio_Data_System) — including the PI country-code tables
4. [gr-rds](https://github.com/bastibl/gr-rds) — Bastian Bloessl's production GNU Radio RDS decoder, worth reading after this lab
