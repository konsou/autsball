# -*- coding: utf8 -*-

import network
import json

network_object = network.Network()
test_dict = {'p1': (0, 0), 'p2': (100, 100)}
dict_json = json.dumps(test_dict)

try:
    #message = b'olettekos kuulolla?'

    #network_object.server_send_message(message)
    network_object.server_send_message(dict_json)

    # Listen for responses
    while True:
        #print('waiting for answers')
        network_object.server_listen()

finally:
    print('closing socket')
    network_object.destroy()
