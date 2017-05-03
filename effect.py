# -*- coding: utf8 -*-
import math
import game_object
import groups
from colors import *


class EffectSprite(game_object.GameObject):
    """ Yleinen efektisprite, tällä hetkellä tosin vain moottorin liekit """
    def __init__(self, image=None, group=groups.EffectGroup, attached_player=None, attached_ball=None, effect_type=None, visible=1, parent=None):
        game_object.GameObject.__init__(self, group=group, image=image)
        self.attached_player = attached_player
        self.attached_ball = attached_ball
        self.effect_type = effect_type
        self.visible = visible

    def update(self):
        if self.visible:
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
        self.kill()
