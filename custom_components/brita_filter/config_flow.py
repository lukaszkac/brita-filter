"""Config flow for Brita Filter integration."""
from __future__ import annotations

from datetime import date
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    DateSelector,
    DateSelectorConfig,
    TextSelector,
    TextSelectorConfig,
)

from .const import (
    DOMAIN,
    CONF_FILTER_LIFETIME,
    CONF_LAST_REPLACED,
    CONF_NAME,
    DEFAULT_LIFETIME_DAYS,
    DEFAULT_NAME,
)


def _user_schema(defaults: dict | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): TextSelector(
                TextSelectorConfig()
            ),
            vol.Required(
                CONF_FILTER_LIFETIME,
                default=defaults.get(CONF_FILTER_LIFETIME, DEFAULT_LIFETIME_DAYS),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=7,
                    max=60,
                    step=1,
                    unit_of_measurement="days",
                    mode=NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_LAST_REPLACED,
                default=defaults.get(CONF_LAST_REPLACED, date.today().isoformat()),
            ): DateSelector(DateSelectorConfig()),
        }
    )


def _options_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_FILTER_LIFETIME,
                default=defaults.get(CONF_FILTER_LIFETIME, DEFAULT_LIFETIME_DAYS),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=7,
                    max=60,
                    step=1,
                    unit_of_measurement="days",
                    mode=NumberSelectorMode.BOX,
                )
            ),
            vol.Required(
                CONF_LAST_REPLACED,
                default=defaults.get(CONF_LAST_REPLACED, date.today().isoformat()),
            ): DateSelector(DateSelectorConfig()),
        }
    )


class BritaFilterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Brita Filter."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_FILTER_LIFETIME: int(user_input[CONF_FILTER_LIFETIME]),
                    CONF_LAST_REPLACED: user_input[CONF_LAST_REPLACED],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_user_schema(),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return options flow."""
        return BritaFilterOptionsFlow(config_entry)


class BritaFilterOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Brita Filter."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options."""
        if user_input is not None:
            new_data = {
                **self.config_entry.data,
                CONF_FILTER_LIFETIME: int(user_input[CONF_FILTER_LIFETIME]),
                CONF_LAST_REPLACED: user_input[CONF_LAST_REPLACED],
            }
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(self.config_entry.data),
        )
