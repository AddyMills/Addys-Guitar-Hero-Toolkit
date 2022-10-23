from definitions import *
from Functions import *
from Classes import *
import os
import sys
import CRC



def convert_qb_file(qb_file, file_name, file_headers, console = "PC"):
    endian = console_endian[console]
    consoleType = console_lookup[console]
    qb_node_lookup = qb_type_lookup[console]
    # print(qb_node_lookup)
    qb_filesize = qb_file.getFilesize()

    node_type = lambda: read_node(qb_node_lookup, qb_file)
    read_int_bytes = lambda a = 4: qb_file.readBytes(a)
    read_dbg_bytes = lambda a = 4: get_dbg_name(qb_file, a)
    test_count = 55
    count = 0
    test_run = 0
    section_list = []
    if test_run: # Set test to 1 to print more details and let you step through a qb file per section header if you wish
        # Please see production code below for comments
        while test_count != count:
            while qb_file.getPosition() < qb_filesize:
                section_header = ["id", "pak_name"]
                section_header_2 = ["data_start", "next_item"]
                section_entry = qb_section(node_type())

                for x in section_header:
                    if x == "id":
                        dbg_name = read_dbg_bytes()
                        if type(dbg_name) == int:
                            if dbg_name in file_headers.values():
                                dbg_name = list(file_headers.keys())[list(file_headers.values()).index(dbg_name)]
                    else:
                        dbg_name = read_dbg_bytes()
                        if type(dbg_name) == int:
                            test_midname = f"songs/{file_name}.mid.qb"
                            if dbg_name == int(CRC.QBKey(test_midname), 16):
                                dbg_name = test_midname

                    setattr(section_entry, f"section_{x}", dbg_name)
                    # raise Exception
                for x in section_header_2:
                    setattr(section_entry, f"section_{x}", read_int_bytes())
                if section_entry.section_type != "SectionScript":
                    setattr(section_entry, f"section_data",
                            process_section_data(qb_file, section_entry, qb_node_lookup))
                    print(qb_file.getPosition())
                    print(vars(section_entry))
                    section_list.append(section_entry)
                else:
                    script_crc = hex(read_dbg_bytes())
                    setattr(section_entry, "script_crc", script_crc)
                    script_uncom_size = read_int_bytes()
                    setattr(section_entry, "script_uncom_size", script_uncom_size)
                    script_com_size = read_int_bytes()
                    setattr(section_entry, "script_com_size", script_com_size)
                    if script_com_size % 4 != 0:
                        script_com_size += (4 - (script_com_size % 4))
                    script_data = int.to_bytes(read_int_bytes(script_com_size), script_com_size, endian)
                    setattr(section_entry, f"section_data", script_data)
                    section_list.append(section_entry)
        raise Exception
    else: #Default code. Could probably put this in a function to reduce repetitive code, but I'm lazy to copy over the variables
        while qb_file.getPosition() < qb_filesize:
            section_header = ["id", "pak_name"]
            section_header_2 = ["data_start", "next_item"]
            section_entry = qb_section(node_type())
            # Go through the section header above and generate the id and pak name
            for x in section_header:
                if x == "id":
                    dbg_name = read_dbg_bytes()
                    if type(dbg_name) == int:
                        if dbg_name in file_headers.values():
                            dbg_name = list(file_headers.keys())[list(file_headers.values()).index(dbg_name)]
                else:
                    dbg_name = read_dbg_bytes()
                    if type(dbg_name) == int:
                        test_midname = f"songs/{file_name}.mid.qb"
                        if dbg_name == int(CRC.QBKey(test_midname),16):
                            dbg_name = test_midname

                setattr(section_entry, f"section_{x}", dbg_name)
                # raise Exception
            for x in section_header_2:
                setattr(section_entry, f"section_{x}", read_int_bytes())
            if section_entry.section_type != "SectionScript":
                setattr(section_entry, f"section_data", process_section_data(qb_file, section_entry, qb_node_lookup))
                # print(qb_file.getPosition())
                # print(vars(section_entry))
                section_list.append(section_entry)
            else:
                script_crc = hex(read_dbg_bytes())
                setattr(section_entry, "script_crc", script_crc)
                script_uncom_size = read_int_bytes()
                setattr(section_entry, "script_uncom_size", script_uncom_size)
                script_com_size = read_int_bytes()
                setattr(section_entry, "script_com_size", script_com_size)
                if script_com_size % 4 != 0:
                    script_com_size += (4 - (script_com_size % 4))
                script_data = int.to_bytes(read_int_bytes(script_com_size), script_com_size, endian)
                script_data = " ".join("{:02x}".format(c) for c in script_data)
                setattr(section_entry, f"section_data", script_data)
                section_list.append(section_entry)


    # raise Exception
    return section_list

def read_qb_file(qb_file):

    return

if __name__ == "__main__":
    orig_stdout = sys.stdout
    # if len(sys.argv) == 1:
    directory = f".\\input QB"
    for file in os.listdir(directory):
        if not file.endswith(".qb"):
            continue
        elif file.endswith(".mid.qb"):
            file_name = file[:-7]
            file_headers = createHeaderDict(file_name)
        else:
            file_name = file[:-3]
            file_headers = ""
        filename = os.path.join(directory, file)
        with open(filename, "rb") as f:
            qb_sections = convert_qb_file(qb_bytes(f.read()), file_name, file_headers)
        output_file = f'.\\output\\QB\\{file_name}.txt'
        dir_name = os.path.dirname(output_file)
        try:
            os.makedirs(dir_name)
        except:
            pass
        with open(output_file, "w") as f:
            sys.stdout = f
            print_qb_text_file(qb_sections)
            sys.stdout = orig_stdout
    """else:
        filename = sys.argv[1]
        if filename.endswith(".mid.qb"):
            file_name = os.path.basename(filename[:-7])
            file_headers = createHeaderDict(file_name)
        else:
            file_name = os.path.basename(filename[:-3])
            file_headers = ""
        with open(filename, "rb") as f:
            qb_sections = convert_qb_file(qb_bytes(f.read()), file_name, file_headers)
        dir_name = os.path.dirname(filename)
        output_file = dir_name + "\\" + file_name + ".txt"
        with open(output_file, "w") as f:
            sys.stdout = f
            print_qb_text_file(qb_sections)
            sys.stdout = orig_stdout"""

    """qb_test = f".\\extract\\PAK\\qb\\scripts\\guitar\\songlist.qb"
    qb_test = f".\\extract\\SONGS\\bullsonparade_song\\songs\\bullsonparade.mid.qb"
    if "SONGS" in qb_test:
        file_name = qb_test[qb_test.rfind("\\") + 1:qb_test.rfind(".mid")]
        file_headers = createHeaderDict(file_name)
    else:
        file_name = ""
        file_headers = ""
    with open(qb_test, 'rb') as f:
        qb_data = qb_bytes(f.read())
    mid_sections = main(qb_data, file_name, file_headers)
    print(f'qb_name = \"{mid_sections[0].section_pak_name}\"')
    print_qb_text_file(mid_sections)"""

    # raise Exception
