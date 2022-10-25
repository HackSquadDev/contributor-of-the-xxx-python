# Imports.
import asyncio
import aiohttp
from typing import Any

from dotenv import dotenv_values

from models import Contributor, Organization


class Bot:
    CONFIG = dotenv_values(".env")

    def __init__(self) -> None:
        pass

    async def get_data(self) -> Any:
        """
        GET github data by making a simple request to GitHub's REST API.
        """

        contributors = {}
        headers = {"Authorization": f"token {self.CONFIG['GITHUB_TOKEN']}"}

        async with aiohttp.ClientSession(headers=headers) as session:
            org_name = self.CONFIG["GITHUB_ORG_NAME"]
            api = f"https://api.github.com/orgs/{org_name}/repos"

            async with session.get(api) as response:
                data = await response.json()
                repos = [repo["name"] for repo in data]

                organization = Organization(
                    login=data[0]["owner"]["login"],
                    avatar_url=data[0]["owner"]["avatar_url"],
                )

            for repo in repos:
                api = (
                    f"https://api.github.com/repos/{org_name}/{repo}/pulls"
                    + "?state=closed&per_page=100&page=1"
                )

                async with session.get(api) as response:
                    data = await response.json()

                    for pull in data:
                        if pull["merged_at"] is not None:
                            handle = pull["user"]["login"]

                            if handle not in contributors:
                                api = f'https://api.github.com/users/{handle}'
                                async with session.get(api) as response:
                                    data = await response.json()
                                contributors[handle] = Contributor(data, organization=organization)

                            contributors[handle].score = \
                                contributors[handle].score + 1 if handle in contributors else 1

        contributors = sorted(contributors.items(), key=lambda x: x[1].score, reverse=True)
        return contributors[0][1]

    def get_contributor_before_run(func) -> Any:
        """
        A simple decorator to return top contributor data retrieved from GitHub's REST API.
        """

        async def wrapper(self):
            data = await self.get_data()
            return await func(self, data)

        return wrapper

    @get_contributor_before_run
    async def show_avatar(self, contributor: Contributor) -> None:
        """
        Shows the avatar of the top contributor.
        """

        image = await contributor.generate_avatar()
        await contributor.post_to_Discord(self.CONFIG['DISCORD_HOOK'])
        await contributor.post_to_twitter()
        image.show()

    def run(self) -> None:
        """
        Run the required functions in order for the bot.
        """

        async def every(seconds: float):
            while True:
                await self.show_avatar()
                await asyncio.sleep(seconds)

        loop = asyncio.get_event_loop()
        loop.create_task(
            every(seconds=3600 * 24 * int(self.CONFIG["TIME_PERIOD_DAYS"]))
        )
        loop.run_forever()
