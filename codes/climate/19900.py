DEVICE_DATA = {
  "manufacturer": "Daikin",
  "supportedModels": [
    "ARC478A30",
    "F22TTES-W", "F22TTES-W5", "F22TTES-W7", "F22UTES-W",
    "F22UTES-W5", "F22UTES-W7", "F22VTES-W", "F22VTES-W5",
    "F22VTES-W7", "F22WTES-W", "F22WTES-W5", "F22WTES-W7",
    "F25TTES-W", "F25TTES-W5", "F25TTES-W7", "F25UTES-W",
    "F25UTES-W5", "F25UTES-W7", "F25VTES-W", "F25VTES-W5",
    "F25VTES-W7", "F25WTES-W", "F25WTES-W5", "F25WTES-W7",
    "F28TTES-W", "F28TTES-W5", "F28TTES-W7", "F28TTEV-W",
    "F28UTES-W", "F28UTES-W5", "F28UTES-W7", "F28UTEV-W",
    "F28VTES-W", "F28VTES-W5", "F28VTES-W7", "F28VTEV-W",
    "F28WTES-W", "F28WTES-W5", "F28WTES-W7", "F28WTEV-W"
    "F36TTES-W", "F36TTES-W5", "F36TTES-W7", "F36TTEV-W",
    "F36UTES-W", "F36UTES-W5", "F36UTES-W7", "F36UTEV-W",
    "F36VTES-W", "F36VTES-W5", "F36VTES-W7", "F36VTEV-W",
    "F36WTES-W", "F36WTES-W5", "F36WTES-W7", "F36WTEV-W",
    "F40TTEP-W", "F40TTEV-W", "F40UTEP-W", "F40UTEV-W",
    "F40VTEP-W", "F40VTEV-W", "F40WTEP-W", "F40WTEV-W",
    "F56TTEP-W", "F56TTEV-W", "F56UTEP-W", "F56UTEV-W",
    "F56VTEP-W", "F56VTEV-W", "F56WTEP-W", "F56WTEV-W",
    "S22TTES-W", "S22TTES-W5", "S22TTES-W7", "S22UTES-W",
    "S22UTES-W5", "S22UTES-W7", "S22VTES-W", "S22WTES-W",
    "S25TTES-W", "S25TTES-W5", "S25TTES-W7", "S25UTES-W",
    "S25UTES-W5", "S25UTES-W7", "S25VTES-W", "S25WTES-W",
    "S28TTES-W", "S28TTES-W5", "S28TTES-W7", "S28TTEV-W",
    "S28UTES-W", "S28UTES-W5", "S28UTES-W7", "S28UTEV-W",
    "S28VTES-W", "S28VTEV-W", "S28WTES-W", "S28WTEV-W",
    "S36TTES-W", "S36TTES-W5", "S36TTES-W7", "S36TTEV-W",
    "S36UTES-W", "S36UTES-W5", "S36UTES-W7", "S36UTEV-W",
    "S36VTES-W", "S36VTEV-W", "S36WTES-W", "S36WTEV-W",
    "S40TTEP-W", "S40TTEV-W", "S40UTEP-W", "S40UTEV-W",
    "S40VTEP-W", "S40VTEV-W", "S40WTEP-W", "S40WTEV-W",
    "S56TTEP-W", "S56TTEV-W", "S56UTEP-W", "S56UTEV-W",
    "S56VTEP-W", "S56VTEV-W", "S56WTEP-W", "S56WTEV-W"
  ],
  "commandsEncoding": "Generic",
  "minTemperature": {
    "cool": 18,
    "heat": 14,
    "auto": -5,
    "dry": -2,
  },
  "maxTemperature": {
    "cool": 32,
    "heat": 30,
    "auto": 5,
    "dry": 2,
  },
  "precision": 0.5,
  "operationModes": [
    "auto",
    "cool",
    "heat",
    "dry",
    "fan_only"
  ],
  "fanModes": [
    "auto",
    "quiet",
    "low",
    "low_medium",
    "medium",
    "medium_high",
    "high"
  ],
  "swingModes": [
    "on",
    "nice",
    "top",
    "upper",
    "middle",
    "lower",
    "bottom",
  ]
}

def command(hvac_mode, swing_mode, fan_mode, temp, cleaning_enabled=False):
    if swing_mode == "nice":
        fan_mode = "auto"
    if hvac_mode == "auto" and fan_mode not in ("auto", "quiet"):
        fan_mode = "auto"

    c_fan_mode = {
        "auto":         0xa0,
        "quiet":        0xb0,
        "low":          0x30,
        "low_medium":   0x40,
        "medium":       0x50,
        "medium_high":  0x60,
        "high":         0x70,
    }[fan_mode]

    if swing_mode == "on":
        c_fan_mode |= 0xf

    c_fan_direction = {
        "on": 0,
        "top": 1,
        "upper": 2,
        "middle": 3,
        "lower": 4,
        "bottom": 5,
        "nice": 0,
    }[swing_mode]

    c_mode = {
        "off": 0x38,
        "auto": 0x09,
        "dry": 0x29,
        "cool": 0x39,
        "heat": 0x49,
        "fan_only": 0x69,
    }[hvac_mode]

    c_temp_relative = hvac_mode in ("dry", "auto")

    if hvac_mode in ("off", "fan_only"):
        c_temp = 50 # dummy
    elif c_temp_relative:
        c_temp = 0xc0 | (int(temp * 2) & 0x1f)
    else:
        c_temp = int(temp * 2)

    return ("nec", "tp=421,t0=448,ph=3494,a=-1,pg=34698,b=6,bh=448,bl=446,ck=1", [
        [
            0x11, 0xda, 0x27, 0x00, 0x02, 0, 0, 0, 0,
            0x03, # Button pressed, probably unimportant
            0,
            0x80 if hvac_mode == 'off' else 0,
            c_fan_direction << 4,
            0,
            0x40 if cleaning_enabled else 0,
            0,0,0,0
        ],
        [
            0x11, 0xda, 0x27, 0, 0,
            c_mode,
            c_temp,
            0x80 if c_temp_relative else 0,
            c_fan_mode,
            0, 0, 0x06, 0x60, 0, 0, 0xc3,
            1 if swing_mode == "nice" else 0,
            0
        ],
    ])
