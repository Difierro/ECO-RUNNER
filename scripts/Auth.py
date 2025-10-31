import pygame
import sys
from scripts.utils import load_image
from game import Game

pygame.init()

WIDTH, HEIGHT = 640, 480
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Eco Runner - Autenticação")

BG_COLOR = (30, 60, 30)
TEXT_COLOR = (220, 255, 220)
ERROR_COLOR = (255, 120, 120)
SUCCESS_COLOR = (120, 255, 120)
INPUT_COLOR = (50, 100, 50)
ACTIVE_COLOR = (80, 160, 80)
BUTTON_COLOR = (70, 130, 70)
BUTTON_HOVER = (90, 160, 90)
FONT = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 16)
SMALL_FONT = pygame.font.Font('assets/fonts/PressStart2P-Regular.ttf', 13)

logo = load_image('textos/logo.png')
scale = 0.12
logo = pygame.transform.smoothscale(logo, (int(logo.get_width() * scale), int(logo.get_height() * scale)))

class InputBox:
    def __init__(self, x, y, w, h, text='', password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = INPUT_COLOR
        self.text = text
        self.password = password
        self.active = False
        self.cursor_pos = len(text)
        self.offset = 0
        self.txt_surface = FONT.render(self.display_text(), True, TEXT_COLOR)
        self.cursor_visible = True
        self.cursor_timer = 0

    def display_text(self):
        return '*' * len(self.text) if self.password else self.text

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
            else:
                if len(self.text) < 64 and event.unicode.isprintable():
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += 1

            self.txt_surface = FONT.render(self.display_text(), True, TEXT_COLOR)
            self._adjust_offset()

    def _adjust_offset(self):
        cursor_x = FONT.size(self.display_text()[:self.cursor_pos])[0]
        visible_width = self.rect.w - 10
        if cursor_x - self.offset > visible_width:
            self.offset = cursor_x - visible_width
        elif cursor_x - self.offset < 0:
            self.offset = cursor_x

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer % 60 == 0:
            self.cursor_visible = not self.cursor_visible

    def draw(self, screen):
        visible_area = pygame.Rect(self.offset, 0, self.rect.w - 10, self.txt_surface.get_height())
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5), area=visible_area)

        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + FONT.size(self.display_text()[:self.cursor_pos])[0] - self.offset
            cursor_y = self.rect.y + 5
            pygame.draw.line(screen, TEXT_COLOR, (cursor_x, cursor_y), (cursor_x, cursor_y + FONT.get_height()))

        pygame.draw.rect(screen, ACTIVE_COLOR if self.active else self.color, self.rect, 2)

class Button:
    def __init__(self, text, x, y, w, h, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.callback()

    def draw(self, screen):
        color = BUTTON_HOVER if self.hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        text_surf = FONT.render(self.text, True, TEXT_COLOR)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))

class AuthScreen:
    def __init__(self, title):
        self.title = title
        self.nickname_box = InputBox(240, 180, 200, 40)
        self.password_box = InputBox(240, 240, 200, 40, password=True)
        self.input_boxes = [self.nickname_box, self.password_box]
        self.buttons = []
        self.running = True
        self.feedback = ""
        self.feedback_color = ERROR_COLOR

    def draw_common(self):
        SCREEN.fill(BG_COLOR)
        SCREEN.blit(logo, (20, 20))
        title_text = FONT.render(self.title, True, TEXT_COLOR)
        SCREEN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 120))
        SCREEN.blit(SMALL_FONT.render("Nickname:", True, TEXT_COLOR), (120, 190))
        SCREEN.blit(SMALL_FONT.render("Senha:", True, TEXT_COLOR), (120, 250))

        for box in self.input_boxes:
            box.draw(SCREEN)
        for button in self.buttons:
            button.draw(SCREEN)

        if self.feedback:
            feedback_text = SMALL_FONT.render(self.feedback, True, self.feedback_color)
            SCREEN.blit(feedback_text, (WIDTH // 2 - feedback_text.get_width() // 2, 420))

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for box in self.input_boxes:
                box.handle_event(event)
            for button in self.buttons:
                button.handle_event(event)

    def update(self):
        for box in self.input_boxes:
            box.update()

    def set_feedback(self, text, success=False):
        self.feedback = text
        self.feedback_color = SUCCESS_COLOR if success else ERROR_COLOR


class LoginScreen(AuthScreen):
    usuarios_mock = {"eco_tester": "12345678"}  # simulação local

    def __init__(self):
        super().__init__("Login")
        self.buttons = [
            Button("Entrar", 220, 310, 200, 40, self.login_action),
            Button("Cadastrar", 220, 360, 200, 40, self.open_register)
        ]

    def verificar_login(self, nickname, senha):
        # verificação para quando tiver o banco
        return nickname in self.usuarios_mock and self.usuarios_mock[nickname] == senha

    def login_action(self):
        nickname = self.nickname_box.text.strip()
        senha = self.password_box.text.strip()

        if not nickname or not senha:
            self.set_feedback("Preencha todos os campos.")
            return

        if self.verificar_login(nickname, senha):
            self.set_feedback("Login realizado com sucesso!", success=True)
            pygame.time.wait(1000)
            Game().run()
        else:
            self.set_feedback("Usuário ou senha inválidos.")

    def open_register(self):
        RegisterScreen().main()

    def main(self):
        clock = pygame.time.Clock()
        while self.running:
            self.event_loop()
            self.update()
            self.draw_common()
            pygame.display.flip()
            clock.tick(30)


class RegisterScreen(AuthScreen):
    usuarios_mock = {"eco_tester": "12345678"}  # simulação local

    def __init__(self):
        super().__init__("Cadastro")
        self.buttons = [
            Button("Cadastrar", 220, 310, 200, 40, self.cadastrar_action),
            Button("Voltar", 220, 360, 200, 40, self.voltar)
        ]

    def registrar_usuario(self, nickname, senha):
        # insert quando tiver o banco
        self.usuarios_mock[nickname] = senha

    def cadastrar_action(self):
        nickname = self.nickname_box.text.strip()
        senha = self.password_box.text.strip()

        if len(nickname) < 3 or len(nickname) > 12:
            self.set_feedback("Nickname deve ter 3 a 12 caracteres.")
            return
        if len(senha) < 8 or len(senha) > 64:
            self.set_feedback("Senha deve ter 8 a 64 caracteres.")
            return
        if nickname in self.usuarios_mock:
            self.set_feedback("Nome de usuário já existe.")
            return

        self.registrar_usuario(nickname, senha)
        self.set_feedback("Usuário cadastrado com sucesso!", success=True)
        pygame.time.wait(1000)
        self.voltar()

    def voltar(self):
        LoginScreen().main()

    def main(self):
        clock = pygame.time.Clock()
        while self.running:
            self.event_loop()
            self.update()
            self.draw_common()
            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    LoginScreen().main()
