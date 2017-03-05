
"""
This contains the required settings for the eWater Simulator
"""

#TODO: Retest as part of the encode change

import logging

# System Values
EWC_ID = [b'\x01',b'\x00', b'\x00', b'\x00']
VERSION_MESSAGE = b'EWC Emulator version 1.0'

# This is the 256 bytes of EEPROM memory that can be written.
# These are only the initial values, loaded on startup
EWC_MEMORY = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\x09', b'\x0a', b'\x0b', b'\x0c', b'\x0d', b'\x0e', b'\x0f',
              b'\x10', b'\x11', b'\x12', b'\x13', b'\x14', b'\x15', b'\x16', b'\x17', b'\x18', b'\x19', b'\x1a', b'\x1b', b'\x1c', b'\x1d', b'\x1e', b'\x1f',
              b'\x20', b'\x21', b'\x22', b'\x23', b'\x24', b'\x25', b'\x26', b'\x27', b'\x28', b'\x29', b'\x2a', b'\x2b', b'\x2c', b'\x2d', b'\x2e', b'\x2f',
              b'\x30', b'\x31', b'\x32', b'\x33', b'\x34', b'\x35', b'\x36', b'\x37', b'\x38', b'\x39', b'\x3a', b'\x3b', b'\x3c', b'\x3d', b'\x3e', b'\x3f',
              b'\x40', b'\x41', b'\x42', b'\x43', b'\x44', b'\x45', b'\x46', b'\x47', b'\x48', b'\x49', b'\x4a', b'\x4b', b'\x4c', b'\x4d', b'\x4e', b'\x4f',
              b'\x50', b'\x51', b'\x52', b'\x53', b'\x54', b'\x55', b'\x56', b'\x57', b'\x58', b'\x59', b'\x5a', b'\x5b', b'\x5c', b'\x5d', b'\x5e', b'\x5f',
              b'\x60', b'\x61', b'\x62', b'\x63', b'\x64', b'\x65', b'\x66', b'\x67', b'\x68', b'\x69', b'\x6a', b'\x6b', b'\x6c', b'\x6d', b'\x6e', b'\x6f',
              b'\x70', b'\x71', b'\x72', b'\x73', b'\x74', b'\x75', b'\x76', b'\x77', b'\x78', b'\x79', b'\x7a', b'\x7b', b'\x7c', b'\x7d', b'\x7e', b'\x7f',
              b'\x80', b'\x81', b'\x82', b'\x83', b'\x84', b'\x85', b'\x86', b'\x87', b'\x88', b'\x89', b'\x8a', b'\x8b', b'\x8c', b'\x8d', b'\x8e', b'\x8f',
              b'\x90', b'\x91', b'\x92', b'\x93', b'\x94', b'\x95', b'\x96', b'\x97', b'\x98', b'\x99', b'\x9a', b'\x9b', b'\x9c', b'\x9d', b'\x9e', b'\x9f',
              b'\xa0', b'\xa1', b'\xa2', b'\xa3', b'\xa4', b'\xa5', b'\xa6', b'\xa7', b'\xa8', b'\xa9', b'\xaa', b'\xab', b'\xac', b'\xad', b'\xae', b'\xaf',
              b'\xb0', b'\xb1', b'\xb2', b'\xb3', b'\xb4', b'\xb5', b'\xb6', b'\xb7', b'\xb8', b'\xb9', b'\xba', b'\xbb', b'\xbc', b'\xbd', b'\xbe', b'\xbf',
              b'\xc0', b'\xc1', b'\xc2', b'\xc3', b'\xc4', b'\xc5', b'\xc6', b'\xc7', b'\xc8', b'\xc9', b'\xca', b'\xcb', b'\xcc', b'\xcd', b'\xce', b'\xcf',
              b'\xd0', b'\xd1', b'\xd2', b'\xd3', b'\xd4', b'\xd5', b'\xd6', b'\xd7', b'\xd8', b'\xd9', b'\xda', b'\xdb', b'\xdc', b'\xdd', b'\xde', b'\xdf',
              b'\xe0', b'\xe1', b'\xe2', b'\xe3', b'\xe4', b'\xe5', b'\xe6', b'\xe7', b'\xe8', b'\xe9', b'\xea', b'\xeb', b'\xec', b'\xed', b'\xee', b'\xef',
              b'\xf0', b'\xf1', b'\xf2', b'\xf3', b'\xf4', b'\xf5', b'\xf6', b'\xf7', b'\xf8', b'\xf9', b'\xfa', b'\xfb', b'\xfc', b'\xfd', b'\xfe', b'\xff',
             ]

# Create a list of error codes that can be used in the datalog packet responses and populate it
#    with the posible values, no error is \x80
ERROR_CODES = [b'\xff', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', b'\x08', b'\x09',
                b'\x0a', b'\x0b', b'\x0c', b'\x0d', b'\x0e', b'\x0f', b'\x10', b'\x11', b'\x12']

NO_ERROR = b'\x80'

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


PACKET_LENGTH_ALL = 37          # Number of bytes in the packet
QUANTITY_OF_RECORDS = 1024      # The number of records within the system
PACKET_LENGTH_NO_HEAD = 27      # The length of the record without the header or footer parts, jsut the data record.

# Logging level to be used
LG_LVL = logging.DEBUG

# Command Message Structure
LOC_CMD_BYTE_START = 0
LOC_ID_BYTE_START = 1
LOC_DATA_START = 5
LOC_BLOCK_START = 5             # WHere the block number is in the Request Missing datalog packet message
LOC_ADDR_START = 6              # Where the address is in the Request Missing datalog packet message

#Datalog Commands
CMD_DATALOG_PACKET = bytes.fromhex('44')

#System Commands
CMD_SET_RTC_CLOCK = bytes.fromhex('43')
CMD_BATTERY_STATUS = bytes.fromhex('42')
CMD_MISSING_DATALOG_REQ = bytes.fromhex('FF')         # TO BE DEFINED
CMD_ASSET_STATUS = bytes.fromhex('FF')                # TO BE DEFINED
CMD_SET_BATTERY_VOLT_LVLS = bytes.fromhex('FF')       # TO BE DEFINED

#EWC Commands
CMD_MESSAGE_COMMAND = bytes.fromhex('4d')
CMD_WRITE_PIC_EEPROM = bytes.fromhex('50')
CMD_READ_PIC_EEPROM = bytes.fromhex('45')
CMD_READ_SPI_EEPROM = bytes.fromhex('52')
CMD_VALVE_ON = bytes.fromhex('56')
CMD_VALVE_OFF = bytes.fromhex('4f')

#Responses
RSP_MESSAGE_COMMAND = VERSION_MESSAGE
RSP_POSITIVE = bytes.fromhex('80')
RSP_NEGATIVE = bytes.fromhex('88')

#Other bits
ETX = bytes.fromhex('03')
VERSION_TERMINATOR = bytes.fromhex('00')
BLOCK_COUNT = bytes.fromhex('03')

# Comms Settings (all measured in seconds) for the EWC interface
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

#Gadwell Timings
COMMS_GAD_REPLY_TIMEOUT = 5          # How long to wait for a reply from the EWC

#Battery Trip Levels
BATT_TRIP_LVL1 = 0
BATT_TRIP_LVL2 = 20
BATT_TRIP_LVL3 = 40
BATT_TRIP_LVL4 = 60
BATT_TRIP_LVL5 = 80
BATT_TRIP_LVL6 = 100
