# -*- coding: utf8 -*-

import network
import json
from constants import *


class Server(object):

    def __init__(self):
        self._network = network.Network()
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
        self._update_interval = 20
        self._update_counter = 0

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
                        self._client_ip_id_combination[client_response[1]] = client_id
                        self._client_id_counter += 1
                        print "Added client with ip ", client_response[1]
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
            client_inputs = set()
            while self._update_counter < self._update_interval:
                # Kuunnellaan clientteja fixattu aika ja lasketaan sitten mitä tapahtuu kaikkien syötteille
                data_dict = self._network.server_listen()
                if data_dict is not None:
                    if data_dict[1] in self.client_list:
                        data_object = data_dict[0]
                        # TODO: lisää clientin input vaikuttamaan laskuihin
                        # client_inputs setissä keynä on clientin assignattu id ja valuena clientin lähettämät input tiedot
                        # tarkistetaan onko client lähettänyt jo inputit tässä syklissä
                        if self._client_ip_id_combination[data_dict[1]] not in client_inputs:
                            client_inputs[self._client_ip_id_combination[data_dict[1]]] = data_object
                            print "Got client inputs from ", data_dict[1]
                        else:
                            print 'client already sent input on this cycle'
                clock.tick(PHYSICS_FPS)
                self._update_counter += clock.get_time()

            # TODO: Lasketaan pelin kulku ja muodostetaan paketti clienteille
            #packet_to_client = json_dumps(update_information)

            # TODO: Päivitetään tiedot clienteille
            #self._network.server_send_message(packet_to_clients)

    def start_game(self):
        self._waiting_for_client_to_join = False
        self._in_game = True
        self._network.server_send_message(b'Start game')

    def shutdown(self):
        self._in_game = False
        self._network.destroy()

#player_coordinates = {'p0_x': 0,'p0_y': 0, 'p1_x': 100, 'p1_y': 100, 'p2_x': 100, 'p2_y': 100}
#packet_to_clients = json.dumps(player_coordinates)
