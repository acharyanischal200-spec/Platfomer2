#blocks.py
import pygame


class Block(pygame.sprite.Sprite):
    def __init__(self,x,y,path,w,h):
        super().__init__()
        self.path = path
        
        self.img = pygame.image.load(self.path).convert_alpha()
        self.width = w
        self.height = h
        
        self.img = pygame.transform.scale(self.img,(self.width,self.height))
        self.rect = self.img.get_rect(topleft = (x,y))
          
    def draw(self,win):
        win.blit(self.img,self.rect)