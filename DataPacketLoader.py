#!/usr/bin/env python3
"""
This program loads and validates the given file

When called from another program, it will return a 2 level structure containing the records
When run independently, it can be used to load and validate the files.

Each row of the file will be considered a single record.
The returned structure consists of a list of records, each record consists of the byte list
"""

# It may be necessary to open the file in binary mode 'rb'

# Got to the point of checking the records.
# Need to add a settings file that contains all the various defaults values like record length.

#TODO: need to put try loops around some of the stuff to enable a CTRL C to exit routine.
#TODO: Using PACKET_LENGTH for the record length check. But the file should not include some data
#TODO: Need to have syntax in the file to ignore some data.
#TODO: Chosefile can return an empty file, so there might need to be some more validation within it
#       or further processing to continue or abort

import os
import sys
import logging

import Settings


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

def OpenFileOLD(filename):
    """
    Open the file and return the identifier
    """
    try:
        rd = open(filename, 'r')
        logging.debug("File %s opened as %s" % (filename, rd))
    except:
        print("Unable to Open File, program aborted")
        logging.error("Unable to Open File %s, program aborted" % filename)
        sys.exit()
    return rd

def ReadFile(rd):
    """
    take the given file and read in the records
    Return the structure of the data.
    """
    logging.info("Reading the file in")
    records = []
    # This is a method recommended which is supposed to be more memory efficient
    for record in rd:
        logging.debug("Record Read in:%s" % record)
        slashn = record.rfind(b'\n')
        record = record[0:slashn]
        logging.debug("slash n removed from the right:%s" % record)
        records.append(record.split(','.encode('utf-8')))


#    record = []
#    morerecords = True
#    while morerecords:
#        record = rd.readline()
#        logging.debug("Record Read in:%s" % record)
#        if len(record) == 0:
#            morerecords = False
#        else:
#            records.append(record.split(','))
    logging.debug("File Read and created records\n%s" % records)
    return records

def LoadFile(filename):
    """
    Load the given file for reading and return it
    """
    logging.info("Loading the FIle")
    # Open the file
    rd = OpenFile(filename)
    logging.debug("File Opened as %s" % rd)
    # Read the records
    records = ReadFile(rd)
    logging.debug("File Read and records being returned")
    return records

def CheckRecords(records):
    """
    Check the quantity of records and check each record length
    """
    logging.info("Checking the Records File")
    # Check there are QUANTITY_OF_RECORDS (expected to be 1024) records
    if len(records) != Settings.QUANTITY_OF_RECORDS:
        print("Record count failure, expected %s records, got %s" % (Settings.QUANTITY_OF_RECORDS, len(records)))
        logging.debug("Record count failure, expected %s records, got %s" % (Settings.QUANTITY_OF_RECORDS, len(records)))
        return False
    # Check for each record there are the right number of bytes
    for record in records:
        if len(record) != Settings.PACKET_LENGTH_NO_HEAD:
            print("Record length failure, record \n%s\n incorrect length, expected %s, got %s" % (record, Settings.PACKET_LENGTH_NO_HEAD, len(record)))
            logging.debug("Record length failure, record \n%s\n incorrect length, expected %s, got %s" % (record, Settings.PACKET_LENGTH_NO_HEAD, len(record)))
            return False
    logging.debug("Records Checked Successfully")
    return True

def ValidateFile(rcds):
    """
    Take the given file and validate it for the following
    - The right number of records
    - Each record of the right length
    """

    # Check Qty Records
    good = CheckRecords(rcds)

    return good

def DisplayFile(displayfile):
    """
    Takes the given file and displays it to the screen

    """
    logging.info("Display File")
    if len(displayfile) < 1:
        print("No file selected")
        logging.debug("No Display file selected")
        return
    print("Displaying File, press enter between records, CTRL-C to cancel")
    try:
        for record in displayfile:
            logging.debug("Display Record:%s" % record)
            print("%s" % record)
            input()
    except KeyboardInterrupt:
        return
    return

def HelpText():
    """
    Display the list of commands possible for the program
    """
    print("Menu Options")
    print("------------\n\n")
    print("1 - Choose Sample File")
    print("2 - Load chosen File")
    print("3 - Validate Sample File")
    print("4 - Display Sample File")
    print("a - All")
    print("h - Help")
    print("e - exit")
    return

def SplashScreen():
    print("***********************************************")
    print("*          Bostin Technology Data             *")
    print("*                                             *")
    print("*     in association with eWater Pay          *")
    print("*                                             *")
    print("*            Data Packet Loader               *")
    print("***********************************************\n")
    return

def LoadandValidateFile(chosenfile=""):
    """
    To be called from another program, this routine loads and returns a pass / fail
    and a data structure of the validate data
    If a file is given, it will try and load it.
    """
    logging.info("Load and Validate File started")
    if chosenfile=="":
        # No file given, chose one
        chosenfile = ChooseFile()
    print("Loading File")
    rcds = LoadFile(chosenfile)
    validatedfile = ValidateFile(rcds)
    print("Loading Complete")
    return [validatedfile,rcds]

def main():

    SplashScreen()
    HelpText()

    chosenfile = ""
    choice = ""
    while choice.upper() != "E":
        choice = input("Select Menu Option:")
        if choice == "1":
            chosenfile = ChooseFile()
            print("Chosen File: %s" % chosenfile)
        elif choice =="2":
            rcds = LoadFile(chosenfile)
            print("File Loaded")
        elif choice == "3":
            validatedfile = ValidateFile(rcds)
            print("File Validation Result:%s" % validatedfile)
        elif choice == "4":
            DisplayFile(rcds)
        elif choice.upper() == "H":
            HelpText()
        elif choice.upper() == "A":
            chosenfile = ChooseFile()
            print("Chosen File: %s" % chosenfile)
            rcds = LoadFile(chosenfile)
            print("File Loaded")
            validatedfile = ValidateFile(rcds)
            print("File Validation Result:%s" % validatedfile)
            DisplayFile(rcds)
        elif choice.upper() =="E":
            exit()
        else:
            print("unknown choice")
    return True

if __name__ == '__main__':

    logging.basicConfig(filename="DataPacketLoader.txt", filemode="w", level=Settings.LG_LVL,
                        format='%(asctime)s:%(levelname)s:%(message)s')


    main()

