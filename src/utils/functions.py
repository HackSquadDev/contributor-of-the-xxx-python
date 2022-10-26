import tweepy
from dotenv import dotenv_values

CONFIG = dotenv_values('.env')

CONSUMER_KEY = CONFIG["TWITTER_KEY"]
CONSUMER_SECRET = CONFIG["TWITTER_SECRET"]
ACCESS_TOKEN = CONFIG["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = CONFIG["TWITTER_ACCESS_SECRET"]


def post_tweet(tweet_text, image):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    api.update_status_with_media(
        status=tweet_text, file=image, filename="contributor.png"
    )
