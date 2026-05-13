"""Config flow for SAJ eSolar integration — powered by pysaj-elekeeper."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import section
import homeassistant.helpers.config_validation as cv

from .api import ApiAuthError, ApiError, EsolarApiClient
from .const import (
    CONF_PASSWORD,
    CONF_PLANT_UID,
    CONF_USERNAME,
    DOMAIN,
)

DEFAULT_BASE_URL = "https://eop.saj-electric.com"

_LOGGER = logging.getLogger(__name__)


class EsolarGreenheissFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SAJ eSolar."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        existing_entries = self._async_current_entries()
        if existing_entries:
            return self.async_abort(reason="already_configured")

        errors = {}

        if user_input is not None:
            config = self._flatten_section(user_input)
            try:
                api = EsolarApiClient(
                    self.hass,
                    username=config[CONF_USERNAME],
                    password=config[CONF_PASSWORD],
                    plant_uid=config.get(CONF_PLANT_UID) or None,
                    base_url=config.get("base_url", DEFAULT_BASE_URL),
                )
                await api.verify_login()
            except ApiAuthError as err:
                _LOGGER.error("Authentication error: %s", err)
                errors["base"] = "invalid_auth"
            except ApiError as err:
                _LOGGER.error("API error: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if not errors:
                unique_id = config[CONF_USERNAME]
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=unique_id, data=config)

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required("advanced"): section(
                    vol.Schema(
                        {
                            vol.Optional(CONF_PLANT_UID, default=""): str,
                            vol.Optional("base_url", default=DEFAULT_BASE_URL): str,
                        }
                    ),
                    {"collapsed": True},
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, user_input=None):
        """Handle re-authentication."""
        errors = {}
        entry_id = self.context.get("entry_id")
        entry = self.hass.config_entries.async_get_entry(entry_id)

        if user_input is not None:
            new_data = {**entry.data, **user_input}
            try:
                api = EsolarApiClient(
                    self.hass,
                    username=new_data[CONF_USERNAME],
                    password=new_data[CONF_PASSWORD],
                    plant_uid=new_data.get(CONF_PLANT_UID) or None,
                    base_url=new_data.get("base_url", DEFAULT_BASE_URL),
                )
                await api.verify_login()
            except ApiAuthError:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            if not errors:
                self.hass.config_entries.async_update_entry(entry, data=new_data)
                await self.hass.config_entries.async_reload(entry_id)
                return self.async_abort(reason="reauth_successful")

        schema = vol.Schema(
            {
                vol.Required(CONF_PASSWORD, default=entry.data.get(CONF_PASSWORD)): str,
            }
        )
        return self.async_show_form(
            step_id="reauth",
            data_schema=schema,
            description_placeholders={"username": entry.data[CONF_USERNAME]},
            errors=errors,
        )

    async def async_step_import(self, import_config: dict):
        """Import a config entry from legacy YAML."""
        unique_id = import_config[CONF_USERNAME]
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=unique_id,
            data={
                CONF_USERNAME: import_config[CONF_USERNAME],
                CONF_PASSWORD: import_config[CONF_PASSWORD],
                CONF_PLANT_UID: import_config.get(CONF_PLANT_UID, ""),
                "base_url": DEFAULT_BASE_URL,
            },
        )

    def _flatten_section(self, user_input: dict) -> dict:
        flattened = {}
        for key, value in user_input.items():
            if isinstance(value, dict):
                flattened.update(value)
            else:
                flattened[key] = value
        return flattened
