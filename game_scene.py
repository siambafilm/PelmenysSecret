import pygame as pg
from scene import Scene
from dialog import *

class GameScene(Scene):
    """Игровая сцена - основной геймплей"""
    
    def __init__(self, screen, load_save=False):
        super().__init__(screen)
        self.load_save = load_save
        
        # Загрузка фона
        try:
            self.background = pg.image.load('pics/game/background.jpg').convert()
            self.background = pg.transform.scale(self.background, screen.get_size())
        except:
            self.background = None
        
        # Параметры
        self.cur_w = screen.get_width()
        self.cur_h = screen.get_height()
        
        # Состояния
        self.mouse_coords = (0, 0)
        self.mouse_coords_pressed = (0, 0)
        self.mouse_btn = 0
        self.space_pressed = False
        self.e_pressed = False
        self.escape_pressed = False
        
        # Инициализация диалоговой системы
        self.init_dialog_system()
        
        # Флаг показа меню паузы
        self.pause_menu = False
        self.pause_opened = False
        
    def init_dialog_system(self):
        """Инициализация диалоговой системы"""
        try:
            # Загрузка персонажа
            pers_dialog_face = pg.image.load('pics/main_person/dialogFace.png').convert_alpha()
            pers_dialog_face_rect = pers_dialog_face.get_rect()
            pers = Character("Pers", pers_dialog_face, pers_dialog_face_rect)
            
            # Создание диалогов
            steps1 = [Replique(pers, "Привет! Это первая диалоговая реплика!"),
                     Replique(pers, "А это вторая. Нажми пробел чтобы продолжить."),
                     Replique(pers, "Отлично! Диалог работает!")]
            dial1 = Dialog(steps1)
            
            step2 = ChoiseStep(['Вариант А', 'Вариант Б', 'Вариант В'],
                              [Replique(pers, "Вы выбрали вариант А!"),
                               Replique(pers, 'Вы выбрали вариант Б!'),
                               Replique(pers, 'Вы выбрали вариант В!')])
            dial2 = ChoiceDialogPart(step2)
            
            steps3 = [Replique(pers, "Это конец диалогов! Нажми E чтобы начать снова."),
                     Replique(pers, "Конечно, можно добавить больше диалогов!")]
            dial3 = Dialog(steps3)
            
            self.dialog_system = DialogSystem()
            self.dialogs = [dial1, dial2, dial3]
            
        except Exception as e:
            print(f"Ошибка загрузки диалогов: {e}")
            self.dialog_system = None
    
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

            if self.pause_opened:
                # Если пауза открыта, обрабатываем только ESC для закрытия
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.pause_opened = False
                    self.next_scene = None
                continue  # пропускаем остальные события
                
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_e:
                    self.e_pressed = True
                if event.key == pg.K_SPACE:
                    self.space_pressed = True
                if event.key == pg.K_ESCAPE:
                    self.escape_pressed = True
            
            elif event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.space_pressed = False
                if event.key == pg.K_e:
                    self.e_pressed = False
                if event.key == pg.K_ESCAPE:
                    self.escape_pressed = False
            
            elif event.type == pg.MOUSEMOTION:
                self.mouse_coords = event.pos
            
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_coords_pressed = event.pos
                self.mouse_btn = event.button
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse_coords_pressed = (-1, -1)
                self.mouse_btn = 0
    
    def update(self):
        # НЕ обрабатываем логику игры, если открыто меню паузы
        if hasattr(self, 'pause_opened') and self.pause_opened:
            return
        
        # Обработка паузы
        if self.escape_pressed and not self.dialog_system.is_active():
            self.pause_opened = True  # устанавливаем флаг
            from pause_menu import PauseMenu
            self.next_scene = PauseMenu(self.screen, self)
            return  # выходим, чтобы не обрабатывать остальную логику
        
        # Остальная логика игры (диалоги и т.д.)
        if self.dialog_system and self.e_pressed:
            if not self.dialog_system.is_active():
                self.dialog_system.start_chain(self.dialogs)
        
        if self.dialog_system:
            self.dialog_system.update(self.space_pressed, self.mouse_coords, self.mouse_btn)
    
    def draw(self):
        # Отрисовка фона
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            pg.draw.rect(self.screen, (100, 100, 150), (0, 0, self.cur_w, self.cur_h))
        
        # Игровая информация
        font = pg.font.Font(None, 36)
        info_text = font.render("Нажми E для диалога | ESC - меню", True, (255, 255, 255))
        self.screen.blit(info_text, (20, 20))
        
        # Отрисовка диалогов
        if self.dialog_system and self.dialog_system.is_active():
            self.dialog_system.draw(self.screen, (20, self.cur_h-160, self.cur_w-40, 140),
                                   self.mouse_coords, self.mouse_btn, self.space_pressed)
            
    def resume(self):
        """Возврат из меню паузы"""
        self.pause_opened = False