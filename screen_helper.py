import pygame

class ScreenHelper:
    def __init__(self):
        self.windowed_size = (800, 600)
        self.is_fullscreen = False
        
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        else:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.is_fullscreen = not self.is_fullscreen
        return screen