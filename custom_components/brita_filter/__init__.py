"""Brita Filter integration for Home Assistant."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path
from datetime import date

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, CONF_LAST_REPLACED

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "button"]

_BLUEPRINT_REL = Path("blueprints") / "automation" / "brita_filter_notifications.yaml"


def _blueprint_dest(hass: HomeAssistant) -> Path:
    return Path(hass.config.config_dir) / _BLUEPRINT_REL


def _install_blueprint(hass: HomeAssistant) -> None:
    """Copy blueprint to HA blueprints folder, always overwrite to keep it up to date."""
    try:
        src = Path(__file__).parent / "blueprints" / "brita_filter_notifications.yaml"
        if not src.exists():
            _LOGGER.warning("Brita Filter: blueprint source not found at %s", src)
            return
        dest = _blueprint_dest(hass)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        _LOGGER.info("Brita Filter: blueprint installed/updated at %s", dest)
    except Exception as err:
        _LOGGER.warning("Brita Filter: could not install blueprint: %s", err)


def _remove_blueprint(hass: HomeAssistant) -> None:
    """Remove blueprint only when the last Brita filter instance is removed."""
    remaining = [
        e for e in hass.config_entries.async_entries(DOMAIN)
    ]
    # async_remove_entry is called after the entry is already removed,
    # so 0 remaining means this was the last one.
    if len(remaining) == 0:
        try:
            dest = _blueprint_dest(hass)
            if dest.exists():
                dest.unlink()
                _LOGGER.info("Brita Filter: blueprint removed from %s", dest)
        except Exception as err:
            _LOGGER.warning("Brita Filter: could not remove blueprint: %s", err)


async def _register_static_path(hass: HomeAssistant) -> None:
    """Register static path — compatible with all HA versions."""
    path = str(Path(__file__).parent)
    url = "/static/custom_components/brita_filter"
    try:
        from homeassistant.components.http import StaticPathConfig
        await hass.http.async_register_static_paths(
            [StaticPathConfig(url, path, True)]
        )
    except (ImportError, AttributeError):
        try:
            hass.http.register_static_path(url, path, True)
        except Exception as err:
            _LOGGER.debug("Brita Filter: static path not registered: %s", err)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register static path, install blueprint and register service once."""
    await _register_static_path(hass)
    await hass.async_add_executor_job(_install_blueprint, hass)

    # Register service once here (not per entry) to avoid duplicate registration
    # when multiple filters are configured.
    async def handle_reset_filter(call: ServiceCall) -> None:
        """Reset filter replacement date for a specific or all entries."""
        entry_id = call.data.get("entry_id")
        entries = (
            [hass.config_entries.async_get_entry(entry_id)]
            if entry_id
            else hass.config_entries.async_entries(DOMAIN)
        )
        for entry in entries:
            if entry is None:
                continue
            new_data = {**entry.data, CONF_LAST_REPLACED: date.today().isoformat()}
            hass.config_entries.async_update_entry(entry, data=new_data)
            await hass.config_entries.async_reload(entry.entry_id)

    hass.services.async_register(
        DOMAIN,
        "reset_filter",
        handle_reset_filter,
        schema=vol.Schema({vol.Optional("entry_id"): cv.string}),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Brita Filter from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload entry when options/data are updated (e.g. from options flow)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when config is updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Called when the integration is fully removed — clean up blueprint if last instance."""
    await hass.async_add_executor_job(_remove_blueprint, hass)
