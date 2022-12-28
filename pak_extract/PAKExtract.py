import sys
sys.path.append("../")

from dbg import checksum_dbg
from pak_functions import *
from CRC import QBKey
import os
import zlib

def main(pak, folder, endian = "big"):
    start = 0
    headers = []
    entries = 0
    pakHeader = ["offset", "filesize", "context_checksum", "full_name_checksum", "no_ext_name_checksum", "parent_object", "flags"]
    checksums = ["context_checksum", "full_name_checksum", "no_ext_name_checksum"]

    while True:
        no_checksum = 0
        z, start = readFourBytes(pak, start, endian)
        if z != 0:
            try:
                headers.append(pak_header(checksum_dbg[z]))
            except:
                headers.append(pak_header(f"{hex(z)}"))

                # print(headers)
                no_checksum = 1
            for y, x in enumerate(pakHeader):
                z, start = readFourBytes(pak, start, endian)
                if x == "offset":
                    rel_offset = (32*(entries))
                    setattr(headers[-1], x, z + rel_offset)
                    # print(z, rel_offset, z + rel_offset)
                else:
                    if x in checksums:
                        try:
                            setattr(headers[-1], x, checksum_dbg[z])
                        except:
                            try:
                                pak_name = folder[folder.rfind("\\") + 1:folder.rfind(".pak")]
                                song_name = pak_name[:pak_name.find("_")]
                                test_full_name = f"songs/{song_name}.mid.qb"
                                tests = [f"songs/{song_name}.mid.qb", f"songs/{song_name}_song_scripts.qb"]
                                tests_checksums = []
                                for c in tests:
                                    tests_checksums.append(int(QBKey(c),16))
                                if x == "full_name_checksum":
                                    test_qb = int(QBKey(test_full_name),16)
                                    if z in tests_checksums:
                                        setattr(headers[-1], x, tests[tests_checksums.index(z)])
                                    else:
                                        setattr(headers[-1], x, z)
                                elif x == "no_ext_name_checksum":
                                    if z == int(QBKey(song_name),16):
                                        setattr(headers[-1], x, song_name)
                                    else:
                                        setattr(headers[-1], x, z)
                                else:
                                    setattr(headers[-1], x, z)
                            except:
                                setattr(headers[-1], x, z)
                    else:
                        setattr(headers[-1], x, z)
            # print(headers[-1].extension)
            # for x in pakHeader:
                # print(getattr(headers[-1], x))
            entries += 1
        else:
            break
    if os.path.dirname(folder).find("DATA") == -1:
        main_folder_name = ""
    else:
        folder_offset = os.path.dirname(folder).find("DATA")+len("DATA\\")
        main_folder_name = os.path.dirname(folder[folder_offset:])
    subfolder_name = os.path.splitext(os.path.basename(folder))


    if "." in subfolder_name[0]:
        while "." in subfolder_name[0]:
            subfolder_name = os.path.splitext(subfolder_name[0])
    # print(subfolder_name[0])
    files = []
    for x in headers:
        if x.extension != ".last":
            if not x.extension.startswith("0x"):
                try:
                    split_ext = os.path.splitext(x.full_name_checksum)
                    if split_ext[0].startswith("c:/gh3/data/"):
                        split_0 = f"GH3\\{split_ext[0][len('c:/gh3/data/'):]}"
                    elif split_ext[0].startswith("c:/gh3_xp1/data/"):
                        split_0 = f"GH3_XP1\\{split_ext[0][len('c:/gh3/data/'):]}"
                    else:
                        split_0 = split_ext[0]
                    split_1 = split_ext[1]
                    dir_name = os.path.dirname(split_0)
                except:
                    split_0 = f"{hex(x.full_name_checksum)}"
                    dir_name = ""
            else:
                split_0 = f"{hex(x.full_name_checksum)}."
                setattr(x, "extension", x.extension[2:])
                dir_name = ""


            file_data = pak[x.offset:(x.offset+x.filesize)]
            file_name = f'{main_folder_name}\\{subfolder_name[0]}\\{split_0}{x.extension}'
            files.append({"file_name" : file_name, "file_data": file_data})


    return files

def decompress_pak(comp, endian = "big"):
    comp = compressed_pak(comp, endian)
    decomp_file = b''
    iters = 0
    while True:
        # Grab the header data for each CHNK
        last_chunk = comp.last_chnk
        comp.addToPos(4) # Skip the CHNK
        header_len = comp.readBytes()
        data_length = comp.readBytes()
        next_chnk = comp.readBytes()
        next_chnk_true = next_chnk + last_chunk # This is used to set the position of the bytes to the next piece to be decompped
        next_chnk_len = comp.readBytes() # Reading this simply to move the position 4 bytes ahead
        decomp_len = comp.readBytes()
        decomp_offset = comp.readBytes()
        if decomp_offset != len(decomp_file):
            raise Exception("Chunks appear out of order. Please contact me.")

        comp.setPosition(header_len + comp.last_chnk)
        chnk_data = comp.grabData(data_length)
        chnk_decomp = zlib.decompress(chnk_data, wbits = -15)
        if len(chnk_decomp) != decomp_len:
            raise Exception("Error decompressing. Length of chunk is not what it says it is.")
        decomp_file += chnk_decomp
        iters += 1
        if next_chnk == 0xffffffff:
            break
        comp.setPosition(next_chnk_true)
        comp.updateChnk(comp.position)

    return decomp_file

def compress_pak(decomp):

    return
def extract_paks():
    pabs = []
    paks = []
    filepaths = []
    filepaths_pab = []
    pak_type = 0
    for root, dirs, files in os.walk(f".\\input PAK"):
        for f in files:
            filename = f"{root}\\{f}"
            level_1 = os.path.splitext(os.path.basename(filename))
            level_2 = os.path.splitext(level_1[0])
            if pak_type == 0:
                pak_type = f".pak{level_1[1]}"
                # print(pak_type)
            if "pab." in filename:
                pabs.append(level_2[0])
                filepaths_pab.append(filename)
                # print(f"{level_2[1]}{level_1[1]}")
            elif "pak." in filename:
                if not filename.endswith(".pak.xen"):
                    continue
                paks.append(level_2[0])
                filepaths.append(filename)

    """print(paks)
    print(filepaths)
    print(pabs)"""
    for y, x in enumerate(paks):
        if x in pabs:
            print(f"Processing {os.path.basename(filepaths[y])}")
            with open(filepaths_pab[pabs.index(x)], 'rb') as f:
                pab_file = f.read()
            with open(filepaths[y], 'rb') as f:
                pak_file = f.read()
            pak_file += pab_file
        else:
            print(f"Processing {os.path.basename(filepaths[y])}")
            with open(filepaths[y], 'rb') as f:
                pak_file = f.read()
        if pak_file[:4] == b'CHNK': # Check for xbox compressed file
            pak_file = decompress_pak(pak_file)
            pak_decomp_out = f'.\\Decompressed PAKs\\{os.path.basename(filepaths[y])}'
            if not os.path.exists(pak_decomp_out):
                dir_name = os.path.dirname(pak_decomp_out)
                try:
                    os.makedirs(dir_name)
                except:
                    pass
                with open(pak_decomp_out, 'wb') as write_file:
                    write_file.write(pak_file)
        files = main(pak_file, filepaths[y])
        for x in files:
            output_file = f'.\\output\\PAK{x["file_name"]}.xen'
            dir_name = os.path.dirname(output_file)
            try:
                os.makedirs(dir_name)
            except:
                pass
            with open(output_file, 'wb') as write_file:
                write_file.write(x["file_data"])

    return


if __name__ == "__main__":
    extract_paks()
