import pygame
import numpy as np
from typing import List, Tuple, Optional
from scipy.spatial import ConvexHull
from settings import Settings
from asset_manager import AssetManager
from geometry import GeometryHelper

class Renderer:
    def __init__(self, settings: Settings, assets: AssetManager):
        pygame.init()
        self.settings = settings
        self.screen = pygame.display.set_mode(settings.display.window_size)
        pygame.display.set_caption("Rotander")
        self.assets = assets
        self.font = {
            8: self.assets.get_font('pixel_8'),
            24: self.assets.get_font('pixel_24'),
            48: self.assets.get_font('pixel_48'),
            64: self.assets.get_font('pixel_64'),
        }
        self.center_2D = (settings.display.window_size[0] // 2, 
                         settings.display.window_size[1] // 2)

    def clear_screen(self):
        self.screen.fill(self.settings.display.background_color)
    

    def draw_pulsing_target(self, coords_2d: List[Tuple[float, float]], 
                            edges: List[Tuple[int, int]], pulse_factor: float):
        try:
            hull = ConvexHull(coords_2d)
            hull_indices = hull.vertices
            polygon = [coords_2d[j] for j in hull_indices]
            
            # Convert to screen coordinates
            polygon_screen = [self._to_screen_coords(pt) for pt in polygon]
            
            # Define golden color pulsing
            golden_color = (
                int(255 * pulse_factor), 
                int(215 * pulse_factor), 
                0
            )
            
            pygame.draw.polygon(self.screen, golden_color, polygon_screen, 3)
        except:
            pass

    def draw_shapes(self, shapes: List[dict], 
                   intersection_coords_2D: List[List[Tuple[float, float]]], 
                   intersection_edges: List[List[Tuple[int, int]]]):
        for i, shape in enumerate(shapes):
            color = self.settings.get_shape_color(shape)
            coords_2d = intersection_coords_2D[i]
            edges_2d = intersection_edges[i]

            if len(coords_2d) >= 3:
                self._draw_polygon(coords_2d, color)
            elif len(coords_2d) == 2:
                self._draw_line_segment(coords_2d[0], coords_2d[1], color)

    def _draw_polygon(self, coords_2d: List[Tuple[float, float]], color: Tuple[int, int, int]):
        try:
            hull = ConvexHull(coords_2d)
            hull_indices = hull.vertices
            polygon = [coords_2d[j] for j in hull_indices]
            
            # Convert to screen coordinates
            polygon_screen = [self._to_screen_coords(pt) for pt in polygon]
            
            pygame.draw.polygon(self.screen, color, polygon_screen)
            pygame.draw.polygon(self.screen, (0, 0, 0), polygon_screen, 1)
        except:
            pass

    def draw_enemies(self, enemies_intersections: List[dict]):
        """Draw enemy shapes."""
        for enemy_data in enemies_intersections:
            coords_2d = enemy_data['points_2d']
            if len(coords_2d) >= 3:
                try:
                    hull = ConvexHull(coords_2d)
                    hull_indices = hull.vertices
                    polygon = [coords_2d[j] for j in hull_indices]
                    
                    # Convert to screen coordinates
                    polygon_screen = [self._to_screen_coords(pt) for pt in polygon]
                    
                    # Draw solid red polygon without outline
                    pygame.draw.polygon(self.screen, (255, 0, 0), polygon_screen, 0)
                except:
                    pass

    def _draw_shape(self, coords_2d: List[Tuple[float, float]], edges: List[Tuple[int, int]], color: Tuple[int, int, int]):
        """Helper method to draw shapes and enemies."""
        # Convert to screen coordinates
        screen_coords = [self._to_screen_coords(pt) for pt in coords_2d]
        # Draw edges
        for edge in edges:
            start_idx, end_idx = edge
            if start_idx < len(screen_coords) and end_idx < len(screen_coords):
                pygame.draw.line(
                    self.screen, color,
                    screen_coords[start_idx],
                    screen_coords[end_idx],
                    2
                )
        # Optionally, fill the shape if it's closed
        if len(screen_coords) >= 3:
            try:
                pygame.draw.polygon(self.screen, color, screen_coords, 0)
            except:
                pass

    def _draw_line_segment(self, pt1: Tuple[float, float], pt2: Tuple[float, float], 
                          color: Tuple[int, int, int]):
        screen_pt1 = self._to_screen_coords(pt1)
        screen_pt2 = self._to_screen_coords(pt2)
        pygame.draw.line(self.screen, color, screen_pt1, screen_pt2, 2)

    def draw_debug_hulls(self, user_hull, shape_hulls):
        """Debug visualization of collision hulls"""
        # Draw user hull
        if user_hull:
            points = [self._to_screen_coords(p) for p in user_hull]
            pygame.draw.polygon(self.screen, (0, 255, 0), points, 1)
        
        # Draw shape hulls
        for hull in shape_hulls:
            if hull:
                points = [self._to_screen_coords(p) for p in hull]
                pygame.draw.polygon(self.screen, (255, 0, 0), points, 1)

    def draw_origin_marker(self):
        pygame.draw.circle(self.screen, self.settings.display.origin_color, 
                         self.center_2D, 5)
        
    def draw_user(self, is_jumping: bool, jump_direction: str = 'up'):
        if is_jumping:
            sprite_name = f'player_jump_{jump_direction}'
        else:
            sprite_name = 'player_stand'
            
        sprite = self.assets.get_sprite(sprite_name)
        if sprite:
            scaled_width = self.settings.movement.user_width_pixels
            scaled_height = self.settings.movement.user_height_pixels
            scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
            
            sprite_x = self.center_2D[0] - scaled_width // 2
            sprite_y = self.center_2D[1] - scaled_height // 2
            self.screen.blit(scaled_sprite, (sprite_x, sprite_y))
        else:
            # Fallback to rectangle if sprite not found
            rect_x = self.center_2D[0] - self.settings.movement.user_width_pixels // 2
            rect_y = self.center_2D[1] - self.settings.movement.user_height_pixels // 2
            pygame.draw.rect(self.screen, self.settings.display.user_color,
                           (rect_x, rect_y, 
                            self.settings.movement.user_width_pixels,
                            self.settings.movement.user_height_pixels))

    def draw_status_text(self, user_pos: np.ndarray, plane_angle: float, points: int, min_distance_enemy = "N/A"):
        coord_text = f"User Position: (X: {user_pos[0]:.2f}, Y: {user_pos[1]:.2f}, Z: {user_pos[2]:.2f})"
        angle_degrees = np.degrees(plane_angle) % 360
        angle_text = f"Plane Angle: {angle_degrees:.1f}°"
        points_text = f"Points: {int(points)}"
        min_distance_text = f"Distance to Nearest Enemy: {min_distance_enemy}"

        text_surface1 = self.font[8].render(coord_text, True, (255, 255, 255))
        text_surface2 = self.font[8].render(angle_text, True, (255, 255, 255))
        text_surface3 = self.font[8].render(points_text, True, (255, 255, 255))
        text_surface4 = self.font[8].render(min_distance_text, True, (255, 255, 255))
        
        self.screen.blit(text_surface1, (10, 10))
        self.screen.blit(text_surface2, (10, 20))
        self.screen.blit(text_surface3, (10, 30))
        self.screen.blit(text_surface4, (10, 40))

    def render_win_message(self):
        """Draw centered win message overlay and wait for input"""
        self._render_win_message()
        self.update_display()
        pygame.event.clear()

    def _render_win_message(self):
        """Draw centered win message overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.settings.display.window_size)
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0,0))
        
        # Win message
        text = self.font[48].render("Level Complete!", True, (255, 215, 0))
        text_rect = text.get_rect(center=(self.settings.display.window_size[0]/2,
                                        self.settings.display.window_size[1]/2 - 50))
        self.screen.blit(text, text_rect)
        
        # Instruction to continue
        continue_text = self.font[24].render("Press Space to Continue", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(self.settings.display.window_size[0]/2,
                                                    self.settings.display.window_size[1]/2 + 20))
        self.screen.blit(continue_text, continue_rect)

    def render_elimination_message(self, points: int, is_high_score: bool):
        """Draw centered elimination message overlay and score info"""
        # Semi-transparent overlay
        overlay = pygame.Surface(self.settings.display.window_size)
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0,0))
        
        # Elimination message
        text = self.font[48].render("ELIMINATED", True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.settings.display.window_size[0]/2,
                                        self.settings.display.window_size[1]/2 - 80))
        self.screen.blit(text, text_rect)
        
        # Final score
        score_text = self.font[24].render(f"Final Score: {int(points)}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.settings.display.window_size[0]/2,
                                               self.settings.display.window_size[1]/2 - 20))
        self.screen.blit(score_text, score_rect)

        # High score message if applicable
        if is_high_score:
            hs_text = self.font[24].render("NEW HIGH SCORE!", True, (255, 215, 0))
            hs_rect = hs_text.get_rect(center=(self.settings.display.window_size[0]/2,
                                             self.settings.display.window_size[1]/2 + 20))
            self.screen.blit(hs_text, hs_rect)
        
        # Continue instruction
        continue_text = self.font[24].render("Press Space to Continue", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(self.settings.display.window_size[0]/2,
                                                    self.settings.display.window_size[1]/2 + 60))
        self.screen.blit(continue_text, continue_rect)
        
        self.update_display()

    def render_ultimate_victory_message(self, total_score: int, is_high_score: bool):
        """Draw centered ultimate victory message overlay"""
        # Black overlay
        overlay = pygame.Surface(self.settings.display.window_size)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0,0))
        
        # Victory message
        text = self.font[48].render("ULTIMATE VICTORY", True, (255, 215, 0))
        text_rect = text.get_rect(center=(self.settings.display.window_size[0]/2,
                                        self.settings.display.window_size[1]/2 - 100))
        self.screen.blit(text, text_rect)
        
        # Final score
        score_text = self.font[24].render(f"Final Score: {int(total_score)}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.settings.display.window_size[0]/2,
                                               self.settings.display.window_size[1]/2 - 20))
        self.screen.blit(score_text, score_rect)

        # High score message if applicable
        if is_high_score:
            hs_text = self.font[24].render("NEW HIGH SCORE!", True, (255, 215, 0))
            hs_rect = hs_text.get_rect(center=(self.settings.display.window_size[0]/2,
                                             self.settings.display.window_size[1]/2 + 20))
            self.screen.blit(hs_text, hs_rect)
        
        # Continue instruction
        continue_text = self.font[24].render("Press Space to Continue", True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(self.settings.display.window_size[0]/2,
                                                    self.settings.display.window_size[1]/2 + 60))
        self.screen.blit(continue_text, continue_rect)
        
        self.update_display()

    def draw_minimap(self, user_pos, enemies):
        import numpy as np
        minimap_width, minimap_height = 150, 150  # You can adjust these base dimensions
        margin = 10
        x_pos = self.settings.display.window_size[0] - minimap_width - margin
        y_pos = margin

        # Draw background with border
        pygame.draw.rect(self.screen, (50, 50, 50), (x_pos, y_pos, minimap_width, minimap_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (x_pos, y_pos, minimap_width, minimap_height), 1)
        
        center_x = x_pos + minimap_width // 2
        center_y = y_pos + minimap_height // 2
        
        # Use the viewer's zoom level
        map_scale = 20.0 / self.settings.viewer.minimap_zoom  # Inverse relationship - higher zoom = smaller scale
        
        # Draw user at center
        pygame.draw.circle(self.screen, (0, 255, 0), (center_x, center_y), 5)

        # Draw enemies with zoom factor
        for enemy in enemies:
            enemy_pos = np.array(enemy['position'])
            user_array = np.array(user_pos)
            relative = enemy_pos - user_array
            
            # Scale positions by zoom level
            ex = int(center_x + relative[0] * map_scale)
            ey = int(center_y - relative[1] * map_scale)
            
            # Only draw if within minimap bounds
            if (x_pos <= ex <= x_pos + minimap_width and 
                y_pos <= ey <= y_pos + minimap_height):
                pygame.draw.circle(self.screen, (255, 0, 0), (ex, ey), 3)

        # Draw zoom level indicator
        zoom_text = self.font[8].render(f"Zoom: {self.settings.viewer.minimap_zoom:.1f}x", True, (255, 255, 255))
        self.screen.blit(zoom_text, (x_pos + 5, y_pos + minimap_height + 5))

    def draw_level_info(self, level_name: str, level_number: int):
        """Draw level information in top-right corner"""
        text = f"Level {level_number}: {level_name}"
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(topright=(self.settings.display.window_size[0] - 10, 10))
        self.screen.blit(text_surface, text_rect)

    def _to_screen_coords(self, point: Tuple[float, float]) -> Tuple[int, int]:
        return (
            int(self.center_2D[0] + point[0] * self.settings.display.pixels_per_unit),
            int(self.center_2D[1] - point[1] * self.settings.display.pixels_per_unit)
        )

    def update_display(self):
        pygame.display.flip()

    def quit(self):
        pygame.quit()