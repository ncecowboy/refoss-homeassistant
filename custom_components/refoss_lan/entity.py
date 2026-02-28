"""Entity object for shared properties of refoss_lan entities."""

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import RefossDataUpdateCoordinator
from .const import DOMAIN


class RefossEntity(CoordinatorEntity[RefossDataUpdateCoordinator]):
    """Refoss entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RefossDataUpdateCoordinator,
        channel: int,
        channel_name: str | None = None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self.coordinator = coordinator
        mac = coordinator.device.mac
        self.channel = channel
        self._attr_unique_id = f"{mac}_{channel}"

        if channel_name is not None:
            # Per-channel sub-device linked to the parent integration device via via_device.
            # Use the numeric channel as the stable identifier, not the display name.
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{mac}_{channel}")},
                manufacturer="Refoss",
                name=channel_name,
                model=coordinator.device.device_type,
                sw_version=coordinator.device.fmware_version,
                hw_version=coordinator.device.hdware_version,
                via_device=(DOMAIN, mac),
            )
        else:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, mac)},
                connections={(CONNECTION_NETWORK_MAC, mac)},
                manufacturer="Refoss",
                name=coordinator.device.device_type,
                model=coordinator.device.device_type,
                sw_version=coordinator.device.fmware_version,
                hw_version=coordinator.device.hdware_version,
            )
