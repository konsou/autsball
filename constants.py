# -*- coding: utf8 -*-
import cPickle

# Yleisiä muuttujia
WINDOW_SIZE = (800, 600)
WINDOW_CENTER_POINT = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
GRAPHICS_FPS = 30
PHYSICS_FPS = 60
NETWORK_QUEUE_LENGTH = 30


# because...
class Modes:
    MainMenu, SettingsMenu, Practice, PlayerMenu,  MultiplayerLobby, ReadyLobby, MultiplayerGame = range(7)

# pattern has already formed, why change?
class NetworkMessageTypes:
    """ Näiden maksimimäärä nykyisellä toteutuksella 9 """
    (ServerHereIAm, ServerClientID, ServerStartGame, ServerShipInfo, ServerUpdates,
     ClientMyNameIs, ClientReady, ClientUpdates) = range(8)

class GameEventTypes:
    ShootBasic, ShootSpecial, Goal, PaintLevel, AttachBall, DetachBall = range(6)


class Settings:
    settings_file = 'settings.pkl'
    data = {
        'music_on': True,
        'music_volume': 1.0,
        'sounds_on': True,
        'sound_volume': 1.0,
        'ship_selection': 1,
        'graphic_quality': 1
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
