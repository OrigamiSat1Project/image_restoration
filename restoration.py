# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 22:22:57 2018

@author: Coriolis
"""

import pandas as pd
import numpy as np
import struct
import re
import os


file_name = 'test.bin'

#data = np.zeros([10,16],dtype=np.uint8)

#with open(file_name, 'rb') as f:
#   gr1[1] = f.read(1)


#png_data = open('test.bin', "rb").read()
#a = struct.unpack_from('B', png_data, 1)


#buffer = []
#f = open("test.bin", "rb")
#for b in f.read():
#    buffer.append(hex(b))
#f.close()

#with open('test.bin', 'rb') as f:
#    while True:
#        d = f.read(1)
#        if len(d) == 0:
#            break
#        print('%02x' % (ord(d)), end=' ')


#fp = open(file_name,'rb')
#data = np.fromfile(fp, np.uint8, 16)
#fp.close()

pre_OK = np.array([0x0d, 0x0a],np.uint8)
pre_01 = np.array([0x30, 0x31],np.uint8)
EOF    = np.array([0xff, 0x1e],np.uint8)
EndOfJpeg = np.array([0xff, 0xd9],np.uint8)

with open(file_name, 'rb') as fp:
    data = np.fromfile(fp, np.uint8)

FileSize = data.size
tmp_count = 0
flag = 0
i = 0
j = 1

