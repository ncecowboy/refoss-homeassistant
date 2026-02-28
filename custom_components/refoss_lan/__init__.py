"""The refoss_lan integration."""

from __future__ import annotations

import logging
from typing import Final

from homeassistant.const import Platform, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .refoss_ha.device_manager import async_build_base_device, async_build_rpc_device
from .refoss_ha.device import DeviceInfo
from .refoss_ha.device_rpc import DeviceInfoRpc
from .refoss_ha.exceptions import DeviceTimeoutError, InvalidMessage, RefossError

from .refoss_ha.controller.device import BaseDevice
from .const import CONF_LOG_LEVEL, DOMAIN, LOG_LEVEL_DEFAULT, LOG_LEVEL_OPTIONS, _LOGGER
from .coordinator import RefossDataUpdateCoordinator, RefossConfigEntry

PLATFORMS: Final = [
    Platform.SWITCH,
    Platform.SENSOR,
]


def _apply_log_level(config_entry: RefossConfigEntry) -> None:
    """Apply the configured log level to the integration logger."""
    level_name = config_entry.options.get(CONF_LOG_LEVEL, LOG_LEVEL_DEFAULT)
    if level_name not in LOG_LEVEL_OPTIONS:
        _LOGGER.warning(
            "Invalid log level '%s', falling back to %s", level_name, LOG_LEVEL_DEFAULT
        )
        level_name = LOG_LEVEL_DEFAULT
    level = getattr(logging, level_name)
    _LOGGER.setLevel(level)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: RefossConfigEntry
) -> bool:
    """Set up refoss_lan from a config entry."""
    data = config_entry.data
    if not data.get(CONF_HOST) or not data.get("device"):
        _LOGGER.debug(
            "The config entry %s invalid, please remove it and try again",
            config_entry.title,
        )
        return False
    try:
        raw_device = data["device"]
        protocol = raw_device.get("protocol", "lan")
        if protocol == "rpc":
            device_info_rpc: DeviceInfoRpc = DeviceInfoRpc.from_dict(raw_device)
            base_device: BaseDevice = await async_build_rpc_device(device_info=device_info_rpc)
        else:
            device: DeviceInfo = DeviceInfo.from_dict(raw_device)
            base_device = await async_build_base_device(device_info=device)
    except DeviceTimeoutError as err:
        raise ConfigEntryNotReady(f"Timed out connecting to {data[CONF_HOST]}") from err
    except InvalidMessage as err:
        raise ConfigEntryNotReady(f"Device data error {data[CONF_HOST]}") from err
    except RefossError as err:
        _LOGGER.debug(
            f"Device {config_entry.title} network connection failed, please check the network and try again"
        )
        raise ConfigEntryNotReady(repr(err)) from err
    except Exception as err:
        _LOGGER.exception(
            "Unexpected error setting up %s", config_entry.title
        )
        raise ConfigEntryNotReady("Unexpected error setting up device") from err

    coordinator = RefossDataUpdateCoordinator(hass, config_entry, base_device)
    await coordinator.async_config_entry_first_refresh()
    config_entry.runtime_data = coordinator
    _apply_log_level(config_entry)
    config_entry.async_on_unload(
        config_entry.add_update_listener(_async_update_options)
    )
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def _async_update_options(
    hass: HomeAssistant, config_entry: RefossConfigEntry
) -> None:
    """Handle options update."""
    _apply_log_level(config_entry)


async def async_unload_entry(
    hass: HomeAssistant, config_entry: RefossConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    return unload_ok
