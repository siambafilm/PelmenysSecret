from step import Replique, ChoiseStep, Character
import pygame as pg
import time

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
    
    def next(self):
        if(self.active):
            self.i += 1
            if(self.i >= len(self.steps)):
                self.deactivate()
            else:
                self.cur_step = self.steps[self.i]
    
    def activate(self):
        if(not self.active):
            self.active = True
            self.next()
        
    def deactivate(self):
        if(self.active):
            self.active = False
            self.i = -1


    def draw(self, display, rect):
        if(self.active):
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



class ChoiceDialogPart:
    def __init__(self, step: ChoiseStep):
        self.step = step
        self.active = False
        self.choiced = False
        self.choice = -1

    def activate(self):
        if(not self.active):
            self.active = True
        
    def deactivate(self):
        if(self.active):
            self.active = False
            self.choiced = False
            self.choice = -1

    def draw(self, display, rect, mouseCoords, mouseBtn, space_pressed):
        if(self.active):
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
                
                if(space_pressed):
                    self.deactivate()