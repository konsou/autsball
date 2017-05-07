# -*- coding: utf8 -*-
import pygame
import groups
import text
import xml.etree.ElementTree as ET
from colors import *
from constants import *

class Level(pygame.sprite.Sprite):
    """ Level-classi. Käytännössä vain taustakuva, logiikka tapahtuu muualla. """
    # def __init__(self, image_file=None, image=None, group=groups.LevelGroup, background_image_file=None,

    def __init__(self, level_name=None, group=groups.LevelGroup,
                 colorkey=BLACK):
        pygame.sprite.Sprite.__init__(self, group)

        # Yritetään ladata tiedot xml-filestä.
        if not self.load_from_xml(level_name):
            # Jos ei onnistu niin mennään näillä arvoilla:

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
            self.background_image = pygame.image.load('gfx/cave_background.png').convert_alpha()
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
            if self.background_image:
                self.off_level_surface.blit(self.background_image, (WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2, self.size_x, self.size_y))
            else:
                self.off_level_surface.fill(BLACK, (WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2, self.size_x, self.size_y))
            self.off_level_surface.set_colorkey(BLACK)

    def destroy_land(self, pixels_to_destroy):
        for pixel in pixels_to_destroy:
            self.image.set_at(pixel, pygame.Color(0, 0, 0, 0))

    def load_from_xml(self, level_name):
        level_found = 0
        root = text.read_xml('xml/level.xml')
        current_level = root.find(".//level[@name='"+level_name+"']")
        if current_level is not None:
            level_found = 1
            print 'Level "' + level_name + '" info found'
            self.name = level_name
            self.image = pygame.image.load(current_level.find('image').text).convert_alpha()
            try:
                self.background_image = pygame.image.load(current_level.find('background').text).convert_alpha()
            except AttributeError:
                self.background_image = None
            self.gravity = float(current_level.find('gravity').text)

            self.size_x = self.image.get_width()
            self.size_y = self.image.get_height()
            self.rect = self.image.get_rect()
            self.center_point = self.size_x // 2, self.size_y // 2

            self.player_spawns_team_1 = []
            self.player_spawns_team_2 = []

            for current_spawn in current_level.find('player_spawns').find('team1'):
                self.player_spawns_team_1.append((int(current_spawn.attrib['x']), int(current_spawn.attrib['y'])))
            for current_spawn in current_level.find('player_spawns').find('team2'):
                self.player_spawns_team_2.append((int(current_spawn.attrib['x']), int(current_spawn.attrib['y'])))

        return level_found