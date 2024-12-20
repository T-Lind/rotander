import os
import pygame
from typing import Optional

class AssetManager:
    def __init__(self):
        self.fonts = {}
        self.sounds = {}
        self.sprites = {}
        self.current_music = None
        self.base_path = os.path.join(os.path.dirname(__file__), 'assets')
        
        # Verify directory structure
        if not os.path.exists(self.base_path):
            raise FileNotFoundError(f"Assets directory not found at: {self.base_path}")
            
        sounds_path = os.path.join(self.base_path, 'sounds')
        if not os.path.exists(sounds_path):
            raise FileNotFoundError(f"Sounds directory not found at: {sounds_path}")
            
        self._init_fonts()
        self._init_sounds()
        self._init_sprites()
        
        
    def _init_fonts(self):
        pygame.font.init()
        self.fonts = {
            'pixel_8': pygame.font.Font(os.path.join(self.base_path, 'fonts', 'pixel.ttf'), 8),
            'pixel_16': pygame.font.Font(os.path.join(self.base_path, 'fonts', 'pixel.ttf'), 16),
            'pixel_24': pygame.font.Font(os.path.join(self.base_path, 'fonts', 'pixel.ttf'), 24),
            'pixel_48': pygame.font.Font(os.path.join(self.base_path, 'fonts', 'pixel.ttf'), 48),
            'pixel_64': pygame.font.Font(os.path.join(self.base_path, 'fonts', 'pixel.ttf'), 64),
        }
        
    def _init_sounds(self):
        pygame.mixer.init()
        sound_files = {
            'jump': 'jump.wav',
            'collision': 'collision.ogg',
            'complete': 'complete.wav',
            'select': 'select.wav',
            'highlight': 'highlight.wav',
            'music': 'music.mp3',
            'menu': 'menu.mp3',
            'death': 'death.wav',
            'alarm': 'alarm.wav',
            'elimination': 'explosion.wav',
            'victory': 'victory.ogg',
            'spawn': 'spawn.mp3',
        }
        
        for name, file in sound_files.items():
            try:
                path = os.path.join(self.base_path, 'sounds', file)
                if not os.path.exists(path):
                    print(f"Warning: Sound file not found: {path}")
                    self.sounds[name] = None  # Store None for missing sounds
                    continue
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Warning: Error loading sound {file}: {str(e)}")
                self.sounds[name] = None

    def _init_sprites(self):
        """Load character sprites."""
        sprite_files = {
            'player_stand': 'standing.png',
            'player_jump': 'jumping.png'
        }
        
        for name, file in sprite_files.items():
            try:
                path = os.path.join(self.base_path, 'art', file)
                if not os.path.exists(path):
                    print(f"Warning: Sprite file not found: {path}")
                    self.sprites[name] = None
                    continue
                sprite = pygame.image.load(path).convert_alpha()
                self.sprites[name] = sprite
            except Exception as e:
                print(f"Warning: Error loading sprite {file}: {str(e)}")
                self.sprites[name] = None
                
    def get_font(self, name: str) -> pygame.font.Font:
        return self.fonts.get(name)
        
    def play_sound(self, name: str):
        if sound := self.sounds.get(name):
            sound.play()
            
    def stop_music(self):
        if self.current_music:
            self.current_music.stop()
        self.current_music = None
            
    def play_menu_music(self):
        if menu_music := self.sounds.get('menu'):
            self.stop_music()
            menu_music.play(-1)
            self.current_music = menu_music

    def play_game_music(self):
        if game_music := self.sounds.get('music'):
            self.stop_music()
            game_music.play(-1)
            self.current_music = game_music

    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        return self.sprites.get(name)