# -*- coding: utf8 -*-
import pygame, math, vector, game_object, AUTSball

pygame.init()
win = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Angle finding test")

class TestBall(AUTSball.BallSprite):
    def __init__(self, level):
        AUTSball.BallSprite.__init__(self, level=level)
        self.gravity_affects = 0
        self.start_position = 400, 300

class EmptyLevel(pygame.sprite.Sprite):
    """ Level-classi. Käytännössä vain taustakuva, logiikka tapahtuu muualla. """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, AUTSball.LevelGroup)
        # self.image = pygame.image.load('gfx/test_arena_2400x1200.png').convert_alpha()
        self.image = pygame.Surface(800, 600)
        self.size_x = self.image.get_width()
        self.size_y = self.image.get_height()
        self.rect = self.image.get_rect()
        self.center_point = self.size_x // 2, self.size_y // 2

def show_text(pos, text, color=(255, 255, 255), bgcolor=(0, 0, 0), fontSize=24):
    """ Utility-metodi tekstin näyttämiseen ruudulla """
    global win
    font = pygame.font.Font(None, fontSize)
    textimg = font.render(text, 1, color, bgcolor)
    win.blit(textimg, pos)


center_point = (400,300)

yellow = (255, 255, 0)
red = (255, 0, 0)

level = EmptyLevel()
ball = TestBall(level=level)
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_position = pygame.mouse.get_pos()


    win.fill(0)



    show_text((10,10), str(center_point) + " - " + str(mouse_position))

    pygame.display.flip()
    clock.tick(30)

pygame.exit()