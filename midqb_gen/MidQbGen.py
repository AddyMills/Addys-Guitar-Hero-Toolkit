from midqb_functions import *
from CreatePAK import pakMaker
from mido import MidiFile, MidiTrack
import os
import sys

tbp = 480



def make_mid(midfile, hopo, filename = "", consoleType = 1):
    mid = MidiFile(midfile)

    if filename == "":
        filename = os.path.splitext(os.path.basename(midfile))[0]

    headerDict = createHeaderDict(filename)
    # print(headerDict)

    midParsed = parseGH3QB(mid, hopo)
    midQB = makeMidQB(midParsed, filename, headerDict, consoleType)
    """with open(f"{filename}_song.mid.qb", 'wb') as f:
        f.write(midQB)"""
    pakFile = pakMaker([[midQB, f"songs\\{filename}.mid.qb"]])

    return pakFile, filename

if __name__ == "__main__":
    consoleType = 1  # 0 for Wii, 1 for PC, 2 for 360, 3 for XBX, 4 for PS2, 5 for WPC
    midfile = sys.argv[1]
    if len(sys.argv) == 3:
        hopo = int(sys.argv[2])
    else:
        hopo = 170

    pakFile, filename = make_mid(midfile, hopo)

    with open(f"{filename}_song.pak.xen", 'wb') as f:
        f.write(pakFile)

