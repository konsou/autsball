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
