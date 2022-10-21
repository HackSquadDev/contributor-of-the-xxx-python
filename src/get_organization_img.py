import urllib.request
from PIL import Image
from main import data["avatar_url"]

urllib.request.urlretrieve(data["avatar_url"], "top_contributor_avatar.png")
img = Image.open("organization_avatar.png")
img.show()
