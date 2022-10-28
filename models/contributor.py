# Imports.
from io import BytesIO
from typing import Dict

import aiohttp
import numpy as np
from twitter import *
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
        pr_count: int = 0,
        issue_count: int = 0,
    ) -> None:
        self.login = data["login"]
        self.avatar_url = data["avatar_url"]
        self.bio = data["bio"]
        self.twitter_username = data["twitter_username"]
        self.pr_count = pr_count
        self.issue_count = issue_count
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
        )

        if self.bio:
            draw.text(
                xy=((image.width / 2), 500),
                text=self.bio,
                fill=(255, 255, 255),
                font=ImageFont.truetype("assets/fonts/JosefinSansEL.ttf", 30),
                anchor="mm",
            )

        draw.text(
            xy=((image.width / 2), 600),
            text="Talk is cheap, show me the code.",
            fill=(255, 255, 255),
            font=ImageFont.truetype("assets/fonts/JosefinSansTI.ttf", 25),
            anchor="mm",
        )

        draw.text(
            xy=(200, 280),
            text=str(self.pr_count),
            fill=(183, 183, 183),
            font=ImageFont.truetype("assets/fonts/JosefinSansSB.ttf", 120),
            anchor="ma",
        )

        draw.text(
            xy=(1000, 280),
            text=str(self.issue_count),
            fill=(183, 183, 183),
            font=ImageFont.truetype("assets/fonts/JosefinSansSB.ttf", 120),
            anchor="ma",
        )

        draw.text(
            xy=(150, 50),
            text=f"@{self.organization.login.lower()}",
            fill=(255, 255, 255),
            font=ImageFont.truetype("assets/fonts/JosefinSansT.ttf", 30),
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
            status=f"{self.login} has scored {self.pr_count}!",
            file=self.image_bytes,
            filename="contributor.png",
        )
        
        t = Twitter(auth=OAuth(global_.TWITTER["ACCESS_TOKEN"], global_.TWITTER["ACCESS_TOKEN_SECRET"], global_.TWITTER["CONSUMER_KEY"], global_.TWITTER["CONSUMER_SECRET"]))
        with open("contributor.png", "rb") as imagefile:
            imagedata = imagefile.read()
        
        t_upload = Twitter(domain='upload.twitter.com', auth=OAuth(global_.TWITTER["ACCESS_TOKEN"], global_.TWITTER["ACCESS_TOKEN_SECRET"], global_.TWITTER["CONSUMER_KEY"], global_.TWITTER["CONSUMER_SECRET"]))
        id_img1 = t_upload.media.upload(media=imagedata)["media_id_string"]
        
        t.statuses.update(status="Hello World!", media_ids=",".join([id_img1]))

