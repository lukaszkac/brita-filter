"""Brita Filter integration for Home Assistant."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path
from datetime import date

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, CONF_LAST_REPLACED

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "button"]


def _install_blueprint(hass: HomeAssistant) -> None:
    """Copy blueprint to HA blueprints folder if not already present."""
    try:
        src = Path(__file__).parent / "blueprints" / "brita_filter_notifications.yaml"
        if not src.exists():
            _LOGGER.warning("Brita Filter: blueprint source not found at %s", src)
            return

        dest = (
            Path(hass.config.config_dir)
            / "blueprints"
            / "automation"
            / "brita_filter_notifications.yaml"
        )
        dest.parent.mkdir(parents=True, exist_ok=True)

        if not dest.exists():
            shutil.copy2(src, dest)
            _LOGGER.info("Brita Filter: blueprint installed to %s", dest)
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Brita Filter: could not install blueprint: %s", err)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register static path for HA frontend icon and install blueprint."""
    try:
        await hass.http.async_register_static_paths([
            StaticPathConfig(
                "/static/custom_components/brita_filter",
                str(Path(__file__).parent),
                True,
            )
        ])
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Brita Filter: could not register static path: %s", err)

    await hass.async_add_executor_job(_install_blueprint, hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Brita Filter from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_reset_filter(call: ServiceCall) -> None:
        """Handle filter replacement reset service."""
        entry_id = call.data.get("entry_id", entry.entry_id)
        target_entry = hass.config_entries.async_get_entry(entry_id) or entry
        new_data = {**target_entry.data, CONF_LAST_REPLACED: date.today().isoformat()}
        hass.config_entries.async_update_entry(target_entry, data=new_data)
        await hass.config_entries.async_reload(target_entry.entry_id)

    hass.services.async_register(
        DOMAIN,
        "reset_filter",
        handle_reset_filter,
        schema=vol.Schema({vol.Optional("entry_id"): cv.string}),
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
