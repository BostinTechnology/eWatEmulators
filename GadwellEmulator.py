#!/usr/bin/env python3

# TODO:
#   None of the commands work or send anything out yet
#   Some commands are not yet implemented
#
# Future Expansion
#   It would be nice if it were possible to check the datalog packet received against
#   the data in the EWCEmulator
#
#-----------------------------------------------------------------
# Copy taken of the eWater Emulator on 27th Feb 2017
# These were the notes on this at the time.

# TODO:
#   upgrade pyserial to v3 and change commands marked #v3
#   Allow packet to send to be chosen
#   Add in the Bootloader functionality
#   Call DataPacketLoader and PacketGenerator from within this main menu
#   Consider adding the packets into a class so I can manipulate them easier maybe...
#   improve code by having writedata respond with a message if failed
#   - stops it repeating the same 5 lines of code
#   ValveOff to be implemented
#   I think some of my settings (Packet length esp) are wrong
#
# BUG: chr(0x80).encode('utf-8') creates a \xc2\x80, is this ok??
#
# BUG: I am not convinced the XOR function is woring correctly
#
#-------------------------------------------------------------------------

import RPi.GPIO as GPIO
import serial
import logging
import sys
import datetime
import traceback
import binascii
import random

#import PacketGenerator
#import DataPacketLoader
import Settings


BAUDRATE = 9600         # The speed of the comms
PORT = "/dev/serial0"   # The port being used for the comms
TIMEOUT = 1             # The maximum time allowed to receive a message
GPIO_CTS = 11           # The CTS line, also known as GPIO17


def SerialSetup():
    """
    Setup the serial connection for the EWC, using serial
    Setup the GPIO port for the CTS line
    """
    # set the GPIO pin for the CTS line output
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_CTS, GPIO.OUT)

    # open the serial port and set the speed accordingly
    fd = serial.Serial(PORT, BAUDRATE, timeout = TIMEOUT)

    # clear the serial buffer of any left over data
    #fd.reset_output_buffer()       #v3
    fd.flushOutput()

    if fd.isOpen():
        # if serial is setup and the opened channel is greater than zero (zero = fail)
        print ("PI setup complete on channel %s" % fd)
        logging.info("PI setup complete on channel %s" % fd)
    else:
        print ("Unable to Setup communications")
        logging.error ("Unable to Setup communications")
        sys.exit()

    return fd

def ReadMessage(fd):
    """
    Read the data from the comms port
    """
    char = ""
    message = ""
    while char != "":
        try:
            char = fd.read()
        except:
            char = ""
        if char != "":
            logging.debug("Character returned from serial port:%s" % char)
            message = message + char
    logging.info("Message received from the serial port:%s" % message)
    #TODO: Message is in bytes, do I need to convert it??????
    return message

def CheckForMessage(fd):
    """
    Check if there is data in the serial port to be processed.
    Returns True if there is
    """
    data_avail = False
    try:
        data_avail = fd.in_waiting()        #V3
    except:
        data_avail = False

    return data_avail

def ReceivePackets(fd):
    """
    Receive the datalog packet from the IoT
    In a loop, CTRL-C to exit
    - Check for message
    - Receive it
    - Display it and log it
    """
    print("CTRL-C to exit")
    try:
        while True:
            if CheckForMessage(fd):
                dlp = ReadMessage(fd)
                print("Message Received:%s" % dlp)
                logging.info("Message Received: %s" % dlp)

    except KeyboardInterrupt:
        log.info("Completed reading the incoming datalog packets")
    return

def WaitForResponse(fd):
    """
    Wait in a loop for the response
    return the reply, or an empty string if nothing.
    """
    starttime= datetime.datetime.now()
    endtime = starttime + datetime.timedelta(seconds=Settings.COMMS_GAD_REPLY_TIMEOUT)
    logging.debug("Timeout Parameters, start time:%s, end time:%s" % (starttime, endtime))

    waiting = True
    reply = ""
    while waiting:
        if endtime > datetime.datetime.now():
            waiting = False
            reply = ""
            print("Timeout - No response received")
            logging.info("Timeout - No response received")

        if CheckforMessage(fd):
            reply = ReadMessage(fd)
            print("Message Received:%s" % reply)
            log.info("Message Received: %s" % reply)
            waiting = False

    return reply

def WriteDataBinary(fd,send):
    """
    This routine will take the given data and write it to the serial port
    returns the data length or 0 indicating fail
    """
    try:
        ans = fd.write(b''.join(send))
        logging.info("Message >%s< written to Serial module with response :%s" % (send, ans))
    except Exception as e:
        logging.warning("Message >%s< FAILED with response :%s" % (send, ans))
        ans = 0
    return ans

def CommsMessageBuilder(data):
    """
    Takes the given data and returns the message to be sent to the serial port
    """
    msg = []

    logging.debug("Comms Message being created / modified:%s" % data)

    msg = msg + data
    msg.append(Settings.ETX)

    # Create and add the XOR checksum
    xor = 0
    for byte in (msg):

#BUG: This is not splitting the data into its bits, but treating as oen big list

        logging.debug("byte being XOR'd:%s" % byte)
        xor = xor ^ int(binascii.b2a_hex(byte),16)

    msg.append(binascii.a2b_hex('{:02x}'.format(xor).encode('utf-8')))
    logging.info("Comms Message generated: %s" % msg)
    return msg

def SetRTCClock():
    """
    Send the Set RTC Clock / Calendar information
    """
    request_msg = []
    logging.debug("Sending RTC Clock / Calendar")
    request_msg.append(Settings.CMD_SET_RTC_CLOCK)
    request_msg.append(Settings.EWC_ID)

    # Date and Time
    timenow = datetime.datetime.now()
    logging.debug("Date & Time being used:%s" % timenow)

    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.second).encode('utf-8')))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.minute).encode('utf-8')))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.hour).encode('utf-8')))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.day).encode('utf-8')))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.month).encode('utf-8')))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.year)[2:4].encode('utf-8')))

    request = CommsMessageBuilder(request_msg)
    return request

def GetMissingDatalogPacket():
    """
    Request the missing datalog packet, enter number required
    """
    request_msg = []
    logging.debug("Requesting a Missing Datalog Packet")

    pkt = -1
    while pkt == -1:
        pkt = input("Select Datalog Packet (1 - %s)" % Settings.QUANTITY_OF_RECORDS)
        if pkt.isdigit == False:
            print("Enter a number please")
            pkt = -1
        elif int(pkt) > Settings.QUANTITY_OF_RECORDS or int(pkt) < 0:
            print("Only numbers in the range 0 to %s are allowed\n%s" % Settings.QUANTITY_OF_RECORDS)
            pkt = -1
    print("Sending a request")
    request_msg.append(Settings.CMD_MISSING_DATALOG_REQ)
    request_msg.append(Settings.EWC_ID)
    request_msg.append(binascii.a2b_hex('{:04x}'.format(pkt)))

    request = CommsMessageBuilder(request_msg)
    return request

def AssetStatus():
    """
    Send the Asset Status
    """
    print("Not yet implemented")
    return

def SetBatteryVoltLvls():
    """
    Send the Battery Voltage Levels
    """
    request_mssg = []
    logging.debug("Set Battery Voltage Levels")

    request_msg.append(Settings.CMD_SET_BATTERY_VOLT_LVLS)
    request_msg.append(Settings.EWC_ID)
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL1)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL2)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL3)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL4)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL5)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL6)))

    request = CommsMessageBuilder(request_msg)
    return request

def Menu_IoTSend(fd):
    """
    Enable the Gadwell Emulator to send messages to the IoT
    """
    print("\nSend a message to the EWC\n")
    print("Menu Options")
    print("------------\n\n")
    print("1 - Set RTC Clock / Calendar")
    print("2 - Missing Datalog Message Request")
    print("3 - Asset Status")
    print("4 - Set Battery Voltage Levels")
    print("e - Return to previous menu")

    while True:
        choice = input("Choose:")
        if choice =="1":
            to_send = SetRTCClock()
        elif choice =="2":
            to_send = GetMissingDatalogPacket()
        elif choice =="3":
            to_send = AssetStatus()
        elif choice =="4":
            to_send = SetBatteryVolt()
        elif choice.upper() =="E":
            break
        else:
            print("Unknown Option")

        ans = WriteDataBinary(fd,to_send)
        if ans > 0:
            print("Packet Sent: %s" % to_send)
        else:
            print("Failed to Send Packet")

        #Wait for the reply before exiting
        ans = WaitForResponse(fd)

    return



def HelpText():
    """
    Display the list of commands possible for the program
    """
    print("Menu Options")
    print("------------\n\n")
    print("1 - Receive Datalog Packet")
    print("0 - Send System Command to IoT")
    print("h - Show this help")
    print("e - exit")
    return

def SplashScreen():
    print("***********************************************")
    print("*        Bostin Technology Emulator           *")
    print("*                                             *")
    print("*       in association with eWater Pay        *")
    print("*                                             *")
    print("*              Gadwell Emulator               *")
    print("***********************************************\n")
    return

def main():

    SplashScreen()

    logging.info("Application Started")
    conn = SerialSetup()

    HelpText()
    choice = ""
    while choice.upper() != "E":
        choice = input("Select Menu Option:")
        if choice == "1":
            ReceivePackets(conn)
        elif choice =="0":
            Menu_IoTSend(conn)
        elif choice.upper() =="E":
            print("Leaving")
        elif choice.upper() =="H":
            HelpText()
        else:
            print("Unknown Option")
    return



if __name__ == '__main__':

    conn = ""
    logging.basicConfig(filename="GadwellEmulator.txt", filemode="w", level=Settings.LG_LVL,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    try:
        main()

    except Exception as err:
        # Write the Exception data
        logging.warning("Exception:%s" % traceback.format_exc())
        print("\nError Occurred, program halted - refer to log file\n")

    if conn != "":
        conn.close()
    GPIO.cleanup()
    logging.info("Program Exited")
    sys.exit()



