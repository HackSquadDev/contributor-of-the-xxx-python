# Imports.
import asyncio
import logging
from datetime import datetime
from typing import Any

import aiocron
import aiohttp
from PIL import Image

from src import secrets
from src.models import Contributor, Organization

logging.basicConfig(level=logging.INFO)
headers = {"Authorization": f"token {secrets.github_token}"}
start_time = datetime.utcnow()
org_name = secrets.github_org_name


class Bot:
    def __init__(self) -> None:
        pass

    async def get_contributor(self) -> Contributor | None:
        """
        GET top contributor data by making a simple request to GitHub's REST API.
        """

        contributors = {}
        bots = []

        async with aiohttp.ClientSession(headers=headers) as session:
            for page in range(1, 100):
                api = "https://api.github.com/search/issues" + f"?q=org:{org_name}&sort=created&per_page=100&page={page}"

                async with session.get(api) as response:
                    data = await response.json()

                if not data.get("items"):
                    break

                for item in data["items"]:
                    handle = item["user"]["login"]
                    if item.get("pull_request"):
                        pull = item["pull_request"]
                        if pull["merged_at"] is not None:
                            difference = start_time - datetime.fromisoformat(pull["merged_at"][0:10])

                            if difference.days > int(secrets.time_period_days):
                                break

                            if handle not in list(contributors.keys()) + bots + secrets.excluded_profiles:
                                contributors[handle] = {"pr_count": 0, "issue_count": 0}
                                if item["user"]["type"] == "Bot":
                                    bots += item["user"]["login"]
                            if handle in contributors:
                                contributors[handle]["pr_count"] += 1

                    else:
                        difference = start_time - datetime.fromisoformat(item["created_at"][0:10])

                        if difference.days > int(secrets.time_period_days):
                            break

                        if handle not in list(contributors.keys()) + bots + secrets.excluded_profiles:
                            contributors[handle] = {"pr_count": 0, "issue_count": 0}
                            if item["user"]["type"] == "Bot":
                                bots += item["user"]["login"]
                        if handle in contributors:
                            contributors[handle]["issue_count"] += 1

        contributors = sorted(contributors.items(), key=lambda x: x[1]["pr_count"], reverse=True)

        if contributors:
            return contributors[0]
        else:
            return None

    def get_contributor_before_run(func) -> Any:
        """
        A simple decorator to return top contributor data retrieved from GitHub's REST API.
        """

        async def wrapper(self):
            data = await self.get_contributor()
            return await func(self, data)

        return wrapper

    @get_contributor_before_run
    async def run_once(self, contributor: Any) -> None:
        """
        Shows the avatar of the top contributor.
        """
        if contributor:
            async with aiohttp.ClientSession(headers=headers) as session:
                org_api = f"https://api.github.com/orgs/{org_name}"
                async with session.get(org_api) as response:
                    data = await response.json()
                    organization = Organization(
                        login=data["login"],
                        avatar_url=data["avatar_url"],
                    )

                user_api = f"https://api.github.com/users/{contributor[0]}"
                async with session.get(user_api) as response:
                    data = await response.json()
            contributor = Contributor(
                data=data, organization=organization, pr_count=contributor[1]["pr_count"], issue_count=contributor[1]["issue_count"]
            )
            image = await contributor.generate_image()
            if not secrets.test_mode:
                try:
                    await contributor.post_to_discord()
                    await contributor.post_to_twitter()
                except Exception as e:
                    logging.error(f"{datetime.now()} -> Cannot post to Discord or Twitter\nError: {e}")
            else:
                file_name = "test_image.png"
                image.save(file_name)

                preview = Image.open(file_name)
                preview.show()

            logging.info(f"{datetime.now()} -> Top Contributor: {contributor.login}")

        else:
            logging.info(f"{datetime.now()} -> No contributor for the given time period.")

    @staticmethod
    @aiocron.crontab(f"0 0 */{secrets.time_period_days} * *")
    async def every() -> None:
        bot = Bot()
        await bot.run_once()

    def run(self, *, run_at_start: bool = False) -> None:
        if run_at_start:
            asyncio.get_event_loop().run_until_complete(self.run_once())

        asyncio.get_event_loop().run_forever()
