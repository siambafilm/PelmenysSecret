import pygame as pg
from scene import Scene
from char import Char

class GameScene(Scene):
    """Игровая сцена с персонажем"""
    
    def __init__(self, screen, load_save=False):
        super().__init__(screen)
        self.load_save = load_save
        
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
        
        # Загрузка фона
        try:
            self.background = pg.image.load('pics/game/background.jpg').convert()
            self.background = pg.transform.scale(self.background, screen.get_size())
        except:
            self.background = None
        
        # Создание персонажа
        self.character = Char(
            x=screen.get_width() // 2 - 32,
            y=screen.get_height() // 2 - 32,
            walk_sprite_path="pics/main_person/pers.png",
            idle_sprite_path="pics/main_person/idle.png"
        )
    
    def handle_events(self, events):
        for event in events:
            if event.type == pg.QUIT:
                self.running = False
                self.next_scene = "QUIT"
            
            elif event.type == pg.VIDEORESIZE:
                self.cur_w = max(event.w, 800)
                self.cur_h = max(event.h, 600)
                self.screen = pg.display.set_mode((self.cur_w, self.cur_h), pg.RESIZABLE)
                if self.background:
                    self.background = pg.transform.scale(self.background, self.screen.get_size())
                # Обновляем позицию персонажа при изменении размера окна
                if hasattr(self, 'character'):
                    self.character.x = min(self.character.x, self.cur_w - self.character.frame_width)
                    self.character.y = min(self.character.y, self.cur_h - self.character.frame_height)
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.escape_pressed = True
                if event.key == pg.K_h:
                    self.show_info = not self.show_info
            
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
                self.escape_pressed = False  # Сбрасываем сразу после открытия паузы
                return
        
        # Обновление персонажа
        self.character.handle_input()
        self.character.update_movement(self.cur_w, self.cur_h)
        self.character.update_animation(self.FPS)
    
    def draw(self):
        # Отрисовка фона
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            pg.draw.rect(self.screen, (30, 30, 50), (0, 0, self.cur_w, self.cur_h))
        
        # Отрисовка персонажа
        self.character.draw(self.screen)
        
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
            text_bg = pg.Surface((300, 200))
            text_bg.set_alpha(200)
            text_bg.fill((0, 0, 0))
            self.screen.blit(text_bg, (5, 5))
            
            info_lines = [
                f"Анимация: {current_action}",
                f"Кадр: {self.character.current_frame + 1}/{frames_count}",
                f"Позиция: ({int(self.character.x)}, {int(self.character.y)})",
                "",
                "Управление:",
                "Стрелки - движение",
                "ESC - меню",
                "H - скрыть информацию"
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
