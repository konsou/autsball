# -*- coding: utf8 -*-
import pygame
import math
import game_object
import vector
import groups
import effect
from colors import *


class BallSprite(game_object.GameObject):
    """ Pallo. Osaa liittää itsensä pelaajaan ja poistaa liitoksen. """
    def __init__(self, level=None, parent=None, group=groups.BallGroup):
        game_object.GameObject.__init__(self, group=group, image_file='gfx/ball_50_red.png', level=level, parent=parent)
        self.start_position = self.level.center_point
        self.x, self.y = self.start_position

        # Player attachment
        self.attached_player = None
        self.attached_player_max_distance = 50  # "tetherin" pituus
        self.attached_player_max_distance_squared = self.attached_player_max_distance**2  # distance-laskelmia varten
        self.tether = None

        self.mass = 1.0
        self.max_speed = 10

        # Tämä tekee sen että tarkistetaan törmäys maaliin
        self.is_ball = 1

        # SFX
        self.wall_collide_sound = pygame.mixer.Sound(file='sfx/thump4.wav')
        self.bullet_collide_sound = pygame.mixer.Sound(file='sfx/metal_thud_3.wav')

    def update(self, viewscreen_rect, player_group=groups.PlayerGroup, bullet_group=groups.BulletGroup):
        """ Päivittää palloa. Vaatii viewscreen_rect:in että osaa laskea näyttämisen oikein. """
        self.viewscreen_rect = viewscreen_rect

        # Jos törmää pelaajaan niin liitetään siihen
        # Vain jos ei jo ole liitettynä!
        if self.attached_player is None:
            collide_list = pygame.sprite.spritecollide(self, player_group, dokill=False, collided=pygame.sprite.collide_circle)
            if len(collide_list) > 0:
                self.attach_to_player(collide_list[0])
                self.tether = effect.TetherSprite(attached_ball=self, attached_player=collide_list[0])

        # Jos on liitetty pelaajaan ja jos on liian kaukana niin vetävät toisiaan puoleensa
        # Suht hyvä, voi viilata jos saa vielä paremmaksi
        # TODO: weightit ei tunnu vaikuttavan?
        # TODO: graffat tetherille
        if self.attached_player is not None:
            distance_to_player = self.distance(self.attached_player)
            if distance_to_player >= self.attached_player_max_distance:
                player_angle = game_object.get_angle_in_radians((self.attached_player.x, self.attached_player.y),
                                                                 (self.x, self.y))

                pull_vector_speed = (distance_to_player - self.attached_player_max_distance) * 0.02

                ball_pull_vector = vector.MoveVector(speed=pull_vector_speed, direction=player_angle)
                # Tässä rikotaan voiman ja vastavoiman lakia mutta who cares! (Newton pyörii haudassaan)
                player_pull_vector = vector.MoveVector(speed=pull_vector_speed * -1 * 0.4, direction=player_angle)

                self.move_vector.add_vector(ball_pull_vector)
                self.attached_player.move_vector.add_vector(player_pull_vector)

        self.update_movement()

        self.check_out_of_bounds()
        self.check_collision_with_wall_and_goal()
        self.check_collision_with_bullets(bullet_group)

    def collide_tether(self, other_object):
        """ 
        Eksperimentaalinen tetherin törmäysmetodi. Ei toimi niin kuin haluaisin.
        Ideana tässä että tether-collide on oletettavasti ekvivalentti normaalille törmäykselle niin että
        objektien paikat vaihdetaan
        Ei tällä hetkellä käytössä
        """
        new_self = other_object
        new_other = self
        angle_to_other = game_object.get_angle_in_radians(new_other.rect.center, new_self.rect.center)
        new_self.move_vector.set_direction(angle_to_other - math.pi)
        new_other.move_vector.set_direction(angle_to_other)

        speed1 = new_self.move_vector.get_speed()
        speed2 = new_other.move_vector.get_speed()
        mass1 = new_self.mass
        mass2 = new_other.mass
        speed1_new = (mass2 / mass1) * speed2
        speed2_new = (mass1 / mass2) * speed1
        self.move_vector.set_speed(speed2_new * -1)
        other_object.move_vector.set_speed(speed1_new * -1)

    def shoot(self, direction=0, speed=0, x=None, y=None):
        """ 
        Ampuu itsensä määritettyyn suuntaan, määritetyllä nopeudella, alkaen määritetyistä koordinaateista.
        Tätä kutsuu PlayerSpriten shoot-metodi, joka hoitaa detachauksen ja antaa tarvittavat tiedot
        """

        self.tether.destroy()

        if x is not None and y is not None:
            # Tämä tehdään jos annettu uudet koordinaatit
            # Jostain syystä vaatii direktion korjauksen tässä
            self.move_vector.set_speed_direction(speed, math.radians(270 - direction))
            self.x = int(x)
            self.y = int(y)
            self.update_rect()
        else:
            # Jos ei ole annettu uusia koordinaatteja niin lisätään vain liikevektoriin määritetyt
            # direction ja speed
            self.move_vector.add_vector(vector.MoveVector(speed=speed, direction=math.radians(270 - direction)))

    def attach_to_player(self, player):
        """ 
        Tämä metodi liittää pallon pelaajaan. Olisi tarkoitus myös lisätä painoa mutta paino ei toimi
        oikein vielä.
        """
        self.attached_player = player
        player.attach_ball(self)
        # self.tether = EffectSprite(image=pygame.Surface((0,0)), effect_type='tether',
        #                            attached_ball=self, attached_player=player, parent=self.parent)
        # TODO: korjaa weight että tämä voidaan enabloida
        # self.attached_player.weight += self.weight

    def detach(self):
        """ Tämä metodi poistaa liitoksen pelaajaan. """
        # self.attached_player.weight -= self.weight
        # print("Ball detach method called. Attached player:", self.attached_player)
        if self.attached_player is not None:
            self.attached_player.detach()
            self.attached_player = None
            self.tether.destroy()
            # self.tether = None