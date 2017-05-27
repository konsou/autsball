# -*- coding: utf8 -*-
from gloss import *


class Scene(object):

    def __init__(self, game):
        self._game = game
        pass

    def update(self):
        pass

    def draw(self):
        # tyhjennetään ruutu joka framessa
        Gloss.clear(Color.BLACK)
