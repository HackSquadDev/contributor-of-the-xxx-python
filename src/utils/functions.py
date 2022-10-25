import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

consumer_key = os.environ.get("TWITTER_KEY")
consumer_secret = os.environ.get("TWITTER_SECRET")
access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
access_token_secret = os.environ.get("TWITTER_ACCESS_SECRET")


def post_tweet(tweet_text, image_path):

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    api.update_status_with_media(tweet_text, image_path)
