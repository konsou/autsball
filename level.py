# -*- coding: utf8 -*-
import pygame
import groups
from colors import *


class Level(pygame.sprite.Sprite):
    """ Level-classi. Käytännössä vain taustakuva, logiikka tapahtuu muualla. """
    def __init__(self, image_file=None, image=None, group=groups.LevelGroup, background_image_file=None,
                 colorkey=BLACK):
        pygame.sprite.Sprite.__init__(self, group)

        # Level-imagen lataus
        if image is not None:
            self.image = image
        elif image_file is not None:
            self.image = pygame.image.load(image_file).convert()
        else:
            self.image = pygame.image.load('gfx/test_arena_vertical_challenge_alpha.png').convert()

        # Colorkey eli musta on transparent
        self.image.set_colorkey(colorkey)

        self.size_x = self.image.get_width()
        self.size_y = self.image.get_height()
        self.rect = self.image.get_rect()
        self.center_point = self.size_x // 2, self.size_y // 2
        self.player_spawns_team_1 = [(700, 1200), (400, 1200), (500, 1000)]

        self.background_image = None
        if background_image_file:
            self.background_image = pygame.image.load(background_image_file).convert_alpha()

    def destroy_land(self, pixels_to_destroy):
        for pixel in pixels_to_destroy:
            self.image.set_at(pixel, pygame.Color(0, 0, 0, 0))
