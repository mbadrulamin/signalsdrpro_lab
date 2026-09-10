# 🧩 Fundamentals 10 — Error Detection, Framing & CRC

> **Prerequisite:** Digital Modulation (08), Synchronization (09)
> **Time to read:** 45 minutes
> **Used by:** Lab 07 (RDS), Lab 09 (ADS-B)

---

## Why This Chapter Exists

Labs 07 and 09 both decode real data off the air. In both, the last step before you can
believe a byte is the same question:

> *"Is this actually a valid message, or did I just slice noise into 88 bits?"*

The answer in both cases is a **cyclic redundancy check**, and in both cases the CRC does
something subtler than "pass/fail" — RDS uses it to find the block boundaries in the first
place, and ADS-B uses it to recover the aircraft address. Neither trick makes sense without
understanding what a CRC *is*.

---

## Part 1 — Arithmetic in GF(2)

A CRC is polynomial division over the finite field with two elements, GF(2). The rules are
simpler than ordinary arithmetic, not harder:

| Operation | GF(2) rule | In code |
|---|---|---|
| Addition | $1 + 1 = 0$ | `XOR` |
| Subtraction | Same as addition | `XOR` |
| Multiplication | $1 \times 1 = 1$ | `AND` |

**There are no carries.** Addition and subtraction are the same operation. That is the whole
reason CRCs are cheap enough to put in a $0.20 chip.

### Bit strings as polynomials

The bit string $1011$ represents

$$
x^3 + x + 1
$$

Bit $i$ (counting from the right) is the coefficient of $x^i$. Multiplying by $x$ is a left
shift. Adding two polynomials is XOR.

---

## Part 2 — How a CRC Works

### The construction

Choose a **generator polynomial** $g(x)$ of degree $r$. To protect a message $m(x)$:

1. Shift the message left by $r$ bits: $m(x)\cdot x^r$.
2. Divide by $g(x)$ in GF(2); keep the remainder $c(x)$ — that is the CRC.
3. Transmit $t(x) = m(x)\cdot x^r + c(x)$.

Because we subtracted the remainder (and subtraction is XOR), the transmitted word is exactly
divisible:

$$
\boxed{t(x) \bmod g(x) = 0}
$$

The receiver divides the whole received word by $g(x)$. **Zero remainder means no detected
error.** If there is an error $e(x)$, the received word is $t(x) + e(x)$ and the remainder is
$e(x) \bmod g(x)$ — which is zero only if the error pattern happens to be a multiple of the
generator. Choosing $g(x)$ well makes that vanishingly unlikely.

### A worked example, by hand

Message $1101$, generator $g(x) = x^3 + x + 1 = 1011$ ($r = 3$).

```
Append 3 zeros:   1101000
Divide by 1011 (XOR wherever the leading bit is 1):

  1101000
  1011·····   ← XOR at position 0
  -------
  0110000
  ·1011····   ← XOR at position 1
  -------
  0011100
  ··1011···   ← XOR at position 2
  -------
  0001010
  ···1011··   ← XOR at position 3
  -------
  0000001
        ↑↑↑
     remainder = 001
```

CRC = `001`. Transmit `1101001`. The receiver divides `1101001` by `1011` and gets 0.

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
print('check:', crc([1,1,0,1,0,0,1], [1,0,1,1]))   # all zeros = valid
"
```

### What a CRC guarantees

For a well-chosen degree-$r$ generator:

| Error type | Detected? |
|---|---|
| Any single-bit error | ✅ Always |
| Any odd number of bit errors | ✅ Always, if $g(x)$ has $(x+1)$ as a factor |
| Any burst of $\le r$ consecutive bits | ✅ Always |
| Any two bits within the generator's period | ✅ Always |
| Random error pattern | ✅ with probability $1 - 2^{-r}$ |

A 24-bit CRC (ADS-B) lets a corrupted frame slip through with probability $2^{-24} \approx
6 \times 10^{-8}$. With ~100 frames/second of noise-triggered false preambles, that is one bad
frame every few months. Good enough to trust.

### Reference implementation

```python
def crc_remainder(bits, poly, r):
    """bits: list of 0/1 (message already zero-extended by r).
       poly: generator as an int, WITHOUT the leading x^r term.
       Returns the r-bit remainder as an int."""
    reg = 0
    for b in bits:
        top = (reg >> (r - 1)) & 1
        reg = ((reg << 1) | b) & ((1 << r) - 1)
        if top:
            reg ^= poly
    return reg
```

---

## Part 3 — Framing: Finding the Start of a Message

A CRC tells you whether a block is intact. It does not tell you **where the block begins**.
There are three families of solution, and this repo's two data labs use two different ones.

### Method 1 — Preamble correlation (ADS-B, Lab 09)

Prefix every frame with a fixed, known pattern with excellent autocorrelation. The receiver
slides a correlator along the stream:

$$
R[n] = \sum_{k=0}^{L-1} r[n+k]\, p^*[k]
$$

A peak in $|R[n]|$ marks the frame start.

Mode S / ADS-B uses a **4-pulse preamble** occupying 8 μs:

```
  µs: 0   0.5  1.0  1.5  2.0  2.5  3.0  3.5  4.0 ...
      ██   __   ██   __   __   __   __   ██   __   ██
      ↑         ↑                        ↑         ↑
    pulses at 0, 1.0, 3.5, 4.5 µs
```

The pattern is deliberately non-uniform so that a shifted copy correlates poorly with itself —
this is exactly what "good autocorrelation" means, and it is why sync words are not just
`11111111`.

### Method 2 — Self-synchronising CRC (RDS, Lab 07)

RDS has **no preamble at all**. Instead, each 26-bit block's checkword is the CRC **plus a
block-specific offset word**:

$$
c_{\text{transmitted}} = \bigl(m(x)\cdot x^{10} \bmod g(x)\bigr) \oplus \text{offset}_{A/B/C/D}
$$

The receiver tries every bit position. At the correct alignment, subtracting one of the four
known offsets yields a valid CRC — and *which* offset worked tells you which block of the
group you are looking at. **Synchronisation and block identification for free, with zero
overhead bits.** It is a genuinely beautiful piece of 1970s engineering.

### Method 3 — Fixed slots / TDMA

Used by GSM, DAB, and satellite links: a rigid frame structure where a receiver, once locked,
knows exactly when everything arrives. Highest efficiency, but it needs a strong initial
acquisition burst.

---

## Part 4 — The Two CRCs You Will Actually Implement

### RDS: CRC-10 with offset words

| Property | Value |
|---|---|
| Generator | $x^{10}+x^8+x^7+x^5+x^4+x^3+1$ = `0b10110111001` = `0x5B9` |
| Message | 16 bits |
| Check | 10 bits |
| Block | 26 bits |
| Group | 4 blocks = 104 bits |
| Bit rate | 1187.5 bit/s (= 57000 / 48) |

Offset words (added modulo 2 to the checkword):

| Block | Offset name | Value (binary) |
|---|---|---|
| A | offset A | `0011111100` |
| B | offset B | `0110011000` |
| C | offset C | `0101101000` |
| C′ | offset C′ | `1101010000` |
| D | offset D | `0110110100` |

> **Where does 1187.5 come from?** The RDS subcarrier is at 57 kHz — the third harmonic of the
> 19 kHz stereo pilot, so it can be regenerated from the pilot. The bit rate is
> $57000/48 = 1187.5$ bit/s, a clean integer division that keeps the data clock coherent with
> the subcarrier. Everything in the FM MPX spectrum is locked to that one 19 kHz reference.

### ADS-B / Mode S: CRC-24

| Property | Value |
|---|---|
| Generator | $\texttt{0xFFF409}$ (degree 24) |
| Short frame (DF 0/4/5/11) | 56 bits |
| Long frame (DF 17/18/20/21) | 112 bits |
| Modulation | PPM, 1 Mbit/s |
| Frequency | 1090 MHz |

Mode S plays a trick: for some downlink formats the CRC is **XORed with the aircraft's
24-bit ICAO address**. A ground station that knows which aircraft it interrogated can
therefore verify the frame *and* confirm the sender. For ADS-B (DF 17) the address is sent in
the clear and the CRC is plain — so a zero remainder is a genuine pass.

---

## Part 5 — Beyond Detection: Forward Error Correction

A CRC detects but does not repair. When retransmission is impossible (a broadcast, a deep
space probe), you need **FEC** — deliberately adding redundancy that lets the decoder *fix*
errors.

| Code | Overhead | Corrects | Where you have met it |
|---|---|---|---|
| Hamming(7,4) | 75 % | 1 bit per 7 | Teaching, ECC RAM |
| Reed–Solomon(255,223) | 14 % | 16 bytes per block | CDs, DVB, Voyager |
| Convolutional $r=1/2$, $K=7$ | 100 % | Soft-decision Viterbi | GSM, satellite, NOAA APT |
| LDPC / Turbo | 10–100 % | Near Shannon limit | 5G, DVB-S2, Wi-Fi 6 |

### Coding gain

FEC buys you $E_b/N_0$. A rate-1/2, $K=7$ convolutional code with soft-decision Viterbi
decoding gives roughly **5 dB** of coding gain at BER $10^{-5}$ — meaning you can transmit
with about one third the power. It costs bandwidth (twice as many channel bits) and latency.

$$
\text{Effective } \frac{E_b}{N_0} = \frac{E_b}{N_0}\Big|_{\text{channel}} + G_{\text{coding}} - 10\log_{10}\frac{1}{r}
$$

Neither RDS nor ADS-B uses FEC — both rely on **repetition** instead. RDS retransmits the
station name continuously; ADS-B retransmits position twice a second. When a message repeats
forever, "discard and wait" is a perfectly good error-correction strategy, and it costs
nothing to implement.

---

## 🧠 Self-Check

1. Why is GF(2) subtraction the same as addition?
   **Answer:** The field has two elements and $1+1=0$, so every element is its own additive
   inverse. Both operations are XOR.

2. What burst length does a 10-bit CRC always detect?
   **Answer:** Any burst of 10 or fewer consecutive erroneous bits.

3. Compute the CRC-3 of `1010` with $g = 1011$.
   **Answer:** `1010000` ÷ `1011` → remainder `011`. (Work it out by hand, then check it with
   the snippet above.)

4. How does an RDS receiver find block boundaries without a preamble?
   **Answer:** It tests every bit offset; at the true alignment, removing one of the five known
   offset words leaves a valid CRC — which simultaneously identifies the block type.

5. Why does Mode S XOR the CRC with the aircraft address?
   **Answer:** It authenticates the reply to the interrogator that expected it — a valid CRC
   after XORing the expected address proves both integrity and identity, at zero extra bits.

6. Your ADS-B decoder reports 5000 frames/s, almost all failing CRC. What is wrong?
   **Answer:** The preamble detector threshold is too low, so noise is triggering it. Raise
   the threshold — the CRC is doing its job by rejecting them.

---

**Next:** [Lab 08 — RDS Decoder →](../02_flowgraphs/lab08_rds_decoder/README.md)
