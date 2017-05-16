# -*- coding: utf8 -*-
import pygame
import groups
import string
import random
import xml.etree.ElementTree as ET
from colors import *
from assets import assets

num_images = {}
last_scores = [0, 0]
last_score_images = [None, None]


def init_scores():
    global last_score_images
    for i in range(0, 10):
        num_images[i] = assets['gfx/num_%d.png' % i]
    last_score_images = [num_images[0], num_images[0]]


def show_text(win, pos, text, color=(255, 255, 255), bgcolor=(0, 0, 0), font_size=24):
    """ Utilityfunktio tekstin näyttämiseen ruudulla """
    font = pygame.font.Font(None, font_size)
    textimg = font.render(text, 1, color, bgcolor)
    win.blit(textimg, pos)


def show_score(win, pos, score, team):
    if score != last_scores[team]:
        last_scores[team] = score
        score_numbers = map(int, str(score))
        score_image = pygame.Surface((len(score_numbers)*32, 64), pygame.HWSURFACE)
        score_image.set_colorkey(BLACK)
        i = 0
        for number in score_numbers:
            score_image.blit(num_images[number], (i*32, 0))
            i += 1
        last_score_images[team] = score_image
        win.blit(score_image, pos)
    else:
        win.blit(last_score_images[team], pos)


class DisappearingText(pygame.sprite.Sprite):
    """ Näyttää ruudulla tekstin x framen ajan """
    def __init__(self, group=groups.TextGroup, pos=(0,0), text="", frames_visible=60,
                 color=WHITE, bgcolor=None, font_size=24, flashes=0, flash_interval=10):
        pygame.sprite.Sprite.__init__(self, group)

        self.frame_counter = 0
        self.frames_visible = frames_visible

        font = pygame.font.Font(None, font_size)
        self.image = font.render(text, 1, color)#, bgcolor)
        self.original_position = pos
        self.rect = self.image.get_rect()
        self.rect.center = pos

        self.flashes = flashes
        self.flash_interval = flash_interval
        self.visible = 1

    def update(self):
        self.frame_counter += 1
        if self.frame_counter > self.frames_visible:
            self.kill()

        if self.flashes and self.frame_counter % self.flash_interval == 0:
            self.toggle_image()

    def toggle_image(self):
        if self.visible:
            self.visible = 0
            self.rect.center = -100, -100
        else:
            self.visible = 1
            self.rect.center = self.original_position


class ScrollingText(pygame.sprite.Sprite):
    """ Scrollaa tekstiä ruudulla """
    def __init__(self, group=groups.TextGroup, y_pos=0, screen_size_x=800, text="", scroll_direction='left', scroll_speed=5,
                 color=WHITE, bgcolor=None, font_size=24, flashes=0, flash_interval=10):
        pygame.sprite.Sprite.__init__(self, group)

        self.frame_counter = 0

        font = pygame.font.Font(None, font_size)
        self.image = font.render(text, 1, color)#, bgcolor)
        self.original_image = self.image
        self.empty_image = pygame.Surface((0, 0))
        self.rect = self.image.get_rect()
        self.screen_size_x = screen_size_x

        self.scroll_direction = scroll_direction

        if scroll_direction == 'left':
            self.rect.midleft = screen_size_x, y_pos
            self.original_position = self.rect.midleft
            self.scroll_speed = scroll_speed * -1
        else:
            self.rect.midright = 0, y_pos
            self.original_position = self.rect.midright
            self.scroll_speed = scroll_speed

        self.flashes = flashes
        self.flash_interval = flash_interval
        self.visible = 1

    def update(self):
        self.rect.x += self.scroll_speed
        if self.scroll_direction == 'left':
            if self.rect.midright[0] < 0:
                self.rect.midleft = self.original_position
        else:
            if self.rect.midleft[0] > self.screen_size_x:
                self.rect.midright = self.original_position

        if self.flashes:
            self.frame_counter += 1
            if self.frame_counter % self.flash_interval == 0:
                self.toggle_image()

    def toggle_image(self):
        if self.visible:
            self.visible = 0
            self.image = self.empty_image
        else:
            self.visible = 1
            self.image = self.original_image


def credits_reader(creditsfile='CREDITS'):
    """ 
    Lukee CREDITS-tiedostosta creditsit dictiin ja palauttaa sen, ignoroi kommenttirivit ja tyhjät rivit
    Lisää keyn alkuun osion järjestysnumeron. Jos numero on alle 10, sen alkuun lisätään nolla.
     
    Dictin formaatti:
    {'(järjestysnumero)Osion otsikko': ['lista', 'osiossa', 'olevista', 'nimistä']}
    Esim:
    {'00Idea': ['Konso'], '01Code': ['Konso', 'Tursa', 'Muumi']}
    """
    return_dict = {}
    current_section = ''
    current_section_number = 0
    fileobject = open(creditsfile)
    contents = fileobject.readlines()
    fileobject.close()
    for current_line in contents:
        current_line = string.rstrip(current_line)
        if len(current_line) > 0 and current_line[0] != '#':
            if current_line[-1:] == ':':
                if current_section_number < 10:
                    section_number_string = '0' + str(current_section_number)
                else:
                    section_number_string = str(current_section_number)
                current_section = section_number_string + current_line[:-1]
                current_section_number += 1
            else:
                if len(current_line) > 0:
                    try:
                        return_dict[current_section].append(current_line)
                    except KeyError:
                        return_dict[current_section] = [current_line]
    return return_dict


def make_credits_string(creditsfile='CREDITS', numspaces=30):
    """ 
    Lukee CREDITS-tiedostosta creditsit ja tekee niistä yhden stringin
    Osiot tulee siinä järjestyksessä kuin CREDITS-tiedostossa
    Randomoi nimien järjestyksen osioiden sisällä
    Lisää osioiden väliin numspaces verran välilyöntejä
    Saattaa hieman bugata jos osioita yli 100
    """
    return_string = ''
    credits_dict = credits_reader(creditsfile)
    keys = credits_dict.keys()
    keys.sort()
    for current_key in keys:
        return_string += current_key[2:] + ":  "
        random.shuffle(credits_dict[current_key])
        return_string += ',  '.join(credits_dict[current_key])
        return_string += ' ' * numspaces
    return return_string


def read_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root

