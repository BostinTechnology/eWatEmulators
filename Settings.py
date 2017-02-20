
"""
This contains the required settings for the eWater Simulator
"""

import logging

# System Values
EWC_ID = [b'\x01',b'\x00', b'\x00', b'\x00']
VERSION_MESSAGE = b'EWC Emulator version 1.0'

# This is the 256 bytes of EEPROM memory that can be written.
# These are only the initial values, loaded on startup
EWC_MEMORY = ['\x00', '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\x09', '\x0a', '\x0b', '\x0c', '\x0d', '\x0e', '\x0f',
              '\x10', '\x11', '\x12', '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1a', '\x1b', '\x1c', '\x1d', '\x1e', '\x1f',
              '\x20', '\x21', '\x22', '\x23', '\x24', '\x25', '\x26', '\x27', '\x28', '\x29', '\x2a', '\x2b', '\x2c', '\x2d', '\x2e', '\x2f',
              '\x30', '\x31', '\x32', '\x33', '\x34', '\x35', '\x36', '\x37', '\x38', '\x39', '\x3a', '\x3b', '\x3c', '\x3d', '\x3e', '\x3f',
              '\x40', '\x41', '\x42', '\x43', '\x44', '\x45', '\x46', '\x47', '\x48', '\x49', '\x4a', '\x4b', '\x4c', '\x4d', '\x4e', '\x4f',
              '\x50', '\x51', '\x52', '\x53', '\x54', '\x55', '\x56', '\x57', '\x58', '\x59', '\x5a', '\x5b', '\x5c', '\x5d', '\x5e', '\x5f',
              '\x60', '\x61', '\x62', '\x63', '\x64', '\x65', '\x66', '\x67', '\x68', '\x69', '\x6a', '\x6b', '\x6c', '\x6d', '\x6e', '\x6f',
              '\x70', '\x71', '\x72', '\x73', '\x74', '\x75', '\x76', '\x77', '\x78', '\x79', '\x7a', '\x7b', '\x7c', '\x7d', '\x7e', '\x7f',
              '\x80', '\x81', '\x82', '\x83', '\x84', '\x85', '\x86', '\x87', '\x88', '\x89', '\x8a', '\x8b', '\x8c', '\x8d', '\x8e', '\x8f',
              '\x90', '\x91', '\x92', '\x93', '\x94', '\x95', '\x96', '\x97', '\x98', '\x99', '\x9a', '\x9b', '\x9c', '\x9d', '\x9e', '\x9f',
              '\xa0', '\xa1', '\xa2', '\xa3', '\xa4', '\xa5', '\xa6', '\xa7', '\xa8', '\xa9', '\xaa', '\xab', '\xac', '\xad', '\xae', '\xaf',
              '\xb0', '\xb1', '\xb2', '\xb3', '\xb4', '\xb5', '\xb6', '\xb7', '\xb8', '\xb9', '\xba', '\xbb', '\xbc', '\xbd', '\xbe', '\xbf',
              '\xc0', '\xc1', '\xc2', '\xc3', '\xc4', '\xc5', '\xc6', '\xc7', '\xc8', '\xc9', '\xca', '\xcb', '\xcc', '\xcd', '\xce', '\xcf',
              '\xd0', '\xd1', '\xd2', '\xd3', '\xd4', '\xd5', '\xd6', '\xd7', '\xd8', '\xd9', '\xda', '\xdb', '\xdc', '\xdd', '\xde', '\xdf',
              '\xe0', '\xe1', '\xe2', '\xe3', '\xe4', '\xe5', '\xe6', '\xe7', '\xe8', '\xe9', '\xea', '\xeb', '\xec', '\xed', '\xee', '\xef',
              '\xf0', '\xf1', '\xf2', '\xf3', '\xf4', '\xf5', '\xf6', '\xf7', '\xf8', '\xf9', '\xfa', '\xfb', '\xfc', '\xfd', '\xfe', '\xff',
             ]

# Create a list of error codes and populate it with the posible values, first one is a positive response
ERROR_CODES = [b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07',
                b'\x08', b'\x09', b'\x0a', b'\x0b', b'\x0c', b'\x0d', b'\x0e', b'\x0f', b'\x10', b'\x11']

# Default Datalog Packet
"""                 EE      SS      MM         HH       DD      MT        YY    UU      UU      UU      UU     UC   UC    UC    UC    SCR   SCR   SCR   SCR   ECR   ECR   ECR   ECR   FC        FC      FT       FT
                    0       1       2          3        4       5         6     7       8       9       10     11   12    13    14    15    16    17    18    19    20    21    22    23        24      25       26"""
DEF_DATALOG_PKT = [b'\x01', b'\x59', b'\x59', b'\x23', b'\x01', b'\x01', b'\x70', b'>', b'\xaa', b'\xaa', b'<', b'0', b'0', b'1', b'1', b'4', b'0', b'0', b'0', b'3', b'9', b'8', b'9', b'\x01', b'\x10', b'\x1a', b'\x1a', b'0x0', b'0x4', b'\x03', b'\x06']

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

# Logging level to be used
LG_LVL = logging.DEBUG

# Command Message Structure
LOC_CMD_BYTE_START = 0
LOC_ID_BYTE_START = 1
LOC_DATA_START = 5

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
VERSION_TERMINATOR = chr(0x00).encode('utf-8')

# Comms Settings  (all measured in seconds)
#
#          ________          ________
#         |        |        |        |
#         |        |        |        |
#   ______|        |________|        |________
#
#         ^ High   ^  Low   ^
#           Time      Time
#                  ^^
#                Delay Before Sending Data Packet
#
#
COMMS_HIGH_TIME = 2 #5
COMMS_LOW_TIME = 2 #5
COMMS_DELAY_TIME = 0.250


