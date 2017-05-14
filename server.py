# -*- coding: utf8 -*-

import network
import json

#Tämä dumbleiksi :)
network_object = network.Network()
#player_coordinates = {'p0_x': 0,'p0_y': 0, 'p1_x': 100, 'p1_y': 100, 'p2_x': 100, 'p2_y': 100}
#packet_to_clients = json.dumps(player_coordinates)

try:
    #paketti lähetetään kaikille clienteille
 #   network_object.server_send_message(packet_to_clients)

    # Kuunnellaan clientteja
    while True:

        data_dict = network_object.server_listen()
        if data_dict is not None:
            print(data_dict['up'])

finally:
    print('closing socket')
    network_object.destroy()
