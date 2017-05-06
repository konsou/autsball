# -*- coding: utf8 -*-
import pygame
import math
import sys
import music
import groups
import level
import player
import ball
import text
from pygame.locals import *
from colors import *


class AUTSBallGame:
    def __init__(self):
        self.is_running = False
        self.local_player_id = 0

        # Vakioita
        self.gravity = 0.1
        self.screen_size_x = 800
        self.screen_size_y = 600
        self.screen_center_point = self.screen_size_x // 2, self.screen_size_y // 2

        # Pygamen inittejä
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.init()
        pygame.mixer.init()
        self.win = pygame.display.set_mode((self.screen_size_x, self.screen_size_y))
        pygame.display.set_caption("AUTSball")
        self.clock = pygame.time.Clock()

        # Taustamusiikki
        self.music_player = music.MusicPlayer(screen='game', window_size=(self.screen_size_x, self.screen_size_y),
                                              pos='bottomleft', group=groups.TextGroup, shuffle=0)

        # SFX
        self.goal_green_sound = pygame.mixer.Sound(file='sfx/goal_green.wav')
        self.goal_red_sound = pygame.mixer.Sound(file='sfx/goal_red.wav')

        # Latauskuva koska levelin latauksessa voi kestää jonkin aikaa
        self.loading_image = pygame.image.load('gfx/loading.png').convert_alpha()
        self.win.blit(self.loading_image, self.loading_image.get_rect())
        pygame.display.update()

        # TODO: tähän assettien esilataus
        # Instansioidaan leveli, tämä lataa myös level-kuvan joka voi olla iiisooo
        # self.current_level = level.Level(background_image_file='gfx/cave_background.png')
        self.current_level = level.Level(level_name='Test Level')
        # Instansioidaan pelaaja ja pallo
        self.players = {}
        self.player_count = 0
        self.ball = ball.BallSprite(level=self.current_level, parent=self)

        self.viewscreen_rect = None
        self.background_view_rect = None

        self.score_green = 0
        self.score_red = 0

        self.quit_game = False
        self.frame_counter = 0

    def start(self):
        if not self.is_running:
            self.is_running = True

            self.music_player.play()

    def destroy(self):
        self.is_running = False
        self.players.clear()
        self.player_count = 0
        groups.empty_groups()
        self.music_player.stop()

    def add_player(self, player_id=None):
        # Lisää pelaajan pelaajalistaan
        if player_id == None:
            self.players[self.player_count] = player.PlayerSprite(player_id=player_id,
                                                           level=self.current_level,
                                                           parent=self,
                                                           spawn_point=self.current_level.player_spawns_team_1[
                                                               self.player_count])

        else:
            self.players[player_id] = player.PlayerSprite(player_id=player_id,
                                                   level=self.current_level,
                                                   parent=self,
                                                   spawn_point=self.current_level.player_spawns_team_1[
                                                       self.player_count])

        self.player_count += 1

    def remove_player(self, player_id):
        # Poistaa pelaajan pelaajalistasta ja palauttaa kyseisen pelaajan tai Nonen jos pelaajaa ei löydy
        return self.players.pop(player_id, None)

    def update(self):
        if self.is_running:
            # Tämä estää errorin quitattaessa
            if self.quit_game is False:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.quit_game = True
                    if event.type == music.MUSIC_FINISHED:
                        self.music_player.next()

                pressed_keys = pygame.key.get_pressed()
                if pressed_keys[K_UP]:
                    self.players[self.local_player_id].accelerate()
                else:
                    self.players[self.local_player_id].stop_acceleration()
                if pressed_keys[K_RIGHT]:
                    self.players[self.local_player_id].rotate_right()
                if pressed_keys[K_LEFT]:
                    self.players[self.local_player_id].rotate_left()
                if pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]:
                    self.players[self.local_player_id].shoot()
                if pressed_keys[K_LCTRL] or pressed_keys[K_RCTRL]:
                    self.players[self.local_player_id].shoot_special()
                if pressed_keys[pygame.K_BACKSPACE]:
                    self.players[self.local_player_id].recover()

                # Viewscreen rect: viewscreen absoluuttisissa koordinaateissa
                self.viewscreen_rect = (self.players[self.local_player_id].x - self.screen_size_x // 2,
                                        self.players[self.local_player_id].y - self.screen_size_y // 2,
                                        self.screen_size_x,
                                        self.screen_size_y)

                # Background view rect: näytetään levelistä oikea kohta
                self.background_view_rect = (self.screen_size_x // 2 - self.players[self.local_player_id].x,
                                             self.screen_size_y // 2 - self.players[self.local_player_id].y,
                                             self.screen_size_x,
                                             self.screen_size_y)

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
                self.clock.tick(60)

        if self.quit_game:
            self.exit()

    def update_graphics(self):
        """ Grafiikoiden päivitysmetodi """

        # Ruutu tyhjäksi
        self.win.fill((0, 0, 0))
        # Piirretään taustakuva jos on
        if self.current_level.background_image:
            image_width, image_height = self.current_level.background_image.get_size()
            for y in range(0, self.screen_size_y, image_height):
                for x in range(0, self.screen_size_x, image_width):
                    self.win.blit(self.current_level.background_image, (x, y))
        # Piirretään levelistä vain viewscreenin kokoinen alue, pelaaja keskellä
        self.win.blit(self.current_level.image, self.background_view_rect)

        # Bullettien, pelaajan, pallon piirrot
        groups.BulletGroup.draw(self.win)
        groups.BallGroup.draw(self.win)
        groups.PlayerGroup.draw(self.win)
        groups.EffectGroup.draw(self.win)
        groups.TextGroup.draw(self.win)

        # HUD
        # self.show_text((10, 10), "Speed: " + str(math.hypot(self.player[0].vx, self.player[0].vy)))
        text.show_text(self.win, (10, 50), "FPS: " + str(self.clock.get_fps()))
        text.show_text(self.win, (10, 10), str(self.score_green), color=GREEN, font_size=40)
        text.show_text(self.win, (750, 10), str(self.score_red), color=RED, font_size=40)

        # Näytetään pallonsuuntamarkkeri
        # TODO: muuta pallon sijaan nuoli joka osoittaa oikeaan suuntaan
        # TODO: tee niin että jos pallo on lähempänä kuin 100 pikseliä niin markkeri on pallon päällä
        if self.players[self.local_player_id].attached_ball is None:
            ball_angle = self.get_ball_angle_in_radians(self.ball)
            vx = int(100 * math.cos(ball_angle))
            vy = int(100 * math.sin(ball_angle))
            pygame.draw.circle(self.win, (0, 0, 255),
                               (self.screen_size_x // 2 + vx, self.screen_size_y // 2 + vy), 5)

        # Displayn update
        pygame.display.update()

    def score(self, scoring_team):
        """ Tätä kutsutaan kun tulee maali """
        if scoring_team == 'RED':
            self.score_red += 1
            goal_text_color = RED
            self.goal_red_sound.play()
        elif scoring_team == 'GREEN':
            self.score_green += 1
            goal_text_color = GREEN
            self.goal_green_sound.play()
        text.DisappearingText(pos=self.screen_center_point, text="GOAL!!!", frames_visible=120,
                         color=goal_text_color, font_size=120, flashes=1)

    def get_ball_angle_in_radians(self, ball):
        """ Tämä auttaa pallon suuntamarkkerin piirrossa """
        point2 = (self.screen_size_x // 2, self.screen_size_y // 2)
        point1 = ball.rect.center
        x_difference = point1[0] - point2[0]
        y_difference = point1[1] - point2[1]
        return math.atan2(y_difference, x_difference)


    def exit(self):
        """ Tähän voi laittaa jotain mitä tulee ennen poistumista """
        pygame.quit()
        # Jostain syystä vaatii myös tämän, muuten jää infinite looppi taustalle vaikka pygame-ikkuna katoaakin
        sys.exit()


if __name__ == '__main__':
    game = AUTSBallGame()
    while True:
        game.update()