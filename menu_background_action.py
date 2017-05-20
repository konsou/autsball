# -*- coding: utf8 -*-
import game_object
import game
import pygame
import math
import random
import player
import ball
import level
import groups
import effect
import bullet
import text
from colors import *
from pygame.locals import *
from constants import *

""" IHAN HIRVEÄ SOTKU MUTTA TOIMII PÄÄOSIN """
# TODO: MAJOR CLEANUP
# TODO: äänet pois
# TODO: suuri optimointi, tökkii

background_group = pygame.sprite.GroupSingle()


class DemoPlayer(player.PlayerSprite):
    def __init__(self, team=None, level=None, parent=None, pos=None):
        if team == 'red':
            image_file = 'gfx/ship1_red_20px.png'
        else:
            image_file = 'gfx/ship1_green_20px.png'

        # Lisätään PlayerGroup-ryhmään
        game_object.GameObject.__init__(self, group=groups.PlayerGroup, level=level, parent=parent,
                                        image_file=image_file)

        # Graffat
        self.motor_flame_image_file = 'gfx/motor_flame_10.png'
        self.thrust_gfx = effect.EffectSprite(attached_player=self, image_file=self.motor_flame_image_file,
                                                effect_type='motorflame', visible=0)
        self.viewscreen_rect = (0, 0, 800, 600)

        # Koordinaatit

        # Heading ja thrust
        self.heading = 0
        self.thrust = 0

        # Pallo
        self.attached_ball = None

        # Shipin ominaisuudet
        self.handling = int(5)  # kuinka monta astetta kääntyy per frame
        self.max_thrust = 0.35  # kun FPS 60, gravity 0.1 ja mass 1 niin 0.35 on aika hyvä
        self.max_speed = 10
        self.mass = 1.0
        self._cooldown_basic_shot = 5  # framea
        self._cooldown_special = 60
        self._cooldown_after_ball_shot = 60  # cooldown sen jälkeen kun pallo on ammuttu
        self._cooldown_counter = 0  # cooldown-counter1
        self._cooldown_counter_special = 0
        self._recovery_time = 3  # sekunteja jopa!
        self._recovery_started_at = 0
        self._max_acceleration = self.max_thrust / self.mass

        self.gravity_affects = 1
        self.team = team

        if pos is not None:
            self.start_position = pos
        else:
            if self.team == 'red':
                self.start_position = (700, 300)
            else:
                self.start_position = (100, 300)

        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.x, self.y

        self.goal_green_pos = 50, 300
        self.goal_red_pos = 750, 300
        self.goal = 0, 0

        self.motor_sound_playing = 0
        self.motor_sound = None
        self.ball_capture_sound = None

    def update(self):
        if self.attached_ball is None:
            self.goal = self.parent.ball_pos

        else:
            if self.team == 'red':
                self.goal = self.goal_green_pos
            else:
                self.goal = self.goal_red_pos
        # print("Team, goal point:", self.team, goal)
        # print("Ball attached:", self.attached_ball)
        # pygame.draw.line(window, game_object.blue, goal, (self.x, self.y))

        new_heading = 270 - math.degrees(game_object.get_angle_in_radians(self.goal, (self.x, self.y)))
        self.heading = new_heading
        while self.heading > 359:
            self.heading -= 360
        while self.heading < 0:
            self.heading += 360
        self.rot_self_image_keep_size(self.heading)

        # heading_difference = game_object.get_angle_difference(self.heading, new_heading, degrees=1)
        # print("Heading old, goal, difference:", self.heading, new_heading, heading_difference)
        # if heading_difference > 0:
            # print("Rotating right...")
            # self.rotate_right()
        # else:
            # print("Rotating left...")
            # self.rotate_left()
        # print("New heading:", self.heading)
        # print("---")
        self.accelerate()
        if self.attached_ball is None:
            if random.randint(1, 20) == 1:
                self.shoot()

        player.PlayerSprite.update(self, self.viewscreen_rect)

    def shoot(self):
        """ Pitää overrideta kun randomisyystä vakioarvot ei toimi """
        if self._cooldown_counter == 0:
            bullet_x = int(28 * math.sin(math.radians(self.heading)) * -1 + self.x)
            bullet_y = int(28 * math.cos(math.radians(self.heading)) * -1 + self.y)
            bullet.BasicShot(level=self.level, parent=self.parent, pos=(bullet_x, bullet_y), direction=self.heading,
                         speed=20)
            self._cooldown_counter = self._cooldown_basic_shot


class DemoBall(ball.BallSprite):
    def __init__(self, level, parent):
        ball.BallSprite.__init__(self, level=level, parent=parent)
        self.gravity_affects = 1
        self.image = pygame.image.load('gfx/ball_50_red.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.start_position = (400, 300)
        self.rect.center = self.start_position
        self.x, self.y = self.start_position
        self.x_previous, self.y_previous = self.start_position


class Mouse(game_object.GameObject):
    def __init__(self, level=None, parent=None, group=groups.EffectGroup, start_position=(400, 579),
                 image_file=['gfx/mouse_1.png', 'gfx/mouse_2.png'], follows=None,
                 x_offset=0, y_offset=0):
        game_object.GameObject.__init__(self, level=level, parent=parent, group=group, start_position=start_position,
                                        image_file=image_file)
        self.follows = follows
        self.x_offset = x_offset
        self.y_offset = y_offset

    def update(self, viewscreen_rect):
        self.viewscreen_rect = viewscreen_rect
        self.animate()
        self.x = self.follows.rect.topleft[0] + self.x_offset
        self.y = self.follows.rect.topleft[1] + self.y_offset
        self.update_rect()


class BackgroundAction(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, background_group)

        self.clock = pygame.time.Clock()

        # Vakioita
        self.gravity = 0.1
        self.screen_size_x = WINDOW_SIZE[0]
        self.screen_size_y = WINDOW_SIZE[1]
        self.screen_center_point = self.screen_size_x // 2, self.screen_size_y // 2

        #self.level = level.Level(image_file='gfx/menu_background_level.png')
        self.level = level.Level(level_name='Menu Background', colorkey=None)
        self.ship1 = DemoPlayer(team='green', level=self.level, parent=self, pos=(700, 200))
        self.ship2 = DemoPlayer(team='green', level=self.level, parent=self, pos=(700, 300))
        self.ship3 = DemoPlayer(team='green', level=self.level, parent=self, pos=(700, 400))
        self.ship4 = DemoPlayer(team='red', level=self.level, parent=self, pos=(100, 200))
        self.ship5 = DemoPlayer(team='red', level=self.level, parent=self, pos=(100, 300))
        self.ship6 = DemoPlayer(team='red', level=self.level, parent=self, pos=(100, 400))
        self.ball = DemoBall(level=self.level, parent=self)

        credits_text = text.make_credits_string()
        self.credits = text.ScrollingText(y_pos=590, screen_size_x=800, text=credits_text, scroll_speed=3)
        self.mouse = Mouse(level=self.level, parent=self, group=groups.EffectGroup, follows=self.credits,
                           x_offset=48, y_offset=-3)

        self.image = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]))
        self.rect = self.image.get_rect()
        self.viewscreen_rect = (0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1])

        self.ball_pos = (self.ball.x, self.ball.y)

        self.checked_collisions = set()

        self.score_green = 0
        self.score_red = 0

    def update(self):
        self.clock.tick()

        self.checked_collisions = set()
        self.ball_pos = (self.ball.x, self.ball.y)

        groups.BulletGroup.update(self.viewscreen_rect)
        groups.BallGroup.update(self.viewscreen_rect)
        groups.PlayerGroup.update()
        groups.EffectGroup.update(self.viewscreen_rect)
        groups.TextGroup.update()

        groups.LevelGroup.draw(self.image)
        groups.BallGroup.draw(self.image)
        groups.PlayerGroup.draw(self.image)
        groups.BulletGroup.draw(self.image)
        groups.EffectGroup.draw(self.image)
        groups.TextGroup.draw(self.image)

        text.show_text(self.image, (10, 10), str(self.score_green), color=GREEN, font_size=40)
        text.show_text(self.image, (750, 10), str(self.score_red), color=RED, font_size=40)

    def score(self, scoring_team=None):
        self.ship1.detach()
        self.ship2.detach()
        self.ship3.detach()
        self.ship4.detach()
        self.ship5.detach()
        self.ship6.detach()
        """ Tätä kutsutaan kun tulee maali """
        if scoring_team == 'red':
            self.score_red += 1
            goal_text_color = RED
        elif scoring_team == 'green':
            self.score_green += 1
            goal_text_color = GREEN
        text.DisappearingText(clock=self.clock, pos=(400,525), text="GOAL!!!", ms_visible=2000,
                                  color=goal_text_color, font_size=120, flashes=1)

    def kill_me(self):
        groups.empty_groups()
        background_group.empty()
        self.kill()


def debug_run():
    pygame.init()
    global window
    window = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
    pygame.display.set_caption("Menu test")
    clock = pygame.time.Clock()

    background_action = BackgroundAction()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONUP:
                #print event.pos
                effect.Explosion(pos=event.pos)

        window.fill((0, 0, 0))
        background_group.update()
        background_group.draw(window)

        pygame.display.update()
        clock.tick(30)

    pygame.quit()

if __name__ == '__main__':
    debug_run()

