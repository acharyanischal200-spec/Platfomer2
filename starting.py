#starting.py
import pygame
import os
from os.path import join

class StartingScreen(pygame.sprite.Sprite):
    def __init__(self, s_x, s_y, e_x, e_y):
        super().__init__()
        
        self.s_x = s_x
        self.s_y = s_y
        self.e_x = e_x
        self.e_y = e_y
        
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Load images
        self.start_img = pygame.image.load(join(self.BASE_DIR, "assets", "start.png")).convert_alpha()
        self.exit_img = pygame.image.load(join(self.BASE_DIR, "assets", "exit.png")).convert_alpha()
        
        # Get dimensions
        self.s_width, self.s_height = self.start_img.get_width(), self.start_img.get_height()
        self.e_width, self.e_height = self.exit_img.get_width(), self.exit_img.get_height()
        
        # Assign rect positions directly
        self.start_rect = pygame.Rect(self.s_x, self.s_y, self.s_width, self.s_height)
        self.exit_rect = pygame.Rect(self.e_x, self.e_y, self.e_width, self.e_height)
    
    def draw(self, win):
        win.blit(self.start_img, self.start_rect)
        win.blit(self.exit_img, self.exit_rect)