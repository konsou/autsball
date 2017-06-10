# -*- coding: utf8 -*-
import pygame
import math
import game_object
import vector
import groups
import effect
from colors import *
from constants import *
from assets import assets, assets_rot


class BallSprite(game_object.GameObject):
    """ Pallo. Osaa liittää itsensä pelaajaan ja poistaa liitoksen. """
    def __init__(self, level=None, parent=None, group=groups.BallGroup):
        game_object.GameObject.__init__(self, group=group, image_file='gfx/ball_50_red.png', level=level, parent=parent)

        # Otetaan start_position levelin tiedoista
        self.start_position = self.level.ball_spawns[0]
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
        if not self.parent.demogame:
            self.wall_collide_sound = assets['sfx/thump4.wav']
            self.bullet_collide_sound = assets['sfx/metal_thud_3.wav']
        else:
            self.wall_collide_sound = None
            self.bullet_collide_sound = None

    def __repr__(self):
        return "<BallSprite>"

    def update(self, viewscreen_rect, player_group=groups.PlayerGroup, bullet_group=groups.BulletGroup):
        """ Päivittää palloa. Vaatii viewscreen_rect:in että osaa laskea näyttämisen oikein. """
        self.viewscreen_rect = viewscreen_rect

        # Jos on liitetty pelaajaan ja jos on liian kaukana niin vetävät toisiaan puoleensa
        # Suht hyvä, voi viilata jos saa vielä paremmaksi
        # Lisätty weightien vaikutus
        if self.attached_player is not None:
            distance_to_player = self.distance(self.attached_player)
            if distance_to_player >= self.attached_player_max_distance:
                player_angle = game_object.get_angle_in_radians((self.attached_player.x, self.attached_player.y),
                                                                (self.x, self.y))

                pull_vector_speed = (distance_to_player - self.attached_player_max_distance) * 0.02

                ball_pull_vector = vector.MoveVector(speed=pull_vector_speed / self.mass * self.attached_player.mass,
                                                     direction=player_angle)
                # Tässä rikotaan voiman ja vastavoiman lakia mutta who cares! (Newton pyörii haudassaan)
                player_pull_vector = vector.MoveVector(speed=pull_vector_speed * -1 * 0.4 / self.attached_player.mass * self.mass,
                                                       direction=player_angle)

                self.move_vector.add_vector(ball_pull_vector)
                self.attached_player.move_vector.add_vector(player_pull_vector)

        self.update_movement()

        self.check_out_of_bounds()
        self.check_collision_with_wall_and_goal()
        self.check_collision_with_group(player_group)
        self.check_collision_with_group(bullet_group)

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
        Tämä metodi liittää pallon pelaajaan. 
        """
        self.attached_player = player
        player.attach_ball(self)
        self.tether = effect.TetherSprite(attached_ball=self, attached_player=player)

    def detach(self, force=0):
        """ Tämä metodi poistaa liitoksen pelaajaan. """
        if self.attached_player is not None:
            if self.parent.server_object is not None:
                self.parent.add_event(GameEventTypes.DetachBall)
            if not self.parent._is_client or force:
                self.attached_player.detach()
                self.attached_player = None
                self.tether.destroy()

    def collided_with(self, other_object):
        """
        Jos other_object on pelaaja ja palloa ei vielä ole liitetty pelaajaan niin tehdään liitos
        Emme törmäile pelaajaan, joka on liitettynä
        """
        if not self.parent._is_client:
            apply_collision = 1
            # Jos törmäävä objekti on pelaaja ja palloa ei vielä ole liitetty pelaajaan niin liitetään
            if other_object in groups.PlayerGroup:
                # Jos pallo on ammuttu äskettäin niin ei törmätä
                if pygame.time.get_ticks() - other_object.ball_shot_at < other_object.ball_immunity_time:
                    apply_collision = 0

                if self.attached_player is None and apply_collision == 1:
                    if self.parent.server_object is not None:
                        self.parent.add_event(GameEventTypes.AttachBall, other_object.owning_player_id)
                    self.attach_to_player(other_object)

                if other_object == self.attached_player:
                    apply_collision = 0

            if apply_collision:
                self.apply_collision_to_move_vector(other_object)

    def is_in_goal(self, point_color):
        """ Kun pallo menee maaliin niin tulee maali. Loogista. """
        if point_color == RED:
            self.parent.score('green')
            self.reset()
        elif point_color == GREEN:
            self.parent.score('red')
            self.reset()
