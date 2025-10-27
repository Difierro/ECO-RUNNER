import pygame
from scripts.utils import load_image

class PhysiscsEntitiy:
    def __init__(self, game, entity_type, pos, size):
        self.game = game
        self.entity_type = entity_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0,0]
        self.collisions = {'up': False, 'down': False, 'left': False, 'right':False}
        
        self.action = ''
        self.anim_offset = (3, 0)
        self.flip = False
        if entity_type == 'player':
            self.set_action('anda') 
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.entity_type + '/' + self.action].copy()
    
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['up'] or self.collisions['down']:
            self.velocity[1] = 0
            
        self.animation.update()
    
    def render(self, surf, offset=(0, 0)):
        sprite_pos = (
        self.pos[0] - offset[0] - 3,
        self.pos[1] - offset[1]
        )
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), sprite_pos)


class Player(PhysiscsEntitiy):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 2

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2

        #se tiver animação para pular
        #if self.air_time > 4:
        #    self.set_action('pula')
        
        if movement[0] != 0:
           self.set_action('anda')
        else:
            self.set_action('parada')
            
    def jump(self):
        if self.jumps:
            self.velocity[1] = -2.5
            self.jumps -= 1
            self.air_time = 5
            
    def colide_lixo(self, game):
        tempo_atual = pygame.time.get_ticks()

        for tile in game.tilemap.tiles_around(self.pos):
            if tile['type'] == 'lixo':
                tile_rect = pygame.Rect(
                    tile['pos'][0] * game.tilemap.tile_size,
                    tile['pos'][1] * game.tilemap.tile_size,
                    game.tilemap.tile_size,
                    game.tilemap.tile_size
                )
                if self.rect().colliderect(tile_rect): #se colidiu
                    if not game.tempo_imune_ativo: # se ainda não está imune
                        print("colidiu com lixo radioativo!")
                        game.tempo_imune_ativo = True
                        game.tempo_imune_inicio = tempo_atual

                if game.tempo_imune_ativo: # se está imune, verifica se passou o tempo
                    tempo_passado = tempo_atual - game.tempo_imune_inicio
                    if tempo_passado >= game.duracao_imunidade:
                        print("imunidade acabou!")
                        game.tempo_imune_ativo = False
                    else:
                        print("imune...")
    
    def coleta_reciclavel(self, game, rec):
        rec_rect = rec.rect()
        player_rect = game.player.rect()
        
        # retangulo para depurar
        #pygame.draw.rect(self.display, (0,255,0), (rec_rect.x - self.scroll[0], rec_rect.y - self.scroll[1], rec_rect.width, rec_rect.height), 1)
        #pygame.draw.rect(self.display, (255,0,0), (player_rect.x - self.scroll[0], player_rect.y - self.scroll[1], player_rect.width, player_rect.height), 1)
        
        if rec.tile_data.get('aparece', True) and not rec.collected:
            if player_rect.colliderect(rec_rect):
                rec.collect()
                game.quantidade_coletada_total += 1
                print(f"Reciclável coletado! Total: {game.quantidade_coletada_total}/{game.reciclaveis_por_fase}")

class Reciclavel(PhysiscsEntitiy):
    def __init__(self, game, pos, size, variant=0):
        super().__init__(game, 'reciclavel', pos, size)
        self.variant = variant
        self.collected = False
        self.tile_data = {}  # Aqui armazenamos a info 'aparece'
        self.img = self.game.assets['reciclavel'][self.variant]

    def collect(self):
        self.collected = True

    def render(self, surf, offset=(0, 0)):
        # Se não aparece ou já foi coletado, renderiza imagem "transparente"
        if not self.tile_data.get('aparece', True) or self.collected:
            img_to_draw = load_image('colisao/1.png')
        else:
            img_to_draw = self.img
        surf.blit(img_to_draw, (self.pos[0] - offset[0], self.pos[1] - offset[1]))