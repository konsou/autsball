# -*- coding: utf8 -*-

import pygame
import socket
import struct
import json
from thread import *
from collections import deque
from constants import *


class Network(object):

    def __init__(self):
        # datagram socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # timeout to the socket so it doesn't block indefinitely when trying to receive data
        self._socket.settimeout(0.02)
        # port used to communicate
        self._port = 12345
        self._server_address = ('127.0.0.1', self._port)
        # multicast group
        self._server_multicast_group = ('224.11.22.33', self._port)
        self._client_multicast_group = '224.11.22.33'
        # set time-to-live for messages
        ttl = struct.pack('b', 1)
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        self.network_listening = 1
        self.receive_queue = deque(maxlen=NETWORK_QUEUE_LENGTH)
        start_new_thread(self.network_listen, ('',))

#Server

    # Lähetetään viesti kaikille clienteille
    def server_send_message(self, message):
        #print('sending {!r}'.format(message))
        self._socket.sendto(message, self._server_multicast_group)

    def network_listen(self, required_because_stupid_threading_function):
        """ Tämä on tarkoitus ajaa taustathreadissa. Kuuntelee koko ajan viestejä. """
        print "Network listen thread started."
        while self.network_listening:
            try:
                data, address = self._socket.recvfrom(1024)
            except socket.timeout:
                pass
                # print "Socket timeout when listening. Ignoring."
            else:
                # print('received {} from {}'.format(data, address))
                try:
                    received_data = json.loads(data), address
                except ValueError:
                    received_data = data, address
                self.receive_queue.append(received_data)

    def get_latest_network_package(self, waitforit=1, wait_time=1000):
        """ 
        Hakee verkkojonosta uusimman vastaanotetun viestin. Jos ei ole viestejä ja waitforit==1 niin yrittää uudelleen
        kunnes on kulunut wait_timen verran millisekunteja.
        """
        # print "Trying to get latest network package."
        # print "waitforit={}, wait_time={}".format(waitforit, wait_time)
        try_to_receive = 1
        received_data = None

        if waitforit:
            start_time = pygame.time.get_ticks()
            # print "Start time:", start_time

        while try_to_receive:
            try:
                received_data = self.receive_queue.pop()  # Otetaan vain uusin tieto
                try_to_receive = 0
            except IndexError:
                if waitforit and pygame.time.get_ticks() - start_time < wait_time:
                    # Jos vielä on odotusaikaa jäljellä niin odotetaan vähän ja katsotaan uusiksi
                    pygame.time.wait(5)
                else:
                    # Jos odotusaika on ohi niin poistutaan loopista
                    try_to_receive = 0
        # print "Received data:", received_data
        return received_data

    def get_all_network_packages(self):
        return self.receive_queue

    # server kuuntelee client viestiä
    # palauttaa vastaanotetun datan ja clientin osoitteen
    def server_listen(self):
        try:
            data, client = self._socket.recvfrom(1024)
        except socket.timeout:
            #print('socket timed out')
            #pass
            return None
        else:
            #print('received {!r} from {}'.format(data, client))
            try:
                recv_dict = json.loads(data)
            except ValueError:
                recv_dict = data

            return recv_dict, client

#Client

    # bindaus serveriin
    def bind_to_server(self, server_ip):
        self._server_address = (server_ip, self._port)
        self._socket.bind(self._server_address)

        # tell the OS to add the socket to the multicast group on all interfaces
        group = socket.inet_aton(self._client_multicast_group)
        mreq = struct.pack('4sl', group, socket.INADDR_ANY)
        self._socket.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            mreq)

    # client listens for server messages
    # Palauttaa datan ja osoitteen josta tuli (server)
    def client_listen(self):
        try:
            data, address = self._socket.recvfrom(1024)
        except socket.timeout:
            return None
        else:
            #print('received {} from {}'.format(data, address))
            try:
                recv_dict = json.loads(data)
            except ValueError:
                recv_dict = data

            return recv_dict, address

    #Client lähettää viestin
    def client_send(self, message, address):
        #print ('sending {!r}'.format(message))
        self._socket.sendto(message, address)

    def destroy(self):
        self._socket.close()


def pack_dict(data_dict):
    """ Pakkaa pelaajan näppäinkomennot INTiksi:
    Player id - up - left - right - shoot_basic - shoot_special - recover  
    Esim: 3010101"""
    keys = ['player_id', 'up', 'left', 'right', 'shoot_basic', 'shoot_special', 'recover']
    packed_int = 0
    for n in range(7):
        packed_int += int(data_dict[keys[n]]) * 10 ** (6 - n)
    return packed_int


def unpack_int(packed_int):
    """ Unpackaa pakatun intin takaisin dictiksi """
    keys = ['player_id', 'up', 'left', 'right', 'shoot_basic', 'shoot_special', 'recover']
    data_dict = {}
    for n in range(7):
        current_value = packed_int / 10 ** (6 - n)
        data_dict[keys[n]] = current_value
        packed_int -= current_value * 10 ** (6 - n)
    return data_dict


def debug_run():
    print "Packer test:"
    player_keyboard_commands = {'player_id': 3,
                                'up': 1,
                                'left': 1,
                                'right': 1,
                                'shoot_basic': 1,
                                'shoot_special': 0,
                                'recover': 1}
    print player_keyboard_commands
    packed_int = pack_dict(player_keyboard_commands)
    print packed_int
    print unpack_int(packed_int)


if __name__ == '__main__':
    debug_run()