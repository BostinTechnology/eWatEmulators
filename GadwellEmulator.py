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
#   Consider adding the packets into a class so I can manipulate them easier maybe...
#   improve code by having writedata respond with a message if failed
#   - stops it repeating the same 5 lines of code
#   I think some of my settings (Packet length esp) are wrong
#
# BUG: chr(0x80).encode('utf-8') creates a \xc2\x80, changed, ready to test
#
# TODO:
#   There can now be broadcast messages that start with 0xAA, an example of
#   that would be time synchronisation
#
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
import os

import Settings


BAUDRATE = 9600         # The speed of the comms
PORT = "/dev/serial0"   # The port being used for the comms
TIMEOUT = 0.5           # The maximum time allowed to receive a message
GPIO_CTS = 11           # The CTS line, also known as GPIO17
BLOCK_SIZE = 64         # The maximum size of each block of data

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
#    logging.debug("Data Available status:%s" % data_avail)
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
            datalength = CheckForMessage(fd)
            if datalength > 0:
                dlp = ReadMessage(fd)
                print("Message Received:%s\n" % dlp)
                logging.info("Message Received: %s" % dlp)

    except KeyboardInterrupt:
        logging.info("Completed reading the incoming datalog packets")
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
        if endtime < datetime.datetime.now():
            waiting = False
            reply = ""
            print("Timeout - No response received")
            logging.info("Timeout - No response received")

        datalength = CheckForMessage(fd)
        if datalength > 0:
            reply = ReadMessage(fd)
            print("Message Received:%s" % reply)
            logging.info("Message Received: %s" % reply)
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
        logging.debug("byte being XOR'd:%s" % byte)
        xor = xor ^ int(binascii.b2a_hex(byte),16)

    msg.append(binascii.a2b_hex('{:02x}'.format(xor)))
    logging.info("Comms Message generated: %s" % msg)
    return msg

def SetRTCClock():
    """
    Send the Set RTC Clock / Calendar information
    """
    request_msg = []
    logging.debug("Sending RTC Clock / Calendar")
    request_msg.append(Settings.CMD_SET_RTC_CLOCK)
    request_msg = request_msg + Settings.EWC_ID

    # Date and Time
    timenow = datetime.datetime.now()
    logging.debug("Date & Time being used:%s" % timenow)

    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.second)))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.minute)))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.hour)))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.day)))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.month)))
    request_msg.append(binascii.a2b_hex('{:02d}'.format(timenow.year)[2:4]))

    request = CommsMessageBuilder(request_msg)
    return request

def GetMissingDatalogPacket():
    """
    Request the missing datalog packet, enter number required
    """
    request_msg = []
    logging.info("Requesting a Missing Datalog Packet")

    blk = -1
    while blk == -1:
        blk = input("Select Datalog Packet (1 - %s)" % Settings.QUANTITY_OF_BLOCKS)
        if blk.isdigit() == False:
            print("Enter a number please")
            blk = -1
        elif int(blk) > Settings.QUANTITY_OF_BLOCKS or int(blk) < 0:
            print("Only numbers in the range 0 to %s are allowed\n%s" % Settings.QUANTITY_OF_BLOCKS)
            blk = -1
    blk = int(blk)

    pkt = -1
    while pkt == -1:
        pkt = input("Select Datalog Packet (1 - %s)" % Settings.QUANTITY_OF_RECORDS)
        if pkt.isdigit() == False:
            print("Enter a number please")
            pkt = -1
        elif int(pkt) > Settings.QUANTITY_OF_RECORDS or int(pkt) < 0:
            print("Only numbers in the range 0 to %s are allowed\n%s" % Settings.QUANTITY_OF_RECORDS)
            pkt = -1
    pkt = int(pkt)
    logging.debug("Datalog Packet chosen:%s" % pkt)
    print("Sending a request")
    request_msg.append(Settings.CMD_MISSING_DATALOG_REQ)
    request_msg = request_msg + Settings.EWC_ID
    request_msg.append(binascii.a2b_hex('{:02x}'.format(blk)))
    request_msg.append(binascii.a2b_hex('{:04x}'.format(pkt)))

    request = CommsMessageBuilder(request_msg)
    return request

def AssetStatus():
    """
    Send the Asset Status
    """
    request_msg = []
    logging.debug("Send Asset Status")

    request_msg.append(Settings.CMD_ASSET_STATUS)
    request_msg = request_msg + Settings.EWC_ID
    request = CommsMessageBuilder(request_msg)
    return request

def SetBatteryVoltLvls():
    """
    Send the Battery Voltage Levels
    """
    request_msg = []
    logging.debug("Set Battery Voltage Levels")

    request_msg.append(Settings.CMD_SET_BATTERY_VOLT_LVLS)
    request_msg = request_msg + Settings.EWC_ID
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL1)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL2)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL3)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL4)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL5)))
    request_msg.append(binascii.a2b_hex('{:02x}'.format(Settings.BATT_TRIP_LVL6)))

    request = CommsMessageBuilder(request_msg)
    return request

def ReplyToMessages(fd):
    """
    Reply to the following messages from the IoT
    - Battery Capacity Message


    """
    print ("Not Yet Implemented as there are no commands currently defined that need responses")
    return

def ChooseFile():
    """
    Checks the given directory and allows the user to load a file
    """
    filename = ""
    completed = False
    while completed == False:
        try:
            filename = input("Enter the full filename to load and Press Enter:")
            print("CTRL-C to Cancel")
            completed = os.path.isfile(filename)
            logging.debug("File chosen for downloading:%s with status:%s" % (filename, completed))
        except KeyboardInterrupt:
            completed = True
        except:
            print("Error loading file, please try again")
    return filename

def OpenFile(filename):
    """
    Using binary mode
    Open the file and return the identifier
    """
    try:
        rd = open(filename, 'rb')
        logging.debug("File %s opened as %s" % (filename, rd))
    except:
        print("Unable to Open File, program aborted")
        logging.error("Unable to Open File %s, program aborted" % filename)
        sys.exit()
    return rd

def SelectFile():
    """
    Get the required file to program
    Also get the device type
    return a list of the filename, the identifier,the device type and the quantity of chunks,
    """
    file_data = ["","",0,0]

    file_data[0] = ChooseFile()
    if len(file_data[0]) < 1:
        logging.debug("Failed to choose a file, selcetfile ended")
        return file_data

    file_data[1] = OpenFile(file_data[0])
    if file_data[1] == "":
        logging.debug("Failed to open a file, selcetfile ended")
        return file_data

    # Choose device type
    dev = -1
    while dev == -1:
        dev = input("Select Device Type Packet (1 - 6)")
        if dev.isdigit() == False:
            print("Enter a number please")
            dev = -1
        elif int(dev) > 6 or int(dev) < 1:
            print("Only numbers in the range 0 to 6 are allowed\n")
            dev = -1
    file_data[2] = binascii.a2b_hex('{:02x}'.format(int(dev)))
    logging.debug("Device ID chosen to use (entered and binary):%s - %s" % (dev, file_data[2]))

    file_size = os.path.getsize(file_data[0])
    chunks = int(file_size / BLOCK_SIZE)
    if file_size % BLOCK_SIZE:
        # there is a remainder, therefore 1 left over chunk.
        chunks = chunks + 1
    file_data[3] = chunks
    logging.debug("File size and the number of chunks: %s - %s" % (file_size, chunks))
    return file_data

def RequestID(fd):
    """
    Requests the ID from the IoT
    """
    request_msg = []
    logging.debug("Send Request ID message")

    request_msg.append(Settings.CMD_REQUEST_ID)
    request = CommsMessageBuilder(request_msg)

    ans = WriteDataBinary(fd,request)
    if ans > 0:
        print("Packet Sent: %s" % request)
    else:
        print("Failed to Send Packet")

    #Wait for the reply
    ans = WaitForResponse(fd)

    if len(ans) == 8:
        iot_id = ans[2:6]
    else:
        iot_id = ''
    logging.info("IoT ID extracted from the reply:%s" % iot_id)

    return iot_id

def IoTReadyforFirmware(fd, iot_id, toprogram):
    """
    Asks the IoT if it is ready for the firmware
    """
    request_msg = []
    logging.debug("IoT Ready For Firmware")

    if len(iot_id) != 4:
        print("Please Ensure Request ID command run first")
        iot_id = Settings.EWC_ID
        #return
    if toprogram[0] == '':
        print("Please ensure you have loaded a file first")
        return

    request_msg.append(Settings.CMD_IOT_READY_FOR_FIRMWARE)
    request_msg = request_msg + iot_id
    request_msg.append(toprogram[2])        # Device
    request_msg.append(binascii.a2b_hex('{:02x}'.format(toprogram[3] >> 8)) )           # Chunks MSB
    request_msg.append(binascii.a2b_hex('{:02x}'.format(toprogram[3] & 0x00ff)))            # Chunks LSB
    request = CommsMessageBuilder(request_msg)

    ans = WriteDataBinary(fd,request)
    if ans > 0:
        print("Packet Sent: %s" % request)
    else:
        print("Failed to Send Packet")

    #Wait for the reply
    ans = WaitForResponse(fd)

    if len(ans) > 7:
        if ans[0] != Settings.RSP_POSITIVE:
            logging.info("Response is NEGATIVE: %s" % ans)
            print("Negative response received: %s" % ans)
        else:
            logging.info("Response Received:%s" % ans)
            print("The IoT is Ready for the firmware")
    else:
        logging.info("Response Received:%s" % ans)
        print("Response received is too short (min 7)")

    return

def SendData(fd, iot_id, toprogram):
    """
    Send the data to the IoT
    """
    request_msg = []
    logging.debug("Send Data")

    if len(iot_id) != 4:
        print("Please Ensure Request ID command run first")
        iot_id = Settings.EWC_ID
        #return
    if toprogram[0] == '':
        print("Please ensure you have loaded a file first")
        return

    chunk = toprogram[3]
    while chunk > 0:
        # Send the chunk
        request_msg = []
        request_msg.append(Settings.CMD_SEND_DATA_CHUNK)
        request_msg = request_msg + iot_id
        request_msg.append(binascii.a2b_hex('{:02x}'.format(chunk >> 8)) )           # Chunk MSB
        request_msg.append(binascii.a2b_hex('{:02x}'.format(chunk & 0x00ff)) )           # Chunk LSB
        payload = toprogram[1].read(BLOCK_SIZE)
        request_msg.append(binascii.a2b_hex('{:02x}'.format(len(payload))))
        if len(payload) < BLOCK_SIZE:
            payload = payload + b'00000000000000000000000000000000000000000000000000000000000000000'
        for byte in payload[:64]:
            request_msg.append(binascii.a2b_hex('{:02x}'.format(byte)))
        logging.debug("Data Chunk:%s Content:%s" % (chunk, request_msg))

        request = CommsMessageBuilder(request_msg)

        ans = WriteDataBinary(fd,request)
        if ans > 0:
            print("Chunk Sent: %s" % request)
        else:
            print("Failed to Send Chunk")

        #Wait for the reply
        ans = WaitForResponse(fd)

        if len(ans) > 7:
            if ans[0] != Settings.RSP_POSITIVE:
                logging.debug("Send Chunk Response was negative:%s" % ans)
                print("Negative response to send chunk message")
                break
        else:
            logging.info("Response Received:%s" % ans)
            print("Response received is too short (min 7)")
            break

    return

def ApplyFirmware(fd, iot_id, toprogram):
    """
    Requests the ID from the IoT
    """
    request_msg = []
    logging.debug("Apply Firmware")

    if len(iot_id) != 4:
        print("Please Ensure Request ID command run first")
        iot_id = Settings.EWC_ID
        #return

    request_msg.append(Settings.CMD_APPLY_FIRMWARE)
    request_msg = request_msg + iot_id
    request_msg.append(toprogram[2])        # Device
    request = CommsMessageBuilder(request_msg)

    ans = WriteDataBinary(fd,request)
    if ans > 0:
        print("Packet Sent: %s" % request)
    else:
        print("Failed to Send Packet")

    #Wait for the reply
    ans = WaitForResponse(fd)

    if len(ans) > 8:
        if ans[0] != Settings.RSP_POSITIVE:
            logging.info("Response is NEGATIVE: %s" % ans)
            print("Negative response received: %s" % ans)
        else:
            logging.info("Response Received:%s" % ans)
            print("Application of the firmware has been successful")
    else:
        logging.info("Respojnse too short to validate")
        print("Respnse from IoT too short")
    return



def Programming(fd):
    """
    Perform the system programming functions. Will need to select a suitable file first.
    - Request ID Command (this is not strictly a system command as it can only be sent by the Bluetooth)
    - IoT Ready for Firmware
    - Send Data Chunk
    - Apply Firmware

    """
    print("1 - Select File to Program")
    print("2 - Request ID")
    print("3 - IoT Ready for Firmware")
    print("4 - Send Data")
    print("5 - Apply Firmware")
    print("e - return to previous menu")

    choice = ""
    while choice.upper() != "E":
        choice = input("Select Menu Option:")
        if choice == "1":
            toprogram = SelectFile()
            print("\nFile Loaded . . .\n")
        elif choice == "2":
            iot_id = RequestID(fd)
        elif choice == "3":
            IoTReadyforFirmware(fd, iot_id, toprogram)
        elif choice == "4":
            SendData(fd, iot_id, toprogram)
        elif choice == "5":
            ApplyFirmware(fd, iot_id, toprogram)
        else:
            print("Unknown Option")
    return

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
    print("5 - Reply to IoT Messages")
    print("e - Return to previous menu")

    while True:
        choice = input("Choose command to send:")
        if choice =="1":
            to_send = SetRTCClock()
        elif choice =="2":
            to_send = GetMissingDatalogPacket()
        elif choice =="3":
            to_send = AssetStatus()
        elif choice =="4":
            to_send = SetBatteryVoltLvls()
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
    print("R - Reply to IoT message")
    print("P - Perform Iot / EWC Programming")
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
        elif choice =="P":
            Programming(conn)
        elif choice =="R":
            to_send = ReplyToMessages(conn)
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



