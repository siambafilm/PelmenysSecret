import pygame as pg
import json
import sys
import os

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

# Вычисляем рабочую область
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
        
        # Флаг открытия диалога (чтобы не обрабатывать события Pygame)
        self.dialog_open = False
        
        # Режимы редактирования
        self.mode = "paint"  # "paint" или "collision"
        self.eraser_mode = False  # Режим ластика (ПКМ)
        
        # Настройки карты
        self.map_width_tiles = 20  # по умолчанию
        self.map_height_tiles = 15  # по умолчанию
        self.tile_size = TILE_SIZE
        
        # Камера
        self.camera_x = 0
        self.camera_y = 0
        self.dragging_camera = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Тайлсет для редактора (создаем программно)
        self.editor_tiles = self.create_editor_tiles()
        
        # Доступные тайлы (кисти)
        self.brushes = []
        self.load_brushes()
        self.selected_brush = 0
        
        # Данные карты
        self.tiles = []  # Список (x, y, brush_index)
        self.collisions = []  # Список (x, y, width, height)
        
        # UI состояние
        self.show_new_map_dialog = False
        self.new_map_width = "20"
        self.new_map_height = "15"
        
        # Скролл кистей
        self.brush_scroll_y = 0
        self.brush_area_height = 300  # Высота области кистей
        
        # Кнопки (позиции будут обновляться динамически)
        self.update_ui_rects()
        
        # Флаг для отключения кисти при наведении на UI
        self.mouse_over_ui = False
        
    def get_work_area_width(self):
        """Возвращает ширину рабочей области"""
        return self.screen_width - UI_PANEL_WIDTH
    
    def update_ui_rects(self):
        """Обновляет прямоугольники кнопок в зависимости от размера окна"""
        work_width = self.get_work_area_width()
        self.buttons = {
            "new": pg.Rect(work_width + 10, 50, 180, 30),
            "save": pg.Rect(work_width + 10, 90, 180, 30),
            "load": pg.Rect(work_width + 10, 130, 180, 30),
            "clear": pg.Rect(work_width + 10, 170, 180, 30),
            "mode_paint": pg.Rect(work_width + 10, 210, 180, 30),
            "mode_collision": pg.Rect(work_width + 10, 250, 180, 30),
        }
        
    def create_editor_tiles(self):
        """Создает тайлы для редактора программно"""
        tiles = []
        
        # Трава (зеленая)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((34, 139, 34))
        for i in range(0, TILE_SIZE, 4):
            pg.draw.line(surf, (25, 109, 25), (i, 0), (i, TILE_SIZE), 1)
        for i in range(0, TILE_SIZE, 4):
            pg.draw.line(surf, (25, 109, 25), (0, i), (TILE_SIZE, i), 1)
        tiles.append(surf)
        
        # Камень (серый)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((128, 128, 128))
        for i in range(0, TILE_SIZE, 3):
            pg.draw.line(surf, (100, 100, 100), (i, 0), (i, TILE_SIZE), 1)
        for i in range(0, TILE_SIZE, 3):
            pg.draw.line(surf, (100, 100, 100), (0, i), (TILE_SIZE, i), 1)
        tiles.append(surf)
        
        # Вода (синяя)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((64, 164, 223))
        for i in range(0, TILE_SIZE, 6):
            pg.draw.line(surf, (50, 140, 200), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        
        # Песок (желтый)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((237, 201, 175))
        for i in range(0, TILE_SIZE, 5):
            pg.draw.line(surf, (200, 170, 140), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        
        # Дерево (коричневый + зеленый)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
        pg.draw.rect(surf, (101, 67, 33), (TILE_SIZE//2 - 8, TILE_SIZE//2, 16, 24))
        pg.draw.circle(surf, (34, 139, 34), (TILE_SIZE//2, TILE_SIZE//2 - 5), 20)
        tiles.append(surf)
        
        # Камень (маленький)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
        pg.draw.ellipse(surf, (100, 100, 100), (TILE_SIZE//2 - 15, TILE_SIZE//2 - 10, 30, 20))
        tiles.append(surf)
        
        # Цветы
        surf = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
        surf.fill((34, 139, 34))
        colors = [(255, 100, 100), (255, 200, 100), (200, 100, 255), (100, 200, 255)]
        for i, color in enumerate(colors):
            x = 10 + (i % 2) * 25
            y = 10 + (i // 2) * 25
            pg.draw.circle(surf, color, (x, y), 6)
        tiles.append(surf)
        
        # Путь (серый)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((169, 169, 169))
        for i in range(0, TILE_SIZE, 4):
            pg.draw.line(surf, (150, 150, 150), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        
        # Темная трава
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((25, 80, 25))
        for i in range(0, TILE_SIZE, 4):
            pg.draw.line(surf, (20, 60, 20), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        
        # Лава (красная)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((200, 50, 50))
        for i in range(0, TILE_SIZE, 5):
            pg.draw.line(surf, (180, 30, 30), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        
        # Снег (белый)
        surf = pg.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((240, 240, 255))
        for i in range(0, TILE_SIZE, 6):
            pg.draw.line(surf, (220, 220, 240), (i, 0), (i, TILE_SIZE), 1)
        tiles.append(surf)
        
        return tiles
    
    def load_brushes(self):
        """Загружает доступные кисти (встроенные + кастомные)"""
        self.brushes = self.editor_tiles
        # Пытаемся загрузить кастомные тайлы из папки custom_tiles
        self.load_custom_tiles()
    
    def load_custom_tiles(self):
        """Загружает кастомные тайлы из папки custom_tiles (PNG/JPG, 64x64)"""
        custom_dir = "custom_tiles"
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir)
            print(f"Создана папка для кастомных тайлов: {custom_dir}/")
            print("Поместите туда свои тайлы (PNG/JPG, 64x64 пикселей)")
            return
        
        loaded_count = 0
        for filename in sorted(os.listdir(custom_dir)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                filepath = os.path.join(custom_dir, filename)
                try:
                    surf = pg.image.load(filepath).convert_alpha()
                    # Проверяем размер
                    w, h = surf.get_width(), surf.get_height()
                    if w != TILE_SIZE or h != TILE_SIZE:
                        print(f"  Предупреждение: {filename} имеет размер {w}x{h}, а не {TILE_SIZE}x{TILE_SIZE}")
                        print(f"  Масштабируем до {TILE_SIZE}x{TILE_SIZE}")
                        surf = pg.transform.scale(surf, (TILE_SIZE, TILE_SIZE))
                    self.brushes.append(surf)
                    print(f"✓ Загружен кастомный тайл: {filename} (ID: {len(self.brushes)-1})")
                    loaded_count += 1
                except Exception as e:
                    print(f"✗ Ошибка загрузки {filename}: {e}")
        
        if loaded_count > 0:
            print(f"\nЗагружено {loaded_count} кастомных тайлов")
        else:
            print(f"\nКастомные тайлы не найдены в папке '{custom_dir}/'")
            print("  Создайте папку и добавьте туда свои PNG/JPG файлы (64x64)")
    
    def new_map(self, width, height):
        """Создает новую карту"""
        self.map_width_tiles = max(5, min(100, width))
        self.map_height_tiles = max(5, min(100, height))
        self.tiles = []
        self.collisions = []
        self.camera_x = 0
        self.camera_y = 0
    
    def save_map(self, filename):
        """Сохраняет карту в файл .map"""
        data = {
            "version": "1.0",
            "width": self.map_width_tiles,
            "height": self.map_height_tiles,
            "tile_size": self.tile_size,
            "tiles": self.tiles,
            "collisions": self.collisions
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Карта сохранена: {filename}")
    
    def load_map(self, filename):
        """Загружает карту из файла .map"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            self.map_width_tiles = data.get("width", 20)
            self.map_height_tiles = data.get("height", 15)
            self.tile_size = data.get("tile_size", TILE_SIZE)
            self.tiles = data.get("tiles", [])
            self.collisions = data.get("collisions", [])
            self.camera_x = 0
            self.camera_y = 0
            print(f"Карта загружена: {filename} ({self.map_width_tiles}x{self.map_height_tiles})")
            return True
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")
            return False
    
    def get_tile_at(self, x, y):
        """Получает тайл по координатам"""
        for tx, ty, idx in self.tiles:
            if tx == x and ty == y:
                return idx
        return None
    
    def set_tile(self, x, y, brush_idx):
        """Устанавливает тайл"""
        # Удаляем старый тайл на этой позиции
        self.tiles = [(tx, ty, idx) for tx, ty, idx in self.tiles if not (tx == x and ty == y)]
        # Добавляем новый
        if brush_idx >= 0:
            self.tiles.append((x, y, brush_idx))
    
    def toggle_collision(self, x, y):
        """Переключает коллизию на тайле"""
        # Проверяем, есть ли уже коллизия
        for i, (cx, cy, cw, ch) in enumerate(self.collisions):
            if cx == x and cy == y:
                self.collisions.pop(i)
                return
        # Добавляем новую коллизию
        self.collisions.append((x, y, 1, 1))
    
    def screen_to_world(self, screen_x, screen_y):
        """Конвертирует экранные координаты в мировые"""
        world_x = (screen_x + self.camera_x) // self.tile_size
        world_y = (screen_y + self.camera_y) // self.tile_size
        return world_x, world_y
    
    def world_to_screen(self, world_x, world_y):
        """Конвертирует мировые координаты в экранные"""
        screen_x = world_x * self.tile_size - self.camera_x
        screen_y = world_y * self.tile_size - self.camera_y
        return screen_x, screen_y
    
    def draw_grid(self):
        """Рисует сетку рабочей области"""
        work_width = self.get_work_area_width()
        start_x = (self.camera_x // self.tile_size) * self.tile_size - self.camera_x
        start_y = (self.camera_y // self.tile_size) * self.tile_size - self.camera_y
        
        for x in range(int(start_x), work_width, self.tile_size):
            alpha = 50 if x % (self.tile_size * 5) != 0 else 100
            color = list(COLOR_GRID) + [alpha]
            if len(color) == 4:
                s = pg.Surface((1, self.screen_height))
                s.fill(color)
                self.screen.blit(s, (x, 0))
        
        for y in range(int(start_y), self.screen_height, self.tile_size):
            alpha = 50 if y % (self.tile_size * 5) != 0 else 100
            color = list(COLOR_GRID) + [alpha]
            if len(color) == 4:
                s = pg.Surface((work_width, 1))
                s.fill(color)
                self.screen.blit(s, (0, y))
    
    def draw_tiles(self):
        """Рисует все тайлы с учетом текущего масштаба"""
        # Вычисляем видимую область
        work_width = self.get_work_area_width()
        start_x = max(0, self.camera_x // self.tile_size)
        start_y = max(0, self.camera_y // self.tile_size)
        end_x = min(self.map_width_tiles, (self.camera_x + work_width) // self.tile_size + 1)
        end_y = min(self.map_height_tiles, (self.camera_y + self.screen_height) // self.tile_size + 1)
        
        # Рисуем тайлы
        for x, y, idx in self.tiles:
            if start_x <= x < end_x and start_y <= y < end_y:
                screen_x = x * self.tile_size - self.camera_x
                screen_y = y * self.tile_size - self.camera_y
                if 0 <= idx < len(self.brushes):
                    # Масштабируем кисть до текущего размера тайла
                    scaled_brush = pg.transform.scale(self.brushes[idx], (self.tile_size, self.tile_size))
                    self.screen.blit(scaled_brush, (screen_x, screen_y))
    
    def draw_collisions(self):
        """Рисует коллизии"""
        work_width = self.get_work_area_width()
        start_x = max(0, self.camera_x // self.tile_size)
        start_y = max(0, self.camera_y // self.tile_size)
        end_x = min(self.map_width_tiles, (self.camera_x + work_width) // self.tile_size + 1)
        end_y = min(self.map_height_tiles, (self.camera_y + self.screen_height) // self.tile_size + 1)
        
        for cx, cy, cw, ch in self.collisions:
            if start_x <= cx < end_x and start_y <= cy < end_y:
                screen_x = cx * self.tile_size - self.camera_x
                screen_y = cy * self.tile_size - self.camera_y
                # Полупрозрачный красный прямоугольник
                s = pg.Surface((cw * self.tile_size, ch * self.tile_size), pg.SRCALPHA)
                s.fill((255, 0, 0, 100))
                self.screen.blit(s, (screen_x, screen_y))
                # Контур
                pg.draw.rect(self.screen, (255, 0, 0),
                           (screen_x, screen_y, cw * self.tile_size, ch * self.tile_size), 1)
    
    def draw_ui(self):
        """Рисует интерфейс"""
        # Фон панели
        work_width = self.get_work_area_width()
        pg.draw.rect(self.screen, COLOR_UI_BG, (work_width, 0, UI_PANEL_WIDTH, self.screen_height))
        pg.draw.line(self.screen, COLOR_UI_BORDER, (work_width, 0), (work_width, self.screen_height), 2)
        
        # Заголовок
        title = self.font_title.render("Map Editor", True, COLOR_TEXT)
        self.screen.blit(title, (work_width + 10, 10))
        
        # Разделитель
        pg.draw.line(self.screen, COLOR_UI_BORDER, (work_width + 10, 45), (self.screen_width - 10, 45), 1)
        
        # Кнопки
        mouse_pos = pg.mouse.get_pos()
        for name, rect in self.buttons.items():
            hover = rect.collidepoint(mouse_pos)
            color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
            pg.draw.rect(self.screen, color, rect, border_radius=5)
            pg.draw.rect(self.screen, COLOR_UI_BORDER, rect, 2, border_radius=5)
            
            # Текст кнопки
            text_map = {
                "new": "Новая карта",
                "save": "Сохранить",
                "load": "Загрузить",
                "clear": "Очистить",
                "mode_paint": "Режим: Кисть",
                "mode_collision": "Режим: Коллизия"
            }
            text = self.font_small.render(text_map[name], True, COLOR_TEXT)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Индикатор режима
        mode_text = "Режим: Рисование" if self.mode == "paint" else "Режим: Коллизия"
        mode_color = (100, 255, 100) if self.mode == "paint" else (255, 100, 100)
        mode_surf = self.font.render(mode_text, True, mode_color)
        work_width = self.get_work_area_width()
        self.screen.blit(mode_surf, (work_width + 10, 310))
        
        # Разделитель
        work_width = self.get_work_area_width()
        pg.draw.line(self.screen, COLOR_UI_BORDER, (work_width + 10, 340), (self.screen_width - 10, 340), 1)
        
        # Заголовок кистей
        work_width = self.get_work_area_width()
        brushes_title = self.font.render("Кисти (64x64):", True, COLOR_TEXT)
        self.screen.blit(brushes_title, (work_width + 10, 350))
        
        # Кисти с прокруткой
        work_width = self.get_work_area_width()
        brush_start_y = 380
        # Ограничиваем scroll
        max_scroll = max(0, len(self.brushes) // 2 * 70 - self.brush_area_height)
        self.brush_scroll_y = max(0, min(self.brush_scroll_y, max_scroll))
        
        for i, brush in enumerate(self.brushes):
            x = work_width + 10 + (i % 2) * 85
            y = brush_start_y + (i // 2) * 70 - self.brush_scroll_y
            
            # Пропускаем кисти, которые не видны
            if y + TILE_SIZE < brush_start_y or y > brush_start_y + self.brush_area_height:
                continue
            
            # Рамка
            border_color = COLOR_SELECTED if i == self.selected_brush else COLOR_UI_BORDER
            pg.draw.rect(self.screen, border_color, (x - 2, y - 2, TILE_SIZE + 4, TILE_SIZE + 4), 2, border_radius=3)
            
            # Сам тайл
            scaled = pg.transform.scale(brush, (TILE_SIZE, TILE_SIZE))
            self.screen.blit(scaled, (x, y))
            
            # Номер
            num_text = self.font_small.render(str(i), True, COLOR_TEXT)
            self.screen.blit(num_text, (x + 2, y + TILE_SIZE + 5))
        
        # Статус
        work_width = self.get_work_area_width()
        status_y = self.screen_height - 60
        pg.draw.line(self.screen, COLOR_UI_BORDER, (work_width + 10, status_y - 10), (self.screen_width - 10, status_y - 10), 1)
        
        status_text = f"Карта: {self.map_width_tiles}x{self.map_height_tiles} | Тайлов: {len(self.tiles)} | Коллизий: {len(self.collisions)} | Кистей: {len(self.brushes)}"
        status_surf = self.font_small.render(status_text, True, COLOR_TEXT)
        self.screen.blit(status_surf, (work_width + 10, status_y))
        
        # Подсказка
        work_width = self.get_work_area_width()
        hint_text = "СКМ - камера | ПКМ - ластик | Колесо - масштаб/прокрутка кистей | Пробел - режим"
        hint_surf = self.font_small.render(hint_text, True, (150, 150, 150))
        self.screen.blit(hint_surf, (work_width + 10, self.screen_height - 25))
    
    def draw_new_map_dialog(self):
        """Рисует диалог создания новой карты"""
        overlay = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        dialog_w, dialog_h = 300, 150
        dialog_x = (self.screen_width - dialog_w) // 2
        dialog_y = (self.screen_height - dialog_h) // 2
        
        pg.draw.rect(self.screen, COLOR_UI_BG, (dialog_x, dialog_y, dialog_w, dialog_h), border_radius=10)
        pg.draw.rect(self.screen, COLOR_UI_BORDER, (dialog_x, dialog_y, dialog_w, dialog_h), 2, border_radius=10)
        
        title = self.font_title.render("Новая карта", True, COLOR_TEXT)
        self.screen.blit(title, (dialog_x + (dialog_w - title.get_width()) // 2, dialog_y + 15))
        
        # Поля ввода
        width_label = self.font.render("Ширина (5-100):", True, COLOR_TEXT)
        self.screen.blit(width_label, (dialog_x + 20, dialog_y + 55))
        
        height_label = self.font.render("Высота (5-100):", True, COLOR_TEXT)
        self.screen.blit(height_label, (dialog_x + 20, dialog_y + 90))
        
        # Кнопки
        ok_rect = pg.Rect(dialog_x + 50, dialog_y + 115, 80, 30)
        cancel_rect = pg.Rect(dialog_x + 170, dialog_y + 115, 80, 30)
        
        mouse_pos = pg.mouse.get_pos()
        
        for rect, text, color in [(ok_rect, "OK", COLOR_BUTTON), (cancel_rect, "Отмена", (100, 100, 100))]:
            hover = rect.collidepoint(mouse_pos)
            btn_color = color if hover else tuple(c - 30 for c in color)
            pg.draw.rect(self.screen, btn_color, rect, border_radius=5)
            pg.draw.rect(self.screen, COLOR_UI_BORDER, rect, 2, border_radius=5)
            btn_text = self.font_small.render(text, True, COLOR_TEXT)
            self.screen.blit(btn_text, (rect.x + (rect.width - btn_text.get_width()) // 2,
                                       rect.y + (rect.height - btn_text.get_height()) // 2))
        
        return ok_rect, cancel_rect
    
    def handle_events(self):
        """Обработка событий - returns True to continue, False to quit"""
        # Если открыт диалог, пропускаем события Pygame
        if self.dialog_open:
            pg.event.clear()  # Очищаем очередь событий
            return True
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            if event.type == pg.VIDEORESIZE:
                # Обработка изменения размера окна
                self.screen_width = max(event.w, 800)
                self.screen_height = max(event.h, 600)
                self.screen = pg.display.set_mode((self.screen_width, self.screen_height), pg.RESIZABLE)
                self.update_ui_rects()
            
            if self.show_new_map_dialog:
                self.handle_new_map_dialog(event)
                continue
            
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка
                    if event.pos[0] < self.get_work_area_width():
                        # Рабочая область
                        if self.mode == "paint":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                                self.set_tile(wx, wy, self.selected_brush)
                        elif self.mode == "collision":
                            wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                            if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                                self.toggle_collision(wx, wy)
                    else:
                        # Проверка кнопок
                        button_clicked = False
                        for name, rect in self.buttons.items():
                            if rect.collidepoint(event.pos):
                                self.handle_button(name)
                                button_clicked = True
                                break
                        # Если кликнули по кнопке, не проверяем кисти
                        if not button_clicked:
                            # Проверка кистей
                            work_width = self.get_work_area_width()
                            brush_start_y = 380
                            for i in range(len(self.brushes)):
                                x = work_width + 10 + (i % 2) * 85
                                y = brush_start_y + (i // 2) * 70 - self.brush_scroll_y
                                rect = pg.Rect(x - 2, y - 2, TILE_SIZE + 4, TILE_SIZE + 4)
                                if rect.collidepoint(event.pos):
                                    self.selected_brush = i
                                    break
                
                elif event.button == 2:  # Средняя кнопка - перетаскивание камеры
                    self.dragging_camera = True
                    self.drag_start_x = event.pos[0]
                    self.drag_start_y = event.pos[1]
                elif event.button == 3:  # Правая кнопка - стирание в режиме рисования
                    if self.mode == "paint" and event.pos[0] < self.get_work_area_width():
                        wx, wy = self.screen_to_world(event.pos[0], event.pos[1])
                        if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                            self.set_tile(wx, wy, -1)  # -1 означает удаление тайла
                
                elif event.button == 4:  # Скролл вверх
                    # Если мышь над областью кистей, скроллим кисти, иначе масштаб
                    mouse_x, mouse_y = event.pos if hasattr(event, 'pos') else pg.mouse.get_pos()
                    work_width = self.get_work_area_width()
                    if (work_width + 10 <= mouse_x <= work_width + UI_PANEL_WIDTH - 10 and
                        380 <= mouse_y <= 380 + self.brush_area_height):
                        self.brush_scroll_y = max(0, self.brush_scroll_y - 70)
                    else:
                        self.tile_size = min(128, self.tile_size + 8)
                
                elif event.button == 5:  # Скролл вниз
                    mouse_x, mouse_y = event.pos if hasattr(event, 'pos') else pg.mouse.get_pos()
                    work_width = self.get_work_area_width()
                    if (work_width + 10 <= mouse_x <= work_width + UI_PANEL_WIDTH - 10 and
                        380 <= mouse_y <= 380 + self.brush_area_height):
                        max_scroll = max(0, len(self.brushes) // 2 * 70 - self.brush_area_height)
                        self.brush_scroll_y = min(max_scroll, self.brush_scroll_y + 70)
                    else:
                        self.tile_size = max(32, self.tile_size - 8)
            
            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 2:  # Средняя кнопка - камера
                    self.dragging_camera = False
                elif event.button == 3:  # Правая кнопка - ничего не делаем при отпускании
                    pass
            
            elif event.type == pg.MOUSEMOTION:
                if self.dragging_camera:
                    dx = event.pos[0] - self.drag_start_x
                    dy = event.pos[1] - self.drag_start_y
                    self.camera_x = max(0, self.camera_x - dx)
                    self.camera_y = max(0, self.camera_y - dy)
                    self.drag_start_x = event.pos[0]
                    self.drag_start_y = event.pos[1]
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.mode = "collision" if self.mode == "paint" else "paint"
                elif event.key == pg.K_ESCAPE:
                    if self.show_new_map_dialog:
                        self.show_new_map_dialog = False
                    else:
                        return False
        
        return True  # Continue running
    
    def handle_button(self, name):
        """Обработка нажатия кнопок"""
        if name == "new":
            self.show_new_map_dialog = True
            self.new_map_width = str(self.map_width_tiles)
            self.new_map_height = str(self.map_height_tiles)
        elif name == "save":
            self.save_map_dialog()
        elif name == "load":
            self.load_map_dialog()
        elif name == "clear":
            self.tiles = []
            self.collisions = []
        elif name == "mode_paint":
            self.mode = "paint"
        elif name == "mode_collision":
            self.mode = "collision"
    
    def handle_new_map_dialog(self, event):
        """Обработка событий диалога новой карты"""
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            dialog_w, dialog_h = 300, 150
            dialog_x = (self.screen_width - dialog_w) // 2
            dialog_y = (self.screen_height - dialog_h) // 2
            
            ok_rect = pg.Rect(dialog_x + 50, dialog_y + 115, 80, 30)
            cancel_rect = pg.Rect(dialog_x + 170, dialog_y + 115, 80, 30)
            
            if ok_rect.collidepoint(event.pos):
                try:
                    w = int(self.new_map_width)
                    h = int(self.new_map_height)
                    self.new_map(w, h)
                    self.show_new_map_dialog = False
                except ValueError:
                    pass
            elif cancel_rect.collidepoint(event.pos):
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
    
    def save_map_dialog(self):
        """Диалог сохранения карты"""
        # Очищаем очередь событий Pygame перед открытием диалога
        pg.event.clear()
        
        self.dialog_open = True
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        # Поднимаем диалог на передний план
        root.lift()
        root.attributes('-topmost', True)
        root.focus_force()
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".map",
            filetypes=[("Map files", "*.map"), ("All files", "*.*")],
            title="Сохранить карту"
        )
        
        if filename:
            self.save_map(filename)
        
        root.destroy()
        
        # Очищаем очередь событий Pygame после закрытия диалога
        pg.event.clear()
        self.dialog_open = False
    
    def load_map_dialog(self):
        """Диалог загрузки карты"""
        # Очищаем очередь событий Pygame перед открытием диалога
        pg.event.clear()
        
        self.dialog_open = True
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        # Поднимаем диалог на передний план
        root.lift()
        root.attributes('-topmost', True)
        root.focus_force()
        
        filename = filedialog.askopenfilename(
            filetypes=[("Map files", "*.map"), ("All files", "*.*")],
            title="Загрузить карту"
        )
        
        if filename:
            self.load_map(filename)
        
        root.destroy()
        
        # Очищаем очередь событий Pygame после закрытия диалога
        pg.event.clear()
        self.dialog_open = False
    
    def run(self):
        """Основной цикл редактора"""
        running = True
        while running:
            # handle_events() returns True to continue, False to quit
            if self.handle_events() == False:
                running = False
                break
            
            # Отрисовка
            self.screen.fill(COLOR_BG)
            
            # Рабочая область
            work_width = self.get_work_area_width()
            work_area = pg.Rect(0, 0, work_width, self.screen_height)
            pg.draw.rect(self.screen, (30, 34, 42), work_area)
            
            self.draw_grid()
            self.draw_tiles()
            self.draw_collisions()
            
            # Курсор
            if pg.mouse.get_pos()[0] < work_width:
                wx, wy = self.screen_to_world(*pg.mouse.get_pos())
                if 0 <= wx < self.map_width_tiles and 0 <= wy < self.map_height_tiles:
                    sx, sy = self.world_to_screen(wx, wy)
                    if self.mode == "paint":
                        if 0 <= self.selected_brush < len(self.brushes):
                            brush_scaled = pg.transform.scale(self.brushes[self.selected_brush], (TILE_SIZE, TILE_SIZE))
                            self.screen.blit(brush_scaled, (sx, sy))
                        pg.draw.rect(self.screen, COLOR_SELECTED, (sx, sy, TILE_SIZE, TILE_SIZE), 2)
                    elif self.mode == "collision":
                        s = pg.Surface((TILE_SIZE, TILE_SIZE), pg.SRCALPHA)
                        s.fill((255, 0, 0, 100))
                        self.screen.blit(s, (sx, sy))
                        pg.draw.rect(self.screen, (255, 0, 0), (sx, sy, TILE_SIZE, TILE_SIZE), 2)
            
            self.draw_ui()
            
            if self.show_new_map_dialog:
                self.draw_new_map_dialog()
            
            pg.display.flip()
            self.clock.tick(60)
        
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    editor = MapEditor()
    editor.run()
