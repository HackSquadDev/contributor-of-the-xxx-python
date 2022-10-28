from pydantic import BaseSettings


class BotSettings(BaseSettings):
    time_period_days: int
    github_org_name: str
    github_token: str
    twitter_key: str
    twitter_secret: str
    twitter_access_token: str
    twitter_access_secret: str
    discord_hook: str
    test_mode: bool

    class Config:
        env_file = ".env"


bot_settings = BotSettings()
