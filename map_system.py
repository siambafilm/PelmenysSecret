import pygame as pg
import json
import os

class TileMap:
    def __init__(self, tile_size=64):
        self.tile_size = tile_size
        self.width = 0
        self.height = 0
        self.tiles = []          # объединённые базовые слои (для обратной совместимости)
        self.layer1_tiles = []
        self.layer2_tiles = []
        self.layer3_tiles = []    # слой поверх персонажа
        self.collisions = []
        self.tile_types = {}
        self.custom_tile_start_id = 11
        self._custom_tiles_loaded = False
        self.entry_point = None
        self.teleport_points = []
        self._init_default_tiles()

    def _init_default_tiles(self):
        self.tile_types = {
            0: self._create_tile((34, 139, 34)),
            1: self._create_tile((128, 128, 128)),
            2: self._create_tile((64, 164, 223)),
            3: self._create_tile((237, 201, 175)),
            4: self._create_tree_tile(),
            5: self._create_rock_tile(),
            6: self._create_flower_tile(),
            7: self._create_tile((169, 169, 169)),
            8: self._create_tile((25, 80, 25)),
            9: self._create_tile((200, 50, 50)),
            10: self._create_tile((240, 240, 255)),
        }

    def _ensure_custom_tiles_loaded(self):
        if self._custom_tiles_loaded:
            return
        try:
            pg.display.get_surface()
        except:
            return
        custom_dir = "custom_tiles"
        if not os.path.exists(custom_dir):
            self._custom_tiles_loaded = True
            return
        current_id = self.custom_tile_start_id
        for filename in sorted(os.listdir(custom_dir)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                filepath = os.path.join(custom_dir, filename)
                try:
                    surf = pg.image.load(filepath).convert_alpha()
                    if surf.get_width() != self.tile_size or surf.get_height() != self.tile_size:
                        surf = pg.transform.scale(surf, (self.tile_size, self.tile_size))
                    self.tile_types[current_id] = surf
                    current_id += 1
                except Exception as e:
                    print(f"Ошибка загрузки {filename}: {e}")
        if current_id > self.custom_tile_start_id:
            print(f"Загружено {current_id - self.custom_tile_start_id} кастомных тайлов")
        self._custom_tiles_loaded = True

    def _create_tile(self, color):
        surf = pg.Surface((self.tile_size, self.tile_size))
        surf.fill(color)
        for i in range(0, self.tile_size, 4):
            pg.draw.line(surf, tuple(max(0, c-20) for c in color), (i, 0), (i, self.tile_size), 1)
        for i in range(0, self.tile_size, 4):
            pg.draw.line(surf, tuple(max(0, c-20) for c in color), (0, i), (self.tile_size, i), 1)
        return surf

    def _create_tree_tile(self):
        surf = pg.Surface((self.tile_size, self.tile_size), pg.SRCALPHA)
        pg.draw.rect(surf, (101, 67, 33), (self.tile_size//2-8, self.tile_size//2, 16, 24))
        pg.draw.circle(surf, (34, 139, 34), (self.tile_size//2, self.tile_size//2-5), 20)
        return surf

    def _create_rock_tile(self):
        surf = pg.Surface((self.tile_size, self.tile_size), pg.SRCALPHA)
        pg.draw.ellipse(surf, (100, 100, 100), (self.tile_size//2-15, self.tile_size//2-10, 30, 20))
        return surf

    def _create_flower_tile(self):
        surf = pg.Surface((self.tile_size, self.tile_size), pg.SRCALPHA)
        surf.fill((34, 139, 34))
        colors = [(255, 100, 100), (255, 200, 100), (200, 100, 255), (100, 200, 255)]
        for i, color in enumerate(colors):
            x = 10 + (i % 2) * 25
            y = 10 + (i // 2) * 25
            pg.draw.circle(surf, color, (x, y), 6)
        return surf

    def load_from_file(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.width = data.get("width", 20)
            self.height = data.get("height", 15)
            self.tile_size = data.get("tile_size", 64)
            self.layer1_tiles = data.get("layer1_tiles", [])
            self.layer2_tiles = data.get("layer2_tiles", [])
            self.layer3_tiles = data.get("layer3_tiles", [])
            self.tiles = data.get("tiles", [])
            if not self.tiles:
                self.tiles = self.layer1_tiles + self.layer2_tiles
            self.collisions = data.get("collisions", [])
            self.entry_point = data.get("entry_point", None)
            self.teleport_points = data.get("teleport_points", [])
            self._init_default_tiles()
            self._custom_tiles_loaded = False
            self._ensure_custom_tiles_loaded()
            return True
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            return False

    def get_tile_at(self, x, y):
        for tx, ty, tile_type in self.tiles:
            if tx == x and ty == y:
                return tile_type
        return None

    def is_collision(self, x, y, width=1, height=1):
        for cx, cy, cw, ch in self.collisions:
            if (x < cx + cw and x + width > cx and y < cy + ch and y + height > cy):
                return True
        return False

    def draw(self, screen, camera_x=0, camera_y=0):
        self._ensure_custom_tiles_loaded()
        sw, sh = screen.get_width(), screen.get_height()
        sx = max(0, camera_x // self.tile_size)
        sy = max(0, camera_y // self.tile_size)
        ex = min(self.width, (camera_x + sw) // self.tile_size + 1)
        ey = min(self.height, (camera_y + sh) // self.tile_size + 1)
        for x, y, tile_type in self.tiles:
            if sx <= x < ex and sy <= y < ey:
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y
                if tile_type in self.tile_types:
                    ts = self.tile_types[tile_type]
                    if ts.get_width() != self.tile_size:
                        ts = pg.transform.scale(ts, (self.tile_size, self.tile_size))
                    screen.blit(ts, (screen_x, screen_y))

    def draw_overlay(self, screen, camera_x=0, camera_y=0):
        self._ensure_custom_tiles_loaded()
        sw, sh = screen.get_width(), screen.get_height()
        sx = max(0, camera_x // self.tile_size)
        sy = max(0, camera_y // self.tile_size)
        ex = min(self.width, (camera_x + sw) // self.tile_size + 1)
        ey = min(self.height, (camera_y + sh) // self.tile_size + 1)
        for x, y, tile_type in self.layer3_tiles:
            if sx <= x < ex and sy <= y < ey:
                screen_x = x * self.tile_size - camera_x
                screen_y = y * self.tile_size - camera_y
                if tile_type in self.tile_types:
                    ts = self.tile_types[tile_type]
                    if ts.get_width() != self.tile_size:
                        ts = pg.transform.scale(ts, (self.tile_size, self.tile_size))
                    screen.blit(ts, (screen_x, screen_y))


class Camera:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.smoothness = 0.1

    def follow(self, target_x, target_y):
        self.target_x = target_x - self.screen_width // 2
        self.target_y = target_y - self.screen_height // 2

    def update(self, map_width_pixels, map_height_pixels):
        self.x += (self.target_x - self.x) * self.smoothness
        self.y += (self.target_y - self.y) * self.smoothness
        max_x = max(0, map_width_pixels - self.screen_width)
        max_y = max(0, map_height_pixels - self.screen_height)
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def apply(self, rect):
        return pg.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

    def apply_point(self, x, y):
        return (x - self.x, y - self.y)