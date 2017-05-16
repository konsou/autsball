# -*- coding: utf8 -*-
import pygame
import groups
import text
from colors import *
from constants import *
from assets import assets, assets_rot, load_assets


class Level(pygame.sprite.Sprite):
    """ Level-classi. Käytännössä vain taustakuva, logiikka tapahtuu muualla. """
    # def __init__(self, image_file=None, image=None, group=groups.LevelGroup, background_image_file=None):
    def __init__(self, level_name=None, group=groups.LevelGroup, colorkey=BLACK):
        pygame.sprite.Sprite.__init__(self, group)

        # Ladataan levelin tiedot xml-filestä.
        root = text.read_xml('xml/level.xml')
        current_level = root.find(".//level[@name='"+level_name+"']")

        # print 'Level "' + level_name + '" info found'
        # Levelin nimi
        self.name = level_name

        # Level-kuva
        # self.image = pygame.image.load(current_level.find('images/level-image').text).convert()
        self.image = assets[current_level.find('images/level-image').text]
        # Määritetään alpha pois (asset loaderi ottaa kaikkeen alphan vakiona päälle) että voi laittaa colorkeyn
        self.image.set_alpha(None)
        self.image.set_colorkey(colorkey)

        # Background - jos levelin tiedoista ei löydy niin ladataan mustaa pintaa tilalle
        try:
            background_image = assets[current_level.find('images/background').text]
            background_image.set_alpha(None)
        except AttributeError:
            background_image = pygame.Surface((50, 50))
            # background_image = pygame.image.load('gfx/cave_background.png').convert()
        try:
            self.off_level_image = assets[current_level.find('images/off-level').text]
            self.off_level_image.set_alpha(None)
        except AttributeError:
            self.off_level_image = pygame.Surface((50, 50))
            # self.off_level_image = pygame.image.load('gfx/cave_indestructible_rock.png').convert()

        # Levelin koko, rect, center_point
        self.size_x = self.image.get_width()
        self.size_y = self.image.get_height()
        self.rect = self.image.get_rect()
        self.center_point = self.size_x // 2, self.size_y // 2

        if background_image is not None:
            # background_image.set_colorkey(BLACK)
            #generoidaan taustakuva
            #background_image = pygame.image.load(background_image_file).convert_alpha()
            self.background_image = pygame.Surface((self.size_x, self.size_y))
            surface_rect = self.background_image.get_rect()
            image_rect = background_image.get_rect()
            for x in range(0, surface_rect.width, image_rect.width):
                for y in range(0, surface_rect.height, image_rect.height):
                    self.background_image.blit(background_image, (x, y))

        # Generoidaan ulkopuolinen aines
        self.off_level_surface = pygame.Surface((self.size_x+WINDOW_SIZE[0], self.size_y+WINDOW_SIZE[1]),
                                                pygame.HWSURFACE)
        surface_rect = self.off_level_surface.get_rect()
        image_rect = self.off_level_image.get_rect()
        for x in range(0, surface_rect.width, image_rect.width):
            for y in range(0, surface_rect.height, image_rect.height):
                self.off_level_surface.blit(self.off_level_image, (x, y))
        if self.background_image:
            self.off_level_surface.blit(self.background_image,
                                        (WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2, self.size_x, self.size_y))
        else:
            self.off_level_surface.fill(BLACK, (WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2, self.size_x, self.size_y))
        self.off_level_surface.set_colorkey(BLACK)

        # Gravity
        self.gravity = float(current_level.find('gravity').text)

        # Spawn pointit
        self.player_spawns = {'red': [], 'green': []}
        self.ball_spawns = []

        for current_spawn in current_level.find('player_spawns').find('team_red'):
            self.player_spawns['red'].append((int(current_spawn.attrib['x']), int(current_spawn.attrib['y'])))
        for current_spawn in current_level.find('player_spawns').find('team_green'):
            self.player_spawns['green'].append((int(current_spawn.attrib['x']), int(current_spawn.attrib['y'])))
        for current_spawn in current_level.find('ball_spawns'):
            self.ball_spawns.append((int(current_spawn.attrib['x']), int(current_spawn.attrib['y'])))
