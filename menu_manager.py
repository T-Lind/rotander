import pygame
from typing import List
from asset_manager import AssetManager
from level_manager import LevelManager
from high_score_manager import HighScoreManager
from options_manager import OptionsManager
from settings import MovementSettings
import os
import math
import sys

class MenuManager:
    def __init__(self, level_manager: LevelManager, assets: AssetManager, high_score_manager: HighScoreManager, options_manager: OptionsManager, in_game=False):
        self.level_manager = level_manager
        self.high_score_manager = high_score_manager
        self.options_manager = options_manager
        self.assets = assets
        self.in_game = in_game
        self.screen = pygame.display.get_surface()
        self.sm_font = self.assets.get_font('pixel_16')
        self.font = self.assets.get_font('pixel_24')
        self.title_font = self.assets.get_font('pixel_64')
        if self.in_game:
            self.options = ['Resume', 'Return to Main Menu']
        else:
            self.options = ['Start Game', 'Options', 'Read This', 'High Scores', 'Exit']
        self.selected_index = 0
        self.running = True
        self.resume_game = False
        self.return_to_main = False
        self.username = ""

        # Menu animation properties
        self.animation_time = 0
        self.animation_speed = 2
        self.bounce_height = 20
        self.character_base_y = 160  # Moved up
        self.menu_start_y = 300      # Moved up
        self.is_jumping = False      # Track jump state


    def run_pause_menu(self):
        self.assets.play_menu_music()
        self.resume_game = False
        self.return_to_main = False
        self.running = True  # Reset running state
        clock = pygame.time.Clock()
        while self.running:
            self._handle_pause_events()
            self._render_pause_menu()
            pygame.display.flip()
            clock.tick(60)
        if self.resume_game:
            self.assets.play_game_music()

    def _handle_pause_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.resume_game = True
                    self.running = False
                elif event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                    self.assets.play_sound('highlight')
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                    self.assets.play_sound('highlight')
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.assets.play_sound('select')
                    if self.selected_index == 0:
                        self.resume_game = True
                    elif self.selected_index == 1:
                        self.return_to_main = True
                    self.running = False

    def _load_levels(self) -> List[str]:
        levels = []
        level_folder = self.level_manager.level_folder
        for filename in os.listdir(level_folder):
            if filename.endswith('.json'):
                levels.append(filename.replace('.json', ''))
        levels.sort(key=lambda x: int(x))
        return levels

    def run(self) -> str:
        clock = pygame.time.Clock()
        if not self.in_game:
            self.username = self._get_username(clock)
            self._main_menu(clock)  # Add main menu after username
        while self.running:
            self._handle_events()
            self._render()
            pygame.display.flip()
            clock.tick(60)
        self.assets.play_game_music()
        return self.options[self.selected_index]  # Removed int() cast
    

    def _main_menu(self, clock: pygame.time.Clock):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                        self.assets.play_sound('highlight')
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                        self.assets.play_sound('highlight')
                    elif event.key == pygame.K_RETURN:
                        self.assets.play_sound('select')
                        if self.options[self.selected_index] == 'Start Game':
                            self.running = False
                        elif self.options[self.selected_index] == 'Read This':
                            self._show_instructions()
                        elif self.options[self.selected_index] == 'Options':
                            self._show_options()
                        elif self.options[self.selected_index] == 'High Scores':
                            self._show_high_scores()
                        elif self.options[self.selected_index] == 'Exit':
                            pygame.quit()
                            sys.exit()

            self._render_main_menu()
            clock.tick(60)

    def _show_options(self):
        waiting = True
        selected_option = 0
        options_list = [
            'Master Volume',
            'Music Volume',
            'Sound Effects',
            'Back'
        ]
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                    elif event.key == pygame.K_UP:
                        self.assets.play_sound('highlight')
                        selected_option = (selected_option - 1) % len(options_list)
                    elif event.key == pygame.K_DOWN:
                        self.assets.play_sound('highlight')
                        selected_option = (selected_option + 1) % len(options_list)
                    elif event.key == pygame.K_LEFT:
                        self._adjust_option(selected_option, -1)
                    elif event.key == pygame.K_RIGHT:
                        self._adjust_option(selected_option, 1)
                    elif event.key == pygame.K_RETURN and options_list[selected_option] == 'Back':
                        waiting = False

            self.screen.fill((0, 0, 0))
            
            # Title
            title = self.title_font.render("Options", True, (255, 215, 0))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
            self.screen.blit(title, title_rect)
            
            y_pos = 180
            for i, option in enumerate(options_list):
                # Option name
                color = (255, 215, 0) if i == selected_option else (255, 255, 255)
                text = self.sm_font.render(option, True, color)
                text_rect = text.get_rect(x=self.screen.get_width() // 4, centery=y_pos)
                self.screen.blit(text, text_rect)
                
                # Value bar for adjustable options
                if option != 'Back':
                    value = self._get_option_value(option)
                    bar_width = 200
                    bar_height = 20
                    bar_x = self.screen.get_width() * 3 // 4 - bar_width // 2
                    bar_y = y_pos - bar_height // 2
                    
                    # Background bar
                    pygame.draw.rect(self.screen, (100, 100, 100), 
                                   (bar_x, bar_y, bar_width, bar_height))
                    
                    # Value bar
                    value_width = int(bar_width * value)
                    pygame.draw.rect(self.screen, color,
                                   (bar_x, bar_y, value_width, bar_height))
                    
                    # Value text
                    value_text = f"{int(value * 100)}%"
                    text = self.sm_font.render(value_text, True, (255, 255, 255))
                    text_rect = text.get_rect(midleft=(bar_x + bar_width + 10, y_pos))
                    self.screen.blit(text, text_rect)
                
                y_pos += 50
            
            # Instructions
            instructions = self.sm_font.render("← → to adjust, ESC to save & return", True, (100, 100, 100))
            instructions_rect = instructions.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 40))
            self.screen.blit(instructions, instructions_rect)
            
            pygame.display.flip()
        
        # Save options when leaving menu
        self.options_manager.save_options()
        self.options_manager.apply_volume_settings(self.assets)

    def _adjust_option(self, selected_option, direction):
        option_name = ['Master Volume', 'Music Volume', 'Sound Effects',
                      'Rotate Speed', 'Gravity', 'Jump Power'][selected_option]
        
        if option_name in ['Master Volume', 'Music Volume', 'Sound Effects']:
            current = self._get_option_value(option_name)
            new_value = max(0.0, min(1.0, current + direction * 0.1))
            if option_name == 'Master Volume':
                self.options_manager.options['master_volume'] = new_value
            elif option_name == 'Music Volume':
                self.options_manager.options['music_volume'] = new_value
            elif option_name == 'Sound Effects':
                self.options_manager.options['sfx_volume'] = new_value
        
        elif option_name == 'Rotate Speed':
            current = self.options_manager.options['rotate_speed']
            new_value = max(math.pi/96, min(math.pi/12, current + direction * (math.pi/96)))
            self.options_manager.options['rotate_speed'] = new_value
        
        elif option_name == 'Gravity':
            current = self.options_manager.options['gravity']
            new_value = max(0.005, min(0.5, current + direction * 0.001))
            self.options_manager.options['gravity'] = new_value
        
        elif option_name == 'Jump Power':
            current = self.options_manager.options['jump_velocity']
            new_value = max(0.1, min(0.7, current + direction * 0.01))
            self.options_manager.options['jump_velocity'] = new_value

        # Play test sound for volume changes
        if option_name in ['Master Volume', 'Music Volume', 'Sound Effects']:
            self.assets.play_sound('highlight')

    def _get_option_value(self, option_name):
        if option_name == 'Master Volume':
            return self.options_manager.options['master_volume']
        elif option_name == 'Music Volume':
            return self.options_manager.options['music_volume']
        elif option_name == 'Sound Effects':
            return self.options_manager.options['sfx_volume']
        elif option_name == 'Rotate Speed':
            return self.options_manager.options['rotate_speed'] / (math.pi/48)
        elif option_name == 'Gravity':
            return self.options_manager.options['gravity'] / 0.01
        elif option_name == 'Jump Power':
            return self.options_manager.options['jump_velocity'] / 0.3

    def _show_instructions(self):
        waiting = True
        current_page = 1
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.assets.play_sound('select')
                        waiting = False
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.assets.play_sound('select')
                        if current_page == 1:
                            current_page = 2
                        else:
                            waiting = False

            self.screen.fill((0, 0, 0))
            
            if current_page == 1:
                # Title
                title = self.title_font.render("The Story", True, (255, 215, 0))
                title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
                self.screen.blit(title, title_rect)
                
                # Scenario
                story = [
                    "You are a lost 2D explorer in a 3D world,",
                    "stranded far from your home.",
                    "",
                    "Your mission is to reach the golden targets",
                    "while navigating through increasingly difficult",
                    "geometric landscapes that rotate at your command.",
                    "",
                    "But beware! Your energy depletes with time,",
                    "and each jump brings you closer to exhaustion.",
                    "Enemies will also attempt to thwart your progress.",
                    "",
                    "Can you master the art of dimensional rotation",
                    "& complete your mission before your energy fades?"
                ]
                
                y_pos = 160
                for line in story:
                    text = self.sm_font.render(line, True, (255, 255, 255))
                    text_rect = text.get_rect(center=(self.screen.get_width() // 2, y_pos))
                    self.screen.blit(text, text_rect)
                    y_pos += 30
                
                # Next page instruction
                next_text = self.sm_font.render("Press SPACE/ENTER for controls", True, (100, 100, 100))
                next_rect = next_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
                self.screen.blit(next_text, next_rect)
            
            else:  # Page 2
                # Title
                title = self.title_font.render("How to Play", True, (255, 215, 0))
                title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
                self.screen.blit(title, title_rect)
                
                # Instructions
                instructions = [
                    "Controls:",
                    "A/D - Move left/right",
                    "SPACE/W - Jump",
                    "Mouse Wheel - Rotate plane about player",
                    "ESC - Pause game",
                    "",
                    "Gameplay:",
                    "- Reach the golden target to complete levels",
                    "- Don't fall off or run out of points",
                    "- Jumping costs points",
                    "- Points decrease over time",
                    "- Falling & enemies causes point penalty",
                    "- Complete all levels for ultimate victory!",
                ]
                
                y_pos = 160
                for line in instructions:
                    text = self.sm_font.render(line, True, (255, 255, 255))
                    text_rect = text.get_rect(center=(self.screen.get_width() // 2, y_pos))
                    self.screen.blit(text, text_rect)
                    y_pos += 30
                
                # Back instruction
                back_text = self.sm_font.render("Press ESC/SPACE/ENTER to return", True, (100, 100, 100))
                back_rect = back_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
                self.screen.blit(back_text, back_rect)
            
            pygame.display.flip()

    def _show_high_scores(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        self.assets.play_sound('select')
                        waiting = False

            self.screen.fill((0, 0, 0))
            
            # Title
            title = self.title_font.render("High Scores", True, (255, 215, 0))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
            self.screen.blit(title, title_rect)
            
            # Get top 5 scores
            top_scores = sorted(self.high_score_manager.high_scores.items(), 
                              key=lambda x: x[1], reverse=True)[:5]
            
            y_pos = 180
            for i, (username, score) in enumerate(top_scores, 1):
                # Rank
                rank_text = self.font.render(f"{i}.", True, (255, 215, 0))
                rank_rect = rank_text.get_rect(right=self.screen.get_width() // 2 - 50, centery=y_pos)
                self.screen.blit(rank_text, rank_rect)
                
                # Username
                name_text = self.font.render(username, True, (255, 255, 255))
                name_rect = name_text.get_rect(x=self.screen.get_width() // 2 - 40, centery=y_pos)
                self.screen.blit(name_text, name_rect)
                
                # Score
                score_text = self.font.render(str(int(score)), True, (255, 255, 255))
                score_rect = score_text.get_rect(x=self.screen.get_width() // 2 + 100, centery=y_pos)
                self.screen.blit(score_text, score_rect)
                
                y_pos += 50
            
            # Back instruction
            back_text = self.sm_font.render("Press ESC/SPACE/ENTER to return", True, (100, 100, 100))
            back_rect = back_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
            self.screen.blit(back_text, back_rect)
            
            pygame.display.flip()

    def _render_main_menu(self):
        self.screen.fill((0, 0, 0))
        
        # Update animation and jump state
        self.animation_time = (self.animation_time + 0.016) % self.animation_speed
        bounce_offset = math.sin(self.animation_time * math.pi / (self.animation_speed/2)) * self.bounce_height
        self.is_jumping = bounce_offset > 5  # Switch to jump sprite when bouncing up
        
        # Draw title
        title_surface = self.title_font.render("Rotander", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 80))
        self.screen.blit(title_surface, title_rect)

        # Draw character sprite
        sprite_name = 'player_jump_up' if self.is_jumping else 'player_stand'
        sprite = self.assets.get_sprite(sprite_name)
        if sprite:
            scaled_width = MovementSettings.user_width_pixels * 2
            scaled_height = MovementSettings.user_height_pixels * 2
            scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
            
            sprite_x = self.screen.get_width() // 2 - scaled_width // 2
            sprite_y = self.character_base_y - scaled_height // 2 - bounce_offset
            self.screen.blit(scaled_sprite, (sprite_x, sprite_y))

        # Draw menu options
        for idx, option in enumerate(self.options):
            color = (255, 215, 0) if idx == self.selected_index else (255, 255, 255)
            option_surface = self.font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(self.screen.get_width() // 2, self.menu_start_y + idx * 50))
            self.screen.blit(option_surface, option_rect)

        pygame.display.flip()

    def _get_username(self, clock: pygame.time.Clock) -> str:
                username = ""
                input_active = True
                while input_active:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                self.assets.play_sound('select')
                                input_active = False
                            elif event.key == pygame.K_BACKSPACE:
                                self.assets.play_sound('highlight')
                                username = username[:-1]
                            else:
                                if len(event.unicode.strip()) > 0:  # Only play sound for actual characters
                                    self.assets.play_sound('highlight')
                                username += event.unicode
                    self.screen.fill((0, 0, 0))
                    prompt_surface = self.font.render("Enter Username:", True, (255, 255, 255))
                    prompt_rect = prompt_surface.get_rect(center=(self.screen.get_width() // 2, 200))
                    self.screen.blit(prompt_surface, prompt_rect)
                    
                    username_surface = self.font.render(username, True, (255, 255, 255))
                    username_rect = username_surface.get_rect(center=(self.screen.get_width() // 2, 250))
                    self.screen.blit(username_surface, username_rect)
                    pygame.display.flip()
                    clock.tick(30)
                return username

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                    self.assets.play_sound('highlight')
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                    self.assets.play_sound('highlight')
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.assets.play_sound('select')
                    self.running = False

    def _render_pause_menu(self):
        self.screen.fill((0, 0, 0))
        title_surface = self.title_font.render("Paused", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title_surface, title_rect)

        for idx, option in enumerate(self.options):
            if idx == self.selected_index:
                color = (255, 215, 0)  # Highlighted color
            else:
                color = (255, 255, 255)
            option_surface = self.font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(self.screen.get_width() // 2, 300 + idx * 50))
            self.screen.blit(option_surface, option_rect)


    def _render(self):
        self.screen.fill((0, 0, 0))
        title_surface = self.title_font.render("Rotander", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_surface, title_rect)

        for idx, option in enumerate(self.options):
            if idx == self.selected_index:
                color = (255, 215, 0)  # Highlighted color
            else:
                color = (255, 255, 255)
            option_surface = self.font.render(f"Level {option}", True, color)
            option_rect = option_surface.get_rect(center=(self.screen.get_width() // 2, 200 + idx * 40))
            self.screen.blit(option_surface, option_rect)