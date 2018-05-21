#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from numpy.ctypeslib import load_library, ndpointer
from ctypes import *

class Processor:
    def __init__(self):
        lib = load_library('attitude.so', '.')
        lib.init_system()
        self.reset_delivery_parameter = lib.reset_delivery_parameter
        self.reset_delivery_parameter.argtypes = [c_int, ndpointer(dtype='i2', ndim=1, flags='C_CONTIGUOUS')]
        self.reset_delivery_parameter.restype = None
        self.get_data_result = lib.get_data_result
        self.get_data_result.argtypes = [ndpointer(dtype='i1', ndim=1, flags='C_CONTIGUOUS')]
        self.get_data_result.restype = POINTER(c_float)
        self.get_fake_data_result = lib.get_fake_data_result
        self.get_fake_data_result.argtypes = None
        self.get_fake_data_result.restype = None
        self.get_diagnose_space = lib. get_diagnose_space
        self.get_diagnose_space.argtypes = [POINTER(POINTER(c_int))]
        self.get_diagnose_space.restype = POINTER(c_float)
        self.get_diagnose_time = lib.get_diagnose_time
        self.get_diagnose_time.argtypes = [POINTER(POINTER(c_int)), c_longlong]
        self.get_diagnose_time.restype = POINTER(c_int)
        self.get_diagnose_zero = lib.get_diagnose_zero
        self.get_diagnose_zero.argtypes = [POINTER(POINTER(c_int))]
        self.get_diagnose_zero.restype = POINTER(c_int)
        self.get_diagnose_phase = lib.get_diagnose_phase
        self.get_diagnose_phase.argtypes = [POINTER(c_int), POINTER(c_int)]
        self.get_diagnose_phase.restype = POINTER(c_int)
        self.free_result = lib.free_result
        self.free_result.argtypes = [POINTER(c_int)]
        self.free_result.restype = None
        self.get_detail = lib.get_detail
        self.get_detail.argtypes = None
        self.get_detail.restype = c_void_p
        self.detail_trajectory = lib.detail_trajectory
        self.detail_trajectory.argtypes = [POINTER(POINTER(c_int)), c_void_p]
        self.detail_trajectory.restype = POINTER(c_float)
        self.detail_center = lib.detail_center
        self.detail_center.argtypes = [POINTER(POINTER(c_int)), c_void_p]
        self.detail_center.restype = POINTER(c_float)
        self.next_detail = lib.next_detail
        self.next_detail.argtypes = [c_void_p]
        self.next_detail.restype = c_void_p

        self.interpolate_foot = lib.interpolate_foot
        self.interpolate_foot.argtypes = [ndpointer(dtype='f4', ndim=1, flags='C_CONTIGUOUS'), ndpointer(dtype='f4', ndim=1, flags='C_CONTIGUOUS')]
        self.interpolate_foot.restype = None
