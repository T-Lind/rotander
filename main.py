import sys
import pygame
from level_manager import LevelManager
from settings import Settings
from viewer import GameViewer
from menu_manager import MenuManager
from asset_manager import AssetManager
from high_score_manager import HighScoreManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Rotander")

    assets = AssetManager()
    assets.play_menu_music()
    level_manager = LevelManager()
    high_score_manager = HighScoreManager()
    running = True
    username = ""
    total_score = 0

    while running:
        if level_manager.current_level is None:
            menu = MenuManager(level_manager, assets)
            selected_option = menu.run()
            username = menu.username
            if selected_option == 'Start Game':
                level_manager.current_level = 1
            elif selected_option == 'Exit':
                running = False
                continue

        level_path = level_manager.get_current_level_path()
        try:
            settings = Settings(config_path=level_path)
            viewer = GameViewer(settings, level_manager, assets, username, high_score_manager, total_score)
            viewer.run()
            total_score += viewer.points

            if viewer.return_to_main_menu:
                level_manager.current_level = None
                total_score = 0
            elif viewer.level_complete:
                if level_manager.has_next_level():
                    level_manager.advance_level()
                else:
                    # Ultimate Victory!
                    assets.stop_music()
                    current_high_score = high_score_manager.high_scores.get(username, 0)
                    is_high_score = total_score > current_high_score
                    viewer.renderer.render_ultimate_victory_message(total_score, is_high_score)
                    high_score_manager.add_score(username, total_score)
                    
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
                        pygame.time.Clock().tick(30)
                        
                    level_manager.current_level = None
                    total_score = 0
            elif not viewer.running:
                running = False

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            running = False

    high_score_manager.save_high_scores()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()