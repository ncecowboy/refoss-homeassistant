"""RPC device for the new Refoss Open API protocol."""

from __future__ import annotations

import asyncio
import json
import logging

from aiohttp import ClientSession, ClientTimeout

from .exceptions import DeviceTimeoutError, RefossError

LOGGER = logging.getLogger(__name__)

_PROTOCOL_KEY = "rpc"


class DeviceInfoRpc:
    """Device using the new Refoss Open API (HTTP GET /rpc/<method>)."""

    def __init__(
        self,
        name: str,
        model: str,
        dev_id: str,
        mac: str,
        fw_ver: str,
        hw_ver: str,
        ip: str,
        channels: list[int] | None = None,
    ) -> None:
        """Initialize RPC device info."""
        self.dev_name = name
        self.device_type = model.lower()
        self.uuid = dev_id
        # Normalize MAC to lowercase hex without colons
        self.mac = mac.replace(":", "").lower()
        self.fmware_version = fw_ver
        self.hdware_version = hw_ver
        self.inner_ip = ip
        self.port = "80"
        self.sub_type = ""
        self.channels: list[int] = channels if channels is not None else [1]

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    @classmethod
    async def async_probe(cls, ip: str) -> DeviceInfoRpc | None:
        """Attempt to contact the device via the RPC API.

        Returns a *DeviceInfoRpc* on success, or *None* if the host
        does not speak the new Refoss Open API.
        """
        try:
            async with ClientSession() as session, session.get(
                f"http://{ip}/rpc/Refoss.DeviceInfo.Get",
                timeout=ClientTimeout(total=5),
            ) as response:
                if response.status != 200:
                    return None
                data = await response.json(content_type=None)
                result = data.get("result", data)
                model = result.get("model", "")
                if not model:
                    return None
                mac = result.get("mac", "")
                dev_id = result.get("dev_id", "")
                fw_ver = result.get("fw_ver", "")
                hw_ver = result.get("hw_ver", "")
                name = result.get("name") or model
                # Channels are discovered later during device setup.
                return cls(
                    name=name,
                    model=model,
                    dev_id=dev_id,
                    mac=mac,
                    fw_ver=fw_ver,
                    hw_ver=hw_ver,
                    ip=ip,
                    channels=[1],
                )
        except Exception:
            LOGGER.debug(
                "RPC probe to %s failed; falling back to non-RPC discovery",
                ip,
                exc_info=True,
            )
            return None

    # ------------------------------------------------------------------
    # Command execution
    # ------------------------------------------------------------------

    async def async_execute_rpc_cmd(
        self, method: str, params: dict | None = None, timeout: int = 10
    ) -> dict | None:
        """Execute an RPC command via HTTP GET.

        Returns the parsed JSON response dict, or *None* on error.
        """
        url = f"http://{self.inner_ip}/rpc/{method}"
        query_params: dict[str, str] | None = None
        if params:
            query_params = {}
            for k, v in params.items():
                if isinstance(v, bool):
                    query_params[k] = "true" if v else "false"
                elif isinstance(v, (dict, list)):
                    query_params[k] = json.dumps(v, separators=(",", ":"))
                else:
                    query_params[k] = str(v)

        try:
            async with ClientSession() as session, session.get(
                url, params=query_params, timeout=ClientTimeout(total=timeout)
            ) as response:
                return await response.json(content_type=None)
        except asyncio.TimeoutError:
            LOGGER.debug("Timeout calling RPC method %s on %s", method, self.inner_ip)
            raise DeviceTimeoutError
        except Exception as exc:
            LOGGER.debug(
                "Error calling RPC method %s on %s: %r", method, self.inner_ip, exc
            )
            raise RefossError("Device connection failed") from exc

    # ------------------------------------------------------------------
    # Serialisation (config-entry storage)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Convert to a plain dict suitable for storage in a config entry."""
        return {
            "uuid": self.uuid,
            "devName": self.dev_name,
            "deviceType": self.device_type,
            "devSoftWare": self.fmware_version,
            "devHardWare": self.hdware_version,
            "ip": self.inner_ip,
            "port": self.port,
            "mac": self.mac,
            "subType": self.sub_type,
            "channels": self.channels,
            "protocol": _PROTOCOL_KEY,
        }

    @classmethod
    def from_dict(cls, data: dict) -> DeviceInfoRpc:
        """Reconstruct a *DeviceInfoRpc* from a stored config-entry dict."""
        return cls(
            name=data.get("devName", data.get("deviceType", "")),
            model=data.get("deviceType", ""),
            dev_id=data.get("uuid", ""),
            mac=data.get("mac", ""),
            fw_ver=data.get("devSoftWare", ""),
            hw_ver=data.get("devHardWare", ""),
            ip=data.get("ip", ""),
            channels=data.get("channels", [1]),
        )
