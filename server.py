# -*- coding: utf8 -*-

from network import *
import json
from constants import *


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

        # Aloitetaan clienttien odotus
        self._waiting_for_client_to_join = True
        self._in_game = False
        # Serverin updatejen intervalli millisekunteina
        self._update_interval = 5
        self._update_counter = 0

        # Game instance
        self._game_instance = None

    def update(self, clock):
        # Lobby-vaihe
        if self._waiting_for_client_to_join:
            try:
                # Lähetetään viesti clienteille, jotta ne saa tietää serverin osoitteen
                self._network.server_send_message(b"Join me")

                # Kuunnellaan clienttien vastauksia
                client_response = self._network.server_listen()
                if client_response is not None:
                    # Lisätään client listaan
                    if client_response[0].startswith("My name is:"):
                        client_name = client_response[0].split(":")[1]
                        client_id = {"client_id": self._client_id_counter}
                        self._client_list.add(client_response[1])
                        self._client_ip_id_combination[client_response[1][0]] = self._client_id_counter
                        self._client_id_counter += 1
                        print "Added client with ip ", client_response[1][0]
                        print "Client name is %s" % client_name
                        # Lähetetään pelaajalle sen oma id
                        packet_to_client = json.dumps(client_id)
                        self._network.client_send(packet_to_client, client_response[1])
                    else:
                        print "Not valid client, he said ", client_response
            finally:
                pass
        # Pelin sisällä
        elif self._in_game:
            client_inputs = {}
            while self._update_counter < self._update_interval:
                # Kuunnellaan clientteja fixattu aika ja lasketaan sitten mitä tapahtuu kaikkien syötteille
                data_dict = self._network.server_listen()
                if data_dict is not None:
                    if data_dict[1] in self._client_list:
                        data_object = unpack_int(data_dict[0])
                        # TODO: lisää clientin input vaikuttamaan laskuihin
                        # client_inputs setissä keynä on clientin assignattu id ja valuena clientin lähettämät input tiedot
                        # tarkistetaan onko client lähettänyt jo inputit tässä syklissä
                        if self._client_ip_id_combination[data_dict[1][0]] not in client_inputs:
                            client_inputs[self._client_ip_id_combination[data_dict[1][0]]] = data_object
                            # print "Got client inputs from ", data_dict[1][0]
                            # print "Client input is ", data_object
                        #else:
                            #print 'client already sent input on this cycle'
                # clock.tick(PHYSICS_FPS)
                self._update_counter += clock.get_time()

            self._update_counter = 0

            # TODO: Lasketaan pelin kulku ja muodostetaan paketti clienteille
            for current_id in client_inputs:
                print current_id, client_inputs[current_id]
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

            self._game_instance.update()
            #packet_to_client = json_dumps(update_information)

            # TODO: Päivitetään tiedot clienteille
            #self._network.server_send_message(packet_to_clients)

    def start_game(self, game_instance):
        self._waiting_for_client_to_join = False
        self._in_game = True
        self._network.server_send_message(b'Start game')
        self._game_instance = game_instance
        self._game_instance.local_player_id = 0
        print "add players"
        i = 0
        for ip, player_id in self._client_ip_id_combination.iteritems():
            if i % 2:
                team = "green"
            else:
                team = "red"
            self._game_instance.add_player(player_id, team=team)
            print player_id
            i += 1
        self._game_instance.start()

    def shutdown(self):
        self._in_game = False
        self._network.destroy()

#player_coordinates = {'p0_x': 0,'p0_y': 0, 'p1_x': 100, 'p1_y': 100, 'p2_x': 100, 'p2_y': 100}
#packet_to_clients = json.dumps(player_coordinates)
