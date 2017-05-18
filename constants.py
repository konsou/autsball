# -*- coding: utf8 -*-
import cPickle

# Yleisiä muuttujia
WINDOW_SIZE = (800, 600)
GRAPHICS_FPS = 30
PHYSICS_FPS = 60


class Modes:
    MainMenu, SettingsMenu, Practice, MultiplayerLobby = range(4)


class Settings:

    settings_file = 'settings.pkl'
    data = {
        'music_on': True,
        'music_volume': 1.0,
        'sounds_on': True,
        'sound_volume': 1.0,
        'graphic_quality': 3
    }

    def __init__(self):
        pass

    @staticmethod
    def load():
        try:
            s_file = open(Settings.settings_file, 'rb')
            Settings.data = cPickle.load(s_file)
            s_file.close()
        except IOError:
            print 'No settings file, using default values'

    @staticmethod
    def save():
        try:
            s_file = open(Settings.settings_file, 'wb')
            cPickle.dump(Settings.data, s_file, cPickle.HIGHEST_PROTOCOL)
            s_file.close()
        except IOError:
            print 'File access denied, saving failed'
