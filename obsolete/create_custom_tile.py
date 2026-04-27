#!/usr/bin/env python3
"""Создает пример кастомного тайла 64x64 для использования в редакторе"""

import pygame as pg
import os

pg.init()

# Создаем кастомный тайл - кристалл
surf = pg.Surface((64, 64), pg.SRCALPHA)

# Фон - темный
surf.fill((40, 20, 60))

# Кристалл (синий/фиолетовый)
points = [
    (32, 5),   # верх
    (45, 18),  # верх-право
    (52, 35),  # право-средина
    (45, 50),  # низ-право
    (32, 60),  # низ
    (19, 50),  # низ-лево
    (12, 35),  # лево-средина
    (19, 18),  # верх-лево
]
pg.draw.polygon(surf, (100, 200, 255), points)
pg.draw.polygon(surf, (200, 230, 255), points, 2)

# Внутреннее свечение
inner_points = [
    (32, 12),
    (40, 22),
    (43, 32),
    (40, 42),
    (32, 48),
    (24, 42),
    (21, 32),
    (24, 22),
]
pg.draw.polygon(surf, (150, 220, 255, 180), inner_points)

# Блик
pg.draw.circle(surf, (255, 255, 255, 200), (28, 20), 4)

# Сохраняем
os.makedirs("custom_tiles", exist_ok=True)
pg.image.save(surf, "custom_tiles/crystal.png")
print("✓ Создан custom_tiles/crystal.png (64x64)")

# Еще один тайл - лед
surf2 = pg.Surface((64, 64), pg.SRCALPHA)
surf2.fill((180, 220, 255))
for i in range(0, 64, 8):
    pg.draw.line(surf2, (150, 200, 255), (i, 0), (i, 64), 1)
for i in range(0, 64, 8):
    pg.draw.line(surf2, (150, 200, 255), (0, i), (64, i), 1)
# Блик
pg.draw.ellipse(surf2, (255, 255, 255, 150), (10, 10, 30, 20))
pg.image.save(surf2, "custom_tiles/ice.png")
print("✓ Создан custom_tiles/ice.png (64x64)")

# Третий тайл - огонь
surf3 = pg.Surface((64, 64), pg.SRCALPHA)
for y in range(0, 64, 4):
    for x in range(0, 64, 4):
        intensity = 150 + ((x + y) % 50)
        color = (255, intensity, 0, 200)
        pg.draw.rect(surf3, color, (x, y, 4, 4))
pg.image.save(surf3, "custom_tiles/fire.png")
print("✓ Создан custom_tiles/fire.png (64x64)")

pg.quit()
print("\nВсе кастомные тайлы созданы!")
print("Поместите свои PNG/JPG файлы (64x64) в папку custom_tiles/")
