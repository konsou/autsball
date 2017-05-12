# -*- coding: utf8 -*-
import pygame
import os
import time
from constants import *
from pygame.locals import *

# Sisältää esiladatut kuvat ja äänet. Key = filename
# esim. assets['gfx/ball.png']
assets = {}
# Sisältää esirotatoidut kuvat. Keyt = filename ja rotaatiokulma
# esim. assets_rot['gfx/ball.png'][45]
assets_rot = {}

DEBUG_TEXT = 0

INCLUDED_FOLDERS = ['gfx', 'sfx']
INCLUDED_IMAGE_EXTENSIONS = ['.png']
# ogg-filuja ei esiladata koska pygame streamaa ne suoraan tiedostoista
INCLUDED_SOUND_EXTENSIONS = ['.wav']

# Vakiona rotatoidaan kaikki kuvat PAITSI:
# -ne joiden tiedoston koko on suurempi kuin tässä määritetty:
ROT_IMAGE_MAX_FILESIZE = 10240
# -ne jotka on listattu tähän:
DONT_ROTATE_IMAGES = ['menu_background_level.png', 'ball.png', 'ball_50.png', 'ball_50_red.png',
                      'bullet.png', 'bullet_5.png', 'bullet_10.png']


def load_assets(window):
    # Latauskuva koska latauksissa voi kestää jonkin aikaa
    loading_image = pygame.image.load('gfx/loading.png').convert()
    window.blit(loading_image, loading_image.get_rect())
    pygame.display.flip()

    # Lasketaan tiedostojen määrä ja koot yhteensä
    files_size_total = 0
    number_of_files = 0
    for current_directory in INCLUDED_FOLDERS:
        files_list = os.listdir(current_directory)
        for current_file in files_list:
            extension = current_file[-4:]
            if extension in INCLUDED_IMAGE_EXTENSIONS or extension in INCLUDED_SOUND_EXTENSIONS:
                filepath = os.path.join(current_directory, current_file)
                file_size = os.stat(filepath).st_size
                number_of_files += 1
                files_size_total += file_size
    if DEBUG_TEXT: print "Total number of files:", number_of_files
    if DEBUG_TEXT: print "Total size of files:", files_size_total // 1048576, "MB"

    for current_directory in INCLUDED_FOLDERS:
        files_list = os.listdir(current_directory)
        for current_file in files_list:
            if DEBUG_TEXT: print "---------------"
            extension = current_file[-4:]
            filepath = os.path.join(current_directory, current_file)
            asset_key = current_directory + '/' + current_file
            if extension in INCLUDED_IMAGE_EXTENSIONS:
                file_size = os.stat(filepath).st_size
                if DEBUG_TEXT: print "Loading %r... (size: %r kB)" % (filepath, round(file_size / 1024.0, 2))
                assets[asset_key] = pygame.image.load(filepath).convert_alpha()
                width = assets[asset_key].get_width()
                height = assets[asset_key].get_height()
                if DEBUG_TEXT: print "Loaded %r" % filepath
                if file_size > ROT_IMAGE_MAX_FILESIZE:
                    if DEBUG_TEXT: print "Not rotating - file too big"
                elif current_file in DONT_ROTATE_IMAGES:
                    if DEBUG_TEXT: print "Not rotating - image in exclusion list"
                elif width != height:
                    if DEBUG_TEXT: print "Not rotating - not rectangular"
                else:
                    if DEBUG_TEXT: print "Calculating rotations..."
                    for angle in range(360):
                        if angle == 0:
                            assets_rot[asset_key] = {}
                        assets_rot[asset_key][angle] = rot_image(assets[asset_key], angle)
                    if DEBUG_TEXT: print "Rotations calculated"
            elif extension in INCLUDED_SOUND_EXTENSIONS:
                file_size = os.stat(filepath).st_size
                if DEBUG_TEXT: print "Loading %r... (size: %r kB)" % (filepath, round(file_size / 1024.0, 2))
                assets[asset_key] = pygame.mixer.Sound(file=filepath)
                if DEBUG_TEXT: print "Loaded %r" % filepath
            else:
                if DEBUG_TEXT: print "Skipping", current_file, "- not in included file types"


def rot_image(original_image, angle):
    """rotate an image while keeping its center and size"""
    # Tämä copypastettu jostain netistä. Vaatii että kuva on neliö.
    assert original_image.get_width() == original_image.get_height(), "Can't rotate image - not square. %r" % original_image
    orig_rect = original_image.get_rect()
    rot_image = pygame.transform.rotate(original_image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

if __name__ == '__main__':
    DEBUG_TEXT = 1
    pygame.init()
    window = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
    pygame.display.set_caption("Menu test")
    load_assets(window)
    quit()
