# -*- coding: utf8 -*-
import pygame
import groups
import text
import xml.etree.ElementTree as ET


class Level(pygame.sprite.Sprite):
    """ Level-classi. Käytännössä vain taustakuva, logiikka tapahtuu muualla. """
    # def __init__(self, image_file=None, image=None, group=groups.LevelGroup, background_image_file=None):
    def __init__(self, level_name=None, group=groups.LevelGroup):
        pygame.sprite.Sprite.__init__(self, group)

        if not self.load_from_xml(level_name):
            # Level-imagen lataus
            self.image = pygame.image.load('gfx/test_arena_vertical_challenge_alpha.png').convert_alpha()

            self.size_x = self.image.get_width()
            self.size_y = self.image.get_height()
            self.rect = self.image.get_rect()
            self.center_point = self.size_x // 2, self.size_y // 2
            self.player_spawns_team_1 = [(700, 1200), (400, 1200), (500, 1000)]

            self.background_image = None
            self.background_image = pygame.image.load('gfx/cave_background.png').convert_alpha()

    def load_from_xml(self, level_name):
        level_found = 0
        root = text.read_xml('xml/level.xml')
        for current_level in root.findall('level'):
            if current_level.attrib['name'] == level_name:
                print "Level", level_name, "info found"
                level_found = 1
                self.name = level_name
                self.image = pygame.image.load(current_level.find('image').text).convert_alpha()
                try:
                    self.background_image = pygame.image.load(current_level.find('background').text).convert_alpha()
                except AttributeError:
                    self.background_image = None
                self.gravity = current_level.find('gravity').text

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
                break
        return level_found