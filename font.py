#font.py
import pygame
from os.path import join
import os

class Font:
    def __init__(self,x,y,text,scale):
        self.x = x
        self.y = y
        self.text = text
        self.txt_col = (255,255,255)
        self.scale = scale
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
   #simple fonts     
    def draw_font(self,win):
        self.win = win
        self.font = pygame.font.SysFont("palatino, garamond, georgia",200,bold=True)
        self.img = self.font.render(self.text,True,self.txt_col)
        
        self.win.blit(self.img,(self.x,self.y))
    
    #game font    
    def rpg_font(self):
        self.font_sheet = pygame.image.load(join(self.BASE_DIR,"assets","whitetext.png")).convert_alpha()
        
        self.txt_w = 8
        self.txt_h = 10
        
        self.render_w = self.txt_w * self.scale
        self.render_h = self.txt_h * self.scale
        
        
        self.font_layout = [
            "ABCDEFGHIJ",
            "KLMNOPQRST",
            "UVWXYZ    ",
            "0123456789",
            ".,:?!()+- "
        ]
        self.font_dict = {}
        
        for row_index,row in enumerate(self.font_layout):
            for col_index,cell in enumerate(row):
                
                self.x = col_index * self.txt_w
                self.y = row_index * self.txt_h
                
                if cell == " ":
                    continue
                    
                char_rect = pygame.Rect(self.x,self.y,self.txt_w,self.txt_h)
                
                self.orignal_char_rect = self.font_sheet.subsurface(char_rect)
                self.scaled_char_rect = pygame.transform.scale(self.orignal_char_rect,(self.render_w,self.render_h))
                
                
                self.font_dict[cell] = self.scaled_char_rect
        
    def draw_rpg_font(self,text,start_x,start_y,win):
        self.rpg_font()
        self.current_x = start_x
        self.screen = win
        
        for char in text.upper():
            if char in self.font_dict:
                self.screen.blit(self.font_dict[char],(self.current_x,start_y))
                self.current_x += self.render_w
            elif char == " ":
                self.current_x += self.render_w
         