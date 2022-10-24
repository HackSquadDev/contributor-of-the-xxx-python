# Imports.
import io
import requests
from typing import Dict

from PIL import Image

from .organization import Organization


# Class for top contributors.
class Contributor:
    '''
    Represents the top contributor of a GitHub Organization.
    '''

    def __init__(self, details: Dict[str, str], organization: Organization) -> None:
        self.login = details['login']
        self.id = details['id']
        self.node_id = details['node_id']
        self.avatar_url = details['avatar_url']
        self.url = details['url']
        self.html_url = details['html_url']
        self.followers_url = details['followers_url']
        self.following_url = details['following_url']
        self.gists_url = details['gists_url']
        self.starred_url = details['starred_url']
        self.subscriptions_url = details['subscriptions_url']
        self.organizations_url = details['organizations_url']
        self.repos_url = details['repos_url']
        self.events_url = details['events_url']
        self.received_events_url = details['received_events_url']
        self.type = details['type']
        self.site_admin = details['site_admin']
        self.organization = organization

    def __str__(self) -> str:
        return f'Top contributor of {self.org}: {self.login} | {self.html_url}'

    def generate_avatar(
        self,
        file_name: str | None = None,
    ) -> Image:
        '''
        Generates the avatar image of the contributor in a seeable format.

        Parameters:
            file_name: str,  The file name of the contributor. Defaults to the user's ID.

        Returns:
            An Image object.
        '''

        response = requests.get(self.avatar_url)
        image_bytes = io.BytesIO(response.content)

        image = Image.open(image_bytes)
        return image
