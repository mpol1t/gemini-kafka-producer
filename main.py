import asyncio
import logging
import os

import colorlog

from gemini_kafka_producer.producer import run

# Configure logger
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    reset=True,
    secondary_log_colors={},
    style='%'
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

SYMBOL_CHECK_INTERVAL = int(os.getenv('SYMBOL_CHECK_INTERVAL', 60))  # Set default to 60 if not set
STATUS_CHECK_INTERVAL = int(os.getenv('STATUS_CHECK_INTERVAL', 60))  # Set default to 60 if not set

if __name__ == "__main__":
    asyncio.run(run(SYMBOL_CHECK_INTERVAL, STATUS_CHECK_INTERVAL))
