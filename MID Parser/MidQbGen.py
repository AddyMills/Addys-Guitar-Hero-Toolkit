from mido import MidiFile
from Sections import sections
from Classes import *
from Functions import *
import numpy as np
import definitions
import CRC
import os
import sys
import binascii

tbp = 480

consoleType = 1  # 0 for Wii, 1 for PC, 2 for 360, 3 for XBX, 4 for PS2, 5 for WPC

filename = "D:\\GitHub\\Guitar-Hero-III-Tools\\MID Parser\\MidiFiles\\greengrassreal.mid"

mid = MidiFile(filename)

filename = "greengrassreal"
# filename = os.path.splitext(os.path.basename(filename))[0]

packname = f"songs/{filename}.mid.qb"

headers = []
headerDict = {}
for x in playableParts:
    for z in charts:
        for y in difficulties:
            if z == "song":
                if x == "":
                    headers.append(f"{filename}_{z}_{y}")
                else:
                    headers.append(f"{filename}_{z}_{x}_{y}")
            else:
                if x == "":
                    headers.append(f"{filename}_{y}_{z}")
                else:
                    headers.append(f"{filename}_{x}_{y}_{z}")

for x in others:
    headers.append(f"{filename}{x}")

for x in headers:
    headerDict[x] = CRC.QBKey(x)

print(headerDict)

qbFileHeader = b'\x1C\x08\x02\x04\x10\x04\x08\x0C\x0C\x08\x02\x04\x14\x02\x04\x0C\x10\x10\x0C\x00'

midQB = parseGH3QB(mid)

QBItems = []

# print(midQB)

for x in midQB["playableQB"]:
    # print(x)
    if not midQB["playableQB"][x]:
        for y in difficulties:
            instrument = x.replace("_", "").lower() if x != "Bass" else "rhythm"
            chartName = f"{filename}_song_{instrument}_{y}"
            starName = f"{filename}_{instrument}_{y}_Star"
            BMStarName = f"{filename}_{instrument}_{y}_StarBattleMode"
            QBItems.append(
                QBItem("ArrayInteger", chartName, headerDict[chartName], [], consoleType))
            QBItems.append(QBItem("ArrayArray", starName, headerDict[starName], [], consoleType))
            QBItems.append(QBItem("ArrayArray", BMStarName, headerDict[BMStarName], [], consoleType))

    for i, y in enumerate(midQB["playableQB"][x]):
        data = [midQB["playableQB"][x][y].song, midQB["playableQB"][x][y].star, midQB["playableQB"][x][y].starBM]
        if x == "Guitar":
            chartName = f"{filename}_song_{y}"
            starName = f"{filename}_{y}_Star"
            BMStarName = f"{filename}_{y}_StarBattleMode"
            QBItems.append(
                QBItem("ArrayInteger", chartName, headerDict[chartName], data[0], consoleType))
            QBItems.append(QBItem("ArrayArray", starName, headerDict[starName], data[1], consoleType))
            QBItems.append(QBItem("ArrayArray", BMStarName, headerDict[BMStarName], data[2], consoleType))
        else:
            instrument = x.replace("_", "").lower() if x != "Bass" else "rhythm"
            chartName = f"{filename}_song_{instrument}_{y}"
            starName = f"{filename}_{instrument}_{y}_Star"
            BMStarName = f"{filename}_{instrument}_{y}_StarBattleMode"
            QBItems.append(
                QBItem("ArrayInteger", chartName, headerDict[chartName], data[0], consoleType))
            QBItems.append(QBItem("ArrayArray", starName, headerDict[starName], data[1], consoleType))
            QBItems.append(QBItem("ArrayArray", BMStarName, headerDict[BMStarName], data[2], consoleType))

if not midQB["drumNotes"]:
    chartName = f"{filename}_drums_notes"
    QBItems.append(QBItem("ArrayInteger", chartName, headerDict[chartName], [], consoleType))
    # print(QBItems[-1])
else:
    chartName = f"{filename}_drums_notes"
    QBItems.append(QBItem("ArrayArray", chartName, headerDict[chartName], midQB["drumNotes"], consoleType))

# print(midQB["faceOffs"])
for x in midQB["faceOffs"]:
    chartName = f"{filename}_FaceOff{x}"
    if not midQB["faceOffs"][x]:
        QBItems.append(QBItem("ArrayInteger", chartName, headerDict[chartName], [], consoleType))
    else:
        QBItems.append(QBItem("ArrayArray", chartName, headerDict[chartName], midQB["faceOffs"][x], consoleType))

for x in midQB["faceOffs"]:
    chartName = f"{filename}_BossBattle{x}"
    QBItems.append(QBItem("ArrayArray", chartName, headerDict[chartName], [], consoleType))
# timesig (array), markers (struct), fretbars (integer)
chartName = f"{filename}_timesig"
QBItems.append(QBItem("ArrayArray", chartName, headerDict[chartName], midQB["timesig"], consoleType))
chartName = f"{filename}_fretbars"
QBItems.append(QBItem("ArrayInteger", chartName, headerDict[chartName], midQB["fretbars"], consoleType))
chartName = f"{filename}_markers"
QBItems.append(QBItem("ArrayStruct", chartName, headerDict[chartName], midQB["markers"], consoleType))

# Add drums scripts above and add anim notes
# exit()
toIgnoreNotes = ["anim"]
for x in ["scripts", "anim", "triggers", "cameras", "lightshow", "crowd", "performance"]:
    chartName = f"{filename}_{x}"
    QBItems.append(QBItem("ArrayInteger", chartName, headerDict[chartName], [], consoleType))
    chartName += "_notes"
    if x not in toIgnoreNotes:
        QBItems.append(QBItem("ArrayInteger", chartName, headerDict[chartName], [], consoleType))

P1count = 0
P2count = 0
mergedAnim = []
while True:
    try:
        if midQB["leftHandAnims"]["Guitar"][P1count].time < midQB["leftHandAnims"]["Bass"][P2count].time:
            mergedAnim.append(midQB["leftHandAnims"]["Guitar"][P1count])
            P1count += 1
        else:
            mergedAnim.append(midQB["leftHandAnims"]["Bass"][P2count])
            P2count += 1
    except:
        if P1count == len(midQB["leftHandAnims"]["Guitar"]):
            mergedAnim += midQB["leftHandAnims"]["Bass"][P2count:]
        else:
            mergedAnim += midQB["leftHandAnims"]["Guitar"][P1count:]
        break

chartName = f"{filename}_anim_notes"
QBItems.append(QBItem("ArrayArray", chartName, headerDict[chartName], mergedAnim, consoleType))

positionStart = 28

qbbytes = bytearray()

toBytes = lambda a, b=4: a.to_bytes(b, "big")
updatePos = lambda a, b: a + b

# binascii.hexlify(bytes("Intro Slow", "latin-1"), ' ', 1))
# print(bytes("Intro Slow", "utf-8"))

for i, x in enumerate(QBItems):
    x.processData(consoleType)  # Convert data in classes to numbers for use

    sectionbytes = bytearray()

    # QB Item Header
    sectionbytes += toBytes(qbNodeHeaders["SectionArray"][consoleType])
    sectionbytes += toBytes(int(headerDict[x.name], 16))  # CRC of the header name
    sectionbytes += toBytes(int(QBKey(packname), 16))  # CRC of the mid.qb name (e.g. "songs\slowride.mid.qb")

    position = positionStart + len(sectionbytes)
    sectionbytes += toBytes(position + 8)  # +8 to account for the next 8 bytes
    sectionbytes += toBytes(0)  # Next Item = 0 for mid.qb

    sectionbytes += toBytes(x.qbType)
    if x.node == "ArrayInteger":
        sectionbytes += toBytes(x.itemcount)
        position = positionStart + len(sectionbytes)
        sectionbytes += toBytes(position + 4) #List starts 4 bytes after where the offset is defined
        for y in x.data:
            if isinstance(y, Note):
                sectionbytes += toBytes(y.time)
                sectionbytes += toBytes(y.length)
                sectionbytes += toBytes(int(y.binForm(), 2))
            else:
                sectionbytes += toBytes(y)
    elif x.node == "ArrayArray":
        sectionbytes += toBytes(x.itemcount)
        position = positionStart + len(sectionbytes)
        liststart = position + 4 # To cover the 4 bytes that point to the start of list
        sectionbytes += toBytes(liststart)
        firstitem = position + 4 + (x.itemcount * 4)
        # print(firstitem)
        for j, y in enumerate(x.arraydata): # Add all starts of array entries to the mid
            arraynodelength = 4 + 4 + 4 + (len(y) * 4)
            # print(arraynodelength)
            sectionbytes += toBytes(firstitem + (arraynodelength * j))
            # print(y)
        position = positionStart + len(sectionbytes)
        for y in x.arraydata:
            sectionbytes += toBytes(x.subarraytype)
            sectionbytes += toBytes(len(y))
            position = positionStart + len(sectionbytes) + 4
            sectionbytes += toBytes(position)
            for z in y:
                sectionbytes += toBytes(z)
            position = positionStart + len(sectionbytes)
    elif x.node == "ArrayStruct":
        sectionbytes += toBytes(x.itemcount)
        position = positionStart + len(sectionbytes)
        liststart = position + 4 # To cover the 4 bytes that point to the start of list
        sectionbytes += toBytes(liststart)
        # sectionbytes += toBytes(0) * x.itemcount
        # print(firstitem)
        if "markers" in x.name:
            offsets = []
            markerBytes = bytearray() # 4 for header_marker, 4 for "first item" in struct
            for y in x.arraydata:
                # time
                offsets.append(positionStart + len(sectionbytes) + 4 * x.itemcount + len(markerBytes))
                markerBytes += toBytes(qbNodeHeaders["StructHeader"][consoleType])

                position = positionStart + len(sectionbytes) + len(markerBytes) + 4*x.itemcount
                markerBytes += toBytes(position + 4)
                markerBytes += toBytes(qbNodeHeaders["StructItemInteger"][consoleType])
                markerBytes += toBytes(int(QBKey("time"), 16))
                markerBytes += toBytes(y[0]) # Add the time of the marker
                position = positionStart + len(sectionbytes) + len(markerBytes) + 4 * x.itemcount
                markerBytes += toBytes(position + 4)

                # marker
                markerBytes += toBytes(qbNodeHeaders["StructItemStringW"][consoleType])
                markerBytes += toBytes(int(QBKey("marker"), 16))
                position = positionStart + len(sectionbytes) + len(markerBytes) + 4 * x.itemcount + 8
                markerBytes += toBytes(position)
                markerBytes += toBytes(0)
                markername = y[1]
                # print(markername, len(markername))
                markernamebytes = bytes(markername, "latin-1")
                for z in markernamebytes:
                    markerBytes += toBytes(z, 2)
                markerBytes += toBytes(0, 2)
                if len(markername) % 2 == 0:
                    markerBytes += toBytes(0, 2)
            for y in offsets:
                sectionbytes += toBytes(y)
            sectionbytes += markerBytes
            # print(offsets)

    elif x.node == "Floats":
        sectionbytes += toBytes(0)
        sectionbytes += toBytes(0)
            # print(position)
        # print(position)
        # print(x.name, x.itemcount)
    # Add the section to the overall bytearray
    qbbytes += sectionbytes
    # print(binascii.hexlify(sectionbytes, ' ', 1))
    positionStart = 28 + len(qbbytes)

        # print(positionStart)

# print(binascii.hexlify(qbbytes, ' ', 1))

filesize = len(qbbytes) + 28
fullqb = bytearray()
fullqb += toBytes(0) + toBytes(filesize) + qbFileHeader + qbbytes
with open(f"{filename}.mid.qb.xen", 'wb') as f:
    f.write(fullqb)

