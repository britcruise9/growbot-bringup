# GrowBot V0 — Hardware Bringup Kit

**SCS0009 / SC09 serial-bus servos store 2-byte values big-endian — for reads _and_ writes.**
If you get nonsense positions or a servo that "won't move past some point," check byte
order first. Dynamixel-style little-endian code looks like it works, then silently writes
garbage that the servo clips to its max angle. That one fact cost us a full day; this kit
encodes it correctly so it doesn't cost you one.

This is the **hardware bringup layer** for GrowBot, a small biped robot that learns from
scratch. It is deliberately tiny: enough to prove your servos, bus, and wiring are alive —
nothing more.

> **What this is _not_.** The agent harness, LLM brain, policy runtime, training loop,
> reward functions, and behavior stack are still experimental and are **not** included in
> this release. This repo is diagnostics and safe primitives only.

## What's in it

| File | What it does |
|------|--------------|
| `growbot/servos.py` | Minimal big-endian-correct SCS0009 driver: ping, read position, torque, move, sync-write |
| `growbot/pins.py` | Bus / encoder / register constants — edit to match your build |
| `scripts/scan_servos.py` | **Read-only.** Finds servos on the bus. Commands no motion. |
| `scripts/test_servos_safe.py` | Nudges each joint a few degrees and back, then goes limp. |
| `scripts/hello_growbot.py` | "Hello body" — scan, read, a small wave, release. |

## Quickstart

Tested on a Raspberry Pi Zero 2W (Raspberry Pi OS Bookworm, 64-bit) with two SCS0009
servos on the PL011 UART at 1 Mbaud.

```bash
pip install -r requirements.txt

# 1. Confirm the bus before anything moves (read-only):
python3 scripts/scan_servos.py

# 2. Gentle, bounded motion — hold the robot or use a stand:
python3 scripts/test_servos_safe.py

# 3. Say hello:
python3 scripts/hello_growbot.py
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

## Encoder range

The SCS0009 reports `0–1023` across its ~300° of travel. On our units the usable **floor is
255** — commanding any goal below that just stalls at 255. The driver clamps all motion to
`255–1023` so you can't drive into that dead zone.

## Safety

These scripts move a physical robot. `test_servos_safe.py` and `hello_growbot.py` move each
joint a few degrees around wherever it currently is — keep GrowBot on a stand or hold it,
and keep fingers clear of the joints. Motion is bounded in software to the usable encoder
range; out-of-range commands are clamped, not sent raw.

This kit deliberately talks to servos **by ID** and makes no left/right assumption, so you
can bring up the bus before you've settled your own leg mapping.

## License

MIT — see [LICENSE](LICENSE). Built by Brit Cruise. Bug reports and fixes from anyone
bringing up SCS0009 servos are very welcome.
