from mido import MidiFile
from Sections import sections
from Classes import *
from Functions import *
from CreatePAK import pakMaker
import numpy as np
import definitions
import CRC
import os
import sys
import binascii

tbp = 480

consoleType = 1  # 0 for Wii, 1 for PC, 2 for 360, 3 for XBX, 4 for PS2, 5 for WPC

midfile = sys.argv[1]

mid = MidiFile(midfile)

filename = os.path.splitext(os.path.basename(midfile))[0]

headerDict = createHeaderDict(filename)
print(headerDict)
# print(headerDict)
midParsed = parseGH3QB(mid)
midQB = makeMidQB(midParsed, filename, headerDict, consoleType)
pakFile = pakMaker([[midQB, f"{filename}.mid.qb"]])


with open(f"{filename}_song.pak.xen", 'wb') as f:
    f.write(pakFile)

