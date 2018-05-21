#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bluetooth import *

def recv_data(handle):
    server_sock=BluetoothSocket(RFCOMM)
    server_sock.bind(("", PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    advertise_service(server_sock, "SampleServer",
                        service_id=uuid,
                        service_classes=[uuid, SERIAL_PORT_CLASS],
                        profiles=[SERIAL_PORT_PROFILE]
                        )
    print("Waiting for connection on RFCOMM channel %d" % port)
    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)

    try:
        while True:
            data = client_sock.recv(1024)
            if len(data) == 0: break
            handle(data)
    except IOError:
        pass
    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("all done")

if __name__ == '__main__':
    def handle(data):
        print("received [%s]" % data)
    recv_data(handle)
