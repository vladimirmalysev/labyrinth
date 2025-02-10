import pygame
import sys
from collections import deque
import random

FPS = 30

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SNOW_WHITE = (240, 240, 240)
SNOW_WALL = (200, 220, 255)
PIPES_IMAGE = pygame.image.load("data/pipes.png")

# Размер лабиринта
MAZE_WIDTH = 39
MAZE_HEIGHT = 19

# Фиксируем генерацию лабиринта
random.seed(42)


def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]
    start_x, start_y = 1, 1
    maze[start_y][start_x] = 0
    walls = [(start_x + dx, start_y + dy) for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)] if
             0 <= start_x + dx < width and 0 <= start_y + dy < height]
    random.shuffle(walls)

    while walls:
        x, y = walls.pop()
        if maze[y][x] == 1:
            open_neighbors = [(x + dx * 2, y + dy * 2) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)] if
                              0 <= x + dx * 2 < width and 0 <= y + dy * 2 < height]
            random.shuffle(open_neighbors)

            for nx, ny in open_neighbors:
                if maze[ny][nx] == 0:
                    maze[y][x] = 0
                    maze[(y + ny) // 2][(x + nx) // 2] = 0
                    walls.extend([(x + dx, y + dy) for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)] if
                                  0 <= x + dx < width and 0 <= y + dy < height])
                    break

    for _ in range(int(width * height * 0.1)):  # Дополнительно добавляем проходы
        x, y = random.randint(1, width - 2), random.randint(1, height - 2)
        if maze[y][x] == 1:
            maze[y][x] = 0

    for x in range(width):
        maze[0][x] = 1
        maze[height - 1][x] = 1
    for y in range(height):
        maze[y][0] = 1
        maze[y][width - 1] = 1

    # Добавляем выход в правом нижнем углу
    maze[height - 2][width - 2] = 2  # 2 — это значение выхода
    return maze


maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)


class Hero:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move_delay = 10  # Задержка движения героя
        self.frame_counter = 0

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and (
                maze[new_y][new_x] == 0 or maze[new_y][new_x] == 2):
            self.x, self.y = new_x, new_y


class Monster:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.move_delay = 20
        self.frame_counter = 0

    def move(self, hero):
        self.frame_counter += 1
        if self.frame_counter >= self.move_delay:
            self.frame_counter = 0
            path = self.bfs((self.x, self.y), (hero.x, hero.y))
            if path:
                self.x, self.y = path[0]

    def bfs(self, start, goal):
        queue = deque([start])
        visited = {start: None}

        while queue:
            current = queue.popleft()
            if current == goal:
                break

            x, y = current
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            for neighbor in neighbors:
                nx, ny = neighbor
                if MAZE_WIDTH > nx >= 0 == maze[ny][nx] and 0 <= ny < MAZE_HEIGHT and neighbor not in visited:
                    queue.append(neighbor)
                    visited[neighbor] = current

        path = []
        current = goal
        while current != start:
            if current not in visited:
                return []
            path.append(current)
            current = visited[current]
        path.reverse()
        return path


class Game:
    walkRight = [pygame.image.load('sprites/right1.png'), pygame.image.load('sprites/right2.png'),
                 pygame.image.load('sprites/right3.png'), pygame.image.load('sprites/right4.png')]
    for i in range(4):
        walkRight[i] = pygame.transform.smoothscale(walkRight[i], (100, 100))

    walkLeft = [pygame.image.load('sprites/left1.png'), pygame.image.load('sprites/left2.png'),
                pygame.image.load('sprites/left3.png'), pygame.image.load('sprites/left4.png')]
    for i in range(4):
        walkLeft[i] = pygame.transform.smoothscale(walkLeft[i], (100, 100))

    walkUp = [pygame.image.load('sprites/up1.png'), pygame.image.load('sprites/up2.png'),
              pygame.image.load('sprites/up3.png'), pygame.image.load('sprites/up4.png')]
    for i in range(4):
        walkUp[i] = pygame.transform.smoothscale(walkUp[i], (100, 100))

    walkDown = [pygame.image.load('sprites/down1.png'), pygame.image.load('sprites/down2.png'),
                pygame.image.load('sprites/down3.png'), pygame.image.load('sprites/down4.png')]
    for i in range(4):
        walkDown[i] = pygame.transform.smoothscale(walkDown[i], (100, 100))

    playerStand = pygame.image.load('sprites/down1.png')
    playerStand = pygame.transform.smoothscale(playerStand, (100, 100))

    def __init__(self):
        pygame.init()
        infoobject = pygame.display.Info()
        self.WIDTH, self.HEIGHT = infoobject.current_w, infoobject.current_h
        print(self.WIDTH, self.HEIGHT)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Снежный лабиринт")
        self.CELL_SIZE = min(self.WIDTH // (MAZE_WIDTH // 3), self.HEIGHT // (MAZE_HEIGHT // 3))
        print(self.CELL_SIZE)
        self.clock = pygame.time.Clock()
        self.hero = Hero(1, 1)
        self.monster = Monster(MAZE_WIDTH - 2, MAZE_HEIGHT - 2)

        self.wall_texture = pygame.image.load("data/wall.png")
        self.wall_texture = pygame.transform.smoothscale(self.wall_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.floor_texture = pygame.image.load("data/floor.png")
        self.floor_texture = pygame.transform.smoothscale(self.floor_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.image = self.playerStand
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.monster_texture = pygame.image.load("data/monster.webp").convert_alpha()
        self.monster_texture = pygame.transform.smoothscale(self.monster_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.ice_pick_texture = pygame.image.load("data/ice_pick.webp").convert_alpha()
        self.ice_pick_texture = pygame.transform.smoothscale(self.ice_pick_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.decoration = pygame.image.load("data/exit.webp").convert_alpha()
        self.decoration = pygame.transform.smoothscale(self.decoration, (self.CELL_SIZE, self.CELL_SIZE))
        self.snowstorm = self.create_snowstorm(500)
        self.visibility_radius = self.CELL_SIZE * 2
        self.camera_x = 1
        self.camera_y = 1
        self.ice_pick = None
        self.has_ice_pick = False
        self.ice_pick_pos = None
        self.spawn_ice_pick()
        self.animCount = 0
        self.right = False
        self.left = False
        self.up = False
        self.down = False

    def spawn_ice_pick(self):
        # Генерируем случайную позицию для ледоруба на поле (не на стенке)
        if not self.ice_pick_pos:
            while True:
                xx = random.randint(1, MAZE_WIDTH)
                yy = random.randint(1, MAZE_HEIGHT)
                if maze[yy][xx] == 0:
                    self.ice_pick_pos = xx, yy
                    break

    def draw_ice_pick(self):
        if self.ice_pick_pos:
            ice_pick_screen_x = (self.ice_pick_pos[0] - self.camera_x) * self.CELL_SIZE + self.WIDTH // 2
            ice_pick_screen_y = (self.ice_pick_pos[1] - self.camera_y) * self.CELL_SIZE + self.HEIGHT // 2
            self.screen.blit(self.ice_pick_texture, (ice_pick_screen_x, ice_pick_screen_y))

    def use_ice_pick(self):
        # Если игрок использует ледоруб и находится рядом со стеной
        if self.has_ice_pick:
            hero_x, hero_y = self.hero.x, self.hero.y
            # Проверяем соседние клетки
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = hero_x + dx, hero_y + dy
                if 0 <= new_x < MAZE_WIDTH and 0 <= new_y < MAZE_HEIGHT and maze[new_y][new_x] == 1:
                    maze[new_y][new_x] = 0  # Пробиваем стену
                    self.has_ice_pick = False  # Убираем ледоруб
                    return  # Ледоруб использован, выходим

    def draw_ui(self):
        # Отображаем ледоруб в левом нижнем углу
        if self.has_ice_pick:
            ice_pick_rect = self.ice_pick_texture.get_rect(topleft=(20, self.HEIGHT - 180))
            self.screen.blit(self.ice_pick_texture, ice_pick_rect)

    def draw_maze(self, camera_x, camera_y):
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                screen_x = (x - camera_x) * self.CELL_SIZE + self.WIDTH // 2
                screen_y = (y - camera_y) * self.CELL_SIZE + self.HEIGHT // 2
                if 0 <= screen_x < self.WIDTH and 0 <= screen_y < self.HEIGHT:
                    if cell == 1:
                        self.screen.blit(self.wall_texture, (screen_x, screen_y))
                    elif cell == 2:  # Отрисовка выхода
                        self.screen.blit(self.decoration, (screen_x, screen_y))
                    else:
                        self.screen.blit(self.floor_texture, (screen_x, screen_y))

    def create_snowstorm(self, count):
        snowflakes = []
        for _ in range(count):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            size = random.randint(2, 6)  # Размер снежинки
            speed_x = random.uniform(-2, 2)  # Горизонтальное движение
            speed_y = random.uniform(1, 5)  # Вертикальное падение
            opacity = random.randint(150, 255)  # Прозрачность (чтобы снежинки накладывались)
            snowflakes.append([x, y, size, speed_x, speed_y, opacity])
        return snowflakes

    def update_snowstorm(self):
        for flake in self.snowstorm:
            flake[0] += flake[3]  # Двигаем по X
            flake[1] += flake[4]  # Двигаем по Y

            # Если снежинка вышла за экран — вернуть наверх
            if flake[1] > self.HEIGHT or flake[0] < 0 or flake[0] > self.WIDTH:
                flake[0] = random.randint(0, self.WIDTH)
                flake[1] = random.randint(-50, -10)  # Начинает падать с верху
                flake[3] = random.uniform(-2, 2)  # Новый случайный горизонтальный сдвиг
                flake[4] = random.uniform(1, 5)  # Новая скорость падения

    def draw_snowstorm(self):
        snowstorm_layer = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)

        for flake in self.snowstorm:
            x, y, size, _, _, opacity = flake

            # Проверяем, находится ли снежинка в центре экрана (где герой)
            dx = x - self.WIDTH // 2
            dy = y - self.HEIGHT // 2
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance < 100:  # В центре (радиус 100px) делаем снежинки более прозрачными
                opacity = max(50, opacity - 150)

            pygame.draw.circle(snowstorm_layer, (255, 255, 255, opacity), (int(x), int(y)), size)

        self.screen.blit(snowstorm_layer, (0, 0))  # Отрисовываем поверх лабиринта

    def draw_visibility_mask(self):
        mask = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 180))
        hero_screen_x = self.WIDTH // 2
        hero_screen_y = self.HEIGHT // 2
        pygame.draw.circle(mask, (0, 0, 0, 0), (hero_screen_x, hero_screen_y), self.visibility_radius)
        self.screen.blit(mask, (0, 0))

    def update_camera(self):
        return self.hero.x, self.hero.y

    def handle_events(self):
        pygame.event.pump()
        keys = pygame.key.get_pressed()

        self.hero.frame_counter += 1
        if self.hero.frame_counter >= self.hero.move_delay:
            if keys[pygame.K_w]:
                self.hero.move(0, -1)
                self.up = True
                self.left = self.down = self.right = False
            if keys[pygame.K_s]:
                self.hero.move(0, 1)
                self.down = True
                self.left = self.up = self.right = False
            if keys[pygame.K_a]:
                self.hero.move(-1, 0)
                self.left = True
                self.up = self.down = self.right = False
            if keys[pygame.K_d]:
                self.hero.move(1, 0)
                self.right = True
                self.left = self.up = self.down = False
            self.hero.frame_counter = 0

            self.animCount += 1
            if self.animCount >= 30:
                self.animCount = 0

            if self.animCount <= 25:
                if self.left:
                    self.image = self.walkLeft[self.animCount % 4]
                elif self.right:
                    self.image = self.walkRight[self.animCount % 4]
                elif self.up:
                    self.image = self.walkUp[self.animCount % 4]
                elif self.down:
                    self.image = self.walkDown[self.animCount % 4]
            else:
                self.image = self.playerStand
                self.right = False
                self.left = False
                self.up = False
                self.down = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if (self.hero.x, self.hero.y) == self.ice_pick_pos:
                    self.has_ice_pick = True
                    self.ice_pick_pos = None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.use_ice_pick()
        return True

    def draw_lighting_effect(self):
        dark_surface = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        dark_surface.fill((0, 0, 0, 150))  # Затемнение

        # Создаем плавно исчезающий круг света вокруг героя
        hero_pos = (self.WIDTH // 2, self.HEIGHT // 2)
        pygame.draw.circle(dark_surface, (0, 0, 0, 0), hero_pos, self.visibility_radius * 1.2)

        self.screen.blit(dark_surface, (0, 0))

    def end_screen(self):
        FONT = pygame.font.Font(None, 36)
        while True:
            self.screen.fill((0, 0, 0))

            title = FONT.render("Вы пойманы монстром!", True, WHITE)

            self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 50))

            retry_text = FONT.render("Нажмите Enter, чтобы начать заново", True, WHITE)
            self.screen.blit(retry_text, (self.WIDTH // 2 - retry_text.get_width() // 2, self.HEIGHT - 300))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game = Game()
                        game.run()

    def final_screen(self):
        FONT = pygame.font.Font(None, 36)
        WIDTH, HEIGHT = 1050, 650
        SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Победа")
        SCREEN.fill((0, 0, 0))
        image = PIPES_IMAGE
        text = FONT.render("Победа!", True, WHITE)
        sub_text = FONT.render("Вы доказали свою силу!", True, WHITE)

        image = pygame.transform.scale(image, (300, 300))
        SCREEN.blit(image, (WIDTH // 2 - 150, HEIGHT // 2 - 150))
        SCREEN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))
        SCREEN.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    pygame.quit()
                    sys.exit()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.monster.move(self.hero)
            self.camera_x, self.camera_y = self.update_camera()

            self.screen.fill(SNOW_WHITE)
            self.draw_maze(self.camera_x, self.camera_y)
            self.draw_visibility_mask()
            self.draw_lighting_effect()

            # Отрисовка героя
            hero_screen_x = self.WIDTH // 2
            hero_screen_y = self.HEIGHT // 2
            self.screen.blit(self.image, (hero_screen_x, hero_screen_y))

            # Отрисовка монстра
            monster_screen_x = (self.monster.x - self.camera_x) * self.CELL_SIZE + self.WIDTH // 2
            monster_screen_y = (self.monster.y - self.camera_y) * self.CELL_SIZE + self.HEIGHT // 2
            self.screen.blit(self.monster_texture, (monster_screen_x, monster_screen_y))
            self.draw_ui()
            self.draw_ice_pick()

            self.update_snowstorm()
            self.draw_snowstorm()

            pygame.display.flip()
            self.clock.tick(FPS)
            if maze[self.hero.y][self.hero.x] == 2:
                Game.final_screen(self)
                running = False

            if self.hero.x == self.monster.x and self.hero.y == self.monster.y:
                Game.end_screen(self)
                running = False

        pygame.quit()
        sys.exit()


# Запуск программы
if __name__ == "__main__":
    game = Game()
    game.run()
