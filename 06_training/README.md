# 🎓 Training — 4-hour classroom session

Materials for delivering **Introduction to SDR** as a four-hour taught session to a
**beginner-to-intermediate** audience: people who have *used* radio as operators, but have
never seen an SDR, GNU Radio, or a SignalSDR Pro.

| File | What it is |
|---|---|
| [`intro_to_sdr.html`](./intro_to_sdr.html) | **The deck.** 63 slides, speaker notes built in. One file, no internet required. |
| [`SESSION_PLAN.md`](./SESSION_PLAN.md) | The design rationale, per-slide speaker notes, demo risk plan, and the cut order. Read this before you present. |

The two are kept in sync: every slide number and every per-slide timing in the plan matches
the deck exactly.

---

## Running the deck

Double-click the file, or:

```bash
xdg-open "06_training/intro_to_sdr.html"
```

It is a **single self-contained HTML file**. No reveal.js, no CDN, no fonts to fetch, no build
step — it runs from a USB stick on a machine that has never seen the internet, which is the
point. Venue wifi is never in the critical path.

### Keys

| Key | Does |
|---|---|
| <kbd>→</kbd> <kbd>space</kbd> | Next — advances one *reveal* at a time on stepped slides |
| <kbd>←</kbd> | Back |
| <kbd>S</kbd> | **Speaker view** — opens a second window for your laptop screen |
| <kbd>O</kbd> | Overview grid of all 63 slides — click any to jump |
| <kbd>F</kbd> | Fullscreen |
| <kbd>B</kbd> | Black the screen (during a live demo, so nobody reads ahead) |
| <kbd>T</kbd> | **Light theme** — insurance for a bright room with a weak projector |
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

1. **Read [`SESSION_PLAN.md`](./SESSION_PLAN.md)** — particularly §2 (teaching a mixed-level
   room), §6 (demo risk management) and §7 (why the transmit demo runs down a cable).
2. **Add your QR code.** Slides 6 and 62 have a placeholder. Generate one for wherever this
   repository lives and paste the image in.
3. **Print the handout cards** (§8 of the plan). The setup checklist is the artefact that
   outlives the session.
4. **Record a fallback for every live demo.** If a demo has not recovered in 30 seconds, switch
   to the recording and keep moving. Never debug in front of a classroom.
5. **Pre-flight in the actual room**, on the actual power and network, within an hour of
   starting — and **test the audio**, because half the demos are sound.

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
<aside class="notes"><p>What to say…</p></aside>
  <h2>Slide title</h2>
  …
</section>
```

- `data-seg` — the segment label shown top-left
- `data-min` — planned minutes, which drives the pacing indicator. **Keep it in sync with the
  plan**; the checked total is 235 minutes plus a 5-minute buffer.
- `data-key` — marks a never-cut slide with a ★ in the overview
- `.step` on any element makes it a reveal, shown one press at a time in document order

Diagrams are inline SVG using the deck's CSS variables (`var(--accent)`, `var(--hw)`, …), so
they follow the light/dark toggle automatically. The slide area is a fixed 1280×720 coordinate
space scaled to fit the display, so layout is identical on every projector.

> The entrance animation deliberately animates **transform only, never opacity** — a browser
> with a stalled animation clock must never be able to leave a slide invisible in front of an
> audience.

### Printing to PDF

Print from the browser (`Ctrl+P`). Every slide is forced visible and page-broken. Reveals do
not print in sequence — a stepped slide prints with all its steps shown.
