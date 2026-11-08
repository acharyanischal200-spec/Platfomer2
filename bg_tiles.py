#bg_tiles.py
import pygame
import os
from os.path import join

class BgTiles:
    def __init__(self,width,height):
        self.width = width
        self.height = height
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.color = "Blue" + ".png"
        self.img = pygame.image.load(join(self.BASE_DIR,"assets",self.color)).convert()
        
        self.img_width,self.img_height = self.img.get_width(),self.img.get_height()
        
        
        
        self.tiles = []
        
        for i in range(self.width // self.img_width + 1):
            for j in range(self.height // self.img_height + 1):
                pos = (i * self.img_width,j * self.img_height)
                self.tiles.append(pos)
                