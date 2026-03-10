"""Button platform for Brita Filter integration."""
from __future__ import annotations

from datetime import date

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_NAME, CONF_LAST_REPLACED


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Brita Filter button."""
    async_add_entities([BritaResetButton(entry)])


class BritaResetButton(ButtonEntity):
    """Button to reset the filter replacement date."""

    _attr_has_entity_name = True
    _attr_translation_key = "reset_filter"
    _attr_icon = "mdi:restore"

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_reset_filter"
        self.entity_id = "button.brita_filter_reset"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, "Brita Filter"),
            manufacturer="Brita",
            model="Filter Monitor",
        )

    async def async_press(self) -> None:
        """Handle button press — mark filter as replaced today."""
        new_data = {**self._entry.data, CONF_LAST_REPLACED: date.today().isoformat()}
        self.hass.config_entries.async_update_entry(self._entry, data=new_data)
        await self.hass.config_entries.async_reload(self._entry.entry_id)
