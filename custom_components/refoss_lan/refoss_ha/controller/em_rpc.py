"""Em controller for the new Refoss RPC protocol (EM06P / EM16P)."""

from __future__ import annotations

import logging

from ..device_rpc import DeviceInfoRpc
from .device import BaseDevice
from ..exceptions import DeviceTimeoutError

_LOGGER = logging.getLogger(__name__)


class EmRpcMix(BaseDevice):
    """Energy-monitor controller using the new Refoss Open API.

    Wraps the ``Em.Status.Get`` RPC method and exposes the same
    ``get_value(channel, subkey)`` interface as :class:`ElectricityXMix`.

    Values returned by ``Em.Status.Get`` use milli-units:
    - current:      milliamps (mA); divide by 1000 for amperes
    - voltage:      millivolts (mV); divide by 1000 for volts
    - power:        milliwatts (mW); divide by 1000 for watts
    - power_factor: milli-units (e.g. 992 = 0.992); divide by 1000 for dimensionless 0–1
    - month_energy: kilowatt-hours (kWh, not milli-scaled)
    """

    def __init__(self, device: DeviceInfoRpc) -> None:
        """Initialise the controller."""
        self.device = device
        # channel_id → status dict from Em.Status.Get
        self.em_status: dict[int, dict] = {}
        super().__init__(device)

    # ------------------------------------------------------------------
    # State helper (same interface as ElectricityXMix)
    # ------------------------------------------------------------------

    def get_value(self, channel: int, subkey: str):
        """Return a sensor value for the given channel and sub-key, or *None*."""
        return self.em_status.get(channel, {}).get(subkey)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    async def async_handle_update(self) -> None:
        """Poll all Em channels in a single request (id=65535 = all channels)."""
        try:
            res = await self.device_info.async_execute_rpc_cmd(
                "Em.Status.Get", {"id": 65535}
            )
            if res is not None:
                # HTTP GET may or may not wrap data in a "result" key
                data = res.get("result", res)
                for entry in data.get("status", []):
                    ch = entry.get("id")
                    if ch is not None:
                        self.em_status[ch] = entry
        except DeviceTimeoutError:
            raise
        except Exception as exc:  # noqa: BLE001
            _LOGGER.debug(
                "Error updating Em status for %s: %r", self.inner_ip, exc
            )
        await super().async_handle_update()
