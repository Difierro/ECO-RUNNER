import pygame
from pygame.locals import *
from sys import exit
import random
from scripts.entities import Player, Reciclavel, Lixo
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images, Animation
from scripts.clouds import Clouds
from scripts.database.game_DAO import GameDAO
import time


# Variável global para contagem de recicláveis (compatibilidade)
quantidade_coletada_total = 0

class Game:
    def __init__(self, usuario_dados=None):
        """
        Inicializa o jogo.
        
        Args:
            usuario_dados (dict, optional): Dados do usuário logado do banco de dados.
                Contém: id, nickname, fase1_completa, fase2_completa, fase3_completa, vidas, game_over
        """
        pygame.init()
        
        self.usuario_dados = usuario_dados
        self.user_id = None
        self.nickname = "Jogador"
        self.level=0
        self.quantidade_coletada_total = 0
        if self.usuario_dados:
            self.user_id = usuario_dados.get('id')
            self.nickname = usuario_dados.get('nickname', 'Jogador')
            print(f"Player: {self.nickname} (ID: {self.user_id})")
            if(not usuario_dados.get('fase1_completa')):
                self.level = 0
                progresso = GameDAO.carregar_progresso_fase1(self.user_id)
                if progresso:
                    self.vidas_inicial = progresso.get('vidas', 5)
                    self.itens_papel = progresso.get('itens_papel', 0)
                    self.itens_plastico = progresso.get('itens_plastico', 0)
                    self.itens_vidro = progresso.get('itens_vidro', 0)
                    self.itens_metal = progresso.get('itens_metal', 0)
                    self.quantidade_coletada_total = (self.itens_papel + self.itens_plastico +
                                                self.itens_vidro + self.itens_metal)
                    #print(f"Progresso carregado: Papel={self.itens_papel}, Plástico={self.itens_plastico}, Vidro={self.itens_vidro}, Metal={self.itens_metal}, Vidas={self.vidas_inicial}")

            else:
                self.level = 1
                
                self.vidas_inicial = 5
        else:
            print("modo offline - progresso nao sera salvo")
            self.vidas_inicial = 5
            self.itens_papel = 0
            self.itens_plastico = 0
            self.itens_vidro = 0
            self.itens_metal = 0
    
        width = 640
        heigth = 480
        pygame.display.set_caption("ECO RUNNER")
        self.screen = pygame.display.set_mode((width, heigth))
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 16)
        
        # ==================== SONS ====================
        self.music = pygame.mixer.music.load("assets/sounds/background.mp3")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.05)
        self.jump_sound = pygame.mixer.Sound('assets/sounds/jump.mp3')
        self.item_collected = pygame.mixer.Sound('assets/sounds/collect.mp3')
        self.jump_sound.set_volume(0.1)
        self.item_collected.set_volume(0.1)

        # ==================== ASSETS ====================
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'stone': load_images('tiles/stone'),
            'large_decor': load_images('tiles/large_decor'),
            'clouds': load_images('clouds'),
            'background': load_image('background/2.png'),
            'player/anda': Animation(load_images('player/guardia/anda'), img_dur=5),
            'player/parada': Animation(load_images('player/guardia/parada'), img_dur=6),
            'lixo': load_images('colisao/'),
            'reciclavel': load_images('reciclaveis/'),
            'placas': load_images('placas/'),
            'vida': load_image('vida/0.png')
        }

        # ==================== ENTIDADES ====================
        self.clouds = Clouds(self.assets['clouds'], 8)
        self.player = Player(self, (35,120), (10,16))
        self.tilemap = Tilemap(self, tile_size=16)

        # ==================== CONFIGURAÇÕES DO JOGO ====================

        self.max_level = 2
        self.tempo_imune_ativo = False
        self.tempo_imune_inicio = 0
        self.duracao_imunidade = 3000
        self.reciclaveis_por_fase = 20
        self.reciclaveis_totais = []
        self.lixos_totais = []
        
        self.depurar = False

        self.load_level(self.level)

    def draw_text_hud(self, text, pos, color=(255, 255, 255), outline_color=(0, 0, 1)):
        """Desenha texto com contorno na tela."""
        antialiasing = 0
        text_surf_outline = self.font.render(text, antialiasing, outline_color)
        text_surf_main = self.font.render(text, antialiasing, color)
        self.screen.blit(text_surf_outline, (pos[0] - 1, pos[1]))
        self.screen.blit(text_surf_outline, (pos[0] + 1, pos[1]))
        self.screen.blit(text_surf_outline, (pos[0], pos[1] - 1))
        self.screen.blit(text_surf_outline, (pos[0], pos[1] + 1))
        self.screen.blit(text_surf_main, pos)

    def show_transition_screen(self, image_path, duration=2.0):
        """Mostra tela de transição entre fases."""
        transition_img = load_image(image_path)
        transition_img = pygame.transform.scale(transition_img, self.screen.get_size())
        overlay = pygame.Surface(self.screen.get_size())
        overlay.fill((0, 0, 0))

        for alpha in range(0, 255, 8):
            overlay.set_alpha(alpha)
            self.screen.blit(transition_img, (0, 0))
            self.screen.blit(overlay, (0, 0))
            pygame.display.update()
            self.clock.tick(60)

        for alpha in range(255, -1, -8):
            overlay.set_alpha(alpha)
            self.screen.blit(transition_img, (0, 0))
            self.screen.blit(overlay, (0, 0))
            pygame.display.update()
            self.clock.tick(60)

        start_time = time.time()
        while time.time() - start_time < duration:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
            self.screen.blit(transition_img, (0, 0))
            pygame.display.update()
            self.clock.tick(60)

    def load_level(self, map_id):
        """Carrega uma fase do jogo."""
        self.tilemap.load(f'assets/maps/{map_id}.json')
        self.scroll = [0,0]
        self.player.pos = [35,120]
        self.movement = [False, False]
        self.vidas = self.vidas_inicial if hasattr(self, 'vidas_inicial') else 5
        self.tempo_imune_ativo = False
        self.tempo_imune_inicio = 0

        self.reciclaveis_totais = []
        self.lixos_totais = []
        if(map_id == 0):

            # Carrega recicláveis e lixos do mapa
            for loc in list(self.tilemap.tilemap):
                tile = self.tilemap.tilemap[loc]
                if tile['type'] == 'reciclavel':
                    pos = [tile['pos'][0]*self.tilemap.tile_size, tile['pos'][1]*self.tilemap.tile_size]
                    rec = Reciclavel(self, pos, (16,16), variant=tile['variant'])
                    rec.tile_data = tile
                    self.reciclaveis_totais.append(rec)
                    del self.tilemap.tilemap[loc]
                elif tile['type'] == 'lixo':
                    pos = [tile['pos'][0]*self.tilemap.tile_size, tile['pos'][1]*self.tilemap.tile_size]
                    img = random.choice(self.assets['lixo'])
                    lixo = Lixo(self, pos, (16,16), img)
                    self.lixos_totais.append(lixo)
                    del self.tilemap.tilemap[loc]

            # Define quais recicláveis aparecem nesta fase
            faltam = max(self.reciclaveis_por_fase - self.quantidade_coletada_total, 0)
            for rec in self.reciclaveis_totais:
                rec.tile_data['aparece'] = False
            for rec in random.sample(self.reciclaveis_totais, min(faltam, len(self.reciclaveis_totais))):
                rec.tile_data['aparece'] = True

    def coletar_item(self, tipo_item):
        """
        Atualiza contadores locais e salva no banco ao coletar item.
        
        Args:
            tipo_item (str): Tipo do item coletado ('papel', 'plastico', 'vidro', 'metal')
        """
        self.quantidade_coletada_total += 1
        
        # Atualiza contador específico do tipo
        if tipo_item == 'papel':
            self.itens_papel += 1
        elif tipo_item == 'plastico':
            self.itens_plastico += 1
        elif tipo_item == 'vidro':
            self.itens_vidro += 1
        elif tipo_item == 'metal':
            self.itens_metal += 1

    def next_level(self):
        """Avança para a próxima fase."""
        #primeiro salva a fase completa, depois muda fase
        self.salvar_progresso_fase_completa(self.level)
        self.level += 1
        if self.level < self.max_level:
            self.show_transition_screen(f'textos/level/{self.level}.png')
            self.load_level(self.level)
            

    def salvar_progresso_fase_completa(self, level):
        """Salva no banco quando completa a fase."""
        if level == 0: #salva progresso fase1
            try:
                GameDAO.salvar_progresso_fase1(self.user_id,self.itens_papel,self.itens_plastico,self.itens_vidro, self.itens_metal,self.vidas, True)
            except Exception as e:
                print(f"erro ao salvar progresso: {e}")

    def colide_lixo(self):
        """Verifica colisão com lixo e reduz vidas."""
        if self.tempo_imune_ativo and pygame.time.get_ticks() - self.tempo_imune_inicio > self.duracao_imunidade:
            self.tempo_imune_ativo = False

        player_rect = self.player.rect()
        for lixo in self.lixos_totais:
            if player_rect.colliderect(lixo.rect):
                if not self.tempo_imune_ativo:
                    self.vidas -= 1
                    self.tempo_imune_ativo = True
                    self.tempo_imune_inicio = pygame.time.get_ticks()
                    
    
                if self.vidas <= 0:
                    self.game_over()
                    break

    def game_over(self):
        """Executa lógica de game over."""
        
        self.vidas = 5
        grave_img = load_image('tiles/grave/grave.png')
        self.display.blit(self.assets['background'], (0, 0))
        self.tilemap.render(self.display, offset=(0,0))
        self.clouds.render(self.display, offset=(0,0))
        for lixo in self.lixos_totais:
            lixo.render(self.display, offset=(0,0))
        for rec in self.reciclaveis_totais:
            rec.render(self.display, offset=(0,0))
        self.display.blit(grave_img, self.player.pos)
        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
        pygame.display.update()
        pygame.time.delay(3000)
        self.show_transition_screen('textos/game_over.png', duration=1.0)

    def salvar_progresso_ao_sair(self):
        """Salva o progresso atual ao fechar o jogo."""
        if self.level == 0:
            try:
                GameDAO.salvar_progresso_fase1(
                    self.user_id,
                    itens_papel=self.itens_papel,
                    itens_plastico=self.itens_plastico,
                    itens_vidro=self.itens_vidro,
                    itens_metal=self.itens_metal,
                    vidas=self.vidas,
                    fase_completa=False
                )
            except Exception as e:
                print(f"erro ao salvar progresso: {e}")

    def run(self):
        """Loop principal do jogo."""
        pygame.mixer.music.play(loops=-1)
        while True:
            self.display.blit(self.assets['background'], (0, 0)) 
            camera_offset_y = 70
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30 
            self.scroll[1] += ((self.player.rect().centery - camera_offset_y) - self.display.get_height() / 2 - self.scroll[1]) / 30 
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, (self.movement[1]-self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            # Verifica se caiu do mapa
            if self.player.pos[1] > 1000:
                self.vidas = 5
                self.load_level(self.level)
                self.show_transition_screen('textos/game_over.png', duration = 2.0)

            # Renderiza recicláveis
            for rec in self.reciclaveis_totais:
                self.player.coleta_reciclavel(self, rec)
                rec.render(self.display, offset=render_scroll)

            # Renderiza lixos
            for lixo in self.lixos_totais:
                lixo.render(self.display, offset=render_scroll)

            # Verifica se completou a fase
            if self.quantidade_coletada_total >= self.reciclaveis_por_fase:
                self.next_level()

            # Verifica colisões
            self.player.colide_lixo(self)
            self.colide_lixo()

            # Eventos
            for event in pygame.event.get():
                if event.type == QUIT:
                    # ==================== SALVAR AO SAIR ====================
                    self.salvar_progresso_ao_sair()
                    pygame.quit()
                    exit()
                if event.type == KEYDOWN:
                    if event.key in [K_a, K_LEFT]: 
                        self.movement[0] = True
                    if event.key in [K_d, K_RIGHT]: 
                        self.movement[1] = True
                    if event.key in [K_w, K_UP]: 
                        self.player.jump()
                        self.jump_sound.play()
                    
                if event.type == KEYUP:
                    if event.key in [K_a, K_LEFT]: 
                        self.movement[0] = False
                    if event.key in [K_d, K_RIGHT]: 
                        self.movement[1] = False

            # Renderiza HUD
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            texto_hud = f"ITENS COLETADOS: {self.quantidade_coletada_total}/{self.reciclaveis_por_fase}"
            self.draw_text_hud(texto_hud, pos=(10, 10))
            
            # Renderiza vidas
            for i in range(self.vidas):
                self.screen.blit(self.assets['vida'], (10 + i*20, 30))

            # Mostra nickname e itens coletados
            if self.nickname != "Jogador":
                self.draw_text_hud(f"{self.nickname}", pos=(10, 450), color=(150, 255, 150))

            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    Game().run()