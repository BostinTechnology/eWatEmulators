#!/usr/bin/env python3
"""
This program is used to generate a packet of data and return it as a binary string

It is intended to be used as part of the eWater Emulator, but it can be run independently.

"""

import logging
import random
import datetime

PACKET_LENGTH = 27          # Number of bytes in the packet

# Create a list of error codes and populate it with the posible values
ERROR_CODES = []
for i in range(0,16):
    ERROR_CODES.append(chr(i).encode('utf-8'))

UUID = [b'0xAA', b'0xAA', b'0xAA', b'0xAA']
USAGE = [b'0x21', b'0x22', b'0x23', b'0x24']
START_CREDIT = [b'0x31', b'0x32', b'0x33', b'0x34']
END_CREDIT = [b'0x31', b'0x32', b'0x33', b'0x30']
FLOW_COUNT = [b'0x01', b'0x10']
FLOW_TIME = [b'0x1A', b'0x1A']



def byte_to_bcd(byte):
    # Taking the given byte as an int, return the bcd equivalent
    if (byte & 0xf0) >> 4 > 9 or (byte & 0x0f) > 9:
        print("Byte to BCD Conversion encountered a non BCD value %s, set to 99" % byte)
        bcd = 99
    else:
        bcd = int(format(byte,'x'))
    return bcd

def BuildTimeandDate():
    """
    Generates a string that contains the date and time
    """
    timenow = datetime.datetime.now()
    

def GeneratePacket(good=True, error=0):
    """
    Generates and returns a single packet in binary format
    EE SS MM HH DD MT YY UU UU UU UU UC UC UC UC SCR SCR SCR SCR ECR ECR ECR ECR FC FC FT FT
    0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15  16  17  18  19  20  21  22  23 24 25 26
    """
    # Create an empty packet
    data_packet = []

    # Error Code
    if good:
        data_packet.append(ERROR_CODES[0])
    else:
        data_packet.append(ERROR_CODES[error])

    # Date and Time
    timenow = datetime.datetime.now()
    data_packet.append(str(timenow.second).encode('utf-8'))
    data_packet.append(str(timenow.minute).encode('utf-8'))
    data_packet.append(str(timenow.hour).encode('utf-8'))
    data_packet.append(str(timenow.day).encode('utf-8'))
    data_packet.append(str(timenow.month).encode('utf-8'))
    data_packet.append(str(timenow.year).encode('utf-8'))

    # 4 byte card UUID
    data_packet = data_packet + UUID
    
    # 4 byte usage counter
    data_packet = data_packet + USAGE
    
    # 4 byte start credit
    data_packet = data_packet + START_CREDIT
    
    # 4 byte end credit
    data_packet = data_packet + END_CREDIT
    
    # 2 byte flow meter count
    data_packet = data_packet + FLOW_COUNT
    
    # 2 byte flow meter time
    data_packet = data_packet + FLOW_TIME
    return data_packet


def main():

    sample = GeneratePacket()
    print("Data:%s" % sample)
    for i in range(0,16):
        sample_error = GeneratePacket(False,i)
        print("\nError Data:%s" % sample_error)
        
    return



if __name__ == '__main__':
    main()


