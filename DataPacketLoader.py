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

import os
import sys

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
    Open the file and return the identifier
    """
    try:
        fd = open(filename, 'r')
    except:
        print("Unable to Open File, program aborted")
        sys.exit()
    return fd

def ReadFile(fd):
    """
    take the given file and read in the records
    Return the structure of the data.
    """
    records = []
    record = []
    morerecords = True
    while morerecords:
        record = fd.readline()
        if len(record) == 0:
            morerecords = False
        else:
            records.append(record.split(','))
    return records
    
def LoadFile(filename):
    """
    Load the given file for reading and return it
    """
    # Open the file
    fd = OpenFile(filename)
    
    # Read the records
    records = ReadFile(fd)
    return records

def CheckRecords(records):
    """
    Check the quantity of records and check each record length
    """
    
    # Check there are QUANTITY_OF_RECORDS (expected to be 1024) records
    if len(records) != Settings.QUANTITY_OF_RECORDS:
        print("Record count failure, expected %s records, got %s" % (Settings.QUANTITY_OF_RECORDS, len(records)))
        return False
    # Check for each record there are the right number of bytes
    for record in records:
        if len(record) != Settings.PACKET_LENGTH_NO_HEAD:
            print("Record length failure, record \n%s\n incorrect length, expected %s, got %s" % (record, Settings.PACKET_LENGTH_NO_HEAD, len(record)))
            return False
    
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
    if len(displayfile) < 1:
        print("No file selected")
        return
    print("Displaying File, press enter between records, CTRL-C to cancel")
    try:
        for record in displayfile:
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
    if chosenfile=="":
        # No file given, chose one
        chosenfile = ChooseFile()
    rcds = LoadFile(chosenfile)
    validatedfile = ValidateFile(rcds)
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
	main()

