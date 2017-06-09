# -*- coding: utf8 -*-
import pygame
import math
import random
import game_object
import game
import groups
import bullet
import text
import assets
import numpy
from colors import *
from pygame.locals import *
from constants import *
from collections import deque


""" Näyttää taustatoimintaa menun takana """


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


class BackgroundAction(game.AUTSBallGame):
    def __init__(self, window=None, darken=0):
        game.AUTSBallGame.__init__(self, window=window, level_name='Menu Background', demogame=1)
        # Tämä tummentaa tausta-actionin
        self.darken = darken
        self.darken_surface = pygame.Surface(WINDOW_SIZE)
        self.darken_surface.set_alpha(128)

        if self.level.background_image is not None:
            # generoidaan taustakuva
            self.background_image = pygame.Surface(WINDOW_SIZE)
            surface_rect = self.background_image.get_rect()
            image_rect = self.level.background_image.get_rect()
            for x in range(0, surface_rect.width, image_rect.width):
                for y in range(0, surface_rect.height, image_rect.height):
                    self.background_image.blit(self.level.background_image, (x, y))

        self.goal_green_pos = 50, 300
        self.goal_red_pos = 750, 300
        self.viewscreen_rect = pygame.Rect((0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))
        self.add_player(0, team='red', ship_name='Teafighter', special=bullet.Bouncer)
        self.add_player(1, team='green', ship_name='LactoAcidShip', special=bullet.DumbFire)
        self.add_player(2, team='red', ship_name='Muumi', special=bullet.Switcher)
        self.add_player(3, team='green', ship_name='FastShip', special=bullet.DumbFire)
        self.add_player(4, team='red', ship_name='Trademark Fighter', special=bullet.Dirtball)
        self.add_player(5, team='green', ship_name='Fatship', special=bullet.DumbFire)

        self.player_last_positions = {}
        for current_player in self.players:
            self.player_last_positions[current_player] = deque(maxlen=30)

        credits_text = text.make_credits_string()
        self.credits = text.ScrollingText(y_pos=590, screen_size_x=800, text=credits_text, scroll_speed=3)
        self.mouse = Mouse(level=self.level, parent=self, group=groups.EffectGroup, follows=self.credits,
                           x_offset=48, y_offset=-3)

        self.start()

    def update(self):
        if self.is_running:
            # Tämä estää errorin quitattaessa
            if self.quit_game is False:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.quit_game = True

                # Super-AI:
                for current_player in self.players:
                    # Kaasu pohjassa aina
                    self.players[current_player].accelerate()
                    if self.players[current_player].attached_ball is None:
                        # Suuntaa kohti palloa
                        self.players[current_player].goal = (self.ball.x, self.ball.y)
                    else:
                        # Jos pallo on napattu niin suuntaa kohti maalia
                        if self.players[current_player].team == 'red':
                            self.players[current_player].goal = self.goal_green_pos
                        else:
                            self.players[current_player].goal = self.goal_red_pos
                    # Asetetaan heading suoraan kohti targettia, kääntyminen on nössöille
                    new_heading = 270 - math.degrees(game_object.get_angle_in_radians(self.players[current_player].goal,
                                                                                      (self.players[current_player].x,
                                                                                       self.players[current_player].y)))
                    self.players[current_player].heading = new_heading
                    while self.players[current_player].heading > 359:
                        self.players[current_player].heading -= 360
                    while self.players[current_player].heading < 0:
                        self.players[current_player].heading += 360
                    self.players[current_player].rot_self_image_keep_size(self.players[current_player].heading)

                    # Ampuillaan randomilla
                    if self.players[current_player].attached_ball is None:
                        if random.randint(1, 20) == 1:
                            self.players[current_player].shoot()
                        if random.randint(1, 40) == 1:
                            self.players[current_player].shoot_special()

                    # Tarkistetaan ollaanko oltu jumissa 30 framea
                    # jos juu niin recoverataan
                    current_pos = (self.players[current_player].x, self.players[current_player].y)
                    self.player_last_positions[current_player].append(current_pos)
                    if len(self.player_last_positions[current_player]) > 16:
                        has_moved = 0
                        for logged_pos in self.player_last_positions[current_player]:
                            if logged_pos != current_pos:
                                has_moved = 1
                                break
                        if not has_moved:
                            self.players[current_player].recover()

                # Spritejen päivitykset tässä
                groups.BulletGroup.update(self.viewscreen_rect)
                groups.BallGroup.update(self.viewscreen_rect)
                groups.PlayerGroup.update(self.viewscreen_rect)
                groups.EffectGroup.update(self.viewscreen_rect)
                groups.TextGroup.update()

                # Päivitetään graffat vaan joka toisessa framessa
                if self.frame_counter % 2 == 0:
                    self.update_graphics()

                # Pelilogiikan FPS target 60, eli graffoilla siis 30
                self.clock.tick(GRAPHICS_FPS)

        if self.quit_game:
            self.exit()

    def update_graphics(self):
        """ Grafiikoiden päivitysmetodi """
        # Ruutu tyhjäksi
        self.window.fill(BLACK)

        # Piirretään levelin tausta
        self.window.blit(self.background_image, (0, 0))

        # Piirretään level
        self.window.blit(self.level.image, (0, 0))

        # Bullettien, pelaajan, pallon piirrot
        groups.BulletGroup.draw(self.window)
        groups.BallGroup.draw(self.window)
        groups.PlayerGroup.draw(self.window)
        groups.EffectGroup.draw(self.window)
        groups.TextGroup.draw(self.window)

        # HUD
        text.show_score(self.window, (50, 10), self.score_green, team=0)
        text.show_score(self.window, (700, 10), self.score_red, team=1)

        if self.darken:
            self.window.blit(self.darken_surface, (0,0))

    def calc_viewscreen_rect(self):
        """ Laskee viewscreen_rectin ja background_view_rectin """
        # Viewscreen rect: viewscreen absoluuttisissa koordinaateissa
        self.viewscreen_rect = pygame.Rect((0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]))

    def score(self, scoring_team):
        """ Tätä kutsutaan kun tulee maali """
        if scoring_team == 'red':
            self.score_red += 1
            goal_text_color = RED
        elif scoring_team == 'green':
            self.score_green += 1
            goal_text_color = GREEN
        text.DisappearingText(clock=self.clock, pos=(400, 550), text="GOAL!!!", ms_visible=2000,
                              color=goal_text_color, font_size=120, flashes=1)


def debug_run():
    pygame.init()
    window = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Background Action test")
    # Assettien esilataus
    assets.load_assets(window)

    bg_game = BackgroundAction(window, darken=1)

    while bg_game.is_running:
        bg_game.update()
        if bg_game.is_running:
            pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    debug_run()

