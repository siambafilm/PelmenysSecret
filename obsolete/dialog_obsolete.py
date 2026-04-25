from step import Replique, ChoiseStep, Character
import pygame as pg
import time
from typing import List,Union,Optional

pg.init()

dialog_name_font = pg.font.SysFont('Arial', 12)
dialog_text_font = pg.font.SysFont('Arial', 20)

def draw_text_wrapped(surface, text, font, color, rect):
    words = text.split(' ')
    y = rect.top
    line_height = font.get_height()

    while words:
        line = []
        while words and font.size(' '.join(line + [words[0]]))[0] <= rect.width:
            line.append(words.pop(0))

        if not line:
            line.append(words.pop(0))

        line_surface = font.render(' '.join(line), True, color)
        surface.blit(line_surface, (rect.left, y))
        y += line_height

        if(y+line_height > rect.bottom):
            break


class Dialog:
    def __init__(self, steps: list):
        self.active = False
        self.steps = steps
        self.i = -1
        self.space_handled = False
        self.completed = False
    
    def next(self):
        if(self.active and not self.completed):
            self.i += 1
            print(self.i)
            if(self.i >= len(self.steps)):
                print('Dialog completed')
                self.completed = True
                self.deactivate()
            else:
                self.cur_step = self.steps[self.i]
    
    def activate(self):
        if(not self.active and not self.completed):
            self.active = True
            self.space_handled = False
            print('dialog activated')
            self.next()
        
    def deactivate(self):
        if(self.active):
            self.active = False
            print('dialog deactivated')
            self.space_handled = False
            
    def reset(self):
        if(self.active):
            print('dialog reset')
            self.active = False
            self.i = -1
            self.space_handled = False
            self.completed = False


    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        if(self.active and not self.completed):
            image = self.cur_step.character.dialog_picture
            image_rect = self.cur_step.character.rect
            name = self.cur_step.character.name
            text = self.cur_step.text

            pg.draw.rect(display, (100,100,100), rect) #main rect
            pg.draw.rect(display, (255,255,255), (rect[0]+20,rect[1]+20,rect[2]-40,rect[3]-40)) #white rect
            #image
            image_rect.center = (rect[0]+30+(image_rect.width//2), rect[1]+(rect[3]//2)-5)
            display.blit(image, image_rect)
            #text
            name_surface = dialog_name_font.render(name, False, (0,0,0))
            name_rect = name_surface.get_rect()
            name_rect.center = (image_rect.x + (image_rect.width//2), image_rect.y+image_rect.height+7)
            display.blit(name_surface, name_rect)
            draw_text_wrapped(display, text, dialog_text_font, (0,0,0), pg.Rect((image_rect.x + image_rect.width + 20), rect[1]+25, rect[2]-160, rect[3]-50 ))

            if space_pressed and not self.space_handled:
                self.space_handled = True
                self.next()
            elif not space_pressed:
                self.space_handled = False


class ChoiceDialogPart:
    def __init__(self, step: ChoiseStep):
        self.step = step
        self.active = False
        self.choiced = False
        self.choice = -1
        self.completed = False

    def activate(self):
        if(not self.active and not self.completed):
            self.active = True
            print('activated choice')
        
    def deactivate(self):
        if(self.active):
            self.active = False
            self.choiced = False
            self.choice = -1
            self.completed = True
            print('choice completed')

    def reset(self):
        self.completed = False
        self.active = False
        self.choiced = False
        self.choice = -1

    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        if(self.active and not self.completed):
            pg.draw.rect(display, (100,100,100), rect) #main rect
            pg.draw.rect(display, (255,255,255), (rect[0]+20,rect[1]+20,rect[2]-40,rect[3]-40)) #white rect
            #choices
            if(not self.choiced):
                choices = self.step.choices
                y = rect[1]+30
                hgh = 20
                hghgstep = 10
                for i in range(len(self.step.choices)):
                    pg.draw.rect(display, (150,150,150), (rect[0]+30,y,rect[2]-50, hgh)) #choise rect
                    text_surface = dialog_text_font.render(choices[i], False, (0,0,0))
                    text_rect = text_surface.get_rect()
                    text_rect.center = (pg.Rect(rect).centerx, y+(hgh//2))
                    display.blit(text_surface, text_rect)
                    y += hgh+hghgstep

                #check choice
                y = rect[1]+30
                if(mouseBtn == 1 and (mouseCoords[0] in range(rect[0]+30, rect[0]+rect[2]-20))):
                    for i in range(len(self.step.choices)):
                        if(mouseCoords[1] in range(y + hghgstep*i + hgh*i, y + hghgstep*i + hgh*(i+1))):
                            self.choiced = True
                            self.choice = i
            
            if(self.choiced):
                after = self.step.replicsAfter
                image = after[self.choice].character.dialog_picture
                image_rect = after[self.choice].character.rect
                name = after[self.choice].character.name
                text = after[self.choice].text
                #image
                image_rect.center = (rect[0]+30+(image_rect.width//2), rect[1]+(rect[3]//2)-5)
                display.blit(image, image_rect)
                #text
                name_surface = dialog_name_font.render(name, False, (0,0,0))
                name_rect = name_surface.get_rect()
                name_rect.center = (image_rect.x + (image_rect.width//2), image_rect.y+image_rect.height+7)
                display.blit(name_surface, name_rect)
                draw_text_wrapped(display, text, dialog_text_font, (0,0,0), pg.Rect((image_rect.x + image_rect.width + 20), rect[1]+25, rect[2]-160, rect[3]-50 ))
                
                if space_pressed:
                    self.deactivate()


class DialogNode:
    def __init__(self, dialog, next_node = None):
        self.dialog = dialog
        self.next_node = next_node
        self.completed = False

    def update(self, space_pressed: bool, mouse_pos: tuple, mouse_btn: int) -> bool:
        '''if(not self.dialog.active):
            self.dialog.activate()

        if isinstance(self.dialog, Dialog):
            if(self.dialog.i >= len(self.dialog.steps)-1 and self.dialog.active):
                pass
            elif(self.dialog.i >= len(self.dialog.steps)):
                return True
        elif isinstance(self.dialog, ChoiceDialogPart):
            if(self.dialog.choiced):
                return True
            
        return False'''
        return self.dialog.completed
    
    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        self.dialog.draw(display,rect,mouseCoords,mouseBtn,space_pressed)

    def reset(self):
        self.dialog.reset()
        self.completed = False

class DialogSystem:
    def __init__(self):
        self.current_chain = None
        self.current_index = 0
        self.active = False
        self.space_handled = False
        self.mouse_handled = False

    def start_chain(self, chain: List[Union[Dialog,ChoiceDialogPart]]):
        self.current_chain = []
        for item in chain:
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

        if(self.current_chain):
            self.current_chain[0].dialog.activate()

    def update(self,space_pressed: bool, mouse_pos: tuple, mouse_btn: int):
        if not self.active or not self.current_chain:
            return
        if(self.current_index >= len(self.current_chain)):
            self.stop_chain()
            print('chain finished')
            return
        
        if(hasattr(self, 'waiting_for_space_release') and self.waiting_for_space_release):
            if not space_pressed:
                self.waiting_for_space_release = False
                if(hasattr(self, 'pending_dialog')):
                    self.pending_dialog.dialog.activate()
                    self.pending_dialog = None
                return

        current_node = self.current_chain[self.current_index]

        space_triggered = space_pressed and not self.space_handled
        if(space_pressed):
            self.space_handled = True
        else: 
            self.space_handled = False

        mouse_triggered = (mouse_btn == 1) and not self.mouse_handled
        if(mouse_btn==1):
            self.mouse_handled=True
        elif(mouse_btn==0):
            self.mouse_handled = False

        current_node.update(space_triggered, mouse_pos, mouse_triggered)

        completed = self.is_node_completed(current_node)

        if(completed):
            print('node completed')
            self.current_index += 1

            if(self.current_index < len(self.current_chain)):
                next_node = self.current_chain[self.current_index]
                self.space_handled = False
                self.mouse_handled = False
                if (not space_pressed):
                    next_node.dialog.activate()
                    print('activate next')
                else:
                    self.waiting_for_space_release = True
                    self.pending_dialog = next_node

            else:
                print('all completed')
                self.stop_chain()

    def is_node_completed(self, node: DialogNode) -> bool:
        if(isinstance(node.dialog, Dialog)):
            return node.dialog.completed
        elif(isinstance(node.dialog, ChoiceDialogPart)):
            return node.dialog.choiced and not node.dialog.active
        return False
    
    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        if(not self.active or not self.current_chain):
            return
        if(self.current_index < len(self.current_chain)):
            current_node = self.current_chain[self.current_index]
            current_node.draw(display,rect, mouseCoords, mouseBtn, space_pressed)

    def stop_chain(self):
        self.active = False
        self.current_chain = None
        self.current_index = 0
        self.space_handled = False
        self.mouse_handled = False
    
    def is_active(self) -> bool:
        return self.active