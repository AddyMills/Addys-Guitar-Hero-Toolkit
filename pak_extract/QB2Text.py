from pak_definitions import *
from pak_functions import *
from pak_classes import *
import os
import sys
import CRC

orig_stdout = sys.stdout

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
    if test_run: # Set test_run to 1 to print more details and let you step through a qb file per section header if you wish
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
                script_data = bytearray()
                script_crc = int.to_bytes(read_int_bytes(), 4, endian)
                setattr(section_entry, "script_crc", script_crc)
                script_uncom_size = read_int_bytes()
                setattr(section_entry, "script_uncom_size", script_uncom_size)
                script_com_size = read_int_bytes()
                setattr(section_entry, "script_com_size", script_com_size)
                script_data += script_crc
                script_data += int.to_bytes(script_uncom_size, 4, endian)
                script_data += int.to_bytes(script_com_size, 4, endian)

                script_data += int.to_bytes(read_int_bytes(script_com_size), script_com_size, endian)
                if script_com_size % 4 != 0:
                    offset_amount = (4 - (script_com_size % 4))
                    read_int_bytes(offset_amount)
                script_data = " ".join("{:02x}".format(c) for c in script_data)
                setattr(section_entry, f"section_data", script_data)

                section_list.append(section_entry)
            count += 1
                # raise Exception


    # raise Exception
    return section_list

def output_qb_file(qb_sections, output_file):
    with open(output_file, "w") as f:
        sys.stdout = f
        print_qb_text_file(qb_sections)
        sys.stdout = orig_stdout
    return

def main(file):
    file_strip = os.path.basename(file)
    if not file_strip.endswith(".qb"):
        raise Exception("Not a valid file. File must be a QB file.")
    elif file_strip.endswith(".mid.qb"):
        file_name = file_strip[:-7]
        file_name_qb = file_strip[:-3]
        file_headers = createHeaderDict(file_name)
    else:
        file_name = file_strip[:-3]
        file_name_qb = file_strip[:-3]
        file_headers = createHeaderDict(file_name)
    # filename = os.path.join(directory, file)
    with open(file, "rb") as f:
        qb_sections = convert_qb_file(qb_bytes(f.read()), file_name, file_headers)

    return qb_sections, file_name_qb


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
            file_headers = createHeaderDict(file_name)
        filename = os.path.join(directory, file)
        with open(filename, "rb") as f:
            qb_sections = convert_qb_file(qb_bytes(f.read()), file_name, file_headers)
        output_file = f'.\\output\\QB\\{file_name}.txt'
        dir_name = os.path.dirname(output_file)
        try:
            os.makedirs(dir_name)
        except:
            pass
        output_qb_file(qb_sections, output_file)

    # raise Exception
