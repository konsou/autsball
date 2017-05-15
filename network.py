# -*- coding: utf8 -*-

import socket
import struct
import json


class Network(object):

    def __init__(self):
        # datagram socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # timeout to the socket so it doesn't block indefinitely when trying to receive data
        self._socket.settimeout(0.2)
        # port used to communicate
        self._port = 12345
        self._server_address = ('127.0.0.1', self._port)
        # multicast group
        self._server_multicast_group = ('224.11.22.33', self._port)
        self._client_multicast_group = '224.11.22.33'
        # set time-to-live for messages
        ttl = struct.pack('b', 1)
        self._socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

#Server

    # Lähetetään viesti kaikille clienteille
    def server_send_message(self, message):
        #print('sending {!r}'.format(message))
        self._socket.sendto(message, self._server_multicast_group)

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
            print('received {} from {}'.format(data, address))
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
