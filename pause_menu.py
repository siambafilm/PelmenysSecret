import pygame as pg
from scene import Scene

class PauseMenu(Scene):
    """Меню паузы"""
    
    def __init__(self, screen, game_scene=None):
        super().__init__(screen)
        #self.game_scene = game_scene
        self.game_scene = game_scene
        
        # Создание полупрозрачного фона
        self.overlay = pg.Surface(screen.get_size())
        self.overlay.set_alpha(180)
        self.overlay.fill((0, 0, 0))
        
        # Настройка кнопок
        font = pg.font.Font(None, 48)
        
        button_width = 300
        button_height = 50
        start_x = screen.get_width() // 2 - button_width // 2
        start_y = screen.get_height() // 2 - 100
        
        self.buttons = {
            'continue': {
                'rect': pg.Rect(start_x, start_y, button_width, button_height),
                'text': font.render("Продолжить", True, (255, 255, 255)),
                'action': self.on_continue
            },
            'save': {
                'rect': pg.Rect(start_x, start_y + 70, button_width, button_height),
                'text': font.render("Сохранить", True, (255, 255, 255)),
                'action': self.on_save
            },
            'menu': {
                'rect': pg.Rect(start_x, start_y + 140, button_width, button_height),
                'text': font.render("Главное меню", True, (255, 255, 255)),
                'action': self.on_main_menu
            },
            'exit': {
                'rect': pg.Rect(start_x, start_y + 210, button_width, button_height),
                'text': font.render("Выход", True, (255, 255, 255)),
                'action': self.on_exit
            }
        }
        
        self.button_color = (70, 70, 150)
        self.button_hover_color = (100, 100, 200)
        self.hovered_button = None

    def set_game_scene(self, game_scene):
        self.game_scene = game_scene
        
    def handle_events(self, events):
        for event in events:
            if event.type == pg.QUIT:
                self.next_scene = "QUIT"
            
            elif event.type == pg.MOUSEMOTION:
                self.hovered_button = None
                for button in self.buttons.values():
                    if button['rect'].collidepoint(event.pos):
                        self.hovered_button = button
            
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.buttons.values():
                        if button['rect'].collidepoint(event.pos):
                            button['action']()
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.on_continue()
    
    def update(self):
        pass
    
    def draw(self):
        # Рисуем игровую сцену
        self.game_scene.draw()
        
        # Рисуем overlay паузы
        self.screen.blit(self.overlay, (0, 0))
        
        # Заголовок
        font = pg.font.Font(None, 72)
        title = font.render("ПАУЗА", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Кнопки
        for button in self.buttons.values():
            color = self.button_hover_color if button == self.hovered_button else self.button_color
            pg.draw.rect(self.screen, color, button['rect'], border_radius=10)
            pg.draw.rect(self.screen, (200, 200, 200), button['rect'], width=2, border_radius=10)
            text_rect = button['text'].get_rect(center=button['rect'].center)
            self.screen.blit(button['text'], text_rect)
    
    def on_continue(self):
        """Продолжить игру"""
        if self.game_scene:
            self.game_scene.resume()
            self.game_scene.escape_pressed = False  # Сбрасываем клавишу ESC
        self.next_scene = "BACK"
    
    def on_save(self):
        """Сохранить игру"""
        print("Игра сохранена!")
        # Здесь логика сохранения
        
    def on_main_menu(self):
        """Вернуться в главное меню"""
        from main_menu import MainMenu
        self.next_scene = MainMenu(self.screen)
    
    def on_exit(self):
        """Выход из игры"""
        self.next_scene = "QUIT"