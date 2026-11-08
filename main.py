# main.py
import pygame
import sys
import os
import random
from os.path import join

# file imports 
from settings_and_level import width, height, fps, map_1, start_map
from bg_tiles import BgTiles
from blocks import Block
from Servers.network import Network

from starting import StartingScreen
from blackScreen import BlackScreen
from player import Player
from font import Font

class Game:
    def __init__(self, width, height, fps):
        pygame.init()
        
        # setups
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.width = width
        self.height = height
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Platformer')
        self.clock = pygame.time.Clock()
        
        # Prevent window unresponsiveness during network init
        pygame.event.pump()
        self.screen.fill((0, 0, 0))
        pygame.display.update()

        self.black_screen_start_time = 0
        self.music_start = False
        self.game_over = False
        
        self.player_config = [
            {"x":300,"y":686,"skin_idx":0},
            {"x":500,"y":490,"skin_idx":1},
            {"x":1700,"y":120,"skin_idx":2},
            {"x":1335,"y":380,"skin_idx":3}
            
        ]
      
      
        # Network setup with fallback for single-player/offline
        try:
            self.net = Network(server_ip="127.0.0.1", port=5555)
            if hasattr(self.net, "player_id") and self.net.player_id is not None:
                self.my_id = str(self.net.player_id)
                self.num = getattr(self.net, "num", int(self.my_id) % 4)
            else:
                self.net = None
                self.my_id = None
                self.num = 0
        except Exception as e:
            print(f"Network initialization warning: {e}")
            self.net = None
            self.my_id = None
            self.num = 0
            
        self.other_players = {}
        
        self.rect = pygame.Rect(0, 0, self.width + 100, 130)
        
        self.tiles = BgTiles(self.width, self.height)
        self.background = self.tiles.tiles
        self.bg_image = self.tiles.img
        self.state = "starting"
        self.buttons = StartingScreen(700, 350, 1000, 500)
        
        self.black_screen = BlackScreen(0, 0, self.width, self.height)
        self.time = 5000
        
        # Game over UI buttons
        self.play_again_btn = pygame.image.load(join(self.BASE_DIR, "assets", "start.png")).convert_alpha()
        self.play_again_btn_x = 700
        self.play_again_btn_y = 300
        self.play_again_btn_rect = pygame.Rect(
            self.play_again_btn_x, 
            self.play_again_btn_y, 
            self.play_again_btn.get_width(), 
            self.play_again_btn.get_height()
        )
        
        self.exit_btn = pygame.image.load(join(self.BASE_DIR, "assets", "exit.png")).convert_alpha()
        self.exit_btn_x = 1100
        self.exit_btn_y = 300
        self.exit_btn_rect = self.exit_btn.get_rect()
        
        # Coins and UI icons
        self.coin_record = Block(1890, 10, join(self.BASE_DIR, "assets", "coin.png"), 100, 100)
        
        # Level blocks
        self.blocks = []
        self.block_path = join(self.BASE_DIR, "assets", "Block1.png")
        
        # Character skin configuration
        self.characters_name = [
            "ninja.png",
            "virtualguy.png",
            "maskdude.png",
            "pinkman.png",
        ]
        
        self.characters_fall_name = [
            "ninjafall.png",
            "virtualguyfall.png",
            "maskdudefall.png",
            "pinkmanfall.png",
        ]
        
        self.player_name = self.characters_name[self.num]
        self.player = Player(300, 686, self.player_name, self.blocks, self.characters_fall_name[self.num])
        self.players = [  
            Player(500, 490, self.characters_name[1], self.blocks, self.characters_fall_name[1]),
            Player(300, 190, self.characters_name[0], self.blocks, self.characters_fall_name[0]),
            Player(1600, 90, self.characters_name[2], self.blocks, self.characters_fall_name[2]),
            Player(1500, 490, self.characters_name[3], self.blocks, self.characters_fall_name[3])
        ]
        
        # Fonts
        self.font = Font(0, 0, None, 11) 
        self.font2 = Font(0, 0, None, 5)
        self.font3 = Font(0, 0, None, 5)
        self.font4 = Font(0, 0, None, 20)
        self.font5 = Font(0, 0, None, 11)
        self.coin_font = Font(0, 0, None, 100)
        
        # Map and coin setup
        self.removed_coins = []
        self.load_map()
        self.s_blocks = []
        self.load_start_map() 
        self.coin_path = join(self.BASE_DIR, "assets", "coin.png")
        self.coins = []
        self.respawning_coins = []  
        self.coin_count = 0
        self.coin_spawn_time = 15000
        self.is_game_over = False
        self.exit_game_btn_touch = False
        self.load_coin()
        self.reset_level()
        
    def update_multiplayer(self):
        # Check network connection status
        if not self.net or not getattr(self.net, "connected", False):
            return

        # 1. Package local player state including local death status
        my_data = {
            "x": self.player.player_rect.x,
            "y": self.player.player_rect.y,
            "num": self.num,
            "facing_right": getattr(self.player, "facing_right", True),
            "is_falling": getattr(self.player, "is_falling", False),
            "is_dead": self.game_over  # Notify server if local player is dead
        }
        
        # 2. Send local state and get back dictionary of all connected players
        all_players_data = self.net.send(my_data)
        
        if not all_players_data or not isinstance(all_players_data, dict):
            return
        
        my_id_str = str(self.net.player_id) if self.net.player_id is not None else ""

        # 3. Update or spawn remote players
        for p_id_raw, p_data in all_players_data.items():
            p_id_str = str(p_id_raw)
            
            # Skip local player
            if p_id_str == my_id_str:
                continue  
                
            if p_id_str not in self.other_players:
                char_idx = p_data.get("num", 0) % len(self.characters_name)
                remote_p = Player(
                    p_data.get("x", 300), 
                    p_data.get("y", 686), 
                    self.characters_name[char_idx], 
                    self.blocks, 
                    self.characters_fall_name[char_idx]
                )
                self.other_players[p_id_str] = remote_p
            else:
                remote_p = self.other_players[p_id_str]
                new_x = p_data.get("x", remote_p.player_rect.x)
                new_y = p_data.get("y", remote_p.player_rect.y)
                
                remote_p.player_rect.x = new_x
                remote_p.player_rect.y = new_y
                if hasattr(remote_p, 'rect'):
                    remote_p.rect.x = new_x
                    remote_p.rect.y = new_y
                
                if hasattr(remote_p, "facing_right"):
                    remote_p.facing_right = p_data.get("facing_right", True)
                if hasattr(remote_p, "is_falling"):
                    remote_p.is_falling = p_data.get("is_falling", False)
                    
            # Store remote death status on the player instance
            self.other_players[p_id_str].is_dead = p_data.get("is_dead", False)
                   
    def reset_level(self):
        # Reset local death flags on respawn
        self.game_over = False
        self.music_start = False
        self.is_game_over = False
        
        # Reset positions for UI animation
        self.game_over_y = 100
        self.btn_x, self.btn_y = 700, 300
        self.e_btn_x, self.e_btn_y = 1100, 300
        self.play_again_rect = self.play_again_btn.get_rect(topleft=(self.btn_x, self.btn_y))
        self.exit_btn_rect = self.exit_btn.get_rect(topleft=(self.e_btn_x, self.e_btn_y))
        
        # Rebuild level
        self.blocks = []
        self.coins = []
        self.respawning_coins = []
        self.coin_count = 0
        
        self.load_map()
        self.load_coin()
        
        self.spawn = random.choice(self.player_config)
        self.player = Player(
            self.spawn["x"],
            self.spawn["y"], 
            self.characters_name[self.num], 
            self.blocks, 
            self.characters_fall_name[self.num]
           )
        
    def load_bg_music(self):
        self.volume = 0.2
        try:
            pygame.mixer.music.load(join(self.BASE_DIR, "assets", "bg_music2.mp3"))
            pygame.mixer.music.set_volume(self.volume)   
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Music load warning: {e}")
        
    def load_map(self):
        self.block_size = 100
        for row_index, row in enumerate(map_1):
            for col_index, cell in enumerate(row):
                x = col_index * self.block_size
                y = row_index * self.block_size
                if cell == "x":
                    block = Block(x, y, self.block_path, 115, 115)
                    self.blocks.append(block)
                    
    def load_start_map(self):
        for row_index, row in enumerate(start_map):
            for col_index, cell in enumerate(row):
                x = col_index * self.block_size
                y = row_index * self.block_size
                if cell == "x":
                    s_block = Block(x, y, self.block_path, 115, 115)
                    self.s_blocks.append(s_block)

    def load_coin(self):
        for row_index, row in enumerate(map_1):
            for col_index, cell in enumerate(row):
                x = col_index * self.block_size
                y = row_index * self.block_size
                if cell == "c":
                    coin = Block(x + 20, y, self.coin_path, 65, 55)
                    self.coins.append(coin)

    def handle_coin_respawns(self):
        current_time = pygame.time.get_ticks()
        for item in self.respawning_coins[:]:
            respawn_time, pos_x, pos_y = item
            
            if current_time >= respawn_time:
                new_coin = Block(pos_x + 20, pos_y, self.coin_path, 65, 65)
                self.coins.append(new_coin)
                self.respawning_coins.remove(item)
    
    def loading_logic(self):
        if self.elapsed_time <= 500:
            self.font2.draw_rpg_font("Loading Server.", 840, 600, self.screen)
        elif 500 <= self.elapsed_time < 1000:
            self.font2.draw_rpg_font("Loading Server..", 840, 600, self.screen)
        elif 1000 <= self.elapsed_time < 1500:
            self.font3.draw_rpg_font("Loading Server...", 840, 600, self.screen)
        elif 1500 <= self.elapsed_time < 2000:
            self.font3.draw_rpg_font("Loading Server.", 840, 600, self.screen)
        elif 2000 <= self.elapsed_time < 2500:
            self.font3.draw_rpg_font("Loading Server..", 840, 600, self.screen)
        elif 2500 <= self.elapsed_time < 5000:
            self.font3.draw_rpg_font("Connecting...", 860, 600, self.screen)

    def start_game(self):
        for tile in self.background:
            self.screen.blit(self.bg_image, tile)
            
        for block in self.blocks:
            block.draw(self.screen)
       
        # Send/receive network positions
        self.update_multiplayer()
           
        # Draw local player if alive
        if not self.game_over:
            self.player.draw(self.screen)
        
        # Draw remote players ONLY IF local player is alive AND remote player is alive
        if not self.game_over:
            for remote_player in self.other_players.values():
                if not getattr(remote_player, "is_dead", False):
                    remote_player.draw(self.screen)
            
        self.coin_record.draw(self.screen)
        
        current_time = pygame.time.get_ticks()
        
        # Check coin collisions & register respawn timer
        if not self.game_over:
            for coin in self.coins[:]:
                coin.draw(self.screen)
                if self.player.player_rect.colliderect(coin):
                    respawn_at = current_time + self.coin_spawn_time
                    coin_x = coin.rect.x if hasattr(coin, 'rect') else coin.x
                    coin_y = coin.rect.y if hasattr(coin, 'rect') else coin.y
                    
                    self.respawning_coins.append((respawn_at, coin_x, coin_y))
                    self.coins.remove(coin)
                    self.coin_count += 1
        else:
            for coin in self.coins:
                coin.draw(self.screen)
        
        # Update respawning coins timer
        self.handle_coin_respawns()
              
        self.font5.draw_rpg_font(f"{self.coin_count}", 2000, 8, self.screen)
        
        self.elapsed_time = pygame.time.get_ticks() - self.black_screen_start_time
        if self.elapsed_time < self.time:
            self.black_screen.draw(self.screen)
            self.font.draw_rpg_font("Platformer", 700, 400, self.screen)
            self.loading_logic()
        else:
            if not self.music_start:
                self.load_bg_music()
                self.music_start = True
                
            self.black_screen.move()

    def start_game_screen(self):
        for tile in self.background:
            self.screen.blit(self.bg_image, tile)
        for block in self.s_blocks:
            block.draw(self.screen)
        for player in self.players:
            player.draw(self.screen)
            
        self.buttons.draw(self.screen)
    
    def handel_player_move(self):
        if pygame.time.get_ticks() - self.black_screen_start_time < self.time or self.game_over:
            return
            
        if pygame.mouse.get_pressed()[0]:
            touch_x, touch_y = pygame.mouse.get_pos()
            if touch_x >= self.width / 2:
                self.player.move_right()
            elif touch_x < self.width / 2:
                self.player.move_left()

    def handel_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.tx, self.ty = event.pos
                if self.state == "starting":
                    if self.buttons.start_rect.collidepoint(self.tx, self.ty):
                        self.state = "playing"
                        self.black_screen_start_time = pygame.time.get_ticks()
                        self.music_start = False
                        
                    elif self.buttons.exit_rect.collidepoint(self.tx, self.ty):
                        self.running = False
                        
                elif self.state == "playing":
                    if self.game_over:
                        if self.play_again_btn_rect.collidepoint(self.tx, self.ty):
                            self.reset_level()
                        elif self.exit_btn_rect.collidepoint(self.tx, self.ty):
                            self.exit_game_btn_touch = True
                            pygame.quit()
                            sys.exit()
                    else:
                        if self.ty < self.height / 2:
                            self.player.jump()

    def run(self):
        self.running = True
        while self.running:
            self.handel_event()
            #print(self.player.player_rect.x,self.player.player_rect.y)
            if self.state == "starting":
                self.start_game_screen()
                
            elif self.state == "playing":
                if not self.game_over:
                    self.player.update()
                    
                self.start_game()       
                self.handel_player_move()
                
                if self.player.player_rect.y > self.height + 500:
                    self.game_over = True
                    
                    if not self.is_game_over:
                        try:
                            pygame.mixer.music.fadeout(2500)
                        except Exception:
                            pass
                        self.is_game_over = True
                    
                    for coin in self.coins[:]:
                        self.removed_coins.append(coin)
                        self.coins.remove(coin)
                        
                    if self.game_over_y < 400:
                        self.game_over_y += 1
                    else:
                        self.game_over_y = 400
                        
                    if self.play_again_btn_y < 600:
                        self.play_again_btn_y += 1 
                    else:
                        self.play_again_btn_y = 600
                        
                    if self.exit_btn_y < 600:
                        self.exit_btn_y += 1
                    else:
                        self.exit_btn_y = 600
                        
                    self.play_again_btn_rect.y = self.play_again_btn_y
                    self.exit_btn_rect.y = self.exit_btn_y
                    
                    self.screen.blit(self.exit_btn, (self.exit_btn_x, self.exit_btn_y))
                    self.screen.blit(self.play_again_btn, (self.play_again_btn_x, self.play_again_btn_y))
                    
                    if not self.exit_game_btn_touch:
                        self.font4.draw_rpg_font("GAME OVER!", 350, self.game_over_y, self.screen)
                        
            pygame.display.update()
            self.clock.tick(self.fps)
            
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
            
        pygame.quit()
        sys.exit()    

if __name__ == "__main__":
    game = Game(width, height, fps)
    game.run()