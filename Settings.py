
"""
This contains the required settings for the eWater Simulator
"""

import logging

# System Values
EWC_ID = [b'\x01',b'\x00', b'\x00', b'\x00']
VERSION_MESSAGE = b'EWC Emulator version 1.0'


# Create a list of error codes and populate it with the posible values
ERROR_CODES = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07',
                b'\x08', b'\x09', b'\x0a', b'\x0b', b'\x0c', b'\x0d', b'\x0e', b'\x0f']

# These values are contained within the datalog packet
UUID = [b'\x3e', b'\xAA', b'\xAA', b'\x3c']
USAGE = [b'\x30', b'\x30', b'\x31', b'\x31']
START_CREDIT = [b'\x34', b'\x30', b'\x30', b'\x30']
END_CREDIT = [b'\x33', b'\x39', b'\x38', b'\x39']
FLOW_COUNT = [b'\x01', b'\x10']
FLOW_TIME = [b'\x1A', b'\x1A']


PACKET_LENGTH_ALL = 27              # Number of bytes in the packet
QUANTITY_OF_RECORDS = 1024      # The number of records within the system
PACKET_LENGTH_NO_HEAD = 27      # The length of the record without the header parts.

# Loggin level to be used
LG_LVL = logging.DEBUG


#Datalog Commands
CMD_DATALOG_PACKET = chr(0x44).encode('utf-8')

#System Commands
CMD_SET_RTC_CLOCK = chr(0x43).encode('utf-8')
CMD_BATTERY_STATUS = chr(0x42).encode('utf-8')
CMD_MISSING_DATALOG_REQ = chr(0xFF).encode('utf-8')         # TO BE DEFINED
CMD_ASSET_STATUS = chr(0xFF).encode('utf-8')                # TO BE DEFINED
CMD_SET_BATTERY_VOLT_LVLS = chr(0xFF).encode('utf-8')       # TO BE DEFINED

#EWC Commands
CMD_MESSAGE_COMMAND = chr(0x4d).encode('utf-8')
CMD_WRITE_PIC_EEPROM = chr(0x50).encode('utf-8')
CMD_READ_PIC_EEPROM = chr(0x45).encode('utf-8')
CMD_READ_SPI_EEPROM = chr(0x52).encode('utf-8')
CMD_VALVE_ON = chr(0x56).encode('utf-8')
CMD_VALVE_OFF = chr(0x4f).encode('utf-8')

#Responses
RSP_MESSAGE_COMMAND = VERSION_MESSAGE
RSP_POSITIVE = chr(0x80).encode('utf-8')
RSP_NEGATIVE = chr(0x88).encode('utf-8')

#Other bits
ETX = chr(0x03).encode('utf-8')


