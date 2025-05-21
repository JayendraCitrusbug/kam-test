import logging
import os


def setup_logging():
    """Set up logging for the application.

    The logging level is set to INFO, with a format of
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s".

    Two handlers are used: a StreamHandler for output to the console, and a
    FileHandler to write to a file in the "logs" directory (which is created
    if it doesn't exist).

    The log file is named "app.log" and is written to the "logs" directory.
    """

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
    )
