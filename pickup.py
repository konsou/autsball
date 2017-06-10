# -*- coding: utf8 -*-
import pygame
import math
import game_object
import groups
import effect
import random
import sound
from colors import *
from assets import assets, assets_rot


def spawn_random_pickup(parent, level):
    selected_pickup = random.choice(pickup_types_list)
    print "Spawning random pickup: {}".format(selected_pickup)
    selected_pickup(parent=parent, level=level)


class PickupSprite(game_object.GameObject):
    """ Kerättävien juttujen perusclass. """
    _bobbing_movement_table = [0, 0, 0, 0,
                               -1, 0, -1, 0, -2, 0, -2, 0, -1, 0, -1,
                               0, 0, 0, 0, 0, 0, 0, 0, 0,
                               +1, 0, +1, 0, +2, 0, +2, 0, +1, 0, +1,
                               0, 0, 0, 0, 0]
    _pickup_number_counter = 0

    def __init__(self, parent=None, level=None, group=groups.PickupGroup, image_file=None):
        # Emme halua spawnata seinän sisään
        position_found = 0
        while position_found == 0:
            x = random.randint(0, level.size_x - 1)
            y = random.randint(0, level.size_y - 1)
            if level.get_color_at((x, y)) == BLACK:
                position_found = 1

        game_object.GameObject.__init__(self, group=group, image_file=image_file,
                                        level=level, parent=parent, start_position=(x, y))
        self.gravity_affects = 0
        self._bob_counter = 0

        self.player_collide_sound = assets['sfx/pickup_get.wav']
        # print "Spawning pickup... x: {} y: {}".format(x, y)
        # print "rect: {}".format(self.rect)

    def __repr__(self):
        return "<PickupSprite>"

    def update(self, viewscreen_rect):
        self._bob_counter += 1
        try:
            self.y += self._bobbing_movement_table[self._bob_counter]
        except IndexError:
            self._bob_counter = 0

        self.animate()
        self.update_rect(viewscreen_rect)
        self.check_collision_with_group(groups.PlayerGroup)

    def collided_with(self, other_object):
        """
        Tämä tapahtuu kun törmää toiseen peliobjektiin. Vakiona vain tuhoaa itsensä. Voi overrideta
        kustomikäyttäytymisen mahdollistamiseksi.
        """
        if other_object in groups.PlayerGroup:
            print "YOU GOT PICKUP!"
            sound.force_play_sound(self.player_collide_sound)
            self.kill()

    @classmethod
    def number_of_pickup_types(cls):
        return cls._pickup_number_counter

    @classmethod
    def add_to_pickup_list(cls):
        pickup_types_list.append(cls)


class DummyPickup(PickupSprite):
    image_file = 'gfx/pickup_frame_24.png'

    def __init__(self, level=None, parent=None, group=groups.PickupGroup):
        PickupSprite.__init__(self, parent=parent, level=level, group=group,
                              image_file=self.image_file)

    def __repr__(self):
        return "<DummyPickup>"


class StarPickup(PickupSprite):
    image_file = 'gfx/pickup_star_24.png'

    def __init__(self, level=None, parent=None, group=groups.PickupGroup):
        PickupSprite.__init__(self, parent=parent, level=level, group=group,
                              image_file=self.image_file)

    def __repr__(self):
        return "<StarPickup>"

    def collided_with(self, other_object):
        if other_object in groups.PlayerGroup:
            print "YOU GOT PICKUP!"
            sound.force_play_sound(self.player_collide_sound)
            other_object.mass *= 2
            other_object.max_thrust *= 2
            self.kill()

# TODO: automaattinen tapa tälle
pickup_types_list = [DummyPickup, StarPickup]


def debug_run():
    print pickup_types_list

if __name__ == '__main__':
    debug_run()