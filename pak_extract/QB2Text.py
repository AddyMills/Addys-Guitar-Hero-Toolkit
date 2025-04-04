from pak_definitions import *
from pak_functions import *
from pak_classes import *
from io import StringIO
import os
import sys


orig_stdout = sys.stdout
def print_to_var(text_qb):
    result = StringIO()
    orig_stdout = sys.stdout
    sys.stdout = result
    print_qb_text_file(text_qb)
    sys.stdout = orig_stdout
    qb_text = result.getvalue()
    return qb_text
def convert_qb_file(qb_file, file_name, file_headers, console = "PC"):
    endian = console_endian[console]
    consoleType = console_lookup[console]
    qb_node_lookup = qb_type_lookup[console]
    # print(qb_node_lookup)
    qb_filesize = qb_file.getFilesize()
    file_headers_hex = create_hex_headers(file_headers)
    node_type = lambda: read_node(qb_node_lookup, qb_file)
    read_int_bytes = lambda a = 4: qb_file.readBytes(a)
    read_dbg_bytes = lambda a = 4: get_dbg_name(qb_file, a)
    test_count = 55
    count = 0
    test_run = 0
    section_list = []
    while qb_file.getPosition() < qb_filesize:
        section_header = ["id", "pak_name"]
        section_header_2 = ["data_start", "next_item"]
        section_entry = qb_section(node_type())
        if section_entry.section_type == "Unknown":
            raise Exception
        # Go through the section header above and generate the id and pak name
        for x in section_header:
            dbg_name = read_dbg_bytes()
            if dbg_name.startswith("0x"):
                if dbg_name in file_headers_hex.keys():
                    dbg_name = file_headers_hex[dbg_name]


            setattr(section_entry, f"section_{x}", dbg_name)
            """if "performance" in dbg_name:
                print()"""
            # raise Exception
        for x in section_header_2:
            setattr(section_entry, f"section_{x}", read_int_bytes())
        if section_entry.section_type != "SectionScript":
            section_start = qb_file.getPosition()
            setattr(section_entry, f"section_data", process_section_data(qb_file, section_entry, qb_node_lookup))
            if section_entry.section_type.endswith("Struct"):
                section_entry.make_dict()
                #print()
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
    try:
        with open(output_file, "w") as f:
            if len(qb_sections) == 0:
                print(f"{os.path.basename(output_file)} is blank! Skipping...")
            else:
                sys.stdout = f
                print_qb_text_file(qb_sections)
                sys.stdout = orig_stdout
    except Exception as E:
        if os.path.isfile(output_file):
            os.remove(output_file)
        sys.stdout = orig_stdout
        raise E
    return

def main(file):
    file_strip = os.path.basename(file)
    if file_strip.endswith(".xen"):
        file_strip = file_strip[:-4]
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
        if not file.endswith(".qb.xen") and not file.endswith(".qb.ps2"):
            continue
        elif file.endswith(".mid.qb.xen") or file.endswith("mid.qb.ps2"):
            file_name = file[:-11]
        else:
            file_name = file[:-7]
        file_name_head = file_name
        if "." in file_name_head:
            file_name_head = file_name_head[:file_name_head.find(".")]
        if file_name_head.endswith("song_scripts"):
            file_name_head = file_name_head[:file_name_head.find("_song_scripts")]
        file_headers = createHeaderDict(file_name_head)
        filename = os.path.join(directory, file)
        if file.endswith("xen"):
            console = "PC"
        else:
            console = "PS2"
        with open(filename, "rb") as f:
            qb_sections = convert_qb_file(qb_bytes(f.read(), console_endian[console]), file_name, file_headers, console)
        output_file = f'.\\output\\QB\\{file_name}.txt'
        dir_name = os.path.dirname(output_file)
        try:
            os.makedirs(dir_name)
        except:
            pass
        output_qb_file(qb_sections, output_file)

    # raise Exception
