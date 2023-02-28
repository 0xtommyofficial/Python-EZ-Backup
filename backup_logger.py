"""
Python EZ Backup

This is a simple, zero-bloat Python application for backing up data.

It uses the following technologies and libraries:
- Python 3.7
- PyQt 5
- qtmodern

The app is intended for educational or demonstration purposes only and should not be used in a production environment
without further testing and security measures.

To run the app, you will need to have Python and the required libraries installed.
You can run the app by running the command:
    'python, python3, or py (depending on your setup) main.py' in the terminal.

This project is released under the MIT License.

This script handles the logging for the main application.

Author: 0xtommyOfficial, Molmez LTD (www.molmez.io)
Date Published: 28 February 2023
"""
import logging
from logging.handlers import RotatingFileHandler


class InfoFilter(logging.Filter):
    # filter for information output log to only include INFO level output
    def filter(self, rec):
        return rec.levelno == logging.INFO


logger = logging.getLogger(__name__)
logger.propagate = False  # only forward specific messages to this logger, not all

error_file_handler = RotatingFileHandler('error_log.txt', maxBytes=2000, backupCount=5)
error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:S')
error_file_handler.setFormatter(error_formatter)
error_file_handler.setLevel(logging.ERROR)
logger.addHandler(error_file_handler)

info_file_handler = RotatingFileHandler('backup_log.txt', maxBytes=2000, backupCount=5)
info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:S')
info_file_handler.setFormatter(info_formatter)
info_file_handler.setLevel(logging.INFO)
info_file_handler.addFilter(InfoFilter())
logger.addHandler(info_file_handler)

logger.setLevel(logging.INFO)
