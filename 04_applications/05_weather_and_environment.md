# 🌦️ 05 — Weather & Environment

> Nature transmits too. Lightning, meteors, the ionosphere and the Sun all put energy into the
> radio spectrum. Some of the most interesting SDR projects receive things nobody sent on
> purpose.
>
> [← Satellite & Space](./04_satellite_and_space.md) · [Catalogue index](./README.md) · [Next: Land Mobile →](./06_land_mobile_and_professional.md)

---

## Radiosondes — weather balloons you can chase

Twice a day, from about 800 sites around the world (including the Malaysian Meteorological
Department), weather services launch balloons carrying a small transmitter. It climbs to about
30 km, bursts, and falls. All the way down it sends its **GPS position** — so you can decode it,
go to where it lands, and keep it. Many people do this as a hobby.

| Signal | Frequency | Mode | Diff | Needs | Notes |
|---|---|---|---|---|---|
| **Vaisala RS41** | 400–406 MHz | GFSK 4800 bit/s, Reed-Solomon | ⭐⭐⭐ | ✅ | 🟢 The most common type worldwide. `radiosonde_auto_rx` |
| **Vaisala RS92** | 400–406 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 Older, still flown in places |
| **Graw DFM-09/17** | 400–406 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 Common in Europe |
| **Meteomodem M10/M20** | 400–406 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 France and francophone regions |
| **iMet-4** | 400–406 MHz | FSK | ⭐⭐⭐ | ✅ | 🟢 |
| **Dropsondes** | 400–406 MHz | FSK | ⭐⭐⭐⭐ | ✅ | 🟢 Dropped *from* hurricane-hunter aircraft |
| **Ozonesondes / special payloads** | 400–406 MHz | varies | ⭐⭐⭐⭐ | ✅ | 🟢 Extra sensor channels in the telemetry |

**Why it is a great project:** the signal is strong (a balloon 20 km up can be seen for hundreds
of km), the format is published, decoders already exist, and there is a real object to find at
the end. A quarter-wave antenna for 403 MHz is 186 mm.

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

Before you build anything, spend an evening receiving 433.92 MHz (a licence-free band in
Malaysia). In most neighbourhoods you will pick up weather stations, tyre-pressure sensors,
doorbells and thermometers — dozens of devices, all sending simple on-off (OOK) messages without
encryption.

It is the **easiest introduction to decoding real data**: no synchronisation loops, no error
correction, just "on or off" and timing. After [Lab 08](../02_flowgraphs/lab08_rds_decoder/README.md),
you will understand every protocol in `rtl_433`'s list.

---

## Then: count meteors while you sleep

Choose a strong VHF transmitter that is **just too far away to hear** normally (over the
horizon). Tune a narrow SSB receiver to it and record the audio overnight. Each meteor leaves a
short-lived trail in the sky that reflects the signal for a fraction of a second — a brief
"ping". Count the pings per hour and you have a **meteor rate**: a real scientific measurement,
from a wire antenna, with no satellite pass to catch.

In Europe, people use the GRAVES radar in France (143.050 MHz). It is too far to use from
Malaysia; use a distant FM or TV transmitter instead.

---

[← Satellite & Space](./04_satellite_and_space.md) · [Catalogue index](./README.md) · [Next: Land Mobile →](./06_land_mobile_and_professional.md)
