# -*- coding: utf8 -*-
import pygame
import math
import game_object
import groups
import effect
import random
from colors import *
from assets import assets, assets_rot

# TODO: bulletit tuhoaa itsensä joskus ennen kuin kerkeävät törmätä


class BulletSprite(game_object.GameObject):
    """ Ammuttavien juttujen perusclass. Tässä vakioarvot jos muuta ei overrideta: """
    cooldown = 80  # millisekuntia
    max_speed = 20
    mass = 0.1
    speed = 10
    rotate = 0
    laser_movement = 0

    # direction asteina, tulee PlayerSpriten headingista
    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, image_file=None,
                 heading=0, speed=10):

        game_object.GameObject.__init__(self, group=group, image_file=image_file,
                                        level=level, parent=parent)

        self.heading = heading

        # Lasketaan bulletin aloituspiste niin ettei ole aluksen sisällä.
        # Tässä viilaamisen varaa vielä jos haluaa perfektoida mutta toimii aika hyvin
        self.x = int((shooting_player.radius + self.radius + 2) * math.sin(math.radians(self.heading))
                     * -1 + shooting_player.x)
        self.y = int((shooting_player.radius + self.radius + 2) * math.cos(math.radians(self.heading))
                     * -1 + shooting_player.y)

        self.shooting_player = shooting_player
        self.rect.center = (self.x, self.y)
        self.move_vector.set_speed_direction(speed, math.radians(270 - heading))

        if not self.laser_movement:
            # Lisätään ampuvan pelaajan liikevektori että se vaikuttaa loogisella tavalla bulletin liikemäärään
            self.move_vector.add_vector(shooting_player.move_vector)
        else:
            self.gravity_affects = 0

        self.is_bullet = 1
        self.group = group
        self.kill_pending = 0

        # SFX
        if not self.parent.demogame:
            self.wall_collide_sound = assets['sfx/thump3.wav']
            self.wall_collide_sound.set_volume(1)
        else:
            self.wall_collide_sound = None

    def __repr__(self):
        return "<BulletSprite>"

    def update(self, viewscreen_rect):
        if self.kill_pending:
            self.kill()
        self.viewscreen_rect = viewscreen_rect
        self.update_movement()
        self.animate()
        if self.rotate:
            self.rot_self_image_keep_size(self.heading)
        self.check_out_of_bounds()
        # Out of bounds -check voi tappaa bulletin joten tehdään nämä vain jos ollaan vielä bulletgroupissa:
        if self in self.group:
            # Vakiona bullet voi törmätä seinään, pelaajaan ja palloon
            self.check_collision_with_wall_and_goal()
            self.check_collision_with_group(groups.PlayerGroup)
            self.check_collision_with_group(groups.BallGroup)
            if self in self.group:
                if self.check_collision_with_wall_and_goal(speculate=1) == 1:
                    # Vähennetään nopeutta jos spekulointi havaitsee törmäyksen
                    self.move_vector.set_speed(min(self.move_vector.get_speed(), 3))
                self.update_rect()

    def check_out_of_bounds(self):
        """ Overrideaa GameObjectin metodin koska pitää tuhota bulletti jos on out of bounds """
        if self.x < 0 or self.y < 0 or self.x >= self.level.size_x or self.y >= self.level.size_y:
            self.x = 0
            self.y = 0
            self.kill()

    def collided_with_wall(self):
        """ 
        Tämä tapahtuu kun ammus törmää seinään 
        """
        # Tuhoaa seinää törmätessä ja myös itsensä
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        self.kill_pending = 1

    def collided_with(self, other_object):
        """ 
        Tämä tapahtuu kun ammus törmää toiseen peliobjektiin. Vakiona vain tuhotaan ammus. Voi overrideta
        kustomikäyttäytymisen mahdollistamiseksi.
        """
        self.kill_pending = 1


class BasicShot(BulletSprite):
    """ Perusammus alhaisella massalla mutta suht pienellä cooldownilla """
    cooldown = 80
    mass = 0.1
    speed = 10
    image_file = 'gfx/bullet_5.png'

    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, heading=0):
        BulletSprite.__init__(self, shooting_player=shooting_player, parent=parent, level=level, group=group,
                              image_file=self.image_file, heading=heading, speed=self.speed)


class GreenLaser(BulletSprite):
    """ Star Wars -tyyppinen hidas laser - ei tuhoa seinää """
    cooldown = 80
    mass = 0.1
    speed = 10
    image_file = 'gfx/bullet_laser_green_16.png'
    rotate = 1
    laser_movement = 1

    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, heading=0):
        BulletSprite.__init__(self, shooting_player=shooting_player, parent=parent, level=level, group=group,
                              image_file=self.image_file, heading=heading, speed=self.speed)
        # self.gravity_affects = 0

    def collided_with_wall(self):
        self.kill_pending = 1


class DumbFire(BulletSprite):
    """ Iso ammus joka räjähtää törmätessä """
    cooldown = 3000
    mass = 0.2
    speed = 10
    explosion_force = 10
    explosion_radius = 50
    image_file = 'gfx/bullet_10.png'

    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup,
                 heading=0):
        BulletSprite.__init__(self, shooting_player=shooting_player, parent=parent, level=level, group=group,
                              image_file=self.image_file, heading=heading, speed=self.speed)

    def collided_with_wall(self):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        effect.Explosion(image_file='gfx/explosion_50.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)
        self.kill_pending = 1

    def collided_with(self, other_object):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        effect.Explosion(image_file='gfx/explosion_50.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)
        self.kill_pending = 1


class Dirtball(BulletSprite):
    """ Iso ammus joka luo maastoa törmätessä """
    cooldown = 3000
    mass = 0.2
    speed = 10
    image_file = 'gfx/bullet_10.png'

    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, heading=0):
        BulletSprite.__init__(self, shooting_player=shooting_player, parent=parent, level=level, group=group,
                              image_file=self.image_file,
                              heading=heading, speed=self.speed)

    def collided_with_wall(self):
        pygame.draw.circle(self.level.image, BROWN, (self.x, self.y), 20)
        self.kill_pending = 1

    def collided_with(self, other_object):
        pygame.draw.circle(self.level.image, BROWN, (self.x, self.y), 20)
        self.kill_pending = 1


class Switcher(BulletSprite):
    """ Vaihtaa paikkaa toisen objektin kanssa törmäyksessä """
    cooldown = 3000
    mass = 0.001
    speed = 10
    image_file = ['gfx/bullet_switcher1.png', 'gfx/bullet_switcher2.png']

    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, heading=0):
        BulletSprite.__init__(self, shooting_player=shooting_player, parent=parent, level=level, group=group,
                              image_file=self.image_file, heading=heading, speed=self.speed)

    def collided_with_wall(self):
        """ Mitään ei tapahdu seinätörmäyksessä """
        self.kill_pending = 1

    def collided_with(self, other_object):
        """ 
        Vaihtaa ampujan paikkaa törmäävän objektin kanssa
        """
        temp_x, temp_y = tuple((self.shooting_player.x, self.shooting_player.y))
        self.shooting_player.x, self.shooting_player.y = tuple((other_object.x, other_object.y))
        other_object.x, other_object.y = temp_x, temp_y
        # Tämä tarvitaan että viewscreen pysyy mukana paikanvaihdoksessa
        self.parent.calc_viewscreen_rect()
        self.update_rect()
        other_object.update_rect()
        self.kill_pending = 1


class Bouncer(BulletSprite):
    """ Pomppii, räjähtää vähän """
    cooldown = 2000
    mass = 0.2
    speed = 10
    explosion_force = 5
    explosion_radius = 25
    number_of_bounces = 5
    image_file = 'gfx/bullet_10.png'

    def __init__(self, shooting_player=None, parent=None, level=None, group=groups.BulletGroup, heading=0):
        BulletSprite.__init__(self, shooting_player=shooting_player, parent=parent, level=level, group=group,
                              image_file=self.image_file, heading=heading, speed=self.speed)
        self._bounce_counter = 0

    def collided_with_wall(self):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        randomvalue = random.uniform(-0.5, 0.5)
        self.move_vector.set_direction(self.move_vector.get_direction() - math.pi + randomvalue)
        effect.Explosion(image_file='gfx/explosion_30.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)
        self._bounce_counter += 1
        if self._bounce_counter > self.number_of_bounces:
            self.kill_pending = 1

    def collided_with(self, other_object):
        pygame.draw.circle(self.level.image, BLACK, (self.x, self.y), self.size - 1)
        self.apply_collision_to_move_vector(other_object)
        effect.Explosion(image_file='gfx/explosion_30.png', pos=(self.x, self.y), explosion_radius=self.explosion_radius,
                         explosion_force=self.explosion_force)
        self._bounce_counter += 1
        if self._bounce_counter > self.number_of_bounces:
            self.kill_pending = 1

