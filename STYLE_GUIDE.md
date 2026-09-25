# ✍️ Writing Style Guide

> **Who this is for:** anyone who edits or adds a page to this repository.
> **Why it exists:** the reader is a beginner. Many readers also read English as a second
> language. Every page should be easy to read the first time.

---

## The reader

Picture one person when you write:

- They have used a radio before (a car radio, a walkie-talkie, maybe a ham rig).
- They have **never** used an SDR.
- They know a little school maths. They do not know signal processing.
- English may not be their first language.
- They are reading alone, with nobody to ask.

If this person would get stuck on a sentence, rewrite the sentence.

---

## Ten rules

### 1. Short sentences. One idea each.

| ❌ Hard | ✅ Easy |
|---|---|
| The AD9361 opens its baseband filter to 56 MHz if `bw0` is unset, and LO leakage then swamps the signal you actually wanted. | If you do not set `bw0`, the radio's filter opens to its widest setting (56 MHz). A lot of unwanted energy then gets in. It can drown out the station you want. |

Aim for **under 20 words** per sentence. Split anything longer.

### 2. Plain words.

| Instead of | Write |
|---|---|
| utilise, leverage | use |
| commence | start |
| prior to | before |
| in order to | to |
| subsequently | then, later |
| comprehensively | fully |
| egress / ingress | output / input |

### 3. No idioms or literary phrases.

They are hard to translate and often confusing.

| ❌ Avoid | ✅ Say instead |
|---|---|
| "The mode was welded into the metal." | "The mode was fixed when the radio was built." |
| "This will bite you." | "This causes a common problem." |
| "a margin in hand" | "a margin to spare" |
| "fight an antenna" | "set up an antenna" |
| "Honesty matters more than enthusiasm." | (delete — just state the limits) |

### 4. Define every term the first time you use it.

Use this pattern: **term** — plain meaning — (optional) why it matters.

> **Sample rate** — how many measurements per second the radio takes. More samples per second
> lets you see a wider slice of the radio spectrum.

If the term is in the [Glossary](./05_reference/01_glossary.md), you may also link to it.
Never assume the reader remembers a term from a different page.

### 5. Explain in words first, then maths.

Give the idea and an everyday picture first. Then the equation, if it is needed.
Long derivations go inside a collapsible **Going deeper** block:

```markdown
<details>
<summary><b>Going deeper:</b> where the 6.02 dB per bit comes from</summary>

...maths here...
</details>
```

A beginner must be able to skip every `Going deeper` block and still follow the page.

### 6. Every page has the same frame.

**At the top:**

```markdown
> **What you will learn:** one or two lines.
> **Before this:** links to the pages the reader should have read.
> **Time:** about N minutes.
```

**At the bottom:**

```markdown
## ✅ Summary
- 3 to 6 bullet points. The things to remember.

## 🧠 Check yourself
1. A question. <details><summary>Answer</summary>The answer.</details>

**Next:** [Page name →](link)
```

### 7. Say what the reader will see.

After every command, show the output they should get, or describe it.
After every "try this", say what should happen. Beginners cannot tell success from failure.

### 8. Numbers need meaning.

Do not just say "the SNR went from 34.6 dB to 53.2 dB". Say what that means:

> The audio got much cleaner. The hiss dropped by about 19 dB — roughly 80 times less noise
> power.

### 9. Be direct about warnings.

Use these three markers, and only these:

- 💡 **Tip:** helpful, optional.
- ⚠️ **Warning:** you may waste time or get a wrong result.
- 🚨 **Danger / legal:** you could break the law or damage equipment. Used only for
  transmitting and for hardware damage.

### 10. Keep the facts exactly right.

Simple does not mean vague. When you rewrite a sentence, keep every number, frequency,
parameter name and file path the same, unless you have checked that it was wrong.

---

## Words we use the same way everywhere

| Use | Not |
|---|---|
| SignalSDR Pro | SDR Pro, the Signalens, the board (mix) |
| sample rate | sampling frequency, samp rate (except in code) |
| flowgraph | flow graph, graph |
| block | module, node |
| gain | RF gain / volume (they are different — see Fundamentals 06) |
| antenna port `TX/RX` or `RX2` | antenna input, SMA 1 |
| IQ (or I/Q) | quadrature data, complex baseband (define it first if you use it) |

---

## A quick self-check before you commit

- [ ] Could a beginner read the first paragraph and know what the page is for?
- [ ] Is every term defined, or linked, the first time?
- [ ] Are sentences mostly under 20 words?
- [ ] Does every command show its expected output?
- [ ] Is there a Summary and a Check-yourself section?
- [ ] Did every number survive the rewrite unchanged?
