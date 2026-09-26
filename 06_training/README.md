# 🎓 Training — 4-hour classroom session

Materials for delivering **Introduction to SDR** as a four-hour taught session to a
**beginner-to-intermediate** audience: people who have *used* radio as operators, but have
never seen an SDR, GNU Radio, or a SignalSDR Pro.

| File | What it is |
|---|---|
| [`intro_to_sdr.html`](./intro_to_sdr.html) | **The deck.** 63 slides, speaker notes built in. One file, no internet required. |
| [`PRESENTER_NOTES.md`](./PRESENTER_NOTES.md) | **The full presenter notes for all 63 slides**, in full sentences: why each slide is there, words you can say, what to do, likely questions with answers, and background for you. The speaker view shows the same notes. **Start here.** |
| [`SESSION_PLAN.md`](./SESSION_PLAN.md) | The design rationale, a one-page run of show, the demo risk plan, and the cut order. Read this before you present. |
| [`DEMO_RUNSHEET.md`](./DEMO_RUNSHEET.md) | **Every live demo, step by step:** the exact command and settings, what the room should see or hear, and the fallback. Plus the day-before checklist. Print it. |
| [`handout_cards.html`](./handout_cards.html) | **The two handout cards, ready to print** (A4, double-sided): the setup card, and the 15 words used today. |

The two are kept in sync: every slide number and every per-slide timing in the plan matches
the deck exactly.

---

## Running the deck

Double-click the file, or:

```bash
xdg-open "06_training/intro_to_sdr.html"
```

It is **one HTML file with everything inside it**. It needs no internet, no extra downloads and no
installation — it runs from a USB stick on a computer that has never been online. So a bad venue
Wi-Fi cannot stop your talk.

### Keys

| Key | Does |
|---|---|
| <kbd>→</kbd> <kbd>space</kbd> | Next — advances one *reveal* at a time on stepped slides |
| <kbd>←</kbd> | Back |
| <kbd>S</kbd> | **Speaker view** — opens a second window for your laptop screen |
| <kbd>O</kbd> | Overview grid of all 63 slides — click any to jump |
| <kbd>F</kbd> | Fullscreen |
| <kbd>B</kbd> | Black the screen (during a live demo, so nobody reads ahead) |
| <kbd>T</kbd> | **Light theme** — for a bright room or a weak projector |
| <kbd>P</kbd> | Pause / resume the timer |
| <kbd>12</kbd> <kbd>enter</kbd> | Jump to slide 12 |
| <kbd>H</kbd> | Show / hide the key list |

### Speaker view

Press <kbd>S</kbd>, then drag that window to your laptop screen and fullscreen the deck on the
projector. It shows the notes for the current slide, the next slide's title, how many reveals
remain — and a **pacing indicator**.

The pacing indicator is the reason this deck has its own engine rather than using an
off-the-shelf one. Every slide carries its planned duration, so the speaker view can compare
elapsed time against where the plan says you should be and tell you *"6 min behind"* rather
than making you do the arithmetic while talking. In a four-hour session with a 5-minute
buffer, that is the difference between finishing on time and abandoning the last segment.

> If pressing <kbd>S</kbd> does nothing, the browser blocked the pop-up. Allow pop-ups for this
> file and press it again. **Test this before the session, not during it.**

---

## Before you present

1. **Read [`PRESENTER_NOTES.md`](./PRESENTER_NOTES.md) aloud once**, a few days before. It is the
   best rehearsal there is, and it gives you the background to answer questions calmly.
2. **Read [`SESSION_PLAN.md`](./SESSION_PLAN.md)** — particularly §2 (teaching a mixed-level
   room), §6 (demo risk management) and §7 (why the transmit demo runs down a cable).
3. **Work through [`DEMO_RUNSHEET.md`](./DEMO_RUNSHEET.md) §1 the day before.** It lists every
   check, recording and test file, with the commands.
4. **Print the handout cards** — open [`handout_cards.html`](./handout_cards.html) and press
   <kbd>Ctrl+P</kbd> (A4, double-sided, no margins or "default"). The setup card is the artefact
   that outlives the session. The QR code on the cards, slide 6 and the last slide points to
   `github.com/mbadrulamin/signalsdrpro_lab`; if you move the repository, replace it.
5. **Record a fallback for every live demo.** If a demo has not recovered in 30 seconds, switch
   to the recording and keep moving. Never debug in front of a classroom.
6. **Pre-flight in the actual room**, on the actual power and network, within an hour of
   starting — and **test the audio**, because half the demos are sound.
7. **Run `python3 03_scripts/test_labs_offline.py` the day before.** It checks the real lab
   flowgraphs against known answers in about a minute, with no radio. All nine should PASS.

### Shape of the day

| | Segment | Slides | Min |
|---|---|---|---|
| 1 | Why you are here | 1–6 | 15 |
| 2 | What a radio does, and what SDR changes | 7–15 | 30 |
| 3 | The two ideas you cannot skip | 16–23 | 25 |
| 4 | The hardware | 24–29 | 15 |
| ☕ | Break | 30 | 10 |
| 5 | Making it work, live, from cold | 31–36 | 25 |
| 6 | Your first flowgraph | 37–40 | 25 |
| ☕ | Break | 41 | 10 |
| 7 | What it can do — the lab tour | 42–51 | 40 |
| 8 | Transmitting: a television station | 52–58 | 25 |
| 9 | Where to go next | 59–63 | 15 |
| | **Buffer** | | **5** |

**Five slides are marked ★ in the overview and must not be cut:**
S9 (the line through the superhet), S20 (I and Q), S34 (the failure fixed live),
S38 (the live build), S60 (your first week). S57 is starred too — keep it unless you are
badly over. The cut order for everything else is §10 of the plan.

---

## Editing

Slides are plain `<section class="slide">` elements in document order. Each carries:

```html
<section class="slide" data-seg="3 · The two ideas" data-min="5" data-key="1">
<aside class="notes">…generated — do not edit here…</aside>
  <h2>Slide title</h2>
  …
</section>
```

- `data-seg` — the segment label shown top-left
- `data-min` — planned minutes, which drives the pacing indicator. **Keep it in sync with the
  plan**; the checked total is 235 minutes plus a 5-minute buffer.
- `data-key` — marks a never-cut slide with a ★ in the overview
- `.step` on any element makes it a reveal, shown one press at a time in document order

**Speaker notes are not edited in the deck.** Edit [`PRESENTER_NOTES.md`](./PRESENTER_NOTES.md)
(one `## S12 · Title (2 min)` section per slide), then copy them into the deck:

```bash
python3 03_scripts/sync_speaker_notes.py          # updates every <aside class="notes">
python3 03_scripts/sync_speaker_notes.py --check  # says whether the deck is up to date
```

If you add or remove a slide, add or remove its section in `PRESENTER_NOTES.md` and renumber.

Diagrams are inline SVG using the deck's CSS variables (`var(--accent)`, `var(--hw)`, …), so
they follow the light/dark toggle automatically. The slide area is a fixed 1280×720 coordinate
space scaled to fit the display, so layout is identical on every projector.

> The slide entrance animation only **moves** the slide; it never fades it in. So even if a
> browser's animation gets stuck, a slide can never be left invisible in front of an audience.

### Printing to PDF

Print from the browser (`Ctrl+P`). Every slide is forced visible and page-broken. Reveals do
not print in sequence — a stepped slide prints with all its steps shown.
