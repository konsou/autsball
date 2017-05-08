# -*- coding: utf8 -*-
import pygame
import groups
import text
from colors import *
from constants import *
import xml.etree.ElementTree as ET


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
        self.image = pygame.image.load(current_level.find('image').text).convert()
        self.image.set_colorkey(colorkey)

        # Background - None jos ei ole määritetty
        try:
            self.background_image = pygame.image.load(current_level.find('background').text).convert()
        except AttributeError:
            self.background_image = None

        # Gravity
        self.gravity = float(current_level.find('gravity').text)

        # Levelin koko, rect, center_point
        self.size_x = self.image.get_width()
        self.size_y = self.image.get_height()
        self.rect = self.image.get_rect()
        self.center_point = self.size_x // 2, self.size_y // 2

        # Spawn pointit
        self.player_spawns = {'red': [], 'green': []}
        self.ball_spawns = []

        for current_spawn in current_level.find('player_spawns').find('team_red'):
            self.player_spawns['red'].append((int(current_spawn.attrib['x']), int(current_spawn.attrib['y'])))
        for current_spawn in current_level.find('player_spawns').find('team_green'):
            self.player_spawns['green'].append((int(current_spawn.attrib['x']), int(current_spawn.attrib['y'])))
        for current_spawn in current_level.find('ball_spawns'):
            self.ball_spawns.append((int(current_spawn.attrib['x']), int(current_spawn.attrib['y'])))
