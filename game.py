import pygame
from pygame.locals import *
from sys import exit
import random
import os
import json    
from scripts.entities import Player, Reciclavel, Lixo
from scripts.tilemap import Tilemap
from scripts.utils import load_image, load_images, Animation
from scripts.clouds import Clouds
from scripts.database.game_DAO import GameDAO
import time
from screeninfo import get_monitors



quantidade_coletada_total = 0
monitor = get_monitors()
WIDTH = monitor[0].width
HEIGHT = monitor[0].height

SX = WIDTH / 960
SY = HEIGHT / 720
S = (SX + SY) / 2

class Fase2:
    def __init__(self, game, itens_coletados=None, saved_items=None):
        self.game = game
        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(16*S))
        self.small_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(10*S))
        self.tiny_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(8*S))
        self.feedback_font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(20*S))
        
        btn_size = int(40 * S)
        margin = int(10 * S)
        self.pause_btn_rect = pygame.Rect(WIDTH - btn_size - margin, margin, btn_size, btn_size)
        
        if saved_items is None:
            self.vidas = 5
            self.game.vidas = 5
        else:
             self.vidas = self.game.vidas 
        
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

        self.inv_margin_x = int(70*SX) 
        self.inv_top_y = int(100 * SY)
        self.inv_height = int(250*SY) 

        self.inv_area_rect = pygame.Rect(
            self.inv_margin_x, 
            self.inv_top_y, 
            WIDTH - (self.inv_margin_x * 2), 
            self.inv_height
        )
        
        self.bins_y = HEIGHT - int(180 * SY) 

        self.bins = {
            'papel':    {'img': load_image('lixeiras/lixeiras1.png'), 'type': 'papel', 'label': 'Papel'},
            'plastico': {'img': load_image('lixeiras/lixeiras3.png'), 'type': 'plastico', 'label': 'Plástico'},
            'vidro':    {'img': load_image('lixeiras/lixeiras4.png'), 'type': 'vidro', 'label': 'Vidro'},
            'metal':    {'img': load_image('lixeiras/lixeiras2.png'), 'type': 'metal', 'label': 'Metal'}
        }
        
        total_bins = len(self.bins)
        bin_w, bin_h = int(110*S), int(140*S)
        gap_bins = int(60*S)
        
        total_w = (bin_w * total_bins) + (gap_bins * (total_bins - 1))
        start_x = (WIDTH - total_w) // 2
        
        keys_order = ['papel', 'metal', 'plastico', 'vidro']
        current_x = start_x
        
        for key in keys_order:
            b = self.bins[key]
            b['img'] = pygame.transform.scale(b['img'], (bin_w, bin_h))
            b['rect'] = pygame.Rect(current_x, self.bins_y, bin_w, bin_h)
            current_x += bin_w + gap_bins

        self.items_to_sort = []
        
        if saved_items is not None:
            self.reconstruct_items_grid(saved_items)
        elif itens_coletados is not None:
            print(itens_coletados)
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
        self._place_items_on_grid(temp_list)

    def reconstruct_items_grid(self, saved_list):
        self._place_items_on_grid(saved_list)

    def _place_items_on_grid(self, item_data_list):
        size = int(68 * S)
        pad = int(12 * S)
        cols = 10 
        
        rows = (len(item_data_list) + cols - 1) // cols
        grid_w = cols * size + (cols - 1) * pad
        grid_h = rows * size + (rows - 1) * pad
        
        start_x = self.inv_area_rect.centerx - (grid_w // 2)
        start_y = self.inv_area_rect.centery - (grid_h // 2)
        
        for i, data in enumerate(item_data_list):
            r = i // cols
            c = i % cols
            x = start_x + c * (size + pad)
            y = start_y + r * (size + pad)
            
            img = pygame.transform.scale(self.sorted_sprites[data['sprite_idx']], (size, size))
            self.items_to_sort.append({
                'type': data['type'], 
                'img': img, 
                'name': data['name'],
                'sprite_idx': data['sprite_idx'],
                'rect': pygame.Rect(x, y, size, size), 
                'initial_pos': (x, y)
            })

    def handle_input(self):
        m_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.salvar_progresso_ao_sair()
                pygame.quit(); exit()
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.game.pause_menu()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.pause_btn_rect.collidepoint(m_pos):
                        self.game.pause_menu()
                        return

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
        pass

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
        if self.game.user_id:
            GameDAO.salvar_progresso_fase2(self.game.user_id, 5, 5, 5, 5, True)
        
        self.game.clear_fase2_data()
        
        self.game.level = 2

    def render(self):
        self.game.display.fill((30, 30, 35))
        bg = pygame.transform.scale(self.game.assets['background'], (WIDTH, HEIGHT))
        self.game.screen.blit(bg, (0,0))
        
        ov = pygame.Surface((WIDTH, HEIGHT))
        ov.fill((0,0,0)); ov.set_alpha(180)
        self.game.screen.blit(ov, (0,0))

        t = self.font.render("CLASSIFICAÇÃO DE RECICLÁVEIS", True, (255, 255, 255))
        self.game.screen.blit(t, (WIDTH//2 - t.get_width()//2, 40))
        
        vida_size = int(32 * S)   
        vida_img = pygame.transform.scale(self.game.assets['vida'], (vida_size, vida_size))

        for i in range(self.vidas):
            self.game.screen.blit(
                vida_img,
                (int(40*SX) + i * int(35*SX), int(35*SY))
            )
        
        self.game.draw_pause_button()

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
            self.game.screen.blit(l, (b['rect'].centerx - l.get_width()//2, b['rect'].bottom + 5))

        hover = None
        for item in self.items_to_sort:
            self.game.screen.blit(item['img'], item['rect'])
            if not self.dragging and item['rect'].collidepoint((mx, my)):
                hover = item['name']

        if hover:
            ts = self.tiny_font.render(hover, True, (255, 255, 0))
            tr = pygame.Rect(mx + int(15*SX), my, ts.get_width() + int(10*SX), ts.get_height() + int(10*SY))
            pygame.draw.rect(self.game.screen, (20, 20, 20), tr, border_radius=5)
            pygame.draw.rect(self.game.screen, (255,255,255), tr, 1, border_radius=5)
            self.game.screen.blit(ts, (tr.x+5, tr.y+5))

        if self.feedback_timer > 0:
            fs = self.feedback_font.render(self.feedback_msg, True, self.feedback_color)
            center_y_gap = (self.inv_area_rect.bottom + self.bins_y) // 2
            fy = center_y_gap - fs.get_height() // 2
            self.game.screen.blit(fs, (WIDTH//2 - fs.get_width()//2, fy))
            self.feedback_timer -= 1

        pygame.display.update()

    def run(self, game):
        running = True
        while running and self.items_to_sort:
            if self.game.level != 1:
                running = False
                break
            self.handle_input()
            self.update()
            
            if self.game.level != 1:
                break

            self.render()
            self.game.clock.tick(60)
            if not self.items_to_sort: running = False
        
        if self.vidas > 0 and not self.items_to_sort and self.game.level == 1:
            game.show_transition_screen('textos/fundos/f2f-1.png', 5)
            game.show_transition_screen('textos/fundos/f2f-2.png', 5)
            
            game.screen.fill((0, 0, 0))
            pygame.display.update()
            
            self.finish_phase()


class Game:
    def __init__(self, usuario_dados=None):
        pygame.init()
        
        self.usuario_dados = usuario_dados
        self.user_id = None
        self.nickname = "Jogador"
        self.level = 0
        self.quantidade_coletada_total = 0
        self.mostrar_historia = True 
        
        self.itens_papel = 0
        self.itens_plastico = 0
        self.itens_vidro = 0
        self.itens_metal = 0
        
        self.collected_ids = set() 
        self.fase2_instance = None 

        if self.usuario_dados:
            self.user_id = usuario_dados.get('id')
            self.nickname = usuario_dados.get('nickname', 'Jogador')
            print(f"Player: {self.nickname} (ID: {self.user_id})")
            
            self.collected_ids = self.load_collected_ids()
            
            if usuario_dados.get('fase3_completa'):
                print("Jogo já completado! Reiniciando campanha do zero...")
                GameDAO.resetar_progresso_usuario(self.user_id)
                self.reset_local_data()
                self.level = 0
                self.vidas = 5
                self.itens_papel = 0
                self.itens_plastico = 0
                self.itens_vidro = 0
                self.itens_metal = 0
                self.usuario_dados['fase1_completa'] = False
                self.usuario_dados['fase2_completa'] = False
                self.usuario_dados['fase3_completa'] = False
            
            elif(not usuario_dados.get('fase1_completa')):
                progresso = GameDAO.carregar_progresso_fase1(self.user_id)
                if progresso:
                    self.vidas = progresso.get('vidas', 5)
                    self.itens_papel = progresso.get('itens_papel', 0)
                    self.itens_plastico = progresso.get('itens_plastico', 0)
                    self.itens_vidro = progresso.get('itens_vidro', 0)
                    self.itens_metal = progresso.get('itens_metal', 0)
                    self.quantidade_coletada_total = (self.itens_papel + self.itens_plastico + self.itens_vidro + self.itens_metal)
                    
                    if self.quantidade_coletada_total > 0 or self.vidas < 5:
                        self.mostrar_historia = False

            elif not usuario_dados.get('fase2_completa'): 
                self.level = 1
                self.vidas = 5
                progresso = GameDAO.carregar_progresso_fase2(self.user_id)
                if progresso:
                    self.itens_papel = 5 - progresso.get('lixeira_papel', 0)
                    self.itens_plastico = 5 -  progresso.get('lixeira_plastico', 0)
                    self.itens_vidro = 5 -  progresso.get('lixeira_vidro', 0)
                    self.itens_metal = 5 -  progresso.get('lixeira_metal', 0)
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
    
        pygame.display.set_caption("ECO RUNNER")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN)
        self.display = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        self.movement = [False, False]
        self.font = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(16*S))
        
        btn_size = int(40 * S)
        margin = int(10 * S)
        self.pause_btn_rect = pygame.Rect(WIDTH - btn_size - margin, margin, btn_size, btn_size)

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

        self.clouds = Clouds(self.assets['clouds'], 8)
        self.player = Player(self, (35,120), (10,16))
        self.tilemap = Tilemap(self, tile_size=16)
        self.projectiles = []
        self.enemy_projectiles = []

        self.max_level = 3
        self.tempo_imune_ativo = False
        self.tempo_imune_inicio = 0
        self.duracao_imunidade = 3000
        self.reciclaveis_por_fase = 20
        self.reciclaveis_totais = []
        self.lixos_totais = []
        
        self.boss = None  
        
        self.depurar = False
        
        self.show_transition_screen('textos/fundos/logo.png', 3)
        if self.level == 0 and self.mostrar_historia:
            self.show_transition_screen('textos/fundos/PRE1.png', 3)
            self.show_transition_screen('textos/fundos/PRE2.png', 3)
            self.show_transition_screen('textos/fundos/PRE3.png', 4)
            self.show_transition_screen('textos/fundos/PRE4.png', 3)
            self.show_transition_screen('textos/fundos/PRE5.png', 3)
            pass


        if self.level != 1:
            self.show_transition_screen(f'textos/level/{self.level}.png', 2)
            self.load_level(self.level)

    def draw_text_hud(self, text, pos, color=(255, 255, 255), outline_color=(0, 0, 1)):
        antialiasing = 0
        text_surf_outline = self.font.render(text, antialiasing, outline_color)
        text_surf_main = self.font.render(text, antialiasing, color)
        self.screen.blit(text_surf_outline, (pos[0] - 1, pos[1]))
        self.screen.blit(text_surf_outline, (pos[0] + 1, pos[1]))
        self.screen.blit(text_surf_outline, (pos[0], pos[1] - 1))
        self.screen.blit(text_surf_outline, (pos[0], pos[1] + 1))
        self.screen.blit(text_surf_main, pos)

    def draw_pause_button(self):
        """Desenha o botão de pause no canto superior direito."""
        s = pygame.Surface((self.pause_btn_rect.w, self.pause_btn_rect.h), pygame.SRCALPHA)
        s.fill((0, 0, 0, 100))
        self.screen.blit(s, self.pause_btn_rect.topleft)
        
        pygame.draw.rect(self.screen, (200, 200, 200), self.pause_btn_rect, 2, border_radius=5)
        
        bar_w = int(6 * S)
        bar_h = int(20 * S)
        gap = int(6 * S)
        
        center_x = self.pause_btn_rect.centerx
        center_y = self.pause_btn_rect.centery
        
        left_bar = pygame.Rect(0, 0, bar_w, bar_h)
        left_bar.center = (center_x - gap // 2 - bar_w // 2, center_y)
        
        right_bar = pygame.Rect(0, 0, bar_w, bar_h)
        right_bar.center = (center_x + gap // 2 + bar_w // 2, center_y)
        
        pygame.draw.rect(self.screen, (255, 255, 255), left_bar)
        pygame.draw.rect(self.screen, (255, 255, 255), right_bar)

    def show_transition_screen(self, image_path, duration=2.0):
        """Mostra tela de transição entre fases."""
        try:
            transition_img = pygame.image.load('assets/' + image_path).convert()
            transition_img = pygame.transform.scale(transition_img, self.screen.get_size())
            
            overlay = pygame.Surface(self.screen.get_size())
            overlay.fill((0, 0, 0))

            for alpha in range(0, 255, 8):
                self.screen.fill((0, 0, 0)) 
                overlay.set_alpha(alpha)
                self.screen.blit(transition_img, (0, 0))
                self.screen.blit(overlay, (0, 0))
                pygame.display.update()
                self.clock.tick(60)

            for alpha in range(255, -1, -8):
                self.screen.fill((0, 0, 0)) 
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
                self.screen.fill((0, 0, 0)) 
                self.screen.blit(transition_img, (0, 0))
                pygame.display.update()
                self.clock.tick(60)
        except Exception as e:
            print(f"Erro ao mostrar tela {image_path}: {e}")
            pass

    def get_local_save_path(self):
        return "collected_items.json"
    
    def get_boss_save_path(self):
        return "boss_state.json"
    
    def get_fase2_save_path(self):
        return "fase2_state.json"

    def load_collected_ids(self):
        if not self.user_id: return set()
        path = self.get_local_save_path()
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    return set(data.get(str(self.user_id), []))
        except:
            pass
        return set()

    def save_collected_id(self, item_id):
        if not self.user_id or not item_id: return
        path = self.get_local_save_path()
        data = {}
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
        except:
            pass
        
        u_id = str(self.user_id)
        if u_id not in data:
            data[u_id] = []
        
        if item_id not in data[u_id]:
            data[u_id].append(item_id)
            
        with open(path, 'w') as f:
            json.dump(data, f)

    def save_boss_data(self, hp):
        if not self.user_id: return
        path = self.get_boss_save_path()
        data = {}
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
        except:
            pass
        
        data[str(self.user_id)] = hp
        
        with open(path, 'w') as f:
            json.dump(data, f)

    def load_boss_data(self):
        if not self.user_id: return None
        path = self.get_boss_save_path()
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    return data.get(str(self.user_id))
        except:
            pass
        return None
    
    def clear_boss_data(self):
        path = self.get_boss_save_path()
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                if str(self.user_id) in data:
                    del data[str(self.user_id)]
                    with open(path, 'w') as f:
                        json.dump(data, f)
        except:
            pass

    def save_fase2_data(self, items_list, vidas):
        if not self.user_id: return
        path = self.get_fase2_save_path()
        data = {}
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
        except:
            pass
            
        items_serializable = []
        for item in items_list:
            items_serializable.append({
                'type': item['type'],
                'sprite_idx': item['sprite_idx'],
                'name': item['name']
            })

        data[str(self.user_id)] = {
            'items': items_serializable,
            'vidas': vidas
        }
        
        with open(path, 'w') as f:
            json.dump(data, f)

    def load_fase2_data(self):
        if not self.user_id: return None
        path = self.get_fase2_save_path()
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    return data.get(str(self.user_id))
        except:
            pass
        return None

    def clear_fase2_data(self):
        path = self.get_fase2_save_path()
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                if str(self.user_id) in data:
                    del data[str(self.user_id)]
                    with open(path, 'w') as f:
                        json.dump(data, f)
        except:
            pass

    def reset_local_data(self):
        self.itens_papel = 0
        self.itens_plastico = 0
        self.itens_vidro = 0
        self.itens_metal = 0
        self.quantidade_coletada_total = 0
        self.collected_ids.clear()
        self.clear_boss_data() 
        self.clear_fase2_data()
        
        path = self.get_local_save_path()
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                
                u_id = str(self.user_id)
                if u_id in data:
                    del data[u_id] 
                
                with open(path, 'w') as f:
                    json.dump(data, f)
        except:
            pass

    def load_level(self, map_id):
        if map_id != 2:
            self.boss = None
            self.assets['player/anda'] = Animation(load_images('player/guardia/anda'), img_dur=5)
            self.assets['player/parada'] = Animation(load_images('player/guardia/parada'), img_dur=6)
            if hasattr(self, 'player'):
                self.player.action = '' 
                self.player.set_action('parada')

        json_idx = 0 if map_id == 0 else 1
        
        self.tilemap.load(f'assets/maps/{json_idx}.json')
        self.scroll = [0,0]
        self.player.pos = [35,120]
        self.player.velocity = [0,0]
        self.movement = [False, False]
        
        self.player.flip = False 
        
        self.vidas = self.vidas if hasattr(self, 'vidas') else 5
        self.tempo_imune_ativo = False
        self.tempo_imune_inicio = 0

        self.reciclaveis_totais = []
        self.lixos_totais = []
        
        self.projectiles = []
        self.enemy_projectiles = []
        
        if(map_id == 0):
            self.show_transition_screen('textos/fundos/f1-1.png', 6)
            
            for loc in list(self.tilemap.tilemap):
                tile = self.tilemap.tilemap[loc]
                if tile['type'] == 'reciclavel':
                    pos = [tile['pos'][0]*self.tilemap.tile_size, tile['pos'][1]*self.tilemap.tile_size]
                    rec = Reciclavel(self, pos, (16,16), variant=tile['variant'])
                    rec.tile_data = tile
                    
                    rec.id = f"{int(tile['pos'][0])}_{int(tile['pos'][1])}"
                    
                    if rec.id in self.collected_ids:
                        rec.tile_data['aparece'] = False
                        rec.collected = True
                    else:
                        rec.tile_data['aparece'] = True
                        
                    self.reciclaveis_totais.append(rec)
                    del self.tilemap.tilemap[loc]
                elif tile['type'] == 'lixo':
                    pos = [tile['pos'][0]*self.tilemap.tile_size, tile['pos'][1]*self.tilemap.tile_size]
                    img = random.choice(self.assets['lixo'])
                    lixo = Lixo(self, pos, (16,16), img)
                    self.lixos_totais.append(lixo)
                    del self.tilemap.tilemap[loc]
        
        elif(map_id == 2):
            saved_hp = self.load_boss_data()
            
            if saved_hp is None:
                 self.vidas = 5
            
            self.assets['player/anda'] = Animation(load_images('player/guardia_arma/anda'), img_dur=5)
            self.assets['player/parada'] = Animation(load_images('player/guardia_arma/parada'), img_dur=6)
            
            self.player.action = '' 
            self.player.set_action('parada')
            
            self.screen.fill((0, 0, 0))
            pygame.display.update()
            
            self.show_transition_screen(f'textos/fundos/f3.png', 4)
            from scripts.entities import Yluh
            self.boss = Yluh(self, (250, 130), (50, 60))
            
            if saved_hp is not None:
                self.boss.hp = saved_hp

        
    def coletar_item(self, tipo_item, item_id=None):
        self.quantidade_coletada_total += 1
        
        if item_id:
            self.save_collected_id(item_id)
            self.collected_ids.add(item_id)
        
        if tipo_item == 'papel':
            self.itens_papel += 1
        elif tipo_item == 'plastico':
            self.itens_plastico += 1
        elif tipo_item == 'vidro':
            self.itens_vidro += 1
        elif tipo_item == 'metal':
            self.itens_metal += 1

    def next_level(self):
        self.salvar_progresso_fase_completa(self.level)
        self.level += 1
        
        if self.level < self.max_level:
            if self.level == 1:
                self.start_fase2()
            else:
                self.show_transition_screen(f'textos/level/{self.level}.png', 2)
                self.load_level(self.level)
        else:
             self.show_transition_screen('textos/fundos/logo.png', 3)
             self.level = 0
             self.load_level(self.level)

    def start_fase2(self):
        self.show_transition_screen(f'textos/level/1.png', 2)
        self.show_transition_screen(f'textos/fundos/f2-1.png', 4)
        
        saved_data = self.load_fase2_data()
        
        if saved_data:
             self.vidas = saved_data['vidas'] 
             self.fase2_instance = Fase2(self, itens_coletados=None, saved_items=saved_data['items'])
        else:
             if self.user_id:
                progresso = GameDAO.carregar_progresso_fase2(self.user_id)
                if progresso:
                    qtd_papel = 5 - progresso.get('lixeira_papel', 0)
                    qtd_plastico = 5 - progresso.get('lixeira_plastico', 0)
                    qtd_vidro = 5 - progresso.get('lixeira_vidro', 0)
                    qtd_metal = 5 - progresso.get('lixeira_metal', 0)
                    
                    itens_dict = {
                        'papel': max(0, qtd_papel),
                        'plastico': max(0, qtd_plastico),
                        'vidro': max(0, qtd_vidro),
                        'metal': max(0, qtd_metal)
                    }
                else:
                    itens_dict = {'papel': 5, 'plastico': 5, 'vidro': 5, 'metal': 5}
             else:
                itens_dict = {'papel': 5, 'plastico': 5, 'vidro': 5, 'metal': 5}
        
             self.fase2_instance = Fase2(self, itens_coletados=itens_dict)
        
        self.fase2_instance.run(self)
        
        if self.level == 2 and self.boss is None:
            self.load_level(self.level)

    def salvar_progresso_fase_completa(self, level):
        if level == 0: 
            try:
                GameDAO.salvar_progresso_fase1(self.user_id,self.itens_papel,self.itens_plastico,self.itens_vidro, self.itens_metal,self.vidas, True)
            except Exception as e:
                print(f"erro ao salvar progresso: {e}")

    def colide_lixo(self):
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
        try:
            game_over_bg = pygame.image.load('assets/textos/game_over.png').convert()
            game_over_bg = pygame.transform.scale(game_over_bg, (WIDTH, HEIGHT))
        except:
            game_over_bg = pygame.Surface((WIDTH, HEIGHT))
            game_over_bg.fill((0, 0, 0))
        
        font_big = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(28*S))
        font_med = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(16*S))

        panel_w, panel_h = (500 * SX), (300 * SY)
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_rect = panel_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        start_time = time.time()
        while time.time() - start_time < 3:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.salvar_progresso_ao_sair()
                    pygame.quit(); exit()

            self.screen.blit(game_over_bg, (0, 0))
            pygame.display.update()
            self.clock.tick(60)

        start_time = time.time()
        while time.time() - start_time < 2:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.salvar_progresso_ao_sair()
                    pygame.quit(); exit()

            self.screen.blit(game_over_bg, (0, 0))
            
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100)) 
            self.screen.blit(overlay, (0, 0))

            panel_surf.fill((40, 10, 10, 230))
            pygame.draw.rect(panel_surf, (200, 50, 50), (0, 0, panel_w, panel_h), 3)

            title = font_big.render("FIM DE JOGO", True, (255, 80, 80))
            subtitle = font_med.render("TENTE NOVAMENTE", True, (255, 255, 255))
            
            panel_surf.blit(title, (panel_w//2 - title.get_width()//2, int(80*SY)))
            panel_surf.blit(subtitle, (panel_w//2 - subtitle.get_width()//2, int(160*SY)))

            self.screen.blit(panel_surf, panel_rect)
            pygame.display.update()
            self.clock.tick(60)
            
        self.vidas = 5
        if self.level == 0: 
            self.reset_local_data()
            self.show_transition_screen('textos/level/0.png', 2)
            self.load_level(0)
        elif self.level == 1: 
            self.clear_fase2_data()
            if self.user_id:
                GameDAO.salvar_progresso_fase2(self.user_id, 0, 0, 0, 0, False)
            self.start_fase2()
        elif self.level == 2:
            self.clear_boss_data() 
            self.show_transition_screen('textos/level/2.png', 2)
            self.load_level(2) 

    def victory_menu(self):
        
        try:
            final_bg = pygame.image.load('assets/textos/fundos/pos2.png').convert()
            final_bg = pygame.transform.scale(final_bg, (WIDTH, HEIGHT))
        except:
            final_bg = self.screen.copy() 
        
        font_big = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(26*S))
        font_med = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(16*S))

        panel_w, panel_h = (520 * SX), (320 * SY)
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_rect = panel_surf.get_rect(center=(WIDTH//2, HEIGHT//2))

        def make_button_rect(y_pos):
            btn_w, btn_h = int(380*SX), int(45*SY)
            return pygame.Rect(panel_w//2 - btn_w//2, y_pos, btn_w, btn_h)

        btn_again_rect = make_button_rect(int(140*SY))
        btn_quit_rect = make_button_rect(int(220*SY))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); exit()
                
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    px, py = mx - panel_rect.x, my - panel_rect.y
                    
                    if btn_again_rect.collidepoint((px, py)):
                        self.reset_local_data()
                        if self.user_id:
                            GameDAO.resetar_progresso_usuario(self.user_id)
                        
                        self.screen.fill((0, 0, 0))
                        pygame.display.update()

                        self.show_transition_screen('textos/fundos/logo.png', 3)
                        self.show_transition_screen('textos/fundos/PRE1.png', 3)
                        self.show_transition_screen('textos/fundos/PRE2.png', 3)
                        self.show_transition_screen('textos/fundos/PRE3.png', 4)
                        self.show_transition_screen('textos/fundos/PRE4.png', 3)
                        self.show_transition_screen('textos/fundos/PRE5.png', 3)
                        
                        self.level = 0
                        self.vidas = 5
                        pygame.mixer.music.play(-1)
                        
                        self.show_transition_screen('textos/level/0.png', 2)
                        
                        self.load_level(0)
                        return 
                        
                    elif btn_quit_rect.collidepoint((px, py)):
                        pygame.quit(); exit()

            self.screen.blit(final_bg, (0, 0))
            
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((20, 50, 20, 200)) 
            self.screen.blit(overlay, (0, 0))
            
            panel_surf.fill((30, 60, 30, 255))
            pygame.draw.rect(panel_surf, (100, 255, 100), (0, 0, panel_w, panel_h), 4)

            title = font_big.render("PARABÉNS!", True, (100, 255, 100))
            sub = font_med.render("VOCÊ SALVOU O MUNDO!", True, (200, 255, 200))
            
            panel_surf.blit(title, (panel_w//2 - title.get_width()//2, int(40*SY)))
            panel_surf.blit(sub, (panel_w//2 - sub.get_width()//2, int(90*SY)))

            mx, my = pygame.mouse.get_pos()
            px, py = mx - panel_rect.x, my - panel_rect.y

            def draw_btn(rect, text, hover):
                color = (50, 150, 50) if not hover else (70, 200, 70)
                pygame.draw.rect(panel_surf, color, rect, border_radius=8)
                pygame.draw.rect(panel_surf, (255, 255, 255), rect, 2, border_radius=8)
                txt = font_med.render(text, True, (255, 255, 255))
                panel_surf.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

            draw_btn(btn_again_rect, "JOGAR NOVAMENTE", btn_again_rect.collidepoint((px, py)))
            draw_btn(btn_quit_rect, "SAIR", btn_quit_rect.collidepoint((px, py)))

            self.screen.blit(panel_surf, panel_rect)
            pygame.display.update()
            self.clock.tick(60)

    def salvar_progresso_ao_sair(self):
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
            elif self.level == 1:
                 if self.fase2_instance:
                     self.save_fase2_data(self.fase2_instance.items_to_sort, self.fase2_instance.vidas)
            elif self.level == 2:
                if self.boss:
                     self.save_boss_data(self.boss.hp)
                GameDAO.salvar_progresso_fase3(self.user_id, vidas=self.vidas, derrotar_yluh=False)
            print("progresso salvo")
        except Exception as e:
            print(f"erro ao salvar progresso: {e}")
    
    def pause_menu(self):
        frozen_frame = self.screen.copy()

        font_big = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(28*S))
        font_med = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(16*S))
        font_small = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', int(12*S))

        panel_w, panel_h = (480 * SX), (320*SY) 
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_rect = panel_surf.get_rect(center=(WIDTH//2, HEIGHT//2))

        def make_button(text, y_pos_absolute):
            btn_w, btn_h = int(360*SX), int(38*SY)
            btn_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            btn_rect = btn_surf.get_rect(center=(panel_w//2, y_pos_absolute))
            return btn_surf, btn_rect

        btn_resume_surf, btn_resume_rect = make_button("CONTINUAR", int(160*SY))
        btn_quit_surf, btn_quit_rect = make_button("SAIR", int(230 * SY))

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
            panel_surf.blit(title, (panel_w//2 - title.get_width()//2, int(20*SY)))

            nome_txt = font_med.render(f"Jogador: {self.nickname}", True, (100, 255, 100))
            panel_surf.blit(nome_txt, (panel_w//2 - nome_txt.get_width()//2, int(65*SY)))

            if self.level == 0:
                info_txt = font_small.render(f"Vidas: {self.vidas}  |  Coletados: {self.quantidade_coletada_total}", True, (200, 200, 200))
            elif self.level == 1:
                sorted_count = 0
                if hasattr(self, 'fase2_instance') and self.fase2_instance:
                    sorted_count = len(self.fase2_instance.items_to_sort) 
                    current_lives = self.fase2_instance.vidas 
                else:
                    current_lives = self.vidas
                    
                info_txt = font_small.render(f"Vidas: {current_lives}  |  Faltam: {sorted_count}", True, (200, 200, 200))
            elif self.level == 2:
                info_txt = font_small.render(f"Vidas: {self.vidas}", True, (200, 200, 200))
            
            panel_surf.blit(info_txt, (panel_w//2 - info_txt.get_width()//2, int(90 * SY)))

            def draw_button(surf, rect, text, hovered=False):
                color_bg = (36, 44, 52, 200) if not hovered else (46, 154, 98, 230)
                pygame.draw.rect(surf, (0,0,0,0), rect)
                b = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                b.fill(color_bg)
                surf.blit(b, rect.topleft)
                pygame.draw.rect(surf, (255,255,255,20), rect, int(1*S), border_radius=int(6*S))
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
        pygame.mixer.music.play(loops=-1)
        
        if self.level == 1:
            self.start_fase2()

        while True:
            victory_triggered = False 
            
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
                            victory_triggered = True
                            
                if not p.alive:
                    self.projectiles.remove(p)
            
            if victory_triggered:
                GameDAO.salvar_progresso_fase3(self.user_id, self.vidas, True)
                self.clear_boss_data()
                
                self.show_transition_screen('textos/fundos/pos1.png', 5)
                self.show_transition_screen('textos/fundos/pos2.png', 5)
                self.boss = None
                
                self.victory_menu()
                
                continue

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
                            break 

                    p.alive = False

                if not p.alive:
                    if p in self.enemy_projectiles:
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

            if self.player.pos[1] > 1000:
                self.game_over()

            if self.level == 0:
                for rec in self.reciclaveis_totais:
                    self.player.coleta_reciclavel(self, rec)
                    rec.render(self.display, offset=render_scroll)

                for lixo in self.lixos_totais:
                    lixo.render(self.display, offset=render_scroll)
            
                if self.quantidade_coletada_total >= self.reciclaveis_por_fase:
                    self.show_transition_screen('textos/fundos/f1f-1.png', 5)
                    self.next_level()

            self.player.colide_lixo(self)
            self.colide_lixo()

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.salvar_progresso_ao_sair()
                    pygame.quit()
                    exit()
                if event.type == KEYDOWN:
                    if event.key in [K_a, K_LEFT]: 
                        self.movement[0] = True
                    if event.key in [K_d, K_RIGHT]: 
                        self.movement[1] = True
                    if event.key in [K_w, K_UP]: 
                        if self.player.jumps > 0: 
                            self.player.jump()
                            self.jump_sound.play()
                    if event.key == K_SPACE:
                        self.player.shoot()
                    
                    if event.key == K_ESCAPE:
                        self.pause_menu()
                    
                if event.type == KEYUP:
                    if event.key in [K_a, K_LEFT]: 
                        self.movement[0] = False
                    if event.key in [K_d, K_RIGHT]: 
                        self.movement[1] = False
                
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.pause_btn_rect.collidepoint(event.pos):
                        self.pause_menu()

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            
            if self.level == 0:
                texto_hud = f"ITENS COLETADOS: {self.quantidade_coletada_total}/{self.reciclaveis_por_fase}"
                self.draw_text_hud(texto_hud, pos=(10, 10))
            elif self.level == 2:
                texto_hud = "BOSS BATTLE"
                self.draw_text_hud(texto_hud, pos=(10, 10))
            
            vida_size = int(32 * S)   
            vida_img = pygame.transform.scale(self.assets['vida'], (vida_size, vida_size))

            for i in range(self.vidas):
                self.screen.blit(
                    vida_img,
                    (int(40*SX) + i * int(35*SX), int(35*SY))
                )
            
            self.draw_pause_button()
            self.draw_text_hud(f"{self.nickname}",pos=(25, HEIGHT-40), color=(150, 255, 150))

            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    Game().run()