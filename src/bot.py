# Imports.
import asyncio
import logging
from datetime import datetime
from typing import Any

import aiocron
import aiohttp

from models import Contributor, Organization

from .global_ import bot_settings


class Bot:
    def __init__(self) -> None:
        pass

    async def get_data(self) -> Contributor | None:
        """
        GET github data by making a simple request to GitHub's REST API.
        """

        contributors = {}
        headers = {"Authorization": f"token {bot_settings.github_token}"}

        async with aiohttp.ClientSession(headers=headers) as session:
            org_name = bot_settings.github_org_name
            api = f"https://api.github.com/orgs/{org_name}/repos"

            async with session.get(api) as response:
                data = await response.json()
                repos = [repo["name"] for repo in data]

                organization = Organization(
                    login=data[0]["owner"]["login"],
                    avatar_url=data[0]["owner"]["avatar_url"],
                )

            for repo in repos:

                for page in range(1, 100):
                    api = (
                        f"https://api.github.com/repos/{org_name}/{repo}/pulls"
                        + f"?state=closed&per_page=100&page={page}"
                    )

                    async with session.get(api) as response:
                        data = await response.json()

                        if not data:
                            break

                        for pull in data:
                            if pull["merged_at"] is not None:
                                handle = pull["user"]["login"]
                                difference = datetime.utcnow() - datetime.fromisoformat(
                                    pull["merged_at"][0:10]
                                )

                                if difference.days > int(bot_settings.time_period_days):
                                    break

                                if handle not in contributors:
                                    api = f"https://api.github.com/users/{handle}"
                                    async with session.get(api) as response:
                                        data = await response.json()
                                    contributors[handle] = Contributor(
                                        data, organization=organization
                                    )

                                contributors[handle].pr_count += 1

                for page in range(1, 100):
                    api = (
                        f"https://api.github.com/repos/{org_name}/{repo}/issues"
                        + f"?state=all&per_page=100&page={page}"
                    )

                    async with session.get(api) as response:
                        data = await response.json()

                        if not data:
                            break

                        for issue in data:
                            if not issue.get("pull_request"):
                                handle = issue["user"]["login"]
                                difference = datetime.utcnow() - datetime.fromisoformat(
                                    issue["created_at"][0:10]
                                )

                                if difference.days > int(bot_settings.time_period_days):
                                    break

                                if handle in contributors:
                                    contributors[handle].issue_count += 1

        contributors = sorted(
            contributors.items(), key=lambda x: x[1].pr_count, reverse=True
        )

        if contributors:
            return contributors[0][1]
        else:
            return None

    def get_contributor_before_run(func) -> Any:
        """
        A simple decorator to return top contributor data retrieved from GitHub's REST API.
        """

        async def wrapper(self):
            data = await self.get_data()
            return await func(self, data)

        return wrapper

    @get_contributor_before_run
    async def run_once(self, contributor: Contributor) -> None:
        """
        Shows the avatar of the top contributor.
        """
        if contributor:
            image = await contributor.generate_image()

            if not bot_settings.test_mode:
                await contributor.post_to_discord()
                await contributor.post_to_twitter()
            else:
                image.show()

        else:
            logging.warning("No contributor for the given time period.")

    @staticmethod
    @aiocron.crontab(f"0 0 */{bot_settings.time_period_days} * *")
    async def every() -> None:
        bot = Bot()
        await bot.run_once()

    def run(self, *, run_at_start: bool = False) -> None:
        if run_at_start:
            asyncio.run(self.run_once())

        asyncio.get_event_loop().run_forever()
