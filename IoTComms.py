#!/usr/bin/env python3
"""
IoT Reply
Performs all the comms for handling the normal operation between the IoT and the EWC.
"""



import Settings

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
    return message

def PositiveReply():
    """
    Generate a positive response to send
    includes the ETX and the XOR
    """
    print("Oops something went wrong!")
    return ""

def MissingDataLogPacket(request):
    """
    takes the request and determines what to return.
    No idea how this will work as the data is held in EWCEmulator gbl_EWC_Records
    """

    return

def DecodeandReply(fd,incoming):
    """
    decode the incoming message and determine the correct response
    Returns the reply to be sent (if any)
    """
    reply = ""
    if ValidatePacket(incoming):
        # Strip the packet apart into the key elements
        # first byte is the command
        command = incoming[0]
        if command == Settings.CMD_SET_RTC_CLOCK:
            reply = PositiveReply()
        elif command == CMD_BATTERY_STATUS:
            reply = ""                          # No Response Required
        elif command == CMD_MISSING_DATALOG_REQ:
            reply = MissingDataLogPacket(incoming)
        elif


    return

def SendResponse(fd,response):
    """
    Send the response to the serial port given
    Returns True or False depending on sending success
    """

    return

def RespondToMessage(fd):
    """
    Connects to the port
    - Reads data
    - Decodes it
    - Sends reply

    """
    data = ReadMessage(fd)
    response = DecodeandReply(fd,data)
    success = SendResponse(fd,response)
    return success

def main():

    return 0

if __name__ == '__main__':
    main()

