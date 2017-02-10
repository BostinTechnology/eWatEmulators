
"""
This contains the required settings for the eWater Simulator
"""

EWC_ID = [b'01', b'0x45', b'0x57', b'0x43']     # 4 Byte EWC ID, reads 0x01'EWC'


# Create a list of error codes and populate it with the posible values
ERROR_CODES = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04', b'\x05', b'\x06', b'\x07', 
                b'\x08', b'\x09', b'\x0a', b'\x0b', b'\x0c', b'\x0d', b'\x0e', b'\x0f']

UUID = [b'\x3e', b'\xAA', b'\xAA', b'\x3c']
USAGE = [b'\x30', b'\x30', b'\x31', b'\x31']
START_CREDIT = [b'\x34', b'\x30', b'\x30', b'\x30']
END_CREDIT = [b'\x33', b'\x39', b'\x38', b'\x39']
FLOW_COUNT = [b'\x01', b'\x10']
FLOW_TIME = [b'\x1A', b'\x1A']


PACKET_LENGTH_ALL = 27              # Number of bytes in the packet
QUANTITY_OF_RECORDS = 1024      # The number of records within the system
PACKET_LENGTH_NO_HEAD = 27      # The length of the record without the header parts.
