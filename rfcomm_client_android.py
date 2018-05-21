#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bluetooth import *

def recv_data(handle):
    nearby_devices = discover_devices(lookup_names=True)
    print("found %d devices" % len(nearby_devices))

    for addr, name in nearby_devices:
        print("  %s - %s" % (addr, name))

    addr = '1C:CD:E5:8C:05:88'

    # search for the SampleServer service
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    service_matches = find_service(uuid=uuid, address=addr)

    if len(service_matches) == 0:
        print("couldn't find the SampleServer service")
        sys.exit(0)

    first_match = service_matches[0]
    port = first_match["port"]
    name = first_match["name"]
    host = first_match["host"]

    print("connecting to \"%s\" on %s" % (name, host))

    # Create the client socket
    sock=BluetoothSocket(RFCOMM)
    sock.connect((host, port))

    print("connected. type stuff")
    while True:
        data = sock.recv(1024)
        if len(data) == 0: break
        handle(data)

    sock.close()

last = None

if __name__ == '__main__':
    import numpy as np
    f = open('data/out.dat', 'wb')
    def handle(data):
        global last
        f.write(data)
        data = np.fromstring(data, dtype=np.uint8)
        for c in data:
            if last is not None and last != c - 1 and (last != 0xff or c != 0x00):
                print('*********error*********', last, c)
                break
            last = c
    recv_data(handle)
    f.close()
