import json
import requests
import sys
import urllib.request
from PIL import Image

org_name = input("Org name: ").strip()
repo_name = input("Repo name: ").strip()

# Gets the data from GitHub
r = requests.get('https://api.github.com/repos/{}/{}/contributors?q=contributions&order=desc'.format(org_name, repo_name))

# Serialize the data
data = json.loads(r.text)
print("Organization: {}".format(org_name))
top_contributor = data[0]["login"]
print("Top Contributor: {}".format(top_contributor))
top_contributor_profile = data[0]["html_url"]
print("{}'s Profile: {}".format(top_contributor, top_contributor_profile))
top_contributor_contributions = data[0]["contributions"]
print("No. of Contributions Done by {}: {}".format(top_contributor, top_contributor_contributions))
top_contributor_avatar = data[0]["avatar_url"]
urllib.request.urlretrieve(top_contributor_avatar, "top_contributor_avatar.png")
img = Image.open("top_contributor_avatar.png")
img.show()
