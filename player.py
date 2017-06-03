# -*- coding: utf8 -*-
import pygame
import math
import game_object
import effect
import bullet
import groups
import text
import sound
from colors import *
from constants import *
from pygame.locals import *
from assets import assets, assets_rot


class PlayerSprite(game_object.GameObject):
    def __init__(self, player_id=None, team=None, level=None, parent=None, ship_name='V-Wing',
                 group=groups.PlayerGroup, spawn_point=None, special=None):
        self.owning_player_id = player_id
        self.team = team
        self.ship_name = ship_name

        # Ladataan xml-file
        root = text.read_xml('xml/ship.xml')
        current_ship = root.find(".//ship[@name='" + ship_name + "']")

        # Kuva
        if team == 'red':
            image_file = current_ship.find('images/team_red_image').text
        else:
            image_file = current_ship.find('images/team_green_image').text

        # Lisätään ryhmään
        game_object.GameObject.__init__(self, group=group, level=level, parent=parent,
                                        image_file=image_file)

        # print "player.py: image file:", self.image_filename
        # print self.image
        # Thrust-gfx
        try:
            motor_flame_offset = int(current_ship.find('images/motor_flame_offset').text)
        except AttributeError:
            motor_flame_offset = 0
        thrust_image_file = []
        for value in current_ship.findall('images/motor_flame_image'):
            thrust_image_file.append(value.text)

        if len(thrust_image_file) > 0:
            self.thrust_gfx = effect.MotorFlame(attached_player=self, image_file=thrust_image_file,
                                                visible=0, parent=parent, offset=motor_flame_offset)
        else:
            self.thrust_gfx = None

        self.rect.center = WINDOW_CENTER_POINT
        if self.owning_player_id == parent.local_player_id and not self.parent.demogame:
            self.is_centered_on_screen = 1
            # Pallonsuuntamarkkeri
            effect.BallDirectionMarker(self, self.parent.ball)
        else:
            self.is_centered_on_screen = 0

        self._smoke_interval = 30  # Smoken spawn tiheys millisekunteina
        self._smoke_counter = 0
        self.smoke_effect_image_files = []
        for value in current_ship.findall('images/rear_smoke_image'):
            self.smoke_effect_image_files.append(value.text)

        try:
            self.smoke_effect_offset = int(current_ship.find('images/rear_smoke_offset').text)
        except AttributeError:
            self.smoke_effect_offset = 0

        # Sound effex
        if not self.parent.demogame:
            self.motor_sound = assets[current_ship.find('sounds/motor_sound').text]
            self.motor_sound_playing = 0
            self.bullet_sound = assets[current_ship.find('sounds/bullet_sound').text]
            self.ball_shoot_sound = assets[current_ship.find('sounds/ball_shoot_sound').text]
            self.ball_capture_sound = assets[current_ship.find('sounds/ball_capture_sound').text]
            self.wall_collide_sound = assets[current_ship.find('sounds/wall_collide_sound').text]
            self.bullet_collide_sound = assets[current_ship.find('sounds/bullet_collide_sound').text]
        else:
            self.motor_sound = None
            self.motor_sound_playing = 0
            self.bullet_sound = None
            self.ball_shoot_sound = None
            self.ball_capture_sound = None
            self.wall_collide_sound = None
            self.bullet_collide_sound = None

        # Koordinaatit
        if not spawn_point:
            self.start_position = (700, 1200)
        else:
            self.start_position = spawn_point
        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.x, self.y

        # Heading ja thrust
        self.heading = 0  # HUOM! Heading asteina koska Pygame käyttää niitä rotaatioissa
        self.thrust = 0

        # Pallo
        self.attached_ball = None

        # Abilityt
        self.basic_shot = bullet.BasicShot
        if special is not None:
            self.special = special
        else:
            self.special = bullet.Bouncer

        # Shipin ominaisuudet
        self.handling = float(current_ship.find('handling').text)  # kuinka monta astetta kääntyy per frame
        self.max_thrust = float(current_ship.find('max_thrust').text)
        self.max_speed = int(current_ship.find('max_speed').text)
        self.mass = float(current_ship.find('mass').text)
        self._max_acceleration = self.max_thrust / self.mass
        self.cooldown_multiplier_basic = float(current_ship.find('cooldown_multiplier_basic').text)
        self.cooldown_multiplier_special = float(current_ship.find('cooldown_multiplier_special').text)
        self._cooldown_after_ball_shot = 60
        self._cooldown_counter = self.basic_shot.cooldown
        self._cooldown_counter_special = self.special.cooldown
        self._recovery_time = float(current_ship.find('recovery_time').text)  # sekunteja jopa!
        self._recovery_started_at = 0

        # print "PlayerSprite groups: ", self.groups()

    def __repr__(self):
        return "<PlayerSprite {} {}>".format(self.owning_player_id, self.ship_name)

    def update(self, viewscreen_rect, player_group=groups.PlayerGroup, bullet_group=groups.BulletGroup):
        self.viewscreen_rect = viewscreen_rect
        """ Tämä haluaa tietää player- ja bulletgroupit että ne voi tarvittaessa määrittää vapaasti """
        # Lisätään liikemäärään thrust-vektori
        # Tässä jopa ottaa jo massan huomioon!
        if self.thrust:
            self.move_vector.add_to_velocity(self._max_acceleration, self.heading)

        self.update_movement()

        self.check_out_of_bounds()
        self.check_collision_with_wall_and_goal()
        self.check_collision_with_group(groups.BallGroup)
        self.check_collision_with_group(groups.PlayerGroup)
        self.check_collision_with_group(groups.BulletGroup)

        # Lasketaan cooldownia
        self._cooldown_counter += self.parent.clock.get_time()
        self._cooldown_counter_special += self.parent.clock.get_time()

        # Jos on pallo kytkettynä niin lisätään paljon cooldownia
        # TODO: laita toimimaan uudestaan
        # if self.attached_ball is not None:
        #     self._cooldown_counter = self._cooldown_after_ball_shot

        if self._recovery_started_at != 0:
            if (pygame.time.get_ticks() - self._recovery_started_at) // 1000 > self._recovery_time - 1:
                self.reset()
                self._recovery_started_at = 0

    def collided_with(self, other_object):
        """  
        Emme törmää palloon jos se on attachattu itseemme 
        Pallo-objekti hoitaa attachauksen pelaajaan, se ei ole tässä
        """
        apply_collision = 1
        if other_object in groups.BallGroup:
            if other_object == self.attached_ball:
                apply_collision = 0
            # Emme myöskään törmää palloon jos kukaan ei ole napannut sitä
            elif other_object.attached_player is None:
                apply_collision = 0

        if apply_collision:
            self.apply_collision_to_move_vector(other_object)

    def attach_ball(self, ball):
        if self.attached_ball is None:
            self.attached_ball = ball
            sound.force_play_sound(self.ball_capture_sound)

    def detach(self):
        self.attached_ball = None
        # self.radius = self.original_radius

    def accelerate(self):
        if self.thrust == 0:
            self.thrust = self.max_thrust
            if self.thrust_gfx is not None:
                self.thrust_gfx.visible = 1
            if not self.motor_sound_playing:
                sound.force_play_sound(self.motor_sound, -1)
                self.motor_sound_playing = 1
        else:
            if len(self.smoke_effect_image_files) > 0:
                self._smoke_counter += self.parent.clock.get_time()
                if self._smoke_counter > self._smoke_interval:
                    effect.SmokeEffect(start_position=(self.x, self.y),
                                       effect_type='smoke',
                                       parent=self.parent,
                                       attached_player=self,
                                       viewscreen_rect=self.viewscreen_rect,
                                       image_files=self.smoke_effect_image_files,
                                       offset=self.smoke_effect_offset)
                    self._smoke_counter = 0

    def stop_acceleration(self):
        if self.thrust > 0:
            self.thrust = 0
            if self.thrust_gfx is not None:
                self.thrust_gfx.visible = 0
            self.motor_sound.stop()
            self.motor_sound_playing = 0

    def rotate_right(self):
        self.heading -= self.handling
        if self.heading < 0:
            self.heading += 360
        self.rot_self_image_keep_size(self.heading)

    def rotate_left(self):
        self.heading += self.handling
        if self.heading > 359:
            self.heading -= 360
        self.rot_self_image_keep_size(self.heading)

    def shoot(self):
        # Ammutaan perusammus
        if self._cooldown_counter > self.basic_shot.cooldown or self.parent._is_client:
            # TODO: siirrä ääni bulletin ominaisuudeksi
            sound.force_play_sound(self.bullet_sound)
            self.basic_shot(shooting_player=self, level=self.level, parent=self.parent,
                            heading=self.heading)
            self._cooldown_counter = 0
            self.parent.add_event(GameEventTypes.ShootBasic, self.owning_player_id)

        # Jos pallo on liitettynä niin ammutaan se
        if self.attached_ball is not None:
            self.attached_ball.shoot(direction=self.heading, speed=10)
            self.attached_ball.detach()
            sound.force_play_sound(self.ball_shoot_sound)
            self.parent.add_event(GameEventTypes.ShootBall, self.owning_player_id)

    def shoot_special(self):
        """ Ammutaan erikoisammus """
        if self._cooldown_counter_special > self.special.cooldown or self.parent._is_client:
            sound.force_play_sound(self.bullet_sound)
            self.special(shooting_player=self, level=self.level, parent=self.parent,
                         heading=self.heading)
            self._cooldown_counter_special = 0
            self.parent.add_event(GameEventTypes.ShootSpecial, self.owning_player_id)

    def recover(self):
        """ Aloittaa recovery-laskennan """
        if not self.parent._is_client:
            self._recovery_started_at = pygame.time.get_ticks()
        if not self.parent.demogame:
            text.DisappearingText(clock=self.parent.clock, pos=WINDOW_CENTER_POINT, text="RECOVERING...",
                                  ms_visible=self._recovery_time * 1000, flashes=1, font_size=80, color=RED)

