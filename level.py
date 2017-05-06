# -*- coding: utf8 -*-
import pygame
import groups
from colors import *
from constants import *

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
            #generoidaan taustakuva
            background_image = pygame.image.load(background_image_file).convert_alpha()
            self.background_image = pygame.Surface((self.size_x, self.size_y))
            surface_rect = self.background_image.get_rect()
            image_rect = background_image.get_rect()
            for x in range(0, surface_rect.width, image_rect.width):
                for y in range(0, surface_rect.height, image_rect.height):
                    self.background_image.blit(background_image, (x, y))

        # Generoidaan ulkopuolinen aines
        self.off_level_image = pygame.image.load('gfx/cave_indestructible_rock.png').convert()
        self.off_level_surface = pygame.Surface((self.size_x+WINDOW_SIZE[0], self.size_y+WINDOW_SIZE[1]))
        surface_rect = self.off_level_surface.get_rect()
        image_rect = self.off_level_image.get_rect()
        for x in range(0, surface_rect.width, image_rect.width):
            for y in range(0, surface_rect.height, image_rect.height):
                self.off_level_surface.blit(self.off_level_image, (x, y))
        self.off_level_surface.fill(BLACK, (WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2, self.size_x, self.size_y))
        self.off_level_surface.set_colorkey(BLACK)

    def destroy_land(self, pixels_to_destroy):
        for pixel in pixels_to_destroy:
            self.image.set_at(pixel, pygame.Color(0, 0, 0, 0))
