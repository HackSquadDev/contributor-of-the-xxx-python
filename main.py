# Imports.
from src import global_
from src.bot import Bot

# Initializing environment secrets.
global_.initialize()

# Running the bot.
if __name__ == "__main__":
    bot = Bot()
    bot.run()
