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

        self.SCREEN_WIDTH = screen.get_width()
        self.SCREEN_HEIGHT = screen.get_height()
        self.FPS = 60

        self.cur_w = screen.get_width()
        self.cur_h = screen.get_height()

        self.escape_pressed = False
        self.pause_opened = False
        self.show_info = True

        # Состояния для телепорта
        self.e_pressed = False
        self.teleporting = False
        self.fade_alpha = 0
        self.transition_state = None
        self.target_teleport_map = None
        self.fade_surface = pg.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.fade_surface.fill((0, 0, 0))

        # Загрузка карты
        self.tile_map = TileMap(tile_size=64)
        self.load_map(map_file)

        # Камера
        self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # Персонаж (начальное положение будет скорректировано ниже)
        spawn_x = (self.tile_map.width * self.tile_map.tile_size) // 2 - 32
        spawn_y = (self.tile_map.height * self.tile_map.tile_size) // 2 - 32
        self.character = Char(
            spawn_x, spawn_y,
            walk_sprite_path="pics/main_person/pers.png",
            idle_sprite_path="pics/main_person/idle.png"
        )

        # Если есть точка входа, перемещаем персонажа
        if self.tile_map.entry_point:
            spawn_x = (self.tile_map.entry_point[0] * self.tile_map.tile_size +
                       self.tile_map.tile_size // 2 - self.character.frame_width // 2)
            spawn_y = (self.tile_map.entry_point[1] * self.tile_map.tile_size +
                       self.tile_map.tile_size // 2 - self.character.frame_height // 2)
            self.character.x = spawn_x
            self.character.y = spawn_y

        self.camera.follow(self.character.x + self.character.frame_width // 2,
                           self.character.y + self.character.frame_height // 2)

        self.dialog_system = None
        self.show_collisions = False
        self.hitbox_offset_x = self.character.frame_width // 4
        self.hitbox_offset_y = self.character.frame_height // 2
        self.hitbox_offset_bottom = 4

    def load_map(self, map_file):
        """Загружает карту из файла и обновляет ссылки"""
        self.tile_map = TileMap(tile_size=64)
        if map_file and os.path.exists(map_file):
            self.tile_map.load_from_file(map_file)
        else:
            # Попытка загрузить test.map
            test_map = "Maps/test.map"
            if os.path.exists(test_map):
                self.tile_map.load_from_file(test_map)
            else:
                self._create_default_map()
        # Создаём/перенастраиваем камеру
        if not hasattr(self, 'camera'):
            self.camera = Camera(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

    def _create_default_map(self):
        # та же функция, что и раньше (не менялась)
        self.tile_map.width = 30
        self.tile_map.height = 20
        self.tile_map.tile_size = 64
        self.tile_map.tiles = []
        self.tile_map.collisions = []
        for y in range(self.tile_map.height):
            for x in range(self.tile_map.width):
                self.tile_map.tiles.append((x, y, 0))
        obstacles = [(5,5,1),(6,5,1),(7,5,1),(10,8,4),(15,10,5),(20,15,4),(25,5,1),(26,5,1)]
        for x,y,t in obstacles:
            self.tile_map.tiles = [(tx,ty,tt) for tx,ty,tt in self.tile_map.tiles if not (tx==x and ty==y)]
            self.tile_map.tiles.append((x,y,t))
            if t in [1,4,5]:
                self.tile_map.collisions.append((x,y,1,1))
        for x in range(12,18):
            for y in range(3,7):
                self.tile_map.tiles = [(tx,ty,tt) for tx,ty,tt in self.tile_map.tiles if not (tx==x and ty==y)]
                self.tile_map.tiles.append((x,y,2))
                self.tile_map.collisions.append((x,y,1,1))

    def _get_collision_rect(self):
        cw = self.character.frame_width - self.hitbox_offset_x * 2
        ch = self.character.frame_height - self.hitbox_offset_y - self.hitbox_offset_bottom
        return pg.Rect(self.character.x + self.hitbox_offset_x,
                       self.character.y + self.hitbox_offset_y, cw, ch)

    def _get_collision_rect_at_position(self, x, y):
        cw = self.character.frame_width - self.hitbox_offset_x * 2
        ch = self.character.frame_height - self.hitbox_offset_y - self.hitbox_offset_bottom
        return pg.Rect(x + self.hitbox_offset_x, y + self.hitbox_offset_y, cw, ch)

    def _has_collision_at_rect(self, rect):
        lt = int(rect.left // self.tile_map.tile_size)
        rt = int(rect.right // self.tile_map.tile_size)
        tt = int(rect.top // self.tile_map.tile_size)
        bt = int(rect.bottom // self.tile_map.tile_size)
        for y in range(tt, bt+1):
            for x in range(lt, rt+1):
                if self.tile_map.is_collision(x, y):
                    return True
        return False

    def _has_collision_at_position(self, x, y):
        rect = self._get_collision_rect_at_position(x, y)
        return self._has_collision_at_rect(rect)

    def start_teleport(self, target_map):
        self.teleporting = True
        self.target_teleport_map = target_map
        self.transition_state = "fade_out"
        self.fade_alpha = 0

    def update_transition(self):
        if self.transition_state == "fade_out":
            self.fade_alpha += 5
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.transition_state = "load"
                # Загружаем карту
                map_path = os.path.join("Maps", self.target_teleport_map + ".map")
                self.load_map(map_path)
                # Перемещаем персонажа на entry_point или центр
                if self.tile_map.entry_point:
                    self.character.x = (self.tile_map.entry_point[0] * self.tile_map.tile_size +
                                        self.tile_map.tile_size // 2 - self.character.frame_width // 2)
                    self.character.y = (self.tile_map.entry_point[1] * self.tile_map.tile_size +
                                        self.tile_map.tile_size // 2 - self.character.frame_height // 2)
                else:
                    self.character.x = (self.tile_map.width * self.tile_map.tile_size) // 2 - 32
                    self.character.y = (self.tile_map.height * self.tile_map.tile_size) // 2 - 32
                self.fade_alpha = 255
                self.transition_state = "fade_in"
        elif self.transition_state == "fade_in":
            self.fade_alpha -= 5
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.teleporting = False
                self.transition_state = None
                self.target_teleport_map = None

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
                map_w = self.tile_map.width * self.tile_map.tile_size
                map_h = self.tile_map.height * self.tile_map.tile_size
                hitbox_w = self.character.frame_width - self.hitbox_offset_x * 2
                hitbox_h = self.character.frame_height - self.hitbox_offset_y - self.hitbox_offset_bottom
                min_x = -self.hitbox_offset_x
                max_x = map_w - self.hitbox_offset_x - hitbox_w
                min_y = -self.hitbox_offset_y
                max_y = map_h - self.hitbox_offset_y - hitbox_h
                self.character.x = max(min_x, min(self.character.x, max_x))
                self.character.y = max(min_y, min(self.character.y, max_y))
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.escape_pressed = True
                if event.key == pg.K_e:
                    self.e_pressed = True
                if event.key == pg.K_h:
                    self.show_info = not self.show_info
                if event.key == pg.K_c:
                    self.show_collisions = not self.show_collisions
            elif event.type == pg.KEYUP:
                if event.key == pg.K_ESCAPE:
                    self.escape_pressed = False
                if event.key == pg.K_e:
                    self.e_pressed = False

    def update(self):
        if self.pause_opened or self.teleporting:
            if self.teleporting:
                self.update_transition()
            return

        if self.escape_pressed:
            if not self.dialog_system or not self.dialog_system.is_active():
                self.pause_opened = True
                from pause_menu import PauseMenu
                self.next_scene = PauseMenu(self.screen, self)
                self.escape_pressed = False
                return

        old_x, old_y = self.character.x, self.character.y
        self.character.handle_input()
        self.character.update_movement(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.character.update_animation(self.FPS)

        if self._has_collision_at_position(self.character.x, self.character.y):
            self.character.x = old_x
        if self._has_collision_at_position(self.character.x, self.character.y):
            self.character.y = old_y

        map_w = self.tile_map.width * self.tile_map.tile_size
        map_h = self.tile_map.height * self.tile_map.tile_size
        hbw = self.character.frame_width - self.hitbox_offset_x * 2
        hbh = self.character.frame_height - self.hitbox_offset_y - self.hitbox_offset_bottom
        self.character.x = max(-self.hitbox_offset_x, min(self.character.x, map_w - self.hitbox_offset_x - hbw))
        self.character.y = max(-self.hitbox_offset_y, min(self.character.y, map_h - self.hitbox_offset_y - hbh))

        self.camera.follow(self.character.x + self.character.frame_width // 2,
                           self.character.y + self.character.frame_height // 2)
        self.camera.update(map_w, map_h)

        # Проверка телепортов
        if self.e_pressed and not self.teleporting:
            ch_cx = self.character.x + self.character.frame_width // 2
            ch_cy = self.character.y + self.character.frame_height // 2
            tile_x = int(ch_cx // self.tile_map.tile_size)
            tile_y = int(ch_cy // self.tile_map.tile_size)
            for tp in self.tile_map.teleport_points:
                if tp["x"] == tile_x and tp["y"] == tile_y:
                    self.start_teleport(tp["target_map"])
                    break

    def draw(self):
        self.screen.fill((0,0,0))
        self.tile_map.draw(self.screen, self.camera.x, self.camera.y)
        screen_x = self.character.x - self.camera.x
        screen_y = self.character.y - self.camera.y
        anim = self.character.animations[self.character.current_animation]
        self.screen.blit(anim[self.character.current_frame], (screen_x, screen_y))
        self.tile_map.draw_overlay(self.screen, self.camera.x, self.camera.y)

        if self.show_collisions:
            cr = self._get_collision_rect()
            scx, scy = cr.x - self.camera.x, cr.y - self.camera.y
            pg.draw.rect(self.screen, (0,255,0), (scx, scy, cr.width, cr.height), 2)
            for cx,cy,cw,ch in self.tile_map.collisions:
                scx = cx * self.tile_map.tile_size - self.camera.x
                scy = cy * self.tile_map.tile_size - self.camera.y
                s = pg.Surface((cw*self.tile_map.tile_size, ch*self.tile_map.tile_size), pg.SRCALPHA)
                s.fill((255,0,0,100))
                self.screen.blit(s, (scx, scy))
                pg.draw.rect(self.screen, (255,0,0), (scx, scy, cw*self.tile_map.tile_size, ch*self.tile_map.tile_size), 1)

        if self.show_info:
            font_s = pg.font.Font(None, 20)
            direction_text = {"idle":"IDLE","down":"Вниз","up":"Вверх","left":"Влево","right":"Вправо"}
            cur_dir = direction_text.get(self.character.current_animation, "?")
            frames = len(anim)
            info = [
                f"Анимация: {cur_dir}",
                f"Кадр: {self.character.current_frame+1}/{frames}",
                f"Позиция: ({int(self.character.x)}, {int(self.character.y)})",
                f"Камера: ({int(self.camera.x)}, {int(self.camera.y)})",
                f"Карта: {self.tile_map.width}x{self.tile_map.height}",
                "",
                "Управление:",
                "Стрелки/WASD - движение",
                "C - коллизии | H - скрыть",
                "E - телепорт (рядом с T)",
                "ESC - меню"
            ]
            bg = pg.Surface((320, 260))
            bg.set_alpha(200)
            bg.fill((0,0,0))
            self.screen.blit(bg, (5,5))
            for i, line in enumerate(info):
                if line=="": continue
                color = (200,200,100) if "Управление" in line else (255,255,255)
                self.screen.blit(font_s.render(line, True, color), (10, 10+i*20))

        # Подсказка телепорта
        if not self.teleporting and self.tile_map.teleport_points:
            ch_cx = self.character.x + self.character.frame_width // 2
            ch_cy = self.character.y + self.character.frame_height // 2
            tx = int(ch_cx // self.tile_map.tile_size)
            ty = int(ch_cy // self.tile_map.tile_size)
            for tp in self.tile_map.teleport_points:
                if tp["x"] == tx and tp["y"] == ty:
                    hint = pg.font.Font(None, 24).render("Нажмите E для телепортации", True, (255,255,200))
                    self.screen.blit(hint, (screen_x, screen_y - 30))
                    break

        # Затемнение при переходе
        if self.teleporting:
            self.fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(self.fade_surface, (0,0))

    def resume(self):
        self.pause_opened = False
        self.escape_pressed = False