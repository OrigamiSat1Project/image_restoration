# -*- coding: utf-8 -*-
"""
Created on Sun Dec 23 22:22:57 2018

@author: Coriolis
"""

import pandas as pd
import numpy as np
import struct


file_name = 'thumb.000'

data = np.zeros([10,16],dtype=np.uint8)

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


fp = open(file_name,'rb')
data[0,:] = np.fromfile(fp, np.uint8, 16)
fp.close()