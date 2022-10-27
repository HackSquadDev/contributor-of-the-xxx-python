# Imports.
import datetime
from io import BytesIO
from typing import Any, Dict

import aiohttp
import numpy as np
import tweepy
from discord_webhook import DiscordWebhook
from PIL import Image, ImageDraw, ImageFont
from src import global_

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
        self.image_bytes: bytes = None

    def __str__(self) -> str:
        return f"Top contributor of {self.org}: {self.login} | {self.html_url}"

    async def generate_image(self) -> Image:
        """
        Generates the banner image for the top contributor.
        """

        image = Image.open("assets/background.png")

        async with aiohttp.ClientSession() as session:
            async with session.get(self.avatar_url) as response:
                avatar_bytes = BytesIO(await response.read())
                avatar = Image.open(avatar_bytes).resize((200, 200))
                image.paste(avatar, (500, 216))

            async with session.get(self.organization.avatar_url) as response2:
                org_avatar_bytes = BytesIO(await response2.read())
                org_avatar = Image.open(org_avatar_bytes).resize((80, 80))

                height, width = org_avatar.size
                lum_img = Image.new("L", [height, width], 0)

                org_draw = ImageDraw.Draw(lum_img)
                org_draw.pieslice([(0, 0), (height, width)], 0, 360, fill=255)
                org_avatar_arr = np.array(org_avatar)
                lum_img_arr = np.array(lum_img)

                final_org_avatar = Image.fromarray(
                    np.dstack((org_avatar_arr, lum_img_arr))
                )

                try:
                    image.paste(final_org_avatar, (60, 28), mask=final_org_avatar)
                except ValueError:
                    image.paste(final_org_avatar, (60, 28))

        draw = ImageDraw.Draw(image)

        draw.text(
            xy=((image.width / 2), 160),
            text=self.login,
            fill=(255, 255, 255),
            font=ImageFont.truetype("assets/fonts/JosefinSansSB.ttf", 40),
            anchor="mm",
            align="center",
        )

        if self.bio:
            draw.text(
                xy=((image.width / 2), 500),
                text=self.bio,
                fill=(255, 255, 255),
                font=ImageFont.truetype("assets/fonts/JosefinSansEL.ttf", 30),
                anchor="mm",
                align="center",
            )

        draw.text(
            xy=((image.width / 2), 600),
            text="Talk is cheap, show me the code.",
            fill=(255, 255, 255),
            font=ImageFont.truetype("assets/fonts/JosefinSansTI.ttf", 25),
            anchor="mm",
            align="center",
        )

        draw.text(
            xy=(255, 280),
            text=str(self.score),
            fill=(183, 183, 183),
            font=ImageFont.truetype("assets/fonts/JosefinSansSB.ttf", 120),
            direction="rtl",
        )

        draw.text(
            xy=(900, 280),
            text=str(self.score),
            fill=(183, 183, 183),
            font=ImageFont.truetype("assets/fonts/JosefinSansSB.ttf", 120),
            direction="ltr",
        )

        draw.text(
            xy=(150, 50),
            text=f"@{self.organization.login.lower()}",
            fill=(255, 255, 255),
            font=ImageFont.truetype("assets/fonts/JosefinSansT.ttf", 30),
            direction="ltr",
        )

        overlay = Image.open("assets/overlay.png")
        image.paste(overlay, mask=overlay)

        buffer = BytesIO()
        image.save(buffer, format="png")
        self.image_bytes = buffer.getvalue()

        return image

    async def post_to_discord(self) -> None:
        """
        Posts contributor result image to Discord.
        """
        webhook = DiscordWebhook(url=global_.DISCORD_HOOK)
        webhook.add_file(file=self.image_bytes, filename="contributor.png")
        webhook.execute()

    async def post_to_twitter(self) -> None:
        """
        Posts contributor result image to Twitter.
        """
        auth = tweepy.OAuthHandler(
            global_.TWITTER["CONSUMER_KEY"], global_.TWITTER["CONSUMER_SECRET"]
        )
        auth.set_access_token(
            global_.TWITTER["ACCESS_TOKEN"], global_.TWITTER["ACCESS_TOKEN_SECRET"]
        )
        api = tweepy.API(auth)
        api.update_status_with_media(
            status=f"{self.login} has scored {self.score}!",
            file=self.image_bytes,
            filename="contributor.png",
        )

    async def get_issue_count(self) -> Any:
        """
        GET issue count by making a simple request to GitHub's REST API.
        """

        issue_count = 0
        headers = {"Authorization": f"token {global_.GITHUB['TOKEN']}"}

        async with aiohttp.ClientSession(headers=headers) as session:
            org_name = global_.GITHUB["ORG_NAME"]
            api = f"https://api.github.com/orgs/{org_name}/repos"

            async with session.get(api) as response:
                data = await response.json()
                repos = [repo["name"] for repo in data]

            for repo in repos:
                for page in range(1, 100):
                    api = (
                        f"https://api.github.com/repos/{org_name}/{repo}/issues"
                        + f"?state=closed&per_page=100&page={page}"
                    )

                    async with session.get(api) as response:
                        data = await response.json()

                        if not data:
                            break

                        for issue in data:
                            if issue["merged_at"] is None:
                                break

                            difference = datetime.utcnow() - datetime.fromisoformat(
                                issue["merged_at"][0:10]
                            )

                            if difference.days > int(global_.TIME_PERIOD_DAYS):
                                break

                            else:
                                issue_count += 1

        return issue_count
