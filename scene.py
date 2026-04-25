import pygame as pg

class Scene:
    """Базовый класс для всех сцен игры"""
    
    def __init__(self, screen):
        self.screen = screen
        self.next_scene = None  # Следующая сцена для переключения
        self.running = True     # Флаг работы сцены
    
    def handle_events(self, events):
        """Обработка событий"""
        pass
    
    def update(self):
        """Обновление логики сцены"""
        pass
    
    def draw(self):
        """Отрисовка сцены"""
        pass
    
    def is_complete(self):
        """Завершена ли сцена (требует переключения)"""
        return self.next_scene is not None
    
    def get_next_scene(self):
        """Получить следующую сцену"""
        return self.next_scene