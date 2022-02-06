"""Base class for Nanoleaf entity."""
from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from asyncio.tasks import Task
from typing import Any

from aionanoleaf import Nanoleaf, Panel
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN


class NanoleafEnity(CoordinatorEntity):
    """Representation of a Nanoleaf entity."""

    def __init__(self, nanoleaf: Nanoleaf, coordinator: DataUpdateCoordinator) -> None:
        """Initialize an Nanoleaf entity."""
        self._nanoleaf = nanoleaf
        self._coordinator = coordinator
        self._attr_device_info: DeviceInfo = DeviceInfo(
            manufacturer=nanoleaf.manufacturer,
            sw_version=nanoleaf.firmware_version,
            configuration_url=f"http://{nanoleaf.host}",
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self._attr_available

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_available = self._coordinator.last_update_success
        self.async_write_ha_state()


class NanoleafDeviceEntity(NanoleafEnity):
    """Representation of a Nanoleaf device entity."""

    def __init__(self, nanoleaf: Nanoleaf, coordinator: DataUpdateCoordinator) -> None:
        """Initialize an Nanoleaf entity."""
        super().__init__(nanoleaf, coordinator)
        self._attr_device_info.update(
            DeviceInfo(
                identifiers={(DOMAIN, nanoleaf.serial_no)},
                name=nanoleaf.name,
                model=nanoleaf.model,
            )
        )


class NanoleafPanelEntity(NanoleafEnity):
    """Representation of a Nanoleaf panel entity."""

    _attr_should_poll = False

    def __init__(self, nanoleaf: Nanoleaf, coordinator: DataUpdateCoordinator, panel: Panel) -> None:
        """Initialize an Nanoleaf panel entity."""
        super().__init__(nanoleaf, coordinator)
        self._nanoleaf = nanoleaf
        self._panel = panel
        self._attr_device_info.update(
            DeviceInfo(
                identifiers={(DOMAIN, f"{nanoleaf.serial_no}_{panel.id}")},
                via_device=(DOMAIN, nanoleaf.serial_no),
                name=f"{nanoleaf.name} {panel.shape.name} {panel.id}",
                model=panel.shape.name,
            )
        )


class NanoleafPanelTouchEntity(NanoleafPanelEntity, ABC):
    """Representation of a Nanoleaf touch sensor."""

    _reset_task: Task | None = None
    _should_not_reset_state: Any

    def __init__(self, nanoleaf: Nanoleaf, coordinator: DataUpdateCoordinator, panel: Panel, sensor_type: str) -> None:
        """Initialize an Nanoleaf binary sensor."""
        super().__init__(nanoleaf, coordinator, panel)
        self._attr_unique_id = f"{nanoleaf.serial_no}_{panel.id}_{sensor_type}"
        self._attr_name = f"{nanoleaf.name} {panel.shape.name} {panel.id} {sensor_type}"

    async def _async_handle_touch(self, touch_type: str) -> None:
        """Handle panel touch event."""
        self._set_state(touch_type)
        self.async_write_ha_state()
        if self._reset_task is not None and not self._reset_task.done():
            self._reset_task.cancel()
        if self.state != self._should_not_reset_state:
            self._reset_task = asyncio.create_task(self._reset_after_timeout())

    @abstractmethod
    def _set_state(self, touch_type: str) -> None:
        """Set the entity state."""

    @abstractmethod
    def _reset_entity(self) -> None:
        """Reset entity state."""

    async def async_added_to_hass(self) -> None:
        """Handle entity being added to Home Assistant."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{DOMAIN}_touch_panel_{self._nanoleaf.serial_no}_{self._panel.id}",
                self._async_handle_touch,
            )
        )

    async def _reset_after_timeout(self) -> None:
        """Reset entity state after timeout."""
        # Reset entity if no event is detected for 0.4 seconds
        try:
            await asyncio.sleep(0.4)
        except asyncio.CancelledError:
            return
        self._reset_entity()
        self.async_write_ha_state()
