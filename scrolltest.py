# -*- coding: utf8 -*-
import pygame, math, time
import numpy as np

PlayerGroup = pygame.sprite.Group()
LevelGroup = pygame.sprite.Group()

class Level(pygame.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        pygame.sprite.Sprite.__init__(self, LevelGroup)
        self.image = pygame.image.load('testlevel.png').convert_alpha()
        self.rect = self.image.get_rect()
    def scroll(self, scroll_x=0, scroll_y=0):
        self.image.scroll(scroll_x, scroll_y)

def main():
    # Pygame-ikkunan luonti
    pygame.init()
    win = pygame.display.set_mode((800, 600))

    pygame.display.set_caption("AUTSball")

    current_level = Level()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[pygame.K_UP]:
            current_level.scroll(0, 5)
        if pressed_keys[pygame.K_DOWN]:
            current_level.scroll(0, -5)
        if pressed_keys[pygame.K_RIGHT]:
            current_level.scroll(-5, 0)
        if pressed_keys[pygame.K_LEFT]:
            current_level.scroll(5, 0)


        win.fill((0, 0, 0))
        LevelGroup.draw(win)
        pygame.display.update()
        time.sleep(0.03) #~30fps






if __name__ == '__main__':
    main()
