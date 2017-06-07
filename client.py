# -*- coding: utf8 -*-
from network import *
import json
import pygame
from pygame.locals import *
from types import *


class Client(object):

    def __init__(self, player_name="Nemo"):
        self.network = Network()
        self._player_name = player_name
        self.network.bind_to_server('')
        self._acknowledgement_message = b"My name is:%s" % self._player_name
        self._server_address = None
        self._local_player_id = None
        self._game_started = False

    def try_to_join_server(self, clock):
        print "Trying to join server"
        response_messages = self.network.get_network_packages(NetworkMessageTypes.ServerHereIAm)
        # print "In try_to_join_server got this filtered response:"
        # print response_messages
        for current_message in response_messages:
            # print "Current message:", current_message
            self._server_address = current_message[2]
            self.network.client_send(self._acknowledgement_message, self._server_address,
                                     NetworkMessageTypes.ClientMyNameIs)
            print "Joining server ", self._server_address
            while self._local_player_id is None:
                data = self.network.get_network_packages(NetworkMessageTypes.ServerClientID)
                for current_piece_of_data in data:
                    # print "current_piece_of_data:", current_piece_of_data
                    # print "cliend ID:", current_piece_of_data[1]
                    try:
                        self._local_player_id = current_piece_of_data[1]['client_id']
                        print "Got client ID from server:", current_piece_of_data[1]['client_id']
                        # TODO: joskus jumahtaa johonkin tähän kohtaan näennäisen randomilla kun joinaa
                        return True
                    except (IndexError, TypeError):
                        # Tässä oli pass, vaihdettu return False - katsotaan auttaako yllä mainittuun jumiin
                        return False

        # elif response_message is not None:
        #     print "Noob host"
        #     return False

        clock.tick(10)

    def wait_for_server_start_game(self):
        if not self._game_started:
            response_messages = self.network.get_network_packages(NetworkMessageTypes.ServerStartGame)
            # print "Waiting for server to start game..."
            # print "Server sent:", response_message
            for current_message in response_messages:
                if current_message[2] == self._server_address:
                    self._game_started = True
                    print "Server started the game, wohoo!"
                    return True
                else:
                    return False
            else:
                return False
        else:
            return True

    def wait_for_player_data_after_start(self, game_instance):
        print "Waiting for player data..."
        # response_messages = self.network.get_network_packages(NetworkMessageTypes.ServerShipInfo)
        response_messages = self.network.get_network_packages(NetworkMessageTypes.ServerShipInfo)
        print "wait_for_player_data_after_start - response_messages:", response_messages
        for current_message in response_messages:
            print "Got this info when waiting for player data:", current_message
            if current_message[2] == self._server_address:
                print "We got ships from server! Here's the info:"
                print current_message[1]
                for player_id, info in current_message[1].iteritems():
                    print "Player ID: {}, info: {}".format(player_id, info)
                    #print "Player ID: {}, team: {}, ship_name: {}".format(player_id, info[0], info[1])
                    game_instance.add_player(int(player_id), team=info[0], ship_name=info[1])
                    print "Added ship for player ", player_id
                return True
            else:
                return False
        else:
            return False

    def send_input(self):
        player_keyboard_commands = {'player_id': self._local_player_id,
                                    'up': 0,
                                    'left': 0,
                                    'right': 0,
                                    'shoot_basic': 0,
                                    'shoot_special': 0,
                                    'recover': 0}
        keys = ['player_id', 'up', 'left', 'right', 'shoot_basic', 'shoot_special', 'recover']

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
            player_keyboard_commands['shoot_basic'] = 1
        else:
            player_keyboard_commands['shoot_basic'] = 0
        if pressed_keys[K_LCTRL] or pressed_keys[K_RCTRL]:
            player_keyboard_commands['shoot_special'] = 1
        else:
            player_keyboard_commands['shoot_special'] = 0

        if pressed_keys[pygame.K_BACKSPACE]:
            player_keyboard_commands['recover'] = 1
        else:
            player_keyboard_commands['recover'] = 0

        # pelaajan tiedot pakettiin

        player_data_packet = json.dumps(pack_client_commands(player_keyboard_commands))

        self.network.client_send(player_data_packet, self._server_address, NetworkMessageTypes.ClientUpdates)

    def get_server_updates(self):
        """
        Hakee ja palauttaa kaikki viime framen jälkeen tulleet server update -paketit
        Jos niitä ei ole yhtään niin palauttaa None
        Jos niitä on useampia niin tekee näin:
            * positiotiedot otetaan viimeisimmästä paketista
            * event-tiedot yhdistetään kaikista paketeista
        Tässä toteutuksessa on riskiä osittaisesta off-syncistä lagitilanteissa mutta ei varmaan kovin iso ongelma
        """
        server_updates_all = self.network.get_network_packages(NetworkMessageTypes.ServerUpdates)

        try:
            # Otetaan vain viimeisimmän päivityspaketin dataosuus
            server_updates = server_updates_all.pop()[1]
        except IndexError:
            server_updates = None

        # Lisätään eventsit lopuista paketeista jos niitä on
        # TODO: KAATAA PELIN, KORJAA
        if len(server_updates_all) > 0:
            print "Got more than one server update packet. Adding their events."
            for current_package in server_updates_all:
                print "current_package:", current_package
                server_updates['events'].append(current_package[1]['events'])

        return server_updates

    def _get_client_id(self):
        return self._local_player_id

    client_id = property(_get_client_id)

# Testauksen tässä vaiheessa clientiltä lähetetään ainostaan player_id, ja näppäimistökomennot.
# Myöhemmin lisätään clientin oma ennustava grafiikan laskenta, jota korjataan serveriltä tulevalla tiedolla.
# Testauksen tässä vaiheessa clientiltä lähetetään ainostaan player_id, ja näppäimistökomennot.
# Myöhemmin lisätään clientin oma ennustava grafiikan laskenta, jota korjataan serveriltä tulevalla tiedolla.
# Eihän serveriä kiinnosta mitä client laskee? Näkisin, että serveriltä tulee koordinaatit ja nopeusvektori.
# Niiden pitäisi riittää clientille


# pelaajan tiedot
# pelaajan nimeä ei varmaankaan tarvitse lähetttää joka kerta, id riittää
# pelaajan komennot dictionaryyn, koska on voitava ottaa yhtäaikaa useampia komentoja vastaan
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
