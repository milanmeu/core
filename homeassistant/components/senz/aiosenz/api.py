"""SENZ API."""
from __future__ import annotations

from .account import Account
from .auth import AbstractSENZAuth
from .thermostat import Thermostat


class SENZAPI:
    """Class for the SENZ API."""

    def __init__(self, auth: AbstractSENZAuth):
        """Initialize the API and store the auth so we can make requests."""
        self.auth = auth

    async def get_account(self) -> Account:
        """Return the account."""
        resp = await self.auth._request("get", "Account")
        return Account(resp.json())

    async def get_thermostats(self) -> list[Thermostat]:
        """Return the thermostats."""
        resp = await self.auth._request("get", "Thermostat")
        return [
            Thermostat(thermostat_data, self.auth) for thermostat_data in (resp.json())
        ]

    async def get_thermostat(self, serial_number: str) -> Thermostat:
        """Return the thermostat."""
        resp = await self.auth._request("get", f"Thermostat/{serial_number}")
        resp.raise_for_status()
        return Thermostat((resp.json()), self.auth)
