# Imports.
from io import BytesIO

import aiohttp
from PIL import Image


# Class for organizations.
class Organization:
    """
    Represents a GitHub Organization.
    """

    def __init__(self, login: str, avatar_url: str) -> None:
        self.login = login
        self.avatar_url = avatar_url

    def __str__(self) -> str:
        return self.login

    async def generate_logo(self) -> Image:
        """
        Generates the logo image of the organization in the form of a `PIL.Image` object.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(self.avatar_url) as response:
                image_bytes = BytesIO(await response.read())

        image = Image.open(image_bytes)
        return image
