#player.py
import pygame
from os.path import join
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, name, blocks,fall):
        super().__init__()
        self.width = 120
        self.height = 120
        self.speed = 6
        self.name = name
        self.fall = fall
        self.blocks = blocks
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Load standard character images
        base_img = pygame.image.load(join("/storage", "emulated", "0", "Platfomer/assets", self.name)).convert_alpha()
        base_img = pygame.transform.scale(base_img, (self.width, self.height))
        
        self.right_img = base_img
        self.left_img = pygame.transform.flip(base_img, True, False)
        
        # 1. LOAD FALL IMAGE (Load  fall image file here)
        fall_base = pygame.image.load(join(self.BASE_DIR, "assets", self.fall)).convert_alpha()
        fall_base = pygame.transform.scale(fall_base, (self.width, self.height))
        self.fall_right = fall_base
        self.fall_left = pygame.transform.flip(fall_base, True, False)

        self.img = self.right_img
        self.facing = "right"  # Track facing direction ("right" or "left")
        
        # Hitbox setup
        hitbox_width = 60
        offset_x = (self.width - hitbox_width) // 2
        self.player_rect = pygame.Rect(x + offset_x, y, hitbox_width, self.height)
        
        # Physics State Variables
        self.vel_y = 0
        self.on_ground = False
        self.jump_power = -16
        self.gravity = 0.9
        self.max_jump = 2
        self.jump_left = self.max_jump
        
    def jump(self):
        if self.jump_left > 0:
            self.vel_y = self.jump_power
            self.jump_left -= 1
            self.on_ground = False
            
    def move_left(self):
        self.player_rect.x -= self.speed
        self.facing = "left"  # Update direction facing
        
        for block in self.blocks:
            if self.player_rect.colliderect(block.rect):
                self.player_rect.left = block.rect.right

    def move_right(self):
        self.player_rect.x += self.speed
        self.facing = "right"  # Update direction facing
        
        for block in self.blocks:
            if self.player_rect.colliderect(block.rect):
                self.player_rect.right = block.rect.left

    def update(self):
        # Apply gravity & position updates
        self.vel_y += self.gravity
        if self.vel_y > 15:
            self.vel_y = 15

        self.player_rect.y += self.vel_y
        self.on_ground = False

        # Vertical collisions
        for block in self.blocks:
            if self.player_rect.colliderect(block.rect):
                if self.vel_y > 0:
                    self.player_rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_left = self.max_jump
                elif self.vel_y < 0:
                    self.player_rect.top = block.rect.bottom
                    self.vel_y = 0

        # 2. UPDATE SPRITE BASED ON STATE
        if not self.on_ground and self.vel_y > 0:
            # Player is falling down
            if self.facing == "right":
                self.img = self.fall_right
            else:
                self.img = self.fall_left
        else:
            # Player is on ground
            if self.facing == "right":
                self.img = self.right_img
            else:
                self.img = self.left_img

    def draw(self, win):
        draw_x = self.player_rect.x - (self.width - self.player_rect.width) // 2
        win.blit(self.img, (draw_x, self.player_rect.y))
