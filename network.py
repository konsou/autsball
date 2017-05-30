# -*- coding: utf8 -*-

import pygame
import socket
import struct
import json
import copy
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
        self._receive_queue = deque(maxlen=NETWORK_QUEUE_LENGTH)
        self._threading_lock = allocate_lock()
        start_new_thread(self.network_listen, ('',))

    def network_listen(self, required_because_stupid_threading_function):
        """ Tämä on tarkoitus ajaa taustathreadissa. Kuuntelee koko ajan viestejä ja tallentaa ne receive_queueen.
        Muoto: message_type, data, address """
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
                    received_data = int(data[0]), json.loads(data[1:]), address
                    # received_data = json.loads(data), address
                except ValueError:
                    received_data = int(data[0]), data[1:], address
                with self._threading_lock:
                    # print "Received:", received_data
                    self._receive_queue.append(received_data)

    def get_latest_network_package(self, waitforit=0, wait_time=1000):
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
                with self._threading_lock:
                    received_data = self._receive_queue.pop()  # Otetaan vain uusin tieto
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

    def get_all_network_packages(self, message_filter=None):
        """
        Palauttaa kopion receive_queuesta ja tyhjentää receive_queuen
        Jos message_filter on asetettu (pitää olla joku constants -> NetworkMessageTypesistä) niin palauttaa vain
        sen tyyppiset viestit
        """
        queue_copy = deque()
        # Ensin asetetaan threading-lukko, kopioidaan network queue, tyhjennetään network queue
        with self._threading_lock:
            if message_filter is not None:
                # print "in get_all_network_packages: trying to filter", message_filter
                for current_item in self._receive_queue:
                    # print "current_item:", current_item
                    if current_item[0] == message_filter:
                        queue_copy.append(current_item)
            else:
                queue_copy = copy.copy(self._receive_queue)
            self._receive_queue.clear()

        # Filtteröidään jos niin halutaan - käytännössä poistetaan itemit jotka ei ole filtterissä
        # Tämä tehty tässä kohtaa näin erikseen että minimoidaan thread-lukituksen aika
        # if message_filter is not None:
        #     for current_item in queue_copy:
        #         print "in get_all_network_packages:"
        #         print "current_item:", current_item
        #         if queue_copy[current_item][0] != message_filter:
        #             del queue_copy[current_item]
        # print "queue_copy:", queue_copy

        return queue_copy

    @staticmethod
    def filter_packages(message_queue, message_type):
        """ Käy läpi annetun pakettilistan ja palauttaa vain halutun tyyppiset paketit """
        return_queue = deque()
        for current_item in message_queue:
            print message_queue[current_item]
            return_queue.append(message_queue[current_item])
        return return_queue


# Server

    def server_send_message(self, message, message_type):
        """ Lähetetään viesti kaikille clienteille """
        message = bytes(message_type) + message
        if message_type != NetworkMessageTypes.ServerHereIAm:
            print('sending {!r}'.format(message))
        self._socket.sendto(message, self._server_multicast_group)

# Client

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

    def client_send(self, message, address, message_type):
        """  Client lähettää viestin """
        message = bytes(message_type) + message
        print ('sending {!r}'.format(message))
        self._socket.sendto(message, address)

    def destroy(self):
        self._socket.close()


def pack_client_commands(data_dict):
    """ Pakkaa pelaajan näppäinkomennot INTiksi:
    Player id - up - left - right - shoot_basic - shoot_special - recover  
    Esim: 3010101"""
    keys = ['player_id', 'up', 'left', 'right', 'shoot_basic', 'shoot_special', 'recover']
    packed_int = 0
    for n in range(7):
        packed_int += int(data_dict[keys[n]]) * 10 ** (6 - n)
    return packed_int


def unpack_client_commands(packed_int):
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
    packed_int = pack_client_commands(player_keyboard_commands)
    print packed_int
    print unpack_client_commands(packed_int)


if __name__ == '__main__':
    debug_run()