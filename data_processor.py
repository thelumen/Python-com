#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

last_rotations = None

def android_gyro(handle):
    dt = np.dtype(np.float32).newbyteorder('>')
    def wrapper(data):
        global last_rotations
        rotations = np.fromstring(data, dtype=np.uint8)
        if last_rotations is not None:
            rotations = np.concatenate((last_rotations, rotations))
        dataLen = rotations.size
        curLen = (dataLen // 12) * 12
        if dataLen > curLen:
            last_rotations = rotations[curLen :]
            rotations = rotations[0 : curLen]
        else:
            last_rotations = None

        rotations = np.array(np.frombuffer(rotations, dtype=dt), dtype=np.float32)
        rotations *= 0.02

        i = 0
        curLen = rotations.size
        while i + 3 <= curLen:
            rotation = rotations[i : i + 3]
            handle(rotation)
            i += 3
    return wrapper

def android_imu(handle):
    dt = np.dtype(np.float32).newbyteorder('>')
    def wrapper(data):
        global last_rotations
        rotations = np.fromstring(data, dtype=np.uint8)
        if last_rotations is not None:
            rotations = np.concatenate((last_rotations, rotations))
        dataLen = rotations.size
        curLen = (dataLen // 24) * 24
        if dataLen > curLen:
            last_rotations = rotations[curLen :]
            rotations = rotations[0 : curLen]
        else:
            last_rotations = None

        rotations = np.array(np.frombuffer(rotations, dtype=dt), dtype=np.float32)

        i = 0
        curLen = rotations.size
        while i + 6 <= curLen:
            rotation = rotations[i : i + 6]
            handle(rotation)
            i += 6
    return wrapper

ignore = True

def device_gyro(handle):
    dt = np.dtype(np.int16)
    def wrapper(data):
        global last_rotations, ignore
        rotations = np.fromstring(data, dtype=np.uint8)
        if last_rotations is not None:
            rotations = np.concatenate((last_rotations, rotations))
        elif ignore:
            i = 0
            dataLen = rotations.size
            while i + 3 < dataLen:
                if rotations[i] == 0xff and rotations[i + 1] == 0x8f and rotations[i + 2] == 0xff and rotations[i + 3] == 0x8f:
                    break
                i += 1
            if i + 3 < dataLen:
                rotations = rotations[i :]
                ignore = False
            else:
                return
        dataLen = rotations.size
        curLen = (dataLen // 10) * 10
        if dataLen > curLen:
            last_rotations = rotations[curLen :]
            rotations = rotations[0 : curLen]
        else:
            last_rotations = None

        rotations = np.array(np.frombuffer(rotations, dtype=dt), dtype=np.float32)
        rotations *= 0.061035156 * 0.02 / 57.29578

        i = 0
        curLen = rotations.size
        while i + 5 <= curLen:
            rotation = rotations[i + 2 : i + 5]
            handle(rotation)
            i += 5
    return wrapper

def ble_imu(handle):
    def wrapper(data):
        array = []
        for d in data:
            array.append(int(d, 16))
        handle(np.array(array, dtype='uint8'))
    return wrapper

def checksum_verify(handle):
    dt = np.dtype(np.int16)
    header = 5
    footer = 5
    def wrapper(data):
        pass
    return wrapper

def file_gyro(handle):
    dt = np.dtype(np.int16)
    def wrapper(data):
        rotation = np.array(np.frombuffer(data[6:], dtype=dt), dtype=np.float32)
        rotation *= 0.061035156 / 57.29578
        handle(rotation)
    return wrapper

def file_imu(handle):
    dt = np.dtype(np.int16)
    c1 = 0.488 * 0.0098
    c2 = 0.061035156 / 57.29578
    def wrapper(data):
        rotation = np.array(np.frombuffer(data, dtype=dt), dtype=np.float32)
        rotation[0] *= c1
        rotation[1] *= c1
        rotation[2] *= c1
        rotation[3] *= c2
        rotation[4] *= c2
        rotation[5] *= c2
        handle(rotation)
    return wrapper

def file_euler(handle):
    def wrapper(data):
        handle(data)
    return wrapper