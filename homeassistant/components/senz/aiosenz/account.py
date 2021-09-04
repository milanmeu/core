"""Senz account."""
from .typing import AccountModel


class Account:
    """Senz account."""

    def __init__(self, data: AccountModel):
        """Initialize the API and store the auth so we can make requests."""
        self.data = data

    @property
    def username(self) -> str:
        """Return username of the user that is authenticated."""
        return self.data["userName"]

    @property
    def temperature_scale(self) -> str:
        """Return the accounts preferred Temperature Scale."""
        return self.data["temperatureScale"]

    @property
    def language(self) -> str:
        """Return the users chosen localization language."""
        return self.data["language"]
