# -*- coding: utf8 -*-
import pygame
import os
import time
from constants import *
from pygame.locals import *

assets = {}
assets_rot = {}

ROT_IMAGE_MAX_FILESIZE = 10240
DONT_ROTATE_IMAGES = ['menu_background_level.png', 'ball.png', 'ball_50.png', 'ball_50_red.png',
                      'bullet.png', 'bullet_5.png', 'bullet_10.png']


def load_assets():
    for current_directory in ['gfx', 'sfx']:
        files_list = os.listdir(current_directory)
        for current_file in files_list:
            extension = current_file[-4:]
            filepath = os.path.join(current_directory, current_file)
            if extension == '.png':
                assets[filepath] = pygame.image.load(filepath).convert_alpha()
                print "Loaded:", filepath
                file_size = os.stat(filepath).st_size
                if file_size > ROT_IMAGE_MAX_FILESIZE or current_file in DONT_ROTATE_IMAGES:
                    can_be_rotated = "WON'T ROTATE"
                else:
                    for angle in range(360):
                        if angle == 0:
                            assets_rot[filepath] = {}
                        assets_rot[filepath][angle] = rot_image_keep_size(assets[filepath], angle)
                        print "Loaded rotation:", filepath, angle
                        window.fill(0)
                        window.blit(assets_rot[filepath][angle], (400, 300))
                        pygame.display.flip()
                        #time.sleep(0.01)


                # print current_file, file_size, can_be_rotated
            elif extension == '.wav' or extension == '.ogg':
                print current_file, "is sound"


def rot_image_keep_size(original_image, angle):
    """rotate an image while keeping its center and size"""
    # Tämä copypastettu jostain netistä. Loppujen lopuksi en ole varma onko tarpeen vai ei.
    orig_rect = original_image.get_rect()
    rot_image = pygame.transform.rotate(original_image, angle)
    # rot_rect = orig_rect.copy()
    rot_rect = rot_image.get_rect()
    # rot_rect.center = rot_image.get_rect().center
    # rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

if __name__ == '__main__':
    pygame.init()
    window = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
    pygame.display.set_caption("Menu test")
    load_assets()
    quit()
