# 🎯 Client Briefing — SignalSDR Pro for End Users

> **What this folder is:** everything for a 2½-hour session that shows **end users** what the
> SignalSDR Pro is and what they can do with it. It was first built for a military client.
> **Who it is for:** the presenter. The audience sees only the deck, the demos and the handout.
> **How it differs from [the training course](../06_training/README.md):** no theory, no
> equations, and GNU Radio is never opened on screen. About 45 minutes of plain explanation,
> then 70 minutes of live demonstrations.

---

## What is in this folder

Read them in this order.

| # | File | What it is |
|---|---|---|
| 1 | [SESSION_PLAN.md](./SESSION_PLAN.md) | **Start here.** The run of show, the cut order, the risks, and what to do if the radio fails |
| 2 | [SETUP_CHECKLIST.md](./SETUP_CHECKLIST.md) | What to buy today, what to rehearse tonight, and the 10-minute smoke test |
| 3 | [DEMO_RUNSHEET.md](./DEMO_RUNSHEET.md) | **Print it.** The six demos: command, what the room sees, what to say, fallback, reset |
| 4 | [client_brief.html](./client_brief.html) | **The deck.** 35 slides, 150 minutes, speaker notes and a pace timer built in |
| 5 | [PRESENTER_SCRIPT.md](./PRESENTER_SCRIPT.md) | What to say on every slide, in full sentences. The deck's speaker view shows the same |
| 6 | [QA_MILITARY.md](./QA_MILITARY.md) | About 30 questions they will ask, with honest answers |
| 7 | [client_handout.html](./client_handout.html) | One A4 page to leave behind. Open it and print |
| — | [demo/](./demo/) | One script per demo, plus `preflight.sh` and `stop_all.sh` |
| — | [install_demo_tools.sh](./install_demo_tools.sh) | Optional: installs gqrx (and inspectrum with `--all`) |
| — | [fallbacks/](./fallbacks/) | Screen recordings of each demo working. **You make these at the rehearsal** |

---

## The session in one table

| Min | Block |
|---|---|
| 5 | Welcome |
| 18 | What software-defined radio is, in plain words |
| 12 | What the SignalSDR Pro is, and what it is not |
| 12 | Six things it can do for a military user, and the legal line |
| 10 | Break |
| 70 | Six live demonstrations (see below) |
| 8 | The software they would use, and DragonOS |
| 15 | What you may do with it, and questions |

| # | Demo | Command | Radio |
|---|---|---|---|
| 1 | See the invisible: the live spectrum | `./d1_spectrum.sh` | receive |
| 2 | Hidden data: a station's name from BFM 89.9 | `./d2_rds.sh` | receive |
| 3 | Tour the busy bands: FM, phones, Wi-Fi, TV | `./d3_bands.sh` | receive |
| 4 | Record now, analyse later: replay with no antenna | `./d4_replay.sh` | none |
| 5 | Noise against a signal | `./d5_bpsk.sh` | none |
| 6 | Television from this box to a real TV | `./d6_tv.sh` | 🚨 transmits |

---

## Quick start

```bash
cd "07_client_demo/demo"
./preflight.sh                       # checks everything; nothing transmits
xdg-open ../client_brief.html        # the deck: F for full screen, S for speaker view
```

The demo scripts keep their big files in `~/sdr_demo/`, because `/tmp` is emptied at every boot.
Each script copies what it needs back into `/tmp` before it runs. No lab flowgraph was changed
for this briefing.

🚨 **Danger / legal:** Demo 6 transmits on UHF channel 21 (474 MHz), a licensed TV channel. Use
the lowest power that works, keep it within a few metres in a controlled room, never leave it
running, and finish with `./stop_all.sh`. A cable and attenuators are better than antennas. See
[the legal summary](../05_reference/04_malaysia.md#8-the-short-legal-summary).

---

## Editing the deck

The words in the speaker view come from `PRESENTER_SCRIPT.md`. After changing that file, copy it
into the deck:

```bash
cd 03_scripts
python3 sync_speaker_notes.py --notes ../07_client_demo/PRESENTER_SCRIPT.md \
                              --deck  ../07_client_demo/client_brief.html
```

Add `--check` to see whether they match without changing anything.

---

## What is proven and what is not

| Part | Status |
|---|---|
| Demos 1, 2 and 3 | The same tools and settings were measured live at the lab in September 2026 |
| Demo 4 | Lab 05 record and playback are proven. The recording itself is made at the rehearsal |
| Demo 5 | A simulation; its error rate is checked against theory |
| Demo 6 | Lab 10's picture on a real DVB-T2 TV was confirmed by the lab owner on 26 Sep 2026 |
| Demo 6 fallback | Lab 12 locked with zero errors on the radio. Nobody has yet watched its video window live |
| gqrx | Not tested on this machine. Optional |
| The `demo/` scripts | Checked for errors and run without the radio. **Not yet run with the radio** — that is the rehearsal |

Full details: [VERIFICATION.md](../VERIFICATION.md).

---

## ✅ Summary

- A **2½-hour briefing for end users**: plain words first, then six live demonstrations.
- **Read in order:** session plan → setup checklist → run sheet → deck and script.
- **One command per demo**, from the `demo` folder. `./preflight.sh` first, `./stop_all.sh` last.
- **Rehearse with the radio** and record the fallbacks before the day.

**Next:** [The session plan →](./SESSION_PLAN.md)
