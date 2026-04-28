import pygame as pg
import sys

class Game:
    """Главный класс игры, управляющий сценами"""
    
    def __init__(self):
        pg.init()
        
        # Настройки окна
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT), pg.RESIZABLE)
        pg.display.set_caption("Pelmeshki - Главное меню")
        
        self.clock = pg.time.Clock()
        self.running = True
        
        # Текущая сцена
        self.current_scene = None
        
        self.scene_history = []  # стек сцен
        # Загрузка первой сцены (главное меню)
        self.change_scene("MAIN_MENU")
    
    def change_scene(self, scene_name, **kwargs):
        """Переключение между сценами"""
        if scene_name == "MAIN_MENU":
            from main_menu import MainMenu
            self.current_scene = MainMenu(self.screen)
        elif scene_name == "GAME":
            #from game_scene import GameScene
            from game_scene import GameScene
            self.current_scene = GameScene(self.screen, **kwargs)
        elif scene_name == "QUIT":
            self.running = False
            return
        else:
            self.current_scene = scene_name
        
        print(f"Переключено на сцену: {type(self.current_scene).__name__}")
    
    def run(self):
        """Главный игровой цикл"""
        while self.running:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    self.running = False
            
            if self.current_scene:
                self.current_scene.handle_events(events)
                self.current_scene.update()
                
                # Проверка на необходимость смены сцены
                if self.current_scene.is_complete():
                    next_scene = self.current_scene.get_next_scene()
                    
                    # ВАЖНО: сбрасываем next_scene у текущей сцены, чтобы не вызывать переключение снова
                    self.current_scene.next_scene = None
                    
                    if next_scene == "QUIT":
                        self.running = False
                    elif next_scene == "BACK" and self.scene_history:
                        self.current_scene = self.scene_history.pop()
                    elif next_scene:
                        # Сохраняем текущую сцену в историю
                        self.scene_history.append(self.current_scene)
                        self.change_scene(next_scene)
                
                self.current_scene.draw()
            
            pg.display.update()
            self.clock.tick(60)
        
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()