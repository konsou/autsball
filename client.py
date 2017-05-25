# -*- coding: utf8 -*-

import network
import json
import pygame
from pygame.locals import *


class Client(object):

    def __init__(self, player_name="Nemo"):
        self._network = network.Network()
        self._player_name = player_name
        self._network.bind_to_server('')
        self._acknowledgement_message = b"My name is:%s" % self._player_name
        self._server_address = None
        self._local_player_id = None

    def try_to_join_server(self, clock):
        response_message = self._network.client_listen()
        if response_message is not None and response_message[0] == 'Join me':
            self._server_address = response_message[1]
            self._network.client_send(self._acknowledgement_message, self._server_address)
            print "Joining server ", self._server_address
            while self._local_player_id is None:
                data = self._network.client_listen()
                if data is not None:
                    if data[0]['client_id'] is not None:
                        self._local_player_id = data[0]['client_id']
                        return True
                    else:
                        print data[0]
        elif response_message is not None:
            print response_message[0]
            print "Not valid server"
            return False

        clock.tick(10)

#Testauksen tässä vaiheessa clientiltä lähetetään ainostaan player_id, ja näppäimistökomennot.
#Myöhemmin lisätään clientin oma ennustava grafiikan laskenta, jota korjataan serveriltä tulevalla tiedolla.
# Testauksen tässä vaiheessa clientiltä lähetetään ainostaan player_id, ja näppäimistökomennot.
# Myöhemmin lisätään clientin oma ennustava grafiikan laskenta, jota korjataan serveriltä tulevalla tiedolla.
# Eihän serveriä kiinnosta mitä client laskee? Näkisin, että serveriltä tulee koordinaatit ja nopeusvektori. Niiden pitäisi riittää clientille


#pelaajan tiedot
#pelaajan nimeä ei varmaankaan tarvitse lähetttää joka kerta, id riittää
#pelaajan komennot dictionaryyn, koska on voitava ottaa yhtäaikaa useampia komentoja vastaan
"""

# TODO: Lähetä vain komentojen muutokset (keyup/keydown) liikenteen vähentämiseksi
player_keyboard_commands = {'player_id': player_id,
                            'up': 0,
                            'left': 0,
                            'right': 0,
                            'lshift': 0,
                            'lctrl': 0,
                            'backspace': 0}

#server_address = ('127.0.0.1', 12345)

#pelaajan tiedot pakettiin
player_data_packet = json.dumps(player_keyboard_commands)

pygame.init()

while True:

#Näppäimistökomennot pakettiin.
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_UP]:
        player_keyboard_commands['up'] = 1
    else:
        player_keyboard_commands['up'] = 0
    if pressed_keys[K_RIGHT]:
        player_keyboard_commands['right'] = 1
    else:
        player_keyboard_commands['right'] = 0
    if pressed_keys[K_LEFT]:
        player_keyboard_commands['left'] = 1
    else:
        player_keyboard_commands['left'] = 0
    if pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]:
        player_keyboard_commands['rshift'] = 1
    else:
        player_keyboard_commands['rshift'] = 0
    if pressed_keys[K_LCTRL] or pressed_keys[K_RCTRL]:
        player_keyboard_commands['rctrl'] = 1
    else:
        player_keyboard_commands['rctrl'] = 0

    if pressed_keys[pygame.K_BACKSPACE]:
        player_keyboard_commands['backspace'] = 1
    else:
        player_keyboard_commands['backspace'] = 0

    # pelaajan tiedot pakettiin
    player_data_packet = json.dumps(player_keyboard_commands)

#Clientin paketinlähetys serverille
    # TODO: Lähetä vain tarvittaessa
    data_dict2 = network_object.client_send(player_data_packet, server_address)

#Datan kuuntelu serveriltä
   # server_data = network_object.client_listen()
   # if server_data is not None:

        #tähän kiva looppi, joka käy päivittämässä kaikkien pelaajien koordinaatit clientin näytölle (dumpleja tännekkin, kun ovat niin hyviä)

#        print(server_data['p1_y'])
        # self.players[0].x = server_data['p0_x']
        # self.players[0].y = server_data['p0_x']
        # self.players[1].x = server_data['p1_x']
        # self.players[1].y = server_data['p1_x']

"""