import os
from enum import Enum, auto

class GameState(Enum):
    MAIN_MENU = auto()
    GAME = auto()
    PAUSE = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()
    HIGH_SCORES = auto()
    
class LevelManager:
    def __init__(self, start_level=None):
        self.current_level = start_level
        self.level_folder = os.path.join(os.getenv('GAME_ROOT'), 'levels')

    def get_current_level_path(self) -> str:
        return os.path.join(self.level_folder, f"{self.current_level}.json")

    def advance_level(self):
        self.current_level += 1

    def has_next_level(self) -> bool:
        next_level = self.current_level + 1
        next_level_path = os.path.join(self.level_folder, f"{next_level}.json")
        return os.path.exists(next_level_path)