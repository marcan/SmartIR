DEVICE_DATA = {
  "manufacturer": "Mitsubishi",
  "supportedModels": [
    "RH151",
    "MSZ-GV225", "MSZ-GV255", "MSZ-GV285", "MSZ-GV365",
    "MSZ-GV405S", "MSZ-GV565S", "MSZ-GV2217-W", "MSZ-GV2217-T",
    "MSZ-GV2517-W", "MSZ-GV2517-T", "MSZ-GV2817-W", "MSZ-GV2817-T",
    "MSZ-GV3617-W", "MSZ-GV3617-T", "MSZ-GV4017S-W"
  ],
  "commandsEncoding": "Generic",
  "minTemperature": {
    "cool": 16,
    "heat": 16,
    "dry": -1,
  },
  "maxTemperature": {
    "cool": 31,
    "heat": 31,
    "dry": 1,
  },
  "precision": 1.0,
  "operationModes": [
    "cool",
    "heat",
    "dry",
  ],
  "fanModes": [
    "auto",
    "low",
    "medium",
    "high",
    "powerful",
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
  ]
}

def command(hvac_mode, swing_mode, fan_mode, temp, self_cleaning=True, power_limit=False):
    c_fan_mode = {
        "auto":     0,
        "low":      1,
        "medium":   2,
        "high":     3,
        "powerful": 3,
    }[fan_mode]

    if swing_mode == "on":
        c_fan_mode |= 0xf

    c_fan_direction = {
        "auto":     0,
        "top":      1,
        "upper":    2,
        "middle":   3,
        "lower":    4,
        "bottom":   5,
        "on":       7,
    }[swing_mode]

    c_mode = {
        "off":  0x08, # whatever?
        "heat": 0x08,
        "dry":  0x10,
        "cool": 0x18,
    }[hvac_mode]

    c_sub_mode = {
        "off":  0x30, # whatever?
        "heat": 0x30,
        "dry":  0x30 + (int(temp) + 1) * 2,
        "cool": 0x36,
    }[hvac_mode]

    c_temp_relative = hvac_mode in ("dry", "auto")

    if hvac_mode in ("off", "dry"):
        c_temp = 8
    else:
        c_temp = int(temp) - 16

    c_beep_count = 1

    d = [
        0x23, 0xcb, 0x26, 0x01,
        0,
        0x20 if hvac_mode != "off" else 0,
        c_mode | (0x4 if power_limit else 0),
        c_temp,
        c_sub_mode,
        (c_beep_count << 6) | c_fan_mode | (c_fan_direction << 3),
        0, 0, 0, 0,
        0x04 if self_cleaning else 0,
        0x10 if fan_mode == "powerful" else 0,
        0
    ]

    return ("nec", "tp=445,ph=3420,pg=13245,ck=1", [d, d])
