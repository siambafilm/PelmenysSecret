# Map Editor for PelmenysSecret

## Overview
A powerful tile-based map editor for creating game levels with collision detection support.

## Features
- **Tile Painting Mode**: Paint graphical tiles on the map
- **Collision Painting Mode**: Define walkable and non-walkable areas
- **Camera Scrolling**: Right-click and drag to navigate large maps
- **Zoom Support**: Mouse wheel to zoom in/out
- **Custom Brushes**: Load your own PNG/JPG tiles (64x64) from `custom_tiles/`
- **Save/Load**: Save maps in `.map` JSON format

## Tile Types

### Built-in Tiles (ID 0-10)

| ID | Type | Description |
|----|------|-------------|
| 0 | Трава | Green grass |
| 1 | Камень | Stone ground |
| 2 | Вода | Water (impassable) |
| 3 | Песок | Sand |
| 4 | Дерево | Tree (impassable) |
| 5 | Камень | Small rock (impassable) |
| 6 | Цветы | Flowers |
| 7 | Путь | Path |
| 8 | Темная трава | Dark grass |
| 9 | Лава | Lava (impassable) |
| 10 | Снег | Snow |

### Custom Tiles (ID 11+)

Кастомные тайлы автоматически загружаются из папки `custom_tiles/` при запуске редактора.

**Поддерживаемые форматы:** PNG, JPG, JPEG, BMP, GIF  
**Требуемый размер:** 64x64 пикселя (автоматически масштабируется при необходимости)

Примеры кастомных тайлов уже созданы в `custom_tiles/`:
- `crystal.png` - Синий кристалл (ID: 11)
- `ice.png` - Лед (ID: 12)
- `fire.png` - Огонь (ID: 13)

## Создание своих тайлов

1. Создайте изображение размером **64x64 пикселя** в любом графическом редакторе
2. Сохраните в формате PNG или JPG
3. Поместите файл в папку `custom_tiles/`
4. Запустите редактор - тайл появится в панели кистей

### Программное создание

Используйте скрипт для создания примеров:

```bash
python3 create_custom_tile.py
```

Этот скрипт создаст 3 примера кастомных тайлов в папке `custom_tiles/`.

### Пример кода для создания тайла

```python
import pygame as pg

pg.init()
surf = pg.Surface((64, 64), pg.SRCALPHA)

# Рисуем свой тайл
surf.fill((100, 200, 100))  # Зеленый фон
pg.draw.circle(surf, (255, 255, 0), (32, 32), 20)  # Желтый круг

# Сохраняем
pg.image.save(surf, "custom_tiles/my_tile.png")
```

## Usage

### Running the Editor
```bash
cd /home/siamba/Документы/PelmenysSecret
source Pelmeny_venv/bin/activate
python3 map_editor.py
```

### Controls

#### General
- **ЛКМ (Left Click)**: Paint tiles or place collisions
- **ПКМ (Right Click)**: Drag camera
- **Mouse Wheel**: Zoom in/out
- **Пробел (Space)**: Switch between paint/collision modes
- **ESC**: Exit or close dialogs

#### Buttons
- **Новая карта**: Create a new map (specify width/height)
- **Сохранить**: Save map to `.map` file
- **Загрузить**: Load map from `.map` file
- **Очистить**: Clear all tiles and collisions
- **Режим: Кисть**: Switch to tile painting mode
- **Режим: Коллизия**: Switch to collision painting mode

#### Keyboard Shortcuts
- **C**: Toggle collision display (in game)
- **H**: Toggle info display

## File Format

Maps are saved in JSON format with `.map` extension:

```json
{
  "version": "1.0",
  "width": 25,
  "height": 15,
  "tile_size": 64,
  "tiles": [
    [x, y, tile_type],
    ...
  ],
  "collisions": [
    [x, y, width, height],
    ...
  ]
}
```

## Integration with Game

### Loading a Map in Game
```python
from level1 import GameScene

# Load custom map
scene = GameScene(screen, load_save=False, map_file="my_level.map")

# Or use default generated map
scene = GameScene(screen, load_save=False, map_file=None)
```

### Map Size Limits
- Minimum: 5x5 tiles
- Maximum: 100x100 tiles
- Default tile size: 64x64 pixels

## Collision System

- **Impassable tiles**: Water (2), Tree (4), Rock (5), Lava (9)
- **Walkable tiles**: Grass (0), Stone (1), Sand (3), Path (7), etc.
- Collisions are defined per-tile in the collision layer
- Character cannot move through collided tiles

## Tips

1. **Large Maps**: Use right-click drag to navigate. Maps larger than screen will auto-scroll.
2. **Performance**: Only visible tiles are rendered for optimal performance.
3. **Collisions**: Use collision mode to mark impassable areas (red overlay).
4. **Testing**: Press 'C' in game to visualize collision areas.
5. **Custom Tiles**: Add your own PNG/JPG files to `custom_tiles/` folder.

## Examples

### Creating a Simple Level
1. Open editor: `python3 map_editor.py`
2. Set map size (e.g., 30x20)
3. Paint grass (brush 0) for background
4. Add obstacles with brushes 1, 4, 5
5. Switch to collision mode and mark impassable areas
6. Save as `my_level.map`
7. Load in game with `map_file="my_level.map"`

### Using Sample Map
```python
from level1 import GameScene
scene = GameScene(screen, map_file="sample_map.map")
```

## Troubleshooting

- **Map not loading**: Check JSON syntax and file path
- **Performance issues**: Reduce map size or visible area
- **Collision not working**: Ensure collision layer is properly defined
- **Zoom not working**: Some systems may have different mouse wheel behavior
- **Custom tiles not loading**: Ensure files are in `custom_tiles/` and are valid images

## Technical Details

- Built with PyGame
- JSON-based save format
- Efficient rendering (only visible tiles)
- Smooth camera following with interpolation
- Collision detection via tile lookup
- Automatic custom tile loading from `custom_tiles/`

## Future Enhancements

- Multiple layers (background, foreground, collision)
- Custom tile sets import
- Undo/redo functionality
- Copy/paste regions
- Auto-tiling for edges
- Object placement (NPCs, items, triggers)
