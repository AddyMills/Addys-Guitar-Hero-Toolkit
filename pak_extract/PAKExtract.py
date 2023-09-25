import sys
sys.path.append("../")

from dbg import checksum_dbg
from pak_functions import *
from CRC import QBKey
from io import BytesIO
import os
import zlib

def main(pak, folder, endian = "big", wor_mode = 0, pak_header_size = 0, toolkit_mode = False):
    start = 0
    headers = []
    entries = 0
    pakHeader = ["offset", "filesize", "context_checksum", "full_name_checksum", "no_ext_name_checksum", "parent_object", "flags"]
    checksums = ["context_checksum", "full_name_checksum", "no_ext_name_checksum"]
    num_20_flags = 0
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
                    if wor_mode:
                        setattr(headers[-1], x, z + pak_header_size)
                    else:
                        rel_offset = (32*(entries) + (160*num_20_flags))
                        setattr(headers[-1], x, z + rel_offset)
                    # print(z, rel_offset, z + rel_offset)
                elif x == "flags" and z != 0:
                    if z == 0x20:
                        new_name, start = readxBytes(pak, start, 160)
                        new_name = new_name.replace(b'\x00', b'').decode("utf-8")
                        new_int = int(new_name, 16)
                        setattr(headers[-1], "full_name_checksum", new_int)
                        setattr(headers[-1], "no_ext_name_checksum", new_int)
                        num_20_flags += 1
                    else:
                        input("Weird flag found")
                else:
                    if x in checksums:
                        try:
                            setattr(headers[-1], x, checksum_dbg[z])
                        except:
                            try:
                                pak_name = folder[folder.rfind("\\") + 1:folder.rfind(".pak")]
                                song_name = pak_name[:pak_name.find("_s")]
                                song_names = [song_name]
                                tests_checksums = []
                                if song_name.startswith("a") or song_name.startswith("b"):
                                    song_names.append(song_name[1:])
                                tests = []
                                for checks in song_names:
                                    cur_tests = [f"songs/{checks}.mid.qb", f"songs/{checks}_song_scripts.qb",
                                             f"songs/{checks}.mid.qs", f"songs/{checks}.note", f"songs/{checks}.perf",
                                             f"songs/{checks}.perf.xml.qb"]
                                    tests += cur_tests

                                for c in tests:
                                    tests_checksums.append(int(QBKey(c),16))
                                if x == "full_name_checksum":
                                    # test_qb = int(QBKey(test_full_name),16)
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
    if toolkit_mode:
        subfolder_name = ("",)
    else:
        subfolder_name = os.path.splitext(os.path.basename(folder))


    if "." in subfolder_name[0]:
        while "." in subfolder_name[0]:
            subfolder_name = os.path.splitext(subfolder_name[0])
    # print(subfolder_name[0])
    files = []
    qs_crc = [f"0x{QBKey(x)}" for x in qs_extensions]
    for x in headers:
        if x.extension != ".last":
            if not x.extension.startswith("0x"):
                try:
                    split_ext = os.path.splitext(x.full_name_checksum)
                    split_0 = split_ext[0]
                    split_1 = split_ext[1]
                    dir_name = os.path.dirname(split_0)
                except:
                    if all([x.full_name_checksum == 0, x.no_ext_name_checksum == 0]):
                        if type(x.context_checksum) == str:
                            split_0 = x.context_checksum
                        else:
                            split_0 = hex(x.context_checksum)
                    else:
                        split_0 = f"{hex(x.full_name_checksum)}.{hex(x.no_ext_name_checksum) if type(x.no_ext_name_checksum) == int else x.no_ext_name_checksum}"
                    dir_name = ""
            else:
                if type(x.full_name_checksum) == str:
                    split_0, split_1 = os.path.splitext(x.full_name_checksum)
                    if ".qs" in x.full_name_checksum:
                        if x.extension in qs_crc:
                            setattr(x, "extension", qs_extensions[qs_crc.index(x.extension)])
                        else:
                            setattr(x, "extension", split_1)
                    else:
                        setattr(x, "extension", split_1)
                elif all([x.full_name_checksum == 0,  x.no_ext_name_checksum == 0, type(x.context_checksum) == str]):
                    split_0 = x.context_checksum
                else:
                    split_0 = f"{hex(x.full_name_checksum)}.{hex(x.no_ext_name_checksum) if type(x.no_ext_name_checksum) == int else x.no_ext_name_checksum}."

                dir_name = ""

            file_data = pak[x.offset:(x.offset+x.filesize)]
            backslash = "\\"
            main_out = (main_folder_name + backslash) if main_folder_name != "" else ""
            sub_out = (subfolder_name[0] + backslash) if subfolder_name[0] != "" else ""
            file_name = f'{main_out}{sub_out}{split_0}{x.extension}'
            files.append({"file_name" : file_name, "file_data": file_data})


    return files

def decompress_pab(comp, pak_file):
    pak = BytesIO(pak_file)
    del pak_file
    last = 0x2CB3EF3B
    files = []
    uint32 = lambda x: int.from_bytes(x.read(4), 'big')
    ext = uint32(pak)
    while ext != last:
        entry = {"extension": ext}
        entry["offset"] = uint32(pak)
        entry["length"] = uint32(pak)
        entry["pak_key"] = uint32(pak)
        entry["full_name"] = uint32(pak)
        entry["name_sum"] = uint32(pak)
        entry["parent"] = uint32(pak)
        entry["flags"] = uint32(pak)
        try:
            entry["file_name"] = f"{checksum_dbg[entry['full_name']]}{checksum_dbg[entry['extension']]}"
            entry["full_name"] = checksum_dbg[entry['full_name']]
            entry['extension'] = checksum_dbg[entry['extension']]
        except:
            entry["file_name"] = f"{entry['full_name']}.{entry['name_sum']}.{entry['extension']}"
        files.append(entry)
        ext = uint32(pak)
    pak.close()
    comp = BytesIO(comp)
    for entry in files:
        comp_bytes = comp.read(entry["length"])
        if entry["full_name"] == "SING_Adam_Dammit_100_01":
            print()
        if entry["flags"] == 512:
            magic = str(comp_bytes[:4], encoding = "UTF-8")
            if magic == "CHNK":
                comp_bytes = comp_bytes[128:]
            else:
                raise Exception("Unknown magic value found. Contact me.")
            file_bytes = zlib.decompress(comp_bytes, wbits=-15)
            file_size = int.from_bytes(file_bytes[:4], "big")
            #print()
        elif entry["flags"] == 0:
            file_size = int.from_bytes(comp_bytes[:4], "big")
            file_bytes = comp_bytes[:file_size]
        else:
            raise Exception("Unknown Flag number found. Contact me.")
        entry["file_bytes"] = file_bytes
    #while magic == "CHNK":

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

def check_decomp(comp_file, file_path = "", output_decomp = True, pab = False, *args, **kwargs):
    if comp_file[:4] == b'CHNK':  # Check for xbox compressed file
        if pab:
            comp_file = decompress_pab(comp_file, kwargs["pak_file"])
            return comp_file
        else:
            comp_file = decompress_pak(comp_file)
        if output_decomp:
            pak_decomp_out = os.path.join('.', 'Decompressed PAKs', file_path)
            if not os.path.exists(pak_decomp_out):
                dir_name = os.path.dirname(pak_decomp_out)
                try:
                    os.makedirs(dir_name)
                except:
                    pass
                with open(pak_decomp_out, 'wb') as write_file:
                    write_file.write(comp_file)
    return comp_file

def extract_paks():
    pabs = []
    paks = []
    filepaths = []
    filepaths_pab = []
    
    pak_type = 0
    wor_mode = 0

    for root, dirs, files in os.walk(os.path.join('.', 'input PAK')):
        for f in files:
            filename = os.path.join(root, f).lower()
            name_check = [filename.endswith(".pak.xen"), filename.endswith(".pak.ps3")]
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
                if not any(name_check):
                    continue
                paks.append(level_2[0])
                filepaths.append(filename)

    for y, x in enumerate(paks):
        header_size = 0
        curr_file = os.path.basename(filepaths[y])
        print(f"Processing {curr_file}")
        with open(filepaths[y], 'rb') as f:
            pak_file = f.read()
            if pak_file[:4] == b'CHNK':  # Check for WoR style PAK
                pak_file = check_decomp(pak_file, curr_file,)
        if x in pabs:
            with open(filepaths_pab[pabs.index(x)], 'rb') as f:
                pab_file = check_decomp(f.read(), curr_file.replace(".pak.xen", ".pab.xen"), False, True, pak_file= pak_file)
                if type(pab_file) == list:
                    for z in pab_file:
                        output_file = os.path.join('.', 'output', 'PAK', str(x), f'{z["file_name"]}.xen')
                        dir_name = os.path.dirname(output_file)
                        try:
                            os.makedirs(dir_name)
                        except:
                            pass
                        with open(output_file, 'wb') as write_file:
                            write_file.write(z["file_bytes"])
            continue
        else:
            pab_file = b''
        first_file = int.from_bytes(pak_file[4:8], "big")
        if first_file == 0:
            wor_mode = 1
            header_size = len(pak_file)
        if len(pak_file) > first_file and pab_file and not wor_mode:
            pak_file = pak_file[:first_file]
        pak_file += pab_file
        files = main(pak_file, filepaths[y], wor_mode = wor_mode, pak_header_size = header_size)
        for z in files:
            output_file = os.path.join('.', 'output', 'PAK', f'{z["file_name"]}.xen')
            dir_name = os.path.dirname(output_file)
            try:
                os.makedirs(dir_name)
            except:
                pass
            with open(output_file, 'wb') as write_file:
                write_file.write(z["file_data"])

    return


if __name__ == "__main__":
    extract_paks()
