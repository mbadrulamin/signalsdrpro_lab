# 🛠️ 14 — Test, Measurement & Infrastructure

> Using the SDR as an **instrument** rather than a receiver. These are the least glamorous
> projects in the catalogue and by far the most professionally useful — this is what SDR is
> actually employed to do.
>
> [← Security Research](./13_security_research.md) · [Catalogue index](./README.md) · [Next: Transmit Projects →](./15_transmit_projects.md)

---

## Why this domain repays effort

A $300 SDR plus good software replaces several pieces of laboratory equipment that used to cost
tens of thousands. Not perfectly — a real spectrum analyser has better dynamic range, calibrated
absolute levels and a much cleaner front end — but well enough that measurement stops being a
budget question.

The catch is **calibration**. Your SDR reports dBFS, not dBm, and it has no idea what your
antenna, cable or LNA did to the signal. Everything in this file is *relative* until you
calibrate it against a known reference.

---

## Spectrum monitoring

| Project | Diff | Needs | Notes |
|---|---|---|---|
| **Wideband spectrum survey** | ⭐⭐ | ✅ | Sweep 70 MHz–6 GHz in steps, stitch the results. `soapy_power`, `rtl_power` style |
| **Long-term waterfall logging** | ⭐⭐ | ✅🖥️ | Occupancy over hours or days reveals patterns invisible in real time |
| **Spectrum occupancy statistics** | ⭐⭐⭐ | ✅ | What fraction of the time is each channel in use? Regulators care a great deal |
| **Change detection / baselining** | ⭐⭐⭐ | ✅🖥️ | Record "normal", alert on deviation |
| **Interference hunting** | ⭐⭐⭐ | ✅📡 | Find the source of noise affecting a service |
| **Noise floor characterisation** | ⭐⭐⭐ | ✅ | Measure your own site's RF environment before blaming equipment |
| **Harmonic and spur analysis** | ⭐⭐⭐ | ✅🧊 | Distinguish real signals from your own receiver's artefacts |
| **Intermodulation hunting** | ⭐⭐⭐⭐ | ✅🧊 | Two strong signals producing a third where nothing is transmitted |
| **EMC pre-compliance scanning** | ⭐⭐⭐⭐ | ✅📡 | Near-field probes plus an SDR catches most failures before a paid test |
| **Power line noise location** | ⭐⭐⭐ | ✅📡 | A very common real-world nuisance, and directional antennas find it |

---

## Direction finding

| Technique | Diff | Needs | Notes |
|---|---|---|---|
| **Directional antenna + hunting** | ⭐⭐ | ✅📡 | A Yagi and patience. Still the most reliable method |
| **Body fade / attenuator hunting** | ⭐⭐ | ✅📡 | Use your own body to shadow the signal; add attenuation as you close in |
| **Pseudo-Doppler** | ⭐⭐⭐⭐ | ✅📡 | Switch between four antennas fast; the resulting FM tone gives bearing |
| **Watson-Watt (Adcock)** | ⭐⭐⭐⭐ | ✅📡 | Crossed loops, amplitude comparison |
| **Phase interferometry** | ⭐⭐⭐⭐ | ✅📡 | **Two coherent channels — which your B210 has.** Phase difference gives angle |
| **TDOA across multiple receivers** | ⭐⭐⭐⭐⭐ | ✅🖥️ | Needs GPS-disciplined timing at each site. Your SDR's internal GPSDO helps |
| **Correlative interferometry** | ⭐⭐⭐⭐⭐ | ✅📡🖥️ | Professional-grade; compares measured phase against a calibrated array response |
| **Fox hunting / ARDF** | ⭐⭐ | ✅📡 | The sport version. Genuinely the best way to learn DF |

---

## Antenna and RF component measurement

| Project | Diff | Needs | Notes |
|---|---|---|---|
| **Antenna pattern measurement** | ⭐⭐⭐ | ✅📡 | Rotate the antenna against a fixed source, log power vs angle |
| **Return loss / VSWR (with a bridge)** | ⭐⭐⭐⭐ | ✅🔴 | Needs a directional coupler and a TX source. A NanoVNA is cheaper and better |
| **Cable loss measurement** | ⭐⭐⭐ | ✅🔴 | Compare received power with and without the cable |
| **Filter response measurement** | ⭐⭐⭐ | ✅🔴 | Sweep a signal through it and log the output |
| **LNA gain and noise figure** | ⭐⭐⭐⭐ | ✅🔴 | Y-factor method with a calibrated noise source |
| **Amplifier P1dB and IP3** | ⭐⭐⭐⭐ | ✅🔴 | Two-tone test — teaches you what "linear" really means |
| **Beam pattern from a celestial source** | ⭐⭐⭐⭐ | ✅📡🔊 | Drift-scan the Sun. See [Science](./12_science_and_radio_astronomy.md) |
| **Path loss / link budget verification** | ⭐⭐⭐ | ✅📡 | Measure what [Fundamentals 06](../01_fundamentals/06_noise_snr_and_gain.md) predicts |

---

## Signal analysis

| Project | Diff | Needs | Notes |
|---|---|---|---|
| **Modulation recognition** | ⭐⭐⭐ | ✅ | Constellation, cyclostationary features, spectral shape |
| **Symbol rate estimation** | ⭐⭐⭐ | ✅ | Cyclic spectrum or magnitude autocorrelation |
| **Occupied bandwidth measurement** | ⭐⭐ | ✅ | The 99 % power bandwidth, as regulators define it |
| **Adjacent channel power ratio (ACPR)** | ⭐⭐⭐ | ✅ | How much a transmitter splatters into its neighbours |
| **EVM / constellation quality** | ⭐⭐⭐⭐ | ✅ | Error vector magnitude — the standard transmitter quality metric |
| **Phase noise measurement** | ⭐⭐⭐⭐⭐ | ✅ | Limited by your own SDR's oscillator, but relative comparisons work |
| **Frequency accuracy / drift logging** | ⭐⭐⭐ | ✅ | Track a reference carrier over hours. **Your GPSDO makes this genuinely accurate** |
| **Timing jitter analysis** | ⭐⭐⭐⭐ | ✅ | |

---

## Infrastructure you can build

| Project | Diff | Needs | Notes |
|---|---|---|---|
| **A permanent monitoring station** | ⭐⭐⭐ | ✅🖥️ | Headless, logging, remote-accessible. The natural home for a spare SDR |
| **Feed a public network** | ⭐⭐ | ✅📡 | ADS-B, AIS, radiosondes, SatNOGS, WSPR — all welcome volunteer receivers |
| **A remote/web-accessible SDR** | ⭐⭐⭐ | ✅🖥️ | OpenWebRX lets others use your radio |
| **Multi-SDR coherent array** | ⭐⭐⭐⭐⭐ | ✅🖥️ | Beamforming and DF. Needs shared clock and LO |
| **Automated pass scheduler** | ⭐⭐⭐ | ✅🖥️ | Predict satellite passes and record them unattended |
| **Spectrum database** | ⭐⭐⭐ | ✅🖥️ | Store years of occupancy data and query it |
| **Alerting on specific signals** | ⭐⭐⭐ | ✅🖥️ | Notify when a particular emitter appears |
| **Calibrated power reference** | ⭐⭐⭐⭐ | ✅ | Convert dBFS to dBm using a known source — turns your SDR into a real instrument |

---

## Try this first: measure your own noise floor

Before you blame your antenna, your SDR or the weather for poor reception, **measure your site**.

```python
# sweep the band in 2 MHz steps and log the median power per step
import numpy as np
from gnuradio import gr, blocks, uhd

def floor(fc, gain=40, n=400000):
    tb = gr.top_block()
    u = uhd.usrp_source("", uhd.stream_args(cpu_format="fc32", channels=[0]))
    u.set_samp_rate(2e6); u.set_center_freq(uhd.tune_request(fc), 0)
    u.set_bandwidth(2e6, 0); u.set_gain(gain, 0)   # <- always set bandwidth!
    sk = blocks.skiphead(gr.sizeof_gr_complex, 400000)
    hd = blocks.head(gr.sizeof_gr_complex, n); vs = blocks.vector_sink_c()
    tb.connect(u, sk, hd, vs); tb.run()
    d = np.array(vs.data())
    P = np.abs(np.fft.fftshift(np.fft.fft(d[:8192] * np.hanning(8192))))**2
    return 10*np.log10(np.median(P))

for f in np.arange(80e6, 1000e6, 2e6):
    print(f"{f/1e6:7.1f} MHz  {floor(f):7.1f} dB")
```

The result is a map of **where you can actually hear anything**. Most people discover a broadband
noise floor 20 dB above thermal across the whole VHF range, caused by a switch-mode power supply,
an LED driver or a solar inverter in their own house. Finding and unplugging it is usually worth
more than any amount of antenna work.

> Note the `set_bandwidth()` call. Leaving it out lets the analog filter default to 56 MHz and
> your measurements become meaningless — as this repository discovered the hard way and
> documented in [Fundamentals 06](../01_fundamentals/06_noise_snr_and_gain.md).

---

## Then: contribute to a network

The single most useful thing an idle SDR can do is **feed a public data network**. It costs
nothing, it runs unattended, and your receiver becomes part of a global instrument:

| Network | What you feed | Why it matters |
|---|---|---|
| ADS-B aggregators | aircraft positions | Coverage in your area |
| AISHub / MarineTraffic | ship positions | Same, for shipping |
| `radiosonde_auto_rx` / SondeHub | balloon telemetry | Tracking and recovery |
| SatNOGS | satellite observations | Open ground-station network |
| WSPRnet | propagation reports | A live map of the ionosphere |
| Blitzortung | lightning timing | Global strike location |
| KiwiSDR / OpenWebRX | your receiver itself | Lets others listen from your location |

---

[← Security Research](./13_security_research.md) · [Catalogue index](./README.md) · [Next: Transmit Projects →](./15_transmit_projects.md)
