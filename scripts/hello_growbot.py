#!/usr/bin/env python3
"""GrowBot's first hello: prove the body is alive, gently.

    scan the bus -> read each joint -> a small symmetric wave -> release

No audio, no policies, no autonomy. Just "the hardware works." Keep GrowBot on
a stand or hold it.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from growbot import pins  # noqa: E402
from growbot.servos import ServoBus  # noqa: E402


def main() -> int:
    print("hi, i'm growbot. checking my body...\n")
    with ServoBus() as bus:
        joints = [sid for sid in pins.SERVO_IDS if bus.ping(sid)]
        if not joints:
            print("...i can't feel my legs.")
            print("run scripts/scan_servos.py — check power and that you're on /dev/serial0.")
            return 1

        print(f"i found {len(joints)} joint(s): {joints}")
        starts = {sid: bus.present_position(sid) for sid in joints}
        for sid, pos in starts.items():
            print(f"  joint {sid} is at {pos}")

        # Only wave joints whose position we could actually read — never move
        # blindly to a guessed anchor.
        movable = [sid for sid in joints if starts[sid] is not None]
        if not movable:
            print("\n...i can feel my joints but can't read them — skipping the wave.")
            return 1

        try:
            for sid in movable:
                bus.set_torque(sid, True)
            print("\nwaving hello...")
            for _ in range(2):
                for sid in movable:
                    base = starts[sid]
                    for d in (pins.SAFE_NUDGE, -pins.SAFE_NUDGE, 0):
                        bus.move(sid, base + d)
                        time.sleep(0.25)
            for sid in movable:
                bus.move(sid, starts[sid])
            time.sleep(0.3)
        except KeyboardInterrupt:
            print("\ninterrupted — going limp")
        finally:
            # Always release torque on exit, even on error or Ctrl-C.
            for sid in movable:
                bus.set_torque(sid, False)

    print("\nthat's me. nice to meet you.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
