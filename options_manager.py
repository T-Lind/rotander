from settings import MovementSettings
import os
import json
import pygame

class OptionsManager:
    def __init__(self):
        self.filename = 'data/options.json'
        self.default_options = {
            'master_volume': 1.0,
            'music_volume': 1.0,
            'sfx_volume': 1.0,
            'rotate_speed': MovementSettings.DEFAULT_ROTATE_SPEED,
            'gravity': MovementSettings.DEFAULT_GRAVITY,
            'jump_velocity': MovementSettings.DEFAULT_JUMP_VELOCITY
        }
        self.options = self._load_options()
        MovementSettings.rotate_speed = self.options['rotate_speed']
        MovementSettings.gravity = self.options['gravity']
        MovementSettings.jump_velocity = self.options['jump_velocity']

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
        if setting_name == 'rotate_speed':
            self.options[setting_name] = max(MovementSettings.MIN_ROTATE_SPEED,
                                          min(MovementSettings.MAX_ROTATE_SPEED, value))
        elif setting_name == 'gravity':
            self.options[setting_name] = max(MovementSettings.MIN_GRAVITY,
                                          min(MovementSettings.MAX_GRAVITY, value))
        elif setting_name == 'jump_velocity':
            self.options[setting_name] = max(MovementSettings.MIN_JUMP_VELOCITY,
                                          min(MovementSettings.MAX_JUMP_VELOCITY, value))
        else:
            self.options[setting_name] = value
        MovementSettings.rotate_speed = self.options['rotate_speed']
        MovementSettings.gravity = self.options['gravity']
        MovementSettings.jump_velocity = self.options['jump_velocity']

    def apply_volume_settings(self, asset_manager):
        pygame.mixer.music.set_volume(self.options['master_volume'] * self.options['music_volume'])
        for sound in asset_manager.sounds.values():
            if sound:
                sound.set_volume(self.options['master_volume'] * self.options['sfx_volume'])