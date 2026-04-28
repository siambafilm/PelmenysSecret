import pygame as pg
from scene import Scene

class MainMenu(Scene):
    """Главное меню игры"""
    
    def __init__(self, screen):
        super().__init__(screen)
        
        # Загрузка фонового изображения
        try:
            self.background = pg.image.load('pics/system/main_menu/back.jpg').convert()
            self.background = pg.transform.scale(self.background, screen.get_size())
        except:
            # Если фона нет, создаем градиентный фон
            self.background = pg.Surface(screen.get_size())
            for i in range(screen.get_height()):
                color = (20 + i // 10, 20 + i // 10, 40 + i // 10)
                pg.draw.line(self.background, color, (0, i), (screen.get_width(), i))
        
        '''# Загрузка логотипа
        try:
            
        except:
            # Создаем текстовый логотип
            font = pg.font.Font(None, 72)
            self.logo = font.render("Pelmeny`s Secret", True, (255, 255, 0))'''
        
        self.logo = pg.image.load('pics/system/main_menu/logo.png').convert_alpha()
        self.logo = pg.transform.scale(self.logo, (300, 150))
        
        # Настройка кнопок
        font = pg.font.Font(None, 48)
        font_small = pg.font.Font(None, 36)
        
        button_width = 250
        button_height = 60
        start_x = screen.get_width() // 2 - button_width // 2
        start_y = screen.get_height() // 2 + 50
        
        # Кнопка "Продолжить" (если есть сохранение)
        self.continue_button = {
            'rect': pg.Rect(start_x, start_y, button_width, button_height),
            'text': font.render("Продолжить", True, (255, 255, 255)),
            'enabled': self.check_save_exists()
        }
        
        # Кнопка "Новая игра"
        self.new_game_button = {
            'rect': pg.Rect(start_x, start_y + 80 if self.continue_button['enabled'] else start_y, 
                           button_width, button_height),
            'text': font.render("Новая игра", True, (255, 255, 255)),
            'enabled': True
        }
        
        # Кнопка "Выход"
        self.exit_button = {
            'rect': pg.Rect(start_x, start_y + 160 if self.continue_button['enabled'] else start_y + 80,
                           button_width, button_height),
            'text': font.render("Выход", True, (255, 255, 255)),
            'enabled': True
        }
        
        # Цвета кнопок
        self.button_color = (70, 70, 150)
        self.button_hover_color = (100, 100, 200)
        self.button_disabled_color = (100, 100, 100)
        
        self.hovered_button = None
        
        # Анимация
        self.animation_offset = 0
        self.animation_speed = 0.05
        
    def check_save_exists(self):
        """Проверка наличия сохранения"""
        try:
            with open('savegame.dat', 'rb'):
                return True
        except:
            return False
    
    def handle_events(self, events):
        # Обновляем размеры при изменении окна
        if self.screen.get_size() != self.background.get_size():
            self.background = pg.transform.scale(self.background, self.screen.get_size())
            self.update_button_positions()
        
        for event in events:
            if event.type == pg.QUIT:
                self.running = False
                self.next_scene = "QUIT"
            
            elif event.type == pg.MOUSEMOTION:
                self.hovered_button = None
                for button in [self.continue_button, self.new_game_button, self.exit_button]:
                    if button['enabled'] and button['rect'].collidepoint(event.pos):
                        self.hovered_button = button
            
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка
                    if self.continue_button['enabled'] and self.continue_button['rect'].collidepoint(event.pos):
                        self.on_continue()
                    elif self.new_game_button['rect'].collidepoint(event.pos):
                        self.on_new_game()
                    elif self.exit_button['rect'].collidepoint(event.pos):
                        self.on_exit()
            
            elif event.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode((max(event.w, 800), max(event.h, 600)), pg.RESIZABLE)
                self.update_button_positions()
    
    def update_button_positions(self):
        """Обновление позиций кнопок при изменении размера окна"""
        button_width = 250
        button_height = 60
        start_x = self.screen.get_width() // 2 - button_width // 2
        start_y = self.screen.get_height() // 2 + 50
        
        self.continue_button['rect'] = pg.Rect(start_x, start_y, button_width, button_height)
        self.new_game_button['rect'] = pg.Rect(start_x, start_y + 80 if self.continue_button['enabled'] else start_y,
                                               button_width, button_height)
        self.exit_button['rect'] = pg.Rect(start_x, start_y + 160 if self.continue_button['enabled'] else start_y + 80,
                                          button_width, button_height)
    
    def update(self):
        # Анимация для меню
        self.animation_offset += self.animation_speed
        if self.animation_offset > 2 * 3.14159:
            self.animation_offset = 0
    
    def draw(self):
        # Рисуем фон
        self.screen.blit(self.background, (0, 0))
        
        # Рисуем логотип с легкой анимацией (без)
        #logo_y = 50 + int(10 * (self.animation_offset / 3.14159))
        logo_y = 150
        logo_rect = self.logo.get_rect(center=(self.screen.get_width() // 2, logo_y))
        self.screen.blit(self.logo, logo_rect)
        font_small = pg.font.Font(None, 40)
        subtitle = font_small.render("Pelmeny`s Secret", True, (255, 255, 255))
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, logo_y + 120))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Рисуем кнопки
        for button in [self.continue_button, self.new_game_button, self.exit_button]:
            if not button['enabled']:
                color = self.button_disabled_color
            elif button == self.hovered_button:
                color = self.button_hover_color
                # Эффект увеличения при наведении
                enlarged_rect = button['rect'].inflate(10, 5)
                pg.draw.rect(self.screen, color, enlarged_rect, border_radius=10)
                pg.draw.rect(self.screen, (255, 255, 255), enlarged_rect, width=2, border_radius=10)
                text_rect = button['text'].get_rect(center=enlarged_rect.center)
            else:
                color = self.button_color
                pg.draw.rect(self.screen, color, button['rect'], border_radius=10)
                pg.draw.rect(self.screen, (200, 200, 200), button['rect'], width=2, border_radius=10)
                text_rect = button['text'].get_rect(center=button['rect'].center)
            
            if button['enabled'] or button != self.continue_button:
                self.screen.blit(button['text'], text_rect)
        
        # Добавляем декоративный элемент
        pg.draw.line(self.screen, (255, 255, 100), 
                    (0, self.screen.get_height() - 50),
                    (self.screen.get_width(), self.screen.get_height() - 50), 2)
    
    def on_continue(self):
        """Загрузка сохраненной игры"""
        print("Загрузка сохранения...")
        # Здесь будет загрузка игровых данных
        #from dialog_scene import GameScene
        #self.next_scene = GameScene(self.screen, load_save=True)
    
    def on_new_game(self):
        """Начало новой игры"""
        print("Начало новой игры...")
        from game_scene import GameScene
        self.next_scene = GameScene(self.screen, load_save=False, map_file="Maps/test.map")
    
    def on_exit(self):
        """Выход из игры"""
        self.next_scene = "QUIT"