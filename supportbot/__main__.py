import logging
from supportbot import run_bot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    run_bot()
