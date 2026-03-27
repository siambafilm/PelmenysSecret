from step import Replique, ChoiseStep, Character
import pygame as pg
import time

pg.init()

dialog_name_font = pg.font.SysFont('Arial', 12)
dialog_text_font = pg.font.SysFont('Arial', 20)

def draw_text_wrapped(surface, text, font, color, rect):
    """Отрисовка текста с переносом строк"""
    if not text:
        return
    
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_surface = font.render(word + ' ', False, color)
        word_width = word_surface.get_width()
        
        if current_width + word_width <= rect.width:
            current_line.append(word)
            current_width += word_width
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
    
    if current_line:
        lines.append(' '.join(current_line))
    
    y_offset = rect.y
    for line in lines:
        text_surface = font.render(line, False, color)
        surface.blit(text_surface, (rect.x, y_offset))
        y_offset += font.get_height()


class Dialog:
    def __init__(self, steps: list):
        self.active = False
        self.steps = steps
        self.i = -1
        self.space_handled = False
        self.completed = False

    def next(self):
        if self.active and not self.completed:
            self.i += 1
            print(f"Dialog next: i={self.i}, total={len(self.steps)}")
            if self.i >= len(self.steps):
                print("Dialog completed!")
                self.completed = True
                self.deactivate()
            else:
                self.cur_step = self.steps[self.i]
                print(f"Now showing step {self.i}: {self.cur_step.text}")

    def activate(self):
        if not self.active and not self.completed:
            print(f"Dialog activated (completed={self.completed})")
            self.active = True
            self.space_handled = False
            self.next()
        else:
            print(f"Dialog activate BLOCKED: active={self.active}, completed={self.completed}")

    def deactivate(self):
        if self.active:
            print("Dialog deactivated")
            self.active = False
            # НЕ сбрасываем self.i и self.completed здесь!
            self.space_handled = False

    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        if self.active and not self.completed:
            image = self.cur_step.character.dialog_picture
            image_rect = self.cur_step.character.rect
            name = self.cur_step.character.name
            text = self.cur_step.text

            pg.draw.rect(display, (100,100,100), rect)
            pg.draw.rect(display, (255,255,255), (rect[0]+20,rect[1]+20,rect[2]-40,rect[3]-40))
            
            # image
            # ВАЖНО: создаем копию rect, чтобы не изменять оригинал
            image_rect_copy = image_rect.copy()
            image_rect_copy.center = (rect[0]+30+(image_rect.width//2), rect[1]+(rect[3]//2)-5)
            display.blit(image, image_rect_copy)
            
            # text
            name_surface = dialog_name_font.render(name, False, (0,0,0))
            name_rect = name_surface.get_rect()
            name_rect.center = (image_rect_copy.x + (image_rect_copy.width//2), 
                            image_rect_copy.y + image_rect_copy.height + 7)
            display.blit(name_surface, name_rect)
            
            # Создаем rect для текста
            text_rect = pg.Rect(
                image_rect_copy.x + image_rect_copy.width + 20,
                rect[1] + 25,
                rect[2] - image_rect_copy.width - 60,
                rect[3] - 50
            )
            draw_text_wrapped(display, text, dialog_text_font, (0,0,0), text_rect)

            # Защита от многократного нажатия
            if space_pressed and not self.space_handled:
                self.space_handled = True
                print("Space pressed in Dialog, calling next()")
                self.next()
            elif not space_pressed:
                self.space_handled = False

    def reset(self):
        """Сброс диалога для нового использования"""
        print(f"Dialog reset (was completed={self.completed}, i={self.i})")
        self.completed = False
        self.i = -1
        self.active = False
        self.space_handled = False
        print(f"Dialog reset done (now completed={self.completed})")


class ChoiceDialogPart:
    def __init__(self, step):
        self.step = step
        self.active = False
        self.choiced = False
        self.choice = -1
        self.space_handled = False
        self.completed = False

    def activate(self):
        if not self.active and not self.completed:
            print("ChoiceDialogPart activated")
            self.active = True
            self.space_handled = False
        else:
            print(f"ChoiceDialogPart activate BLOCKED: active={self.active}, completed={self.completed}")

    def deactivate(self):
        if self.active:
            print("ChoiceDialogPart deactivated")
            self.active = False
            self.completed = True
            self.space_handled = False

    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        if self.active and not self.completed:
            pg.draw.rect(display, (100,100,100), rect)
            pg.draw.rect(display, (255,255,255), (rect[0]+20,rect[1]+20,rect[2]-40,rect[3]-40))
            
            if not self.choiced:
                choices = self.step.choices
                y = rect[1]+30
                hgh = 20
                hghstep = 10
                for i in range(len(self.step.choices)):
                    pg.draw.rect(display, (150,150,150), (rect[0]+30, y, rect[2]-50, hgh))
                    text_surface = dialog_text_font.render(choices[i], False, (0,0,0))
                    text_rect = text_surface.get_rect()
                    text_rect.center = (rect[0] + rect[2]//2, y + (hgh//2))
                    display.blit(text_surface, text_rect)
                    y += hgh + hghstep

                # Проверка выбора
                if mouseBtn == 1:
                    y = rect[1]+30
                    hgh = 20
                    hghstep = 10
                    for i in range(len(self.step.choices)):
                        choice_rect = pg.Rect(rect[0]+30, y + i*(hgh + hghstep), rect[2]-50, hgh)
                        if choice_rect.collidepoint(mouseCoords):
                            print(f"Choice {i} selected")
                            self.choiced = True
                            self.choice = i
                            break
            
            if self.choiced:
                after = self.step.replicsAfter
                image = after[self.choice].character.dialog_picture
                image_rect = after[self.choice].character.rect
                name = after[self.choice].character.name
                text = after[self.choice].text
                
                # ВАЖНО: создаем копию rect, чтобы не изменять оригинал
                image_rect_copy = image_rect.copy()
                image_rect_copy.center = (rect[0]+30+(image_rect.width//2), rect[1]+(rect[3]//2)-5)
                display.blit(image, image_rect_copy)
                
                name_surface = dialog_name_font.render(name, False, (0,0,0))
                name_rect = name_surface.get_rect()
                name_rect.center = (image_rect_copy.x + (image_rect_copy.width//2), 
                                image_rect_copy.y + image_rect_copy.height + 7)
                display.blit(name_surface, name_rect)
                
                # Создаем rect для текста
                text_rect = pg.Rect(
                    image_rect_copy.x + image_rect_copy.width + 20,
                    rect[1] + 25,
                    rect[2] - image_rect_copy.width - 60,
                    rect[3] - 50
                )
                draw_text_wrapped(display, text, dialog_text_font, (0,0,0), text_rect)

                # Защита от многократного нажатия
                if space_pressed and not self.space_handled:
                    self.space_handled = True
                    print("Space pressed in ChoiceDialogPart, deactivating")
                    self.deactivate()
                elif not space_pressed:
                    self.space_handled = False

    def reset(self):
        """Сброс для нового использования"""
        print(f"ChoiceDialogPart reset (was completed={self.completed})")
        self.completed = False
        self.choiced = False
        self.choice = -1
        self.active = False
        self.space_handled = False
        print(f"ChoiceDialogPart reset done (now completed={self.completed})")


class DialogNode:
    """Узел цепочки диалогов"""
    def __init__(self, dialog, next_node=None):
        self.dialog = dialog
        self.next_node = next_node
        self.completed = False
    
    def update(self, space_pressed: bool, mouse_pos: tuple, mouse_btn: int) -> bool:
        """Обновляет состояние узла"""
        # Не делаем ничего, вся логика уже в самом диалоге
        return False
    
    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        """Отрисовка узла"""
        self.dialog.draw(display, rect, mouseCoords, mouseBtn, space_pressed)
    
    def reset(self):
        """Сброс узла"""
        if hasattr(self.dialog, 'reset'):
            self.dialog.reset()
        self.completed = False


class DialogSystem:
    """Система управления цепочками диалогов"""
    def __init__(self):
        self.current_chain = None
        self.current_index = 0
        self.active = False
        self.space_handled = False
        self.mouse_handled = False
        self.waiting_for_space_release = False
        self.pending_dialog = None

    def start_chain(self, chain):
        """Начать цепочку диалогов"""
        print(f"\n=== Starting chain with {len(chain)} dialogs ===")
        
        self.current_chain = []
        for i, item in enumerate(chain):
            print(f"  Dialog {i}: {type(item).__name__}")
            if hasattr(item, 'reset'):
                item.reset()
            if isinstance(item, (Dialog, ChoiceDialogPart)):
                self.current_chain.append(DialogNode(item))
            else:
                self.current_chain.append(item)
        
        self.current_index = 0
        self.active = True
        self.space_handled = False
        self.mouse_handled = False
        self.waiting_for_space_release = False
        self.pending_dialog = None
        
        if self.current_chain:
            print(f"Activating first dialog (index 0)")
            self.current_chain[0].dialog.activate()
    
    def update(self, space_pressed: bool, mouse_pos: tuple, mouse_btn: int):
        """Обновление системы"""
        if not self.active or not self.current_chain:
            return
        
        # Если ждем отпускания пробела
        if self.waiting_for_space_release:
            #print(f"Waiting for space release, space_pressed={space_pressed}")
            if not space_pressed:
                #print("Space released, activating pending dialog")
                self.waiting_for_space_release = False
                if self.pending_dialog:
                    self.pending_dialog.dialog.activate()
                    self.pending_dialog = None
                else:
                    print("ERROR: No pending dialog!")
            return
        
        if self.current_index >= len(self.current_chain):
            #print("Chain finished - all nodes processed")
            self.stop_chain()
            return
        
        current_node = self.current_chain[self.current_index]
        
        #print(f"\n--- Update ---")
        #print(f"Current index: {self.current_index}, Dialog type: {type(current_node.dialog).__name__}")
        #print(f"space_pressed={space_pressed}, mouse_btn={mouse_btn}")
        
        # Защита от многократного нажатия
        space_triggered = space_pressed and not self.space_handled
        if space_pressed:
            self.space_handled = True
        else:
            self.space_handled = False
        
        mouse_triggered = (mouse_btn == 1) and not self.mouse_handled
        if mouse_btn == 1:
            self.mouse_handled = True
        elif mouse_btn == 0:
            self.mouse_handled = False
        
        #print(f"space_triggered={space_triggered}, mouse_triggered={mouse_triggered}")
        
        # Обновляем текущий узел
        current_node.update(space_triggered, mouse_pos, mouse_triggered)
        
        # Проверяем завершен ли текущий диалог
        completed = self.is_node_completed(current_node)
        #print(f"Node completed: {completed}")
        
        if completed:
            #print(f"Node {self.current_index} completed")
            
            # Деактивируем текущий диалог если он еще активен
            if current_node.dialog.active:
                #print("Deactivating current dialog")
                current_node.dialog.deactivate()
            
            # Переходим к следующему
            self.current_index += 1
            #print(f"Moved to next index: {self.current_index}")
            
            # Активируем следующий диалог если есть
            if self.current_index < len(self.current_chain):
                next_node = self.current_chain[self.current_index]
                #print(f"Preparing to activate next dialog (index {self.current_index})")
                
                # Сбрасываем флаги
                self.space_handled = False
                self.mouse_handled = False
                
                # Проверяем состояние пробела
                if space_pressed:
                    #print("Space is still pressed, waiting for release")
                    self.waiting_for_space_release = True
                    self.pending_dialog = next_node
                else:
                    #print("Activating next dialog immediately")
                    next_node.dialog.activate()
            else:
                print("All dialogs completed, stopping chain")
                self.stop_chain()
    
    def is_node_completed(self, node):
        """Проверяет завершен ли узел"""
        if isinstance(node.dialog, Dialog):
            result = node.dialog.completed
            #print(f"  Dialog completed={result}")
            return result
        elif isinstance(node.dialog, ChoiceDialogPart):
            result = node.dialog.completed or (node.dialog.choiced and not node.dialog.active)
            #print(f"  ChoiceDialogPart completed={result}, choiced={node.dialog.choiced}, active={node.dialog.active}")
            return result
        return False
    
    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        """Отрисовка текущего диалога"""
        if not self.active or not self.current_chain:
            return
        
        if self.current_index < len(self.current_chain):
            current_node = self.current_chain[self.current_index]
            current_node.draw(display, rect, mouseCoords, mouseBtn, space_pressed)
    
    def stop_chain(self):
        """Остановка цепочки"""
        print("=== Stopping chain ===\n")
        self.active = False
        self.current_chain = None
        self.current_index = 0
        self.space_handled = False
        self.mouse_handled = False
        self.waiting_for_space_release = False
        self.pending_dialog = None
    
    def is_active(self):
        """Возвращает активна ли система"""
        return self.active