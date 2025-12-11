"""Config flow for Jarolift integration."""
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from . import (
    CONF_COVERS,
    CONF_DELAY,
    CONF_GROUP,
    CONF_LSB,
    CONF_MSB,
    CONF_REMOTE_ENTITY_ID,
    CONF_REP_COUNT,
    CONF_REP_DELAY,
    CONF_REVERSE,
    CONF_SERIAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class JaroliftConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jarolift."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate remote entity exists
            if not self.hass.states.get(user_input[CONF_REMOTE_ENTITY_ID]):
                errors[CONF_REMOTE_ENTITY_ID] = "invalid_remote_entity"
            else:
                # Create the config entry
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Jarolift",
                    data={
                        CONF_REMOTE_ENTITY_ID: user_input[CONF_REMOTE_ENTITY_ID],
                        CONF_MSB: user_input[CONF_MSB],
                        CONF_LSB: user_input[CONF_LSB],
                        CONF_DELAY: user_input.get(CONF_DELAY, 0),
                    },
                    options={
                        CONF_COVERS: [],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REMOTE_ENTITY_ID): cv.string,
                    vol.Required(CONF_MSB): cv.string,
                    vol.Required(CONF_LSB): cv.string,
                    vol.Optional(CONF_DELAY, default=0): vol.Coerce(int),
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        # Check if already configured
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        # Extract jarolift config - import_data contains the full config dict
        domain_config = import_data.get(DOMAIN, {})
        
        # Validate required keys
        if not domain_config:
            _LOGGER.error("No jarolift configuration found in import data")
            return self.async_abort(reason="missing_configuration")
        
        try:
            remote_entity_id = domain_config[CONF_REMOTE_ENTITY_ID]
            msb = domain_config[CONF_MSB]
            lsb = domain_config[CONF_LSB]
        except KeyError as err:
            _LOGGER.error("Missing required configuration key: %s", err)
            return self.async_abort(reason="missing_configuration")

        # Retrieve covers that were stored by setup_platform during YAML setup
        covers_list = []
        yaml_covers = self.hass.data.get(DOMAIN, {}).get("yaml_covers")
        if yaml_covers is not None:
            covers_list = yaml_covers
            _LOGGER.info("Importing %d cover(s) from YAML configuration", len(covers_list))

        return self.async_create_entry(
            title="Jarolift",
            data={
                CONF_REMOTE_ENTITY_ID: remote_entity_id,
                CONF_MSB: msb,
                CONF_LSB: lsb,
                CONF_DELAY: domain_config.get(CONF_DELAY, 0),
            },
            options={
                CONF_COVERS: covers_list,
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "JaroliftOptionsFlow":
        """Get the options flow for this handler."""
        return JaroliftOptionsFlow(config_entry)


class JaroliftOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Jarolift."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.covers = dict(config_entry.options).get(CONF_COVERS, [])
        self.edit_cover_index = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        return await self.async_step_manage_covers()

    async def async_step_manage_covers(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage covers."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add":
                return await self.async_step_add_cover()
            elif action == "edit":
                return await self.async_step_select_cover_to_edit()
            elif action == "remove":
                return await self.async_step_select_cover_to_remove()
            elif action == "finish":
                return self.async_create_entry(title="", data={CONF_COVERS: self.covers})

        # Build list of existing covers
        cover_list = "\n".join(
            [f"- {cover[CONF_NAME]} (Serial: {cover[CONF_SERIAL]}, Group: {cover[CONF_GROUP]})" for cover in self.covers]
        ) if self.covers else "No covers configured"

        return self.async_show_form(
            step_id="manage_covers",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): vol.In(
                        {
                            "add": "Add new cover",
                            "edit": "Edit existing cover",
                            "remove": "Remove cover",
                            "finish": "Finish",
                        }
                    ),
                }
            ),
            description_placeholders={"covers": cover_list},
        )

    async def async_step_add_cover(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a new cover."""
        errors = {}

        if user_input is not None:
            # Validate that serial+group combination is unique
            for cover in self.covers:
                if (
                    cover[CONF_SERIAL] == user_input[CONF_SERIAL]
                    and cover[CONF_GROUP] == user_input[CONF_GROUP]
                ):
                    errors["base"] = "duplicate_cover"
                    break

            if not errors:
                self.covers.append(user_input)
                return await self.async_step_manage_covers()

        return self.async_show_form(
            step_id="add_cover",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): cv.string,
                    vol.Required(CONF_GROUP): cv.string,
                    vol.Required(CONF_SERIAL): cv.string,
                    vol.Optional(CONF_REP_COUNT, default=0): vol.Coerce(int),
                    vol.Optional(CONF_REP_DELAY, default=0.2): vol.Coerce(float),
                    vol.Optional(CONF_REVERSE, default=False): cv.boolean,
                }
            ),
            errors=errors,
        )

    async def async_step_select_cover_to_edit(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select a cover to edit."""
        if not self.covers:
            return await self.async_step_manage_covers()

        if user_input is not None:
            self.edit_cover_index = int(user_input["cover_index"])
            return await self.async_step_edit_cover()

        # Create selection list
        cover_options = {
            str(i): f"{cover[CONF_NAME]} (Serial: {cover[CONF_SERIAL]}, Group: {cover[CONF_GROUP]})"
            for i, cover in enumerate(self.covers)
        }

        return self.async_show_form(
            step_id="select_cover_to_edit",
            data_schema=vol.Schema(
                {
                    vol.Required("cover_index"): vol.In(cover_options),
                }
            ),
        )

    async def async_step_edit_cover(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit a cover."""
        errors = {}

        if user_input is not None:
            # Validate that serial+group combination is unique (except for the current cover)
            for i, cover in enumerate(self.covers):
                if i != self.edit_cover_index and (
                    cover[CONF_SERIAL] == user_input[CONF_SERIAL]
                    and cover[CONF_GROUP] == user_input[CONF_GROUP]
                ):
                    errors["base"] = "duplicate_cover"
                    break

            if not errors:
                self.covers[self.edit_cover_index] = user_input
                self.edit_cover_index = None
                return await self.async_step_manage_covers()

        # Pre-fill with existing values
        cover = self.covers[self.edit_cover_index]
        return self.async_show_form(
            step_id="edit_cover",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=cover[CONF_NAME]): cv.string,
                    vol.Required(CONF_GROUP, default=cover[CONF_GROUP]): cv.string,
                    vol.Required(CONF_SERIAL, default=cover[CONF_SERIAL]): cv.string,
                    vol.Optional(CONF_REP_COUNT, default=cover.get(CONF_REP_COUNT, 0)): vol.Coerce(int),
                    vol.Optional(CONF_REP_DELAY, default=cover.get(CONF_REP_DELAY, 0.2)): vol.Coerce(float),
                    vol.Optional(CONF_REVERSE, default=cover.get(CONF_REVERSE, False)): cv.boolean,
                }
            ),
            errors=errors,
        )

    async def async_step_select_cover_to_remove(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select a cover to remove."""
        if not self.covers:
            return await self.async_step_manage_covers()

        if user_input is not None:
            cover_index = int(user_input["cover_index"])
            self.covers.pop(cover_index)
            return await self.async_step_manage_covers()

        # Create selection list
        cover_options = {
            str(i): f"{cover[CONF_NAME]} (Serial: {cover[CONF_SERIAL]}, Group: {cover[CONF_GROUP]})"
            for i, cover in enumerate(self.covers)
        }

        return self.async_show_form(
            step_id="select_cover_to_remove",
            data_schema=vol.Schema(
                {
                    vol.Required("cover_index"): vol.In(cover_options),
                }
            ),
        )
