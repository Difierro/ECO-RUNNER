import pygame
import math
import random
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

        if self.velocity[0] > 0:
            self.velocity[0] = max(0, self.velocity[0] - 0.1)
        elif self.velocity[0] < 0:
            self.velocity[0] = min(0, self.velocity[0] + 0.1)
            
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
        self.shoot_cooldown = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 2

        # Se tiver animação para pular
        # if self.air_time > 4:
        #     self.set_action('pula')
        
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
        """
        Verifica colisão com lixo radioativo.
        A lógica de reduzir vida está no game.py (método colide_lixo).
        """
        tempo_atual = pygame.time.get_ticks()
        colidiu = False

        for lixo in game.lixos_totais:
            if self.rect().colliderect(lixo.rect):
                colidiu = True
                if not game.tempo_imune_ativo:
                    print("Colidiu com lixo radioativo!")
                else:
                    print("Imune...")
                    self.velocity[1] = -3
                    if self.flip: 
                        self.velocity[0] = 2 
                    else:
                        self.velocity[0] = -2

        if game.tempo_imune_ativo:
            tempo_passado = tempo_atual - game.tempo_imune_inicio
            if tempo_passado >= game.duracao_imunidade:
                print("Imunidade acabou!")
                game.tempo_imune_ativo = False

        return colidiu
    
    def coleta_reciclavel(self, game, rec):
        """
        Coleta item reciclável e salva no banco de dados.
        Agora usa game.coletar_item() que integra com GameDAO.
        """
        rec_rect = rec.rect()
        player_rect = game.player.rect()
        
        if rec.tile_data.get('aparece', True) and not rec.collected:
            if player_rect.colliderect(rec_rect):
                game.item_collected.play()
                rec.collect()
                
                tipo_item = self._get_tipo_item(rec.variant)
                game.coletar_item(tipo_item)
                
                print(f"Reciclavel {tipo_item} coletado! Total: {game.quantidade_coletada_total}/{game.reciclaveis_por_fase}")

    def _get_tipo_item(self, variant):
        """
        Mapeia o variant do reciclável para o tipo no banco de dados.
        20 itens no total: 5 de cada tipo (papel, plástico, vidro, metal).
        
        Args:
            variant (int): Índice do sprite do reciclável (0-19)
            
        Returns:
            str: Tipo do item ('papel', 'plastico', 'vidro', 'metal')
        """
        # Mapeamento completo para 20 recicláveis (5 de cada tipo)
        # ⚠️ AJUSTE conforme a ordem dos arquivos em assets/reciclaveis/
        tipos_map = {
            # Papel (5 itens)
            0: 'papel',  1: 'papel',  2: 'papel',  3: 'papel',  4: 'papel',
            # Plástico (5 itens)
            5: 'plastico',  6: 'plastico',  7: 'plastico',  8: 'plastico',  9: 'plastico',
            # Vidro (5 itens)
            10: 'vidro', 11: 'vidro', 12: 'vidro', 13: 'vidro', 14: 'vidro',
            # Metal (5 itens)
            15: 'metal', 16: 'metal', 17: 'metal', 18: 'metal', 19: 'metal',
        }
        
        tipo = tipos_map.get(variant, 'papel')
        return tipo

    def render(self, surf, offset=(0, 0)):
        """Renderiza o player com efeito de imunidade (piscar)."""
        sprite = pygame.transform.flip(self.animation.img(), self.flip, False).copy()
        
        # Efeito de piscar durante imunidade
        if self.game.tempo_imune_ativo:
            tempo_passado = pygame.time.get_ticks() - self.game.tempo_imune_inicio
            if ((tempo_passado // 150) % 2) == 0:
                sprite.set_alpha(100)
            else:
                sprite.set_alpha(255)
        else:
            sprite.set_alpha(255)
        
        sprite_pos = (
            self.pos[0] - offset[0] - 3,
            self.pos[1] - offset[1]
        )
        surf.blit(sprite, sprite_pos)
    
    def shoot(self):
        if self.game.level == 2:
            if self.shoot_cooldown == 0:
                self.shoot_cooldown = 15
                direction = -1 if self.flip else 1
                velocity = 5*direction
                projectile_pos = self.rect().center
                projectile = Projectile(self.game, projectile_pos, (6, 2), velocity)
                self.game.projectiles.append(projectile)
                self.game.shoot_sound.play()

class Reciclavel(PhysiscsEntitiy):
    def __init__(self, game, pos, size, variant=0):
        super().__init__(game, 'reciclavel', pos, size)
        self.variant = variant
        self.collected = False
        self.tile_data = {}  # Aqui armazenamos a info 'aparece'
        self.img = self.game.assets['reciclavel'][self.variant]

    def collect(self):
        """Marca o reciclável como coletado."""
        self.collected = True

    def render(self, surf, offset=(0, 0)):
        """Renderiza o reciclável apenas se deve aparecer e não foi coletado."""
        deve_aparecer = self.tile_data.get('aparece', True)
        foi_coletado = self.collected

        if deve_aparecer and not foi_coletado:
            surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))


class Lixo:
    def __init__(self, game, pos, size, img):
        self.game = game
        self.pos = pos
        self.size = size
        self.image = img
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])

    def render(self, surface, offset=(0,0)):
        """Renderiza o lixo radioativo."""
        surface.blit(self.image, (self.pos[0]-offset[0], self.pos[1]-offset[1]))

class Projectile:
    def __init__(self, game, pos, size, velocity):
        self.game = game
        self.pos = list(pos)
        self.size = size
        
        if isinstance(velocity, (int, float)):
             self.velocity = [velocity, 0]
        else:
             self.velocity = list(velocity) 
             
        self.lifetime = 300 
        self.alive = True
        
        if 'projetil' in self.game.assets:
            self.image = self.game.assets['projetil']
        else:
            self.image = pygame.Surface(size)
            self.image.fill((255, 255, 255))

        if self.velocity[0] < 0:
            self.image = pygame.transform.flip(self.image, True, False)
            
        self.is_enemy = False 

    def update(self, tilemap):
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        bullet_rect = self.rect()
        
        for rect in tilemap.physics_rects_around(self.pos):
            if bullet_rect.colliderect(rect):
                self.alive = False 
                self.game.impact_sound.play()
                break 

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.image, (self.pos[0] - offset[0], self.pos[1] - offset[1]))


class Yluh(PhysiscsEntitiy):
    def __init__(self, game, pos, size):
        super().__init__(game, 'yluh', pos, size)
        self.set_action('idle')
        self.hp = 20
        self.max_hp = 20
        self.alive = True
        self.dead = False
        self.start_y = pos[1] 
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.is_attacking = False
        self.shots_fired = 0
        self.shot_timer = 0
        self.burst_cooldown = random.randint(120, 300) 

    def update(self, tilemap):
            self.velocity[1] = 0 
            flutuacao = (math.cos(pygame.time.get_ticks() / 1500) - 1) * 45
            
            self.pos[1] = self.start_y + flutuacao
            if self.game.player.rect().centerx < self.rect().centerx:
                self.flip = False 
            else:
                self.flip = True  

            if self.is_attacking:
                if self.shot_timer > 0:
                    self.shot_timer -= 1
                else:
                    self.fire_projectile()
                    self.shots_fired += 1
                    self.shot_timer = 60
                    
                    if self.shots_fired >= 5:
                        self.is_attacking = False
                        self.shots_fired = 0
                        self.burst_cooldown = random.randint(120, 300)
            else:
                if self.burst_cooldown > 0:
                    self.burst_cooldown -= 1
                else:
                    self.is_attacking = True
                    self.shot_timer = 0

            self.animation.update()
            
            if self.hp <= 0:
                self.alive = False
                self.dead = True
                
            if self.invulnerable:
                self.invulnerable_timer -= 1
                if self.invulnerable_timer <= 0:
                    self.invulnerable = False

    def fire_projectile(self):
        start_pos = self.rect().center
        target_pos = self.game.player.rect().center
        
        diff_x = target_pos[0] - start_pos[0]
        diff_y = target_pos[1] - start_pos[1]
        dist = math.sqrt(diff_x**2 + diff_y**2)
        
        if dist > 0:
            speed = 2
            vel_x = (diff_x / dist) * speed
            vel_y = (diff_y / dist) * speed
            p = Projectile(self.game, start_pos, (8, 8), [vel_x, vel_y])
            p.image = self.game.assets['projetil_yluh']
            p.is_enemy = True 
            self.game.enemy_projectiles.append(p)
            self.game.throw_sound.play()

    def render(self, surf, offset=(0, 0)):
        if self.invulnerable and (self.invulnerable_timer // 5) % 2 == 0:
            return 
        super().render(surf, offset)
        x = self.pos[0] - offset[0]
        y = self.pos[1] - offset[1] - 10 
        pygame.draw.rect(surf, (200, 0, 0), (x, y, self.size[0], 4))
        if self.max_hp > 0:
            w = (self.hp / self.max_hp) * self.size[0]
            pygame.draw.rect(surf, (0, 200, 0), (x, y, w, 4))
    
    def take_damage(self):
        if not self.invulnerable:
            self.hp -= 1
            self.invulnerable = True
            self.invulnerable_timer = 30
            if self.hp <= 0:
                self.alive = False
                return True
        return False