import subprocess

import pygame
import random
import sys
import math

from main3 import Game


def init():
    global WIDTH, HEIGHT, SCREEN, clock, FPS, FONT
    global WHITE, BLACK, RED, BLUE, GREEN, YELLOW, GRAY
    global TILE_SIZE, WALL_TEXTURE, ROAD_TEXTURE, ENEMY_TEXTURE, PLAYER_TEXTURE1, PLAYER_TEXTURE2, PLAYER_TEXTURE3
    global TREASURE_TEXTURE, CHARACTERS, MAZE

    # Инициализация pygame
    pygame.init()

    # Размеры окна
    WIDTH, HEIGHT = 1050, 650
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Лабиринт")

    # Цвета
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    GRAY = (169, 169, 169)

    # Кадровая частота
    FPS = 30
    clock = pygame.time.Clock()
    TILE_SIZE = 50
    # Шрифты
    FONT = pygame.font.Font(None, 36)
    # Загрузка текстур
    WALL_TEXTURE = pygame.image.load("data/wall_texture.png")
    WALL_TEXTURE = pygame.transform.scale(WALL_TEXTURE, (TILE_SIZE, TILE_SIZE))
    ROAD_TEXTURE = pygame.image.load("data/road_texture.png")
    ROAD_TEXTURE = pygame.transform.scale(ROAD_TEXTURE, (TILE_SIZE, TILE_SIZE))
    ENEMY_TEXTURE = pygame.image.load("data/monster.png").convert_alpha()
    ENEMY_TEXTURE = pygame.transform.scale(ENEMY_TEXTURE, (40, 40))  # Масштабируем текстуру до 40x40
    PLAYER_TEXTURE1 = pygame.image.load("data/player1.png")
    PLAYER_TEXTURE1 = pygame.transform.scale(PLAYER_TEXTURE1, (40, 40))
    PLAYER_TEXTURE2 = pygame.image.load("data/player2(robin).png")
    PLAYER_TEXTURE2 = pygame.transform.scale(PLAYER_TEXTURE2, (40, 40))
    PLAYER_TEXTURE3 = pygame.image.load("data/player3(moustache).png")
    PLAYER_TEXTURE3 = pygame.transform.scale(PLAYER_TEXTURE3, (40, 40))
    TREASURE_TEXTURE = pygame.image.load("data/treasure.png").convert_alpha()
    TREASURE_TEXTURE = pygame.transform.scale(TREASURE_TEXTURE, (40, 40))

    # Спрайты персонажей
    CHARACTERS = [
        pygame.Surface((40, 40)),
        pygame.Surface((40, 40)),
        pygame.Surface((40, 40))
    ]
    CHARACTERS[0] = PLAYER_TEXTURE1
    CHARACTERS[1] = PLAYER_TEXTURE2
    CHARACTERS[2] = PLAYER_TEXTURE3

    # Лабиринт
    MAZE = [
        "WWWWWWWWWWWWWWWWWWWWW",
        "W     W       W     W",
        "W WWW WWWWW W W WWW W",
        "W W         W W W   W",
        "W W WWWWWWW WWW W WWW",
        "W W       W     W   W",
        "W WWWWW W W WWWWW W W",
        "W     W W W     W W W",
        "WWW W W WWWWW W W W W",
        "W   W W     W W   W W",
        "W WWWWWWW W W WWWWW W",
        "W         W W       W",
        "WWWWWWWWWWWWWWWWWWWWW"
    ]


# Класс игрока
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

    def __init__(self, character, x, y):
        super().__init__()
        self.image = Player.playerStand
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 5
        self.animCount = 0
        self.right = False
        self.left = False
        self.up = False
        self.down = False

    def update(self, keys, walls):
        dx, dy = 0, 0
        if keys[pygame.K_UP]:
            dy = -self.speed
            self.up = True
            self.left = self.down = self.right = False
        if keys[pygame.K_DOWN]:
            dy = self.speed
            self.down = True
            self.left = self.up = self.right = False
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.left = True
            self.up = self.down = self.right = False
        if keys[pygame.K_RIGHT]:
            dx = self.speed
            self.right = True
            self.left = self.up = self.down = False

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

        # Проверка столкновений со стенами
        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.x -= dx

        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.y -= dy


# Класс обитателя лабиринта
class Enemy(pygame.sprite.Sprite):
    def __init__(self, walls):
        super().__init__()
        self.image = ENEMY_TEXTURE  # Используем текстуру для врага
        self.rect = self.image.get_rect()
        while True:
            self.rect.topleft = (
                random.randint(0, WIDTH // TILE_SIZE - 1) * TILE_SIZE,
                random.randint(0, HEIGHT // TILE_SIZE - 1) * TILE_SIZE
            )
            if not pygame.sprite.spritecollideany(self, walls):
                break
        self.direction = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])

    def update(self, walls):
        dx, dy = self.direction[0] * 2, self.direction[1] * 2
        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.x -= dx
            self.direction = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])

        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, walls):
            self.rect.y -= dy
            self.direction = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])

        # Простая логика изменения направления
        if random.random() < 0.02:
            self.direction = random.choice([(1, 0), (0, 1), (-1, 0), (0, -1)])


# Класс сокровища
class Treasure(pygame.sprite.Sprite):
    def __init__(self, walls, player):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image = TREASURE_TEXTURE
        self.rect = self.image.get_rect()
        max_distance = 0
        best_position = None
        for _ in range(100):  # Попробуем 100 случайных мест
            x = random.randint(0, WIDTH // TILE_SIZE - 1) * TILE_SIZE + TILE_SIZE // 2
            y = random.randint(0, HEIGHT // TILE_SIZE - 1) * TILE_SIZE + TILE_SIZE // 2
            self.rect.center = (x, y)
            if not pygame.sprite.spritecollideany(self, walls):
                distance = math.sqrt((x - player.rect.x) ** 2 + (y - player.rect.y) ** 2)
                if distance > max_distance:
                    max_distance = distance
                    best_position = (x, y)
        if best_position:
            self.rect.center = best_position


# Класс стены
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = WALL_TEXTURE
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# Класс звезды
class Star(pygame.sprite.Sprite):
    def __init__(self, walls):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        while True:
            self.rect.topleft = (
                random.randint(0, WIDTH // TILE_SIZE - 1) * TILE_SIZE + TILE_SIZE // 4,
                random.randint(0, HEIGHT // TILE_SIZE - 1) * TILE_SIZE + TILE_SIZE // 4
            )
            if not pygame.sprite.spritecollideany(self, walls):
                break


# Экран окончания игры
def end_screen(stars_collected):
    while True:
        SCREEN.fill(BLACK)

        title = FONT.render("Вы выиграли!", True, WHITE)

        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Рисуем звезды
        for i in range(3):
            color = YELLOW if i < stars_collected else GRAY
            pygame.draw.circle(SCREEN, color, (WIDTH // 2 - 50 + i * 50, HEIGHT // 2), 20)

        retry_text = FONT.render("Нажмите Enter, чтобы перейти к следующему уровню", True, WHITE)
        SCREEN.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT - 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.display.quit()
                    new_game = Game()
                    new_game.run()
                    quit()


def screen(stars_collected):
    while True:
        SCREEN.fill(BLACK)

        title = FONT.render("Вы проиграли!", True, WHITE)

        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Рисуем звезды
        for i in range(3):
            color = YELLOW if i < stars_collected else GRAY
            pygame.draw.circle(SCREEN, color, (WIDTH // 2 - 50 + i * 50, HEIGHT // 2), 20)

        retry_text = FONT.render("Нажмите Enter, чтобы начать заново", True, WHITE)
        SCREEN.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT - 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game()


# Основная функция
def game():
    init()
    character = Player.image
    player = Player(character, TILE_SIZE, TILE_SIZE)
    wall_group = pygame.sprite.Group()

    # Создание стен лабиринта
    for row_index, row in enumerate(MAZE):
        for col_index, cell in enumerate(row):
            if cell == "W":
                wall = Wall(col_index * TILE_SIZE, row_index * TILE_SIZE)
                wall_group.add(wall)

    enemy = Enemy(wall_group)
    treasure = Treasure(wall_group, player)

    stars = pygame.sprite.Group()
    for _ in range(3):
        stars.add(Star(wall_group))

    player_group = pygame.sprite.Group(player)
    enemy_group = pygame.sprite.Group(enemy)
    treasure_group = pygame.sprite.Group(treasure)

    running = True
    stars_collected = 0

    while running:
        SCREEN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys, wall_group)
        enemy_group.update(wall_group)

        # Рисуем лабиринт
        for row_index, row in enumerate(MAZE):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if cell == "W":
                    SCREEN.blit(WALL_TEXTURE, (x, y))
                else:
                    SCREEN.blit(ROAD_TEXTURE, (x, y))

        player_group.draw(SCREEN)
        enemy_group.draw(SCREEN)
        treasure_group.draw(SCREEN)
        stars.draw(SCREEN)

        # Проверка столкновений
        if pygame.sprite.spritecollide(player, enemy_group, False):
            screen(stars_collected)
            running = False
        if pygame.sprite.spritecollide(player, treasure_group, True):
            end_screen(stars_collected)
            running = False

        collected_stars = pygame.sprite.spritecollide(player, stars, True)
        stars_collected += len(collected_stars)

        # Затемнение экрана за пределами круга
        shadow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 255))  # Полностью черный цвет
        pygame.draw.circle(shadow, (0, 0, 0, 0), player.rect.center, 100)
        SCREEN.blit(shadow, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
