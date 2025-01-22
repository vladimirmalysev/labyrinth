import pygame
import os
import sys


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


pygame.init()
size = w, h = (500, 500)
screen = pygame.display.set_mode(size)
FPS = 50
print('Введите название уровня:')
m = input()

images = {'wall': load_image('wall.png'),
          'empty': load_image('floor.png')}
hero_image = load_image('mar.png')

tile_width = tile_height = 50

# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = hero_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos = pos_x, pos_y

    def move(self, pos_x, pos_y):
        self.pos = pos_x, pos_y
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)


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
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (w, h))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


level_map = load_level(m)
max_x = len(level_map)
max_y = len(level_map[0])


def move(hero, movement):
    x, y = hero.pos
    if movement == 'up':
        if y > 0 and level_map[y - 1][x] == '.':
            hero.move(x, y - 1)
    elif movement == 'down':
        if y < max_y - 1 and level_map[y + 1][x] == '.':
            hero.move(x, y + 1)
    elif movement == 'right':
        if x < max_x - 1 and level_map[y][x + 1] == '.':
            hero.move(x + 1, y)
    elif movement == 'left':
        if x > 0 and level_map[y][x - 1] == '.':
            hero.move(x - 1, y)


start_screen()
hero, x, y = generate_level(level_map)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(hero, 'up')
            elif event.key == pygame.K_DOWN:
                move(hero, 'down')
            elif event.key == pygame.K_RIGHT:
                move(hero, 'right')
            elif event.key == pygame.K_LEFT:
                move(hero, 'left')
    screen.fill('black')
    tiles_group.draw(screen)
    player_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
terminate()
