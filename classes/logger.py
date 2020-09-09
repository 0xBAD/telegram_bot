import logging
import os


class Logger(logging.Logger):

    def __init__(self, name: str = 'my_app', level: str = None):
        level = level if level else os.environ.get("LOG_LEVEL", "INFO")
        super().__init__(name)
        consle_handler = logging.StreamHandler()
        consle_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        consle_handler.setFormatter(formatter)
        self.addHandler(consle_handler)


log = Logger()
