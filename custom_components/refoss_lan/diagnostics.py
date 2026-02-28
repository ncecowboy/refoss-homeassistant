"""Diagnostics support for Refoss LAN."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .coordinator import RefossConfigEntry
from .refoss_ha.controller.electricity import ElectricityXMix
from .refoss_ha.controller.em_rpc import EmRpcMix
from .refoss_ha.controller.switch_rpc import SwitchRpcMix


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: RefossConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = config_entry.runtime_data
    device = coordinator.device

    device_info: dict[str, Any] = {
        "device_type": device.device_type,
        "inner_ip": device.inner_ip,
        "mac": device.mac,
        "firmware_version": device.fmware_version,
        "hardware_version": device.hdware_version,
        "channels": device.channels,
    }

    raw_data: dict[str, Any] = {}
    if isinstance(device, ElectricityXMix):
        raw_data["electricity_status"] = device.electricity_status
    elif isinstance(device, EmRpcMix):
        raw_data["em_status"] = device.em_status
    elif isinstance(device, SwitchRpcMix):
        raw_data["switch_status"] = device.switch_status

    return {
        "device_info": device_info,
        "raw_data": raw_data,
    }
