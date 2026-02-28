"""BaseDevice."""

from __future__ import annotations

import json
import logging
from typing import Union

from ..enums import Namespace
from ..device import DeviceInfo

_LOGGER = logging.getLogger(__name__)


class BaseDevice:
    """ "BaseDevice."""

    def __init__(self, device_info: DeviceInfo):
        """Construct BaseDevice."""
        self.device_info = device_info
        self.uuid = device_info.uuid
        self.dev_name = device_info.dev_name
        self.device_type = device_info.device_type
        self.fmware_version = device_info.fmware_version
        self.hdware_version = device_info.hdware_version
        self.inner_ip = device_info.inner_ip
        self.port = device_info.port
        self.mac = device_info.mac
        self.sub_type = device_info.sub_type
        raw_channels = (
            device_info.channels
            if isinstance(device_info.channels, list)
            else json.loads(device_info.channels)
        )
        if raw_channels and isinstance(raw_channels[0], dict):
            self.channels = []
            for i, c in enumerate(raw_channels):
                ch = c.get("channel")
                if ch is None:
                    _LOGGER.debug(
                        "Channel dict missing 'channel' key at index %d, using index as fallback: %s",
                        i,
                        c,
                    )
                    ch = i
                self.channels.append(int(ch))
        else:
            self.channels = [int(c) for c in raw_channels] if raw_channels else []

    async def async_handle_update(self):
        """update device state."""

    async def async_execute_cmd(
        self,
        device_uuid: str,
        method: str,
        namespace: Union[Namespace, str],
        payload: dict,
        timeout: int = 5,
    ):
        """Execute command."""
        res = await self.device_info.async_execute_cmd(
            device_uuid=device_uuid,
            method=method,
            namespace=namespace,
            payload=payload,
            timeout=timeout,
        )
        return res
