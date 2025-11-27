import pygame
from pygame.locals import *
from sys import exit
import random
import os
from scripts.entities import Player, Reciclavel, Lixo
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images, Animation
from scripts.clouds import Clouds
from scripts.database.game_DAO import GameDAO
import time


# Variável global para contagem de recicláveis (compatibilidade)
quantidade_coletada_total = 0

# --- FASE 2 (SEPARAÇÃO) - INTACTA ---
class Fase2:
    def __init__(self, game, itens_coletados):
        self.game = game
        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 16)
        self.small_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 10)
        self.tiny_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 8)
        
        self.width = game.width
        self.height = game.heigth
        
        # Reinicia as vidas ao começar a fase
        self.vidas = 5
        self.game.vidas = 5
        
        self.sorted_sprites = self.load_sorted_images('reciclaveis/')

        self.type_ranges = {
            'papel':    list(range(0, 5)),
            'plastico': list(range(5, 10)),
            'vidro':    list(range(10, 15)),
            'metal':    list(range(15, 20))
        }

        self.item_names = {
            0: "Carta", 1: "Caixa", 2: "Papelão", 3: "Jornal", 4: "Folha",
            5: "Lego", 6: "Borrifador", 7: "Copo de plástico", 8: "Garrafa de amaciante", 9: "Garrafa pet",
            10: "Garrafa de vinho", 11: "Pote de vidro", 12: "Garrafa quebrada", 13: "Garrafa de cerveja", 14: "Copo de vidro",
            15: "Parafuso", 16: "Martelo", 17: "Cadeado", 18: "Chave", 19: "Lata de refrigerante"
        }

        self.inv_margin_x = 140 
        self.inv_top_y = 100
        self.inv_height = 220 

        self.inv_area_rect = pygame.Rect(
            self.inv_margin_x, 
            self.inv_top_y, 
            self.width - (self.inv_margin_x * 2), 
            self.inv_height
        )
        
        self.bins_y = self.height - 180 

        self.bins = {
            'papel':    {'img': load_image('lixeiras/lixeiras1.png'), 'type': 'papel', 'label': 'Papel'},
            'plastico': {'img': load_image('lixeiras/lixeiras3.png'), 'type': 'plastico', 'label': 'Plástico'},
            'vidro':    {'img': load_image('lixeiras/lixeiras4.png'), 'type': 'vidro', 'label': 'Vidro'},
            'metal':    {'img': load_image('lixeiras/lixeiras2.png'), 'type': 'metal', 'label': 'Metal'}
        }
        
        total_bins = len(self.bins)
        bin_w, bin_h = 70, 90
        gap_bins = 80
        total_w = (bin_w * total_bins) + (gap_bins * (total_bins - 1))
        start_x = (self.width - total_w) // 2
        
        keys_order = ['papel', 'metal', 'plastico', 'vidro']
        current_x = start_x
        
        for key in keys_order:
            b = self.bins[key]
            b['img'] = pygame.transform.scale(b['img'], (bin_w, bin_h))
            b['rect'] = pygame.Rect(current_x, self.bins_y, bin_w, bin_h)
            current_x += bin_w + gap_bins

        self.items_to_sort = []
        self.generate_items_grid(itens_coletados)
        self.selected_item = None
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        
        self.feedback_msg = "SEPARE O LIXO!"
        self.feedback_timer = 180
        self.feedback_color = (255, 255, 255)
        self.correct_sound = self.game.item_collected

    def load_sorted_images(self, path):
        base_path = 'assets/' + path
        try:
            files = sorted(os.listdir(base_path), key=lambda x: int(os.path.splitext(x)[0]) if x.split('.')[0].isdigit() else x)
            images = []
            for f in files:
                if f.endswith('.png'):
                    images.append(load_image(path + f))
            return images
        except:
            return []

    def generate_items_grid(self, itens_dict):
        temp_list = []
        ordem = ['papel', 'plastico', 'vidro', 'metal']
        
        for tipo in ordem:
            qtd = itens_dict.get(tipo, 0)
            if qtd > 0:
                indices = self.type_ranges[tipo]
                usar_sprites = []
                
                full = qtd // len(indices)
                rest = qtd % len(indices)
                
                for _ in range(full): 
                    usar_sprites.extend(indices)
                if rest > 0: 
                    usar_sprites.extend(random.sample(indices, rest))
                
                for idx in usar_sprites:
                    if idx < len(self.sorted_sprites):
                        nome = self.item_names.get(idx, f"{tipo.capitalize()}")
                        temp_list.append({'type': tipo, 'sprite_idx': idx, 'name': nome})

        random.shuffle(temp_list)

        size = 48
        pad = 15
        cols = (self.inv_area_rect.width - pad) // (size + pad)
        if cols < 1: cols = 1
        
        rows = (len(temp_list) + cols - 1) // cols
        grid_w = cols * size + (cols - 1) * pad
        grid_h = rows * size + (rows - 1) * pad
        
        start_x = self.inv_area_rect.centerx - (grid_w // 2)
        start_y = self.inv_area_rect.centery - (grid_h // 2)
        
        for i, data in enumerate(temp_list):
            r = i // cols
            c = i % cols
            x = start_x + c * (size + pad)
            y = start_y + r * (size + pad)
            
            img = pygame.transform.scale(self.sorted_sprites[data['sprite_idx']], (size, size))
            self.items_to_sort.append({
                'type': data['type'], 'img': img, 'name': data['name'],
                'rect': pygame.Rect(x, y, size, size), 'initial_pos': (x, y)
            })

    def handle_input(self):
        m_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.salvar_progresso_ao_sair()
                pygame.quit(); exit()
            
            # --- ADIÇÃO: MENU DE PAUSE NA FASE 2 ---
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.game.pause_menu()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for item in reversed(self.items_to_sort):
                        if item['rect'].collidepoint(m_pos):
                            self.selected_item = item
                            self.dragging = True
                            self.offset_x = item['rect'].x - m_pos[0]
                            self.offset_y = item['rect'].y - m_pos[1]
                            self.items_to_sort.remove(item)
                            self.items_to_sort.append(item)
                            self.feedback_msg = ""
                            break
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    self.check_drop(m_pos)
                    self.dragging = False
                    self.selected_item = None

    def update(self):
        if self.dragging and self.selected_item:
            mx, my = pygame.mouse.get_pos()
            self.selected_item['rect'].x = mx + self.offset_x
            self.selected_item['rect'].y = my + self.offset_y
        
        if not self.items_to_sort:
            self.finish_phase()

    def check_drop(self, m_pos):
        dropped = False
        for key in ['papel', 'metal', 'plastico', 'vidro']:
            b = self.bins[key]
            if b['rect'].collidepoint(m_pos):
                if self.selected_item['type'] == b['type']:
                    self.items_to_sort.remove(self.selected_item)
                    self.set_feedback("CORRETO! PONTO PARA O MEIO AMBIENTE.", (100, 255, 100))
                    self.correct_sound.play()
                    dropped = True
                    if self.game.user_id:
                        GameDAO.adicionar_item_lixeira(self.game.user_id, b['type'])
                else:
                    self.punish_player(f"ISSO NÃO É {b['label'].upper()}!")
                    dropped = True
                break
        
        if not dropped:
            self.set_feedback("JOGUE NA LIXEIRA!", (255, 255, 255))
            self.return_item_to_start()

    def punish_player(self, msg):
        self.vidas -= 1
        self.game.vidas = self.vidas
        self.set_feedback(msg, (255, 100, 100))
        self.return_item_to_start()
        if self.vidas <= 0: 
            self.vidas = 5
            self.game.vidas = 5
            self.game.game_over()

    def return_item_to_start(self):
        self.selected_item['rect'].topleft = self.selected_item['initial_pos']

    def set_feedback(self, text, color):
        self.feedback_msg = text
        self.feedback_color = color
        self.feedback_timer = 120

    def finish_phase(self):
        # Fim da fase 2: não mostra a logo, apenas passa para a fase 3
        if self.game.user_id:
            GameDAO.salvar_progresso_fase2(self.game.user_id, 5, 5, 5, 5, True)
        self.game.level = 2

    def render(self):
        self.game.display.fill((30, 30, 35))
        bg = pygame.transform.scale(self.game.assets['background'], (self.width, self.height))
        self.game.screen.blit(bg, (0,0))
        
        ov = pygame.Surface((self.width, self.height))
        ov.fill((0,0,0)); ov.set_alpha(180)
        self.game.screen.blit(ov, (0,0))

        t = self.font.render("CLASSIFICAÇÃO DE RECICLÁVEIS", True, (255, 255, 255))
        self.game.screen.blit(t, (self.width//2 - t.get_width()//2, 40))
        
        for i in range(self.vidas):
            self.game.screen.blit(self.game.assets['vida'], (40 + i*35, 35))

        pygame.draw.rect(self.game.screen, (255, 255, 255), self.inv_area_rect, 2, border_radius=15)
        l_inv = self.small_font.render("ITENS COLETADOS", True, (200, 200, 200))
        self.game.screen.blit(l_inv, (self.inv_area_rect.centerx - l_inv.get_width()//2, self.inv_area_rect.top - 25))

        mx, my = pygame.mouse.get_pos()
        for key in ['papel', 'metal', 'plastico', 'vidro']:
            b = self.bins[key]
            if b['rect'].collidepoint((mx, my)):
                glow = pygame.Surface((b['rect'].w + 20, b['rect'].h + 20), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (255, 255, 255, 40), glow.get_rect())
                self.game.screen.blit(glow, (b['rect'].x - 10, b['rect'].y - 10))

            self.game.screen.blit(b['img'], b['rect'])
            l = self.small_font.render(b['label'], True, (255, 255, 255))
            self.game.screen.blit(l, (b['rect'].centerx - l.get_width()//2, b['rect'].bottom + 10))

        hover = None
        for item in self.items_to_sort:
            self.game.screen.blit(item['img'], item['rect'])
            if not self.dragging and item['rect'].collidepoint((mx, my)):
                hover = item['name']

        if hover:
            ts = self.tiny_font.render(hover, True, (255, 255, 0))
            tr = pygame.Rect(mx + 15, my, ts.get_width() + 10, ts.get_height() + 10)
            pygame.draw.rect(self.game.screen, (20, 20, 20), tr, border_radius=5)
            pygame.draw.rect(self.game.screen, (255,255,255), tr, 1, border_radius=5)
            self.game.screen.blit(ts, (tr.x+5, tr.y+5))

        if self.feedback_timer > 0:
            fs = self.small_font.render(self.feedback_msg, True, self.feedback_color)
            fy = self.height - 40 
            self.game.screen.blit(fs, (self.width//2 - fs.get_width()//2, fy))
            self.feedback_timer -= 1

        pygame.display.update()

    def run(self):
        running = True
        while running and self.items_to_sort:
            self.handle_input()
            self.update()
            self.render()
            self.game.clock.tick(60)
            if not self.items_to_sort: running = False
        if self.vidas > 0 and not self.items_to_sort:
            self.finish_phase()


class Game:
    def __init__(self, usuario_dados=None):
        """
        Inicializa o jogo.
        """
        pygame.init()
        
        self.usuario_dados = usuario_dados
        self.user_id = None
        self.nickname = "Jogador"
        self.level = 2
        self.quantidade_coletada_total = 0
        
        self.itens_papel = 0
        self.itens_plastico = 0
        self.itens_vidro = 0
        self.itens_metal = 0

        if self.usuario_dados:
            self.user_id = usuario_dados.get('id')
            self.nickname = usuario_dados.get('nickname', 'Jogador')
            print(f"Player: {self.nickname} (ID: {self.user_id})")
            if(not usuario_dados.get('fase1_completa')):
                progresso = GameDAO.carregar_progresso_fase1(self.user_id)
                if progresso:
                    self.vidas = progresso.get('vidas', 5)
                    self.itens_papel = progresso.get('itens_papel', 0)
                    self.itens_plastico = progresso.get('itens_plastico', 0)
                    self.itens_vidro = progresso.get('itens_vidro', 0)
                    self.itens_metal = progresso.get('itens_metal', 0)
                    self.quantidade_coletada_total = (self.itens_papel + self.itens_plastico +
                                                self.itens_vidro + self.itens_metal)

            elif not usuario_dados.get('fase2_completa'): 
                self.level = 1
                self.vidas = 5
                progresso = GameDAO.carregar_progresso_fase1(self.user_id)
                if progresso:
                    self.itens_papel = progresso.get('itens_papel', 0)
                    self.itens_plastico = progresso.get('itens_plastico', 0)
                    self.itens_vidro = progresso.get('itens_vidro', 0)
                    self.itens_metal = progresso.get('itens_metal', 0)
            else: 
                self.level = 2
                self.vidas = 5
                progresso_f3 = GameDAO.carregar_progresso_fase3(self.user_id)
                if progresso_f3:
                    self.vidas = progresso_f3.get('vidas', 5)
        else:
            print("modo offline - progresso nao sera salvo")
            self.vidas = 5
            self.itens_papel = 0
            self.itens_plastico = 0
            self.itens_vidro = 0
            self.itens_metal = 0
    
        self.width = 640 * 1.5
        self.heigth = 480 * 1.5
        pygame.display.set_caption("ECO RUNNER")
        self.screen = pygame.display.set_mode((self.width, self.heigth))
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
        self.shoot_sound = pygame.mixer.Sound('assets/sounds/shoot.mp3')
        self.shoot_sound.set_volume(0.5)
        self.hit_sound = pygame.mixer.Sound('assets/sounds/hit.mp3')
        self.hit_sound.set_volume(0.1)
        self.hurt_sound = pygame.mixer.Sound('assets/sounds/hurt.mp3')
        self.hurt_sound.set_volume(0.3)
        self.impact_sound = pygame.mixer.Sound('assets/sounds/impact.mp3')
        self.impact_sound.set_volume(0.2)
        self.throw_sound = pygame.mixer.Sound('assets/sounds/throw.mp3')
        self.throw_sound.set_volume(0.3)
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
            'player/arma_anda': Animation(load_images('player/guardia_arma/anda'), img_dur=5),
            'player/arma_parada': Animation(load_images('player/guardia_arma/parada'), img_dur=6), 
            'lixo': load_images('colisao/'),
            'reciclavel': load_images('reciclaveis/'),
            'placas': load_images('placas/'),
            'vida': load_image('vida/0.png'),
            'projetil': load_image('projetil/0.png'),
            'projetil_yluh': pygame.transform.scale(load_image('projetil/1.png'), (13, 13)),
            'yluh/idle': Animation([pygame.transform.scale(img, (70, 70)) for img in load_images('yluh')], img_dur=3)
        }

        # ==================== ENTIDADES ====================
        self.clouds = Clouds(self.assets['clouds'], 8)
        self.player = Player(self, (35,120), (10,16))
        self.tilemap = Tilemap(self, tile_size=16)
        self.projectiles = []
        self.enemy_projectiles = []
        # ==================== CONFIGURAÇÕES DO JOGO ====================

        self.max_level = 3
        self.tempo_imune_ativo = False
        self.tempo_imune_inicio = 0
        self.duracao_imunidade = 3000
        self.reciclaveis_por_fase = 20
        self.reciclaveis_totais = []
        self.lixos_totais = []
        
        self.depurar = False
        
        if self.level == 0:
            self.show_transition_screen('textos/logo.png', 3)

        if self.level != 1:
            self.show_transition_screen(f'textos/level/{self.level}.png', 2)
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
        try:
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
        except:
            pass

    def load_level(self, map_id):
        self.boss = None
        """Carrega uma fase do jogo."""
        json_idx = 0 if map_id == 0 else 1
        
        self.tilemap.load(f'assets/maps/{json_idx}.json')
        self.scroll = [0,0]
        self.player.pos = [35,120]
        self.player.velocity = [0,0]
        self.movement = [False, False]
        self.vidas = self.vidas if hasattr(self, 'vidas') else 5
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
            if self.reciclaveis_totais:
                for rec in random.sample(self.reciclaveis_totais, min(faltam, len(self.reciclaveis_totais))):
                    rec.tile_data['aparece'] = True
        
        elif(map_id == 2):
            self.vidas = 5
            self.assets['player/anda'] = Animation(load_images('player/guardia_arma/anda'), img_dur=5)
            self.assets['player/parada'] = Animation(load_images('player/guardia_arma/parada'), img_dur=6)
            self.player.set_action('parada')
            from scripts.entities import Yluh
            self.boss = Yluh(self, (250, 130), (50, 60))

        
    def coletar_item(self, tipo_item):
        """
        Atualiza contadores locais e salva no banco ao coletar item.
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
            if self.level == 1:
                self.start_fase2()
            else:
                # Passagem de fase: mostra apenas o letreiro da fase
                self.show_transition_screen(f'textos/level/{self.level}.png', 2)
                self.load_level(self.level)
        else:
             self.show_transition_screen('textos/logo.png', 3)
             self.level = 0
             self.load_level(self.level)

    def start_fase2(self):
        self.show_transition_screen(f'textos/level/1.png', 2)
        
        itens_dict = {
            'papel': self.itens_papel,
            'plastico': self.itens_plastico,
            'vidro': self.itens_vidro,
            'metal': self.itens_metal
        }
        if sum(itens_dict.values()) == 0:
             itens_dict = {'papel': 5, 'plastico': 5, 'vidro': 5, 'metal': 5}
        
        fase2 = Fase2(self, itens_dict)
        fase2.run()
        
        if self.level == 2:
             self.show_transition_screen(f'textos/level/2.png', 2)
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
                    self.hurt_sound.play()
                    self.tempo_imune_inicio = pygame.time.get_ticks()
                if self.vidas <= 0:
                    self.game_over()
                    break

    def game_over(self):
        """Executa lógica de game over.""" 
        self.vidas = 5
        self.display.blit(self.assets['background'], (0, 0))
        self.tilemap.render(self.display, offset=(0,0))
        self.clouds.render(self.display, offset=(0,0))
        for lixo2 in self.lixos_totais:
            lixo2.render(self.display, offset=(0,0))
        for rec in self.reciclaveis_totais:
            rec.render(self.display, offset=(0,0))
        self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
        pygame.display.update()
        pygame.time.delay(1000)
        self.show_transition_screen('textos/game_over.png', duration=2.0)
        self.load_level(self.level)


    def salvar_progresso_ao_sair(self):
        """Salva o progresso atual ao fechar o jogo."""
        try:
            if self.level == 0:
                GameDAO.salvar_progresso_fase1(
                    self.user_id,
                    itens_papel=self.itens_papel,
                    itens_plastico=self.itens_plastico,
                    itens_vidro=self.itens_vidro,
                    itens_metal=self.itens_metal,
                    vidas=self.vidas,
                    fase_completa=False
                )
            elif self.level == 2:
                GameDAO.salvar_progresso_fase3(self.user_id, vidas=self.vidas, derrotar_yluh=False)
            print("progresso salvo")
        except Exception as e:
            print(f"erro ao salvar progresso: {e}")
    
    # === MÉTODOS DE CONTINUAR, SAIR E PAUSAR  ===

    def pause_menu(self):
        """Exibe o menu de pausa."""
        frozen_frame = self.screen.copy()

        font_big = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 28)
        font_med = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 16)
        font_small = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 12)

        panel_w, panel_h = 480, 320 
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_rect = panel_surf.get_rect(center=(self.width//2, self.heigth//2))

        def make_button(text, y_pos_absolute):
            btn_w, btn_h = 360, 38
            btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            btn_rect = btn_surf.get_rect(center=(panel_w//2, y_pos_absolute))
            return btn_surf, btn_rect

        btn_resume_surf, btn_resume_rect = make_button("CONTINUAR", 160)
        btn_quit_surf, btn_quit_rect = make_button("SAIR", 230)

        paused = True
        max_fade = 180

        def panel_point(global_pos):
            return (global_pos[0] - panel_rect.x, global_pos[1] - panel_rect.y)

        while paused:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.salvar_progresso_ao_sair()
                    pygame.quit(); exit()

                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        paused = False 

                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    px, py = panel_point((mx, my))
                    if btn_resume_rect.collidepoint((px, py)):
                        paused = False
                    elif btn_quit_rect.collidepoint((px, py)):
                        self.salvar_progresso_ao_sair()
                        pygame.quit(); exit()

            self.screen.blit(frozen_frame, (0, 0))
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((8, 12, 18, max_fade))
            self.screen.blit(overlay, (0, 0))

            shadow = pygame.Surface((panel_w+12, panel_h+12), pygame.SRCALPHA)
            shadow.fill((0,0,0,140))
            self.screen.blit(shadow, (panel_rect.x-6, panel_rect.y-6))

            panel_surf.fill((18, 26, 32, 240))

            title = font_big.render("PAUSADO", True, (240, 240, 240))
            panel_surf.blit(title, (panel_w//2 - title.get_width()//2, 20))

            nome_txt = font_med.render(f"Jogador: {self.nickname}", True, (100, 255, 100))
            panel_surf.blit(nome_txt, (panel_w//2 - nome_txt.get_width()//2, 65))

            # informações do menu
            if self.level == 1:
                info_txt = font_small.render(f"Vidas: {self.vidas}", True, (200, 200, 200))
            else: 
                info_txt = font_small.render(f"Vidas: {self.vidas}  |  Coletados: {self.quantidade_coletada_total}", True, (200, 200, 200))
            
            panel_surf.blit(info_txt, (panel_w//2 - info_txt.get_width()//2, 90))

            def draw_button(surf, rect, text, hovered=False):
                color_bg = (36, 44, 52, 200) if not hovered else (46, 154, 98, 230)
                pygame.draw.rect(surf, (0,0,0,0), rect)
                b = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                b.fill(color_bg)
                surf.blit(b, rect.topleft)
                pygame.draw.rect(surf, (255,255,255,20), rect, 1, border_radius=6)
                t = font_med.render(text, True, (255,255,255))
                surf.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))

            mx, my = pygame.mouse.get_pos()
            px, py = panel_point((mx, my))

            draw_button(panel_surf, btn_resume_rect, "CONTINUAR", btn_resume_rect.collidepoint((px, py)))
            draw_button(panel_surf, btn_quit_rect, "SAIR", btn_quit_rect.collidepoint((px, py)))

            self.screen.blit(panel_surf, panel_rect.topleft)
            pygame.display.update()
            self.clock.tick(60)

    def run(self):
        """Loop principal do jogo."""
        pygame.mixer.music.play(loops=-1)
        
        if self.level == 1:
            self.start_fase2()

        while True:
            self.display.blit(self.assets['background'], (0, 0)) 
            camera_offset_y = 70

            if self.level == 2:
                self.scroll[0] = 0
                self.scroll[1] = 0
            else:
                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30 
                self.scroll[1] += ((self.player.rect().centery - camera_offset_y) - self.display.get_height() / 2 - self.scroll[1]) / 30 
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)

            self.player.update(self.tilemap, (self.movement[1]-self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            for p in self.projectiles.copy():
                p.update(self.tilemap)
                p.render(self.display, offset = render_scroll)

                if self.level == 2 and self.boss and self.boss.alive:
                    if p.rect().colliderect(self.boss.rect()):
                        damage = self.boss.take_damage()
                        p.alive = False
                        self.hit_sound.play()

                        if not self.boss.alive:
                            GameDAO.salvar_progresso_fase3(self.user_id, self.vidas, True)

                            # MODIFICAR (ir para que tela quando terminar a terceira fase?)
                            self.show_transition_screen('textos/logo.png', 5)
                            self.boss = None
                            self.level = 0
                            self.load_level(self.level)
                            
                if not p.alive:
                    self.projectiles.remove(p)
            
            for p in self.enemy_projectiles.copy():
                p.update(self.tilemap)
                p.render(self.display, offset = render_scroll)

                if p.rect().colliderect(self.player.rect()):
                    if not self.tempo_imune_ativo:
                        self.vidas -= 1
                        self.tempo_imune_ativo = True
                        self.tempo_imune_inicio = pygame.time.get_ticks()
                        self.hurt_sound.play()
                        
                        if self.vidas <= 0:
                            self.game_over()

                    p.alive = False

                if not p.alive:
                    self.enemy_projectiles.remove(p)

            if self.level == 2 and self.boss and self.boss.alive:
                self.boss.update(self.tilemap)
                self.boss.render(self.display, offset=render_scroll)
                if self.player.rect().colliderect(self.boss.rect()):
                    if not self.tempo_imune_ativo:
                        self.vidas -= 1
                        self.tempo_imune_ativo = True
                        self.tempo_imune_inicio = pygame.time.get_ticks()
            
                        if self.boss.rect().centerx > self.player.rect().centerx:
                            self.player.velocity[0] = -4
                        else:
                            self.player.velocity[0] = 4  
                        self.player.velocity[1] = -1.5   
                        
                        if self.vidas <= 0:
                            self.game_over()

            # Verifica se caiu do mapa
            if self.player.pos[1] > 1000:
                self.game_over()

            # Renderiza recicláveis
            if self.level == 0:
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
                    # salva se sair pelo X
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
                    if event.key == K_SPACE:
                        self.player.shoot()
                    
                    # --- COMANDOS DE PAUSE ---
                    if event.key == K_ESCAPE:
                        self.pause_menu()
                    
                if event.type == KEYUP:
                    if event.key in [K_a, K_LEFT]: 
                        self.movement[0] = False
                    if event.key in [K_d, K_RIGHT]: 
                        self.movement[1] = False

            # Renderiza HUD
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            
            if self.level == 0:
                texto_hud = f"ITENS COLETADOS: {self.quantidade_coletada_total}/{self.reciclaveis_por_fase}"
                self.draw_text_hud(texto_hud, pos=(10, 10))
            elif self.level == 2:
                texto_hud = "BOSS BATTLE"
                self.draw_text_hud(texto_hud, pos=(10, 10))
            
            # Renderiza vidas
            for i in range(self.vidas):
                self.screen.blit(self.assets['vida'], (10 + i*20, 30))

            # Mostra nickname 
            self.draw_text_hud(f"{self.nickname}",pos=(25, self.heigth-40), color=(150, 255, 150))

            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    Game().run()