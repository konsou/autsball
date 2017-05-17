# -*- coding: utf8 -*-
import cPickle


class Settings:

    def __init__(self):
        self.settings_file = 'settings.pkl'
        self.data = {
            'music_on': True,
            'music_volume': 1.0,
            'sounds_on': True,
            'sound_volume': 1.0,
            'graphic_quality': 3
        }

    def load(self):
        try:
            s_file = open(self.settings_file, 'rb')
            self.data = cPickle.load(s_file)
            s_file.close()
        except IOError:
            print 'No settings file, using default values'

    def save(self):
        try:
            s_file = open(self.settings_file, 'wb')
            cPickle.dump(self.data, s_file, cPickle.HIGHEST_PROTOCOL)
            s_file.close()
        except IOError:
            print 'File access denied, saving failed'
