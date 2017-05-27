# -*- coding: utf8 -*-
import pygame
import os
import time
import ui_components
from constants import *
from pygame.locals import *
from colors import *
from gloss import *


""" 
Assettien esilataaja. Vakioasetuksilla esilataa kaikki gfx- ja sfx-kansioissa olevat png- ja wav-tiedostot.
Asetuksia voi halutessaan muuttaa.

Esirotatoi kaikki kuvat, joiden koko on alle ROT_IMAGE_MAX_FILESIZE ja joita ei löydy DONT_ROTATE_IMAGES -listasta.
"""
# Tämä dict sisältää esiladatut kuvat ja äänet. Key = filename
# esim. assets['gfx/ball.png']
assets = {}
assets_mask = {}
# Tämä dict sisältää esirotatoidut kuvat. Keyt = filename ja rotaatiokulma asteina
# esim. assets_rot['gfx/ball.png'][45]
assets_rot = {}
assets_rot_mask = {}

DEBUG_TEXT = 0

INCLUDED_FOLDERS = ['gfx', 'sfx']
# HUOM! Tällaisenaan tukee vain file extensioneja, joissa on pisteen jälkeen 3 merkkiä. Jos on muunlaisia (.jpeg?)
# niin korjaa koodia.
INCLUDED_IMAGE_EXTENSIONS = ['.png']
# ogg-filuja ei esiladata koska pygame streamaa ne suoraan tiedostoista
INCLUDED_SOUND_EXTENSIONS = ['.wav']

# Vakiona rotatoidaan kaikki kuvat PAITSI:
# -ne joiden tiedoston koko on suurempi kuin tässä määritetty:
ROT_IMAGE_MAX_FILESIZE = 10240  # tavua/bytes
# -ne jotka on listattu tähän:
DONT_ROTATE_IMAGES = ['menu_background_level.png', 'ball.png', 'ball_50.png', 'ball_50_red.png',
                      'bullet.png', 'bullet_5.png', 'bullet_10.png']


def load_assets(window=None):
    if DEBUG_TEXT: start_time = time.time()

    # Latauskuva koska latauksissa voi kestää jonkin aikaa
    # TODO: Siirrä latauspalkin piirto Glossin omaan funktioon
    #loading_image = pygame.image.load('gfx/loading.png').convert()
    #window.blit(loading_image, loading_image.get_rect())
    #pygame.display.flip()

    # Lasketaan tiedostojen määrä ja koot yhteensä
    files_size_total = 0
    number_of_files = 0
    for current_directory in INCLUDED_FOLDERS:
        files_list = os.listdir(current_directory)
        for current_file in files_list:
            extension = current_file[-4:]  # tämän kohdan takia tukee vain 3-merkkisiä extensioneja
            if extension in INCLUDED_IMAGE_EXTENSIONS or extension in INCLUDED_SOUND_EXTENSIONS:
                filepath = os.path.join(current_directory, current_file)
                file_size = os.stat(filepath).st_size
                number_of_files += 1
                files_size_total += file_size
    if DEBUG_TEXT: print "Total number of files:", number_of_files
    if DEBUG_TEXT: print "Total size of files:", round(files_size_total / 1048576.0, 2), "MB"

    files_size_current = 0
    files_size_total_inc_rot = 0
    # number_of_files = 0
    number_of_rotations = 0

    for current_directory in INCLUDED_FOLDERS:
        files_list = os.listdir(current_directory)
        for current_file in files_list:
            if DEBUG_TEXT: print "---------------"
            extension = current_file[-4:]
            filepath = os.path.join(current_directory, current_file)
            asset_key = current_directory + '/' + current_file
            if extension in INCLUDED_IMAGE_EXTENSIONS:
                # Ladataan kuvatiedostot ensin
                file_size = os.stat(filepath).st_size
                if DEBUG_TEXT: print "Loading %r... (size: %r kB)" % (filepath, round(file_size / 1024.0, 2))
                # Tässä itse kuvan lataus. Vakiona aina convert_alpha().
                #assets[asset_key] = pygame.image.load(filepath).convert_alpha()
                assets[asset_key] = Texture(filepath)
                # Bitmaskiin lataus
                # TODO: Ratkaise tämä opengl:ssä jotenkin
                #assets_mask[asset_key] = pygame.mask.from_surface(assets[asset_key])
                # files_size_total += file_size
                files_size_current += file_size
                files_size_total_inc_rot += file_size
                # TODO: Siirrä latauspalkin piirto Glossin omaan funktioon
                #ui_components.draw_loading_bar(window, files_size_current, files_size_total)
                # number_of_files += 1
                """ OpenGL-tekstuureja ei tarvitse esirotatoida
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
                    # Rotatoidaan kuvaa - yhteensä 360 rotaatiota per kuva
                    if DEBUG_TEXT: print "Calculating rotations..."
                    for angle in range(360):
                        if angle == 0:
                            assets_rot[asset_key] = {}
                            assets_rot_mask[asset_key] = {}
                        assets_rot[asset_key][angle] = rot_image(assets[asset_key], angle)
                        assets_rot_mask[asset_key][angle] = pygame.mask.from_surface(assets_rot[asset_key][angle])
                        number_of_rotations += 1
                        files_size_total_inc_rot += file_size
                    if DEBUG_TEXT: print "Rotations calculated"
                """
            elif extension in INCLUDED_SOUND_EXTENSIONS:
                # Ladataan äänitiedostot sitten
                file_size = os.stat(filepath).st_size
                if DEBUG_TEXT: print "Loading %r... (size: %r kB)" % (filepath, round(file_size / 1024.0, 2))
                # Tässä itse lataus
                assets[asset_key] = pygame.mixer.Sound(file=filepath)
                # files_size_total += file_size
                files_size_current += file_size
                files_size_total_inc_rot += file_size
                # TODO: Siirrä latauspalkin piirto Glossin omaan funktioon
                #ui_components.draw_loading_bar(window, files_size_current, files_size_total)
                # number_of_files += 1
                if DEBUG_TEXT: print "Loaded %r" % filepath
                # Äänitiedostoja emme rotatoi :)
            else:
                if DEBUG_TEXT: print "Skipping", current_file, "- not in included file types"

    if DEBUG_TEXT:
        end_time = time.time()
        runtime = end_time - start_time
        print "--------------------------------------------"
        print "--------------------------------------------"
        print "                  STATS:"
        print "Loading time:", round(runtime, 2), "seconds"
        print "Total number of files loaded:", number_of_files
        print "Total size of loaded files (not including rotations):", round(files_size_total / 1048576.0, 2), "MB"
        print "Total size of loaded files (including rotations):", round(files_size_total_inc_rot / 1048576.0, 2), "MB"
        print "Total number of rotations calculated:", number_of_rotations
        print "--------------------------------------------"
        print "--------------------------------------------"


def rot_image(original_image, angle):
    """rotate an image while keeping its center and size"""
    # Tämä copypastettu jostain netistä. Vaatii että kuva on neliö.
    assert original_image.get_width() == original_image.get_height(), \
        "Can't rotate image - not square. %r" % original_image
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
