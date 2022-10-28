# Imports.
from src.bot import Bot

# Initialize with testing enabled (Twitter / Discord posting disabled).
# Set `.env` TEST_MODE=true

# Running the bot.
if __name__ == "__main__":
    bot = Bot()
    bot.run()
