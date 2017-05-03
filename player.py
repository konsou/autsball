# -*- coding: utf8 -*-
import pygame
import math
import game_object
import effect
import bullet
import groups
from colors import *


class PlayerSprite(game_object.GameObject):
    def __init__(self, level=None, parent=None, group=groups.PlayerGroup):
        # Lisätään ryhmään
        game_object.GameObject.__init__(self, group=group, level=level, parent=parent,
                                        image_file='gfx/ship1_red_20px.png')

        # Graffat
        self.motor_flame_image = pygame.image.load('gfx/motor_flame_10.png').convert_alpha()
        self.thrust_gfx = effect.EffectSprite(attached_player=self, image=self.motor_flame_image,
                                       effect_type='motorflame', visible=0, parent=parent)
        self.rect.center = self.parent.screen_center_point
        self.is_centered_on_screen = 1

        # Sound effex
        self.motor_sound = pygame.mixer.Sound(file='sfx/shhhh_v2.wav')
        self.motor_sound_playing = 0
        self.bullet_sound = pygame.mixer.Sound(file='sfx/pop.wav')
        self.ball_shoot_sound = pygame.mixer.Sound(file='sfx/pchou.wav')
        self.ball_capture_sound = pygame.mixer.Sound(file='sfx/ball_capture.wav')
        self.wall_collide_sound = pygame.mixer.Sound(file='sfx/thump4.wav')
        self.bullet_collide_sound = pygame.mixer.Sound(file='sfx/metal_thud_2.wav')

        # Koordinaatit
        self.start_position = (700, 1200)
        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.x, self.y

        # Heading ja thrust
        self.heading = 0  # HUOM! Heading asteina koska Pygame käyttää niitä rotaatioissa
        self.thrust = 0

        # Pallo
        self.attached_ball = None

        # Shipin ominaisuudet
        self.handling = int(5)  # kuinka monta astetta kääntyy per frame
        self.max_thrust = 0.35  # kun FPS 60, gravity 0.1 ja mass 1 niin 0.35 on aika hyvä
        self.max_speed = 10
        self.mass = 1.0
        self.cooldown_basic_shot = 5 # framea
        self.cooldown_after_ball_shot = 60 # cooldown sen jälkeen kun pallo on ammuttu
        self.cooldown_counter = 0 # cooldown-counter1
        self.recovery_time = 3  # sekunteja jopa!
        self.recovery_started_at = 0

    def update(self, player_group=groups.PlayerGroup, bullet_group=groups.BulletGroup):
        """ Tämä haluaa tietää player- ja bulletgroupit että ne voi tarvittaessa määrittää vapaasti """
        # Lisätään liikemäärään thrust-vektori
        # Tässä jopa ottaa jo massan huomioon!
        self.move_vector.add_to_vx((self.thrust / self.mass * math.sin(math.radians(self.heading)) * -1))
        self.move_vector.add_to_vy((self.thrust / self.mass * math.cos(math.radians(self.heading)) * -1))

        self.update_movement()

        self.check_out_of_bounds()
        self.check_collision_with_wall_and_goal()
        self.check_collision_with_players(player_group)
        self.check_collision_with_bullets(bullet_group)

        # Lasketaan cooldownia
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1

        # Jos on pallo kytkettynä niin lisätään paljon cooldownia
        if self.attached_ball is not None:
            self.cooldown_counter = self.cooldown_after_ball_shot

        if self.recovery_started_at != 0:
            if (pygame.time.get_ticks() - self.recovery_started_at) // 1000 > self.recovery_time - 1:
                self.reset()
                self.recovery_started_at = 0

    def attach_ball(self, ball):
        if self.attached_ball is None:
            self.attached_ball = ball
            self.force_play_sound(self.ball_capture_sound)

    def detach(self):
        self.attached_ball = None
        # self.radius = self.original_radius

    def accelerate(self):
        self.thrust = self.max_thrust
        self.thrust_gfx.visible = 1
        if not self.motor_sound_playing:
            if self.motor_sound is not None:
                self.force_play_sound(self.motor_sound, -1)
                self.motor_sound_playing = 1

    def stop_acceleration(self):
        self.thrust = 0
        self.thrust_gfx.visible = 0
        self.motor_sound.stop()
        self.motor_sound_playing = 0

    def rotate_right(self):
        self.heading -= self.handling
        if self.heading < 0:
            self.heading += 360
        # TODO: laske rotaatiot latausvaiheessa valmiiksi
        self.rot_self_image_keep_size(self.heading)

    def rotate_left(self):
        self.heading += self.handling
        if self.heading > 360:
            self.heading -= 360
        self.rot_self_image_keep_size(self.heading)

    def shoot(self):
        # Ammutaan perusammus
        # Pelaajan nopeus vaikuttaa ammuksen vauhtiin
        # TODO: pelaajan nopeus lisää aina ammuksen nopeutta saman verran riippumatta siitä mihin suuntaan se ammutaan!
        # Asetetaan ammuksen alkupiste riittävän kauas pelaajasta ettei törmää saman tien siihen
        if self.cooldown_counter == 0:
            self.force_play_sound(self.bullet_sound)
            bullet_x = int(10 * math.sin(math.radians(self.heading)) * -1 + self.x)
            bullet_y = int(10 * math.cos(math.radians(self.heading)) * -1 + self.y)
            bullet.BulletSprite(level=self.level, parent=self.parent, x=bullet_x, y=bullet_y, direction=self.heading,
                         speed=10 + self.move_vector.get_speed())
            self.cooldown_counter = self.cooldown_basic_shot

        # Jos pallo on liitettynä niin ammutaan se
        if self.attached_ball is not None:
            # ball_x = self.attached_ball.image.get_width() * math.sin(math.radians(self.heading)) * -1 + self.x
            # ball_y = self.attached_ball.image.get_height() * math.cos(math.radians(self.heading)) * -1 + self.y

            # self.attached_ball.shoot(x=ball_x, y=ball_y, direction=self.heading, speed=10)
            self.attached_ball.shoot(direction=self.heading, speed=10)
            self.attached_ball.detach()
            self.force_play_sound(self.ball_shoot_sound)

    def recover(self):
        """ Aloittaa recovery-laskennan """
        self.recovery_started_at = pygame.time.get_ticks()
        DisappearingText(pos=self.parent.screen_center_point, text="RECOVERING...", frames_visible=240, flashes=1,
                         font_size=80, color=RED)


