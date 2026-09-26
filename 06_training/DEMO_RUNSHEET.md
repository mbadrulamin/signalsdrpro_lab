# 🎬 Demo Run Sheet — every live moment, step by step

> **What this is:** the exact command, settings and fallback for every live demo in the deck.
> Print it, and keep it next to the laptop.
> **Before this:** read [`SESSION_PLAN.md`](./SESSION_PLAN.md) §6 (demo risk) and §7 (the
> transmit demo).
> **Time:** preparation takes about 90 minutes the day before, and 30 minutes on the day.

All commands start in the repository's top folder (`signalsdrpro_lab`) unless a line says `cd`.

---

## 1. The day before (about 90 minutes)

Do these on **the laptop you will present with**, with **the radio and antennas you will use**.

| ✔ | Task | How |
|---|---|---|
| ☐ | Check the setup | `uhd_find_devices`, then `uhd_usrp_probe`. Look for `Operating over USB 3` |
| ☐ | Check the labs without a radio | `cd 03_scripts && python3 test_labs_offline.py` — all nine say **PASS** (about a minute) |
| ☐ | Choose your FM stations | One **strong** station for Labs 01–03 and 06. One **music** station for Lab 04 (talk stations carry almost no stereo) |
| ☐ | Check the labs on the radio | `cd 03_scripts && python3 test_labs_live.py --station <your station> --empty <an empty frequency>` — everything says **PASS**. Receive only |
| ☐ | Find an RDS station | Run Lab 08 on your stations (§3, S48). Write down which one shows a name |
| ☐ | Check for aircraft | Lab 09 with a **1090 MHz antenna** by a window (§3, S49). If nothing in 5 minutes, plan on the test capture |
| ☐ | Make the Lab 05 recording | §3, S45. Copy it somewhere safe — it is your fallback for all the FM demos |
| ☐ | Make the TV stream | §3, S56. Then rehearse the whole cable demo once |
| ☐ | Make the test files | the RDS and ADS-B test captures (§3, S48 and S49) |
| ☐ | Record a fallback video of each live demo | a 30–60 s screen recording, one keystroke away |
| ☐ | Print | the handout cards ([`handout_cards.html`](./handout_cards.html), `Ctrl+P`, double-sided) and this sheet |

---

## 2. One hour before, in the room

1. **Power first, then data** (SESSION_PLAN S32): USB-C power → wait 30 s → USB 3.0 data cable.
   Then leave the radio powered all day.
2. `uhd_find_devices` — the radio answers.
3. Laptop: on mains power, sleep off, notifications off, terminal font large.
4. **Test the sound** from the back of the room. Half the demos are sound.
5. Open the deck (`06_training/intro_to_sdr.html`), press <kbd>S</kbd> for speaker view, and
   check the pop-up opened.
6. Run the waterfall for slide 1 (below) and leave it running.

---

## 3. Each demo

"**Room sees/hears**" is what should happen. If it has not happened after **30 seconds**, switch to
the fallback and keep going. (The one exception is S34, where the failure *is* the lesson.)

### S1 and S13 — the live waterfall

```bash
uhd_fft -f 98e6 -s 20e6 -g 40 -A TX/RX
```

- **Room sees:** the whole FM band (88–108 MHz) at once, with bright stripes for stations.
- A thin spike exactly in the middle is the radio's own leak, not a station. Someone may ask.
- **If it fails:** your fallback video.

### S33 — the radio answers

```bash
uhd_find_devices
uhd_usrp_probe
```

- **Room sees:** the serial number, then a long description. Scroll to **one** part only — the
  receive gain range or the sample rates.

### S34 — the failure, on purpose (★ never cut)

Tested: this changes nothing on the laptop.

```bash
mkdir -p /tmp/no_images
UHD_IMAGES_DIR=/tmp/no_images uhd_usrp_probe      # the error, on purpose
cd 00_setup && ./fix_uhd_version_conflict.sh      # checks every driver version (asks for your password)
uhd_usrp_probe                                    # works again
```

- **Room sees:** `Could not find path for image: usrp_b200_fw.hex`, or the newer wording
  `Could not find the image 'usrp_b200_fw.hex' in the image directory /tmp/no_images`. Same
  problem.
- **Say honestly what you did:** "I sent the driver to an empty folder. That is exactly what
  having two driver versions does."

### S38 — build Lab 01 live (★ never cut)

```bash
gnuradio-companion
```

Start from an empty canvas. Search each block with <kbd>Ctrl+F</kbd>.

| Block | Settings |
|---|---|
| **UHD: USRP Source** | Sample Rate `1e6` · Ch0 Center Freq `89.9e6` (your station) · Ch0 Gain `40` · Ch0 Antenna `TX/RX` · **Ch0 Bandwidth `1e6`** |
| **WBFM Receive** | Quadrature Rate `1e6` · Audio Decimation `20` |
| **Audio Sink** | Sample Rate `50000` |

Connect them left to right and press ▶.

- **Room hears:** the station.
- **If it fails:** open the finished file, `02_flowgraphs/lab01_simple_wbfm/lab01_simple_wbfm.grc`.

### S39 — break it on purpose

Rehearse all three. How they sound depends a little on your station and laptop.

| Change | Room hears | Put back |
|---|---|---|
| Audio Sink `50000` → `25000` | slow, deep, jumpy sound; `O` letters in the terminal | `50000` |
| Frequency → an empty spot (found in rehearsal) | a loud rushing hiss | your station |
| Gain → maximum, then `0` | overload / distortion, then the station sinking into hiss | `40` |

### S43 — Labs 02 and 03

```bash
gnuradio-companion 02_flowgraphs/lab02_enhanced_wbfm/lab02_enhanced_wbfm.grc
gnuradio-companion 02_flowgraphs/lab03_advanced_wbfm/lab03_advanced_wbfm.grc
```

- **Lab 02, room sees:** spectrum, waterfall, and the **FM Station** slider retuning while it plays.
- **Lab 03, room hears:** tune to your empty frequency — **silence**, because the squelch closed.
  Tune back — the station returns.
- **If Lab 03 hisses on the empty frequency:** raise the **Squelch (dB)** slider a little.

### S44 — Lab 04, stereo

```bash
gnuradio-companion 02_flowgraphs/lab04_stereo_wbfm/lab04_stereo_wbfm.grc
```

- Set the frequency to your **music** station, and RF gain to about **55**.
- **Room sees:** the 19 kHz pilot tone in the spectrum. **Room hears:** stereo (headphones or
  two speakers help).

### S45 — Lab 05, record once

Record the day before, not live — 10 seconds is 160 MB.

```bash
gnuradio-companion 02_flowgraphs/lab05_iq_record_playback/lab05_iq_record.grc      # set freq + gain, flip Record, Ctrl+C after 10 s
gnuradio-companion 02_flowgraphs/lab05_iq_record_playback/lab05_iq_playback.grc    # plays /tmp/capture_100M0_2Msps_fc32.iq
```

- In the room: **unplug the antenna in front of them**, then play the recording and move the
  **Offset from centre** slider between stations inside it.
- **Fallback, no radio at all:** `cd 03_scripts && python3 make_test_iq.py /tmp/capture_100M0_2Msps_fc32.iq --mono --seconds 10`
  (a test tone, not music).

### S46 — Lab 06, many modes

```bash
gnuradio-companion 02_flowgraphs/lab06_multimode_receiver/lab06_multimode_receiver.grc
```

- Set the frequency **0.2 MHz above** your station (for 89.9 MHz, use `90.1e6`). The channel
  offset is already −200 kHz.
- Choose the mode in the **Mode** box: AM, NBFM (narrow FM) or WBFM (wide FM). Only wide FM is
  sure to have a signal. Switch to the others to show the controls; do not promise a voice.

### S47 — Lab 07, digital (no radio)

```bash
gnuradio-companion 02_flowgraphs/lab07_bpsk_link_sim/lab07_bpsk_link_sim.grc
```

- **Room sees:** two tight dots. Lower the **Eb/N0** slider (less signal compared with the
  noise): the dots smear into clouds, and the error count in the terminal rises.

### S48 — Lab 08, RDS

```bash
gnuradio-companion 02_flowgraphs/lab08_rds_decoder/lab08_rds_decoder.grc
```

- Set the frequency **0.2 MHz below** the station, and the channel offset to `+200e3`. RF gain
  about 60.
- **Room sees:** `[RDS] ... PS='BFM 89.9'` (or your station's name) in the terminal.
- At the lab, only BFM 89.9 sent RDS, and only its name — no song titles.
- **Fallback (test signal):**

  ```bash
  cd 03_scripts
  python3 simulate_rds_decode.py --seconds 8 --snr 30 --ps "SDR LAB " \
          --rt "Hello from the SignalSDR Pro lab" --out /tmp/rds_test_2Msps_fc32.iq
  cd ../02_flowgraphs/lab08_rds_decoder && python3 lab08_rds_from_file.py
  ```

### S49 — Lab 09, aircraft

```bash
gnuradio-companion 02_flowgraphs/lab09_adsb_receiver/lab09_adsb_receiver.grc
```

- Needs a **1090 MHz antenna**. The FM whip heard nothing. No real aircraft has been decoded at
  the lab yet, so check in rehearsal.
- **Fallback (test capture) — say that it is a test:**

  ```bash
  cd 03_scripts
  python3 simulate_adsb_decode.py --seconds 2 --snr 20 --out /tmp/adsb_test_2Msps_fc32.iq
  cd ../02_flowgraphs/lab09_adsb_receiver && python3 lab09_adsb_from_file.py
  ```

### S55 — scan the TV band (receive only)

```bash
cd 03_scripts
python3 scan_tv_band.py --first 21 --last 48 --dwell 0.4
```

- About 40 seconds. **Room sees:** a table, one row per channel.
- **Fallback, no radio:** `python3 scan_tv_band.py --selftest` — it creates the false alarm from
  the slide on purpose, and shows the scanner refusing it.

### S56 — a picture, down a cable (🚨 transmits)

🚨 **Only into a cable. No antenna on either port.** TV channels are licensed spectrum.

1. Cable: **`TX/RX` → 40 dB attenuator → `RX2`**. (Lab 12's README allows 20–30 dB. In a room,
   start with 40: the transmitter has plenty of spare gain, and the receiver cannot be overloaded.)
2. The day before, make the stream:

   ```bash
   cd 02_flowgraphs/lab12_fullduplex_tv
   ../../03_scripts/make_video_ts.py ~/Videos/your_clip.mp4 /tmp/bintang.ts \
       --mode 16qam-2/3-1/32 --width 1280 --duration 300 --loop
   ```

3. In the room: `gnuradio-companion lab12_fullduplex_tv.grc`. It starts with the transmitter at
   **zero**. Raise `tx_gain`, then `tx_amplitude`, **slowly**, watching the MER.
4. **Room sees:** the MER readout rise above about 15 dB, the constellation become 16 tight dots,
   `[TV] LOCKED` in the terminal with zero continuity errors — and, a few seconds later, a separate
   video window titled **SDR LAB TV** opens by itself.
5. If the constellation becomes a smeared blob, the signal is too **strong**: lower `rx_gain`
   first, then `tx_gain`.

**How much attenuation?** Whatever you have, watch the receive **level** rather than the dB
printed on the attenuator. Aim for about **−10 to −20 dBFS**: that is where MER is best. Above
about −6 dBFS the receiver starts to overload and MER falls. If it will not lock even at TX gain
89, there is too much attenuation (or raise RX gain); if the level stays above −6 dBFS, there is
too little (lower RX gain first).

Measured on the real radio at the lab (26 September 2026, channel 31, `TX/RX` → `RX2` between two
short antennas a few centimetres apart — not a cable, so your numbers will differ):

| RX gain | TX gain | Level | MER | Result |
|---|---|---|---|---|
| 20 | 80 | — | 15.0 dB | 16.15 Mbit/s, 0 errors |
| 20 | 89 | −12.4 dBFS | 19.7–20.4 dB | 16.13 Mbit/s, 0 errors |
| 35 | 70 | −19.3 dBFS | 15.9 dB | clean |
| 35 | 80 | −6.6 dBFS | 18.7 dB | clean |
| 35 | 89 | −2.5 dBFS | 13.5 dB | at the edge: overload |

> ⚠️ **Rehearse this exact setup** with your own cable and attenuator — the numbers above depend
> on them.

---

## 4. If the radio behaves strangely

| Symptom | What it means | Do this |
|---|---|---|
| `No UHD Devices Found` | the radio is not answering | power-cycle: unplug **both** cables, wait, power first, wait 30 s, then data |
| Stations are weak, and gain below about 50 seems to change nothing | very little signal is reaching the radio, so the converter's own noise dominates | check the antenna is on the port the flowgraph uses (`TX/RX`), and is the right one for the band |
| The radio reports `LO: unlocked` | on this board the reading is **not reliable**: on 26 Sep 2026 it said "unlocked" while stations measured within 2 kHz and the stereo pilot at 19,000.0 Hz | ignore it. Judge by whether known stations appear at the right frequency |
| `O` letters stream in the terminal | the laptop cannot keep up | close the waterfall and other programs; mains power |
| Sound stutters, `aU` in the terminal | the sound card rate does not match | check the Audio Sink rate |

---

## ✅ Summary

- Prepare **the day before**, on the real laptop, radio and antennas.
- Every demo has a **fallback**. After 30 seconds, use it.
- Labs 08 and 09 depend on the outside world. **Check them** — and be honest when you use a test file.
- The TV demo transmits: **cable and attenuator only**, start at zero, and rehearse it.
