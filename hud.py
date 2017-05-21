# -*- coding: utf8 -*-
import pygame
import groups
import math
import game_object
import assets
from pygame.locals import *
from colors import *
from constants import *
# from assets import assets, assets_rot
""" 
Sisältää juttuja, jotka pelissä näyttää pelitilanteen infoa kuten:
    -maalinumerot
    -cooldown-counterit
    -pallonsuuntamarkkeri
    -yms. 
"""


class BallDirectionMarker(pygame.sprite.Sprite):
    """ En ole ihan varma kuuluuko tämä tänne, text.py:hyn, vai pitäisikö tehdä oma file info-jutuille """
    def __init__(self, local_player=None, ball=None):
        pygame.sprite.Sprite.__init__(self, groups.TextGroup)
        self.image_file = 'gfx/arrow_blue_32.png'
        self.image = assets.assets[self.image_file]
        self.rect = self.image.get_rect()
        self.player = local_player
        self.ball = ball

    def update(self):
        if self.player.attached_ball is None:
            ball_angle_rad = game_object.get_angle_in_radians(self.ball.rect.center, self.player.rect.center)
            ball_angle_deg = game_object.rad2deg_custom(ball_angle_rad)
            self.image = assets.assets_rot[self.image_file][ball_angle_deg]
            # Jos etäisyys palloon on yli 100 niin näytetään 100 pikselin päässä
            if self.player.distance_squared(self.ball) >= 10000:
                vx = int(100 * math.cos(ball_angle_rad))
                vy = int(100 * math.sin(ball_angle_rad))
                self.rect.center = (WINDOW_SIZE[0] // 2 + vx, WINDOW_SIZE[1] // 2 + vy)
            # Jos etäisyys palloon on alle 100 niin näytetään marker pallon päällä
            else:
                self.rect.center = self.ball.rect.center
        else:
            self.rect.center = (-100, -100)


def draw_loading_bar(window, current, total, bar_width=400, bar_height=30, pos=(200, 335), color=BLACK):
    """
    Piirtää ruudulle latauspalkin.
    window - pygamen ruutuobjekti
    current - ladattavan jutun nykyinen arvo
    total - ladattavan jutun täysi arvo
    bar_width - latauspalkin leveys kun lataus on valmis
    bar_height - latauspalkin korkeus 
    pos - positio
    color - väri  
    """
    # TODO: muuta tämäkin classiksi
    current = float(current)  # vaatii tämän ettei tee integer divisionia
    width = int(current / total * bar_width)  # lasketaan loading barin leveys
    height = bar_height
    loading_bar_surface = pygame.Surface((width, height))
    loading_bar_surface.fill(color)
    blitrect = window.blit(loading_bar_surface, pos)
    pygame.display.update(blitrect)  # päivitetään vain se osa ruudusta mitä tarvii


num_images = {}
last_scores = [0, 0]
last_score_images = [None, None]


def init_scores():
    global last_score_images
    for i in range(0, 10):
        num_images[i] = assets.assets['gfx/num_%d.png' % i]
    last_score_images = [num_images[0], num_images[0]]


def show_score(win, pos, score, team):
    # Tämä voisi olla parempi omana objektinaan, joka kuuluu HudGroupiin niin ei tarvitsisi erikseen kutsua
    if score != last_scores[team]:
        last_scores[team] = score
        score_numbers = map(int, str(score))
        score_image = pygame.Surface((len(score_numbers)*32, 64), pygame.HWSURFACE)
        score_image.set_colorkey(BLACK)
        i = 0
        for number in score_numbers:
            score_image.blit(num_images[number], (i*32, 0))
            i += 1
        last_score_images[team] = score_image
        win.blit(score_image, pos)
    else:
        win.blit(last_score_images[team], pos)
