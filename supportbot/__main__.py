import logging
from supportbot import bot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    bot.run_bot()
