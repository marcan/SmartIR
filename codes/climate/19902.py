DEVICE_DATA = {
  "manufacturer": "Sharp",
  "supportedModels": [
    "A940JB",
    "AC-225FD",
    "AC-255FD",
    "AC-285FD",
  ],
  "commandsEncoding": "Generic",
  "minTemperature": {
    "cool": 18,
    "heat": 18,
    "dry": -2,
  },
  "maxTemperature": {
    "cool": 32,
    "heat": 32,
    "dry": 2,
  },
  "precision": 1.0,
  "operationModes": [
    "cool",
    "heat",
    "dry",
    "fan_only",
  ],
  "fanModes": [
    "auto",
    "low",
    "low_medium",
    "medium",
    "high",
  ],
  "swingModes": [
    "on",
    "auto",
    "top",
    "upper",
    "middle",
    "lower",
    "bottom",
  ],
  "toggles": [
    "self_cleaning",
    "power_limit",
    "ionizer",
  ],
  "actions": [
    "start_self_cleaning",
    "toggle_brightness",
  ]
}

def command(hvac_mode, swing_mode, fan_mode, temp, self_cleaning=True, power_limit=False, ionizer=False, action=None):
    if action == "start_self_cleaning" and hvac_mode != "off":
        # Only allowed while off
        action = None

    if action == "toggle_brightness" and hvac_mode == "off":
        # Only allowed while on
        action = None

    if hvac_mode == "dry":
        # others disallowed
        fan_mode = "auto"

    c_mode = {
        "off":  0x1, # arbitrary
        "heat": 0x1,
        "cool": 0x2,
        "dry":  0x3,
        # called ion mode in remote, but really just this + forces ion on. ion off also works as fan only.
        "fan_only":  0x4,
    }[hvac_mode]

    if action == "start_self_cleaning":
      c_mode = 0xb

    c_fan_direction = {
        "on":       0xf,
        "auto":     0x8,
        "top":      0x9,
        "upper":    0xa,
        "middle":   0xb,
        "lower":    0xc,
        "bottom":   0xd,
    }[swing_mode]

    # Weird mapping, top is disallowed in heat mode and rest are shifted down
    if hvac_mode == "heat" and 0xa <= c_fan_direction <= 0xd:
        c_fan_direction -= 1

    # 1: power on
    # 2: power off
    # 3: change state
    # 6: toggle light mode
    # d: change single setting (changes meaning of rest of packet)
    c_op = 2 if hvac_mode == "off" else 1

    if action == "toggle_brightness":
      c_op = 6

    c_fan_mode = {
        "auto":         2,
        "low":          3,
        "low_medium":   5,
        "medium":       7,
        "high":         6,
    }[fan_mode]

    if action == "start_self_cleaning":
        c_temp = 0
    elif hvac_mode in ("off", "fan_only"):
        c_temp = 1 # dummy, actually last state
    elif hvac_mode == "dry":
        # weird offset mode
        c_temp = [10, 9, 0, 1, 2][int(temp) + 2] << 4
    else:
        c_temp = int(temp) - 17

    c_flags = 0x80
    if power_limit:
        c_flags |= 0x10
    if self_cleaning and action != "start_self_cleaning":
        c_flags |= 0x20

    d = [
        0xaa, 0x5a, 0xcf, 0x10,
        c_temp,
        0x01 | (c_op << 4),
        c_mode | (c_fan_mode << 4),
        0x80 if action == "toggle_brightness" else 0,
        c_fan_direction,
        c_flags,
        0x00, # key group pressed, should not matter
        0xe0 | (4 if ionizer else 0),
        0x01
    ]

    # 4-bit XOR checksum
    csum = 0
    for i in d:
        csum ^= i & 0xf
        csum ^= (i >> 4)

    d[-1] |= csum << 4

    # Original remote only sends once, but let's be redundant
    return ("nec", "tp=461,ph=3729", [d, d])
