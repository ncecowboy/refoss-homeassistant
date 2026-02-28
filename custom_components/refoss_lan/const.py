"""const."""

from __future__ import annotations

from logging import Logger, getLogger

_LOGGER: Logger = getLogger(__package__)

DISCOVERY_TIMEOUT = 8
UPDATE_INTERVAL = "update_interval"


DOMAIN = "refoss_lan"

MAX_ERRORS = 4

# Energy monitoring sensor type keys
SENSOR_EM = "em"
# New RPC protocol: Em.Status.Get values are in milli-units (mA, mV, mW; pf ×1000; kWh for energy)
SENSOR_EM_RPC = "em_rpc"
# New RPC protocol: Switch.Status.Get energy values (mW, mV, mA, Wh)
SENSOR_SWITCH_RPC = "switch_rpc"

CHANNEL_DISPLAY_NAME: dict[str, dict[int, str]] = {
    "em06": {
        1: "A1",
        2: "B1",
        3: "C1",
        4: "A2",
        5: "B2",
        6: "C2",
    },
    "em16": {
        1: "A1",
        2: "A2",
        3: "A3",
        4: "A4",
        5: "A5",
        6: "A6",
        7: "B1",
        8: "B2",
        9: "B3",
        10: "B4",
        11: "B5",
        12: "B6",
        13: "C1",
        14: "C2",
        15: "C3",
        16: "C4",
        17: "C5",
        18: "C6",
    },
    "em06p": {
        1: "A1",
        2: "B1",
        3: "C1",
        4: "A2",
        5: "B2",
        6: "C2",
    },
    "em16p": {
        1: "A1",
        2: "A2",
        3: "A3",
        4: "A4",
        5: "A5",
        6: "A6",
        7: "B1",
        8: "B2",
        9: "B3",
        10: "B4",
        11: "B5",
        12: "B6",
        13: "C1",
        14: "C2",
        15: "C3",
        16: "C4",
        17: "C5",
        18: "C6",
    },
}
