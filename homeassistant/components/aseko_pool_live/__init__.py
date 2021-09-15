"""The Aseko Pool Live integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .aioaseko import APIUnavailable, MobileAccount, Unit, Variable
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Aseko Pool Live from a config entry."""
    account = MobileAccount(
        async_get_clientsession(hass), access_token=entry.data[CONF_ACCESS_TOKEN]
    )

    try:
        devices = await account.get_devices()
    except APIUnavailable as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = []

    for device in devices:
        coordinator = AsekoDataUpdateCoordinator(hass, device)
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id].append((device, coordinator))

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AsekoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Aseko unit data from single endpoint."""

    def __init__(self, hass: HomeAssistant, unit: Unit) -> None:
        """Initialize global Aseko unit data updater."""
        self._unit = unit
        super().__init__(
            hass,
            _LOGGER,
            name=f"{self._unit.type if self._unit.name is None else self._unit.name}-{self._unit.serial_number}",
            update_interval=timedelta(seconds=60),
        )

    async def _async_update_data(self) -> dict[str, Variable]:
        """Fetch unit data."""
        await self._unit.get_state()
        return {variable.type: variable for variable in self._unit.variables}
