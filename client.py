# -*- coding: utf8 -*-

import network
import json
import pygame
from pygame.locals import *

#Testauksen tässä vaiheessa clientiltä lähetetään ainostaan player_id, ja näppäimistökomennot.
#Myöhemmin lisätään clientin oma ennustava grafiikan laskenta, jota korjataan serveriltä tulevalla tiedolla.
# Eihän serveriä kiinnosta mitä client laskee? Näkisin, että serveriltä tulee koordinaatit ja nopeusvektori. Niiden pitäisi riittää clientille

network_object = network.Network()

network_object.bind_to_server('')

# Kuunnellaan serveriä ensin, että saadaan selville sen osoite
client_server_acknowledgement_message = b"I'm client"
server_address = None
while server_address is None:
    response_message = network_object.client_listen()
    if response_message is not None:
        server_address = response_message[1]
        print server_address
        # Kun server on tunnistettu, lähetetään serverille oma osoite i.e. 'joinataan'
        network_object.client_send(client_server_acknowledgement_message, server_address)


#pelaajan tiedot
#pelaajan nimeä ei varmaankaan tarvitse lähetttää joka kerta, id riittää
player_name = 'Tursa'
player_id = 1
#pelaajan komennot dictionaryyn, koska on voitava ottaa yhtäaikaa useampia komentoja vastaan
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