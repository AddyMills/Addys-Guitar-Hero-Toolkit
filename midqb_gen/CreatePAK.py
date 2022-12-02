import os
import sys
from CRC import QBKey
import binascii

toBytes = lambda a, b=4: a.to_bytes(b, "big")

def pakHeaderMaker(pakbytes, pakname, offset):
    headerext = toBytes(int(QBKey(os.path.splitext(os.path.basename(pakname))[1]), 16))
    startoffset = toBytes(offset)
    filesize = toBytes(len(pakbytes))
    aContextChecksum = toBytes(0)
    if ".qb" in pakname:
        fullChecksum = toBytes(int(QBKey(f"songs/{os.path.basename(pakname)}"), 16))
    elif ".ska" in pakname:
        fullChecksum = toBytes(int(QBKey(f"{os.path.basename(pakname)[:-4]}"), 16))
    else:
        raise Exception
    name = f"{os.path.basename(pakname)}"
    if "." in name:
        name = name[0:name.find(".")]
    nameChecksum = toBytes(int(QBKey(f"{name}"), 16))
    parent = toBytes(0)
    flags = toBytes(0)
    header = bytearray()
    header += headerext + startoffset + filesize + aContextChecksum + fullChecksum + nameChecksum + parent + flags
    # print(binascii.hexlify(header, ' ', 1))
    return header

def pakMaker(pakfiles):
    pakHeader = bytearray()
    offset = 4096
    files = []
    for y, x in enumerate(pakfiles):
        # print(offset)
        pakHeader += pakHeaderMaker(x[0], x[1], offset - (32 * y))
        while len(x[0]) % 32 != 0:
            x[0] += toBytes(0, 1)
            # print(len(x[0]))
        offset += len(x[0])
        files.append(x[0])

    # Add footer reference to PAK header
    pakHeader += toBytes(int(QBKey(".last"), 16))
    pakHeader += toBytes(offset - (32 * len(files))) #Offset of entry is relative start of entry in header file
    pakHeader += toBytes(4)
    pakHeader += toBytes(0)
    pakHeader += toBytes(int("897ABB4A6AF98ED1", 16), 8) # Always is this. No idea what the strings are pre-checksum
    pakHeader += toBytes(0, 8)
    # Pad out the pak Header to 4096. Could technically be larger than 4096, but unlikely for songs
    while len(pakHeader) % 4096 != 0:
        pakHeader += toBytes(0, 1)
    # Create actual PAK file
    pakFile = bytearray()
    pakFile += pakHeader
    # Write each padded file to the PAK
    for x in files:
        pakFile += x

    # Write the last entry, plus pad out the PAK file to the % 512 bytes
    pakFile += toBytes(int(("AB" * 4) + ("00" * 12) + ("AB" * 496), 16), 512)
    # print(len(pakFile))

        # pakHeader += pakHeaderMaker(x[0], x[1], offset)
    return pakFile


def main(midBytes, toAdd):
    pak = pakMaker([[midBytes, toAdd]])
    name = f"{os.path.basename(toAdd)}"
    if "." in name:
        name = name[0:name.find(".")]
    # print(name)
    with open(f"{name}_song.pak.xen", 'wb') as f:
        f.write(pak)

    return

if __name__ == "__main__":
    # toAdd = "D:\GitHub\Guitar-Hero-III-Tools\MIDQBgen\greengrassreal.mid.qb.xen"
    toAdd = sys.argv[1]
    with open(toAdd, 'rb') as f:
        midBytes = f.read()
    if toAdd.endswith(".xen"):
        pakname = toAdd[:-4]
    else:
        pakname = toAdd
    main(midBytes, pakname)