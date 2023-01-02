import os
import sys
from CRC import QBKey
from math import trunc
import binascii

toBytes = lambda a, b=4: a.to_bytes(b, "big")

def pakHeaderMaker(pakbytes, pakname, offset, context = False):
    local_strings = [".en", ".de", ".fr", ".it", ".es"]
    qb_name, extension = os.path.splitext(pakname)
    if extension in local_strings:
        extension = qb_name[-3:] + extension
        qb_name = qb_name[:-3]
        headerext = toBytes(int(QBKey(extension), 16))
        # raise Exception
    else:
        headerext = toBytes(int(QBKey(extension), 16))
    # raise Exception
    startoffset = toBytes(offset)
    filesize = toBytes(len(pakbytes))
    if context:
        aContextChecksum = toBytes(int(QBKey(context), 16))
    else:
        aContextChecksum = toBytes(0)

    if ".qb" in pakname:
        fullChecksum = toBytes(int(QBKey(pakname), 16))
    elif ".ska" in pakname:
        fullChecksum = toBytes(int(QBKey(f"{qb_name}"), 16))
    elif ".qs" in pakname:
        fullChecksum = toBytes(int(QBKey(qb_name + ".qs"), 16))
    elif ".note" in pakname:
        fullChecksum = toBytes(int(QBKey(pakname), 16))
    elif ".perf" in pakname:
        fullChecksum = toBytes(int(QBKey(pakname), 16))
    else:
        raise Exception

    if "songs\\" in qb_name:
        no_songs_name = os.path.basename(qb_name)
        no_ext_name = os.path.splitext(no_songs_name)[0]
        if ".xml" in pakname:
            no_ext_name = os.path.splitext(no_ext_name)[0]
    else:
        no_ext_name = f"{qb_name}"

    """if "." in no_ext_name:
        no_ext_name = no_ext_name[0:no_ext_name.find(".")]"""
    nameChecksum = toBytes(int(QBKey(f"{no_ext_name}"), 16))

    parent = toBytes(0)
    flags = toBytes(0)

    """
    Will need to set parents and children as well as flags evenutally. 
    Probably as a different function once I add all the headers.
    """

    header = bytearray()
    header += headerext + startoffset + filesize + aContextChecksum + fullChecksum + nameChecksum + parent + flags
    # print(binascii.hexlify(header, ' ', 1))
    return header

def pakMaker(pakfiles, songname = False):
    pakHeader = bytearray()
    offset = 4096 + (4096 * trunc(len(pakfiles)/128))
    files = []
    for y, x in enumerate(pakfiles):
        # print(offset)
        pakHeader += pakHeaderMaker(x[0], x[1], offset - (32 * y), songname)
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
    if "-songname" in sys.argv:
        songname = sys.argv[sys.argv.index("-songname")+1]
    else:
        songname = False
    pakfiles = []
    for root, dirs, files in os.walk(toAdd, topdown = False):
        for name in files:
            fullpath = os.path.join(root, name)
            with open(fullpath, 'rb') as f:
                x = f.read()
            item_name = fullpath[len(toAdd)+1:]
            # raise Exception
            pakfiles.append([x, item_name if not item_name.endswith(".xen") else item_name[:-4]])
            # print(os.path.join(root, name)[len(toAdd)+1:])
    pak_file = pakMaker(pakfiles, songname)
    with open("output.pak.xen", 'wb') as f:
        f.write(pak_file)
