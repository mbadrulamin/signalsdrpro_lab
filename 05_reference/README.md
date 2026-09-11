# 📚 Part 5 — Reference

> Lookup material. Not meant to be read front to back — come here when you need something.
>
> [← Repository home](../README.md)

---

| # | Document | Use it when… |
|---|---|---|
| 01 | **[Glossary](./01_glossary.md)** | Any document throws an acronym at you. **202 terms**, plain English first |
| 02 | **[Signal Identification](./02_signal_identification.md)** | You see something on the waterfall and have no idea what it is |
| 03 | **[Antennas](./03_antennas.md)** | Always. This is the highest-value page here for a beginner |
| 04 | **[Malaysia](./04_malaysia.md)** | You are in Malaysia and need bands, law, licensing or local community |

---

## If you are brand new

Read these three things, in this order, and nothing else:

1. **[Your First 30 Minutes](../QUICKSTART.md)** — plug it in and hear a station today
2. **[The Twenty That Matter Most](./01_glossary.md#the-twenty-that-matter-most)** — the only
   jargon you need to start
3. **[What to build first](./03_antennas.md#9-what-to-build-first)** — 20 minutes and $3 will
   improve your results more than anything else you can do

Then go to [Introduction to SDR](../01_fundamentals/00_introduction_to_sdr.md).

---

## Quick answers

| Question | Answer | More |
|---|---|---|
| How long should my antenna be? | $75{,}000 / f_{\text{MHz}}$ mm for a quarter wave | [Antennas §2](./03_antennas.md#2-the-one-equation) |
| What does dB mean? | A power ratio. Power → 10·log₁₀, voltage → 20·log₁₀ | [Glossary](./01_glossary.md#the-twenty-that-matter-most) |
| Why is there a spike in the middle of my spectrum? | Your own LO leaking. Not a signal | [Signal ID §5](./02_signal_identification.md#5-things-that-are-not-signals) |
| More gain isn't helping — why? | If the noise floor rises 1:1 with gain, you are front-end limited | [Antennas §6](./03_antennas.md#6-do-i-need-an-amplifier) |
| What is that signal? | Measure its width first | [Signal ID §3](./02_signal_identification.md#3-the-identification-procedure) |
| Can I transmit? | Almost certainly not without a licence | [Malaysia §3](./04_malaysia.md#3-getting-licensed-to-transmit) |
| Why can't I tune to 7 MHz? | Your SDR starts at 70 MHz. HF needs an upconverter | [Introduction §3.2](../01_fundamentals/00_introduction_to_sdr.md#32-what-the-numbers-mean-in-practice) |

---

## The whole repository

```
  QUICKSTART.md       ← 30 minutes: plug in and hear something
  01_fundamentals/00  ← Introduction: what SDR is, the hardware, the tools
  00_setup/           ← install and verify
  01_fundamentals/    ← theory, 01-11
  02_flowgraphs/      ← Labs 01-10
  03_scripts/         ← validators and simulators
  04_applications/    ← 589 things to point it at
  05_reference/       ← you are here
```

---

[← Repository home](../README.md)
