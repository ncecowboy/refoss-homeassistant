"""Support for refoss_lan sensors."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import CHANNEL_DISPLAY_NAME, SENSOR_EM, SENSOR_EM_RPC, SENSOR_SWITCH_RPC
from .entity import RefossEntity
from .refoss_ha.controller.electricity import ElectricityXMix
from .refoss_ha.controller.em_rpc import EmRpcMix
from .refoss_ha.controller.switch_rpc import SwitchRpcMix
from .coordinator import RefossDataUpdateCoordinator, RefossConfigEntry

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class RefossSensorEntityDescription(SensorEntityDescription):
    """Describes Refoss sensor entity."""

    subkey: str | None = None
    fn: Callable[[float], float] | None = None

SENSORS: dict[str, tuple[RefossSensorEntityDescription, ...]] = {
    SENSOR_EM: (
        RefossSensorEntityDescription(
            key="power",
            translation_key="em_power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPower.WATT,
            suggested_display_precision=2,
            subkey="power",
            fn=lambda x: x / 1000.0,
        ),
        RefossSensorEntityDescription(
            key="voltage",
            translation_key="em_voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
            suggested_display_precision=2,
            suggested_unit_of_measurement=UnitOfElectricPotential.VOLT,
            subkey="voltage",
        ),
        RefossSensorEntityDescription(
            key="current",
            translation_key="em_current",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
            suggested_display_precision=2,
            suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            subkey="current",
        ),
        RefossSensorEntityDescription(
            key="factor",
            translation_key="em_power_factor",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            subkey="factor",
        ),
        RefossSensorEntityDescription(
            key="energy",
            translation_key="em_this_month_energy",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=2,
            subkey="mConsume",
            fn=lambda x: max(0, x),
        ),
        RefossSensorEntityDescription(
            key="energy_returned",
            translation_key="em_this_month_energy_returned",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=2,
            subkey="mConsume",
            fn=lambda x: abs(x) if x < 0 else 0,
        ),
        RefossSensorEntityDescription(
            key="today_energy",
            translation_key="em_today_energy",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=2,
            subkey="today",
            fn=lambda x: max(0, x),
        ),
        RefossSensorEntityDescription(
            key="week_energy",
            translation_key="em_week_energy",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=2,
            subkey="week",
            fn=lambda x: max(0, x),
        ),
    ),
    # New RPC protocol – Em.Status.Get returns milli-units (mA, mV, mW; pf ×1000; kWh for energy)
    SENSOR_EM_RPC: (
        RefossSensorEntityDescription(
            key="power",
            translation_key="em_power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPower.WATT,
            suggested_display_precision=2,
            subkey="power",
            fn=lambda x: x / 1000.0,
        ),
        RefossSensorEntityDescription(
            key="voltage",
            translation_key="em_voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
            suggested_display_precision=2,
            suggested_unit_of_measurement=UnitOfElectricPotential.VOLT,
            subkey="voltage",
        ),
        RefossSensorEntityDescription(
            key="current",
            translation_key="em_current",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
            suggested_display_precision=3,
            suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            subkey="current",
        ),
        RefossSensorEntityDescription(
            key="factor",
            translation_key="em_power_factor",
            device_class=SensorDeviceClass.POWER_FACTOR,
            state_class=SensorStateClass.MEASUREMENT,
            suggested_display_precision=2,
            subkey="power_factor",
            fn=lambda x: x / 1000.0,
        ),
        RefossSensorEntityDescription(
            key="energy",
            translation_key="em_this_month_energy",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
            suggested_display_precision=3,
            subkey="month_energy",
            fn=lambda x: max(0.0, x),
        ),
    ),
    # New RPC protocol – Switch.Status.Get energy data (mW, mV, mA, Wh)
    SENSOR_SWITCH_RPC: (
        RefossSensorEntityDescription(
            key="power",
            translation_key="power",
            device_class=SensorDeviceClass.POWER,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfPower.WATT,
            suggested_display_precision=2,
            subkey="apower",
            fn=lambda x: x / 1000.0,
        ),
        RefossSensorEntityDescription(
            key="voltage",
            translation_key="voltage",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
            suggested_display_precision=2,
            suggested_unit_of_measurement=UnitOfElectricPotential.VOLT,
            subkey="voltage",
        ),
        RefossSensorEntityDescription(
            key="current",
            translation_key="current",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
            suggested_display_precision=2,
            suggested_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            subkey="current",
        ),
        RefossSensorEntityDescription(
            key="energy",
            translation_key="this_month_energy",
            device_class=SensorDeviceClass.ENERGY,
            state_class=SensorStateClass.TOTAL_INCREASING,
            native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
            suggested_display_precision=2,
            subkey="month_consumption",
            fn=lambda x: max(0, x),
        ),
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: RefossConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Refoss device from a config entry."""
    coordinator = config_entry.runtime_data
    device = coordinator.device
    if not isinstance(device, (ElectricityXMix, EmRpcMix, SwitchRpcMix)):
        _LOGGER.warning(
            "Unrecognised device class %s for %s; no sensors will be created",
            type(device).__name__,
            device.device_type,
        )
        return

    def init_device(device: ElectricityXMix | EmRpcMix | SwitchRpcMix):
        """Register the device."""
        if isinstance(device, ElectricityXMix):
            sensor_type = SENSOR_EM
        elif isinstance(device, EmRpcMix):
            sensor_type = SENSOR_EM_RPC
        else:
            sensor_type = SENSOR_SWITCH_RPC
        descriptions: tuple[RefossSensorEntityDescription, ...] = SENSORS.get(
            sensor_type, ()
        )
        device_type = device.device_type
        # Only create per-channel sub-devices for device types that have a known
        # channel name mapping; this ensures the parent device registered in
        # __init__.py always exists before sub-devices reference it via via_device.
        use_sub_devices = device_type in CHANNEL_DISPLAY_NAME
        async_add_entities(
            RefossSensor(
                coordinator=coordinator,
                channel=channel,
                description=description,
                channel_name=(
                    CHANNEL_DISPLAY_NAME.get(device_type, {}).get(channel, str(channel))
                    if use_sub_devices
                    else None
                ),
            )
            for channel in device.channels
            for description in descriptions
        )

    init_device(device)


class RefossSensor(RefossEntity, SensorEntity):
    """Refoss Sensor Device."""

    entity_description: RefossSensorEntityDescription

    def __init__(
        self,
        coordinator: RefossDataUpdateCoordinator,
        channel: int,
        description: RefossSensorEntityDescription,
        channel_name: str | None = None,
    ) -> None:
        """Init Refoss sensor."""
        super().__init__(coordinator, channel, channel_name)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}{description.key}"
        if channel_name is None:
            device_type = coordinator.device.device_type
            name = CHANNEL_DISPLAY_NAME.get(device_type, {}).get(channel, str(channel))
            self._attr_translation_placeholders = {"channel_name": name}

    @property
    def native_value(self) -> StateType:
        """Return the native value."""
        value = self.coordinator.device.get_value(
            self.channel, self.entity_description.subkey
        )
        if value is None:
            return None
        if self.entity_description.fn:
            return self.entity_description.fn(value)
        return value
