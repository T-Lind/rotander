import pygame
from typing import List
from asset_manager import AssetManager
from level_manager import LevelManager
from high_score_manager import HighScoreManager
import os

class MenuManager:
    def __init__(self, level_manager: LevelManager, assets: AssetManager, high_score_manager: HighScoreManager, in_game=False):
        self.level_manager = level_manager
        self.high_score_manager = high_score_manager
        self.assets = assets
        self.in_game = in_game
        self.screen = pygame.display.get_surface()
        self.sm_font = self.assets.get_font('pixel_16')
        self.font = self.assets.get_font('pixel_24')
        self.title_font = self.assets.get_font('pixel_64')
        if self.in_game:
            self.options = ['Resume', 'Return to Main Menu']
        else:
            self.options = ['Start Game', 'Read This', 'High Scores', 'Exit']
        self.selected_index = 0
        self.running = True
        self.resume_game = False
        self.return_to_main = False
        self.username = ""


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
                exit()
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
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.options[self.selected_index] == 'Start Game':
                            self.running = False
                        elif self.options[self.selected_index] == 'Read This':
                            self._show_instructions()
                        elif self.options[self.selected_index] == 'High Scores':
                            self._show_high_scores()
                        elif self.options[self.selected_index] == 'Exit':
                            pygame.quit()
                            exit()

            self._render_main_menu()
            clock.tick(60)

    def _show_instructions(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        waiting = False

            self.screen.fill((0, 0, 0))
            
            # Title
            title = self.title_font.render("How to Play", True, (255, 215, 0))
            title_rect = title.get_rect(center=(self.screen.get_width() // 2, 80))
            self.screen.blit(title, title_rect)
            
            # Instructions
            instructions = [
                "Controls:",
                "A/D - Move left/right",
                "SPACE/W - Jump",
                "Mouse Wheel - Rotate level",
                "ESC - Pause game",
                "",
                "Gameplay:",
                "- Reach the golden target to complete levels",
                "- Don't fall off or run out of points",
                "- Jumping costs points",
                "- Points decrease over time",
                "- Falling causes point penalty",
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
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
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
                score_text = self.font.render(str(score), True, (255, 255, 255))
                score_rect = score_text.get_rect(x=self.screen.get_width() // 2 + 100, centery=y_pos)
                self.screen.blit(score_text, score_rect)
                
                y_pos += 50
            
            # Back instruction
            back_text = self.font.render("Press ESC/SPACE/ENTER to return", True, (100, 100, 100))
            back_rect = back_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
            self.screen.blit(back_text, back_rect)
            
            pygame.display.flip()

    def _render_main_menu(self):
        self.screen.fill((0, 0, 0))
        title_surface = self.title_font.render("Rotander", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title_surface, title_rect)

        for idx, option in enumerate(self.options):
            color = (255, 215, 0) if idx == self.selected_index else (255, 255, 255)
            option_surface = self.font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(self.screen.get_width() // 2, 300 + idx * 50))
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
                            exit()
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RETURN:
                                input_active = False
                            elif event.key == pygame.K_BACKSPACE:
                                username = username[:-1]
                            else:
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
                exit()
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