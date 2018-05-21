#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import multiprocessing as mp
import urllib.request
import os
import math
import time

class TiandituDownloader:
    def __init__(self):
        self.lon_left = 111.36
        self.lat_top = 29.441
        self.lon_right = 111.531
        self.lat_bottom = 29.27
        self.zoom_min = 15
        self.zoom_max = 18
        self.tile_size = 256
        self.base_dir = 'addresses/%d/'
        # self.base_url = 'http://t%d.tianditu.com/img_c/wmts?Service=WMTS&Request=GetTile&Version=1.0.0&Style=default&TileMatrixSet=c&Layer=img&TileMatrix=%d&tileRow=%d&TileCol=%d&format=tiles'
        # self.base_url = 'http://www.dzmap.cn/OneMapServer/rest/services/img_service/MapServer/WMTS?Service=WMTS&Request=GetTile&Version=1.0.0&Style=default&TileMatrixSet=c&Layer=img_service&TileMatrix=%d&tileRow=%d&TileCol=%d&format=tiles'
        self.base_url = 'http://www.dzmap.cn/OneMapServer/rest/services/img_ant/MapServer/WMTS?Service=WMTS&Request=GetTile&Version=1.0.0&Style=default&TileMatrixSet=c&Layer=img_ant&TileMatrix=%d&tileRow=%d&TileCol=%d&format=tiles'

    def getXY_mercator(self, lon, lat, zoom):
        numTiles = 1 << zoom
        point_x = math.floor((180.0 + lon) / 360.0 * numTiles)
        sin_y = math.sin(lat * (math.pi / 180.0))
        point_y = math.floor((0.5 - 0.5 * math.log((1 + sin_y) / (1 - sin_y)) / (math.pi * 2)) * numTiles)
        return point_x, point_y

    def getXY_equirectangular(self, lon, lat, zoom):
        numTiles = 1 << zoom
        point_x = math.floor((180.0 + lon) / 360.0 * numTiles)
        point_y = math.floor((90.0 - lat) / 360.0 * numTiles)
        return point_x, point_y

if __name__ == '__main__':
    tile = TiandituDownloader()
    total = 0
    for z in range(tile.zoom_min, tile.zoom_max):
        x_left, y_top = tile.getXY_equirectangular(tile.lon_left, tile.lat_top, z)
        x_right, y_bottom = tile.getXY_equirectangular(tile.lon_right, tile.lat_bottom, z)
        cur_dir = tile.base_dir % z
        if not os.path.exists(cur_dir):
            os.makedirs(cur_dir)
        print('zoom: %d' % z)
        print('(%d, %d) - (%d, %d)' % (x_left, y_top, x_right, y_bottom))
        for x in range(x_left, x_right + 1):
            for y in range(y_top, y_bottom + 1):
                cur_tile = cur_dir + ('%d%d.jpg' % (x, y))
                url = tile.base_url % (z - 1, y, x)
                urllib.request.urlretrieve(url, cur_tile)
                print('(%d, %d)' % (x, y), end='\r')
                total += 1
                if total % 100 == 0:
                    if total % 1000 == 0:
                        time.sleep(60)
                    else:
                        time.sleep(10)
        print('\ndone: %d' % z)
