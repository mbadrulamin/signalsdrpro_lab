# 🌦️ 05 — Weather & Environment

> The natural world transmits too. Lightning, meteors, the ionosphere and the Sun all put energy
> into the spectrum, and some of the most interesting SDR projects involve receiving things
> nobody deliberately sent.
>
> [← Satellite & Space](./04_satellite_and_space.md) · [Catalogue index](./README.md) · [Next: Land Mobile →](./06_land_mobile_and_professional.md)

---

## Radiosondes — weather balloons you can chase

Twice a day, from roughly 800 sites worldwide, meteorological services launch balloons carrying
a small transmitter. It climbs to ~30 km, bursts, and falls. The payload transmits its **GPS
position** the whole way down — which means you can decode it, drive to where it lands, and keep
it. This is a genuinely popular hobby with an active community.

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Vaisala RS41** | 400–406 MHz | GFSK 4800 bit/s, Reed-Solomon | ⭐⭐⭐ | ✅ | 🟢 The most common type worldwide. `radiosonde_auto_rx` |
| **Vaisala RS92** | 400–406 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 Older, still flown in places |
| **Graw DFM-09/17** | 400–406 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 Common in Europe |
| **Meteomodem M10/M20** | 400–406 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 France and francophone regions |
| **iMet-4** | 400–406 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 |
| **Dropsondes** | 400–406 MHz | FSK | ⭐⭐⭐⭐ | ✅ | 🟢 Dropped *from* hurricane-hunter aircraft |
| **Ozonesondes / special payloads** | 400–406 MHz | varies | ⭐⭐⭐⭐ | ✅ | 🟢 Extra sensor channels in the telemetry |

**Why it is a great project:** the signal is strong (a balloon at 20 km is line-of-sight for
hundreds of km), the format is documented, the decoder exists, and there is a physical object at
the end of it. Your ¼-wave for 403 MHz is 186 mm.

---

## Atmospheric and natural phenomena

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Lightning sferics** | 3–30 kHz (VLF) | broadband impulse | ⭐⭐ | 🔻📡 | 🟢 Every stroke worldwide radiates here. A wire and a soundcard will do |
| **Whistlers** | 1–10 kHz | dispersed impulse | ⭐⭐⭐ | 🔻📡 | 🟢 Lightning energy that travelled along a magnetic field line and back. Audibly descending tones |
| **Chorus / dawn chorus** | VLF | natural emission | ⭐⭐⭐⭐ | 🔻📡 | 🟢 Magnetospheric plasma waves. Sounds like birdsong |
| **Schumann resonances** | 7.83, 14.3, 20.8 Hz | ELF | ⭐⭐⭐⭐⭐ | 🔻📡 | 🟢 The Earth-ionosphere cavity ringing. Extremely difficult |
| **Meteor scatter (forward)** | 30–70 MHz, 143.05 MHz | ping off ionised trails | ⭐⭐ | ✅📡 | 🟢 Listen to a distant beacon or radar and count the pings. **Works day or night, all year** |
| **Meteor scatter (GRAVES radar)** | 143.050 MHz | CW reflections | ⭐⭐ | ✅📡 | 🟢 French space-surveillance radar; the standard European meteor source |
| **Aurora scatter** | 6 m, 2 m amateur bands | distorted, "rasping" signals | ⭐⭐⭐ | ✅📡 | 🟢 Signals reflected off auroral ionisation |
| **Sporadic-E propagation** | 28–150 MHz | opens paths of 1000+ km | ⭐⭐ | ✅ | 🟢 Watch distant FM or TV appear in summer. **You can observe this with Lab 06** |
| **Tropospheric ducting** | VHF/UHF | long-range anomalous propagation | ⭐⭐ | ✅ | 🟢 Weather-driven. Distant stations appear for hours |

---

## Ionosphere and space weather

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Ionosondes (chirp sounders)** | 2–30 MHz sweeps | swept CW | ⭐⭐⭐ | 🔻📡 | 🟢 Government transmitters measuring ionospheric height. Visible as diagonal streaks on a waterfall |
| **NCDXF/IARU beacons** | 14.100, 18.110, 21.150, 24.930, 28.200 MHz | CW, 3-minute cycle | ⭐⭐ | 🔻📡 | 🟢 18 stations worldwide on a shared schedule. **A live propagation map** |
| **WWV propagation reports** | 2.5, 5, 10, 15, 20 MHz | AM voice + tones | ⭐ | 🔻📡 | 🟢 Space weather bulletins at 18 minutes past each hour |
| **Riometer (cosmic noise absorption)** | 30–50 MHz | broadband noise level | ⭐⭐⭐⭐ | ✅📡 | 🟢 Measure ionospheric absorption by watching galactic noise |
| **Solar radio bursts** | see [Science](./12_science_and_radio_astronomy.md) | | | | |
| **GNSS scintillation monitoring** | 1.5 GHz | phase/amplitude of GNSS | ⭐⭐⭐⭐⭐ | ✅📡🔊 | 🟢 Ionospheric turbulence measured through satellite signals |

---

## Terrestrial environmental sensing

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Weather station sensors** | 433.92, 868, 915 MHz | OOK/FSK, simple framing | ⭐⭐ | ✅ | 🟢 `rtl_433` knows hundreds of protocols. **The single best "first data decode" project** |
| **River and flood gauges** | VHF/UHF telemetry | FSK | ⭐⭐⭐ | ✅ | 🟡 Hydrological monitoring networks |
| **Seismic telemetry** | VHF | FM subcarrier or digital | ⭐⭐⭐⭐ | ✅ | 🟡 Remote seismometers reporting home |
| **Wildlife / animal tracking collars** | 148–152, 216 MHz | pulsed CW | ⭐⭐ | ✅📡 | 🟡 Simple beeps; direction finding to locate |
| **Argos satellite tags** | 401.65 MHz | PSK bursts | ⭐⭐⭐⭐ | ✅📡 | 🟡 Animal and buoy tracking uplinks |
| **Agricultural soil sensors** | 868/915 MHz LoRa | see [IoT](./08_iot_ism_and_short_range.md) | ⭐⭐⭐ | ✅ | 🟢 |
| **Air quality sensor networks** | 868/915 MHz | LoRa/FSK | ⭐⭐⭐ | ✅ | 🟢 Increasingly common in cities |

---

## Try this first: `rtl_433` on 433.92 MHz

Before you build anything, spend an evening capturing 433.92 MHz. In any suburb you will pick
up neighbours' weather stations, tyre-pressure sensors, doorbells and thermometers — dozens of
devices, all transmitting simple OOK frames in the clear.

It is the **cheapest possible introduction to real-world data decoding**: no synchronisation
loops, no FEC, just amplitude and timing. And when you then read `rtl_433`'s protocol
definitions, you will find you can understand every one of them after
[Lab 08](../02_flowgraphs/lab08_rds_decoder/README.md).

---

## Then: count meteors while you sleep

Point a 2 m antenna away from the GRAVES radar in France (143.050 MHz), run a narrow SSB-style
receiver, and log the audio overnight. Each meteor trail reflects the radar for a fraction of a
second, producing a brief ping. Count them per hour and you have a meteor rate — a real
scientific measurement, from a wire in your garden, with no satellite pass to catch and no
weather to wait for.

The same technique works with any strong distant VHF transmitter; European observers use GRAVES,
others use distant TV or FM carriers just over the horizon.

---

[← Satellite & Space](./04_satellite_and_space.md) · [Catalogue index](./README.md) · [Next: Land Mobile →](./06_land_mobile_and_professional.md)
