import pygame as pg
from dialog import Replique, ChoiseStep, Character, Dialog, ChoiceDialogPart

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
mouse_coords = (0,0)
mouse_coords_pressed = (0,0)
mouse_btn = 0
space_pressed = False
e_pressed = False

#dialogs
steps1 = ChoiseStep(['a', 'b', 'c'], [Replique(pers, "u touched a"), Replique(pers, 'u touched b'), Replique(pers, 'u touched c')])
dial1 = ChoiceDialogPart(steps1)

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
        if(not dialog_start):
            dialog_start = True

    #graphics
    pg.draw.rect(display, (255,255,255), (0,0,cur_w,cur_h)) #background
    if(dialog_start):
        dial1.activate()
        dialog_start = False
    
    
    dial1.draw(display, (20,cur_h-160,cur_w-40,140), mouse_coords, mouse_btn, space_pressed)

    pg.display.update()

pg.quit()