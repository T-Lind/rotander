from settings import MovementSettings
import os
import json
import pygame

class OptionsManager:
    def __init__(self):
        self.filename = os.path.join(os.getenv('GAME_ROOT'), 'data', 'options.json')
        self.default_options = {
            'master_volume': 1.0,
            'music_volume': 1.0,
            'sfx_volume': 1.0,
        }
        self.options = self._load_options()

    def _load_options(self):
        if not os.path.exists(self.filename):
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            return self.default_options.copy()
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return self.default_options.copy()
        
    def save_options(self):
        with open(self.filename, 'w') as f:
            json.dump(self.options, f)
        
    def update_setting(self, setting_name: str, value: float):
        """Update a setting within its min/max bounds"""
        self.options[setting_name] = value
        self.apply_volume_settings()

    def apply_volume_settings(self, asset_manager):
        pygame.mixer.music.set_volume(self.options['master_volume'] * self.options['music_volume'])
        for sound in asset_manager.sounds.values():
            if sound:
                sound.set_volume(self.options['master_volume'] * self.options['sfx_volume'])