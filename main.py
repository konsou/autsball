# -*- coding: utf8 -*-
from pygame import *
from gloss import *
from constants import *
from scene_main_menu import SceneMainMenu
from scene_practice import ScenePractice
from assets import assets, load_assets


class AutsballMain(GlossGame):

    """
    When you call run(), Gloss calls your methods in the following order:
        - preload_content()
        - draw_loading_screen()
        - load_content()
    """

    def __init__(self, game_name):
        """
        This creates your new Gloss game, setting up some basic values. Note that you must provide the name of your
        game here
        :param game_name: Pelin nimi
        """
        GlossGame.__init__(self, game_name)

        # Dictionary sceneistä, joita vaihdellaan (scenen_numero: Scene)
        self._scenes = {}
        self._active_scene = 0

    def preload_content(self):
        """
        This is an empty stub method that you can override yourself if you want to load any game data before
        draw_loading_screen() is called
        """
        pass

    def draw_loading_screen(self):
        """
        This is an empty stub method that you can override yourself if you want to show a message as soon as the game
        starts and before load_content() is called. Unlike the normal draw() method, draw_loading_screen() is called
        only once
        """
        pass

    def load_content(self):
        """
        This is an empty stub method that you should override yourself to load all your game assets.
        This gets called after preload_content() and draw_loading_screen() because your game may take some time to load
        """

        # Ladataan assetit
        load_assets()

        # Luodaan scenepohjat
        self._scenes[Modes.MainMenu] = SceneMainMenu(self)
        self._scenes[Modes.Practice] = ScenePractice(self)

    def draw(self):
        """
        Piirretään aktiivisen skenen sisältö
        """
        self._scenes[self._active_scene].draw()

    def update(self):
        """
        Päivitetään aktiivisen skenen sisältö
        Gloss rajoittaa fps:n 60:een automaattisesti
        """
        self._scenes[self._active_scene].update()

    # Property getter
    def _get_active_scene(self):
        return self._active_scene

    # Property setter
    def _set_active_scene(self, value):
        if value in self._scenes:
            self._active_scene = value
            # TODO: Ehkä jokin transitioefekti tähän?
        else:
            print("Invalid scene number!")

    active_scene = property(_get_active_scene, _set_active_scene)


if __name__ == '__main__':
    game = AutsballMain("AUTSBALL OpenGL")
    Gloss.screen_resolution = WINDOW_SIZE
    game.run()
