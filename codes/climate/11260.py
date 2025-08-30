DEVICE_DATA = {
  "manufacturer": "Toshiba",
  "supportedModels": [
    "WH-D6B",
    "RAS-221B", "RAS-251B", "RAS-361B", "RAS-401S",
    "RAS-502S", "RAS-225G", "RAS-255G", "RAS-285G",
    "RAS-365G", "RAS-405G", "RAS-506G", "RAS-401B",
    "RAS-502B", "RAS-221S", "RAS-251S", "RAS-281S",
    "RAS-361S",
  ],
  "commandsEncoding": "Generic",
  "minTemperature": {
    "heat": 17,
    "dry": 17,
    "cool": 17,
    "auto": -5,
  },
  "maxTemperature": {
    "heat": 30,
    "dry": 30,
    "cool": 30,
    "auto": 5,
  },
  "precision": 1,
  "operationModes": [
    "auto",
    "cool",
    "heat",
    "dry",
    "fan_only",
  ],
  "fanModes": [
    "auto",
    "mild",
    "quiet",
    "low",
    "medium",
    "high",
  ],
}

def command(hvac_mode, swing_mode, fan_mode, temp):
    c_fan_mode = {
        "auto": 0x00,
        "mild": 0x00,
        "quiet": 0x20,
        "low": 0x40,
        "medium": 0x80,
        "high": 0xc0,
    }[fan_mode]

    c_mode = {
        "off": 7,
        "auto": 0,
        "cool": 1,
        "dry": 2,
        "heat": 3,
        "fan_only": 4,
    }[hvac_mode]

    if hvac_mode == "auto":
      c_temp = int(temp) + 7 # standard -> 7
    else:
      c_temp = int(temp) - 17 # 17 -> 0

    if fan_mode == "mild":
      d = [0xf2, 0x04, 0x09, c_temp << 4, c_mode | c_fan_mode, 0, 3]
    else:
      d = [0xf2, 0x03, 0x01, c_temp << 4, c_mode | c_fan_mode, 0]

    return ("necb", "ph=4367,pl=4395,cm=2,pg=5249,ck=2", [d, d])
