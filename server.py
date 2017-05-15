# -*- coding: utf8 -*-

import network
import json

#Tämä dumbleiksi :)
network_object = network.Network()
#player_coordinates = {'p0_x': 0,'p0_y': 0, 'p1_x': 100, 'p1_y': 100, 'p2_x': 100, 'p2_y': 100}
#packet_to_clients = json.dumps(player_coordinates)

# Lista clienteista, joiden viesteistä välitetään lobby vaiheen jälkeen (ei hyväksytä pelin ulkopuolista häirintää)
client_list = set()
waiting_for_clients_to_join = True

while waiting_for_clients_to_join:
    try:
        # Lähetetään viesti clienteille, jotta ne saa tietää serverin osoitteen
        network_object.server_send_message(b"I'm the server")

        # Kuunnellaan clienttien vastauksia
        client_response = network_object.server_listen()
        if client_response is not None:
            # Lisätään client listaan
            client_list.add(client_response[1])

            # TODO: lopeta lobby-vaihe paremmin, ei ensimmäisen clientin joinattua
            waiting_for_clients_to_join = False
    finally:
        pass

try:
    #paketti lähetetään kaikille clienteille
 #   network_object.server_send_message(packet_to_clients)

    # Kuunnellaan clientteja
    while True:

        data_dict = network_object.server_listen()
        if data_dict is not None:
            if data_dict[1] in client_list:
                data_object = data_dict[0]
                print(data_object['up'])

finally:
    print('closing socket')
    network_object.destroy()
