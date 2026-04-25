import pygame as pg

pg.init() #initialize lib
display = pg.display.set_mode((800, 600)) #make window 800*600
pg.display.set_caption("Super game")

#definitions
mouse_coords = (0,0)
mouse_btns = (0,0,0)
radius = 20.0
coords = (radius,radius)
draw = False

#first draw
pg.draw.rect(display, (100,100,100), (0,0,800,600))
pg.draw.circle(display, (255,0,0), coords, radius)

run = True
while run:
    
    #events
    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False

        if e.type == pg.KEYDOWN:
            print(e.key, e.mod)

        if e.type == pg.MOUSEMOTION:
            print(e)
            mouse_coords = e.pos
            mouse_btns = e.buttons


    #logics
    if(coords[0]-radius <= mouse_coords[0] <= coords[0]+radius):
        if(coords[1]-radius <= mouse_coords[1] <= coords[1]+radius):
            if(mouse_btns == (1,0,0)):
                coords = mouse_coords
                draw = True
            


    #graphics
    if(draw):
        pg.draw.rect(display, (100,100,100), (0,0,800,600))
        pg.draw.circle(display, (255,0,0), coords, radius)

    pg.display.update()

pg.quit()