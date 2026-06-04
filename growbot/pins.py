"""Bus, encoder, and register constants for the GrowBot bringup kit.

These describe how GrowBot's hardware is wired and its safe operating limits.
Edit them to match YOUR build.
"""

# --- Servo bus (SCS0009 / SC09 Feetech serial-bus servos) ---
# On a Raspberry Pi Zero 2W this is the real PL011 UART. NOT /dev/ttyS0, which
# exists but raises termios.error (5, 'Input/output error').
SERVO_PORT = "/dev/serial0"
SERVO_BAUD = 1_000_000

# Servo IDs present on the bus. GrowBot has two legs.
SERVO_IDS = (1, 2)

# Usable encoder range. The SCS0009 reports 0-1023 over its ~300 deg of travel,
# but the usable floor on our units is 255 — commanding below that just stalls
# at 255. Motion is clamped to this range so you can't drive into the dead zone.
ENCODER_MIN = 255
ENCODER_MAX = 1023

# Conservative nudge size (encoder units) for the safe-motion smoke tests.
# ~30 units is a few degrees: visible, gentle, nowhere near the end stops.
SAFE_NUDGE = 30

# --- SCS0009 register map (all 2-byte values are BIG-ENDIAN) ---
REG_ID = 0x03             # 1 byte, 1-253 (changing IDs is intentionally not in V0)
REG_TORQUE_ENABLE = 0x28  # 1 byte: 0 = off (limp), 1 = on (holding)
REG_GOAL_POS = 0x2A       # 2 bytes BE, 0-1023
REG_EEPROM_LOCK = 0x30    # 1 byte: write 0 to unlock, 1 to lock
REG_PRESENT_POS = 0x38    # 2 bytes BE, read-only

# --- IMU (MPU-6050 family) over I2C — here for later kit growth ---
IMU_I2C_ADDR = 0x68

# --- Body mapping ---
# NOTE: which servo ID drives which leg depends on YOUR horn mounting, so this
# kit never assumes a side — it tests servos by ID and nudges around each
# joint's current position. Record your own mapping here once you've confirmed
# it, e.g. LEFT_LEG_ID = 2 / RIGHT_LEG_ID = 1.
