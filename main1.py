import pygame
import os
import gif_pygame

import sys

import sqlite3
import bcrypt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLineEdit, QDialog, QFormLayout, QMessageBox, QLabel
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

from main2 import game

DB_NAME = "task_manager.db"


# Создание базы данных (если нет)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()


# Хэширование пароля
def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


# Проверка пароля
def check_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)


# Регистрация пользователя
def register_user(username, password):
    hashed_password = hash_password(password)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


# Аутентификация пользователя
def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password(user[0], password):
        return True
    return False


# Окно авторизации
class AuthDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setModal(True)
        self.setFixedSize(300, 200)

        layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Логин:", self.username_input)
        layout.addRow("Пароль:", self.password_input)

        self.login_btn = QPushButton("Войти")
        self.register_btn = QPushButton("Регистрация")
        layout.addRow(self.login_btn, self.register_btn)

        self.setLayout(layout)
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.register)
        self.authenticated = False

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if len(username) < 3 or len(password) < 8:
            QMessageBox.warning(self, "Ошибка", "Логин должен быть > 3 символов, пароль > 8.")
            return

        if register_user(username, password):
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован!")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь уже существует!")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if authenticate_user(username, password):
            self.authenticated = True
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")


# Стартовое окно с кнопкой "Начать игру"
class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Снежный лабиринт")
        self.setFixedSize(800, 600)

        # Устанавливаем фоновое изображение
        self.background = QLabel(self)
        self.background.setPixmap(
            QPixmap("data/start_screen.png").scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatioByExpanding))
        self.background.setGeometry(0, 0, 800, 600)

        # Кнопка "Начать игру"
        self.start_btn = QPushButton("Начать игру", self)
        self.start_btn.setGeometry(300, 500, 200, 60)
        self.start_btn.setFont(QFont("dark ages", 18))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffA500;
                color: #00008B;
                border-radius: 20px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
            QPushButton:pressed {
                background-color: #FF8C00;
            }
        """)
        self.start_btn.clicked.connect(self.start_game)

    def start_game(self):
        self.close()
        game1()
        return


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as mes:
        print(f'Не могу загрузить файл: {name}')
        print(mes)
        return
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x = obj.pos[0] + self.dx
        obj.rect.y = obj.pos[1] + self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = 0
        self.dy = 0


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = self.rect.x, self.rect.y


class Player(pygame.sprite.Sprite):
    walkRight = [pygame.image.load('sprites/right1.png'), pygame.image.load('sprites/right2.png'),
                 pygame.image.load('sprites/right3.png'), pygame.image.load('sprites/right4.png')]

    walkLeft = [pygame.image.load('sprites/left1.png'), pygame.image.load('sprites/left2.png'),
                pygame.image.load('sprites/left3.png'), pygame.image.load('sprites/left4.png')]

    walkUp = [pygame.image.load('sprites/up1.png'), pygame.image.load('sprites/up2.png'),
              pygame.image.load('sprites/up3.png'), pygame.image.load('sprites/up4.png')]

    walkDown = [pygame.image.load('sprites/down1.png'), pygame.image.load('sprites/down2.png'),
                pygame.image.load('sprites/down3.png'), pygame.image.load('sprites/down4.png')]

    playerStand = pygame.image.load('sprites/down1.png')

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = Player.playerStand
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = pos_x, pos_y
        self.animCount = 0
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.hurts = 30
        self.heart = pygame.transform.scale(pygame.image.load('data/heart.png'), (30, 30))

    def move(self, pos_x, pos_y):
        camera.dx -= tile_width * (pos_x - self.pos[0])
        camera.dy -= tile_height * (pos_y - self.pos[1])
        self.pos = pos_x, pos_y
        for sprite in tiles_group:
            camera.apply(sprite)

    def check_win(self):
        if pygame.sprite.spritecollide(self, win_group, False):
            return True
        return False

    def check_hurts(self):
        if self.pos == (9, 3) or self.pos == (6, 7) or self.pos == (8, 9):
            self.hurts -= 1
        return self.hurts

    def draw_hearts(self):
        for i in range(self.hurts // 10):
            screen.blit(self.heart, (i * self.heart.width + 5, 0))

    def update(self):
        self.animCount += 1
        if self.animCount >= 30:
            self.animCount = 0

        if self.animCount <= 25:
            if self.left:
                self.image = Player.walkLeft[self.animCount % 4]
            elif self.right:
                self.image = Player.walkRight[self.animCount % 4]
            elif self.up:
                self.image = Player.walkUp[self.animCount % 4]
            elif self.down:
                self.image = Player.walkDown[self.animCount % 4]
        else:
            self.image = self.playerStand
            self.right = False
            self.left = False
            self.up = False
            self.down = False


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'p':
                Tile('putes', x, y)
            elif level[y][x] == 'b':
                Tile('bochkes', x, y)
            elif level[y][x] == 'd':
                Tile('dereves', x, y)
            elif level[y][x] == 'l':
                Tile('lujes', x, y)
            elif level[y][x] == 'v':
                Tile('pugales', x, y)
            elif level[y][x] == 's':
                Tile('senes', x, y)
            elif level[y][x] == 't':
                Tile('traves', x, y)
            elif level[y][x] == 'z':
                Tile('zabores', x, y)
            elif level[y][x] == 'w':
                h = Tile('home', x, y)
                win_group.add(h)
            elif level[y][x] == '@':
                Tile('putes', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'h':
                Tile('shipes', x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen1():
    intro_text = ["ПОЗДРАВЛЯЕМ!", "",
                  "Вы прошли первый уровень",
                  "Чтобы перейти к следующему",
                  "нажмите на любую кнопку"]
    screen.fill('white')
    gif = gif_pygame.load("data/animation.gif", 100)
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        gif.render(screen, (128 - gif.get_width() * 0.3, 256 - gif.get_height() * 0.5))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # subprocess.run(['python', 'main2.py'])
                game()
                quit()
        pygame.display.flip()
        clock.tick(FPS)


def finish_screen():
    intro_text = ["К сожалению, вы проиграли", "",
                  "Чтобы начать заново, нажмите enter"]
    screen.fill('white')
    font = pygame.font.Font(None, 30)
    text_coord = 10
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game1()


level_map = load_level('map1.map')
max_x = len(level_map[0])
max_y = len(level_map)


def move(hero, movement):
    x, y = hero.pos
    if movement == 'up':
        if y > 0 and level_map[y - 1][x] in 'p@wh':
            hero.move(x, y - 1)
    elif movement == 'down':
        if y < max_y - 1 and level_map[y + 1][x] in 'p@h':
            hero.move(x, y + 1)
    elif movement == 'right':
        if x < max_x - 1 and level_map[y][x + 1] in 'p@h':
            hero.move(x + 1, y)
    elif movement == 'left':
        if x > 0 and level_map[y][x - 1] in 'ph':
            hero.move(x - 1, y)


def game1():
    global camera, fon, hero, tile_width, tile_height, tiles_group, screen, all_sprites, images, player_group
    global win_group, FPS
    pygame.init()
    size = w, h = (400, 400)
    screen = pygame.display.set_mode(size)
    FPS = 20

    images = {'bochkes': load_image('bochkes.png'),
              'dereves': load_image('dereves.png'),
              'lujes': load_image('lujes.png'),
              'pugales': load_image('pugales.png'),
              'putes': load_image('putes.png'),
              'senes': load_image('senes.png'),
              'traves': load_image('traves.png'),
              'zabores': load_image('zabores.png'),
              'home': load_image('home.png'),
              'shipes': load_image('shipes.png')}

    def draw():
        screen.blit(fon, (0, 0))

        tiles_group.draw(screen)
        hero.update()
        player_group.draw(screen)
        hero.draw_hearts()

        pygame.display.flip()

    tile_width = tile_height = 50

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    win_group = pygame.sprite.Group()
    hero, x, y = generate_level(level_map)
    camera = Camera()
    camera.update(hero)
    running = True
    fon = pygame.transform.scale(load_image('fon1.png'), (w, h))
    screen.blit(fon, (0, 0))
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move(hero, 'up')
                    hero.up = True
                    hero.down = hero.right = hero.left = False
                elif event.key == pygame.K_DOWN:
                    move(hero, 'down')
                    hero.down = True
                    hero.up = hero.left = hero.right = False
                elif event.key == pygame.K_RIGHT:
                    move(hero, 'right')
                    hero.right = True
                    hero.left = hero.up = hero.down = False
                elif event.key == pygame.K_LEFT:
                    move(hero, 'left')
                    hero.left = True
                    hero.right = hero.up = hero.down = False
                else:
                    hero.up = hero.down = hero.right = hero.left = False
                    hero.animCount = 0
        if hero.check_win():
            start_screen1()
            break
        if hero.check_hurts() // 10 == 0:
            finish_screen()
        draw()


init_db()
app = QApplication(sys.argv)
auth = AuthDialog()
if auth.exec() == QDialog.DialogCode.Accepted:
    start_window = StartWindow()
    start_window.show()
    sys.exit(app.exec())
