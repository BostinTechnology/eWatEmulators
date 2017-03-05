#!/usr/bin/env python3

# CUrrently doing:

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
#   Packet Validation is not yet implemented
#   I've got DataLogPacketBuilder and GenNextDatalogPacket that do virtualy identical things.
#       They need to be rationalised.
#
# BUG: chr(0x80).encode('utf-8') creates a \xc2\x80, This needs to be fixed.
#       changed, ready to test
#
# Testing To Do
#   Test CTS control
#   Test IoT Reply - failed lat time I tried.
# BUGS
#   conn in the try except routine at the end is not defined!
#


import RPi.GPIO as GPIO
import serial
import logging
import sys
import datetime
import traceback
import binascii
import random

import PacketGenerator
import DataPacketLoader
import Settings


BAUDRATE = 9600         # The speed of the comms
PORT = "/dev/serial0"   # The port being used for the comms
TIMEOUT = 0.5           # The maximum time allowed to receive a message
GPIO_CTS = 11           # The CTS line, also known as GPIO17

# EWC_Records holds all the records generated or send to the IoT
# EWC_Pointer holds the value of the last record sent to the IoT
gbl_EWC_Records = [''] * Settings.QUANTITY_OF_RECORDS
gbl_EWC_Pointer = -1           # Set to -1 to indicate not yet initialised

# Contains the latest values for the EWC MEMORY
gbl_EWC_Memory = Settings.EWC_MEMORY


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

def CTSControl(state="SWITCH"):
    """
    Set the state of the CTS line
    possible values for the state are
       HIGH     set it high
       LOW      set it low
       SWITCH   (default)
    """
    logging.info("CTS State Requested:%s" % state)
    if state.upper() == "HIGH":
        GPIO.output(GPIO_CTS, GPIO.HIGH)
        logging.debug("CTS Line Set High")
    elif state.upper() == "LOW":
        GPIO.output(GPIO_CTS, GPIO.LOW)
        logging.debug("CTS Line Set Low")
    elif state.upper() == "SWITCH":
        GPIO.output(GPIO_CTS, not(GPIO.input(GPIO_CTS)))
        logging.debug("CTS Line Switched")
    else:
        print("CTS Control State requested outside of range")
        logging.error("CTS Control State requested outside of range")
    return

def WriteDataBinary(fd,send,cts=True):
    """
    This routine will take the given data and write it to the serial port
    returns the data length or 0 indicating fail
    if cts is False, doesn't control the cts line
    """

    try:
        if cts:
            CTSControl("LOW")
        ans = fd.write(b''.join(send))
        logging.info("Message >%s< written to Serial module with response :%s" % (send, ans))
        if cts:
            CTSControl("HIGH")
    except Exception as e:
        logging.warning("Message >%s< FAILED with response :%s" % (send, ans))
        ans = 0
    return ans

def DataLogPacketBuilder(data, inc_id=True, ewc_id=""):
    """
    See notes in book
    Takes the given data packet and
    - Increases the gbl_EWC_Pointer
        Checks for it wrapping around
    - Generates a full packet
        Adds it into the data structure
    returns the record
    if inc_id is False, the ID is not included
    """
    msg = []
    global gbl_EWC_Pointer              # Added as I am modifying the global variable
    global gbl_EWC_Records              # Added as I am modifying the global variable

    gbl_EWC_Pointer = gbl_EWC_Pointer + 1
    logging.debug("Datalog Packet being created / modified:%s" % gbl_EWC_Pointer)
    if gbl_EWC_Pointer >= Settings.QUANTITY_OF_RECORDS:
        # Pointer has jumped past the last record, reset to the start
        gbl_EWC_Pointer = 0
        logging.debug("Buffer reached limit and reset to zero")
    msg.append(Settings.CMD_DATALOG_PACKET)
    if inc_id:
        if ewc_id == "":
            msg = msg + Settings.EWC_ID
        else:
            msg = msg + ewc_id
            logging.debug("Wrong EWC ID Used:%s" % ewc_id)
    else:
        logging.debug("EWC ID NOT included")
    msg = msg + data
    # build pointer, lower part is simply AND'd with 0xFF, while the upper part is AND'd with 0xff00 and then shited 8 bits
    ptr_l = (gbl_EWC_Pointer & 0x000000ff).to_bytes(1, byteorder='big')
    ptr_h = ((gbl_EWC_Pointer & 0x0000ff00)>>8).to_bytes(1, byteorder='big')
    msg.append(ptr_h)
    msg.append(ptr_l)
    msg.append(Settings.ETX)

    # Create and add the XOR checksum
    xor = 0
    for byte in (msg):
        logging.debug("byte being XOR'd:%s" % byte)
        xor = xor ^ int(binascii.b2a_hex(byte),16)

    msg.append(binascii.a2b_hex('{:02x}'.format(xor)))
    logging.info("Datalog Packet:%s" % msg)
    gbl_EWC_Records[gbl_EWC_Pointer] = msg
    return msg

def GenerateGoodPacket():
    """
    Generates and returns a single packet
    Uses the Packet Generator program to get a packet
    """
    # generated by the PacketGenerator script
    datalog = PacketGenerator.GeneratePacket()
    logging.debug("Data Packet Generated:%s" % datalog)
    packet = DataLogPacketBuilder(datalog)
    return packet

def GenerateErrorPacket(error):
    """
    Generates a packet with an error code first
    """
    # generated by the PacketGenerator script
    datalog = PacketGenerator.GeneratePacket(False,error)
    logging.debug("Data Packet Generated:%s" % datalog)
    packet = DataLogPacketBuilder(datalog)
    return packet

def Menu_ControlCTS(fd):
    """
    Allow the user to manually, or automatically toggle the CTS line
    """
    print("\nControl the CTS Line\n")
    choice = input("Choose (H)igh, (L)ow, (T)oggle or (R)epeatably Toggle:")
    if choice.upper() =="H":
        CTSControl("HIGH")
        print("CTS Now High")
    elif choice.upper() =="L":
        CTSControl("LOW")
        print("CTS Now Low")
    elif choice.upper() =="T":
        CTSControl("SWITCH")
        print("CTS Switched")
    elif choice.upper() =="R":
        speed =0
        while speed ==0:
            speed = input("Set time period (in seconds)")
            if speed.isdigit() == False:
                print("Enter a number please")
                speed = 0
            elif speed < 0:
                print("Only positive numbers please")
                speed = 0
        print("CTRL-C to exit")
        try:
            while True:
                # in the loop waiting for the CTRL-C key press to exit
                starttime = datetime.datetime.now()
                endtime = starttime + datetime.timedelta(seconds=speed)
                while endtime > datetime.datetime.now():
                    print ("\r.", end="")
                CTSControl("SWITCH")
                print("Switched")
        except KeyboardInterrupt:
            print("Completed")
    else:
        print("Unknown Option")
    return

def SendSinglePacket(fd):
    """
    Send a single packet to the EWC
    Controls the CTS line automatically
    """
    print("Sending a packet")
    # Get a packet
    to_send = GenerateGoodPacket()

    # Send a packet
    ans = WriteDataBinary(fd,to_send)
    if ans > 0:
        print("Packet Sent: %s" % to_send)
    else:
        print("Failed to send packet")
    return

def SendRepeatingPacket(fd):
    """
    Allows the user to determine the speed of messaging and then sends a packet repeatably
    Controls the CTS line
    """

    speed =0
    while speed ==0:
        speed = input("Set time period (in seconds)")
        if speed.isdigit() == False:
            print("Enter a number please")
            speed = 0
        else:
            if int(speed) < 0:
                print("Only positive numbers please")
                speed = 0
            else:
                speed = int(speed)
    print("CTRL-C to exit")
    try:
        while True:
            # in the loop waiting for the CTRL-C key press to exit
            starttime = datetime.datetime.now()
            endtime = starttime + datetime.timedelta(seconds=speed)
            while endtime > datetime.datetime.now():
                print ("\rWaiting", end="")
            print("\nSending a packet")
            # Get a packet
            to_send = GenerateGoodPacket()

            # Send a packet
            ans = WriteDataBinary(fd,to_send)
            if ans > 0:
                print("Packet Sent: %s" % to_send)
            else:
                print("Failed to Send Packet")
    except KeyboardInterrupt:
        print("Completed")
    return

def SendErrorPacket(fd):
    """
    Allow the user to select an error code and then send a single packet with the error code
    Controls the CTS line
    """
    err =0
    #Print the error codes
    logging.info("Sending a Error Packet")
    while err == 0:
        err = input("Enter Error Code (decimal only)")
        if err.isdigit() == False:
            print("Enter a number please")
            err = 0
        else:
            # Need to validate the error reqeusted is in the list of error codes
            err = int(err)
            # Convert to a binary number
            err_bin = binascii.unhexlify('{:02x}'.format(int(err)))
            if err_bin not in Settings.ERROR_CODES:
                print("Only numbers listed below are allowed\n%s" % Settings.ERROR_CODES)
                err = 0
    logging.debug("Error Code Entered / Selected: %s / %s" % (err, Settings.ERROR_CODES.index(err_bin)))
    print("Sending a packet")
    # Get a packet
    to_send = GenerateErrorPacket(Settings.ERROR_CODES.index(err_bin) )


    # Send a packet
    ans = WriteDataBinary(fd,to_send)
    if ans > 0:
        print("Packet Sent: %s" % to_send)
    else:
        print("Failed to Send Packet")
    return

def GenerateTooShort():
    """
    Send a data packet that is too short
    """
    # generated by the PacketGenerator script
    datalog = PacketGenerator.GeneratePacket()
    logging.debug("Datalog Packet Generated:%s" % datalog)
    packet = DataLogPacketBuilder(datalog[0:len(datalog)-1])
    return packet

def GenerateTooBig():
    """
    Send a data packet that is too big, added 0xff at the end
    """
    # generated by the PacketGenerator script
    datalog = PacketGenerator.GeneratePacket()
    datalog.append(b'\xff')
    logging.debug("Datalog Packet Generated:%s" % datalog)
    packet = DataLogPacketBuilder(datalog)
    return packet

def GenerateOutofSyncForward():
    """
    Send a data packet that is the wrong sequence number
    """
    for i in range(0,6):
        data = GenerateGoodPacket()
    return data

def GenerateOutofSyncBackward():
    """
    Send a data packet that is the wrong sequence number
    """
    cur_posn = gbl_EWC_Pointer
    if cur_posn > 5:
        new_posn = cur_posn - 5
    else:
        new_posn = 0
    logging.debug("Calculated position for sync backwards %s" % new_posn)
    data = gbl_EWC_Records[new_posn]
    return data

def GenerateWrongID():
    """
    Send a data packet with No ID at the front of it
    """
    wrong_ewc = [b'\x02',b'\xF0', b'\x00', b'\x0F']
    # generated by the PacketGenerator script
    datalog = PacketGenerator.GeneratePacket()
    logging.debug("Data Packet Generated:%s" % datalog)
    packet = DataLogPacketBuilder(datalog, ewc_id=wrong_ewc)
    return packet

def GenerateNoID():
    """
    Send a data packet that has NO ID in it
    """
    # generated by the PacketGenerator script
    datalog = PacketGenerator.GeneratePacket()
    logging.debug("Data Packet Generated:%s" % datalog)
    packet = DataLogPacketBuilder(datalog, inc_id=False)
    return packet

def HelpMenu_BadPacket():
    """
    Help for the Bad Packet Menu
    """
    print("\nSend a bad Packet from the EWC\n")
    print("Menu Options")
    print("------------\n\n")
    print("1 - Too short (1 byte)")
    print("2 - Too big (1 byte)")
    print("3 - Out of Sync Forward")
    print("4 - Out of Sync Backward")
    print("5 - Wrong ID")
    print("6 - No ID")
    print("h - This help information")
    print("e - Return to previous menu")
    return

def Menu_BadPacket(fd):
    """
    Provide the menu to allow the different bad packets to be sent / received
    - Too small / big
    - Out of Sync
    - Wrong ID / No ID
    - CRC Error
    """
    HelpMenu_BadPacket()
    choice = ""
    while choice.upper() !="E":
        choice = input("Choose:")
        if choice =="1":
            to_send = GenerateTooShort()
        elif choice =="2":
            to_send = GenerateTooBig()
        elif choice =="3":
            to_send = GenerateOutofSyncForward()
        elif choice =="4":
            to_send = GenerateOutofSyncBackward()
        elif choice =="5":
            to_send = GenerateWrongID()
        elif choice =="6":
            to_send = GenerateNoID()
        elif choice.upper() =="H":
            HelpMenu_BadPacket()

        if choice.upper() !="H":
            # Send the generated data packet unless help chosen
            ans = WriteDataBinary(fd,to_send)
            if ans > 0:
                print("Packet Sent: %s" % to_send)
            else:
                print("Failed to Send Packet")
    return

########################################################################
#
#           Generic Comms Routines
#
########################################################################



def ReadMessage(fd):
    """
    Read the data from the comms port
    """
    logging.info("Reading a message")
    moredata = True
    char = b''
    message = b''
    while moredata:
        try:
            char = fd.read()
            logging.debug("Character returned from serial port:%s" % char)
        except:
            char = ""
            logging.error("Error reading the serial port")
            moredata = False

        if len(char) > 0:
            message = message + char
        else:
            moredata = False
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
        data_avail = fd.inWaiting()        #V3
    except:
        data_avail = False

    return data_avail

def CommsMessageBuilder(data):
    """
    Takes the given data and returns the message to be sent to the serial port
    Data passed in must be a list
    """
    msg = []

    logging.debug("Comms Message being created / modified:%s" % data)

    msg = msg + data
    msg.append(Settings.ETX)

    # Create and add the XOR checksum
    xor = 0
    for byte in (msg):
        logging.debug("byte being XOR'd:%s" % byte)
        xor = xor ^ int(binascii.b2a_hex(byte),16)

    msg.append(binascii.a2b_hex('{:02x}'.format(xor)))      #TODO: Retest due to encoding
    logging.info("Comms Message generated: %s" % msg)
    return msg

def PositiveReply():
    """
    Generate a positive response to send
    ETX and the XOR, handled by the CommsMessaegBuilder
    """
    response_cmd = []
    logging.debug("Positive Response Required")
    response_cmd.append(Settings.RSP_POSITIVE)
    response = CommsMessageBuilder(response_cmd)
    return response

def NegativeReply():
    """
    Generate a positive response to send
    ETX and the XOR, handled by the CommsMessaegBuilder
    """
    response_cmd = []
    logging.debug("Negative Response Required")
    response_cmd.append(Settings.RSP_NEGATIVE)
    response = CommsMessageBuilder(response_cmd)
    return response

def VersionMessage():
    """
    Return the version information
    """
    response = []
    logging.debug("Version Message Response Required")
    response.append(Settings.VERSION_MESSAGE)
    response.append(Settings.VERSION_TERMINATOR)
    return response

def WritePICEEPROM(message):
    """
    Capture the PIC valuie being written incase it is read afterwards
    Return a positive reply
    """
    logging.debug("Writing PIC EEPROM Response required")
    global gbl_EWC_Memory
    #convert the binary string to a value
    addr = int(binascii.b2a_hex(message[Settings.LOC_DATA_START]),16)          # The address is the first byte
    value = int(binascii.b2a_hex(message[Settings.LOC_DATA_START+1]),16)       # The data required is the next byte
    try:
        gbl_EWC_Memory[addr] = value
    except:
        print("Failed to Write PIC memory, possibly out of range")
        logging.error("Failed to Write PIC memory, possibly out of range")
        logging.debug("Useful Information addr:%s, value%s" % (addr, value))
    return PositiveReply()

def ReadPICEEPROM(message):
    """
    Respond with the value stored in the PIC EEPROM
    """
    logging.debug("Reading PIC EEPROM Response required")
    global gbl_EWC_Memory
    addr = int(binascii.b2a_hex(message[Settings.LOC_DATA_START]),16)          # The address is the first byte
    try:
        value = gbl_EWC_Memory[addr]
    except:
        print("Failed to Read PIC memory, possibly out of range")
        logging.error("Failed to Read PIC memory, possibly out of range")
        logging.debug("Useful Information addr:%s" % addr)
    response = Settings.RSP_POSITIVE
    response = response + value
    return response

def ReadSPIEEPROM(message):
    """
    Respond with a 36 byte SPI eeprom Datalog packet from the given location
    """
    print("Not yet implemented and not clear in the spec")
    logging.error("Not yet implemented and not clear in the spec")

    response_msg = []
    logging.debug("Reading SPI EEPROM Response required")
    global gbl_EWC_Records
    addr = int(binascii.b2a_hex(message[Settings.LOC_ADDR_START:Settings.LOC_ADDR_START+1]),16)          # The address is 2 bytes long
    try:
        value = gbl_EWC_Records[addr]
    except:
        print("Failed to Read EWC Record, possibly out of range")
        logging.error("Failed to Read EWC Record, possibly out of range")
        logging.debug("Useful Information addr:%s" % addr)
        value = Settings.DEF_DATALOG_PKT
    response_msg = Settings.CMD_DATALOG_PACKET
#BUG: The above line is incorrect as the response should be different to this
    response_msg.append(Settings.EWC_ID)
    response_msg = response_msg + value

    response = CommsMessageBuilder(response_msg)
    return response

def ValveOff():
    """
    Return a message stating how much water has been used
    """
    response_cmd = []
    logging.debug("Valve Off Response")
    response_cmd.append(Settings.RSP_POSITIVE)
    response_cmd.append(Settings.FLOW_COUNT)
    response = CommsMessageBuilder(response_cmd)
    return response

def ValidatePacket(message):
    """
    Given the incoming message, validate it as a full packet
    """
    print("Packet Validation not yet implemented")
    logging.debug("Packet Validation not yet implemented")
    return True

def DecodeandReply(fd,incoming):
    """
    decode the incoming message and determine the correct response
    Returns the reply to be sent (if any)
    """
    reply = ""
    if ValidatePacket(incoming):
        # Strip the packet apart into the key elements
        # first byte is the command
        command = incoming[Settings.LOC_CMD_BYTE_START]
        if command == Settings.CMD_MESSAGE_COMMAND:
            reply = VersionMessage()
        elif command == Settings.CMD_WRITE_PIC_EEPROM:
            reply = WritePICEEPROM(incoming)
        elif command == Settings.CMD_READ_PIC_EEPROM:
            reply = ReadPICEEPROM(incoming)
        elif command == Settings.CMD_READ_SPI_EEPROM:
            reply = ReadSPIEEPROM(incoming)
        elif command == Settings.CMD_VALVE_ON:
            reply = PositiveReply(incoming)
        elif command == Settings.CMD_VALVE_OFF:
            reply = ValveOff(incoming)
        else:
            reply = NegativeReply()

    return reply

def SendResponse(fd,send):
    """
    Send the response to the serial port given
    Returns True or False depending on sending success
    """
    logging.info("Message to be sent is:%s" % send)

    try:
        ans = fd.write(b''.join(send))
        logging.info("Message >%s< written to Serial module with response :%s" % (send, ans))
    except Exception as e:
        logging.warning("Message >%s< FAILED with response :%s" % (send, ans))
        ans = 0
    return ans

def RespondToMessage(fd):
    """
    Connects to the port
    - Reads data
    - Decodes it
    - Sends reply

    """
    data = ReadMessage(fd)              # Data is in type bytes,
    response = DecodeandReply(fd,data)
    success = SendResponse(fd,response)
    return success

def GetNextDataLogPacket():
    """
    Returns the NEXT datalog packet already generated
    - Increases the gbl_EWC_Pointer
        Checks for it wrapping around
    """
    msg = []
    global gbl_EWC_Pointer              # Added as I am modifying the global variable
    global gbl_EWC_Records              # Added as I am modifying the global variable

    msg.append(Settings.CMD_DATALOG_PACKET)
    msg = msg + Settings.EWC_ID
    gbl_EWC_Pointer = gbl_EWC_Pointer + 1
    logging.debug("Get Next Datalog Packet being returned:%s" % gbl_EWC_Pointer)
    if gbl_EWC_Pointer >= Settings.QUANTITY_OF_RECORDS:
        # Pointer has jumped past the last record, reset to the start
        gbl_EWC_Pointer = 0
        logging.debug("Get Next Datalog Buffer reached limit and reset to zero")
    logging.debug("Datalog Packet Being used:%s" % gbl_EWC_Records[gbl_EWC_Pointer])
    msg = msg + gbl_EWC_Records[gbl_EWC_Pointer]
    # build pointer, lower part is simply AND'd with 0xFF, while the upper part is AND'd with 0xff00 and then shited 8 bits
    ptr_l = (gbl_EWC_Pointer & 0x000000ff).to_bytes(1, byteorder='big')
    ptr_h = ((gbl_EWC_Pointer & 0x0000ff00)>>8).to_bytes(1, byteorder='big')
    msg.append(ptr_h)
    msg.append(ptr_l)
    msg.append(Settings.ETX)

    # Create and add the XOR checksum
    xor = 0
    for byte in (msg):
        logging.debug("byte being XOR'd:%s" % byte)
        xor = xor ^ int(binascii.b2a_hex(byte),16)

    msg.append(binascii.a2b_hex('{:02x}'.format(xor)))

    return msg

def MaybeSendPacket(fd):
    """
    This routine is called every time, but it only sends a packet response SOMETIMES
    Handles everything about sending the packet
    """
    global gbl_EWC_Pointer              # Added as I am modifying the global variable
    global gbl_EWC_Records              # Added as I am modifying the global variable

    guess = random.randint(0,6)
    if guess > 0:       # Changed for debugging
#    if guess == 5:
        logging.info("Sending a message")
        response = DataLogPacketBuilder()

        SendResponse(fd,response)
    else:
        logging.info("No message sent this time")
    return

def LoadDataPacket():
    """
    Perform the data loading activities
    Returns a structure of the data loaded
    """
    goodfile = False
    while goodfile == False:
        dpl = DataPacketLoader.LoadandValidateFile()
        goodfile = dpl[0]
    logging.info("Valid Data file loaded")
    return dpl[1]

def IoTReply(fd):
    """
    Perform the actions to respond to the IoT.
    Doesn't handle CTS Control
    """
    print("CTRL-C To Exit")
    try:
        incomms = True
        while incomms:
            # Waiting to see if comms message received
            gotmessage = CheckForMessage(fd)            #Checks to see if there is any data to be received
            if gotmessage:
                RespondToMessage(fd)

    except KeyboardInterrupt:
        incomms = False

    return

def AutomatedSolution(fd):
    """
    Respond to the IoT commands automatically
    Routine (stay in until CTRL-C
    0. Load data file into gbl_EWC_Records
    1. CTS Low
    2. Send Data Packet (sometimes)
    3. Wait for comms
    4. CTS High
    """
    global gbl_EWC_Records

    # load the file
    gbl_EWC_Records = LoadDataPacket()

    print("CTRL-C To Exit")
    try:
        incomms = True
        while incomms:
            # Comms high time
            CTSControl("HIGH")
            gonehigh = datetime.datetime.now()
            endtime = gonehigh + datetime.timedelta(seconds=Settings.COMMS_HIGH_TIME)
            logging.debug("High Time Parameters, gone high at:%s, end time:%s" % (gonehigh, endtime))
            while endtime > datetime.datetime.now():
                print ("\rH", end="")

            # Comms Low Time
            CTSControl("LOW")
            print("\rL", end="")
            gonelow = datetime.datetime.now()
            endtime = gonelow + datetime.timedelta(seconds=Settings.COMMS_LOW_TIME)
            logging.debug("Low Time Parameters, gone low at:%s, end time:%s" % (gonelow, endtime))

            MaybeSendPacket(fd)                 # Determines if there is a datalog packet to send and sends it
            while endtime > datetime.datetime.now():
                # Waiting to see if comms message received
                gotmessage = CheckForMessage(fd)            #Checks to see if there is any data to be received
                if gotmessage:
                    RespondToMessage(fd)

    except KeyboardInterrupt:
        incomms = False


    return





def HelpText():
    """
    Display the list of commands possible for the program
    """
    print("Menu Options")
    print("------------\n\n")
    print("1 - Control CTS")
    print("2 - Send Datalog Packet")
    print("3 - Send Datalog Packet every x seconds")
    print("4 - Send Datalog Packet with error code ee")
    print("5 - Send bad Datalog Packet")
    print("0 - Respond to IoT")
    print("a - Automated Solution")
    print("h - Show this help")
    print("e - exit")
    return

def SplashScreen():
    print("***********************************************")
    print("*        Bostin Technology Emulator           *")
    print("*                                             *")
    print("*       in association with eWater Pay        *")
    print("*                                             *")
    print("*                EWC Emulator                 *")
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
            Menu_ControlCTS(conn)
        elif choice == "2":
            SendSinglePacket(conn)
        elif choice == "3":
            SendRepeatingPacket(conn)
        elif choice == "4":
            SendErrorPacket(conn)
        elif choice == "5":
            Menu_BadPacket(conn)
        elif choice =="0":
            IoTReply(conn)
        elif choice.upper() == "A":
            AutomatedSolution(conn)
        elif choice.upper() == "E":
            print("Leaving")
        elif choice.upper() == "H":
            HelpText()
        else:
            print("Unknown Option")
    return



if __name__ == '__main__':

    conn = ""
    logging.basicConfig(filename="EWCEmulator.txt", filemode="w", level=Settings.LG_LVL,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    try:
        main()

    except Exception as err:
        # Write the Exception data
        logging.warning("Exception:%s" % traceback.format_exc())
        print("\nError Occurred, program halted - refer to log file\n")

    logging.info("gbl_EWC_Pointer:%s" % gbl_EWC_Pointer)
    logging.info("Capturing gbl_EWC_Records data")
    for rcd in range(0, gbl_EWC_Pointer):
        logging.info("%s -> %s" %(rcd, gbl_EWC_Records[rcd]))
    logging.info("Capturing the EEPROM Map")
    for i in range(0,len(gbl_EWC_Memory),8):
        logging.info("%s : %s: %s: %s: %s: %s: %s: %s" %(gbl_EWC_Memory[i],gbl_EWC_Memory[i+1],
                gbl_EWC_Memory[i+2],gbl_EWC_Memory[i+3],gbl_EWC_Memory[i+4],gbl_EWC_Memory[i+5],
                gbl_EWC_Memory[i+6],gbl_EWC_Memory[i+7]))

    if conn != "":
        conn.close()
    GPIO.cleanup()
    logging.info("Program Exited")
    sys.exit()



