# 📖 Glossary — Every Acronym in This Repository

> **If you are new, read [The Twenty That Matter Most](#the-twenty-that-matter-most) first.**
> The rest is a lookup table — come back to it whenever a document throws a new acronym at you.
>
> Terms are defined in **plain English first**, with the technical detail second.

---

## The Twenty That Matter Most

If you understand these twenty, you can read almost anything in this repository.

| Term | Say it as | What it actually means |
|---|---|---|
| **SDR** | "S-D-R" | **Software-Defined Radio.** A radio whose behaviour is set by software rather than by its wiring |
| **RF** | "R-F" | **Radio Frequency.** Any signal a radio deals with, roughly 20 kHz to 300 GHz |
| **IQ** | "eye-queue" | **In-phase and Quadrature.** The pair of numbers an SDR produces for each sample. Together they describe a signal's amplitude *and* its phase |
| **Sample rate** | — | How many measurements per second. For IQ, **the sample rate equals the bandwidth you can see** |
| **Bandwidth** | — | How wide a slice of spectrum, in Hz. One FM station is 200 kHz wide |
| **dB** | "dee-bee" | **Decibel.** A ratio on a logarithmic scale. +10 dB = 10× the power, +3 dB = 2× |
| **dBm** | "dee-bee-em" | Power measured against 1 milliwatt. −90 dBm is a typical usable broadcast signal |
| **SNR** | "S-N-R" | **Signal-to-Noise Ratio.** How much louder your signal is than the noise. The number that decides whether anything works |
| **Noise floor** | — | The background hiss present even with no signal. You cannot hear anything below it |
| **Gain** | — | Amplification. More is **not** always better — see [Fundamentals 06](../01_fundamentals/06_noise_snr_and_gain.md) |
| **LO** | "L-O" | **Local Oscillator.** The internal tone a radio mixes with the incoming signal to shift it down to a workable frequency |
| **Modulation** | — | How information is stuck onto a radio wave — by varying its amplitude (AM), frequency (FM), or phase (PSK) |
| **Demodulate** | — | Getting the information back out |
| **AM / FM** | — | **Amplitude / Frequency Modulation.** The two classic analog schemes |
| **Filter** | — | Something that keeps the frequencies you want and removes the rest |
| **Decimate** | — | Reduce the sample rate by throwing samples away — **only safe after filtering** |
| **FFT** | "F-F-T" | **Fast Fourier Transform.** The algorithm that turns a signal into a spectrum display |
| **Flowgraph** | — | A GNU Radio program: blocks connected by wires, each doing one operation |
| **GNU Radio** | "g-noo radio" | The open-source toolkit this entire repository is built on |
| **UHD** | "U-H-D" | **USRP Hardware Driver.** The software that talks to your SignalSDR Pro |

---

## A

| Term | Meaning |
|---|---|
| **ACARS** | Aircraft Communications Addressing and Reporting System — text messages to and from aircraft, around 131 MHz |
| **ACPR** | Adjacent Channel Power Ratio. How much a transmitter spills into its neighbours' channels |
| **ADC** | Analogue-to-Digital Converter. The chip that turns voltage into numbers. **The heart of an SDR** |
| **AD9361** | The Analog Devices RF transceiver chip inside the SignalSDR Pro |
| **ADS-B** | Automatic Dependent Surveillance–Broadcast. Aircraft broadcasting their position at 1090 MHz. [Lab 09](../02_flowgraphs/lab09_adsb_receiver/README.md) |
| **AFSK** | Audio Frequency Shift Keying. FSK done at audio frequencies, then fed to an ordinary FM radio |
| **AGC** | Automatic Gain Control. A feedback loop that keeps the signal level roughly constant |
| **AIS** | Automatic Identification System. Ships broadcasting position, around 162 MHz |
| **Aliasing** | When a signal above half the sample rate folds down and masquerades as a different frequency. **Irreversible** — filter first |
| **AM** | Amplitude Modulation. Information carried in the wave's *height* |
| **AMBE** | A proprietary voice codec used in DMR, P25 and D-STAR digital voice |
| **Antenna gain** | How much an antenna concentrates energy in one direction, in dBi |
| **APRS** | Automatic Packet Reporting System. Amateur position/telemetry packets, 144.39/144.80 MHz |
| **APT** | Automatic Picture Transmission. The old NOAA weather-satellite image mode — **switched off in 2025** |
| **ARQ** | Automatic Repeat reQuest. Asking for a retransmission when a message arrives corrupted |
| **ASK** | Amplitude Shift Keying. Digital AM — the carrier is switched between levels |
| **ATIS** | Automatic Terminal Information Service. A looped airport weather broadcast. The easiest airband signal to find |
| **ATSC** | The American digital television standard |
| **Attenuator** | A part that *reduces* signal power by a known amount. Essential for safe transmit testing |
| **AWGN** | Additive White Gaussian Noise. The standard mathematical model of thermal noise |

## B

| Term | Meaning |
|---|---|
| **B210** | The Ettus USRP B210, the radio your SignalSDR Pro emulates |
| **Band** | A named range of frequencies, e.g. the FM broadcast band, 87.5–108 MHz |
| **Bandwidth** | Width of a frequency range, in Hz |
| **Baseband** | A signal shifted down so it is centred on 0 Hz. What your SDR delivers |
| **Baud** | Symbols per second. **Not** the same as bits per second unless 1 bit per symbol |
| **BCH** | An algebraic error-correcting code, used *outside* LDPC in DVB-T2 to clean up residual errors |
| **BER** | Bit Error Rate. The fraction of received bits that are wrong. Measured in [Lab 07](../02_flowgraphs/lab07_bpsk_link_sim/README.md) |
| **BLE** | Bluetooth Low Energy |
| **BPF** | Band-Pass Filter. Keeps a range of frequencies, removes everything above and below |
| **BPSK** | Binary Phase Shift Keying. Two constellation points 180° apart. The most robust digital modulation |
| **Burst** | A short transmission, on and then off again. Airband and ADS-B are bursty; FM broadcast is not |

## C

| Term | Meaning |
|---|---|
| **Carrier** | The plain radio wave that information is modulated onto |
| **Carson's rule** | The formula for FM bandwidth: $B \approx 2(\Delta f + f_m)$ |
| **CDMA** | Code Division Multiple Access. Many users share a frequency, separated by codes. GPS works this way |
| **Channel** | One allocated slot of spectrum, e.g. one 200 kHz FM station |
| **Chip** | One element of a spread-spectrum code. Chips are faster than bits |
| **CMA** | Communications and Multimedia Act 1998 — the Malaysian law governing spectrum |
| **Codec** | Coder/decoder — compresses voice or video |
| **Coherent** | Two receivers sharing one clock and one LO, so their phase relationship is stable. Needed for direction finding and MIMO |
| **Complex sample** | An IQ pair, written as a complex number |
| **Constellation** | A plot of the allowed symbol values on the I/Q plane. Tight dots = good signal |
| **Costas loop** | A circuit/algorithm that recovers a carrier from a signal that does not transmit one |
| **CP** | Cyclic Prefix. A copy of a symbol's end pasted onto its front, making OFDM immune to multipath |
| **CPR** | Compact Position Reporting. The modular-arithmetic trick ADS-B uses to send a position in 17 bits |
| **CRC** | Cyclic Redundancy Check. A checksum that detects corrupted messages. [Fundamentals 10](../01_fundamentals/10_error_detection_and_framing.md) |
| **CTCSS** | Continuous Tone-Coded Squelch System. A sub-audible tone that keeps a radio quiet unless the right group is talking |
| **CW** | Continuous Wave — Morse code, strictly a carrier switched on and off |

## D

| Term | Meaning |
|---|---|
| **DAB** | Digital Audio Broadcasting. Digital radio, 174–240 MHz |
| **DAC** | Digital-to-Analogue Converter. The ADC's opposite, used when transmitting |
| **dB / dBm / dBFS / dBi / dBc** | Decibel variants: ratio / vs 1 mW / vs ADC full scale / vs an isotropic antenna / vs the carrier |
| **DC offset** | An unwanted constant added to the signal, appearing as a spike at 0 Hz. Very common in SDRs |
| **DDC / DUC** | Digital Down/Up Converter. Shifts a signal in frequency digitally |
| **Decimation** | Reducing the sample rate by keeping 1 sample in N. **Always filter first** |
| **De-emphasis** | A treble cut applied after FM demodulation, undoing the pre-emphasis the transmitter applied |
| **Deviation** | How far FM swings the carrier. ±75 kHz for broadcast, ±5 kHz for narrowband |
| **DF** | Direction Finding — working out where a transmission came from |
| **DMR** | Digital Mobile Radio. A common digital two-way voice standard |
| **Doppler** | Frequency shift caused by motion. ±3.5 kHz for a satellite pass at 137 MHz |
| **DSB-SC** | Double Sideband Suppressed Carrier. AM with the carrier removed. Used by FM stereo and RDS |
| **DSP** | Digital Signal Processing |
| **DTT** | Digital Terrestrial Television |
| **Duplex** | Transmitting and receiving at the same time (full) or alternately (half) |
| **DVB-T / DVB-T2** | The European digital television standards. Malaysia uses **DVB-T2**. [Lab 10](../02_flowgraphs/lab10_dvbt2_tx_rx/README.md) |

## E

| Term | Meaning |
|---|---|
| **Eb/N0** | "E-B over N-nought". Energy per bit divided by noise density. **The fair way to compare digital links** |
| **EIRP** | Effective Isotropic Radiated Power. Transmit power including antenna gain. What regulators limit |
| **EME** | Earth-Moon-Earth — bouncing signals off the Moon |
| **Envelope** | The outline of a signal's amplitude. AM detection means extracting it |
| **EVM** | Error Vector Magnitude. How far constellation points land from where they should |
| **Eye diagram** | Overlaid symbol waveforms. A wide-open "eye" means good timing and low noise |

## F

| Term | Meaning |
|---|---|
| **FEC** | Forward Error Correction. Extra bits that let the receiver *repair* errors, not just detect them |
| **FFT** | Fast Fourier Transform. Converts time into frequency — how every waterfall display works |
| **FHSS** | Frequency Hopping Spread Spectrum. Rapidly changing frequency in a known pattern |
| **FIR** | Finite Impulse Response. The standard, always-stable digital filter. [Fundamentals 05](../01_fundamentals/05_sampling_and_filters.md) |
| **FLL** | Frequency Locked Loop. Corrects frequency error, ignoring phase |
| **FM** | Frequency Modulation. Information carried in the wave's *frequency* |
| **FPGA** | Field-Programmable Gate Array. Reconfigurable logic. The Zynq in your SDR contains one |
| **FSK** | Frequency Shift Keying. Digital FM — the carrier jumps between frequencies |
| **FT8** | An amateur weak-signal mode that decodes 21 dB below the noise |

## G

| Term | Meaning |
|---|---|
| **Gain** | Amplification, in dB. Raise it until the noise floor starts rising, then back off |
| **GFSK / GMSK** | Gaussian-filtered FSK/MSK. Smoothed FSK that occupies less bandwidth. Used by AIS and Bluetooth |
| **GNSS** | Global Navigation Satellite System — the umbrella term for GPS, Galileo, GLONASS, BeiDou |
| **GNU Radio** | The open-source DSP toolkit used throughout this repository |
| **GPSDO** | GPS-Disciplined Oscillator. A clock corrected by GPS. **Your SignalSDR Pro has one built in** |
| **GRC** | GNU Radio Companion — the graphical flowgraph editor |
| **Guard interval** | See **Cyclic Prefix** |

## H – I

| Term | Meaning |
|---|---|
| **HF** | High Frequency, 3–30 MHz. Bounces off the ionosphere, so it reaches worldwide. **Your SDR cannot tune here without an upconverter** |
| **ICAO** | International Civil Aviation Organization. Also the 24-bit aircraft address in ADS-B |
| **IF** | Intermediate Frequency. In old radios, a fixed frequency the signal was shifted to for filtering |
| **IIR** | Infinite Impulse Response. A filter with feedback — efficient but can be unstable |
| **IMD** | Intermodulation Distortion. False signals created when two strong signals mix in an overloaded receiver |
| **Interleaving** | Shuffling data before transmission so a burst of noise damages scattered bits rather than consecutive ones |
| **ISI** | Inter-Symbol Interference. Symbols smearing into each other |
| **ISM** | Industrial, Scientific and Medical. Licence-exempt bands: in Malaysia 433 MHz, 919–923 MHz, 2.4 GHz |
| **IQ** | In-phase / Quadrature. See [Fundamentals 02](../01_fundamentals/02_iq_sampling.md) |

## L

| Term | Meaning |
|---|---|
| **LDPC** | Low-Density Parity Check. A modern error-correcting code that gets within ~1 dB of the theoretical limit |
| **LNA** | Low-Noise Amplifier. An amplifier placed **at the antenna** to set the system noise figure |
| **LNB** | Low-Noise Block downconverter. The thing on a satellite dish that shifts Ku-band down to something usable |
| **LO** | Local Oscillator. See the top-twenty table |
| **LoRa** | Long Range. A chirp-spread-spectrum IoT modulation. Malaysia uses 919–923 MHz |
| **LPF** | Low-Pass Filter. Keeps low frequencies, removes high ones |
| **LSB / USB** | Lower / Upper Sideband — the two SSB variants. (Also USB = Universal Serial Bus. Context decides) |
| **LTE** | Long Term Evolution — 4G cellular |

## M – N

| Term | Meaning |
|---|---|
| **MCMC / SKMM** | Malaysian Communications and Multimedia Commission — the spectrum regulator |
| **MER** | Modulation Error Ratio. A quality measure for digital signals; what a TV's signal-quality bar shows |
| **MIMO** | Multiple Input Multiple Output. Several antennas used together |
| **Mixer** | A circuit that multiplies two signals, shifting frequency. Tuning, essentially |
| **MPX** | Multiplex. The composite baseband inside an FM broadcast: mono, stereo and RDS stacked together |
| **MSPS** | Mega-samples per second |
| **Multipath** | The same signal arriving several times by different paths. Causes fading and ISI |
| **NBFM / WBFM** | Narrowband / Wideband FM. ±5 kHz vs ±75 kHz deviation |
| **NCO** | Numerically Controlled Oscillator. A tone generated in software |
| **NF** | Noise Figure. How much noise a receiver adds, in dB. Lower is better |
| **Noise floor** | See the top-twenty table |
| **Nyquist** | The rule that you must sample faster than twice the highest frequency — or, for IQ, faster than the bandwidth |

## O – P

| Term | Meaning |
|---|---|
| **OFDM** | Orthogonal Frequency Division Multiplexing. Thousands of slow carriers instead of one fast one. Used by Wi-Fi, LTE, 5G, DAB, DVB-T2. [Fundamentals 11](../01_fundamentals/11_ofdm_and_broadcast_systems.md) |
| **OOK** | On-Off Keying. The simplest modulation: carrier on = 1, off = 0. Most cheap remotes use it |
| **P25** | A digital radio standard used by public safety in North America |
| **PAPR** | Peak-to-Average Power Ratio. OFDM's ~10 dB PAPR is why transmitters must be backed off |
| **Phase** | Where in its cycle a wave is. The "Q" half of IQ exists to measure it |
| **Pilot** | A known reference signal inserted so the receiver can measure the channel. FM stereo's 19 kHz tone is one |
| **PLL** | Phase Locked Loop. Locks an oscillator onto an incoming signal |
| **POCSAG** | A pager protocol. The simplest real data decode available to a beginner |
| **PPM** | Pulse Position Modulation (ADS-B) — **or** parts per million (clock accuracy). Context decides |
| **ppm** | Parts per million. 1 ppm at 1 GHz = 1 kHz of error |
| **Pre-emphasis** | Treble boost applied before FM transmission, undone by de-emphasis at the receiver |
| **PSK** | Phase Shift Keying. Information carried in the wave's *phase* |
| **PTY** | Programme Type. The genre field in RDS |

## Q – R

| Term | Meaning |
|---|---|
| **QAM** | Quadrature Amplitude Modulation. Phase *and* amplitude both carry information |
| **QPSK** | Quadrature PSK. Four constellation points, 2 bits per symbol |
| **Quadrature demod** | The standard way to demodulate FM digitally: measure the phase change between consecutive samples |
| **RDS / RBDS** | Radio Data System. The digital data hidden at 57 kHz in every FM broadcast. [Lab 08](../02_flowgraphs/lab08_rds_decoder/README.md) |
| **Resampling** | Changing the sample rate by a ratio, e.g. 2 MSPS → 48 kSPS |
| **RF** | Radio Frequency |
| **RRC** | Root Raised Cosine. The standard pulse shape for digital links, split between transmitter and receiver |
| **RTL-SDR** | The $40 USB dongle that started the hobby. Still the best way to begin |

## S

| Term | Meaning |
|---|---|
| **Sample** | One measurement. For IQ, one complex number |
| **Sample rate** | Samples per second. For IQ, equals the visible bandwidth |
| **SDR** | Software-Defined Radio |
| **SFN** | Single Frequency Network. Many transmitters on one frequency, made possible by OFDM's guard interval |
| **Sideband** | The frequencies either side of a carrier, created by modulation |
| **SMA** | The small screw-on coaxial connector on your SDR |
| **SNR** | Signal-to-Noise Ratio |
| **Spectrum** | Signal strength plotted against frequency |
| **Squelch** | Muting the audio when the signal is too weak, so you get silence instead of hiss |
| **SSB** | Single Sideband. AM with the carrier and one sideband removed — efficient, and the standard HF voice mode |
| **SSTV** | Slow-Scan Television. Sending still images as audio tones |
| **Symbol** | One transmitted unit carrying one or more bits |
| **Symbol rate** | Symbols per second, in baud |
| **Sync word** | A known pattern marking the start of a message |
| **Syndrome** | The remainder from a CRC calculation. Zero means no error detected |

## T – Z

| Term | Meaning |
|---|---|
| **TCXO** | Temperature-Compensated Crystal Oscillator. A stable clock. Yours is ±1 ppm |
| **TDMA** | Time Division Multiple Access. Users share a frequency by taking turns |
| **TDOA** | Time Difference Of Arrival. Locating a transmitter by comparing arrival times at several receivers |
| **TED** | Timing Error Detector. The part of a symbol synchroniser that measures how wrong the sampling instant is |
| **TETRA** | A European digital radio standard for public safety |
| **Throttle** | A GNU Radio block that limits a flowgraph to real time when there is no hardware to pace it |
| **TPMS** | Tyre Pressure Monitoring System. Sensors in car wheels, 433 MHz here |
| **Transceiver** | A device that both transmits and receives |
| **TS** | Transport Stream. The MPEG-2 container digital television is carried in |
| **UHD** | USRP Hardware Driver |
| **UHF** | Ultra High Frequency, 300 MHz – 3 GHz |
| **Upconverter** | A box that shifts HF up into a range your SDR can tune. Needed for anything below 70 MHz |
| **USRP** | Universal Software Radio Peripheral — Ettus Research's SDR family |
| **VCO** | Voltage Controlled Oscillator |
| **VHF** | Very High Frequency, 30–300 MHz. FM, airband, marine, 2 m amateur |
| **Viterbi** | The optimal decoding algorithm for convolutional error-correcting codes |
| **VLF** | Very Low Frequency, 3–30 kHz. Lightning, submarines, natural radio |
| **VSWR** | Voltage Standing Wave Ratio. How well an antenna matches its feedline. 1:1 is perfect |
| **Waterfall** | A display with frequency across and time downward. Better than an FFT for spotting brief signals |
| **Wavelength (λ)** | $\lambda = 300 / f_{\text{MHz}}$ metres. Sets how long your antenna must be |
| **WSPR** | Weak Signal Propagation Reporter. Decodes 28 dB below the noise |
| **Zynq** | The AMD/Xilinx chip in your SDR: an FPGA and two ARM processors on one die |

---

## Symbols and units

| Symbol | Reads as | Meaning |
|---|---|---|
| $f_s$ | "f sub s" | Sample rate |
| $f_c$ | "f sub c" | Centre / carrier frequency |
| $\Delta f$ | "delta f" | Frequency deviation, or a frequency difference |
| $\lambda$ | "lambda" | Wavelength |
| $\tau$ | "tau" | A time constant |
| $\beta$ | "beta" | Modulation index (FM), or a filter parameter |
| $\sigma$ | "sigma" | Standard deviation — usually of noise |
| Hz, kHz, MHz, GHz | — | Cycles per second, ×10³, ×10⁶, ×10⁹ |
| SPS, kSPS, MSPS | — | Samples per second, and its multiples |

---

## Numbers worth memorising

| Number | What it is |
|---|---|
| **−174 dBm/Hz** | Thermal noise at room temperature. The noise floor of the universe |
| **3 dB** | A factor of 2 in power |
| **6 dB** | A factor of 2 in voltage, and 1 extra ADC bit |
| **±75 kHz** | FM broadcast deviation |
| **19 kHz** | The FM stereo pilot tone |
| **57 kHz** | The RDS subcarrier (3 × 19 kHz) |
| **1090 MHz** | ADS-B |
| **1575.42 MHz** | GPS L1 |
| **69 mm** | A quarter wave at 1090 MHz |
| **300 / f(MHz)** | Wavelength in metres |

---

**See also:** [Introduction to SDR](../01_fundamentals/00_introduction_to_sdr.md) ·
[Signal identification](./02_signal_identification.md) · [Reference index](./README.md)
