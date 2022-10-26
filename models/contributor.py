# Imports.
from io import BytesIO
from typing import Dict

import aiohttp
from discord_webhook import DiscordWebhook
from PIL import Image
from src.utils.functions import post_tweet

from .organization import Organization


# Class for top contributors.
class Contributor:
    """
    Represents the top contributor of a GitHub Organization.
    """

    def __init__(
        self,
        data: Dict,
        organization: Organization,
        score: int = 0,
    ) -> None:
        self.login = data["login"]
        self.avatar_url = data["avatar_url"]
        self.bio = data["bio"]
        self.twitter_username = data["twitter_username"]
        self.score = score
        self.organization = organization

    def __str__(self) -> str:
        return f"Top contributor of {self.org}: {self.login} | {self.html_url}"

    async def generate_avatar(self) -> Image:
        """
        Generates the avatar image of the contributor in a seeable format.

        Parameters:
            file_name: str,  The file name of the contributor. Defaults to the user's ID.

        Returns:
            An Image object.
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(self.avatar_url) as response:
                self.image_bytes = BytesIO(await response.read())

        image = Image.open(self.image_bytes)
        return image

    async def post_to_discord(self, DISCORD_HOOK) -> None:
        """
        Posts contributor result image to Discord.
        """
        webhook = DiscordWebhook(url=DISCORD_HOOK)
        webhook.add_file(file=self.image_bytes.getbuffer(), filename="contributor.png")
        webhook.execute()

    async def post_to_twitter(self) -> None:
        """
        Posts contributor result image to Twitter.
        """
        post_tweet(self.login + ": " + str(self.score), self.image_bytes.getbuffer())
