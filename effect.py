# -*- coding: utf8 -*-
import math
import game_object
import groups
import pygame
import vector
import assets
from constants import *


class EffectSprite(game_object.GameObject):
    """ Yleinen efektisprite """
    def __init__(self, parent=None, image_file=None, group=groups.EffectGroup,
                 attached_player=None, attached_ball=None,
                 effect_type=None, visible=1, start_position=None, offset=12):
        game_object.GameObject.__init__(self, group=group, image_file=image_file, start_position=start_position)
        self.attached_player = attached_player
        self.offset = offset
        self.attached_ball = attached_ball
        self.effect_type = effect_type
        self.visible = visible
        self.gravity_affects = 0

    def update(self, viewscreen_rect):
        self.viewscreen_rect = viewscreen_rect

        if self.visible:
            self.animate()
            player_dir_radians = math.radians(self.attached_player.heading)
            dx = int(self.offset * math.sin(player_dir_radians))
            dy = int(self.offset * math.cos(player_dir_radians))
            self.rect.center = self.attached_player.rect.center[0] + dx, self.attached_player.rect.center[1] + dy
            self.rot_self_image_keep_size(self.attached_player.heading)
        else:
            # jos ei visible niin heitetään vaan jonnekin kuuseen
            self.rect.center = -100, -100

    def destroy(self):
        self.attached_player = None
        self.attached_ball = None
        self.kill()


class MotorFlame(EffectSprite):
    def __init__(self, parent=None, image_file=None, group=groups.EffectGroup,
                 attached_player=None, attached_ball=None,
                 effect_type='motorflame', visible=1, start_position=None, offset=12):
        EffectSprite.__init__(self, parent=parent, image_file=image_file, group=group,
                              attached_player=attached_player, effect_type=effect_type, visible=visible,
                              start_position=start_position, offset=offset)


class TetherSprite(EffectSprite):
    def __init__(self, group=groups.EffectGroup, attached_player=None, attached_ball=None, parent=None):
        EffectSprite.__init__(self, image_file='gfx/tractor_beam.png', group=group,
                              attached_player=attached_player, attached_ball=attached_ball, parent=parent)
        self.effect_type = 'tether'

    def update(self, viewscreen_rect):
        self.viewscreen_rect = viewscreen_rect
        ball_player_distance = self.attached_player.distance(self.attached_ball)
        ball_player_angle = game_object.get_angle_in_radians((self.attached_player.x, self.attached_player.y),
                                                             (self.attached_ball.x, self.attached_ball.y))
        ball_player_angle = 270 - math.degrees(ball_player_angle)
        # Käännetään ja zoomataan tetherin graffaa sopivasti
        self.image = pygame.transform.rotozoom(self.original_image, ball_player_angle,
                                               ball_player_distance / self.attached_ball.attached_player_max_distance)
        self.rect = self.image.get_rect()
        # rect.center laitetaan pallon ja pelaajan puoliväliin
        self.rect.center = ((self.attached_player.rect.center[0] + self.attached_ball.rect.center[0]) // 2,
                            (self.attached_player.rect.center[1] + self.attached_ball.rect.center[1]) // 2)


class Explosion(EffectSprite):
    """ Räjähdys, joka työntää pelaajia ja palloa pois keskipisteestä """
    def __init__(self, image_file=None, group=groups.EffectGroup, pos=None,
                 explosion_radius=100, explosion_force=20, frames_visible=10,
                 player_group=groups.PlayerGroup, ball_group=groups.BallGroup):
        # Tämä piti tehdä näin koska jos laittoi tuohon initin kutsujuttuihin niin heitti assetsista KeyErroria
        if image_file is None:
            image_file = 'gfx/explosion_100.png'
        EffectSprite.__init__(self, image_file=image_file, group=group, start_position=pos)
        self.explosion_radius = explosion_radius
        self.explosion_radius_squared = explosion_radius ** 2
        self.explosion_force = explosion_force

        # Tässä tapahtuu räjähdyksen työntöefekti
        self.apply_explosion(player_group)
        self.apply_explosion(ball_group)

        self._lifetime_counter = frames_visible

    def update(self, viewscreen_rect):
        """ Tämä on lähinnä vain räjähdysgraffan näyttämistä määritetyn framemäärän ajan """
        self._lifetime_counter -= 1
        if self._lifetime_counter < 0:
            self.kill()
        else:
            self.viewscreen_rect = viewscreen_rect
            self.update_rect()

    def apply_explosion(self, group):
        """ 
        Käy läpi ryhmän objektit ja tekee seuraavaa:
            -jos etäisyys on alle explosion_radius:
                -työntää objektia poispäin räjähdyksen keskipisteestä explosion_forcen verran
                
        TODO: räjähdysvoiman pieneneminen mitä kauempana keskustasta objekti on?
        """
        for current_object in group:
            if self.distance_squared(current_object) < self.explosion_radius_squared:
                current_object.move_vector.add_vector(vector.MoveVector(
                                                      speed=self.explosion_force,
                                                      direction=game_object.get_angle_in_radians(
                                                          (current_object.x, current_object.y),
                                                          (self.x, self.y))
                                                      ))


class SmokeEffect(EffectSprite):
    def __init__(self, start_position, parent=None, attached_player=None, effect_type='smoke', viewscreen_rect=None,
                 image_files=None, offset=10):
        EffectSprite.__init__(self, image_file=image_files,
                              group=groups.EffectGroup, parent=parent, effect_type=effect_type,
                              attached_player=attached_player, offset=offset)
        self.parent = parent
        self.viewscreen_rect = viewscreen_rect
        if self.parent is not None and type(parent).__name__ is not 'BackgroundAction':
            self.x, self.y = start_position
            self.first_image = True
            self.gravity_affects = 1
            self._animation_enabled = 1

            # spawnaa oikeaan paikkaan (ei pelaajan sisään)
            player_dir_radians = math.radians(self.attached_player.heading)
            dx = int(self.offset * math.sin(player_dir_radians))
            dy = int(self.offset * math.cos(player_dir_radians))
            self.x, self.y = self.x + dx, self.y + dy
            self.rot_self_image_keep_size(self.attached_player.heading)  # en tiedä onko tästä iloa savun kanssa
        else:
            self.kill()

    def update(self, viewscreen_rect):
        if self.parent is not None and type(self.parent).__name__ is not 'BackgroundAction':
            self.viewscreen_rect = viewscreen_rect
            self.update_movement()
            self.animate()
            if self._animation_current_image_counter is 0 and not self.first_image:
                self.kill()
            elif self._animation_current_image_counter > 0:
                self.first_image = False


def antialiasing(window, graphic_quality):
    """ 
    Antialiasointi on juuri sitä mitä tämä peli tarvitsee! 
    samples saa olla 0, 2 tai 4, muita arvoja ei tueta
    
    """
    if graphic_quality == 2: samples = 2
    elif graphic_quality == 3: samples = 4
    else: samples = 0

    if samples >= 2:
        surf1 = window.copy()
        surf1.scroll(dx=1)
        surf2 = window.copy()
        surf2.scroll(dy=1)
        if samples == 4:
            surf3 = window.copy()
            surf3.scroll(dx=-1)
            surf4 = window.copy()
            surf4.scroll(dy=-1)
            pygame.transform.average_surfaces((window, surf1, surf2, surf3, surf4), window)
        else:
            pygame.transform.average_surfaces((window, surf1, surf2), window)


class BallDirectionMarker(pygame.sprite.Sprite):
    """ En ole ihan varma kuuluuko tämä tänne, text.py:hyn, vai pitäisikö tehdä oma file info-jutuille """
    def __init__(self, local_player=None, ball=None):
        pygame.sprite.Sprite.__init__(self, groups.TextGroup)
        self.image_file = 'gfx/arrow_blue_32.png'
        self.image = assets.assets[self.image_file]
        self.rect = self.image.get_rect()
        self.player = local_player
        self.ball = ball

    def update(self):
        if self.player.attached_ball is None:
            ball_angle_rad = game_object.get_angle_in_radians(self.ball.rect.center, self.player.rect.center)
            ball_angle_deg = game_object.rad2deg_custom(ball_angle_rad)
            self.image = assets.assets_rot[self.image_file][ball_angle_deg]
            # Jos etäisyys palloon on yli 100 niin näytetään 100 pikselin päässä
            if self.player.distance_squared(self.ball) >= 10000:
                vx = int(100 * math.cos(ball_angle_rad))
                vy = int(100 * math.sin(ball_angle_rad))
                self.rect.center = (WINDOW_SIZE[0] // 2 + vx, WINDOW_SIZE[1] // 2 + vy)
            # Jos etäisyys palloon on alle 100 niin näytetään marker pallon päällä
            else:
                self.rect.center = self.ball.rect.center
        else:
            self.rect.center = (-100, -100)



