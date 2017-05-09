# -*- coding: utf8 -*-
import math
import game_object
import groups
import pygame
from colors import *


class EffectSprite(game_object.GameObject):
    """ Yleinen efektisprite """
    def __init__(self, image=None, image_file=None, group=groups.EffectGroup, attached_player=None, attached_ball=None,
                 effect_type=None, visible=1, parent=None):
        game_object.GameObject.__init__(self, group=group, image=image, image_file=image_file)
        self.attached_player = attached_player
        self.attached_ball = attached_ball
        self.effect_type = effect_type
        self.visible = visible

    def update(self, viewscreen_rect):
        self.viewscreen_rect = viewscreen_rect
        if self.visible:
            self.animate()
            player_dir_radians = math.radians(self.attached_player.heading)
            dx = int(12 * math.sin(player_dir_radians))
            dy = int(12 * math.cos(player_dir_radians))
            self.rect.center = self.attached_player.rect.center[0] + dx, self.attached_player.rect.center[1] + dy
            self.rot_self_image_keep_size(self.attached_player.heading)

        else:
            # jos ei visible niin heitetään vaan jonnekin kuuseen
            self.rect.center = -100, -100

    def destroy(self):
        self.attached_player = None
        self.attached_ball = None
        self.kill()


class TetherSprite(EffectSprite):
    def __init__(self, group=groups.EffectGroup, attached_player=None, attached_ball=None, parent=None):
        EffectSprite.__init__(self, image=pygame.image.load('gfx/tractor_beam.png').convert_alpha(), group=group,
                              attached_player=attached_player, attached_ball=attached_ball, parent=parent)
        self.effect_type = 'tether'

    def update(self, viewscreen_rect):
        self.viewscreen_rect = viewscreen_rect
        ball_player_distance = self.attached_player.distance(self.attached_ball)
        ball_player_angle = game_object.get_angle_in_radians((self.attached_player.x, self.attached_player.y),
                                                             (self.attached_ball.x, self.attached_ball.y))
        ball_player_angle = 270 - math.degrees(ball_player_angle)
        self.image = pygame.transform.rotozoom(self.original_image, ball_player_angle,
                                               ball_player_distance / self.attached_ball.attached_player_max_distance)
        self.rect = self.image.get_rect()
        self.rect.center = ((self.attached_player.rect.center[0] + self.attached_ball.rect.center[0]) // 2,
                            (self.attached_player.rect.center[1] + self.attached_ball.rect.center[1]) // 2)


class SmokeEffect(EffectSprite):

    def __init__(self, start_position, parent=None):
        # TODO: lataa kuvat vain kerran ja käytä uudestaan instansseissa

        EffectSprite.__init__(self, image_file=['gfx/smoke_16_0.png',
                                                'gfx/smoke_16_1.png',
                                                'gfx/smoke_16_2.png',
                                                'gfx/smoke_16_3.png',
                                                'gfx/smoke_16_4.png'],
                              group=groups.EffectGroup, parent=parent)
        self.parent = parent
        if self.parent is not None and type(parent).__name__ is not 'BackgroundAction':
            try:
                self.timer = parent.clock
            except AttributeError:
                self.timer = pygame.time.Clock()
            self.x, self.y = start_position
            self.first_image = True
            self.gravity_affects = 1
            self._animation_enabled = 1

            # TODO: spawnaa oikeaan paikkaan (ei pelaajan sisään)
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
