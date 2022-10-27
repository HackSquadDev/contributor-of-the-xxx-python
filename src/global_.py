from dotenv import dotenv_values

config = dotenv_values(".env")


def initialize(social_secrets: bool = True) -> None:
    """
    Initializes environment secrets into native Python environment.
    """

    global TIME_PERIOD_DAYS
    TIME_PERIOD_DAYS = config["TIME_PERIOD_DAYS"]

    global GITHUB
    GITHUB = {
        "ORG_NAME": config["GITHUB_ORG_NAME"],
        "TOKEN": config["GITHUB_TOKEN"],
    }

    if social_secrets:
        global TWITTER
        TWITTER = {
            "CONSUMER_KEY": config["TWITTER_KEY"],
            "CONSUMER_SECRET": config["TWITTER_SECRET"],
            "ACCESS_TOKEN": config["TWITTER_ACCESS_TOKEN"],
            "ACCESS_TOKEN_SECRET": config["TWITTER_ACCESS_SECRET"],
        }

        global DISCORD_HOOK
        DISCORD_HOOK = config["DISCORD_HOOK"]
