import config
from code.core.keys_manager import KeysManager
from code.handlers.file_handler import FileHandler


def init_all():
    KeysManager.initialize(config.keys_path)
    FileHandler.initialize(config.files_base_path)
