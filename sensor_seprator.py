#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def remove_audio():
    inf = open("/home/longzhou/Sublime/data/out.dat", "rb")
    outf = open("data/out_right.dat", "wb")
    while True:
        da = inf.read(508)
        if len(da) == 0:
            break
        outf.write("\xff\xff\xff\xff")
        outf.write(da[404:])
    inf.close()
    outf.close()


def data_seprate():
    f = open('/home/longzhou/Data/chaoyangxiyuan/2017-12-26/1514266857_right.dat', 'rb')
    out = [open('data/out.pcm', 'wb'), open('data/out.prs', 'wb'), open('data/out.imu', 'wb')]
    mode = 0
    limit = [8, 408, 448, 508]
    index = 4
    while True:
        data = f.read(1024 * 4)
        length = len(data)
        if length == 0:
            break
        while length > 0:
            cur_limit = limit[mode]
            if index + length < cur_limit:
                if mode > 0:
                    out[mode - 1].write(data)
                index += length
                length = 0
            else:
                if mode > 0:
                    out[mode - 1].write(data[: cur_limit - index])
                data = data[cur_limit - index:]
                length -= cur_limit - index
                mode += 1
                if mode == 4:
                    mode = 0
                    index = 0
                else:
                    index = cur_limit
    f.close()
    for o in out:
        o.close()


if __name__ == '__main__':
    data_seprate()
