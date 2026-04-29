#!/usr/bin/env python3
"""
Создает пример кастомного тайла - каменная арка
"""

import pygame as pg
import os

# Инициализация Pygame
pg.init()

# Создаем кастомный тайл - каменная арка
tile_size = 64
surf = pg.Surface((tile_size, tile_size), pg.SRCALPHA)

# Фон - полупрозрачный камень
surf.fill((100, 100, 100, 180))

# Верхняя часть арки
pg.draw.arc(surf, (200, 200, 200), (10, 10, 44, 44), 0, 3.14159)
pg.draw.arc(surf, (200, 200, 200), (20, 10, 44, 44), 0, 3.14159)

# Нижняя часть арки
pg.draw.arc(surf, (200, 200, 200), (10, 50, 44, 44), 0, 3.14159)
pg.draw.arc(surf, (200, 200, 200), (20, 50, 44, 44), 0, 3.14159)

# Детали арки
pg.draw.line(surf, (150, 150, 150), (15, 20), (45, 20), 2)
pg.draw.line(surf, (150, 150, 150), (15, 40), (45, 40), 2)

# Сохраняем
os.makedirs("custom_tiles", exist_ok=True)
pg.image.save(surf, "custom_tiles/arch.png")
print("✓ Создан custom_tiles/arch.png (64x64)")
