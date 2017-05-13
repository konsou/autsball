# -*- coding: utf8 -*-

import network
import json

network_object = network.Network()

network_object.bind_to_server('')

#pelaajan tiedot
#pelaajan nimeä ei varmaankaan tarvitse lähetttää joka kerta, id riittää
player_name = 'Tursa'
player_id = 1

#pelaajan tiedot pakettiin
player_data = {'name': player_name, 'id': player_id}
player_data_packet = json.dumps(player_data)

while True:
    server_data = network_object.client_listen()
   # data_dict2 = network_object.client_send(player_name)
    if server_data is not None:
        print(server_data['p1_y'])
        #self.players[0].x = server_data['p0_x']
        #self.players[0].y = server_data['p0_x']
        #self.players[1].x = server_data['p1_x']
        #self.players[1].y = server_data['p1_x']
