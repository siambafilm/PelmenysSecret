import pygame
import sys
import os

# Константы
#SCREEN_WIDTH = 800
#SCREEN_HEIGHT = 600
#FPS = 60

# Скорость анимации (чем меньше число, тем быстрее анимация)
ANIMATION_SPEED = 8

class Char:
    def __init__(self, x, y, walk_sprite_path, idle_sprite_path=None):
        self.x = x
        self.y = y
        self.speed = 3
        self.direction = [0, 0]  # [x, y]
        
        # Параметры анимации
        self.current_animation = "idle"  # idle, down, left, right, up
        self.current_frame = 0
        self.animation_timer = 0
        
        # Загрузка анимаций
        self.animations = {}
        self.load_walk_animation(walk_sprite_path)
        
        # Загрузка анимации стояния (если указана)
        if idle_sprite_path and os.path.exists(idle_sprite_path):
            self.load_idle_animation(idle_sprite_path)
        else:
            # Если файл стояния не указан, используем первый кадр из ходьбы вниз
            print("Предупреждение: Анимация стояния не найдена, использую первый кадр из ходьбы вниз")
            self.animations["idle"] = [self.animations["down"][0]]
    
    def load_walk_animation(self, sprite_path):
        """Загрузка анимации ходьбы из спрайт-листа 4x3"""
        try:
            # Загрузка спрайт-листа
            sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
            sheet_width = sprite_sheet.get_width()
            sheet_height = sprite_sheet.get_height()
            
            # Определяем количество строк и столбцов (4 строки, 3 столбца для ходьбы)
            rows = 4  # вниз, влево, вправо, вверх
            cols = 3  # по 3 кадра на анимацию
            
            # Автоматически вычисляем размеры одного кадра
            self.frame_width = sheet_width // cols
            self.frame_height = sheet_height // rows
            
            print(f"Загружен спрайт-лист: {sheet_width}x{sheet_height}")
            print(f"Размер кадра: {self.frame_width}x{self.frame_height}")
            print(f"Строк: {rows}, Столбцов: {cols}")
            
            # Названия анимаций для каждой строки
            animation_names = ["down", "left", "right", "up"]
            
            # Вырезаем кадры для каждой анимации
            for row in range(rows):
                frames = []
                for col in range(cols):
                    # Вырезаем кадр
                    frame = sprite_sheet.subsurface(pygame.Rect(
                        col * self.frame_width,
                        row * self.frame_height,
                        self.frame_width,
                        self.frame_height
                    ))
                    frames.append(frame)
                
                # Сохраняем анимацию
                animation_name = animation_names[row]
                self.animations[animation_name] = frames
                
            print(f"Загружено анимаций: {list(self.animations.keys())}")
            
        except Exception as e:
            print(f"Ошибка загрузки спрайт-листа: {e}")
            sys.exit(1)
    
    def load_idle_animation(self, idle_path):
        """Загрузка анимации стояния из отдельного файла (1 строка, 2 столбца)"""
        try:
            idle_sheet = pygame.image.load(idle_path).convert_alpha()
            sheet_width = idle_sheet.get_width()
            sheet_height = idle_sheet.get_height()
            
            # Определяем размеры для стояния (2 кадра в строке)
            idle_cols = 2
            idle_rows = 1
            
            # Вычисляем размеры кадров (должны совпадать с размерами кадров ходьбы)
            frame_width = sheet_width // idle_cols
            frame_height = sheet_height // idle_rows
            
            print(f"\nЗагружена анимация стояния: {sheet_width}x{sheet_height}")
            print(f"Размер кадра стояния: {frame_width}x{frame_height}")
            
            # Проверяем соответствие размеров
            if frame_width != self.frame_width or frame_height != self.frame_height:
                print(f"Предупреждение: Размеры кадров не совпадают!")
                print(f"Ходьба: {self.frame_width}x{self.frame_height}")
                print(f"Стояние: {frame_width}x{frame_height}")
                print("Анимация стояния будет масштабирована")
                
                # Масштабируем кадры до нужного размера
                frames = []
                for col in range(idle_cols):
                    frame = idle_sheet.subsurface(pygame.Rect(
                        col * frame_width,
                        0,
                        frame_width,
                        frame_height
                    ))
                    # Масштабируем до размера кадров ходьбы
                    frame = pygame.transform.scale(frame, (self.frame_width, self.frame_height))
                    frames.append(frame)
                self.animations["idle"] = frames
            else:
                # Размеры совпадают, просто вырезаем кадры
                frames = []
                for col in range(idle_cols):
                    frame = idle_sheet.subsurface(pygame.Rect(
                        col * frame_width,
                        0,
                        frame_width,
                        frame_height
                    ))
                    frames.append(frame)
                self.animations["idle"] = frames
                
            print(f"Загружено {len(frames)} кадров для анимации стояния")
            
        except Exception as e:
            print(f"Ошибка загрузки анимации стояния: {e}")
            print("Использую первый кадр из ходьбы вниз")
            self.animations["idle"] = [self.animations["down"][0]]
    
    def set_animation(self, animation_name):
        """Установка текущей анимации"""
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            self.current_frame = 0
            self.animation_timer = 0
    
    def update_animation(self, FPS):
        """Обновление анимации"""
        if self.current_animation not in self.animations:
            return
            
        self.animation_timer += 1
        
        # Получаем количество кадров в текущей анимации
        frames_count = len(self.animations[self.current_animation])
        
        if self.animation_timer >= FPS / ANIMATION_SPEED:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % frames_count
    
    def update_movement(self, screen_width, screen_height):
        """Обновление движения персонажа"""
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        # Ограничение движения по границам экрана
        self.x = max(0, min(self.x, screen_width - self.frame_width))
        self.y = max(0, min(self.y, screen_height - self.frame_height))
        
        # Выбор анимации на основе направления движения
        if self.direction == [0, 0]:
            self.set_animation("idle")
        elif self.direction[1] > 0:  # Вниз
            self.set_animation("down")
        elif self.direction[1] < 0:  # Вверх
            self.set_animation("up")
        elif self.direction[0] < 0:  # Влево
            self.set_animation("left")
        elif self.direction[0] > 0:  # Вправо
            self.set_animation("right")
    
    def handle_input(self):
        """Обработка ввода с клавиатуры"""
        keys = pygame.key.get_pressed()
        
        self.direction = [0, 0]
        
        if keys[pygame.K_LEFT]:
            self.direction[0] = -1
        if keys[pygame.K_RIGHT]:
            self.direction[0] = 1
        if keys[pygame.K_UP]:
            self.direction[1] = -1
        if keys[pygame.K_DOWN]:
            self.direction[1] = 1
        
        # Нормализация диагонального движения (чтобы скорость не была выше)
        if self.direction[0] != 0 and self.direction[1] != 0:
            self.direction[0] *= 0.707
            self.direction[1] *= 0.707
    
    def update(self):
        """Обновление состояния персонажа"""
        self.update_movement()
        self.update_animation()
    
    def draw(self, screen):
        """Отрисовка персонажа"""
        if self.current_animation in self.animations:
            frames = self.animations[self.current_animation]
            if self.current_frame < len(frames):
                current_sprite = frames[self.current_frame]
                screen.blit(current_sprite, (self.x, self.y))
            else:
                screen.blit(frames[0], (self.x, self.y))
        else:
            # Fallback: рисуем первый кадр анимации вниз
            screen.blit(self.animations["down"][0], (self.x, self.y))