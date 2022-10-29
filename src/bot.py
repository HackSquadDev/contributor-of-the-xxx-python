# Imports.
import asyncio
import logging
from datetime import datetime
from typing import Any

import aiocron
import aiohttp
from models import Contributor, Organization

from src import secrets


class Bot:
    def __init__(self) -> None:
        pass

    async def get_contributor(self) -> Contributor | None:
        """
        GET top contributor data by making a simple request to GitHub's REST API.
        """

        contributors = {}
        headers = {"Authorization": f"token {secrets.github_token}"}

        async with aiohttp.ClientSession(headers=headers) as session:
            org_name = secrets.github_org_name
            org_api = f"https://api.github.com/orgs/{org_name}/repos"

            try:
                async with session.get(org_api) as response:
                    data = await response.json()
                    repos = [repo["name"] for repo in data]

                    organization = Organization(
                        login=data[0]["owner"]["login"],
                        avatar_url=data[0]["owner"]["avatar_url"],
                    )
            except:
                logging.error(f"Failed to get organization data. Status code: {response.status}")
                return

            for repo in repos:

                for page in range(1, 100):
                    api = (
                        f"https://api.github.com/repos/{org_name}/{repo}/issues"
                        + f"?state=all&per_page=100&page={page}"
                    )

                    try:

                        async with session.get(api) as response:
                            data = await response.json()

                        if not data:
                            break

                        for item in data:
                            handle = item["user"]["login"]
                            if item.get("pull_request"):
                                pull = item["pull_request"]
                                if pull["merged_at"] is not None:
                                    difference = datetime.utcnow() - datetime.fromisoformat(
                                        pull["merged_at"][0:10]
                                    )
                                    if difference.days > int(secrets.time_period_days):
                                        break

                                    if handle not in contributors:
                                        user_api = f"https://api.github.com/users/{handle}"
                                        async with session.get(user_api) as response:
                                            data = await response.json()
                                        contributors[handle] = Contributor(
                                            data, organization=organization
                                        )

                                    contributors[handle].pr_count += 1
                            else:
                                difference = datetime.utcnow() - datetime.fromisoformat(
                                    pull["merged_at"][0:10]
                                )

                                if difference.days > int(secrets.time_period_days):
                                    break

                                if handle not in contributors:
                                    user_api = f"https://api.github.com/users/{handle}"
                                    async with session.get(user_api) as response:
                                        data = await response.json()
                                    contributors[handle] = Contributor(
                                        data, organization=organization
                                    )

                                contributors[handle].issue_count += 1
                    except:
                        logging.error(f"Failed to get pull requests or issues count. Status code: {response.status}")
                        return

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
            data = await self.get_contributor()
            return await func(self, data)

        return wrapper

    @get_contributor_before_run
    async def run_once(self, contributor: Contributor) -> None:
        """
        Shows the avatar of the top contributor.
        """
        if contributor:
            image = await contributor.generate_image()

            if not secrets.test_mode:
                try:
                    await contributor.post_to_discord()
                    await contributor.post_to_twitter()
                except Exception as e:
                    logging.error("Failed to post to Discord or Twitter. Error:\n\n" + e)
                    return
            else:
                image.show()

        else:
            logging.warning("No contributor for the given time period.")

    @staticmethod
    @aiocron.crontab(f"0 0 */{secrets.time_period_days} * *")
    async def every() -> None:
        bot = Bot()
        await bot.run_once()

    def run(self, *, run_at_start: bool = False) -> None:
        if run_at_start:
            asyncio.get_event_loop().run_until_complete(self.run_once())
            

        asyncio.get_event_loop().run_forever()
