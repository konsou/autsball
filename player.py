# -*- coding: utf8 -*-
import pygame
import math
import game_object
import effect
import bullet
import groups
import text
from colors import *
from pygame.locals import *
from assets import assets, assets_rot


class PlayerSprite(game_object.GameObject):
    def __init__(self, player_id=None, team=None, level=None, parent=None, ship_name='V-Wing',
                 group=groups.PlayerGroup, spawn_point=None):
        self.owning_player_id = player_id
        self.team = team
        self.name = ship_name

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

        # Thrust-gfx
        thrust_image_file = []
        for value in current_ship.findall('images/motor_flame_image'):
            thrust_image_file.append(value.text)

        self.thrust_gfx = effect.EffectSprite(attached_player=self, image_file=thrust_image_file,
                                              visible=0, parent=parent)
        self.rect.center = self.parent.screen_center_point
        if self.owning_player_id == parent.local_player_id:
            self.is_centered_on_screen = 1
        else:
            self.is_centered_on_screen = 0

        self._smoke_interval = 30  # Smoken spawn tiheys millisekunteina
        self._smoke_counter = 0
        self.smoke_effect_image_files = []
        for value in current_ship.findall('images/rear_smoke_image'):
            self.smoke_effect_image_files.append(value.text)
        # self.smoke_effect_images = effect.SmokeEffect.preload_images(smoke_image_file)  # ladataan kuvat etukäteen

        # Sound effex
        self.motor_sound = assets[current_ship.find('sounds/motor_sound').text]
        self.motor_sound_playing = 0
        self.bullet_sound = assets[current_ship.find('sounds/bullet_sound').text]
        self.ball_shoot_sound = assets[current_ship.find('sounds/ball_shoot_sound').text]
        self.ball_capture_sound = assets[current_ship.find('sounds/ball_capture_sound').text]
        self.wall_collide_sound = assets[current_ship.find('sounds/wall_collide_sound').text]
        self.bullet_collide_sound = assets[current_ship.find('sounds/bullet_collide_sound').text]

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

        # Shipin ominaisuudet
        self.handling = float(current_ship.find('handling').text)  # kuinka monta astetta kääntyy per frame
        self.max_thrust = float(current_ship.find('max_thrust').text)  # kun FPS 60, gravity 0.1 ja mass 1 niin 0.35 on aika hyvä
        self.max_speed = int(current_ship.find('max_speed').text)
        self.mass = float(current_ship.find('mass').text)
        self._max_acceleration = self.max_thrust / self.mass
        self._cooldown_basic_shot = int(current_ship.find('cooldown_basic_shot').text)  # framea
        self._cooldown_special = int(current_ship.find('cooldown_special').text)
        self._cooldown_after_ball_shot = int(current_ship.find('cooldown_after_ball_shot').text) # cooldown sen jälkeen kun pallo on ammuttu
        self._cooldown_counter = 0  # cooldown-counter1
        self._cooldown_counter_special = 0
        self._recovery_time = float(current_ship.find('recovery_time').text)  # sekunteja jopa!
        self._recovery_started_at = 0

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
        self.check_collision_with_group(player_group)
        self.check_collision_with_group(bullet_group)

        # Lasketaan cooldownia
        if self._cooldown_counter > 0:
            self._cooldown_counter -= 1
        if self._cooldown_counter_special > 0:
            self._cooldown_counter_special -= 1

        # Jos on pallo kytkettynä niin lisätään paljon cooldownia
        if self.attached_ball is not None:
            self._cooldown_counter = self._cooldown_after_ball_shot

        if self._recovery_started_at != 0:
            if (pygame.time.get_ticks() - self._recovery_started_at) // 1000 > self._recovery_time - 1:
                self.reset()
                self._recovery_started_at = 0

    def attach_ball(self, ball):
        if self.attached_ball is None:
            self.attached_ball = ball
            self.force_play_sound(self.ball_capture_sound)

    def detach(self):
        self.attached_ball = None
        # self.radius = self.original_radius

    def accelerate(self):
        if self.thrust == 0:
            self.thrust = self.max_thrust
            self.thrust_gfx.visible = 1
            if not self.motor_sound_playing:
                self.force_play_sound(self.motor_sound, -1)
                self.motor_sound_playing = 1
        else:
            if type(self).__name__ is not 'DemoPlayer':
                self._smoke_counter += self.parent.clock.get_time()
                if self._smoke_counter > self._smoke_interval:
                    effect.SmokeEffect(start_position=(self.x, self.y),
                                       effect_type='smoke',
                                       parent=self.parent,
                                       attached_player=self,
                                       viewscreen_rect=self.viewscreen_rect,
                                       image_files=self.smoke_effect_image_files)
                    self._smoke_counter = 0

    def stop_acceleration(self):
        if self.thrust > 0:
            self.thrust = 0
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
        # Pelaajan nopeus vaikuttaa ammuksen vauhtiin
        # TODO: pelaajan nopeus lisää aina ammuksen nopeutta saman verran riippumatta siitä mihin suuntaan se ammutaan!
        # Asetetaan ammuksen alkupiste riittävän kauas pelaajasta ettei törmää saman tien siihen
        if self._cooldown_counter == 0:
            self.force_play_sound(self.bullet_sound)
            bullet_x = int(10 * math.sin(math.radians(self.heading)) * -1 + self.x)
            bullet_y = int(10 * math.cos(math.radians(self.heading)) * -1 + self.y)
            bullet.BasicShot(level=self.level, parent=self.parent, pos=(bullet_x, bullet_y), direction=self.heading,
                         speed=10 + self.move_vector.get_speed())
            self._cooldown_counter = self._cooldown_basic_shot

        # Jos pallo on liitettynä niin ammutaan se
        if self.attached_ball is not None:
            # ball_x = self.attached_ball.image.get_width() * math.sin(math.radians(self.heading)) * -1 + self.x
            # ball_y = self.attached_ball.image.get_height() * math.cos(math.radians(self.heading)) * -1 + self.y

            # self.attached_ball.shoot(x=ball_x, y=ball_y, direction=self.heading, speed=10)
            self.attached_ball.shoot(direction=self.heading, speed=10)
            self.attached_ball.detach()
            self.force_play_sound(self.ball_shoot_sound)

    def shoot_special(self):
        """ Ammutaan erikoisammus """
        # Asetetaan ammuksen alkupiste riittävän kauas pelaajasta ettei törmää saman tien siihen
        if self._cooldown_counter_special == 0:
            self.force_play_sound(self.bullet_sound)
            # TODO: laske dx, dy ammuksen initissä
            bullet_x = int(20 * math.sin(math.radians(self.heading)) * -1 + self.x)
            bullet_y = int(20 * math.cos(math.radians(self.heading)) * -1 + self.y)
            bullet.Switcher(shooting_player=self, level=self.level, parent=self.parent, pos=(bullet_x, bullet_y),
                            direction=self.heading, speed=10 + self.move_vector.get_speed())
            self._cooldown_counter_special = self._cooldown_special

    def recover(self):
        """ Aloittaa recovery-laskennan """
        self._recovery_started_at = pygame.time.get_ticks()
        text.DisappearingText(pos=self.parent.screen_center_point, text="RECOVERING...", frames_visible=240, flashes=1,
                         font_size=80, color=RED)

