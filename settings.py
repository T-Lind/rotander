import json
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import os
import math
@dataclass(frozen=False)
class DisplaySettings:
    pixels_per_unit: float
    background_color: Tuple[int, int, int]
    origin_color: Tuple[int, int, int]
    user_color: Tuple[int, int, int]
    default_shape_color: List[int]
    window_size: Tuple[int, int]
    windowed_size: Tuple[int, int] = (800, 600)
    
@dataclass(frozen=False)
class MovementSettings:
    # Constants for min/max values
    MIN_ROTATE_SPEED = math.pi/96  # Slowest rotation
    MAX_ROTATE_SPEED = math.pi/24  # Fastest rotation
    DEFAULT_ROTATE_SPEED = math.pi/48  # Default rotation (medium)
    
    MIN_GRAVITY = 0.005
    MAX_GRAVITY = 0.02
    DEFAULT_GRAVITY = 0.01
    
    MIN_JUMP_VELOCITY = 0.2
    MAX_JUMP_VELOCITY = 0.4
    DEFAULT_JUMP_VELOCITY = 0.3
    
    acceleration: float = 0.02
    max_velocity: float = 5.0
    friction: float = 0.95
    rotate_speed: float = DEFAULT_ROTATE_SPEED
    user_width_pixels: int = 20*2
    user_height_pixels: int = 30*2
    bounce_factor: float = 0.5
    gravity: float = DEFAULT_GRAVITY
    jump_velocity: float = DEFAULT_JUMP_VELOCITY
    jump_cooldown: float = 0.5

    def get_collision_dimensions(self, pixels_per_unit: float) -> Tuple[float, float]:
        """Convert pixel dimensions to world units for collision detection"""
        return (
            self.user_width_pixels / pixels_per_unit,
            self.user_height_pixels / pixels_per_unit
        )
    
@dataclass(frozen=True)
class GameplaySettings:
    fall_threshold: float = -10.0
    spawn_position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    target_color: Tuple[int, int, int] = (0, 255, 0)
    target_pulse_rate: float = 0.2
    target_pulse_magnitude: float = 0.6
    points_decrease_rate: float = 1.0  # Default rate if not specified in level
    debug_mode: bool = True

    def __init__(self, settings_dict: dict = None):
        object.__setattr__(self, 'points_decrease_rate', 
                          float(settings_dict.get('points_decrease_rate', 1.0)) if settings_dict else 1.0)

class Settings:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config_data = self._load_config()
        self.display = self._init_display_settings()
        self.gameplay = GameplaySettings()
        self.movement = MovementSettings()
        self.shapes = self.config_data.get('shapes', [])
        self.enemies = self.config_data.get('enemies', [])

    def _load_config(self) -> dict:
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config from {self.config_path}: {e}")
            return self._get_default_config()

    def _init_display_settings(self) -> DisplaySettings:
        settings = self.config_data.get('settings', {})
        return DisplaySettings(
            pixels_per_unit=float(settings.get('pixels_per_unit', 100.0)),
            background_color=tuple(settings.get('background_color', [30, 30, 30])),
            origin_color=tuple(settings.get('origin_color', [255, 0, 0])),
            user_color=tuple(settings.get('user_color', [255, 255, 255])),
            default_shape_color=settings.get('default_shape_color', [100, 200, 255]),
            window_size=(800, 600)
        )

    def _get_default_config(self) -> dict:
        return {
            'settings': {
                'pixels_per_unit': 100.0,
                'background_color': [30, 30, 30],
                'origin_color': [255, 0, 0],
                'default_shape_color': [100, 200, 255]
            },
            'shapes': []
        }

    def get_shape_color(self, shape: dict) -> Tuple[int, int, int]:
        color_dict = shape.get('color', {})
        default = self.display.default_shape_color
        return (
            int(color_dict.get('r', default[0] / 255.0) * 255),
            int(color_dict.get('g', default[1] / 255.0) * 255),
            int(color_dict.get('b', default[2] / 255.0) * 255)
        )