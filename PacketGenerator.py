#!/usr/bin/env python3
"""
This program is used to generate a packet of data and return it as a binary string

It is intended to be used as part of the eWater Emulator, but it can be run independently.

"""

# It may be necessary to open the file in binary mode, using 'wb'.
#TODO: Building of the sample file needs to be able to add error details

#BUG: The seperator between records is currently attaching itself to the last value.
# Handled within the loading program to strip it off before processing.

#TODO: Retest as part of the encode change
# changed time calculation as part of the packet generation

#BUG: The conversion to BCD for the date and time is not working correctly as it is not returning BCD.

import logging
import random
import datetime
import time
import binascii
import json

import Settings

#TODO: Need to move the settings into the seperate settings.py script

def GeneratePacket(good=True, error=0, timenow=0):
    """
    Generates and returns a single packet in binary format
    EE SS MM HH DD MT YY UU UU UU UU UC UC UC UC SCR SCR SCR SCR ECR ECR ECR ECR FC FC FT FT CONVH CONVL
    5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20  21  22  23  24  25  26  27  28 29 39 31 32    33
    """
    # Create an empty packet
    data_packet = []

    # Error Code
    if good:
        data_packet.append(Settings.NO_ERROR)
    else:
        data_packet.append(Settings.ERROR_CODES[error])

    # Date and Time
    if timenow ==0:
        timenow = datetime.datetime.now()
    logging.debug("Date & Time being used:%s" % timenow)

    #BUG: This is not working correctly as it is not returning BCD.
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.second)))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.minute)))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.hour)))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.day)))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.month)))
    data_packet.append(binascii.a2b_hex('{:02d}'.format(timenow.year)[2:4]))

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

    # 2 byte litre / Credit conversion
    data_packet = data_packet + Settings.LITRE_CREDIT_CONV
    return data_packet

def BuildSampleFile(err):
    """
    Using binary mode in the file
    Build a sample file, with each record being the next second
    """
    filename = input("Enter filename:")
    fd = open(filename, 'wb')
    time = datetime.datetime.now()
    for i in range(0,Settings.QUANTITY_OF_RECORDS):
        time = time + datetime.timedelta(seconds=1)
        # i % len.. % is modulo
        data = GeneratePacket(err, (i % len(Settings.ERROR_CODES)), time)
        for j in range(0,len(data)):
#            fd.write(str(data[j]))
            fd.write(data[j])
            if j != len(data)-1:
#                fd.write(",")
                fd.write(b',')

        fd.write(b'\n')      # BUG: This is not working right.      # TODO: Retest as changed as part of encode removal
    fd.close
    return

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
            for i in range(0,len(Settings.ERROR_CODES)):
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


