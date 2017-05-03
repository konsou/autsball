# -*- coding: utf8 -*-
import pygame
import math
import game_object
import groups
from colors import *


class BulletSprite(game_object.GameObject):
    """ direction asteina, tulee PlayerSpriten headingista """
    def __init__(self, parent=None, level=None, group=groups.BulletGroup, x=0, y=0, direction=0, parent_speed=0, speed=5, type='basic'):
        game_object.GameObject.__init__(self, group=group, image_file='gfx/bullet_5.png', start_position=(x, y),
                                        level=level, parent=parent)
        self.rect.center = (x, y)
        self.move_vector.set_speed_direction(speed, math.radians(270 - direction))
        self.max_speed = 20
        self.explosion_force = 1

        self.is_bullet = 1
        self.group = group

        # SFX
        self.wall_collide_sound = pygame.mixer.Sound(file='sfx/thump3.wav')
        self.wall_collide_sound.set_volume(1)

    def update(self, viewscreen_rect):
        self.viewscreen_rect = viewscreen_rect
        self.update_movement()
        self.check_out_of_bounds()
        # print("Speed:", self.move_vector.get_speed())
        # Tehdään nämä vain jos on olemassa
        if self in self.group:
            self.check_collision_with_wall_and_goal()
            if self in self.group:
                if self.speculate_collision_with_wall() == 1:
                    # Vähennetään nopeutta jos spekulointi havaitsee törmäyksen
                    self.move_vector.set_speed(min(self.move_vector.get_speed(), 3))
                self.update_rect()

    def check_out_of_bounds(self):
        """ Overrideaa GameObjectin metodin koska pitää tuhota bulletti jos on out of bounds """
        if self.x < 0 or self.y < 0 or self.x >= self.level.size_x or self.y >= self.level.size_y:
            self.x = 0
            self.y = 0
            self.kill()


