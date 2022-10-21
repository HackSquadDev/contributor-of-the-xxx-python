# Imports.
import json
import asyncio
import requests
import urllib.request
from typing import Any

from PIL import Image
from dotenv import dotenv_values


# Bot class.
class Bot:
    CONFIG = dotenv_values('.env')

    def __init__(self) -> None:
        pass

    def get_data(self) -> Any:
        '''
        GET github data by making a simple request to GitHub's REST API.
        '''

        got = requests.get(f"https://api.github.com/repos/{self.CONFIG['GITHUB_ORG_NAME']}/{self.CONFIG['GITHUB_REPO_NAME']}/contributors?q=contributions&order=desc")        
        data = json.loads(got.text)

        return data

    def get_data_before_run(func) -> Any:
        '''
        A simple decorator to return data retrieved from GitHub's REST API.
        '''

        def wrapper(self):
            data = self.get_data()
            return func(self, data)

        return wrapper

    @get_data_before_run
    def show_top_avatar(self, data) -> None:
        '''
        Shows the avatar of the top contributor using Pillow.
        '''

        # Retrieving the user's avatar and saving it.
        top_contributor_avatar = data[0]['avatar_url']
        urllib.request.urlretrieve(top_contributor_avatar, 'top_contributor_avatar.png')
        img = Image.open('top_contributor_avatar.png')
        img.show()

    def run(self) -> None:
        '''
        Run the required functions in order for the bot.
        '''

        async def every(seconds: float):
            while True:
                self.show_top_avatar()
                await asyncio.sleep(seconds)

        loop = asyncio.get_event_loop()
        loop.create_task(
            every(
                seconds=3600 * 24 * int(self.CONFIG['TIME_PERIOD_DAYS'])
            )
        )
        loop.run_forever()
