"""Sensor platform for Brita Filter integration."""
from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_FILTER_LIFETIME, CONF_LAST_REPLACED, CONF_NAME


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Brita Filter sensors."""
    async_add_entities([
        BritaDaysSinceSensor(entry),
        BritaRemainingPctSensor(entry),
        BritaDisplayLevelSensor(entry),
        BritaStatusSensor(entry),
    ])


class BritaBaseSensor(SensorEntity):
    """Base class for Brita sensors.

    entity_id is set explicitly in each subclass __init__ so it is always
    stable English regardless of HA language.
    _attr_translation_key provides the translated friendly name shown in UI.
    """

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_NAME, "Brita Filter"),
            manufacturer="Brita",
            model="Filter Monitor",
        )

    @property
    def _lifetime(self) -> int:
        return int(self._entry.data.get(CONF_FILTER_LIFETIME, 28))

    @property
    def _last_replaced(self) -> date:
        raw = self._entry.data.get(CONF_LAST_REPLACED, date.today().isoformat())
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return date.today()

    @property
    def _days_since(self) -> int:
        return max((date.today() - self._last_replaced).days, 0)

    @property
    def _pct_remaining(self) -> int:
        pct = 100 - round(self._days_since / self._lifetime * 100)
        return max(min(pct, 100), 0)


class BritaDaysSinceSensor(BritaBaseSensor):
    _attr_translation_key = "days_since"
    _attr_icon = "mdi:calendar-clock"
    _attr_native_unit_of_measurement = "d"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_days_since"
        self.entity_id = f"sensor.brita_filter_days_since"

    @property
    def native_value(self) -> int:
        return self._days_since


class BritaRemainingPctSensor(BritaBaseSensor):
    _attr_translation_key = "remaining"
    _attr_icon = "mdi:water-percent"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_remaining"
        self.entity_id = f"sensor.brita_filter_remaining"

    @property
    def native_value(self) -> int:
        return self._pct_remaining

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "days_remaining": max(self._lifetime - self._days_since, 0),
            "last_replaced": self._last_replaced.isoformat(),
            "filter_lifetime_days": self._lifetime,
        }


class BritaDisplayLevelSensor(BritaBaseSensor):
    _attr_translation_key = "display_level"
    _attr_icon = "mdi:water-alert"
    _attr_entity_registry_enabled_default = False

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_display_level"
        self.entity_id = f"sensor.brita_filter_display_level"

    @property
    def native_value(self) -> str:
        pct = self._pct_remaining
        if pct > 75:   return "100%"
        elif pct > 50: return "75%"
        elif pct > 25: return "50%"
        elif pct > 0:  return "25%"
        return "REPLACE"


class BritaStatusSensor(BritaBaseSensor):
    _attr_translation_key = "status"

    def __init__(self, entry: ConfigEntry) -> None:
        super().__init__(entry)
        self._attr_unique_id = f"{entry.entry_id}_status"
        self.entity_id = f"sensor.brita_filter_status"

    @property
    def icon(self) -> str:
        pct = self._pct_remaining
        if pct > 50:   return "mdi:check-circle"
        elif pct > 25: return "mdi:alert-circle"
        return "mdi:close-circle"

    @property
    def native_value(self) -> str:
        pct = self._pct_remaining
        if pct > 50:   return "good"
        elif pct > 15: return "replace_soon"
        return "replace_now"
