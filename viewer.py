import numpy as np
import pygame
from pygame.locals import *
from settings import Settings, ViewerSettings
from geometry import GeometryHelper
from renderer import Renderer
from level_manager import LevelManager, GameState
from menu_manager import MenuManager
from asset_manager import AssetManager
from high_score_manager import HighScoreManager
from options_manager import OptionsManager
import sys

class GameViewer:
    def __init__(self, settings: Settings, level_manager: LevelManager, assets: AssetManager, username: str, high_score_manager: HighScoreManager, total_score: int, options_manager: OptionsManager):
        self.settings = settings
        self.level_manager = level_manager
        self.renderer = Renderer(settings, assets)
        self.geometry = GeometryHelper()

        # Initialize enemies
        self.enemies = []
        for enemy_data in settings.enemies:
            enemy = {
                'position': np.array(enemy_data['position'], dtype=float),
                'size': enemy_data.get('size', 1.0),
                'speed': enemy_data.get('speed', 0.1),
                'shape': self._create_enemy_shape(enemy_data)
            }
            self.enemies.append(enemy)

        self.username = username
        self.high_score_manager = high_score_manager
        self.assets = assets
        self.assets.play_game_music()
        self.return_to_main_menu = False
        self.state = GameState.GAME
        self.menu = MenuManager(level_manager, assets, high_score_manager, options_manager, in_game=True)
        
        # State
        self.running = True
        self.user_pos = np.array([0.0, 0.0, 0.0], dtype=float)
        self.plane_angle = 0.0
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=float)
        
        # Movement tracking
        self.keys_pressed = {
            K_w: False,
            K_s: False,
            K_a: False,
            K_d: False,
            K_SPACE: False,
        }
        self.ground_contact = False
        self.last_jump_time = 0
        self.is_jumping = False
        self.jump_direction = 'up'  # Can be 'up', 'left', or 'right'
        
        # Clock for consistent framerate
        self.clock = pygame.time.Clock()
        
        # Compute initial intersections
        self._compute_all_intersections()

        self.level_complete = False
        self.spawn_position = np.array(settings.gameplay.spawn_position, dtype=float)
        self.user_pos = self.spawn_position.copy()
        self.target_pulse_time = 0

        self.total_score = total_score
        self.points = 10000
        self.points_decrease_rate = 1
        self.jump_penalty = 100
        self.death_penalty = 1500

        self.alarm_playing = False
        self.alarm_distance = 2.0  # Distance threshold for alarm


    def _create_enemy_shape(self, enemy_data: dict) -> dict:
        """Create a cube shape for the enemy."""
        size = enemy_data.get('size', 1.0)
        half_size = size / 2.0
        px, py, pz = enemy_data['position']
        points = [
            [px - half_size, py - half_size, pz - half_size],
            [px + half_size, py - half_size, pz - half_size],
            [px + half_size, py + half_size, pz - half_size],
            [px - half_size, py + half_size, pz - half_size],
            [px - half_size, py - half_size, pz + half_size],
            [px + half_size, py - half_size, pz + half_size],
            [px + half_size, py + half_size, pz + half_size],
            [px - half_size, py + half_size, pz + half_size],
        ]
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7],
        ]
        return {
            'name': 'Enemy',
            'points': points,
            'edges': edges,
            'color': {'r': 1.0, 'g': 0.0, 'b': 0.0},  # Red color
            'is_enemy': True  # Mark as enemy
        }
                
    def _check_fall_condition(self):
        """Check if player has fallen below threshold"""
        if self.user_pos[2] < self.settings.gameplay.fall_threshold:
            self._reset_player()
            self.assets.play_sound('death')
            self.points -= self.death_penalty

    def _handle_elim(self):
        """Handle player's elimination"""
        self.assets.stop_music()
        self.assets.play_sound('elimination')
        
        # Check if this is a high score -- note this has to be 0 points, so just refer to total_score in elim case
        current_high_score = self.high_score_manager.high_scores.get(self.username, 0)
        is_high_score = self.total_score > current_high_score
        
        self.renderer.render_elimination_message(self.total_score, is_high_score)
        self.high_score_manager.add_score(self.username, self.total_score)
        
        # Wait for space key
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        waiting = False
            self.clock.tick(30)
        
        self.running = False
        self.level_complete = False
        self.return_to_main_menu = True
            
    def _reset_player(self):
        """Reset player to spawn position"""
        self.user_pos = self.spawn_position.copy()
        self.velocity = np.zeros(3, dtype=float)
        self._compute_all_intersections()
        
    def _update_target_pulse(self):
        """Update target pulsing animation"""
        self.target_pulse_time += 1/30  # Assuming 60 FPS
        pulse_factor = (np.sin(self.target_pulse_time * 2 * np.pi * 
                        self.settings.gameplay.target_pulse_rate) + 1) / 2
        self.current_pulse_factor = pulse_factor
        return pulse_factor
    
    def _adjust_user_position_after_rotation(self):
        """Move the user up if colliding after rotation."""
        max_adjustment = 10.0  # Maximum height to adjust
        adjustment_step = 0.1  # Step size for adjustment
        total_adjustment = 0.0

        while total_adjustment < max_adjustment:
            collision = False
            user_shape = self.geometry.get_user_convex_hull(self.user_pos, self.plane_angle, self.settings)
            for shape in self.settings.shapes:
                shape_hull = self.geometry.get_convex_hull(shape, self.user_pos, self.plane_angle)
                if self.geometry.check_collision(user_shape, shape_hull):
                    collision = True
                    break
            if collision:
                self.user_pos[2] += adjustment_step
                total_adjustment += adjustment_step
            else:
                break

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.high_score_manager.add_score(self.username, self.total_score + self.points)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._pause_game()
                elif event.key == pygame.K_F5 and self.settings.gameplay.debug_mode:
                    self.level_complete = True
                    self.running = False

                if event.key in self.keys_pressed:
                    self.keys_pressed[event.key] = True

                if event.key == pygame.K_k:  # Zoom in
                    self.settings.viewer.minimap_zoom = min(self.settings.viewer.MAX_ZOOM, self.settings.viewer.minimap_zoom + 0.5)
                elif event.key == pygame.K_l:  # Zoom out
                    self.settings.viewer.minimap_zoom = max(self.settings.viewer.MIN_ZOOM, self.settings.viewer.minimap_zoom - 0.5)

                # Control plane angle by i/o
                if event.key == pygame.K_i:
                    self.plane_angle = (self.plane_angle + self.settings.movement.rotate_speed) % (2 * np.pi)
                    self._compute_all_intersections()
                    self._adjust_user_position_after_rotation()
                elif event.key == pygame.K_o:
                    self.plane_angle = (self.plane_angle - self.settings.movement.rotate_speed) % (2 * np.pi)
                    self._compute_all_intersections()
                    self._adjust_user_position_after_rotation()

            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed[event.key] = False

            
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self.plane_angle = (self.plane_angle + self.settings.movement.rotate_speed) % (2 * np.pi)
                    self._compute_all_intersections()
                    self._adjust_user_position_after_rotation()
                elif event.button == 5:  # Scroll down
                    self.plane_angle = (self.plane_angle - self.settings.movement.rotate_speed) % (2 * np.pi)
                    self._compute_all_intersections()
                    self._adjust_user_position_after_rotation()

    def _pause_game(self):
        self.state = GameState.PAUSE
        self.menu.run_pause_menu()
        if self.menu.resume_game:
            self._resume_game()
        elif self.menu.return_to_main:
            self.return_to_main_menu = True
            self.running = False

    def _resume_game(self):
        self.state = GameState.GAME
        # Reset keys to allow pausing again
        self.keys_pressed = {key: False for key in self.keys_pressed}


    def _handle_level_completion(self):
        self.renderer.render_win_message()
        self.assets.stop_music()
        self.assets.play_sound('complete')
        self.renderer.update_display()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False
            self.clock.tick(30)
        self.level_complete = True
        self.running = False

        

    def _update_physics(self):
        movement_acceleration = np.array([0.0, 0.0, -self.settings.movement.gravity], dtype=float)
        
        current_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        can_jump = (current_time - self.last_jump_time) >= self.settings.movement.jump_cooldown
        
        # Handle jumping
        if (self.keys_pressed[K_SPACE] or self.keys_pressed[K_w]) and self.ground_contact and can_jump:
            self.velocity[2] = self.settings.movement.jump_velocity
            self.ground_contact = False
            self.assets.play_sound('jump')
            self.points -= self.jump_penalty
            self.last_jump_time = current_time

        if self.keys_pressed[K_s]:
            movement_acceleration[2] -= self.settings.movement.acceleration
        if self.keys_pressed[K_a]:
            p_x = np.array([-np.sin(self.plane_angle), np.cos(self.plane_angle), 0.0], dtype=float)
            movement_acceleration += -self.settings.movement.acceleration * p_x
        if self.keys_pressed[K_d]:
            p_x = np.array([-np.sin(self.plane_angle), np.cos(self.plane_angle), 0.0], dtype=float)
            movement_acceleration += self.settings.movement.acceleration * p_x

        # Update velocity
        self.velocity += movement_acceleration
        
        # Limit velocity
        speed = np.linalg.norm(self.velocity)
        if speed > self.settings.movement.max_velocity:
            self.velocity = (self.velocity / speed) * self.settings.movement.max_velocity
            
        # Apply friction
        self.velocity *= self.settings.movement.friction

        # Update jump direction based on velocity
        if self.is_jumping:
            # Project velocity onto plane
            p_x = np.array([-np.sin(self.plane_angle), np.cos(self.plane_angle), 0.0], dtype=float)
            horizontal_velocity = np.dot(self.velocity, p_x)
            
            if abs(horizontal_velocity) < 0.1:
                self.jump_direction = 'up'
            else:
                self.jump_direction = 'right' if horizontal_velocity > 0 else 'left'


        # Store previous position
        previous_pos = self.user_pos.copy()
        
        # Update position if moving
        if np.linalg.norm(self.velocity) > 0.01:
            self.user_pos += self.velocity
            self._compute_all_intersections()
        
        # Collision Detection
        user_shape = self.geometry.get_user_convex_hull(self.user_pos, self.plane_angle, self.settings)
        collision = False
        for shape in self.settings.shapes:
            shape_hull = self.geometry.get_convex_hull(shape, self.user_pos, self.plane_angle)
            if self.geometry.check_collision(user_shape, shape_hull):
                if shape.get('is_target', False):
                    self.level_complete = True

                # Get collision normal
                normal = self.geometry.get_collision_normal(user_shape, shape_hull, 
                                                         self.user_pos, np.zeros(3))
                if normal is not None:
                    # Reflect velocity off normal with bounce factor
                    normal_2d = np.array([normal[0], normal[1]])
                    velocity_2d = np.array([self.velocity[0], self.velocity[1]])
                    
                    # Reflection formula: v' = v - 2(v·n)n
                    reflected = velocity_2d - 2 * np.dot(velocity_2d, normal_2d) * normal_2d
                    
                    # Apply bounce factor
                    self.velocity[0] = reflected[0] * self.settings.movement.bounce_factor
                    self.velocity[1] = reflected[1] * self.settings.movement.bounce_factor
                    self.velocity[2] *= self.settings.movement.bounce_factor
                
                collision = True
                self.ground_contact = True
                break
        self.is_jumping = not self.ground_contact
        if collision:
            self.user_pos = previous_pos

    def _compute_all_intersections(self):
        self.intersection_coords_2D = []
        self.intersection_edges = []
        
        for shape in self.settings.shapes:
            points_2d, edges = self.geometry.compute_intersections(
                shape, self.user_pos, self.plane_angle)
            self.intersection_coords_2D.append(points_2d)
            self.intersection_edges.append(edges)

        # Compute intersections for enemies
        self.enemy_intersections = []
        for enemy in self.enemies:
            points_2d, edges_2d = self.geometry.compute_intersections(
                enemy['shape'],
                self.user_pos,
                self.plane_angle
            )
            self.enemy_intersections.append({
                'points_2d': points_2d,
                'edges_2d': edges_2d,
                'color': self.settings.get_shape_color(enemy['shape']),
                'enemy': enemy
            })

    def _check_enemy_collisions(self):
        """Check for collisions between the player and enemies."""
        user_hull = self.geometry.get_user_convex_hull(
            self.user_pos, self.plane_angle, self.settings)
        for enemy_data in self.enemy_intersections:
            enemy_hull = self.geometry.get_convex_hull(
                enemy_data['enemy']['shape'], self.user_pos, self.plane_angle)
            collision = self.geometry.check_collision(user_hull, enemy_hull)
            if collision:
                self._handle_death()
                break

    def _update_enemies(self):
        """Move enemies towards the player."""
        for enemy in self.enemies:
            direction = self.user_pos - enemy['position']
            distance = np.linalg.norm(direction)
            if distance > 0:
                direction /= distance  # Normalize
                enemy['position'] += direction * enemy['speed']
                # Update enemy shape points
                self._update_enemy_shape(enemy)

    def _update_enemy_shape(self, enemy):
        """Update the enemy's shape points based on its new position."""
        size = enemy['size']
        half_size = size / 2.0
        px, py, pz = enemy['position']
        points = [
            [px - half_size, py - half_size, pz - half_size],
            [px + half_size, py - half_size, pz - half_size],
            [px + half_size, py + half_size, pz - half_size],
            [px - half_size, py + half_size, pz - half_size],
            [px - half_size, py - half_size, pz + half_size],
            [px + half_size, py - half_size, pz + half_size],
            [px + half_size, py + half_size, pz + half_size],
            [px - half_size, py + half_size, pz + half_size],
        ]
        enemy['shape']['points'] = points

    def _handle_death(self):
        """Handle player's death when colliding with an enemy."""
        self._reset_player()
        self.assets.play_sound('death')
        self.points -= self.death_penalty

    def _update(self):
        dt = 1/60  # Fixed timestep
        if not self.level_complete:
            self._update_physics()
            self._check_fall_condition()
            self._update_enemies()
            self._check_enemy_collisions()
            self._update_target_pulse()
            
            # Calculate minimum distance to enemies
            self.min_distance_enemy = "N/A"
            if self.enemies:
                distances = [np.linalg.norm(self.user_pos - enemy['position']) for enemy in self.enemies]
                min_dist = min(distances)
                self.min_distance_enemy = f"{min_dist:.2f}"

                # Handle alarm sound
                if min_dist <= self.alarm_distance and not self.alarm_playing:
                    self.assets.play_sound('alarm')
                    self.alarm_playing = True
                elif min_dist > self.alarm_distance and self.alarm_playing:
                    self.assets.sounds['alarm'].stop()
                    self.alarm_playing = False
            
            self.points -= self.settings.gameplay.points_decrease_rate
            if self.points < 0:
                self.points = 0
                self._handle_elim()

    def _render(self):
        self.renderer.clear_screen()
        self.renderer.draw_shapes(self.settings.shapes,
                                self.intersection_coords_2D,
                                self.intersection_edges)
        
        self.renderer.draw_enemies(self.enemy_intersections)
        
        # Target shapes with pulsing border
        target_shapes = [s for s in self.settings.shapes if s.get('is_target')]
        target_idx = [i for i, s in enumerate(self.settings.shapes) if s.get('is_target')]
        if target_shapes:
            pulse_factor = self.current_pulse_factor if hasattr(self, 'current_pulse_factor') else 1.0
            for i in target_idx:
                coords = self.intersection_coords_2D[i]
                edges = self.intersection_edges[i]
                self.renderer.draw_pulsing_target(coords, edges, pulse_factor)
        
        self.renderer.draw_origin_marker()
        self.renderer.draw_user(self.is_jumping, self.jump_direction)

        self.renderer.draw_status_text(
            self.user_pos,
            self.plane_angle,
            self.points,
            self.min_distance_enemy
        )
        
        # Handle level completion before final display update
        if self.level_complete:
            self._handle_level_completion()
        
        self.renderer.draw_minimap(self.user_pos, self.enemies)
        self.renderer.update_display()

    def run(self):
        self.assets.play_sound('spawn')
        while self.running:
            if self.state == GameState.GAME:
                self._handle_events()
                self._update()
                self._render()
                pygame.display.flip()
                self.clock.tick(60)
            elif self.state == GameState.PAUSE:
                self._handle_events()
                self.clock.tick(60)