import pygame as pg
import os
from scene import Scene
from char import Char
from map_system import TileMap, Camera

class GameScene(Scene):
    """Игровая сцена с персонажем и тайловой картой"""
    
    def __init__(self, screen, load_save=False, map_file=None):
        super().__init__(screen)
        self.load_save = load_save
        self.map_file = map_file
        
        # Константы для сцены
        self.SCREEN_WIDTH = screen.get_width()
        self.SCREEN_HEIGHT = screen.get_height()
        self.FPS = 60
        
        # Параметры
        self.cur_w = screen.get_width()
        self.cur_h = screen.get_height()
        
        # Состояния
        self.escape_pressed = False
        self.pause_opened = False
        self.show_info = True
        
        # Загрузка карты
        self.tile_map = TileMap(tile_size=64)
        if map_file and os.path.exists(map_file):
            self.tile_map.load_from_file(map_file)
        else:
            # Создаем тестовую карту по умолчанию
            self._create_default_map()
        
        # Камера
        self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # Создание персонажа (в центре карты)
        spawn_x = (self.tile_map.width * self.tile_map.tile_size) // 2 - 32
        spawn_y = (self.tile_map.height * self.tile_map.tile_size) // 2 - 32
        
        self.character = Char(
            x=spawn_x,
            y=spawn_y,
            walk_sprite_path="pics/main_person/pers.png",
            idle_sprite_path="pics/main_person/idle.png"
        )
        # Initialize camera to follow the character
        self.camera.follow(self.character.x + self.character.frame_width // 2,
                            self.character.y + self.character.frame_height // 2)
        
        # Диалоговая система
        self.dialog_system = None
        
        # Флаги
        self.show_collisions = False
        
        # Отступы для хитбокса (подберите под свой спрайт)
        self.hitbox_offset_x = 12      # Отступ слева и справа
        self.hitbox_offset_y = 120      # Отступ сверху
        self.hitbox_offset_bottom = 8  # Отступ снизу
    
    def _create_default_map(self):
        """Создает тестовую карту по умолчанию"""
        self.tile_map.width = 30
        self.tile_map.height = 20
        self.tile_map.tile_size = 64
        
        # Заполняем травой
        for y in range(self.tile_map.height):
            for x in range(self.tile_map.width):
                self.tile_map.tiles.append((x, y, 0))  # Трава
        
        # Добавляем препятствия (камни, деревья)
        obstacles = [
            (5, 5, 1), (6, 5, 1), (7, 5, 1),  # Камни
            (10, 8, 4),  # Дерево
            (15, 10, 5),  # Камень
            (20, 15, 4),  # Дерево
            (25, 5, 1), (26, 5, 1),  # Камни
        ]
        for x, y, tile_type in obstacles:
            # Заменяем траву на препятствие
            self.tile_map.tiles = [(tx, ty, tt) for tx, ty, tt in self.tile_map.tiles 
                                   if not (tx == x and ty == y)]
            self.tile_map.tiles.append((x, y, tile_type))
            # Добавляем коллизию для препятствий
            if tile_type in [1, 4, 5]:  # Камень или дерево
                self.tile_map.collisions.append((x, y, 1, 1))
        
        # Добавляем воду
        for x in range(12, 18):
            for y in range(3, 7):
                self.tile_map.tiles = [(tx, ty, tt) for tx, ty, tt in self.tile_map.tiles 
                                       if not (tx == x and ty == y)]
                self.tile_map.tiles.append((x, y, 2))  # Вода
                self.tile_map.collisions.append((x, y, 1, 1))
    
    def _get_collision_rect(self):
        """
        Возвращает прямоугольник для проверки коллизий.
        Персонаж визуально 64x64, но для коллизий используем меньший размер.
        """
        collision_width = self.character.frame_width - self.hitbox_offset_x * 2
        collision_height = self.character.frame_height - self.hitbox_offset_y - self.hitbox_offset_bottom
        
        return pg.Rect(
            self.character.x + self.hitbox_offset_x,
            self.character.y + self.hitbox_offset_y,
            collision_width,
            collision_height
        )
    
    def _get_collision_rect_at_position(self, x, y):
        """
        Возвращает прямоугольник коллизий в заданной позиции.
        """
        collision_width = self.character.frame_width - self.hitbox_offset_x * 2
        collision_height = self.character.frame_height - self.hitbox_offset_y - self.hitbox_offset_bottom
        
        return pg.Rect(
            x + self.hitbox_offset_x,
            y + self.hitbox_offset_y,
            collision_width,
            collision_height
        )
    
    def _has_collision_at_rect(self, rect):
        """
        Проверяет, есть ли коллизия с тайлами для данного прямоугольника.
        """
        left_tile = int(rect.left // self.tile_map.tile_size)
        right_tile = int(rect.right // self.tile_map.tile_size)
        top_tile = int(rect.top // self.tile_map.tile_size)
        bottom_tile = int(rect.bottom // self.tile_map.tile_size)
        
        for tile_y in range(top_tile, bottom_tile + 1):
            for tile_x in range(left_tile, right_tile + 1):
                if self.tile_map.is_collision(tile_x, tile_y):
                    return True
        return False
    
    def _has_collision_at_position(self, x, y):
        """
        Проверяет, есть ли коллизия в позиции (x, y) персонажа.
        """
        rect = self._get_collision_rect_at_position(x, y)
        return self._has_collision_at_rect(rect)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pg.QUIT:
                self.running = False
                self.next_scene = "QUIT"
            
            elif event.type == pg.VIDEORESIZE:
                self.cur_w = max(event.w, 800)
                self.cur_h = max(event.h, 600)
                self.screen = pg.display.set_mode((self.cur_w, self.cur_h), pg.RESIZABLE)
                self.camera.screen_width = self.cur_w
                self.camera.screen_height = self.cur_h
                # Обновляем позицию персонажа при изменении размера окна
                if hasattr(self, 'character'):
                    self.character.x = min(self.character.x, self.tile_map.width * self.tile_map.tile_size - self.character.frame_width)
                    self.character.y = min(self.character.y, self.tile_map.height * self.tile_map.tile_size - self.character.frame_height)
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.escape_pressed = True
                if event.key == pg.K_h:
                    self.show_info = not self.show_info
                if event.key == pg.K_c:
                    self.show_collisions = not self.show_collisions
            
            elif event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:
                    self.escape_pressed = False
    
    def update(self):
        # Если открыто меню паузы - не обновляем игру
        if self.pause_opened:
            return
        
        # Обработка паузы
        if self.escape_pressed:
            if not hasattr(self, 'dialog_system') or not self.dialog_system or not self.dialog_system.is_active():
                self.pause_opened = True
                from pause_menu import PauseMenu
                pause_menu = PauseMenu(self.screen, self)
                self.next_scene = pause_menu
                self.escape_pressed = False
                return
        
        # Сохраняем старую позицию для проверки коллизий
        old_x, old_y = self.character.x, self.character.y
        
        # Обновление персонажа
        self.character.handle_input()
        self.character.update_movement(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.character.update_animation(self.FPS)
        
        # --- ПОЛНАЯ БЛОКИРОВКА КОЛЛИЗИЙ СО ВСЕХ СТОРОН ---
        
        # Проверяем горизонтальное движение
        if self._has_collision_at_position(self.character.x, self.character.y):
            self.character.x = old_x
        
        # Проверяем вертикальное движение
        if self._has_collision_at_position(self.character.x, self.character.y):
            self.character.y = old_y
        
        # Обновляем камеру
        self.camera.follow(
            self.character.x + self.character.frame_width // 2,
            self.character.y + self.character.frame_height // 2
        )
        self.camera.update(self.tile_map.width * self.tile_map.tile_size,
                            self.tile_map.height * self.tile_map.tile_size)
    
    def draw(self):
        # Заполнение экрана одним цветом
        self.screen.fill((0, 0, 0))
        # Отрисовка карты
        self.tile_map.draw(self.screen, self.camera.x, self.camera.y)
        
        # Отрисовка персонажа
        screen_x = self.character.x - self.camera.x
        screen_y = self.character.y - self.camera.y
        # Draw character at screen coordinates
        self.screen.blit(self.character.animations[self.character.current_animation][self.character.current_frame], (screen_x, screen_y))
        
        # Отладочная отрисовка коллизий
        if self.show_collisions:
            # Рисуем хитбокс персонажа (зеленый)
            collision_rect = self._get_collision_rect()
            screen_cx = collision_rect.x - self.camera.x
            screen_cy = collision_rect.y - self.camera.y
            pg.draw.rect(self.screen, (0, 255, 0), 
                        (screen_cx, screen_cy, collision_rect.width, collision_rect.height), 2)
            
            # Рисуем коллизии тайлов (красные)
            for cx, cy, cw, ch in self.tile_map.collisions:
                screen_cx = cx * self.tile_map.tile_size - self.camera.x
                screen_cy = cy * self.tile_map.tile_size - self.camera.y
                s = pg.Surface((cw * self.tile_map.tile_size, ch * self.tile_map.tile_size), pg.SRCALPHA)
                s.fill((255, 0, 0, 100))
                self.screen.blit(s, (screen_cx, screen_cy))
                pg.draw.rect(self.screen, (255, 0, 0), 
                           (screen_cx, screen_cy, cw * self.tile_map.tile_size, ch * self.tile_map.tile_size), 1)
        
        # Информация на экране
        if self.show_info:
            font_small = pg.font.Font(None, 20)
            
            direction_text = {
                "idle": "IDLE (Стояние)",
                "down": "Вниз ↓",
                "up": "Вверх ↑",
                "left": "Влево ←",
                "right": "Вправо →"
            }
            
            current_action = direction_text.get(self.character.current_animation, "UNKNOWN")
            frames_count = len(self.character.animations.get(self.character.current_animation, []))
            
            # Фон для текста
            text_bg = pg.Surface((320, 260))
            text_bg.set_alpha(200)
            text_bg.fill((0, 0, 0))
            self.screen.blit(text_bg, (5, 5))
            
            info_lines = [
                f"Анимация: {current_action}",
                f"Кадр: {self.character.current_frame + 1}/{frames_count}",
                f"Позиция: ({int(self.character.x)}, {int(self.character.y)})",
                f"Камера: ({int(self.camera.x)}, {int(self.camera.y)})",
                f"Карта: {self.tile_map.width}x{self.tile_map.height}",
                f"Коллизий: {len(self.tile_map.collisions)}",
                f"Хитбокс: {self.hitbox_offset_x},{self.hitbox_offset_y}",
                "",
                "Управление:",
                "Стрелки/WASD - движение",
                "C - показать коллизии",
                "H - скрыть информацию",
                "ESC - меню"
            ]
            
            for i, line in enumerate(info_lines):
                if line == "":
                    continue
                color = (200, 200, 100) if "Управление:" in line else (255, 255, 255)
                text_surface = font_small.render(line, True, color)
                self.screen.blit(text_surface, (10, 10 + i * 20))
    
    def resume(self):
        """Возврат из меню паузы"""
        self.pause_opened = False
        self.escape_pressed = False