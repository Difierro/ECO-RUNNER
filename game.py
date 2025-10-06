import pygame
from pygame.locals import *
from sys import exit
from scripts.entities import PhysiscsEntitiy
from scripts.tilemap import Tilemap 
from scripts.utils import load_image, load_images

class Game:
    def __init__(self):
        pygame.init()
        width = 640
        heigth = 480
        
        pygame.display.set_caption("ECO RUNNER")
        self.screen = pygame.display.set_mode((width, heigth))
        
        self.clock = pygame.time.Clock()
    
        self.movement = [False, False]
        
        self.collision_area = pygame.Rect(50,50,300,50)
            
        self.assets = {
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'player': load_image('player/guardia1.png')
        }
        self.player = PhysiscsEntitiy(self, 'player', (50,50), (16,16))
        
        self.tilemap = Tilemap(self, tile_size=16)
    
    def run(self):
        while True:
            self.screen.fill((14,219,248))  
            
            self.tilemap.render(self.screen)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.screen)
            
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
            
            pygame.display.update()
            self.clock.tick(60)
 
if __name__ == "__main__":                    
    Game().run()