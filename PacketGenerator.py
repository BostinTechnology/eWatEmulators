#!/usr/bin/env python3
"""
This program is used to generate a packet of data and return it as a binary string

It is intended to be used as part of the eWater Emulator, but it can be run independently.

"""

# It may be necessary to open the file in binary mode, using 'wb'.
#TODO: Building of the sample file needs to be able to add error details

import logging
import random
import datetime
import time
import binascii

import Settings

#TODO: Need to move the settings into the seperate settings.py script

def GeneratePacket(good=True, error=0, timenow=0):
    """
    Generates and returns a single packet in binary format
    EE SS MM HH DD MT YY UU UU UU UU UC UC UC UC SCR SCR SCR SCR ECR ECR ECR ECR FC FC FT FT
    0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15  16  17  18  19  20  21  22  23 24 25 26
    """
    # Create an empty packet
    data_packet = []

    # Error Code
    if good:
        data_packet.append(Settings.ERROR_CODES[0])
    else:
        data_packet.append(Settings.ERROR_CODES[error])

    # Date and Time
    if timenow ==0:
        timenow = datetime.datetime.now()
    logging.debug("Date & Time being used:%s" % timenow)
#BUG: These should be in BCD, not strings!!!!"
    #ss = binascii.a2b_hex('{:02d}'.format(timenow.second).encode('utf-8'))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.second).encode('utf-8')))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.minute).encode('utf-8')))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.hour).encode('utf-8')))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.day).encode('utf-8')))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.month).encode('utf-8')))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.year)[2:4].encode('utf-8')))

    # 4 byte card UUID
    data_packet = data_packet + Settings.UUID

    # 4 byte usage counter
    data_packet = data_packet + Settings.USAGE

    # 4 byte start credit
    data_packet = data_packet + Settings.START_CREDIT

    # 4 byte end credit
    data_packet = data_packet + Settings.END_CREDIT

    # 2 byte flow meter count
    data_packet = data_packet + Settings.FLOW_COUNT

    # 2 byte flow meter time
    data_packet = data_packet + Settings.FLOW_TIME
    return data_packet

def BuildSampleFile(err):
    """
    Build a sample file, with each record being the next second
    """
    filename = input("Enter filename:")
    fd = open(filename, 'w')
    time = datetime.datetime.now()
    for i in range(0,Settings.QUANTITY_OF_RECORDS):
        time = time + datetime.timedelta(seconds=1)
        data = GeneratePacket(err, (i % 16), time)
        for j in range(0,len(data)):
            fd.write(str(data[j]))
            if j != len(data)-1:
                fd.write(",")
        fd.write("\n")
    fd.close

def HelpText():
    """
    Display the list of commands possible for the program
    """
    print("Menu Options")
    print("------------\n\n")
    print("1 - Build Sample Good Packet")
    print("2 - Build Sample Error Packets\n")
    print("3 - Build Sample Good File")
    print("4 - Build Sample Error File")
    print("h - Help Text")
    print("e - exit")
    return

def SplashScreen():
    print("***********************************************")
    print("*        Bostin Technology Emulator           *")
    print("*                                             *")
    print("*       in association with eWater Pay        *")
    print("*                                             *")
    print("*              Packet Generator               *")
    print("***********************************************\n")
    return

def main():

    SplashScreen()
    HelpText()
    choice = ""

    while choice.upper() != "E":
        choice = input("Select Menu Option:")
        if choice == "1":
            sample = GeneratePacket()
            print("Data:%s" % sample)
        elif choice == "2":
            for i in range(0,16):                       #TODO: Use a variable for the range, not 16
                sample_error = GeneratePacket(False,i)
                print("\nError Data:%s" % sample_error)
        elif choice == "3":
            BuildSampleFile(True)
        elif choice == "4":
            BuildSampleFile(False)
        elif choice.upper() == "H":
            HelpText()
        elif choice.upper() =="E":
            exit()
        else:
            print("unknown choice")
    return True



if __name__ == '__main__':

    logging.basicConfig(filename="PacketGenerator.txt", filemode="w", level=Settings.LG_LVL,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    main()


