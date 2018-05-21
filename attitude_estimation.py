#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import math
import threading
import numpy as np
from numpy.ctypeslib import ndpointer
from ctypes import *
from data_processor import *

lock = threading.Lock()

rotation_x = rotation_y = rotation_z = 0.0
location_x = location_y = location_z = 0.0

def start_thread():
    class myThread (threading.Thread):
        def run(self):
            connect()
    myThread().start()

def handle_gyro(get_attitude):
    # @device_gyro
    @android_gyro
    # @file_gyro
    def wrapper(rotation):
        global rotation_x, rotation_y, rotation_z
        # cosa = math.cos(orientation[2])
        # sina = math.sin(orientation[2])
        # cosb = math.cos(orientation[1])
        # sinb = math.sin(orientation[1])
        # mat = np.matrix([[cosa, sina, 0],[-sina*cosb, cosa*cosb, 0],[cosa*sinb, sina*sinb, -cosb]])
        # mat /= cosb
        # orientation = (mat.dot(rotation) + orientation).tolist()[0]
        rotation = get_attitude(np.ascontiguousarray(rotation))
        # print(rotation)
        if lock.acquire():
            rotation_x = rotation[0]
            rotation_y = rotation[1]
            rotation_z = rotation[2]
            lock.release()
    return wrapper

stationary = False
need_calibrate = False

def handle_imu(get_attitude, set_stationary):
    # @device_imu
    # @android_imu
    # @file_imu
    @ble_imu
    def wrapper(data):
        global rotation_x, rotation_y, rotation_z
        global location_x, location_y, location_z
        global stationary, stop, stopped, need_calibrate
        set_stationary(stationary)
        attitude = get_attitude(data)
        # print(attitude)
        if lock.acquire():
            rotation_x = attitude[0]
            rotation_y = attitude[1]
            rotation_z = attitude[2]
            location_x = attitude[3]
            location_y = attitude[4]
            location_z = attitude[5]
            lock.release()
        # print(location_x, location_y, location_z)
    return wrapper

def connect():
    lib = np.ctypeslib.load_library('attitude.so', '.')

    reset_delivery_parameter = lib.reset_delivery_parameter
    reset_delivery_parameter.argtypes = [c_int, ndpointer(dtype=np.int16, ndim=1, flags='C_CONTIGUOUS')]
    reset_delivery_parameter.restype = None
    reset_delivery_parameter(0, np.array([0, 0, 0, 4096, 4096, 4096, 0, 0, 0], dtype=np.int16))

    set_stationary = lib.set_stationary

    get_attitude = lib.get_attitude
    get_attitude.argtypes = [ndpointer(dtype=np.uint8, ndim=1, flags='C_CONTIGUOUS')]
    get_attitude.restype = ndpointer(dtype=np.float32, ndim=1, shape=(9,), flags='C_CONTIGUOUS')

    handle = handle_imu(get_attitude, set_stationary)

    # import serial_cp2102
    # serial_cp2102.recv_data(handle)
    # import rfcomm_server
    # rfcomm_server.recv_data(handle)
    # import imu_from_file
    # imu_from_file.recv_data(handle)
    import gatttool
    gatttool.recv_data(handle)

def get_rotation():
    global rotation_x, rotation_y, rotation_z
    global location_x, location_y, location_z
    if lock.acquire():
        rotation = [rotation_x, rotation_y, rotation_z, location_x, location_y, location_z]
        lock.release()
    return rotation

if __name__ == '__main__':
    start_thread()
    from time import sleep
    sleep(1000)
