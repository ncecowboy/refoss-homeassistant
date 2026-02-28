"""ElectricityXMix."""

import logging

from ..enums import Namespace
from ..device import DeviceInfo
from .device import BaseDevice

_LOGGER = logging.getLogger(__name__)

# Fields that the old LAN protocol *may* include but often omits on EM06/EM16.
_OPTIONAL_ELECTRICITY_KEYS = {"factor", "mConsume"}


class ElectricityXMix(BaseDevice):
    """A device."""

    def __init__(self, device: DeviceInfo):
        """Initialize."""
        self.device = device
        self.electricity_status = {}
        self._electricity_keys_logged = False
        super().__init__(device)

    def get_value(self, channel: int, subkey: str):
        """
        Returns the value for the given channel and subkey, or None if not found.
        """
        channel_status = self.electricity_status.get(channel, None)
        if channel_status is not None and subkey in channel_status:
            return channel_status.get(subkey, None)
        return None

    async def async_handle_update(self):
        """Update device state,65535 get all channel."""

        payload = {"electricity": {"channel": 65535}}
        res = await self.async_execute_cmd(
            device_uuid=self.uuid,
            method="GET",
            namespace=Namespace.CONTROL_ELECTRICITYX,
            payload=payload,
        )
        if res is not None:
            data = res.get("payload", {})
            payload = data.get("electricity")
            if payload is None:
                _LOGGER.debug(
                    f"{data} could not find 'electricity' attribute in push notification data"
                )

            elif isinstance(payload, list):
                for state in payload:
                    channel = state["channel"]
                    self.electricity_status[channel] = state
                if payload and not self._electricity_keys_logged:
                    self._electricity_keys_logged = True
                    available = set(payload[0].keys()) - {"channel"}
                    missing = _OPTIONAL_ELECTRICITY_KEYS - available
                    if missing:
                        _LOGGER.warning(
                            "Device %s (%s) does not provide %s in its "
                            "ElectricityX response; those sensors will show "
                            "as Unknown. Available fields: %s",
                            self.inner_ip,
                            self.device_type,
                            sorted(missing),
                            sorted(available),
                        )
                    else:
                        _LOGGER.debug(
                            "Device %s (%s) ElectricityX fields: %s",
                            self.inner_ip,
                            self.device_type,
                            sorted(available),
                        )
        await super().async_handle_update()
