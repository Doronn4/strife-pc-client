import config
from src.core.keys_manager import KeysManager
from src.handlers.file_handler import FileHandler


def init_all():
    KeysManager.initialize(config.keys_path)
    FileHandler.initialize(config.files_base_path)
