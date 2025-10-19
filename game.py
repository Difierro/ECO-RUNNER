import pygame
from pygame.locals import *
from sys import exit
from scripts.entities import PhysiscsEntitiy, Player
from scripts.tilemap import Tilemap 
from scripts.utils import load_image, load_images, Animation
from scripts.clouds import Clouds


class Game:
    def __init__(self):
        pygame.init()
        width = 640
        heigth = 480
        
        pygame.display.set_caption("ECO RUNNER")
        self.screen = pygame.display.set_mode((width, heigth))
        self.display = pygame.Surface((320, 240))
        
        self.clock = pygame.time.Clock()
    
        self.movement = [False, False]
            
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'large_decor': load_images('tiles/large_decor'),
            'clouds': load_images('clouds'),
            'background': load_image('background/0.png'),
            'player/anda': Animation(load_images('player/guardia/anda'), img_dur=5),
            'player/parada': Animation(load_images('player/guardia/parada'), img_dur=6)
        }

        self.clouds = Clouds(self.assets['clouds'], 16)

        self.player = Player(self, (50,50), (16,16))
        
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load('map.json')
        
        self.scroll = [0,0]
    
    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
          
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                if event.type == KEYDOWN:
                    if event.key == K_a or event.key == K_LEFT:
                        self.movement[0] = True
                    if event.key == K_d or event.key == K_RIGHT:
                        self.movement[1] = True
                    if event.key == K_w or event.key == K_UP: 
                        self.player.velocity[1] = -3
                if event.type == KEYUP:
                    if event.key == K_a or event.key == K_LEFT:
                        self.movement[0] = False
                    if event.key == K_d or event.key == K_RIGHT:
                        self.movement[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)
 
if __name__ == "__main__":                    
    Game().run()