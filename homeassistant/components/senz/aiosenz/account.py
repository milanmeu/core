#    Copyright 2021, Milan Meulemans
#
#    This file is part of aiosenz.
#
#    aiosenz is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    aiosenz is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with aiosenz.  If not, see <https://www.gnu.org/licenses/>.

"""SENZ account."""
from .typing import AccountModel


class Account:
    """SENZ account."""

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
