# -*- coding: utf8 -*-
from pygame import *
from gloss import *
from constants import *
from ui_components_gl import *


class MenuTest(GlossGame):

    def __init__(self, name):
        GlossGame.__init__(self, name)
        self.assets = {}

    def load_content(self):
        """
        Tässä ladataan tekstuurit openGL:n puolelle, voisi hyödyntää olemassa olevaa assets.py:n assets-dictionaryä
        sen sijaan, että tehdään se uusiksi:
            self.assets[asset_key] = Texture(assets[asset_key])
            
        Testauksen vuoksi nyt vain kopioitu pätkä asset.py:stä
        """
        included_folders = ['gfx']
        included_image_extensions = ['.png']

        for current_directory in included_folders:
            files_list = os.listdir(current_directory)
            for current_file in files_list:
                extension = current_file[-4:]
                filepath = os.path.join(current_directory, current_file)
                asset_key = current_directory + '/' + current_file
                if extension in included_image_extensions:
                    # Ladataan kuvatiedostot
                    self.assets[asset_key] = Texture(filepath)

        """
        Main menu buttonit openGL-sprite buttoneina
        """
        self.logo_sprite = Sprite(self.assets['gfx/AUTSBall_Logo.png'], position=(400, 110))
        self.practice_button = Button([self.assets['gfx/UI_practice_button_normal.png'],
                                       self.assets['gfx/UI_practice_button_down.png'],
                                       self.assets['gfx/UI_practice_button_highlight.png']],
                                      position=(400, 280))
        self.multiplayer_button = Button([self.assets['gfx/UI_multiplayer_button_normal.png'],
                                          self.assets['gfx/UI_multiplayer_button_down.png'],
                                          self.assets['gfx/UI_multiplayer_button_highlight.png']],
                                         position=(400, 340))
        self.settings_button = Button([self.assets['gfx/UI_settings_button_normal.png'],
                                       self.assets['gfx/UI_settings_button_down.png'],
                                       self.assets['gfx/UI_settings_button_highlight.png']],
                                      position=(400, 400))
        self.quit_button = Button([self.assets['gfx/UI_quit_button_normal.png'],
                                   self.assets['gfx/UI_quit_button_down.png'],
                                   self.assets['gfx/UI_quit_button_highlight.png']],
                                  position=(400, 460))

        """
        Käsitellään hiiren eventit
        """
        self.on_mouse_up = self.handle_mouse_events
        self.on_mouse_motion = self.handle_mouse_events
        self.on_mouse_down = self.handle_mouse_events

    def draw(self):
        Gloss.fill(self.assets['gfx/menu_background_level.png'])
        self.logo_sprite.draw(origin=None)
        self.practice_button.draw(origin=None)
        self.multiplayer_button.draw(origin=None)
        self.settings_button.draw(origin=None)
        self.quit_button.draw(origin=None)

    def update(self):
        pass

    def handle_mouse_events(self, event_obj):
        if 'click' in self.practice_button.handle_event(event_obj):
            print 'practice pressed'
        if 'click' in self.multiplayer_button.handle_event(event_obj):
            print 'multiplayer pressed'
        if 'click' in self.settings_button.handle_event(event_obj):
            print 'settings pressed'
        if 'click' in self.quit_button.handle_event(event_obj):
            game.quit()


game = MenuTest("Menu test OpenGL")
Gloss.screen_resolution = WINDOW_SIZE
game.run()
