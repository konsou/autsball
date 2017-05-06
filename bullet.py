# -*- coding: utf8 -*-
import pygame
import math
import game_object
import groups
import effect
from colors import *


class BulletSprite(game_object.GameObject):
    """ direction asteina, tulee PlayerSpriten headingista """
    def __init__(self, parent=None, level=None, group=groups.BulletGroup, image_file=None,
                 pos=(0, 0), direction=0, speed=10):
        game_object.GameObject.__init__(self, group=group, image_file=image_file, start_position=pos,
                                        level=level, parent=parent)
        self.rect.center = pos
        self.move_vector.set_speed_direction(speed, math.radians(270 - direction))
        self.max_speed = 20
        self.mass = 0.1
        # self.explosion_force = 1

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

    def collide_with_wall(self):
        """ 
        Tämä tapahtuu kun ammus törmää seinään 
        HUOM! Tähän TULEE self.kill() koska ei hoidu pygamen törmäystarkistusten kautta!
        """
        # Tuhoaa seinää törmätessä ja myös itsensä jos on bullet
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        self.kill()

    def collide_with_player(self):
        """ 
        Tämä tapahtuu kun ammus törmää pelaajaan
        Vakiona tyhjä - tarkoitus overrideta jos tulee erikoisefektejä uusissa ammustyypeissä
        HUOM! Tähän EI tule self.kill() koska pygamen törmäystarkistus hoitaa sen
        """
        pass

    def collide_with_ball(self):
        """ 
        Tämä tapahtuu kun ammus törmää pelaajaan
        Vakiona tyhjä - tarkoitus overrideta jos tulee erikoisefektejä uusissa ammustyypeissä
        HUOM! Tähän EI tule self.kill() koska pygamen törmäystarkistus hoitaa sen
        """
        pass


class BasicShot(BulletSprite):
    def __init__(self, parent=None, level=None, group=groups.BulletGroup, pos=(0,0), direction=0, speed=10):
        BulletSprite.__init__(self, parent=parent, level=level, group=group, image_file='gfx/bullet_5.png',
                              pos=pos, direction=direction, speed=speed)
        self.mass = 0.1


class DumbFire(BulletSprite):
    """ Iso ammus joka räjähtää törmätessä """
    def __init__(self, parent=None, level=None, group=groups.BulletGroup, pos=(0,0), direction=0, speed=10):
        BulletSprite.__init__(self, parent=parent, level=level, group=group, image_file='gfx/bullet_10.png',
                              pos=pos, direction=direction, speed=speed)

        self.mass = 0.2
        self.explosion_force = 10
        self.explosion_radius = 50

    def collide_with_wall(self):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        effect.Explosion(image_file='gfx/explosion_50.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)
        self.kill()

    def collide_with_player(self):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        effect.Explosion(image_file='gfx/explosion_50.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)

    def collide_with_ball(self):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        effect.Explosion(image_file='gfx/explosion_50.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)

