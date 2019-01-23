
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import binascii
import datetime
import time
import sys


# In[2]:


import serial
import os
import glob


# ### CSV data to hex

# In[3]:


file_name = sys.argv[1]
#file_name = 'function_check_MDC.csv'


# In[4]:


cmd_df = pd.read_csv(file_name,sep=',')


# In[5]:


action_list = cmd_df.loc[:,'action']


# In[6]:


remove_data_name_list = ['module','action']


# In[7]:


for remove_data_name in remove_data_name_list:
    del cmd_df[remove_data_name]


# In[8]:


cmd_df = cmd_df.astype(bytes)


# In[9]:


ascii_data_name_list = ['cmd_target','task_target']


# In[10]:


data_name_index = cmd_df.columns
hex_data_name_list = list(data_name_index)


# In[11]:


for ascii_data_name in ascii_data_name_list:
    hex_data_name_list.remove(ascii_data_name)


# In[12]:


for i in cmd_df.index:
    for hex_data_name in hex_data_name_list:
        data_int = int(cmd_df.loc[i,hex_data_name],16)
        data_bytes = data_int.to_bytes(1,'little')
        if data_int != 0:
            cmd_df.loc[i,hex_data_name] = data_bytes
        if data_int == 0x30:
            cmd_df.loc[i,hex_data_name] = b'30'


# ### Set command address

# In[13]:


cmd_length = 32


# In[14]:


start_add = 0x0000


# In[15]:


for i in cmd_df.index:
    add = start_add + cmd_length*i
    add_h_int = add >>8
    add_l_int = add & 0x00FF
    cmd_df.loc[i,'EEPROM_high_adress'] = add_h_int.to_bytes(1,'little')
    cmd_df.loc[i,'EEPROM_low_adress'] = add_l_int.to_bytes(1,'little')
    if add_h_int == 0x00:
        cmd_df.loc[i,'EEPROM_high_adress'] = b'0'
    if add_l_int == 0x00:
        cmd_df.loc[i,'EEPROM_low_adress'] = b'0'


# ### Set command ID

# In[16]:


start_ID = 0x00
cmd_ID = start_ID


# In[17]:


for i in cmd_df.index:
    cmd_df.loc[i,'cmd_ID'] = cmd_ID.to_bytes(1,'little')
    if cmd_ID == 0x00:
        cmd_df.loc[i,'cmd_ID'] = b'0'
    cmd_ID += 1
    if(cmd_ID > 0xFF):
        cmd_ID = 0x00


# ### Set time

# In[18]:


datetime_now = datetime.datetime.now()
start_seconds = 10 ## change if needed
td_start = datetime.timedelta(seconds=start_seconds)
start_daytime = datetime_now + td_start
cmd_daytime = start_daytime


# In[19]:


datetime_data_name_list = ['year','month','day','hour','minute','second']


# In[20]:


for i in cmd_df.index:
    for datetime_data_name in datetime_data_name_list:
        datetime_data = getattr(cmd_daytime, datetime_data_name)
        timetag_name = 'timetag_{0}'.format(datetime_data_name)
        if datetime_data_name == 'year':
            datetime_data -= 2000
            
        cmd_df.loc[i,timetag_name] = datetime_data.to_bytes(1,'little')
        if datetime_data == 0x00:
            cmd_df.loc[i,timetag_name] = b'0'
        elif datetime_data == 0x30:
            cmd_df.loc[i,timetag_name] = b'30'
    time_interval_s = int.from_bytes(cmd_df.loc[i,'time_interval'],'big')
    interval_daytime = datetime.timedelta(seconds = time_interval_s)
    cmd_daytime = cmd_daytime + interval_daytime


# In[21]:


option_data_name_list = ['time_interval']
cmd_data_name_list = list(data_name_index)


# In[22]:


for option_data_name in option_data_name_list:
    cmd_data_name_list.remove(option_data_name)


# ### Save as bin file

# In[23]:


bin_file_name = 'cmd_{0}_{1}_{2}.bin'.format(start_daytime.hour,start_daytime.minute,start_daytime.second)


# In[24]:


f = open(bin_file_name, 'wb')
for i in cmd_df.index:
    for data_name in cmd_data_name_list:
        if cmd_df.loc[i,data_name] == b'0':
            f.write(bytes(b'\x00'))
        elif cmd_df.loc[i,data_name] == b'00':
            f.write(bytes(b'\x00'))
        elif cmd_df.loc[i,data_name] == b'30':
            f.write(bytes(b'\x30'))
        else:
            f.write(cmd_df.loc[i,data_name])
f.close()


# ### serial config

# In[25]:


target = "COM11"
baudrate = "500000"


# In[26]:


def sendExecuteCmd(target,baudrate):
    ser = serial.Serial(target,baudrate)
    ser.write(b'\xff')
    for j in range(cmd_length - 1):
        ser.write(b'\x00')
    ser.close()


# In[27]:


def sendTimeTagCmd(target, baurate, cmd , crc_16):
    ser = serial.Serial(target,baudrate)
    crc_l = int(crc_16 & 0x00FF).to_bytes(1,'big')
    crc_h = (int(crc_16)>>8).to_bytes(1,'big')
    for i in range(len(cmd)):
        send_bytes = cmd[i].to_bytes(1,'big')
        if i == 29:
            send_bytes = crc_l
        elif i == 30:
            send_bytes = crc_h
            
        if send_bytes == b'\xc0':
            ser.write(b'\xdb')
            ser.write(b'\xdc')
        elif send_bytes == b'\db':
            ser.write(b'\xdb')
            ser.write(b'\xdd')
        else:
            ser.write(send_bytes)
    ser.close()


# In[28]:


def crc16(cmd):
    crc = 0xFFFF
    poly = 0xa001
    cmd_array = bytearray(cmd)
    for i in range(len(cmd_array)):
        cmd_byte = cmd_array[i]
        crc ^= cmd_byte
        for _ in range(0, 8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
    return np.uint16(~crc)


# ## send cmd

# In[34]:


f = open(bin_file_name, 'rb')
i = 0
while i < len(cmd_df):
    cmd = f.read(cmd_length)
    crc_16 = crc16(cmd[:29])
    print("enter: Send/", end=" ")
    print("e : Send and Execute/", end=" ")
    print("r : Return previous/", end=" ")
    print("s : Skip/", end=" ")
    print("q : Quit")
    if i < len(cmd_df) - 1:
        next_cmd_action = "next \"{0}\"".format(action_list[i+1])
    else:
        next_cmd_action = "Last cmd"
    print("\"{0}\" / {1}".format(action_list[i], next_cmd_action), end=" ")
    key = input(" Please push key:")
    if key == 's':
        print('Skip')
        if i == (len(cmd_df) -1):
            print('last cmd start')
            sendExecuteCmd(target,baudrate)
        continue
    elif key == 'q':
        print('Quit')
        break
    elif key == 'e':
        print('Send and Execute')
        sendTimeTagCmd(target, baudrate, cmd ,crc_16)
        time.sleep(1)
        sendExecuteCmd(target,baudrate)
    elif key == 'r':
        if i < 1:
            continue
        i = i - 1
        print('\r\n')
        continue
    else:
        print('Send')
        sendTimeTagCmd(target, baudrate, cmd, crc_16)
        if i == (len(cmd_df) -1):
            print('last cmd start')
            sendExecuteCmd(target,baudrate)
    print('\r\n')
    i += 1
print("finish all cmd")
f.close()


# In[30]:


os.remove(bin_file_name)

