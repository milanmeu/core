"""Support for Nanoleaf sensors."""
from __future__ import annotations

from aionanoleaf import Nanoleaf, Panel

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEGREE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import NanoleafEntryData
from .const import DOMAIN
from .entity import NanoleafPanelEntity

PANEL_SENSOR_TYPES = (
    SensorEntityDescription(
        key="x_coordinate",
        name="X Coordinate",
        icon="mdi:axis-x-arrow",
    ),
    SensorEntityDescription(
        key="y_coordinate",
        name="Y Coordinate",
        icon="mdi:axis-y-arrow",
    ),
    SensorEntityDescription(
        key="orientation",
        name="Orientation",
        icon="mdi:circular-arrows",
        native_unit_of_measurement=DEGREE,
    ),
)

SHAPE_SENSOR_TYPES = (
    SensorEntityDescription(
        key="name",
        name="Shape",
        icon="mdi:shape",
    ),
    SensorEntityDescription(
        key="side_length",
        name="Side Length",
        icon="mdi:arrow-expand-horizontal",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Nanoleaf binary sensor."""
    entry_data: NanoleafEntryData = hass.data[DOMAIN][entry.entry_id]
    entities: list[NanoleafSensorEntity] = []
    nanoleaf = entry_data.device
    for panel in nanoleaf.panels:
        for description in PANEL_SENSOR_TYPES:
            entities.append(PanelSensorEntity(nanoleaf, panel, description))
        for description in SHAPE_SENSOR_TYPES:
            entities.append(ShapeSensorEntity(nanoleaf, panel, description))
        entities.append(TouchSensorEntity(nanoleaf, panel))
    async_add_entities(entities)


class TouchSensorEntity(NanoleafPanelEntity, SensorEntity):
    """Representation of a Nanoleaf touch sensor."""

    def __init__(self, nanoleaf: Nanoleaf, panel: Panel, sensor_type: str) -> None:
        """Initialize an Nanoleaf binary sensor."""
        super().__init__(nanoleaf, panel)
        self._attr_unique_id = f"{nanoleaf.serial_no}_{panel.id}_{sensor_type}"
        self._attr_name = f"{nanoleaf.name} {panel.shape.name} {panel.id} {sensor_type}"

    async def _async_handle_touch(self, touch_type: str) -> None:
        """Handle panel touch event."""

    def _should_reset(self) -> bool:
        """Return if entity state should reset."""
        return self._attr_native_value != 0

    def _reset_value(self) -> None:
        """Reset entity state."""
        self._attr_native_value = 0



class NanoleafPanelBinarySensorEntity(NanoleafTouchEntity, BinarySensorEntity):
    """Representation of a Nanoleaf panel binary sensor entity."""

    _attr_native_value = False
    _should_not_reset_state = "off"

    def _reset_entity(self) -> None:
        """Reset entity state."""
        self._attr_is_on = False

    def __init__(self, nanoleaf: Nanoleaf, panel: Panel) -> None:
        """Initialize an Nanoleaf panel touch binary sensor."""
        super().__init__(nanoleaf, panel, "Touch")

    def _set_state(self, touch_type: str) -> None:
        """Set the entity state."""
        self._attr_is_on = touch_type == "Hold" or touch_type == "Down"


class NanoleafSensorEntity(NanoleafPanelEntity, SensorEntity):
    """Representation of a Nanoleaf panel sensor entity."""

    def __init__(
        self, nanoleaf: Nanoleaf, panel: Panel, description: SensorEntityDescription
    ) -> None:
        """Initialize an Nanoleaf binary sensor."""
        super().__init__(nanoleaf, panel)
        self._description = description
        self._attr_unique_id = f"{nanoleaf.serial_no}_{panel.id}_{description.key}"
        self._attr_name = (
            f"{nanoleaf.name} {panel.shape.name} {panel.id} {description.name}"
        )
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_entity_category = EntityCategory.DIAGNOSTIC


class PanelSensorEntity(NanoleafSensorEntity):
    """Representation of a Nanoleaf shape sensor entity."""

    @property
    def native_value(self) -> int:
        """Return the native value of the sensor."""
        value: int = getattr(self._panel, self._description.key)
        return value


class ShapeSensorEntity(NanoleafSensorEntity):
    """Representation of a Nanoleaf panel shape sensor entity."""

    @property
    def native_value(self) -> str | int | None:
        """Return the native value of the sensor."""
        value: str | int | None = getattr(self._panel.shape, self._description.key)
        return value

