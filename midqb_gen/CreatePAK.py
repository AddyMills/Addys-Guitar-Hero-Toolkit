import os
import sys


from math import trunc
root_folder = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{root_folder}\\..\\")
from CRC import QBKey
import binascii

toBytes = lambda a, b=4: a.to_bytes(b, "big")
footer = toBytes(int(("AB" * 4) + ("00" * 12) + ("AB" * 496), 16), 512)

def pakHeaderMaker(pakbytes, pakname, offset, context = False):
    pakname = pakname.lower().replace("/", "\\").replace(".xen","")
    local_strings = [".en", ".de", ".fr", ".it", ".es"]
    qb_name, extension = os.path.splitext(pakname)

    if extension in local_strings:
        extension = qb_name[-3:] + extension
        qb_name = qb_name[:-3]
        headerext = toBytes(int(QBKey(extension), 16))
        # raise Exception
    else:
        if ".0x" in extension:
            extension = extension[1:]
        headerext = toBytes(int(QBKey(extension), 16))
    # raise Exception
    startoffset = toBytes(offset)
    filesize = toBytes(len(pakbytes))
    if context:
        aContextChecksum = toBytes(int(QBKey(context), 16))
    else:
        aContextChecksum = toBytes(0)

    qb_split = qb_name.split(".")
    non_debug = 0
    for elem in qb_split:
        if "0x" in elem:
            non_debug = 1

    if not non_debug:
        if ".qb" in pakname:
            fullChecksum = toBytes(int(QBKey(pakname), 16))
        elif ".ska" in pakname:
            fullChecksum = toBytes(int(QBKey(f"{qb_name}"), 16))
        elif ".qs" in pakname:
            fullChecksum = toBytes(int(QBKey(qb_name + (".qs" if not pakname.startswith("0x") else "")), 16))
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
    elif len(qb_split) == 2:
        fullChecksum = toBytes(int(QBKey(qb_split[0]), 16))
        nameChecksum = toBytes(int(QBKey(qb_split[1]), 16))
    else:
        raise Exception



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

def pakMaker(pakfiles, songname = False, split_head = False):
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
    if songname:
        pakHeader += toBytes(int(QBKey(songname), 16))
    else:
        pakHeader += toBytes(0)
    pakHeader += toBytes(int("897ABB4A6AF98ED1", 16), 8) # Always is this. No idea what the strings are pre-checksum
    pakHeader += toBytes(0, 8)

    # Pad out the pak Header to 4096. Could technically be larger than 4096, but unlikely for songs
    if len(pakHeader) % 4096 != 0:
        pakHeader += b'\x00' * (4096 - (len(pakHeader) % 4096))

    # Create actual PAK file
    pakFile = bytearray()
    pabFile = bytearray()
    # print(len(pakFile))
    pakFile += pakHeader
        # pakHeader += pakHeaderMaker(x[0], x[1], offset)
    if not split_head:

        # Write each padded file to the PAK
        for x in files:
            pakFile += x

        # Write the last entry, plus pad out the PAK file to the % 512 bytes
        pakFile += footer
        return pakFile
    else:
        for x in files:
            pabFile += x

        # Write the last entry, plus pad out the PAK file to the % 512 bytes
        pabFile += footer
        return pakFile, pabFile


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
    root_folder = os.path.realpath(os.path.dirname(__file__))
    to_add = f"{root_folder}\\Pak Input"
    output = f'{root_folder}\\PAK compile'
    if "-pak_name" in sys.argv:
        pak_name = sys.argv[sys.argv.index("-pak_name") + 1]
    else:
        pak_name = False
    if "-split" in sys.argv:
        split = True
    else:
        split = False
    pak_data = []
    for root, dirs, files in os.walk(to_add, topdown = False):
        for name in files:
            fullpath = os.path.join(root, name)
            with open(fullpath, 'rb') as f:
                x = f.read()
            item_name = fullpath[len(to_add) + 1:]
            # raise Exception
            pak_data.append([x, item_name if not item_name.endswith(".xen") else item_name[:-4]])
            # print(os.path.join(root, name)[len(toAdd)+1:])

    filename = f"{output}\\{'b' if 'dlc' in str(pak_name) else ''}{pak_name if pak_name else 'output'}{'_song' if 'dlc' in str(pak_name) else ''}"
    if not split:
        pak_file = pakMaker(pak_data, pak_name, split)
        with open(f"{filename}.pak.xen", 'wb') as f:
            f.write(pak_file)
    else:
        pak_file, pab_file = pakMaker(pak_data, pak_name, split)
        with open(f"{filename}.pak.xen", 'wb') as f:
            f.write(pak_file)
        with open(f"{filename}.pab.xen", 'wb') as f:
            f.write(pab_file)
