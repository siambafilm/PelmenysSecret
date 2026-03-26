import pygame as pg
from dialog import *

pg.init() #initialize lib
WIDTH = 800
HEIGHT = 600
display = pg.display.set_mode((WIDTH, HEIGHT),pg.RESIZABLE) #make window 
pg.display.set_caption("Super game")
clock = pg.time.Clock()


#characters
pers_dialog_face = pg.image.load('pics/main_person/dialogFace.png').convert_alpha()
pers_dialog_face_rect = pers_dialog_face.get_rect()
pers = Character("Pers", pers_dialog_face, pers_dialog_face_rect)

#definitions
cur_w = WIDTH
cur_h = HEIGHT
mouse_coords = (0,0)
mouse_coords_pressed = (0,0)
mouse_btn = 0
space_pressed = False
e_pressed = False

#dialogs
steps1 = [Replique(pers, "sosiska"), Replique(pers, "iriska"), Replique(pers, "piska")]
dial1 = Dialog(steps1)
step2 = ChoiseStep(['a', 'b', 'c'], [Replique(pers, "u touched a"), Replique(pers, 'u touched b'), Replique(pers, 'u touched c')])
dial2 = ChoiceDialogPart(step2)

dialogs = [
    dial1,
    dial2
]
cur_dialog = -1

run = True
while run:
    #fps
    clock.tick(60)
    
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
            if e.key == pg.K_e:
                e_pressed = True
            if e.key == pg.K_SPACE:
                space_pressed = True

        if e.type == pg.KEYUP:
            if e.key == pg.K_SPACE:
                space_pressed = False
            if e.key == pg.K_e:
                e_pressed = False

        if e.type == pg.MOUSEMOTION:
            mouse_coords = e.pos

        if e.type == pg.MOUSEBUTTONDOWN:
            mouse_coords_pressed = e.pos
            mouse_btn = e.button
        if e.type == pg.MOUSEBUTTONUP:
            mouse_coords_pressed = (-1,-1)
            mouse_btn = 0


    #logics

    if(e_pressed):
        #for test
        cur_dialog = 1
        if(cur_dialog != -1):
            if(not dialogs[cur_dialog].active):
                dialogs[cur_dialog].activate()
            


    #graphics
    pg.draw.rect(display, (255,255,255), (0,0,cur_w,cur_h)) #background
    

    if(cur_dialog != -1):
        dialogs[cur_dialog].draw(display, (20,cur_h-160,cur_w-40,140), mouse_coords, mouse_btn, space_pressed)

    pg.display.update()

pg.quit()