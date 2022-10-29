# Imports.
from src.bot import Bot

# Initialize with testing enabled (Twitter / Discord posting disabled).
# Set `.env` TEST_MODE=true

# Running the bot.

# Set the run_at_start argument to False if you'd not like to optionally
# execute tasks every time you start the bot.
if __name__ == "__main__":
    bot = Bot()
    bot.run(run_at_start=True)
