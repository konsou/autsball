from distutils.core import setup
setup(name='AUTSBall',
      version='0.1',
      py_modules=['ball', 'bullet', 'colors', 'constants', 'effect', 'game', 'game_object', 'groups',
                  'level', 'menu', 'menu_background_action', 'music', 'player', 'text', 'vector'],
      requires=['pygame', 'tinytag']
      )
