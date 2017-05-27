# -*- coding: utf8 -*-
from gloss import *
from scene import *
from ui_components_gl import *
from assets import assets
from constants import *


class SceneMainMenu(Scene):

    def __init__(self, game):
        Scene.__init__(self, game)

        self.logo_sprite = Sprite(assets['gfx/AUTSBall_Logo.png'], position=(400, 110))
        self.practice_button = Button([assets['gfx/UI_practice_button_normal.png'],
                                       assets['gfx/UI_practice_button_down.png'],
                                       assets['gfx/UI_practice_button_highlight.png']],
                                      position=(400, 280))
        self.multiplayer_button = Button([assets['gfx/UI_multiplayer_button_normal.png'],
                                          assets['gfx/UI_multiplayer_button_down.png'],
                                          assets['gfx/UI_multiplayer_button_highlight.png']],
                                         position=(400, 340))
        self.settings_button = Button([assets['gfx/UI_settings_button_normal.png'],
                                       assets['gfx/UI_settings_button_down.png'],
                                       assets['gfx/UI_settings_button_highlight.png']],
                                      position=(400, 400))
        self.quit_button = Button([assets['gfx/UI_quit_button_normal.png'],
                                   assets['gfx/UI_quit_button_down.png'],
                                   assets['gfx/UI_quit_button_highlight.png']],
                                  position=(400, 460))

        """
        Käsitellään hiiren eventit
        """
        self._game.on_mouse_up = self.handle_mouse_events
        self._game.on_mouse_motion = self.handle_mouse_events
        self._game.on_mouse_down = self.handle_mouse_events

    def update(self):
        Scene.update(self)

    def draw(self):
        Scene.draw(self)

        Gloss.fill(assets['gfx/menu_background_level.png'])
        self.logo_sprite.draw(origin=None)
        self.practice_button.draw(origin=None)
        self.multiplayer_button.draw(origin=None)
        self.settings_button.draw(origin=None)
        self.quit_button.draw(origin=None)

    def handle_mouse_events(self, event_obj):
        if 'click' in self.practice_button.handle_event(event_obj):
            self._game.active_scene = Modes.Practice
        if 'click' in self.multiplayer_button.handle_event(event_obj):
            self._game.active_scene = Modes.MultiplayerLobby
        if 'click' in self.settings_button.handle_event(event_obj):
            self._game.active_scene = Modes.SettingsMenu
        if 'click' in self.quit_button.handle_event(event_obj):
            self._game.quit()