import pygame
import sys
from collections import deque
import random
import sqlite3
import bcrypt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLineEdit, QDialog, QFormLayout, QMessageBox, QLabel
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

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
        self.background.setPixmap(QPixmap("start_screen.png").scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatioByExpanding))
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
        game = Game()
        game.run()


FPS = 60

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SNOW_WHITE = (240, 240, 240)
SNOW_WALL = (200, 220, 255)

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
                if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and maze[ny][nx] == 0 and neighbor not in visited:
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
    def __init__(self):
        pygame.init()
        infoobject = pygame.display.Info()
        self.WIDTH, self.HEIGHT = infoobject.current_w, infoobject.current_h
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Снежный лабиринт")
        self.CELL_SIZE = min(self.WIDTH // (MAZE_WIDTH // 3), self.HEIGHT // (MAZE_HEIGHT // 3))
        self.clock = pygame.time.Clock()
        self.hero = Hero(1, 1)
        self.monster = Monster(MAZE_WIDTH - 2, MAZE_HEIGHT - 2)

        self.wall_texture = pygame.image.load("wall.png")
        self.wall_texture = pygame.transform.smoothscale(self.wall_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.floor_texture = pygame.image.load("floor.png")
        self.floor_texture = pygame.transform.smoothscale(self.floor_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.hero_texture = pygame.image.load("vadim.png")
        self.hero_texture = pygame.transform.smoothscale(self.hero_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.monster_texture = pygame.image.load("monster.webp").convert_alpha()
        self.monster_texture = pygame.transform.smoothscale(self.monster_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.ice_pick_texture = pygame.image.load("ice_pick.webp").convert_alpha()
        self.ice_pick_texture = pygame.transform.smoothscale(self.ice_pick_texture, (self.CELL_SIZE, self.CELL_SIZE))

        self.decoration = pygame.image.load("exit.webp").convert_alpha()
        self.decoration = pygame.transform.smoothscale(self.decoration, (self.CELL_SIZE, self.CELL_SIZE))
        self.snowstorm = self.create_snowstorm(500)
        self.visibility_radius = self.CELL_SIZE * 2
        self.camera_x = 1
        self.camera_y = 1
        self.ice_pick = None
        self.has_ice_pick = False
        self.ice_pick_pos = None
        self.spawn_ice_pick()

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
        # Если игрок использует ледоруб и находится рядом с стеной
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
            if keys[pygame.K_s]:
                self.hero.move(0, 1)
            if keys[pygame.K_a]:
                self.hero.move(-1, 0)
            if keys[pygame.K_d]:
                self.hero.move(1, 0)
            self.hero.frame_counter = 0

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
            self.screen.blit(self.hero_texture, (hero_screen_x, hero_screen_y))

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
                running = False

            if self.hero.x == self.monster.x and self.hero.y == self.monster.y:
                print("Вы пойманы монстром!")
                running = False

        pygame.quit()
        sys.exit()


# Запуск программы
if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    auth = AuthDialog()

    if auth.exec() == QDialog.DialogCode.Accepted:
        start_window = StartWindow()
        start_window.show()
        sys.exit(app.exec())
