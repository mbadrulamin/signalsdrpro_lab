# 🧩 Fundamentals 10 — Error Detection, Framing and CRC

> **What you will learn:** how a receiver knows data arrived **correctly** (the **CRC**), how it
> finds **where a message starts** (framing), the two CRCs used in Labs 08 and 09, and how
> error-**correcting** codes go further.
> **Before this:** [Fundamentals 08](./08_digital_modulation.md) and
> [09](./09_synchronization.md).
> **Time:** about 45 minutes. **Used by:** Lab 08 (RDS), Lab 09 (ADS-B).

---

## Why this chapter exists

Labs 08 and 09 decode real data from the air. In both, before you can trust the result, you must
answer one question:

> *"Is this a real message — or did I just turn random noise into bits?"*

In both labs, the answer is a **CRC** (cyclic redundancy check). And in both, the CRC does
something clever beyond "pass / fail": RDS uses it to **find where blocks start**, and Mode S can
use it to **check which aircraft** sent the message. To understand those tricks, you first need
to know what a CRC is.

---

## Part 1 — Arithmetic with only 0 and 1

A CRC is a kind of **division**, done with a very simple arithmetic that has only two numbers,
0 and 1. (Mathematicians call it GF(2).)

| Operation | Rule | In code |
|---|---|---|
| Add | 0+0 = 0, 0+1 = 1, **1+1 = 0** | XOR |
| Subtract | the same as adding | XOR |
| Multiply | 1×1 = 1, anything else = 0 | AND |

**There is never a "carry".** Adding and subtracting are the same thing: XOR. That is why a CRC is
cheap enough for the smallest chips.

### Bits as polynomials

A string of bits can be written as a polynomial. `1011` means:

$$
1\cdot x^3 + 0\cdot x^2 + 1\cdot x + 1 = x^3 + x + 1
$$

Shifting left by one is the same as multiplying by *x*. Adding two of them is XOR.

---

## Part 2 — How a CRC works

### The recipe

Choose a fixed bit pattern called the **generator** — *r* + 1 bits long (degree *r*). Then:

1. Add *r* zeros to the end of the message.
2. **Divide** by the generator (using XOR instead of subtraction). Keep the **remainder** — *r*
   bits. That is the CRC.
3. Send the message with the CRC in place of the zeros.

The sent word is now **exactly divisible** by the generator. So the receiver divides everything it
received by the generator:

- remainder **zero** → no error found ✅
- remainder **not zero** → something was damaged ❌

An error can only slip through if the damage happens to be an exact multiple of the generator.
With a well-chosen generator, that is very unlikely.

### A worked example

Message `1101`, generator `1011` (*r* = 3):

```
Add 3 zeros:      1101000
Divide by 1011 — XOR it in wherever the leftmost remaining bit is 1:

  1101000
  1011···      ← XOR at position 0
  -------
  0110000
   1011··      ← XOR at position 1
  -------
  0011100
    1011·      ← XOR at position 2
  -------
  0001010
     1011      ← XOR at position 3
  -------
  0000001
       ↑↑↑
    remainder = 001
```

CRC = `001`. Send `1101001`. The receiver divides `1101001` by `1011` and gets **000**.

Check it:

```bash
python3 -c "
def crc(msg, gen):
    r = len(gen) - 1
    d = list(msg) + [0]*r
    for i in range(len(msg)):
        if d[i]:
            for j in range(len(gen)): d[i+j] ^= gen[j]
    return d[-r:]
print('crc  :', crc([1,1,0,1], [1,0,1,1]))
print('check:', crc([1,1,0,1,0,0,1], [1,0,1,1]))   # all zeros = valid"
```

✅ `crc  : [0, 0, 1]` and `check: [0, 0, 0]`.

### What a CRC always catches

For a good *r*-bit CRC:

| Damage | Caught? |
|---|---|
| any single wrong bit | ✅ always |
| any odd number of wrong bits | ✅ always (for most standard generators) |
| any run of up to *r* wrong bits in a row | ✅ always |
| random damage | ✅ except with a chance of 1 in 2^*r* |

For ADS-B's **24-bit** CRC, a random bad message passes with a chance of 1 in 2²⁴ — about 1 in
17 million. If noise causes 100 false starts every second, one bad message gets through about
**every two days**. That is rare enough for a hobby receiver — and it is why real ADS-B systems
also check that a new aircraft's messages make sense over time.

<details>
<summary><b>Going deeper:</b> a CRC in Python, the fast way</summary>

```python
def crc_remainder(bits, poly, r):
    """bits: list of 0/1 (message already followed by r zeros).
       poly: generator as an int, WITHOUT its top x^r bit.
       Returns the r-bit remainder as an int."""
    reg = 0
    for b in bits:
        top = (reg >> (r - 1)) & 1
        reg = ((reg << 1) | b) & ((1 << r) - 1)
        if top:
            reg ^= poly
    return reg
```
</details>

---

## Part 3 — Framing: where does a message start?

A CRC tells you if a block is intact. It does **not** tell you where the block **begins**. There
are three common solutions. Labs 08 and 09 use two different ones.

### Method 1 — a known start pattern (ADS-B, Lab 09)

Put a fixed, known pattern — a **preamble** — at the start of every message. The receiver slides
along the signal looking for it.

ADS-B uses **4 pulses** in the first 8 µs:

```
  µs: 0   0.5  1.0  1.5  2.0  2.5  3.0  3.5  4.0  4.5
      ██   __   ██   __   __   __   __   ██   __   ██
      ↑         ↑                        ↑         ↑
    pulses at 0, 1.0, 3.5 and 4.5 µs
```

The spacing is deliberately **uneven**. Shift it by one step and it no longer matches itself. That
is what makes a good start pattern — and why start patterns are never just `11111111`.

### Method 2 — let the CRC find the start (RDS, Lab 08)

RDS has **no start pattern at all**. Instead, each 26-bit block's check bits are the CRC **XOR a
special "offset word"**, a different one for each of the four blocks (A, B, C, D).

The receiver tries every bit position. At the **right** position, removing one of the known
offset words gives a valid CRC — and **which** offset word worked tells it **which** block it is
looking at. Finding the start and naming the block, with **no extra bits**. A beautiful design
from the 1980s.

### Method 3 — fixed time slots

Used by GSM, digital radio (DAB) and satellites. Everything arrives at exact, known times. Once a
receiver has locked on, it knows when every part comes. Very efficient, but it needs a strong
signal to lock on first.

---

## Part 4 — The two CRCs in this course

### RDS: a 10-bit CRC with offset words (Lab 08)

| Property | Value |
|---|---|
| Generator | $x^{10}+x^8+x^7+x^5+x^4+x^3+1$ = `0x5B9` |
| Data per block | 16 bits |
| Check bits | 10 bits |
| Block | 26 bits |
| Group | 4 blocks = 104 bits |
| Bit rate | 1187.5 bits/s (= 57,000 ÷ 48) |

The offset words:

| Block | Offset word |
|---|---|
| A | `0011111100` |
| B | `0110011000` |
| C | `0101101000` |
| C′ | `1101010000` |
| D | `0110110100` |

> 💡 **Why 1187.5 bits/s?** RDS sits at 57 kHz = 3 × the 19 kHz stereo pilot. The bit rate is
> 57,000 ÷ 48. Everything in the FM signal is locked to that one 19 kHz reference.

### ADS-B / Mode S: a 24-bit CRC (Lab 09)

| Property | Value |
|---|---|
| Generator | `0xFFF409` (degree 24) |
| Short messages (DF 0, 4, 5, 11) | 56 bits |
| Long messages (DF 17, 18, 20, 21) | 112 bits |
| Modulation | PPM, 1 Mbit/s |
| Frequency | 1090 MHz |

**A trick in Mode S:** for some message types, the CRC is **XORed with the aircraft's 24-bit
address**. A ground radar that asked a particular aircraft a question can then check both that
the answer is intact **and** who sent it — with no extra bits. For **ADS-B** (DF 17), the address
is sent openly and the CRC is plain, so a correct message gives **remainder zero**.

---

## Part 5 — Going further: correcting errors (FEC)

A CRC **finds** errors, but cannot **fix** them. When you cannot ask for the data again (a
broadcast, or a space probe), you need **FEC** — forward error correction. The transmitter adds
extra, carefully designed bits, so the receiver can **repair** some damage.

| Code | Extra bits | Can fix | Where you meet it |
|---|---|---|---|
| Hamming (7,4) | 75 % | 1 bit in every 7 | teaching, computer memory |
| Reed–Solomon (255,223) | 14 % | 16 bytes per block | CDs, DVB-T, Voyager |
| Convolutional, rate ½ | 100 % | many, with Viterbi decoding | GSM, satellites, Meteor LRPT |
| LDPC / Turbo | 10–100 % | almost the theoretical limit | 5G, Wi-Fi 6, **DVB-T2 (Lab 10)** |

**Coding gain:** a rate-½ convolutional code with good ("soft-decision") Viterbi decoding gives
about **5 dB** at a BER of 10⁻⁵ — the same results with about **one third** of the power. The
price is bandwidth (twice the bits) and delay.

**RDS and ADS-B use no FEC at all.** They use **repetition**: RDS sends the station name again and
again; aircraft send their position twice every second. When a message repeats forever,
"throw away bad ones and wait for the next" is a perfectly good strategy, and costs nothing.

---

## ✅ Summary

- In 0/1 arithmetic, adding and subtracting are both **XOR**, with no carries.
- A **CRC** is the remainder of dividing by a generator. Remainder **zero** at the receiver = no
  error found.
- An *r*-bit CRC lets random damage through with a chance of 1 in 2^*r*.
- **Framing** finds the start of a message: a start pattern (ADS-B), the CRC itself with offset
  words (RDS), or fixed time slots.
- **FEC** repairs errors, at the cost of extra bits. Lab 10's DVB-T2 uses LDPC and BCH.

## 🧠 Check yourself

1. Why is subtracting the same as adding in 0/1 arithmetic?
   <details><summary>Answer</summary>Because 1 + 1 = 0, every number is its own opposite. Both
   are XOR.</details>
2. What is the longest run of wrong bits a 10-bit CRC always catches?
   <details><summary>Answer</summary>10 bits in a row.</details>
3. Work out the 3-bit CRC of `1010` with generator `1011`.
   <details><summary>Answer</summary><code>1010000</code> ÷ <code>1011</code> → remainder
   <code>011</code>. (Check it with the snippet above.)</details>
4. How does an RDS receiver find where blocks start, with no start pattern?
   <details><summary>Answer</summary>It tries every position. Only at the right one does
   removing a known offset word leave a valid CRC — which also tells it which block it
   is.</details>
5. Why does Mode S XOR the CRC with the aircraft's address?
   <details><summary>Answer</summary>So the radar that asked can check both that the reply is
   intact and that it came from the aircraft it asked — with no extra bits.</details>
6. Your ADS-B decoder finds 5000 possible messages per second, and almost all fail the CRC. What
   is wrong?
   <details><summary>Answer</summary>Probably nothing. The CRC is rejecting noise, as designed.
   A generous detector finds more real aircraft (Lab 09). Only raise the threshold if the CPU
   cannot keep up.</details>

**Next:** [Lab 08 — RDS Decoder →](../02_flowgraphs/lab08_rds_decoder/README.md), then
[Fundamentals 11 — OFDM →](./11_ofdm_and_broadcast_systems.md)
