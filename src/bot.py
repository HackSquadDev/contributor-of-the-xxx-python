# Imports.
# import json
import asyncio
import aiohttp
import urllib.request
from typing import Any

from PIL import Image
from dotenv import dotenv_values


# Bot class.
class Bot:
    CONFIG = dotenv_values('.env')

    def __init__(self) -> None:
        pass

    async def get_data(self) -> Any:
        '''
        GET github data by making a simple request to GitHub's REST API.
        '''

        contributors = {}
        headers = {
            "Authorization": f"token {self.CONFIG['GITHUB_TOKEN']}"
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            org = self.CONFIG['GITHUB_ORG_NAME']
            api = "https://api.github.com/orgs/{}/repos".format(org)

            async with session.get(api) as response:
                data = await response.json()
                repos = [repo["name"] for repo in data]

            for repo in repos:
                api = "https://api.github.com/repos/{}/{}/pulls".format(org, repo) + \
                    "?state=closed&per_page=100&page=1"
                async with session.get(api) as response:
                    data = await response.json()
                    for pull in data:
                        if pull["merged_at"] is not None:
                            handle = pull["user"]["login"]

                            if handle not in contributors:
                                contributors[handle] = {"score": 0}

                            contributors[handle]["details"] = pull["user"]
                            contributors[handle]["score"] = \
                                contributors[handle]["score"] + 1 if handle in contributors else 1

        contributors = sorted(contributors.items(), key=lambda x: x[1]["score"], reverse=True)
        return contributors[0][1]["details"]

    def get_data_before_run(func) -> Any:
        '''
        A simple decorator to return data retrieved from GitHub's REST API.
        '''

        async def wrapper(self):
            data = await self.get_data()
            return func(self, data)

        return wrapper

    @get_data_before_run
    def show_top_avatar(self, contributor) -> None:
        '''
        Shows the avatar of the top contributor using Pillow.
        '''

        # Retrieving the user's avatar and saving it.
        avatar = contributor['avatar_url']
        urllib.request.urlretrieve(avatar, 'avatar.png')
        img = Image.open('avatar.png')
        img.show()

    def run(self) -> None:
        '''
        Run the required functions in order for the bot.
        '''

        async def every(seconds: float):
            while True:
                await self.show_top_avatar()
                await asyncio.sleep(seconds)

        loop = asyncio.get_event_loop()
        loop.create_task(
            every(
                seconds=3600 * 24 * int(self.CONFIG['TIME_PERIOD_DAYS'])
            )
        )
        loop.run_forever()
