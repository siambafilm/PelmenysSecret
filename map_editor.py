import pygame as pg
import json
import sys
import os
import copy
import tkinter as tk
from tkinter import filedialog

# Инициализация Pygame
pg.init()

# Константы
TILE_SIZE = 64
UI_PANEL_WIDTH = 200
INITIAL_SCREEN_WIDTH = 1024
INITIAL_SCREEN_HEIGHT = 768

# Цвета
COLOR_BG = (40, 44, 52)
COLOR_UI_BG = (55, 59, 68)
COLOR_UI_BORDER = (86, 182, 194)
COLOR_SELECTED = (255, 215, 0)
COLOR_TEXT = (220, 220, 220)
COLOR_BUTTON = (86, 182, 194)
COLOR_BUTTON_HOVER = (106, 202, 214)
COLOR_GRID = (60, 64, 72)
COLOR_COLLISION = (255, 0, 0, 100)
COLOR_FILL_PREVIEW = (0, 255, 0, 100)
COLOR_ENTRY_POINT = (0, 255, 0)
COLOR_TELEPORT_POINT = (0, 150, 255)

def get_work_area_width(screen_width):
    return screen_width - UI_PANEL_WIDTH

class MapEditor:
    def __init__(self):
        self.screen_width = INITIAL_SCREEN_WIDTH
        self.screen_height = INITIAL_SCREEN_HEIGHT
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height), pg.RESIZABLE)
        pg.display.set_caption("PelmenysSecret - Map Editor")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 24)
        self.font_small = pg.font.Font(None, 20)
        self.font_title = pg.font.Font(None, 36)

        # Единый корень tkinter для диалогов
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()
        self.tk_root.update_idletasks()

        self.dialog_open = False

        self.mode = "paint"
        self.eraser_mode = False

        self.current_layer = 1
        self.layer1_tiles = []
        self.layer2_tiles = []
        self.layer3_tiles = []
        self.collisions = []

        self.map_width_tiles = 20
        self.map_height_tiles = 15
        self.tile_size = TILE_SIZE

        self.camera_x = 0
        self.camera_y = 0
        self.dragging_camera = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.editor_tiles = self.create_editor_tiles()
        self.brushes = []
        self.load_brushes()
        self.selected_brush = 0

        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 50

        self.clipboard = []
        self.copy_start_pos = None
        self.copy_end_pos = None
        self.is_selecting = False

        self.show_new_map_dialog = False
        self.new_map_width = "20"
        self.new_map_height = "15"
        self.show_resize_dialog = False
        self.resize_width = "20"
        self.resize_height = "15"
        self.resize_active_field = None

        self.brush_scroll_y = 0
        self.brush_area_height = 300

        self.entry_point = None
        self.teleport_points = []

        self.update_ui_rects()
        self.mouse_over_ui = False

    def __del__(self):
        if hasattr(self, 'tk_root'):
            try:
                self.tk_root.destroy()
            except:
                pass

    def get_work_area_width(self):
        return self.screen_width - UI_PANEL_WIDTH

    def update_ui_rects(self):
        work_width = self.get_work_area_width()
        self.buttons = {
            "new": pg.Rect(work_width + 10, 50, 180, 30),
            "save": pg.Rect(work_width + 10, 90, 180, 30),
            "load": pg.Rect(work_width + 10, 130, 180, 30),
            "clear": pg.Rect(work_width + 10, 170, 180, 30),
            "mode_paint": pg.Rect(work_width + 10, 210, 180, 30),
            "mode_collision": pg.Rect(work_width + 10, 250, 180, 30),
            "mode_fill": pg.Rect(work_width + 10, 290, 180, 30),
            "resize": pg.Rect(work_width + 10, 330, 180, 30),
            "mode_entry": pg.Rect(work_width + 10, 370, 180, 30),
            "mode_teleport": pg.Rect(work_width + 10, 410, 180, 30),
        }

    def create_editor_tiles(self):
        tiles = []
        # 0 - Трава
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 139, 34))
        for i in range(0, TILE_SIZE, 4):
            pg.draw.line(surf, (25, 109, 25), (i, 0), (i, TILE_SIZE), 1)
        for i in range(0, TILE_SIZE, 4):
            pg.draw.line(surf, (25, 109, 25), (0, i), (TILE_SIZE, i), 1)
        tiles.append(surf)
        # 1 - Камень
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((128, 128, 128))
        for i in range(0, TILE_SIZE, 3):
            pg.draw.line(surf, (100, 100, 100), (i, 0), (i, TILE_SIZE), 1)
        for i in range(0, TILE_SIZE, 3):
            pg.draw.line(surf, (100, 100, 100), (0, i), (TILE_SIZE, i), 1)
        tiles.append(surf)
        # 2 - Вода
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((64, 164, 223))
        for i in range(0, TILE_SIZE, 6):
            pg.draw.line(surf, (50, 140, 200), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        # 3 - Песок
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((237, 201, 175))
        for i in range(0, TILE_SIZE, 5):
            pg.draw.line(surf, (200, 170, 140), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        # 4 - Дерево
        surf = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
        pg.draw.rect(surf, (101, 67, 33), (TILE_SIZE//2 - 8, TILE_SIZE//2, 16, 24))
        pg.draw.circle(surf, (34, 139, 34), (TILE_SIZE//2, TILE_SIZE//2 - 5), 20)
        tiles.append(surf)
        # 5 - Камень (маленький)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
        pg.draw.ellipse(surf, (100, 100, 100), (TILE_SIZE//2 - 15, TILE_SIZE//2 - 10, 30, 20))
        tiles.append(surf)
        # 6 - Цветы
        surf = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
        surf.fill((34, 139, 34))
        colors = [(255, 100, 100), (255, 200, 100), (200, 100, 255), (100, 200, 255)]
        for i, color in enumerate(colors):
            x = 10 + (i % 2) * 25
            y = 10 + (i // 2) * 25
            pg.draw.circle(surf, color, (x, y), 6)
        tiles.append(surf)
        # 7 - Путь
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((169, 169, 169))
        for i in range(0, TILE_SIZE, 4):
            pg.draw.line(surf, (150, 150, 150), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        # 8 - Темная трава
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((25, 80, 25))
        for i in range(0, TILE_SIZE, 4):
            pg.draw.line(surf, (20, 60, 20), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        # 9 - Лава
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((200, 50, 50))
        for i in range(0, TILE_SIZE, 5):
            pg.draw.line(surf, (180, 30, 30), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        # 10 - Снег
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((240, 240, 255))
        for i in range(0, TILE_SIZE, 6):
            pg.draw.line(surf, (220, 220, 240), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        return tiles

    def load_brushes(self):
        self.brushes = self.editor_tiles
        self.load_custom_tiles()

    def load_custom_tiles(self):
        custom_dir = "custom_tiles"
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir)
            return
        loaded_count = 0
        for filename in sorted(os.listdir(custom_dir)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                filepath = os.path.join(custom_dir, filename)
                try:
                    surf = pg.image.load(filepath).convert_alpha()
                    w, h = surf.get_width(), surf.get_height()
                    if w != TILE_SIZE or h != TILE_SIZE:
                        surf = pg.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
                    self.brushes.append(surf)
                    loaded_count += 1
                except Exception as e:
                    print(f"Ошибка загрузки {filename}: {e}")
        if loaded_count > 0:
            print(f"Загружено {loaded_count} кастомных тайлов")

    def save_state(self):
        state = {
            'layer1_tiles': copy.deepcopy(self.layer1_tiles),
            'layer2_tiles': copy.deepcopy(self.layer2_tiles),
            'layer3_tiles': copy.deepcopy(self.layer3_tiles),
            'collisions': copy.deepcopy(self.collisions),
            'entry_point': copy.deepcopy(self.entry_point),
            'teleport_points': copy.deepcopy(self.teleport_points),
        }
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        current_state = {
            'layer1_tiles': copy.deepcopy(self.layer1_tiles),
            'layer2_tiles': copy.deepcopy(self.layer2_tiles),
            'layer3_tiles': copy.deepcopy(self.layer3_tiles),
            'collisions': copy.deepcopy(self.collisions),
            'entry_point': copy.deepcopy(self.entry_point),
            'teleport_points': copy.deepcopy(self.teleport_points),
        }
        self.redo_stack.append(current_state)
        prev_state = self.undo_stack.pop()
        self.layer1_tiles = prev_state['layer1_tiles']
        self.layer2_tiles = prev_state['layer2_tiles']
        self.layer3_tiles = prev_state['layer3_tiles']
        self.collisions = prev_state['collisions']
        self.entry_point = prev_state.get('entry_point')
        self.teleport_points = prev_state.get('teleport_points', [])

    def redo(self):
        if not self.redo_stack:
            return
        current_state = {
            'layer1_tiles': copy.deepcopy(self.layer1_tiles),
            'layer2_tiles': copy.deepcopy(self.layer2_tiles),
            'layer3_tiles': copy.deepcopy(self.layer3_tiles),
            'collisions': copy.deepcopy(self.collisions),
            'entry_point': copy.deepcopy(self.entry_point),
            'teleport_points': copy.deepcopy(self.teleport_points),
        }
        self.undo_stack.append(current_state)
        next_state = self.redo_stack.pop()
        self.layer1_tiles = next_state['layer1_tiles']
        self.layer2_tiles = next_state['layer2_tiles']
        self.layer3_tiles = next_state['layer3_tiles']
        self.collisions = next_state['collisions']
        self.entry_point = next_state.get('entry_point')
        self.teleport_points = next_state.get('teleport_points', [])

    def copy_selection(self):
        if self.copy_start_pos is None or self.copy_end_pos is None:
            return
        x1, y1 = self.copy_start_pos
        x2, y2 = self.copy_end_pos
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        self.clipboard = []
        for tiles, layer_num in [(self.layer1_tiles, 1), (self.layer2_tiles, 2), (self.layer3_tiles, 3)]:
            for tx, ty, idx in tiles:
                if min_x <= tx <= max_x and min_y <= ty <= max_y:
                    self.clipboard.append((tx - min_x, ty - min_y, idx, layer_num))

    def paste_tiles(self):
        if not self.clipboard:
            return
        mouse_x, mouse_y = pg.mouse.get_pos()
        if mouse_x >= self.get_work_area_width():
            return
        world_x, world_y = self.screen_to_world(mouse_x, mouse_y)
        self.save_state()
        for rel_x, rel_y, brush_idx, layer_num in self.clipboard:
            target_x = world_x + rel_x
            target_y = world_y + rel_y
            if 0 <= target_x < self.map_width_tiles and 0 <= target_y < self.map_height_tiles:
                self.set_tile_at_layer(target_x, target_y, brush_idx, layer_num)

    def flood_fill(self, start_x, start_y, brush_idx):
        if not (0 <= start_x < self.map_width_tiles and 0 <= start_y < self.map_height_tiles):
            return
        if self.copy_start_pos and self.copy_end_pos:
            x1, y1 = self.copy_start_pos
            x2, y2 = self.copy_end_pos
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            self.save_state()
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    self.set_tile_at_layer(x, y, brush_idx, self.current_layer)
            self.copy_start_pos = None
            self.copy_end_pos = None
            return
        if self.current_layer == 3:
            queue = [(start_x, start_y)]
            visited = set()
            target_tile = self.get_tile_at_layer(start_x, start_y, self.current_layer)
            if target_tile == brush_idx:
                return
            self.save_state()
            while queue:
                x, y = queue.pop(0)
                if (x, y) in visited:
                    continue
                visited.add((x, y))
                self.set_tile_at_layer(x, y, brush_idx, self.current_layer)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.map_width_tiles and 0 <= ny < self.map_height_tiles:
                        neighbor = self.get_tile_at_layer(nx, ny, self.current_layer)
                        if neighbor == target_tile:
                            queue.append((nx, ny))
        else:
            current_tiles = self.layer1_tiles if self.current_layer == 1 else self.layer2_tiles
            target_tile = None
            for tx, ty, idx in current_tiles:
                if tx == start_x and ty == start_y:
                    target_tile = idx
                    break
            if target_tile == brush_idx:
                return
            self.save_state()
            queue = [(start_x, start_y)]
            visited = set([(start_x, start_y)])
            while queue:
                x, y = queue.pop(0)
                self.set_tile_at_layer(x, y, brush_idx, self.current_layer)
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.map_width_tiles and 0 <= ny < self.map_height_tiles and (nx, ny) not in visited:
                        neighbor_tile = None
                        for tx, ty, idx in current_tiles:
                            if tx == nx and ty == ny:
                                neighbor_tile = idx
                                break
                        if neighbor_tile == target_tile:
                            visited.add((nx, ny))
                            queue.append((nx, ny))

    def new_map(self, width, height):
        self.map_width_tiles = max(5, min(100, width))
        self.map_height_tiles = max(5, min(100, height))
        self.layer1_tiles = []
        self.layer2_tiles = []
        self.layer3_tiles = []
        self.collisions = []
        self.entry_point = None
        self.teleport_points = []
        self.camera_x = 0
        self.camera_y = 0
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.clipboard.clear()

    def resize_map(self, width, height):
        new_w = max(5, min(100, width))
        new_h = max(5, min(100, height))
        self.layer1_tiles = [(x, y, idx) for (x, y, idx) in self.layer1_tiles if x < new_w and y < new_h]
        self.layer2_tiles = [(x, y, idx) for (x, y, idx) in self.layer2_tiles if x < new_w and y < new_h]
        self.layer3_tiles = [(x, y, idx) for (x, y, idx) in self.layer3_tiles if x < new_w and y < new_h]
        self.collisions = [(x, y, w, h) for (x, y, w, h) in self.collisions if x < new_w and y < new_h]
        if self.entry_point and (self.entry_point[0] >= new_w or self.entry_point[1] >= new_h):
            self.entry_point = None
        self.teleport_points = [tp for tp in self.teleport_points if tp["x"] < new_w and tp["y"] < new_h]
        self.map_width_tiles = new_w
        self.map_height_tiles = new_h
        self.camera_x = min(self.camera_x, self.map_width_tiles * self.tile_size - self.get_work_area_width())
        self.camera_y = min(self.camera_y, self.map_height_tiles * self.tile_size - self.screen_height)

    def save_map(self, filename):
        combined_tiles = self.layer1_tiles + self.layer2_tiles
        data = {
            "version": "1.2",
            "width": self.map_width_tiles,
            "height": self.map_height_tiles,
            "tile_size": self.tile_size,
            "tiles": combined_tiles,
            "layer1_tiles": self.layer1_tiles,
            "layer2_tiles": self.layer2_tiles,
            "layer3_tiles": self.layer3_tiles,
            "collisions": self.collisions,
            "entry_point": self.entry_point,
            "teleport_points": self.teleport_points
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Карта сохранена: {filename}")

    def load_map(self, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.map_width_tiles = data.get("width", 20)
            self.map_height_tiles = data.get("height", 15)
            self.tile_size = data.get("tile_size", TILE_SIZE)
            self.layer1_tiles = data.get("layer1_tiles", [])
            self.layer2_tiles = data.get("layer2_tiles", [])
            self.layer3_tiles = data.get("layer3_tiles", [])
            self.collisions = data.get("collisions", [])
            self.entry_point = data.get("entry_point", None)
            self.teleport_points = data.get("teleport_points", [])
            self.camera_x = 0
            self.camera_y = 0
            self.undo_stack.clear()
            self.redo_stack.clear()
            print(f"Карта загружена: {filename} ({self.map_width_tiles}x{self.map_height_tiles})")
            return True
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            return False

    def get_tile_at_layer(self, x, y, layer):
        if layer == 1:
            tiles = self.layer1_tiles
        elif layer == 2:
            tiles = self.layer2_tiles
        else:
            tiles = self.layer3_tiles
        for tx, ty, idx in tiles:
            if tx == x and ty == y:
                return idx
        return None

    def get_tile_at(self, x, y):
        return self.get_tile_at_layer(x, y, self.current_layer)

    def set_tile_at_layer(self, x, y, brush_idx, layer):
        if layer == 1:
            tiles = self.layer1_tiles
        elif layer == 2:
            tiles = self.layer2_tiles
        else:
            tiles = self.layer3_tiles
        new_tiles = [(tx, ty, idx) for tx, ty, idx in tiles if not (tx == x and ty == y)]
        if brush_idx >= 0:
            new_tiles.append((x, y, brush_idx))
        if layer == 1:
            self.layer1_tiles = new_tiles
        elif layer == 2:
            self.layer2_tiles = new_tiles
        else:
            self.layer3_tiles = new_tiles

    def set_tile(self, x, y, brush_idx):
        self.set_tile_at_layer(x, y, brush_idx, self.current_layer)

    def toggle_collision(self, x, y):
        for i, (cx, cy, cw, ch) in enumerate(self.collisions):
            if cx == x and cy == y:
                self.collisions.pop(i)
                return
        self.collisions.append((x, y, 1, 1))

    def screen_to_world(self, screen_x, screen_y):
        world_x = (screen_x + self.camera_x) // self.tile_size
        world_y = (screen_y + self.camera_y) // self.tile_size
        return world_x, world_y

    def world_to_screen(self, world_x, world_y):
        screen_x = world_x * self.tile_size - self.camera_x
        screen_y = world_y * self.tile_size - self.camera_y
        return screen_x, screen_y

    def draw_grid(self):
        work_width = self.get_work_area_width()
        start_x = (self.camera_x // self.tile_size) * self.tile_size - self.camera_x
        start_y = (self.camera_y // self.tile_size) * self.tile_size - self.camera_y
        for x in range(int(start_x), work_width, self.tile_size):
            alpha = 50 if x % (self.tile_size * 5) != 0 else 100
            s = pg.Surface((1, self.screen_height))
            s.fill((*COLOR_GRID, alpha))
            self.screen.blit(s, (x, 0))
        for y in range(int(start_y), self.screen_height, self.tile_size):
            alpha = 50 if y % (self.tile_size * 5) != 0 else 100
            s = pg.Surface((work_width, 1))
            s.fill((*COLOR_GRID, alpha))
            self.screen.blit(s, (0, y))
        map_px_width = self.map_width_tiles * self.tile_size
        map_px_height = self.map_height_tiles * self.tile_size
        screen_left = -self.camera_x
        screen_top = -self.camera_y
        screen_right = screen_left + map_px_width
        screen_bottom = screen_top + map_px_height
        if screen_left < 0: screen_left = 0
        if screen_top < 0: screen_top = 0
        if screen_right > work_width: screen_right = work_width
        if screen_bottom > self.screen_height: screen_bottom = self.screen_height
        if screen_right > screen_left and screen_bottom > screen_top:
            pg.draw.rect(self.screen, (255, 0, 0), (screen_left, screen_top, screen_right - screen_left, screen_bottom - screen_top), 2)

    def draw_tiles(self):
        work_width = self.get_work_area_width()
        start_x = max(0, self.camera_x // self.tile_size)
        start_y = max(0, self.camera_y // self.tile_size)
        end_x = min(self.map_width_tiles, (self.camera_x + work_width) // self.tile_size + 1)
        end_y = min(self.map_height_tiles, (self.camera_y + self.screen_height) // self.tile_size + 1)

        if self.current_layer == 1:
            l1_a, l2_a, l3_a = 255, 100, 100
        elif self.current_layer == 2:
            l1_a, l2_a, l3_a = 100, 255, 100
        else:
            l1_a, l2_a, l3_a = 100, 100, 255

        for x, y, idx in self.layer1_tiles:
            if start_x <= x < end_x and start_y <= y < end_y:
                sx, sy = x * self.tile_size - self.camera_x, y * self.tile_size - self.camera_y
                if 0 <= idx < len(self.brushes):
                    scaled = pg.transform.scale(self.brushes[idx], (self.tile_size, self.tile_size))
                    if l1_a < 255:
                        scaled = scaled.copy()
                        scaled.set_alpha(l1_a)
                    self.screen.blit(scaled, (sx, sy))
        for x, y, idx in self.layer2_tiles:
            if start_x <= x < end_x and start_y <= y < end_y:
                sx, sy = x * self.tile_size - self.camera_x, y * self.tile_size - self.camera_y
                if 0 <= idx < len(self.brushes):
                    scaled = pg.transform.scale(self.brushes[idx], (self.tile_size, self.tile_size))
                    if l2_a < 255:
                        scaled = scaled.copy()
                        scaled.set_alpha(l2_a)
                    self.screen.blit(scaled, (sx, sy))
        for x, y, idx in self.layer3_tiles:
            if start_x <= x < end_x and start_y <= y < end_y:
                sx, sy = x * self.tile_size - self.camera_x, y * self.tile_size - self.camera_y
                if 0 <= idx < len(self.brushes):
                    scaled = pg.transform.scale(self.brushes[idx], (self.tile_size, self.tile_size))
                    self.screen.blit(scaled, (sx, sy))

    def draw_collisions(self):
        work_width = self.get_work_area_width()
        start_x = max(0, self.camera_x // self.tile_size)
        start_y = max(0, self.camera_y // self.tile_size)
        end_x = min(self.map_width_tiles, (self.camera_x + work_width) // self.tile_size + 1)
        end_y = min(self.map_height_tiles, (self.camera_y + self.screen_height) // self.tile_size + 1)
        for cx, cy, cw, ch in self.collisions:
            if start_x <= cx < end_x and start_y <= cy < end_y:
                sx, sy = cx * self.tile_size - self.camera_x, cy * self.tile_size - self.camera_y
                s = pg.Surface((cw * self.tile_size, ch * self.tile_size), pg.SRCALPHA)
                s.fill((255, 0, 0, 100))
                self.screen.blit(s, (sx, sy))
                pg.draw.rect(self.screen, (255, 0, 0), (sx, sy, cw * self.tile_size, ch * self.tile_size), 1)

    def draw_selection(self):
        if self.copy_start_pos and self.copy_end_pos:
            x1, y1 = self.copy_start_pos
            x2, y2 = self.copy_end_pos
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            sx1 = min_x * self.tile_size - self.camera_x
            sy1 = min_y * self.tile_size - self.camera_y
            sx2 = (max_x + 1) * self.tile_size - self.camera_x
            sy2 = (max_y + 1) * self.tile_size - self.camera_y
            rect = pg.Rect(sx1, sy1, sx2 - sx1, sy2 - sy1)
            pg.draw.rect(self.screen, (255, 255, 0), rect, 2)
            s = pg.Surface((sx2 - sx1, sy2 - sy1), pg.SRCALPHA)
            s.fill((255, 255, 0, 50))
            self.screen.blit(s, (sx1, sy1))

    def draw_entry_teleport_points(self):
        if self.entry_point:
            x, y = self.entry_point
            sx = x * self.tile_size - self.camera_x
            sy = y * self.tile_size - self.camera_y
            pg.draw.rect(self.screen, COLOR_ENTRY_POINT, (sx + 2, sy + 2, self.tile_size - 4, self.tile_size - 4), 3)
            label = self.font_small.render("S", True, COLOR_ENTRY_POINT)
            self.screen.blit(label, (sx + self.tile_size//2 - 4, sy + self.tile_size//2 - 8))
        for tp in self.teleport_points:
            x, y = tp["x"], tp["y"]
            sx = x * self.tile_size - self.camera_x
            sy = y * self.tile_size - self.camera_y
            pg.draw.rect(self.screen, COLOR_TELEPORT_POINT, (sx + 2, sy + 2, self.tile_size - 4, self.tile_size - 4), 3)
            label = self.font_small.render("T", True, COLOR_TELEPORT_POINT)
            self.screen.blit(label, (sx + self.tile_size//2 - 4, sy + self.tile_size//2 - 8))
            map_label = self.font_small.render(tp["target_map"], True, COLOR_TELEPORT_POINT)
            self.screen.blit(map_label, (sx, sy + self.tile_size))

    def draw_ui(self):
        work_width = self.get_work_area_width()
        pg.draw.rect(self.screen, COLOR_UI_BG, (work_width, 0, UI_PANEL_WIDTH, self.screen_height))
        pg.draw.line(self.screen, COLOR_UI_BORDER, (work_width, 0), (work_width, self.screen_height), 2)
        title = self.font_title.render("Map Editor", True, COLOR_TEXT)
        self.screen.blit(title, (work_width + 10, 10))
        pg.draw.line(self.screen, COLOR_UI_BORDER, (work_width + 10, 45), (self.screen_width - 10, 45), 1)

        mouse_pos = pg.mouse.get_pos()
        for name, rect in self.buttons.items():
            hover = rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pg.draw.rect(self.screen, color, rect, border_radius=5)
            pg.draw.rect(self.screen, COLOR_UI_BORDER, rect, 2, border_radius=5)
            text_map = {
                "new": "Новая карта",
                "save": "Сохранить",
                "load": "Загрузить",
                "clear": "Очистить",
                "mode_paint": "Режим: Кисть",
                "mode_collision": "Режим: Коллизия",
                "mode_fill": "Режим: Заливка (F)",
                "resize": "Изменить размер",
                "mode_entry": "Точка входа (S)",
                "mode_teleport": "Точка телепорта (T)",
            }
            text = self.font_small.render(text_map[name], True, COLOR_TEXT)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # Индикатор режима
        mode_text = {
            "paint": "Режим: Рисование",
            "collision": "Режим: Коллизия",
            "fill": "Режим: Заливка",
            "entry_point": "Режим: Точка входа",
            "teleport_point": "Режим: Телепорт",
        }.get(self.mode, "")
        mode_color = {
            "paint": (100, 255, 100),
            "collision": (255, 100, 100),
            "fill": (100, 100, 255),
            "entry_point": COLOR_ENTRY_POINT,
            "teleport_point": COLOR_TELEPORT_POINT,
        }.get(self.mode, (255,255,255))
        mode_surf = self.font.render(mode_text, True, mode_color)
        self.screen.blit(mode_surf, (work_width + 10, 450))

        # Слой
        layer_text = f"Слой: {self.current_layer}"
        self.screen.blit(self.font.render(layer_text, True, (255,255,255)), (work_width + 10, 475))

        # Заголовок кистей
        pg.draw.line(self.screen, COLOR_UI_BORDER, (work_width + 10, 490), (self.screen_width - 10, 490), 1)
        brushes_title = self.font.render("Кисти:", True, COLOR_TEXT)
        self.screen.blit(brushes_title, (work_width + 10, 495))

        # Отрисовка кистей с прокруткой
        brush_start_y = 525
        max_scroll = max(0, len(self.brushes) // 2 * 70 - self.brush_area_height)
        self.brush_scroll_y = max(0, min(self.brush_scroll_y, max_scroll))
        for i, brush in enumerate(self.brushes):
            x = work_width + 10 + (i % 2) * 85
            y = brush_start_y + (i // 2) * 70 - self.brush_scroll_y
            if y + TILE_SIZE < brush_start_y or y > brush_start_y + self.brush_area_height:
                continue
            border_color = COLOR_SELECTED if i == self.selected_brush else COLOR_UI_BORDER
            pg.draw.rect(self.screen, border_color, (x - 2, y - 2, TILE_SIZE + 4, TILE_SIZE + 4), 2, border_radius=3)
            scaled = pg.transform.scale(brush, (TILE_SIZE, TILE_SIZE))
            self.screen.blit(scaled, (x, y))
            num_text = self.font_small.render(str(i), True, COLOR_TEXT)
            self.screen.blit(num_text, (x + 2, y + TILE_SIZE + 5))

        # Статус
        status_y = self.screen_height - 60
        pg.draw.line(self.screen, COLOR_UI_BORDER, (work_width + 10, status_y - 10), (self.screen_width - 10, status_y - 10), 1)
        status = f"Карта: {self.map_width_tiles}x{self.map_height_tiles} | Слой1: {len(self.layer1_tiles)} Слой2: {len(self.layer2_tiles)} Слой3: {len(self.layer3_tiles)} Коллизий: {len(self.collisions)}"
        self.screen.blit(self.font_small.render(status, True, COLOR_TEXT), (work_width + 10, status_y))

        # Подсказки
        hints = [
            "1/2/3 - сменa слоя | 4 - точка входа | 5 - телепорт",
            "F - заливка | Пробел - режимы | ПКМ - ластик",
            "Ctrl+Z/Y - undo/redo | C - выделить | Ctrl+V - вставить",
        ]
        for i, h in enumerate(hints):
            surf = self.font_small.render(h, True, (150,150,150))
            self.screen.blit(surf, (work_width + 10, self.screen_height - 40 + i * 18))

    def draw_new_map_dialog(self):
        overlay = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))
        dialog_w, dialog_h = 300, 150
        dialog_x = (self.screen_width - dialog_w)//2
        dialog_y = (self.screen_height - dialog_h)//2
        pg.draw.rect(self.screen, COLOR_UI_BG, (dialog_x, dialog_y, dialog_w, dialog_h), border_radius=10)
        pg.draw.rect(self.screen, COLOR_UI_BORDER, (dialog_x, dialog_y, dialog_w, dialog_h), 2, border_radius=10)
        title = self.font_title.render("Новая карта", True, COLOR_TEXT)
        self.screen.blit(title, (dialog_x + (dialog_w - title.get_width())//2, dialog_y + 15))
        self.screen.blit(self.font.render("Ширина (5-100):", True, COLOR_TEXT), (dialog_x + 20, dialog_y + 55))
        self.screen.blit(self.font.render("Высота (5-100):", True, COLOR_TEXT), (dialog_x + 20, dialog_y + 90))
        ok_rect = pg.Rect(dialog_x + 50, dialog_y + 115, 80, 30)
        cancel_rect = pg.Rect(dialog_x + 170, dialog_y + 115, 80, 30)
        for rect, text, color in [(ok_rect, "OK", COLOR_BUTTON), (cancel_rect, "Отмена", (100,100,100))]:
            hover = rect.collidepoint(pg.mouse.get_pos())
            c = COLOR_BUTTON_HOVER if hover else color
            pg.draw.rect(self.screen, c, rect, border_radius=5)
            pg.draw.rect(self.screen, COLOR_UI_BORDER, rect, 2, border_radius=5)
            btn_text = self.font_small.render(text, True, COLOR_TEXT)
            self.screen.blit(btn_text, (rect.x + (rect.width - btn_text.get_width())//2, rect.y + (rect.height - btn_text.get_height())//2))
        return ok_rect, cancel_rect

    def draw_resize_dialog(self):
        overlay = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        overlay.fill((0,0,0,180))
        self.screen.blit(overlay, (0,0))
        dialog_w, dialog_h = 300, 150
        dialog_x = (self.screen_width - dialog_w)//2
        dialog_y = (self.screen_height - dialog_h)//2
        pg.draw.rect(self.screen, COLOR_UI_BG, (dialog_x, dialog_y, dialog_w, dialog_h), border_radius=10)
        pg.draw.rect(self.screen, COLOR_UI_BORDER, (dialog_x, dialog_y, dialog_w, dialog_h), 2, border_radius=10)
        title = self.font_title.render("Изменить размер", True, COLOR_TEXT)
        self.screen.blit(title, (dialog_x + (dialog_w - title.get_width())//2, dialog_y + 15))
        self.screen.blit(self.font.render("Ширина (5-100):", True, COLOR_TEXT), (dialog_x + 20, dialog_y + 55))
        self.screen.blit(self.font.render("Высота (5-100):", True, COLOR_TEXT), (dialog_x + 20, dialog_y + 90))
        width_input = pg.Rect(dialog_x + 150, dialog_y + 50, 80, 24)
        height_input = pg.Rect(dialog_x + 150, dialog_y + 85, 80, 24)
        for rect, is_active in [(width_input, self.resize_active_field == "width"), (height_input, self.resize_active_field == "height")]:
            pg.draw.rect(self.screen, (200,200,200) if is_active else (150,150,150), rect)
            pg.draw.rect(self.screen, COLOR_UI_BORDER, rect, 1)
        self.screen.blit(self.font_small.render(self.resize_width, True, (0,0,0)), (width_input.x+5, width_input.y+5))
        self.screen.blit(self.font_small.render(self.resize_height, True, (0,0,0)), (height_input.x+5, height_input.y+5))
        if self.resize_active_field == "width":
            w_text = self.font_small.render(self.resize_width, True, (0,0,0))
            pg.draw.line(self.screen, (0,0,0), (width_input.x+5+w_text.get_width(), width_input.y+5),
                         (width_input.x+5+w_text.get_width(), width_input.y+19), 1)
        elif self.resize_active_field == "height":
            h_text = self.font_small.render(self.resize_height, True, (0,0,0))
            pg.draw.line(self.screen, (0,0,0), (height_input.x+5+h_text.get_width(), height_input.y+5),
                         (height_input.x+5+h_text.get_width(), height_input.y+19), 1)
        ok_rect = pg.Rect(dialog_x + 50, dialog_y + 115, 80, 30)
        cancel_rect = pg.Rect(dialog_x + 170, dialog_y + 115, 80, 30)
        for rect, text, color in [(ok_rect, "OK", COLOR_BUTTON), (cancel_rect, "Отмена", (100,100,100))]:
            hover = rect.collidepoint(pg.mouse.get_pos())
            c = COLOR_BUTTON_HOVER if hover else color
            pg.draw.rect(self.screen, c, rect, border_radius=5)
            pg.draw.rect(self.screen, COLOR_UI_BORDER, rect, 2, border_radius=5)
            btn_text = self.font_small.render(text, True, COLOR_TEXT)
            self.screen.blit(btn_text, (rect.x + (rect.width - btn_text.get_width())//2, rect.y + (rect.height - btn_text.get_height())//2))
        return ok_rect, cancel_rect, width_input, height_input

    def handle_events(self):
        if self.dialog_open:
            pg.event.clear()
            return True
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.VIDEORESIZE:
                self.screen_width = max(event.w, 800)
                self.screen_height = max(event.h, 600)
                self.screen = pg.display.set_mode((self.screen_width, self.screen_height), pg.RESIZABLE)
                self.update_ui_rects()
            if self.show_new_map_dialog:
                self.handle_new_map_dialog(event)
                continue
            if self.show_resize_dialog:
                self.handle_resize_dialog(event)
                continue
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if event.pos[0] < self.get_work_area_width():
                        if self.is_selecting:
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            self.copy_end_pos = (wx, wy)
                            if self.copy_start_pos:
                                self.copy_selection()
                                self.is_selecting = False
                        elif self.mode == "paint":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                                self.save_state()
                                self.set_tile(wx, wy, self.selected_brush)
                        elif self.mode == "collision":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                                self.save_state()
                                self.toggle_collision(wx, wy)
                        elif self.mode == "fill":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                                self.flood_fill(wx, wy, self.selected_brush)
                        elif self.mode == "entry_point":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                                self.save_state()
                                self.entry_point = (wx, wy)
                        elif self.mode == "teleport_point":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                                self.dialog_open = True
                                target = self.ask_string_pygame("Имя карты (без .map):", default="")
                                self.dialog_open = False
                                if target:
                                    self.save_state()
                                    self.teleport_points = [p for p in self.teleport_points if not (p["x"] == wx and p["y"] == wy)]
                                    self.teleport_points.append({"x": wx, "y": wy, "target_map": target})
                    else:
                        for name, rect in self.buttons.items():
                            if rect.collidepoint(event.pos):
                                self.handle_button(name)
                                break
                        else:
                            work_width = self.get_work_area_width()
                            brush_start_y = 525
                            for i in range(len(self.brushes)):
                                x = work_width + 10 + (i % 2) * 85
                                y = brush_start_y + (i // 2) * 70 - self.brush_scroll_y
                                rect = pg.Rect(x - 2, y - 2, TILE_SIZE + 4, TILE_SIZE + 4)
                                if rect.collidepoint(event.pos):
                                    self.selected_brush = i
                                    break
                elif event.button == 2:
                    self.dragging_camera = True
                    self.drag_start_x = event.pos[0]
                    self.drag_start_y = event.pos[1]
                elif event.button == 3:
                    if event.pos[0] < self.get_work_area_width():
                        if self.mode == "paint":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                                self.save_state()
                                self.set_tile(wx, wy, -1)
                        elif self.mode == "teleport_point":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            self.teleport_points = [p for p in self.teleport_points if not (p["x"] == wx and p["y"] == wy)]
                elif event.button == 4:
                    mouse_x, mouse_y = event.pos
                    work_width = self.get_work_area_width()
                    if work_width + 10 <= mouse_x <= work_width + UI_PANEL_WIDTH - 10 and 525 <= mouse_y <= 525 + self.brush_area_height:
                        self.brush_scroll_y = max(0, self.brush_scroll_y - 70)
                    else:
                        self.tile_size = min(128, self.tile_size + 8)
                elif event.button == 5:
                    mouse_x, mouse_y = event.pos
                    work_width = self.get_work_area_width()
                    if work_width + 10 <= mouse_x <= work_width + UI_PANEL_WIDTH - 10 and 525 <= mouse_y <= 525 + self.brush_area_height:
                        max_scroll = max(0, len(self.brushes)//2 * 70 - self.brush_area_height)
                        self.brush_scroll_y = min(max_scroll, self.brush_scroll_y + 70)
                    else:
                        self.tile_size = max(32, self.tile_size - 8)
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 2:
                    self.dragging_camera = False
            elif event.type == pg.MOUSEMOTION:
                if self.dragging_camera:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.camera_x = max(0, self.camera_x - dx)
                    self.camera_y = max(0, self.camera_y - dy)
                    self.drag_start_x = event.pos[0]
                    self.drag_start_y = event.pos[1]
                elif self.is_selecting and event.pos[0] < self.get_work_area_width():
                    wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                    self.copy_end_pos = (wx, wy)
            elif event.type == pg.KEYDOWN:
                mods = pg.key.get_mods()
                ctrl = mods & pg.KMOD_CTRL
                if ctrl:
                    if event.key == pg.K_z:
                        self.undo()
                    elif event.key == pg.K_y:
                        self.redo()
                    elif event.key == pg.K_c:
                        if self.copy_start_pos:
                            self.copy_selection()
                            self.is_selecting = False
                    elif event.key == pg.K_v:
                        self.paste_tiles()
                else:
                    if event.key == pg.K_SPACE:
                        modes = ["paint", "collision", "fill", "entry_point", "teleport_point"]
                        idx = modes.index(self.mode) if self.mode in modes else 0
                        self.mode = modes[(idx + 1) % len(modes)]
                    elif event.key == pg.K_f:
                        self.mode = "fill"
                    elif event.key == pg.K_1:
                        self.current_layer = 1
                    elif event.key == pg.K_2:
                        self.current_layer = 2
                    elif event.key == pg.K_3:
                        self.current_layer = 3
                    elif event.key == pg.K_4:
                        self.mode = "entry_point"
                    elif event.key == pg.K_5:
                        self.mode = "teleport_point"
                    elif event.key == pg.K_c:
                        if not self.is_selecting:
                            self.is_selecting = True
                            mx, my = pg.mouse.get_pos()
                            self.copy_start_pos = self.screen_to_world(mx, my)
                            self.copy_end_pos = None
                    elif event.key == pg.K_ESCAPE:
                        if self.show_new_map_dialog:
                            self.show_new_map_dialog = False
                        elif self.is_selecting:
                            self.is_selecting = False
                            self.copy_start_pos = None
                            self.copy_end_pos = None
                        else:
                            return False
        return True

    def handle_button(self, name):
        if name == "new":
            self.show_new_map_dialog = True
        elif name == "save":
            self.save_map_dialog()
        elif name == "load":
            self.load_map_dialog()
        elif name == "clear":
            self.save_state()
            self.layer1_tiles = []
            self.layer2_tiles = []
            self.layer3_tiles = []
            self.collisions = []
            self.entry_point = None
            self.teleport_points = []
        elif name == "mode_paint":
            self.mode = "paint"
        elif name == "mode_collision":
            self.mode = "collision"
        elif name == "mode_fill":
            self.mode = "fill"
        elif name == "resize":
            self.show_resize_dialog = True
            self.resize_width = str(self.map_width_tiles)
            self.resize_height = str(self.map_height_tiles)
            self.resize_active_field = "width"
        elif name == "mode_entry":
            self.mode = "entry_point"
        elif name == "mode_teleport":
            self.mode = "teleport_point"

    def handle_new_map_dialog(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            dw, dh = 300, 150
            dx = (self.screen_width - dw)//2
            dy = (self.screen_height - dh)//2
            ok = pg.Rect(dx + 50, dy + 115, 80, 30)
            cancel = pg.Rect(dx + 170, dy + 115, 80, 30)
            if ok.collidepoint(event.pos):
                try:
                    w = int(self.new_map_width)
                    h = int(self.new_map_height)
                    self.new_map(w, h)
                    self.show_new_map_dialog = False
                except ValueError:
                    pass
            elif cancel.collidepoint(event.pos):
                self.show_new_map_dialog = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                try:
                    w = int(self.new_map_width)
                    h = int(self.new_map_height)
                    self.new_map(w, h)
                    self.show_new_map_dialog = False
                except ValueError:
                    pass
            elif event.key == pg.K_ESCAPE:
                self.show_new_map_dialog = False

    def handle_resize_dialog(self, event):
        dw, dh = 300, 150
        dx = (self.screen_width - dw)//2
        dy = (self.screen_height - dh)//2
        wi = pg.Rect(dx + 150, dy + 50, 80, 24)
        hi = pg.Rect(dx + 150, dy + 85, 80, 24)
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            ok = pg.Rect(dx + 50, dy + 115, 80, 30)
            cancel = pg.Rect(dx + 170, dy + 115, 80, 30)
            if wi.collidepoint(event.pos):
                self.resize_active_field = "width"
            elif hi.collidepoint(event.pos):
                self.resize_active_field = "height"
            elif ok.collidepoint(event.pos):
                try:
                    w = int(self.resize_width)
                    h = int(self.resize_height)
                    self.resize_map(w, h)
                    self.show_resize_dialog = False
                except ValueError:
                    pass
            elif cancel.collidepoint(event.pos):
                self.show_resize_dialog = False
        elif event.type == pg.KEYDOWN:
            if self.resize_active_field:
                if event.key == pg.K_BACKSPACE:
                    if self.resize_active_field == "width":
                        self.resize_width = self.resize_width[:-1]
                    else:
                        self.resize_height = self.resize_height[:-1]
                elif event.unicode.isdigit():
                    if self.resize_active_field == "width" and len(self.resize_width) < 3:
                        self.resize_width += event.unicode
                    elif self.resize_active_field == "height" and len(self.resize_height) < 3:
                        self.resize_height += event.unicode
                elif event.key == pg.K_RETURN:
                    try:
                        w = int(self.resize_width)
                        h = int(self.resize_height)
                        self.resize_map(w, h)
                        self.show_resize_dialog = False
                    except ValueError:
                        pass
                elif event.key == pg.K_ESCAPE:
                    self.show_resize_dialog = False
            else:
                if event.key == pg.K_RETURN:
                    try:
                        w = int(self.resize_width)
                        h = int(self.resize_height)
                        self.resize_map(w, h)
                        self.show_resize_dialog = False
                    except ValueError:
                        pass
                elif event.key == pg.K_ESCAPE:
                    self.show_resize_dialog = False

    def save_map_dialog(self):
        pg.event.clear()
        self.dialog_open = True
        filename = filedialog.asksaveasfilename(defaultextension=".map", filetypes=[("Map files", "*.map")], title="Сохранить карту", parent=self.tk_root)
        self.tk_root.update()
        if filename:
            self.save_map(filename)
        pg.event.clear()
        self.dialog_open = False

    def load_map_dialog(self):
        pg.event.clear()
        self.dialog_open = True
        filename = filedialog.askopenfilename(filetypes=[("Map files", "*.map")], title="Загрузить карту", parent=self.tk_root)
        self.tk_root.update()
        if filename:
            self.load_map(filename)
        pg.event.clear()
        self.dialog_open = False

    def ask_string_pygame(self, prompt, default=""):
        """Ввод строки через Pygame (замена simpledialog)"""
        input_text = default
        done = False
        clock = pg.time.Clock()
        font = pg.font.Font(None, 32)
        # Полупрозрачный фон
        overlay = pg.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        
        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    input_text = None
                    done = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        done = True
                    elif event.key == pg.K_ESCAPE:
                        input_text = None
                        done = True
                    elif event.key == pg.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pg.K_SPACE:
                        input_text += " "
                    elif event.unicode and event.unicode.isprintable():
                        input_text += event.unicode
            
            self.screen.blit(overlay, (0, 0))
            # Рамка окна
            dw, dh = 400, 120
            dx = (self.screen_width - dw)//2
            dy = (self.screen_height - dh)//2
            pg.draw.rect(self.screen, COLOR_UI_BG, (dx, dy, dw, dh), border_radius=10)
            pg.draw.rect(self.screen, COLOR_UI_BORDER, (dx, dy, dw, dh), 2, border_radius=10)
            # Подсказка
            prompt_surf = font.render(prompt, True, COLOR_TEXT)
            self.screen.blit(prompt_surf, (dx + 20, dy + 15))
            # Поле ввода
            input_rect = pg.Rect(dx + 20, dy + 45, dw - 40, 30)
            pg.draw.rect(self.screen, (200, 200, 200), input_rect)
            pg.draw.rect(self.screen, COLOR_UI_BORDER, input_rect, 1)
            # Текст
            text_surf = font.render(input_text, True, (0, 0, 0))
            self.screen.blit(text_surf, (input_rect.x + 5, input_rect.y + 3))
            # Мигающий курсор
            if int(pg.time.get_ticks() / 500) % 2 == 0:
                cursor_x = input_rect.x + 5 + text_surf.get_width()
                pg.draw.line(self.screen, (0, 0, 0),
                            (cursor_x, input_rect.y + 5),
                            (cursor_x, input_rect.y + 25), 2)
            # Подсказка клавиш
            hint = self.font_small.render("Enter - OK, Esc - отмена", True, (150, 150, 150))
            self.screen.blit(hint, (dx + 20, dy + 85))
            
            pg.display.flip()
            clock.tick(60)
        return input_text

    def run(self):
        running = True
        while running:
            if not self.handle_events():
                running = False
                break
            self.screen.fill(COLOR_BG)
            pg.draw.rect(self.screen, (30,34,42), (0,0, self.get_work_area_width(), self.screen_height))
            self.draw_grid()
            self.draw_tiles()
            self.draw_collisions()
            self.draw_entry_teleport_points()
            self.draw_selection()
            mp = pg.mouse.get_pos()
            if mp[0] < self.get_work_area_width():
                wx, wy = self.screen_to_world(*mp)
                if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                    sx, sy = self.world_to_screen(wx, wy)
                    if self.mode == "paint" and 0 <= self.selected_brush < len(self.brushes):
                        scaled = pg.transform.scale(self.brushes[self.selected_brush], (self.tile_size, self.tile_size))
                        self.screen.blit(scaled, (sx, sy))
                        pg.draw.rect(self.screen, COLOR_SELECTED, (sx, sy, self.tile_size, self.tile_size), 2)
                    elif self.mode == "collision":
                        s = pg.Surface((self.tile_size, self.tile_size), pg.SRCALPHA)
                        s.fill((255,0,0,100))
                        self.screen.blit(s, (sx, sy))
                        pg.draw.rect(self.screen, (255,0,0), (sx, sy, self.tile_size, self.tile_size), 2)
                    elif self.mode == "fill":
                        s = pg.Surface((self.tile_size, self.tile_size), pg.SRCALPHA)
                        s.fill(COLOR_FILL_PREVIEW)
                        self.screen.blit(s, (sx, sy))
                        pg.draw.rect(self.screen, (0,255,0), (sx, sy, self.tile_size, self.tile_size), 2)
                    elif self.mode == "entry_point":
                        pg.draw.rect(self.screen, COLOR_ENTRY_POINT, (sx+2, sy+2, self.tile_size-4, self.tile_size-4), 2)
                    elif self.mode == "teleport_point":
                        pg.draw.rect(self.screen, COLOR_TELEPORT_POINT, (sx+2, sy+2, self.tile_size-4, self.tile_size-4), 2)
            self.draw_ui()
            if self.show_new_map_dialog:
                self.draw_new_map_dialog()
            if self.show_resize_dialog:
                self.draw_resize_dialog()
            pg.display.flip()
            self.clock.tick(60)
        try:
            self.tk_root.destroy()
        except:
            pass
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    editor = MapEditor()
    editor.run()