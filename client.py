# -*- coding: utf8 -*-

import network

network_object = network.Network()

network_object.bind_to_server('')

while True:
    data_dict = network_object.client_listen()
    if data_dict is not None:
        print(data_dict['p1'])
        print(data_dict['p2'])
