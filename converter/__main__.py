from .config import Config
from .controller import Controller


Controller(Config(config_path="config.yml")).run()
