# -*- coding: utf8 -*-

from network import *
import json
from constants import *
import time


class Server(object):

    def __init__(self):
        self._network = Network()
        # Lista clienteista, joiden viesteistä välitetään
        self._client_list = set()
        self._client_ip_id_combination = {}
        self._client_id_counter = 0

        # lisää serveri client listaan
        server_local_ip = '127.0.0.1'
        self._client_list.add(server_local_ip)
        self._client_ip_id_combination[server_local_ip] = self._client_id_counter
        self._client_id_counter += 1
        print "Server created, local client joined"
        print "client_ip_id_combination:", self._client_ip_id_combination

        # Aloitetaan clienttien odotus
        self._waiting_for_client_to_join = True
        self._in_game = False
        # Serverin updatejen intervalli millisekunteina
        self._update_interval = 20
        self._update_counter = 0

        # Game instance
        self._game_instance = None

    def update(self):
        # Lobby-vaihe
        if self._waiting_for_client_to_join:
            try:
                # Lähetetään viesti clienteille, jotta ne saa tietää serverin osoitteen
                self._network.server_send_message(b"Join me", message_type=NetworkMessageTypes.ServerHereIAm)

                # Kuunnellaan clienttien vastauksia
                client_responses = self._network.get_network_packages(NetworkMessageTypes.ClientMyNameIs)
                for current_message in client_responses:
                    print "Client response:", current_message
                    # Lisätään client listaan
                    client_name = current_message[1].split(":")[1]
                    client_id = {"client_id": self._client_id_counter}
                    self._client_list.add(current_message[2])
                    self._client_ip_id_combination[current_message[2][0]] = self._client_id_counter
                    self._client_id_counter += 1
                    print "Added client with ip ", current_message[2][0]
                    print "Client name is %s" % client_name
                    # print "client_ip_id_combination:", self._client_ip_id_combination
                    # HUOMIO: Kun testaa omalla koneella ilman nettiyhteyttä ja koneella ei ole muita
                    # IP-osoitteita kuin 127.0.0.1 niin clientti overrideaa serverin local clientin ja peli
                    # kaatuu kun se käynnistetään

                    # Lähetetään pelaajalle sen oma id
                    packet_to_client = json.dumps(client_id)
                    self._network.client_send(packet_to_client, current_message[2],
                                              NetworkMessageTypes.ServerClientID)
            finally:
                pass

        # Pelin sisällä
        elif self._in_game:
            client_inputs = {}
            try:
                data_dict = self._network.get_network_packages(NetworkMessageTypes.ClientUpdates)[0]
            except IndexError:
                data_dict = None
            if data_dict is not None:
                # print data_dict
                if data_dict[2] in self._client_list:
                    data_object = unpack_client_commands(data_dict[1])
                    # client_inputs dictissä keynä on clientin assignattu id ja valuena clientin lähettämät input tiedot
                    # tarkistetaan onko client lähettänyt jo inputit tässä syklissä
                    if self._client_ip_id_combination[data_dict[2][0]] not in client_inputs:
                        client_inputs[self._client_ip_id_combination[data_dict[2][0]]] = data_object
                        # print "Got client inputs from ", data_dict[1][0]
                        # print "Client input is ", data_object
                    #else:
                        #print 'client already sent input on this cycle'
                # clock.tick(PHYSICS_FPS)
                # self._update_counter += clock.get_time()

            # self._update_counter = 0

            self._game_instance.update()

            # TODO: Lasketaan pelin kulku ja muodostetaan paketti clienteille
            for current_id in client_inputs:
                #print current_id, client_inputs[current_id]
                if client_inputs[current_id]['up']:
                    self._game_instance.players[current_id].accelerate()
                else:
                    self._game_instance.players[current_id].stop_acceleration()
                if client_inputs[current_id]['right']:
                    self._game_instance.players[current_id].rotate_right()
                if client_inputs[current_id]['left']:
                    self._game_instance.players[current_id].rotate_left()
                if client_inputs[current_id]['shoot_basic']:
                    self._game_instance.players[current_id].shoot()
                if client_inputs[current_id]['shoot_special']:
                    self._game_instance.players[current_id].shoot_special()
                if client_inputs[current_id]['recover']:
                    self._game_instance.players[current_id].recover()

            # TODO: Päivitetään tiedot clienteille
            update_information = {}
            update_information['players'] = {}
            update_information['ball'] = {}
            update_information['events'] = self._game_instance.get_events()
            for player_id in self._game_instance.players:
                update_information['players'][player_id] = {}
                update_information['players'][player_id]['x'] = self._game_instance.players[player_id].x
                update_information['players'][player_id]['y'] = self._game_instance.players[player_id].y
                update_information['players'][player_id]['heading'] = self._game_instance.players[player_id].heading
                update_information['players'][player_id]['thrust'] = self._game_instance.players[player_id].thrust
            update_information['ball']['pos'] = self._game_instance.ball.x, self._game_instance.ball.y

            self._game_instance.clear_events()

            packet_to_client = json.dumps(update_information)
            #print packet_to_client
            self._network.server_send_message(packet_to_client, NetworkMessageTypes.ServerUpdates)
            # clock.tick(120)
            # clock.tick(PHYSICS_FPS)

    def start_game(self, game_instance, clock):
        self._waiting_for_client_to_join = False
        self._in_game = True
        self._network.server_send_message(b'Start game', NetworkMessageTypes.ServerStartGame)
        self._game_instance = game_instance
        self._game_instance.local_player_id = 0
        i = 0
        print "Starting game..."
        print "client_ip_id_combination:", self._client_ip_id_combination

        for ip, player_id in self._client_ip_id_combination.iteritems():
            if i % 2:
                team = "green"
            else:
                team = "red"
            print "Adding player {} {}".format(player_id, team)
            self._game_instance.add_player(player_id, team=team)
            i += 1
        clock.tick(2)

        # Kerro clienteille pelaajista ja aluksista
        player_infos = {}
        for index, player in self._game_instance.players.iteritems():
            player_infos[player.owning_player_id] = (player.team, player.ship_name)
        player_package = json.dumps(player_infos)
        print "player_package:", player_package
        self._network.server_send_message(player_package, NetworkMessageTypes.ServerShipInfo)
        clock.tick(1)

        # Aloita peli
        self._game_instance.start(server_object=self)

    def shutdown(self):
        self._in_game = False
        self._network.destroy()

#player_coordinates = {'p0_x': 0,'p0_y': 0, 'p1_x': 100, 'p1_y': 100, 'p2_x': 100, 'p2_y': 100}
#packet_to_clients = json.dumps(player_coordinates)
