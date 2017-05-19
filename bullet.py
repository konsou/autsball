# -*- coding: utf8 -*-
import pygame
import math
import game_object
import groups
import effect
from colors import *
from assets import assets, assets_rot


class BulletSprite(game_object.GameObject):
    """ direction asteina, tulee PlayerSpriten headingista """
    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, image_file=None,
                 pos=(0, 0), direction=0, speed=10):
        game_object.GameObject.__init__(self, group=group, image_file=image_file, start_position=pos,
                                        level=level, parent=parent)
        self.shooting_player = shooting_player
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
        self.animate()
        self.check_out_of_bounds()
        # Out of bounds -check voi tappaa bulletin joten tehdään nämä vain jos ollaan vielä bulletgroupissa:
        if self in self.group:
            # Vakiona bullet voi törmätä seinään, pelaajaan ja palloon
            self.check_collision_with_wall_and_goal()
            self.check_collision_with_group(groups.PlayerGroup)
            self.check_collision_with_group(groups.BallGroup)
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

    def get_non_alpha_pixels(self):
        pixels = []
        for x in range(0, self.image.get_width()):
            for y in range(0, self.image.get_height()):
                if self.image.get_at((x, y)).a > 0:
                    pixels.append([x, y])
        return pixels

    def collided_with_wall(self):
        """ 
        Tämä tapahtuu kun ammus törmää seinään 
        """
        # Tuhoaa seinää törmätessä ja myös itsensä
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        self.kill()

    def collided_with(self, other_object):
        """ 
        Tämä tapahtuu kun ammus törmää toiseen peliobjektiin. Vakiona vain tuhotaan ammus. Voi overrideta
        kustomikäyttäytymisen mahdollistamiseksi.
        """
        self.kill()


class BasicShot(BulletSprite):
    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, pos=(0,0), direction=0, speed=10):
        BulletSprite.__init__(self, parent=parent, level=level, group=group, image_file='gfx/bullet_5.png',
                              pos=pos, direction=direction, speed=speed)
        self.mass = 0.1


class DumbFire(BulletSprite):
    """ Iso ammus joka räjähtää törmätessä """
    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, pos=(0,0), direction=0, speed=10):
        BulletSprite.__init__(self, parent=parent, level=level, group=group, image_file='gfx/bullet_10.png',
                              pos=pos, direction=direction, speed=speed)

        self.mass = 0.2
        self.explosion_force = 10
        self.explosion_radius = 50

    def collided_with_wall(self):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        effect.Explosion(image_file='gfx/explosion_50.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)
        self.kill()

    def collided_with(self, other_object):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        effect.Explosion(image_file='gfx/explosion_50.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)
        self.kill()


class Dirtball(BulletSprite):
    """ Iso ammus joka luo maastoa törmätessä """
    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, pos=(0, 0), direction=0, speed=10):
        BulletSprite.__init__(self, parent=parent, level=level, group=group, image_file='gfx/bullet_10.png',
                              pos=pos, direction=direction, speed=speed)

        self.mass = 0.2

    def collided_with_wall(self):
        pygame.draw.circle(self.level.image, BROWN, (self.x, self.y), 20)
        self.kill()

    def collided_with(self, other_object):
        pygame.draw.circle(self.level.image, BROWN, (self.x, self.y), 20)
        self.kill()


class Switcher(BulletSprite):
    """ Vaihtaa paikkaa toisen objektin kanssa """
    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, pos=(0, 0), direction=0,
                 speed=10):
        image_file = ['gfx/switcher1.png', 'gfx/switcher2.png']
        BulletSprite.__init__(self, shooting_player=shooting_player, parent=parent, level=level, group=group,
                              image_file=image_file, pos=pos, direction=direction, speed=speed)

        self.mass = 0

    def collided_with_wall(self):
        """ Mitään ei tapahdu seinätörmäyksessä """
        self.kill()

    def collided_with(self, other_object):
        """ 
        Vaihtaa ampujan paikkaa törmäävän objektin kanssa
        TODO: jostan syystä jos osuu palloon niin attachaa aina, korjaa? 
        """
        temp_x, temp_y = self.shooting_player.x, self.shooting_player.y
        self.shooting_player.x, self.shooting_player.y = other_object.x, other_object.y
        other_object.x, other_object.y = temp_x, temp_y
        self.update_rect()
        other_object.update_rect()
        self.kill()


