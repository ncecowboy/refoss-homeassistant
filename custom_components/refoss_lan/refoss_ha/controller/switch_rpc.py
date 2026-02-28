"""Switch controller for the new Refoss RPC protocol."""

from __future__ import annotations

import logging

from ..device_rpc import DeviceInfoRpc
from .device import BaseDevice
from ..exceptions import DeviceTimeoutError

_LOGGER = logging.getLogger(__name__)


class SwitchRpcMix(BaseDevice):
    """Switch controller using the new Refoss Open API.

    Wraps the ``Switch.Status.Get`` / ``Switch.Action.Set`` RPC methods and
    exposes the same interface as :class:`ToggleXMix` so the existing
    switch and sensor entity code can treat both device types uniformly.
    """

    def __init__(self, device: DeviceInfoRpc) -> None:
        """Initialise the controller."""
        self.device = device
        # channel_id → status dict from Switch.Status.Get
        self.switch_status: dict[int, dict] = {}
        super().__init__(device)

    # ------------------------------------------------------------------
    # State helpers (same interface as ToggleXMix)
    # ------------------------------------------------------------------

    def is_on(self, channel: int = 1) -> bool | None:
        """Return *True* if the given channel is on, *False* if off, *None* if unknown."""
        return self.switch_status.get(channel, {}).get("output")

    def get_value(self, channel: int, subkey: str):
        """Return a sensor value for the given channel and sub-key, or *None*."""
        return self.switch_status.get(channel, {}).get(subkey)

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    async def async_handle_update(self) -> None:
        """Poll each switch channel for current status."""
        for channel in self.channels:
            try:
                res = await self.device_info.async_execute_rpc_cmd(
                    "Switch.Status.Get", {"id": channel}
                )
                if res is not None:
                    # HTTP GET may or may not wrap data in a "result" key
                    data = res.get("result", res)
                    self.switch_status[channel] = data
            except DeviceTimeoutError:
                raise
            except Exception as exc:  # noqa: BLE001
                _LOGGER.debug(
                    "Error updating switch channel %d for %s: %r",
                    channel,
                    self.inner_ip,
                    exc,
                )
        await super().async_handle_update()

    # ------------------------------------------------------------------
    # Control
    # ------------------------------------------------------------------

    async def async_turn_on(self, channel: int = 1) -> None:
        """Turn channel on."""
        await self._send_action(channel, "on")

    async def async_turn_off(self, channel: int = 1) -> None:
        """Turn channel off."""
        await self._send_action(channel, "off")

    async def async_toggle(self, channel: int = 1) -> None:
        """Toggle channel."""
        await self._send_action(channel, "toggle")

    async def _send_action(self, channel: int, action: str) -> None:
        """Send a Switch.Action.Set command and update cached state."""
        try:
            res = await self.device_info.async_execute_rpc_cmd(
                "Switch.Action.Set", {"id": channel, "action": action}
            )
            if res is not None:
                data = res.get("result", res)
                was_on: bool | None = data.get("was_on")
                if was_on is not None:
                    # Derive new state from the previous state + action
                    new_state: bool | None = None
                    if action == "on":
                        new_state = True
                    elif action == "off":
                        new_state = False
                    elif action == "toggle":
                        new_state = not was_on
                    if new_state is not None:
                        if channel not in self.switch_status:
                            self.switch_status[channel] = {}
                        self.switch_status[channel]["output"] = new_state
        except DeviceTimeoutError:
            pass
