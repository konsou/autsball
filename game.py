# -*- coding: utf8 -*-
import pygame
import music
import sound
import groups
import level
import player
import ball
import text
import effect
import bullet
import ui_components
from pygame.locals import *
from colors import *
from constants import *
from assets import assets, load_assets


class AUTSBallGame:
    def __init__(self, window=None, level_name='Test Level', demogame=0, client=False):
        groups.empty_groups()
        self.demogame = demogame
        self.window = window
        self.is_running = False
        self.local_player_id = 0
        self._is_client = client

        # Pygamen inittejä
        # HUOM! Inittien järjestys tärkeä!
        # 1) mixerin pre-init
        # 2) pygamen init
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
        pygame.init()
        # self.window = pygame.display.set_mode(WINDOW_SIZE)
        # pygame.display.set_caption("AUTSball")
        self.clock = pygame.time.Clock()

        # Taustamusiikki
        if not demogame:
            self.music_player = music.MusicPlayer(screen='game', window_size=WINDOW_SIZE,
                                                  pos='bottomleft', group=groups.TextGroup, shuffle=0)

        # SFX
        if not demogame:
            self.goal_green_sound = assets['sfx/goal_green.wav']
            self.goal_red_sound = assets['sfx/goal_red.wav']
        else:
            self.goal_green_sound = None
            self.goal_red_sound = None

        # Instansioidaan leveli
        self.current_level = level.Level(level_name=level_name)
        self.gravity = self.current_level.gravity

        # Instansioidaan pelaaja ja pallo
        self.players = {}
        self.player_count = 0
        self.player_count_team = {'red': 0, 'green': 0}

        self.ball = ball.BallSprite(level=self.current_level, parent=self)

        self.viewscreen_rect = None
        self.background_view_rect = None

        self.score_green = 0
        self.score_red = 0

        self.quit_game = False
        self.frame_counter = 0

        # Ladataan numerokuvat
        text.init_scores()

    def start(self):
        if not self.is_running:
            self.is_running = True

            # Lasketaan viewscreen- ja background rectit
            self.calc_viewscreen_rect()

            if not self.demogame:
                self.music_player.play()

    def destroy(self):
        self.is_running = False
        self.players.clear()
        self.player_count = 0
        self.player_count_team = {'red': 0, 'green': 0}
        # groups.empty_groups()
        try:
            self.music_player.stop()
        except AttributeError:
            pass

    def add_player(self, player_id=None, team=None, ship_name='Fatship', special=None):
        # Lisää pelaajan pelaajalistaan
        if player_id is None:
            self.players[self.player_count] = player.PlayerSprite(player_id=player_id,
                                                                  team=team,
                                                                  level=self.current_level,
                                                                  parent=self,
                                                                  ship_name=ship_name,
                                                                  spawn_point=self.current_level.player_spawns[team][
                                                                              self.player_count_team[team]],
                                                                  special=special)

        else:
            self.players[player_id] = player.PlayerSprite(player_id=player_id,
                                                          team=team,
                                                          level=self.current_level,
                                                          parent=self,
                                                          ship_name=ship_name,
                                                          spawn_point=self.current_level.player_spawns[team][
                                                                      self.player_count_team[team]],
                                                          special=special)

        self.player_count += 1
        self.player_count_team[team] += 1

    def remove_player(self, player_id):
        # Poistaa pelaajan pelaajalistasta ja palauttaa kyseisen pelaajan tai Nonen jos pelaajaa ei löydy
        return self.players.pop(player_id, None)

    def update(self, server_updates=None):
        if self.is_running:
            # Tämä estää errorin quitattaessa
            if self.quit_game is False:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.quit_game = True
                    if event.type == music.MUSIC_FINISHED:
                        self.music_player.next()
                if server_updates is None:
                    #Tähän silmukka, jossa käydään clientiltä tulleet komennot pelaajittain läpi
                    if not self._is_client:
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

                        # Spritejen päivitykset tässä
                        groups.BulletGroup.update(self.viewscreen_rect)
                        groups.BallGroup.update(self.viewscreen_rect)
                        groups.PlayerGroup.update(self.viewscreen_rect)
                        groups.EffectGroup.update(self.viewscreen_rect)
                        groups.TextGroup.update()
                else:
                    # self.calc_viewscreen_rect()
                    # print "Server sent this info:"
                    if server_updates is not None:
                        # print server_updates
                        # print "Current players:", self.players
                        for server_update_key in server_updates:
                            #print server_update_key, server_updates[server_update_key]
                            if server_update_key == 'players':
                                for current_player in server_updates[server_update_key]:
                                    current_player_int = int(current_player)
                                    self.players[current_player_int].x = server_updates[server_update_key][current_player]['x']
                                    self.players[current_player_int].y = server_updates[server_update_key][current_player]['y']
                                    self.players[current_player_int].heading = server_updates[server_update_key][current_player]['heading']
                                    self.players[current_player_int].update_rect(self.viewscreen_rect)
                                    self.players[current_player_int].rot_self_image_keep_size(self.players[current_player_int].heading)
                    # groups.PlayerGroup.update(self.viewscreen_rect)
                    # print groups.PlayerGroup

                # print self.players[0].x, self.players[0].y, self.players[0].rect
                # print self.players[1].x, self.players[1].y, self.players[1].rect
                # self.window.blit(self.players[self.local_player_id].image, (390, 290))
                # Lasketaan viewscreen- ja background rectit
                self.calc_viewscreen_rect()

                # Päivitetään graffat vaan joka toisessa framessa
                if self.frame_counter % 2 == 0:
                    self.update_graphics()

                # Pelilogiikan FPS target 60, eli graffoilla siis 30
                self.clock.tick(PHYSICS_FPS)

        if self.quit_game:
            self.exit()

    def update_graphics(self):
        """ Grafiikoiden päivitysmetodi """

        # Ruutu tyhjäksi
        self.window.fill(BLACK)

        # Piirretään levelin ulkopuolinen tuhoutumaton alue
        off_level_rect = pygame.Rect(self.background_view_rect[0]-WINDOW_SIZE[0]//2,
                                     self.background_view_rect[1]-WINDOW_SIZE[1]//2,
                                     self.background_view_rect[2],
                                     self.background_view_rect[3])
        self.window.blit(self.current_level.off_level_surface, off_level_rect)

        # Piirretään levelistä vain viewscreenin kokoinen alue, pelaaja keskellä
        self.window.blit(self.current_level.image, self.background_view_rect)

        # Bullettien, pelaajan, pallon piirrot
        groups.BulletGroup.draw(self.window)
        groups.BallGroup.draw(self.window)
        groups.PlayerGroup.draw(self.window)
        groups.EffectGroup.draw(self.window)
        groups.TextGroup.draw(self.window)

        # HUD
        text.show_text(self.window, (10, 70), "FPS: " + str(round(self.clock.get_fps(), 2)))
        text.show_score(self.window, (50, 10), self.score_green, team=0)
        text.show_score(self.window, (700, 10), self.score_red, team=1)
        # Ammusten cooldownien latauspalkit
        ui_components.draw_loading_bar(window=self.window,
                                       current=self.players[self.local_player_id]._cooldown_counter,
                                       total=self.players[self.local_player_id].basic_shot.cooldown,
                                       bar_width=50, bar_height=5,
                                       pos=(WINDOW_CENTER_POINT[0] - 25,
                                            WINDOW_CENTER_POINT[1] + self.players[self.local_player_id].radius + 10),
                                       color=GREEN
                                       )
        ui_components.draw_loading_bar(window=self.window,
                                       current=self.players[self.local_player_id]._cooldown_counter_special,
                                       total=self.players[self.local_player_id].special.cooldown,
                                       bar_width=50, bar_height=5,
                                       pos=(WINDOW_CENTER_POINT[0] - 25,
                                            WINDOW_CENTER_POINT[1] + self.players[self.local_player_id].radius + 17),
                                       color=RED
                                       )

        # Antialiasing!
        effect.antialiasing(self.window, graphic_quality=Settings.data['graphic_quality'])

        # Displayn update
        pygame.display.flip()

    def calc_viewscreen_rect(self):
        """ Laskee viewscreen_rectin ja background_view_rectin """
        # Viewscreen rect: viewscreen absoluuttisissa koordinaateissa
        self.viewscreen_rect = pygame.Rect((self.players[self.local_player_id].x - WINDOW_SIZE[0] // 2,
                                            self.players[self.local_player_id].y - WINDOW_SIZE[1] // 2,
                                            WINDOW_SIZE[0],
                                            WINDOW_SIZE[1]))

        # Background view rect: näytetään levelistä oikea kohta
        self.background_view_rect = pygame.Rect((WINDOW_SIZE[0] // 2 - self.players[self.local_player_id].x,
                                                 WINDOW_SIZE[1] // 2 - self.players[self.local_player_id].y,
                                                 WINDOW_SIZE[0],
                                                 WINDOW_SIZE[1]))

    def score(self, scoring_team):
        """ Tätä kutsutaan kun tulee maali """
        if scoring_team == 'red':
            self.score_red += 1
            goal_text_color = RED
            sound.force_play_sound(self.goal_red_sound)
        elif scoring_team == 'green':
            self.score_green += 1
            goal_text_color = GREEN
            sound.force_play_sound(self.goal_green_sound)
        text.DisappearingText(clock=self.clock, pos=WINDOW_CENTER_POINT, text="GOAL!!!", ms_visible=2000,
                              color=goal_text_color, font_size=120, flashes=1)

    def exit(self):
        """ Tähän voi laittaa jotain mitä tulee ennen poistumista """
        self.is_running = 0
        pygame.quit()


if __name__ == '__main__':
    # HUOM! Inittien järjestys tärkeä!
    # 1) mixerin pre-init
    # 2) pygamen init

    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=1024)
    pygame.init()
    window = pygame.display.set_mode(WINDOW_SIZE)#, pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("AUTSball")

    Settings.load()

    load_assets(window)

    game = AUTSBallGame(window)
    game.add_player(0, team='red', ship_name='Teafighter', special=bullet.Dirtball)
    game.add_player(1, team='green', ship_name='Muumi')
    game.add_player(2, team='red', ship_name='Rocket')
    game.add_player(3, team='green', ship_name='Fatship')
    game.start()

    while game.is_running:
        game.update()
