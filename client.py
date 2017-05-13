# -*- coding: utf8 -*-

import network
import json

#Testauksen tässä vaiheessa clientiltä lähetetään ainostaan player_id, ja näppäimistökomennot.
#Myöhemmin lisätään clientin oma ennustava grafiikan laskenta, jota korjataan serveriltä tulevalla tiedolla.

network_object = network.Network()

network_object.bind_to_server('')

#pelaajan tiedot
#pelaajan nimeä ei varmaankaan tarvitse lähetttää joka kerta, id riittää
player_name = 'Tursa'
player_id = 1
#pelaajan komennot dictionaryyn, koska on voitava ottaa yhtäaikaa useampia komentoja vastaan
player_keyboad_commands = {'player_id': player_id,'up': 0, 'left': 0, 'right': 0, 'lshift': 0, 'lctrl': 0, 'backspace': 0}
#server_address = ('127.0.0.1', 12345)

#pelaajan tiedot pakettiin
player_data_packet = json.dumps(player_keyboard_commands)

while True:

#Näppäimistökomennot pakettiin.
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_UP]:
        player_keyboad_commands{'up':1}}
        else
        player_keyboad_commands{'up': 0}}
    if pressed_keys[K_RIGHT]:
        player_keyboad_commands{'right':1}}
        else
        player_keyboad_commands{'right': 0}}
    if pressed_keys[K_LEFT]:
        player_keyboad_commands{'left':1}}
        else
        player_keyboad_commands{'left': 0}}
    if pressed_keys[K_LSHIFT] or pressed_keys[K_RSHIFT]:
        player_keyboad_commands{'rshift':1}}
        else
        player_keyboad_commands{'rshift': 0}}
    if pressed_keys[K_LCTRL] or pressed_keys[K_RCTRL]:
        player_keyboad_commands{'rctrl':1}}
        else
        player_keyboad_commands{'rctrl': 0}}

    if pressed_keys[pygame.K_BACKSPACE]:
        player_keyboad_commands{'backspace':1}}
        else
        player_keyboad_commands{'backspace': 0}}


#Clientin paketinlähetys serverille
    data_dict2 = network_object.client_send(player_data_packet)

#Datan kuuntelu serveriltä
    server_data = network_object.client_listen()
    if server_data is not None:
        #tähän kiva looppi, joka käy päivittämässä kaikkien pelaajien koordinaatit clientin näytölle (dumpleja tännekkin, kun ovat niin hyviä)

       # print(server_data['p1_y'])
        # self.players[0].x = server_data['p0_x']
        # self.players[0].y = server_data['p0_x']
        # self.players[1].x = server_data['p1_x']
        # self.players[1].y = server_data['p1_x']