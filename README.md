# GrowBot V0 — Hardware Bringup Kit

**SCS0009 / SC09 serial-bus servos store 2-byte values big-endian — for reads _and_ writes.**
If you get nonsense positions or a servo that "won't move past some point," check byte
order first. Dynamixel-style little-endian code looks like it works, then silently writes
garbage that the servo clips to its max angle. That one fact cost us a full day; this kit
encodes it correctly so it doesn't cost you one.

This is the **hardware bringup layer** for GrowBot, a small biped robot that learns from
scratch. Reusable drivers plus a tiny test per subsystem — servos, LED ring, speaker/voice,
IMU, camera — and a `hello_growbot.py` that ties lights + voice + legs into a first hello.
Its only job is to prove the body is alive.

> **What this is _not_ — yet.** The agent harness, LLM brain, policy runtime, training
> loop, reward functions, and behavior stack aren't in here. They're still in active R&D
> and are planned for **V1**. This release (V0) is hardware bringup and diagnostics only —
> prove the body first, the mind comes next.

## What's in it

**Drivers** — `growbot/` (you `import` these):

| Module | Hardware | What it gives you |
|--------|----------|-------------------|
| `pins.py` | — | every wiring constant in one place (ports, IDs, GPIO pins, encoder range). **Edit this to match your build.** |
| `servos.py` | SCS0009 serial-bus servos | big-endian-correct: scan, read position, torque, move, sync-move |
| `leds.py` | WS2812 / NeoPixel ring (GPIO12) | fill, spin, off |
| `audio.py` | Google voiceHAT speaker + mic | `speak(text)` via espeak-ng/flite → aplay; sample a mic level |
| `imu.py` | MPU-6050 over I²C | WHO_AM_I + accel/gyro |
| `camera.py` | Pi camera | capture one still (picamera2 → rpicam-still) |

**Scripts** — `scripts/` (you run these):

| Command | What it does |
|---------|--------------|
| `python3 scripts/scan_servos.py` | **Read-only.** Finds servos, prints positions. No motion. |
| `python3 scripts/test_servos_safe.py` | Nudges each leg a few degrees and back, then goes limp. |
| `sudo python3 scripts/test_leds.py` | Ring through red → green → blue → white, then a spin. |
| `python3 scripts/test_audio.py` | Says *"hello, I'm GrowBot"*, then samples the mic level. |
| `python3 scripts/test_imu.py` | Prints WHO_AM_I + live accel/gyro — tilt it to watch them move. |
| `python3 scripts/test_camera.py` | Captures one photo to `/tmp`. |
| `sudo -E python3 scripts/hello_growbot.py` | **The full hello:** lights → voice → legs → green spin. Skips any subsystem that isn't present. |

## Setup

```bash
pip install -r requirements.txt

# System packages (ship with Raspberry Pi OS; install if missing):
sudo apt install espeak-ng        # text-to-speech for the speaker (flite also works)
# picamera2 and alsa-utils (aplay/arecord) come with Raspberry Pi OS
```

The LED ring uses the Pi's PWM/DMA for WS2812 timing, which **needs root** — run the LED
test and the full hello with `sudo`.

## Quickstart

```bash
python3 scripts/scan_servos.py            # read-only: confirm the servo bus
python3 scripts/test_servos_safe.py       # gentle leg nudge — hold the robot or use a stand
sudo python3 scripts/test_leds.py         # ring colors + spin
python3 scripts/test_audio.py             # speaker says hello, mic level
python3 scripts/test_imu.py               # tilt to watch accel/gyro
python3 scripts/test_camera.py            # one photo to /tmp
sudo -E python3 scripts/hello_growbot.py  # meet GrowBot: lights + voice + legs
```

If `scan_servos.py` can't open the port: on a Pi Zero 2W the servo bus is **`/dev/serial0`**
(the real PL011 UART), **not** `/dev/ttyS0` — that one throws
`termios.error: (5, 'Input/output error')`. Enable the UART with `raspi-config` →
Interface Options → Serial Port: login shell **off**, serial hardware **on**, then reboot.

## SCS0009 register cheat sheet

All 2-byte values are **big-endian**.

| Reg  | Name             | Bytes | Notes |
|------|------------------|-------|-------|
| 0x03 | ID               | 1     | 1–253 |
| 0x28 | torque enable    | 1     | 0 = limp, 1 = holding |
| 0x2A | goal position    | 2 BE  | 0–1023 |
| 0x30 | EEPROM lock      | 1     | write 0 to unlock before changing 0x00–0x2F, 1 to lock |
| 0x38 | present position | 2 BE  | read-only |

Packet format: `FF FF <id> <len> <inst> <params...> <checksum>`, where
`len = len(params) + 2` and `checksum = ~(id + len + inst + sum(params)) & 0xFF`.
The bus is half-duplex, so every send is echoed back before the reply — strip the echo
before parsing. The driver does this and validates the checksum so a stray echo byte can't
be misread as a position.

The SCS0009 reports `0–1023` across ~300° of travel. On our units the usable **floor is
255** — commanding below that just stalls at 255, so the driver clamps motion to `255–1023`.

## Tested on

Developed and tested on a **Raspberry Pi Zero 2W** (Raspberry Pi OS Bookworm, 64-bit) with
two SCS0009 servos on the PL011 UART at 1 Mbaud, an MPU-6050 IMU at I²C `0x68`, a 7-pixel
WS2812 ring on GPIO12, a Google voiceHAT (speaker + mic), and a Pi camera. Your build will
differ — `growbot/pins.py` is where you reconcile it.

A note on audio: the voiceHAT's I²S amplifier has no software volume, so `audio.py` simply
renders speech to a WAV and plays it with `aplay`. If a play returns cleanly but you hear
nothing, it's almost always speaker wiring, not software.

## Safety

These scripts move a physical robot. `test_servos_safe.py` and `hello_growbot.py` move each
joint a few degrees around wherever it currently is — keep GrowBot on a stand or hold it,
and keep fingers clear of the joints. Motion is bounded in software to the usable encoder
range; out-of-range commands are clamped, not sent raw. Motion scripts release torque on
exit, even on Ctrl-C.

This kit talks to servos **by ID** and makes no left/right assumption, so you can bring up
the bus before you've settled your own leg mapping. Every subsystem is optional — the full
hello runs whatever's present and skips the rest.

## License

MIT — see [LICENSE](LICENSE). Built by Brit Cruise. Bug reports and fixes from anyone
bringing up SCS0009 servos, voiceHATs, or small bipeds are very welcome.
