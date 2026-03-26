import pygame as pg
from dialog import Replique, ChoiseStep, Character, Dialog

pg.init() #initialize lib
WIDTH = 800
HEIGHT = 600
display = pg.display.set_mode((WIDTH, HEIGHT),pg.RESIZABLE) #make window 800*600
pg.display.set_caption("Super game")


#characters
pers_dialog_face = pg.image.load('pics/main_person/dialogFace.png').convert_alpha()
pers_dialog_face_rect = pers_dialog_face.get_rect()
pers = Character("Pers", pers_dialog_face, pers_dialog_face_rect)

#definitions
dialog_start = False
cur_w = WIDTH
cur_h = HEIGHT

#dialogs
steps1 = [Replique(pers, "sosiska"), Replique(pers, "iriska"), Replique(pers, "piska")]
dial1 = Dialog(steps1)

run = True
while run:
    
    #events
    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False

        if e.type == pg.VIDEORESIZE:
            new_w = max(e.w, WIDTH)
            new_h = max(e.h, HEIGHT)
            display = pg.display.set_mode((new_w, new_h), pg.RESIZABLE)
            cur_w = display.get_rect().width
            cur_h = display.get_rect().height

        if e.type == pg.KEYDOWN:
            if e.key == pg.K_SPACE:
                #next = True
                dial1.next()
                print(e)
            if e.key == pg.K_e:
                if(not dialog_start):
                    dialog_start = True
        else:
            next = False

        if e.type == pg.MOUSEMOTION:
            #print(e)
            mouse_coords = e.pos
            mouse_btns = e.buttons


    #logics

    
    #dialog 1
    replics = [
        ["pers"]
    ]
            


    #graphics
    pg.draw.rect(display, (255,255,255), (0,0,cur_w,cur_h)) #background
    if(dialog_start):
        dial1.activate()
        dialog_start = False
    
    #if(next):
    #    next = False
    #    dial1.next()
    
    dial1.draw(display, (20,cur_h-160,cur_w-40,140))

    pg.display.update()

pg.quit()