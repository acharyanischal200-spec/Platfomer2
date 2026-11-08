#blackScreen.py
import pygame

class BlackScreen:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Expand rect dimensions once during initialization
        self.black_rect = pygame.Rect(self.x, self.y, self.width + 100, self.height + 100)

    def move(self):
        # Stop updating once it moves past the screen bounds
        if self.black_rect.x <= self.width:
            self.black_rect.x += 35

    def draw(self, win):
        # Only draw if the rect is still visible on screen
        if self.black_rect.x <= self.width:
            pygame.draw.rect(win, (0, 0, 0), self.black_rect)