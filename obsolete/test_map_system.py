#!/usr/bin/env python3
"""Тестовая программа для проверки системы карт и редактора"""

import pygame as pg
import sys
import os

def test_map_editor():
    """Тест редактора карт"""
    print("=" * 50)
    print("ТЕСТ: Map Editor")
    print("=" * 50)
    print("Запуск редактора...")
    print("Управление:")
    print("  ЛКМ - рисовать/ставить коллизии")
    print("  ПКМ - перетаскивать камеру")
    print("  Пробел - переключить режим (кисть/коллизия)")
    print("  ESC - выход")
    print()
    
    from map_editor import MapEditor
    editor = MapEditor()
    editor.run()

def test_game_with_map():
    """Тест игры с тайловой картой"""
    print("=" * 50)
    print("ТЕСТ: Игра с тайловой картой")
    print("=" * 50)
    print("Запуск игры...")
    print("Управление:")
    print("  Стрелки/WASD - движение")
    print("  C - показать/скрыть коллизии")
    print("  H - показать/скрыть информацию")
    print("  ESC - пауза")
    print()
    
    pg.init()
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("PelmenysSecret - Тест карты")
    clock = pg.time.Clock()
    
    from game_scene import GameScene
    scene = GameScene(screen, load_save=False, map_file=None)
    
    running = True
    while running:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                running = False
        
        scene.handle_events(events)
        scene.update()
        scene.draw()
        
        pg.display.update()
        clock.tick(60)
    
    pg.quit()
    sys.exit()

def test_map_save_load():
    """Тест сохранения и загрузки карты"""
    print("=" * 50)
    print("ТЕСТ: Сохранение и загрузка карты")
    print("=" * 50)
    
    from map_system import TileMap
    
    # Создаем тестовую карту
    tile_map = TileMap(tile_size=64)
    tile_map.width = 10
    tile_map.height = 10
    
    # Добавляем тайлы
    for y in range(10):
        for x in range(10):
            tile_map.tiles.append((x, y, 0))  # Трава
    
    # Добавляем препятствия
    tile_map.tiles.append((5, 5, 1))  # Камень
    tile_map.collisions.append((5, 5, 1, 1))
    
    # Сохраняем
    test_file = "test_map.map"
    import json
    data = {
        "version": "1.0",
        "width": tile_map.width,
        "height": tile_map.height,
        "tile_size": tile_map.tile_size,
        "tiles": tile_map.tiles,
        "collisions": tile_map.collisions
    }
    with open(test_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Карта сохранена в {test_file}")
    
    # Загружаем
    tile_map2 = TileMap(tile_size=64)
    if tile_map2.load_from_file(test_file):
        print(f"✓ Карта загружена: {tile_map2.width}x{tile_map2.height}")
        print(f"  Тайлов: {len(tile_map2.tiles)}")
        print(f"  Коллизий: {len(tile_map2.collisions)}")
    
    # Очищаем тестовый файл
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"✓ Тестовый файл удален")
    
    print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "editor":
            test_map_editor()
        elif sys.argv[1] == "game":
            test_game_with_map()
        elif sys.argv[1] == "test":
            test_map_save_load()
        else:
            print("Использование:")
            print("  python test_map_system.py editor  - запустить редактор")
            print("  python test_map_system.py game    - запустить игру")
            print("  python test_map_system.py test    - запустить тест")
    else:
        print("PelmenysSecret - Map System Test")
        print("=" * 50)
        test_map_save_load()
        print("\nДля запуска редактора: python test_map_system.py editor")
        print("Для запуска игры: python test_map_system.py game")
