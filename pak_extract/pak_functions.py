import sys

sys.path.append("../")

from pak_classes import *
from pak_definitions import *

from dbg import checksum_dbg as dbg
from copy import deepcopy

import CRC
import struct

float_round = 15

def round_time(entry):
    # return entry
    time_trunc = int(str(entry).zfill(6)[-2:])
    if time_trunc == 0 or time_trunc == 33 or time_trunc == 67:
        new_time = entry
    elif time_trunc == 99:
        new_time = entry + 1
    elif time_trunc < 33:
        new_time = int(str(entry)[:-2] + str(33))
    elif time_trunc < 67:
        new_time = int(str(entry)[:-2] + str(67))
    else:
        new_time = int(str(entry)[:-2] + str(99)) + 1
    return new_time

def round_cam_len(length_val):
    if str(length_val)[-1] == "4":
        length_val -= 1
    elif str(length_val)[-1] == "6":
        length_val += 1
    return length_val

def readFourBytes(file, start, endian="big"):
    x = []
    currPlace = start
    for y in range(4):  # Iterate through the 4 bytes that make up the starting number
        x.append(file[y + start])
        currPlace += 1
    xBytes = bytearray(x)
    x = int.from_bytes(xBytes, endian)
    return x, currPlace

def readxBytes(file, start, to_read, endian="big"):
    x = []
    currPlace = start
    for y in range(to_read):  # Iterate through the 4 bytes that make up the starting number
        x.append(file[y + start])
        currPlace += 1
    xBytes = bytes(x)
    # x = int.from_bytes(xBytes, endian)
    return xBytes, currPlace

def createHeaderDict(filename):
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
        for z in face_off:
            if x == "":
                headers.append(f"{filename}_{z}")
            else:
                headers.append(f"{filename}_{x}_{z}")

    for x in others:
        headers.append(f"{filename}{x}")

    for x in others_wt:
        headers.append(f"{filename}{x}")

    for x in markers_wt:
        headers.append(f"{filename}{x}")

    for x in drum_wt:
        for y in difficulties:
            headers.append(f"{filename}_{y}_{x}")

    for x in vocals_wt:
        headers.append(f"{filename}_vocals{x}")

    headers.append(f"{filename}_song_vocals")
    headers.append(f"{filename}_lyrics")

    for x in songs_folder:
        headers.append(f"songs/{filename}{x}")

    for x in anims_pre:
        headers.append(f"{x}{filename}")

    for x in headers:
        int_val = int(CRC.QBKey(x), 16)
        headerDict[x] = hex(int_val)

    return headerDict


def create_hex_headers(header_dict):
    file_headers_hex = {}
    for x in header_dict.keys():
        file_headers_hex[header_dict[x]] = x
    return file_headers_hex


def read_node(node_lookup, qb_file):
    return qb_node_list[node_lookup.index(qb_file.readBytes())]


def pull_dbg_name(reference):
    try:
        debug_name = dbg[reference]
        if " " in debug_name:
            debug_name = f"`{debug_name}`"
    except:
        debug_name = hex(reference)
    return debug_name


def get_dbg_name(qb_file, length=4):
    x = qb_file.readBytes(length)
    debug_name = pull_dbg_name(x)
    return debug_name


def read_qb_item(qb_file, item_type):
    read_int_bytes = lambda a=4: qb_file.readBytes(a)
    read_dbg_bytes = lambda a=4: get_dbg_name(qb_file, a)
    endian = qb_file.endian
    unpack_floats = lambda: \
        struct.unpack(f'{">" if endian == "big" else "<"}f', int.to_bytes(read_int_bytes(), 4, endian))[0]
    if item_type.endswith("QbKey"):
        return read_dbg_bytes()
    elif "QbKeyString" in item_type:
        return read_dbg_bytes()
    elif item_type.endswith("Integer"):
        return read_int_bytes()
    elif item_type.endswith("StringW"):
        count = 0
        wide_string = ""
        while True:
            count += 1
            char = qb_file.readBytes(2)
            if char == 0:
                qb_modulo = qb_file.getPosition() % 4
                if qb_modulo != 0:
                    qb_file.readBytes(4 - qb_modulo)
                break
            wide_string += chr(char)
        return wide_string
    elif item_type.endswith("String"):
        count = 0
        skinny_string = ""
        while True:
            count += 1
            char = qb_file.readBytes(1)
            if char == 0:
                qb_modulo = qb_file.getPosition() % 4
                if qb_modulo != 0:
                    qb_file.readBytes(4 - qb_modulo)
                # raise Exception
                break
            skinny_string += chr(char)
        return skinny_string
    elif item_type.endswith("Struct"):
        raise Exception
    elif "FloatsX" in item_type:
        float_header = read_int_bytes()
        if float_header != 0x00010000:
            raise Exception
        if item_type.endswith("X2"):
            floats = []
            for x in range(2):
                floats.append(round(unpack_floats(), float_round))
            floats = tuple(floats)
            # raise Exception
        elif item_type.endswith("X3"):
            floats = []
            for x in range(3):
                floats.append(round(unpack_floats(), float_round))
            floats = tuple(floats)
            # raise Exception
        else:
            raise Exception("Unknown float structure found. Contact me to implement it.")
        return floats
    elif item_type.endswith("Float"):
        float_val = round(unpack_floats(), float_round)
        return float_val
    else:
        raise Exception
    return


def process_array_data(qb_file, array_node, qb_node_lookup):
    node_type = lambda: read_node(qb_node_lookup, qb_file)
    read_int_bytes = lambda a=4: qb_file.readBytes(a)
    # print(array_node.array_type)
    array_type = array_node.array_type
    # print(array_node.array_type)
    # print(qb_file.getPosition())
    array_data = []
    subarrays = []

    if array_type.endswith("Array"):
        offsets = []
        if array_node.item_count > 1:
            for x in range(array_node.item_count):
                offsets.append(read_int_bytes())
            for x in offsets:
                qb_file.setPosition(x)
                subarray_type = node_type()
                if subarray_type == "Floats":
                    # print("Floats test")
                    read_int_bytes()
                    read_int_bytes()
                    sub_item_count = 1
                else:
                    sub_item_count = read_int_bytes()
                if sub_item_count > 1:
                    list_start = read_int_bytes()
                else:
                    list_start = qb_file.position
                subarray = array_item(subarray_type, sub_item_count, list_start)
                """if subarray.item_count == 1:
                    print("Subarray with one item")"""
                array_data.append(process_array_data(qb_file, subarray, qb_node_lookup)[0])
                subarrays.append(subarray.array_type)
        else:
            item_start = read_int_bytes()
            qb_file.setPosition(item_start)
            # raise Exception
            subarray = array_item(node_type(), read_int_bytes(), read_int_bytes())
            array_data.append(process_array_data(qb_file, subarray, qb_node_lookup)[0])
            subarrays.append(subarray.array_type)
            # raise Exception
    elif array_type.endswith("Integer"):
        for x in range(0, array_node.item_count):
            array_data.append(read_qb_item(qb_file, array_node.array_type))
    elif array_type.endswith("Struct"):
        offsets = []
        if array_node.item_count > 1:
            for x in range(array_node.item_count):
                offsets.append(read_int_bytes())
            for x in offsets:
                qb_file.setPosition(x)
                array_struct_header = struct_header(node_type(), read_int_bytes())
                subarray_data = process_struct_data(qb_file, array_struct_header, qb_node_lookup)
                # array_data += subarray_data
                array_data.append(struct_item("StructHeader", 0, subarray_data, 0))
                array_data[-1].make_dict()
                # raise Exception
        else:
            item_start = read_int_bytes()
            qb_file.setPosition(item_start)
            array_struct_header = struct_header(node_type(), read_int_bytes())
            subarray_data = process_struct_data(qb_file, array_struct_header, qb_node_lookup)
            array_data.append(struct_item("StructHeader", 0, subarray_data, 0))
            array_data[-1].make_dict()
    elif array_type in simple_array_types:
        """if array_node.item_count == 1:
            print("Simple array with one item")"""
        for x in range(0, array_node.item_count):
            array_data.append(str(read_qb_item(qb_file, array_node.array_type)))
    elif "String" in array_type:
        if "QbKeyString" in array_type:
            raise Exception
        if array_type.endswith("Pointer"):
            raise Exception
        offsets = []
        if array_type.endswith("StringW"):
            to_read = 2
        else:
            to_read = 1
        if array_node.item_count > 1:
            for x in range(array_node.item_count):
                offsets.append(read_int_bytes())
            for x in offsets:
                string_val = ""
                qb_file.setPosition(x)
                curr_char = -1
                while curr_char != 0:
                    curr_char = qb_file.readBytes(to_read)
                    if curr_char != 0:
                        string_val += chr(curr_char)
                array_data.append(string_val)
        else:
            string_val = ""
            item_start = read_int_bytes()
            qb_file.setPosition(item_start)
            curr_char = -1
            while curr_char != 0:
                curr_char = qb_file.readBytes(to_read)
                if curr_char != 0:
                    string_val += chr(curr_char)
            array_data.append(string_val)
            # raise Exception
        if qb_file.position % 4 != 0:
            qb_file.readBytes(4 - qb_file.position % 4)
            # raise Exception
    elif "FloatsX" in array_type:
        offsets = []
        if array_node.item_count > 1:
            for x in range(array_node.item_count):
                offsets.append(read_int_bytes())
            for x in offsets:
                qb_file.setPosition(x)
                floats_entry = read_qb_item(qb_file, array_type)
                array_data.append(floats_entry)
                # subarrays.append(subarray.array_type)
                # raise Exception
        else:
            item_start = read_int_bytes()
            qb_file.setPosition(item_start)
            floats_entry = read_qb_item(qb_file, array_type)
            array_data.append(floats_entry)
            raise Exception
    elif array_type == "Floats":
        array_data = [0]
        # print("Float test")
    else:
        raise Exception("Unknown Array Type found")
    return array_data, subarrays


def process_section_data(qb_file, section_entry, qb_node_lookup):
    node_type = lambda: read_node(qb_node_lookup, qb_file)
    read_int_bytes = lambda a=4: qb_file.readBytes(a)
    read_dbg_bytes = lambda a=4: get_dbg_name(qb_file, a)
    endian = qb_file.endian
    # print(section_entry.section_type)
    section_type = section_entry.section_type
    if section_type.endswith("Array"):
        array_node_type = node_type()
        setattr(section_entry, "array_node_type", array_node_type)
        if array_node_type == "Floats":
            section_data = [read_int_bytes(), read_int_bytes()]
        else:
            item_count = read_int_bytes()
            if item_count == 1:
                list_start = 0
                section_data, subarrays = process_array_data(qb_file,
                                                             array_item(array_node_type, item_count, list_start),
                                                             qb_node_lookup)
            else:
                list_start = read_int_bytes()
                section_data, subarrays = process_array_data(qb_file,
                                                             array_item(array_node_type, item_count, list_start),
                                                             qb_node_lookup)
            setattr(section_entry, "subarray_types", subarrays)
    elif section_type.endswith("Struct"):
        section_data = process_struct_data(qb_file, struct_header(node_type(), read_int_bytes()), qb_node_lookup)
    elif section_type.endswith("Integer"):
        # raise Exception
        section_data = section_entry.section_data_start
        return section_data - (2 ** 32) if section_data >= 2 ** 31 else section_data
    elif section_type.endswith("Float"):
        section_data = round(struct.unpack(f'{">" if endian == "big" else "<"}f',
                                           int.to_bytes(section_entry.section_data_start, 4, endian))[0], float_round)
        return section_data
    elif "QbKey" in section_type:
        section_data = pull_dbg_name(section_entry.section_data_start)
        return section_data
    else:
        # raise Exception
        section_data = read_qb_item(qb_file, section_type)
    return section_data


def process_struct_data(qb_file, struct_node, qb_node_lookup):
    node_type = lambda: read_node(qb_node_lookup, qb_file)
    read_int_bytes = lambda a=4: qb_file.readBytes(a)
    read_dbg_bytes = lambda a=4: get_dbg_name(qb_file, a)
    if struct_node.data_start == 0:
        return struct_node
    else:
        struct_data = []
        while True:
            data_type = node_type()
            if data_type.startswith("Array"):  # This is impossible, so it must be a new type of qb
                struct_node.set_game("GHWT")
                data_type = "StructItem" + data_type[5:]
            else:
                struct_node.set_game("GH3")
            data_id = read_dbg_bytes()
            """Test Here"""
            if "String" in data_type:
                if not data_type.endswith("QbKeyString"):
                    data_value = read_int_bytes()
                    # raise Exception
                else:
                    data_value = read_dbg_bytes()
                    # raise Exception
            elif "Integer" in data_type:
                data_value = read_int_bytes()
            else:
                data_value = read_dbg_bytes()
            next_item = read_int_bytes()
            struct_entry = struct_item(data_type, data_id, data_value, next_item)
            if data_type.endswith("Struct"):
                struct_data_struct = process_struct_data(qb_file, struct_header(node_type(), read_int_bytes()),
                                                         qb_node_lookup)
                setattr(struct_entry, "struct_data_struct", struct_data_struct)
                struct_entry.make_dict()
                # raise Exception
            elif data_type[len("StructItem"):] == "String":
                struct_data_string = read_qb_item(qb_file, data_type)
                if next_item != 0:
                    qb_file.setPosition(next_item)
                setattr(struct_entry, "struct_data_string", struct_data_string)
                # raise Exception
            elif data_type[len("StructItem"):] == "StringW":
                struct_data_string_w = read_qb_item(qb_file, data_type)
                setattr(struct_entry, "struct_data_string_w", struct_data_string_w)
            elif data_type[len("StructItem"):] == "Float":
                byte_order = qb_file.getEndian()
                float_bytes = int.to_bytes(int(struct_entry.data_value, 16), 4, byte_order)
                setattr(struct_entry, "data_value",
                        round(struct.unpack(f'{">" if byte_order == "big" else "<"}f', float_bytes)[0], float_round))
            elif data_type[len("StructItem"):] == "Array":
                array_node_type = node_type()
                array_item_count = read_int_bytes()
                if array_item_count == 1:
                    array_list_start = qb_file.getPosition()
                    # raise Exception
                else:
                    array_list_start = read_int_bytes()
                struct_array, subarrays = process_array_data(qb_file, array_item(array_node_type, array_item_count,
                                                                                 array_list_start), qb_node_lookup)
                setattr(struct_entry, "struct_data_array", struct_array)
                setattr(struct_entry, "struct_data_array_type", array_node_type)
                setattr(struct_entry, "subarray_types", subarrays)
                # raise Exception
            elif data_type[len("StructItem"):] == "FloatsX2":
                struct_data_floats = read_qb_item(qb_file, data_type)
                setattr(struct_entry, "struct_data_floats", struct_data_floats)
            elif data_type[len("StructItem"):] == "FloatsX3":
                struct_data_floats = read_qb_item(qb_file, data_type)
                setattr(struct_entry, "struct_data_floats", struct_data_floats)
                # raise Exception
            elif data_type[len("StructItem"):] == "StringPointer":
                raise Exception
            else:
                pass
            struct_data.append(struct_entry)
            if next_item == 0:
                break
        # setattr(struct_node, "struct_data", )
        # raise Exception
    return struct_data


def print_struct_item(item, indent=0):
    if item.data_type != "StructItemStruct":
        indent_val = '\t' * indent
        if item.data_id.startswith("0x"):
            id_string = "no_id" if int(item.data_id, 16) == 0 else item.data_id
        else:
            id_string = item.data_id
        if "StructItemString" in item.data_type:
            if item.data_type.endswith("StringW"):
                item_data = item.struct_data_string_w
            else:
                item_data = item.struct_data_string
            print(f"{indent_val}{id_string}", f'= {"w" if item.data_type.endswith("StringW") else ""}\"{item_data}\"')
        else:
            if item.data_type == "StructItemArray":
                # print_array_data()
                array_type = item.struct_data_array_type
                print_array_data(item.struct_data_array, array_type, item.subarray_types, id_string, indent)
            elif "FloatsX" in item.data_type:
                print(f"{indent_val}{id_string} = {item.struct_data_floats}")
                # raise Exception
            elif "Integer" in item.data_type:
                int_val = item.data_value
                print(f"{indent_val}{id_string}",
                      f'= {int_val - (2 ** 32) if int_val >= 2 ** 31 else int_val}')
            elif "QbKey" in item.data_type:
                """if item.data_type.endswith('Qs'):
                    print("Qs test")"""
                print(f"{indent_val}{id_string}",
                      f"= {'$' if item.data_type.endswith('String') else 'qbs(' if item.data_type.endswith('Qs') else ''}{hex(item.data_value) if item.data_type.endswith('Qs') else item.data_value}{')' if item.data_type.endswith('Qs') else ''}")
            elif "0x" not in str(item.data_value):
                print(f"{indent_val}{id_string}",
                      f'= {item.data_value}')

            else:
                raise Exception
    else:
        print_struct_data(item, indent)

    return


def print_array_data(array_data, array_type, sub_array="", id_string="", indent=0):
    indent_val = '\t' * indent
    if sub_array == 1 and not array_type.endswith("Struct"):
        array_string = f"{indent_val}["
        for y, x in enumerate(array_data):
            array_string += f"{output_item_data(x, array_type)}"
            if y != len(array_data) - 1:
                array_string += ", "
        # print(f"{indent_val}{id_string}", f"= [{array_string}]")
        return array_string + "]"
    elif array_type.endswith("Array"):
        print(f"{indent_val}{id_string} = [")
        for y, x in enumerate(array_data):
            """if not type(sub_array) == str:
                print("test")"""
            if sub_array[y].endswith("Struct"):
                print(f"{indent_val}\t[")
                # raise Exception
                for s_count, struct in enumerate(array_data[y]):
                    print(f"{indent_val}\t\t" + "{")
                    for items in struct.data_value:
                        print_struct_item(items, indent + 3)
                    print(f"{indent_val}\t\t" + "}" + f"{',' if s_count != len(array_data[y]) - 1 else ''}")
                print(f"{indent_val}\t]" + f"{',' if y != len(array_data) - 1 else ''}")
                # raise Exception
            else:
                print(
                    f"{print_array_data(x, sub_array[y], 1, '', indent + 1)}{',' if y != len(array_data) - 1 else ''}")
        print(f"{indent_val}]")
    elif array_type.endswith("Struct"):
        """if sub_array:
            print(f"{indent_val}[")
        else:"""
        print(f"{indent_val}{id_string} = [")
        for y, x in enumerate(array_data):
            print(f"{indent_val}\t" + "{")
            if type(x.data_value) == struct_header:
                print(f"{indent_val}\t\tEmpty")
            else:
                for z in x.data_value:
                    print_struct_item(z, indent + 2)
            print(f"{indent_val}\t" + "}" + f"{',' if y != len(array_data) - 1 else ''}")
            # raise Exception
        print(f"{indent_val}]")
        # raise Exception
    elif len(array_data) > 3:
        print(f"{indent_val}{id_string} = [")
        for y, x in enumerate(array_data):
            print(f"{indent_val}\t{output_item_data(x, array_type)}{',' if y != len(array_data) - 1 else ''}")
        print(f"{indent_val}]")
    else:
        array_string = ""
        for y, x in enumerate(array_data):
            array_string += f"{output_item_data(x, array_type)}"
            if y != len(array_data) - 1:
                array_string += ", "
        print(f"{indent_val}{id_string}", f"= [{array_string}]")

    return


def print_struct_data(struct, indent=0):
    if "struct_data_struct" in vars(struct):
        indent_val = '\t' * indent
        print(f"{indent_val}{struct.data_id} = " + "{")
        if type(struct.struct_data_struct) == struct_header:
            print(f"{indent_val}\tEmpty")
        else:
            for x in struct.struct_data_struct:
                print_struct_item(x, indent + 1)
        print(f"{indent_val}" + "}")
    else:
        print_struct_item(struct, indent)

    return


def output_item_data(item_data, item_type, endian="big"):
    simple_data = ["Float"]
    for x in simple_data:
        if item_type.endswith(x):
            return item_data
    if "QbKey" in item_type:
        """if item_type.endswith('Qs'):
            print("Qs test")"""
        test_data = f"{'$' if item_type.endswith('String') else 'qbs(' if item_type.endswith('Qs') else ''}{item_data}{')' if item_type.endswith('Qs') else ''}"
        # raise Exception
        return test_data
    if item_type.endswith("QbKeyString"):
        return f"${item_data}"
    elif item_type.endswith("QbKeyStringQs"):
        return f"qbs({item_data})"
    elif item_type.endswith("String") or item_type.endswith("StringW"):
        return f'{"w" if item_type.endswith("StringW") else ""}\"{item_data}\"'
    elif "FloatsX" in item_type:
        return item_data
        # raise Exception
    elif "Integer" in item_type:
        int_val = item_data - (2 ** 32) if item_data >= 2 ** 31 else item_data
        return int_val
    elif item_type.endswith("Floats"):
        return "Empty"
    else:
        raise Exception(f"Unknown data type {item_type} found. Please bug me to implement it!")


def find_array_type(array_data):
    return


def print_qb_text_file(mid_sections):
    print(f"qb_file = {mid_sections[0].section_pak_name}")
    for x in mid_sections:
        if x.section_type == "SectionArray":
            array_type = x.array_node_type
            # raise Exception
            if x.section_data == [0, 0] and "Floats" in x.array_node_type:
                print(f'{x.section_id} = [Empty]')
            else:
                try:
                    subarray_types = x.subarray_types
                except:
                    subarray_types = []
                print_array_data(x.section_data, array_type, subarray_types, x.section_id, 0)
        elif x.section_type == "SectionStruct":
            print(x.section_id, "= {")
            if type(x.section_data) == struct_header:
                print("\tEmpty")
            else:
                for y in x.section_data:
                    if type(y) == struct_item:
                        print_struct_item(y, 1)
            print("}")
        elif x.section_type == "SectionInteger":
            print(f"{x.section_id} = {x.section_data}")
        elif x.section_type == "SectionString" or x.section_type == "SectionStringW":
            print(f"{x.section_id} = {'w' if x.section_type == 'SectionStringW' else ''}\"{x.section_data}\"")
        elif x.section_type == "SectionFloat":
            print(f"{x.section_id} = {x.section_data}")
        elif "FloatsX" in x.section_type:
            print(f"{x.section_id} = {x.section_data}")
        elif "QbKey" in x.section_type:
            print(
                f"{x.section_id} = {'$' if x.section_type.endswith('String') else 'qbs(' if x.section_type.endswith('Qs') else ''}{x.section_data}{')' if x.section_type.endswith('Qs') else ''}")
        elif x.section_type == "SectionScript":
            print("script", f"{x.section_id} = \"{x.section_data}\"")
        else:
            raise Exception("Found a section type not yet supported. Please go bug me, AddyMills, to implement it!")

    return

def new_lipsync(time, instrument, ska_file):
    params_list = []
    params_list.append(struct_item("StructItemQbKey", "name", instrument, 0))
    params_list.append(struct_item("StructItemQbKey", "anim", ska_file, 0))
    params = struct_item("StructItemStruct", "params", params_list, 0)
    scr = struct_item("StructItemQbKey", "scr", "Band_PlayFacialAnim", 0)
    time = struct_item("StructItemInteger", "time", time, 0)
    lipsync = struct_item("StructHeader", 0, [time, scr, params], 0)
    return lipsync

def new_facial_anim_gh5(time, instrument, face_type):
    params_list = []
    params_list.append(struct_item("StructItemQbKey", "name", instrument, 0))
    params_list.append(struct_item("StructItemString", "fa_type", face_type, 0))
    params = struct_item("StructItemStruct", "params", params_list, 0)
    scr = struct_item("StructItemQbKey", "scr", "Band_ChangeFacialAnims", 0)
    time = struct_item("StructItemInteger", "time", time, 0)
    facial_anim = struct_item("StructHeader", 0, [time, scr, params], 0)
    return facial_anim

def new_facial_anim_gh5_gender(time, instrument, face_anims):
    params_list = []
    params_list.append(struct_item("StructItemQbKey", "name", instrument, 0))
    params_list.append(struct_item("StructItemQbKey", "ff_anims", face_anims[0], 0))
    params_list.append(struct_item("StructItemQbKey", "mf_anims", face_anims[1], 0))
    params = struct_item("StructItemStruct", "params", params_list, 0)
    scr = struct_item("StructItemQbKey", "scr", "Band_ChangeFacialAnims", 0)
    time = struct_item("StructItemInteger", "time", time, 0)
    facial_anim = struct_item("StructHeader", 0, [time, scr, params], 0)
    return facial_anim

def new_play_loop(time, instrument, anim_type=0):
    params_list = []
    params_list.append(struct_item("StructItemQbKey", "name", instrument, 0))
    if anim_type:
        params_list.append(struct_item("StructItemQbKey", "male", f"{anim_type}", 0))
        params_list.append(struct_item("StructItemQbKey", "female", f"{anim_type}_F", 0))
    params = struct_item("StructItemStruct", "params", params_list, 0)
    scr = struct_item("StructItemQbKey", "scr", "Band_PlayLoop", 0)
    time = struct_item("StructItemInteger", "time", time, 0)
    play_loop = struct_item("StructHeader", 0, [time, scr, params], 0)

    return play_loop

def new_play_clip(time, clip, start, end = 0):
    params_list = []
    params_list.append(struct_item("StructItemQbKey", "clip", clip, 0))
    params_list.append(struct_item("StructItemInteger", "startframe", start, 0))
    if end:
        params_list.append(struct_item("StructItemInteger", "endframe", end, 0))
    params_list.append(struct_item("StructItemInteger", "timefactor", 1, 0))
    params = struct_item("StructItemStruct", "params", params_list, 0)
    scr = struct_item("StructItemQbKey", "scr", "Band_PlayClip", 0)
    time = struct_item("StructItemInteger", "time", time, 0)
    play_clip = struct_item("StructHeader", 0, [time, scr, params], 0)

    return play_clip

def make_script_struct(script_data, to_round = True):
    final_struct = struct_data()
    if to_round:
        time = basic_data("time", round_time(script_data.time))
    else:
        time = basic_data("time", script_data.time)
    time.set_type("Integer")
    if to_round:
        time.set_bin_data(struct.pack(">i", round_time(script_data.time)))
    else:
        time.set_bin_data(struct.pack(">i", script_data.time))
    scr = basic_data("scr", script_data.type)
    scr.set_type("QbKey")
    scr.set_bin_data(bytes.fromhex(CRC.QBKey(script_data.type)))
    params_struct = struct_data()
    params_list = []
    for x in script_data.data:
        params_list.append(basic_data(x["param"], x["data"]))
        param_type = x["type"]
        params_list[-1].set_type(param_type)
        if param_type == "Float":
            params_list[-1].set_bin_data(struct.pack(">f", x["data"]))
        elif param_type == "Integer":
            params_list[-1].set_bin_data(struct.pack(">i", x["data"]))
        elif param_type == "QbKey":
            params_list[-1].set_bin_data(bytes.fromhex(CRC.QBKey(x["data"])))
    params_struct.add_multiple_basic(params_list)
    params = basic_data("params", params_struct)
    final_struct.add_multiple_basic([time, scr, params])
    return final_struct

def camera_band_clip(cameras):
    cameras_qb = []
    for x in cameras:
        slot = struct_item("StructItemInteger", "slot", x["slot"], 0)
        name = struct_item("StructItemString", "name", x["name"], 0)
        anim = struct_item("StructItemQbKey", "anim", x["anim"], 0)
        cameras_qb.append(struct_item("StructHeader", 0, [slot, name, anim], 0))
    camera_array = struct_item("StructItemArray", "cameras", cameras_qb, 0)
    return camera_array

def force_all_to_idle(time):
    time = struct_item("StructItemInteger", "time", time, 0)
    scr = struct_item("StructItemQbKey", "scr", "Band_ForceAllToIdle", 0)

    idle_script = struct_item("StructHeader", 0, [time, scr], 0)
    return idle_script

def new_band_clip_gh5(char_class):
    char_type = {"name": "StructItemQbKey", "startnode": "StructItemString", "anim": "StructItemQbKey",
                 "startframe": "StructItemInteger", "endframe": "StructItemInteger", "timefactor": "StructItemInteger",
                 "ik_targetl": "StructItemQbKey", "ik_targetr": "StructItemQbKey", "strum": "StructItemQbKey",
                 "fret": "StructItemQbKey", "chord": "StructItemQbKey"}
    char_array = []
    for x in ["name", "startnode", "anim", "startframe", "endframe", "timefactor", "ik_targetl", "ik_targetr", "strum",
              "fret", "chord"]:
        if not getattr(char_class, x):
            pass
            """if x != "endframe" and x != "anim":
                char_array.append(struct_item(char_type[x], x, getattr(char_class, x), 0))"""
        else:
            char_array.append(struct_item(char_type[x], x, getattr(char_class, x), 0))

    return char_array

def new_stance_gh3(name, stance, anim_type, *args):
    param_name = {"param": "name", "data": name, "type": "QbKey"}
    param_stance = {"param": anim_type, "data": stance, "type": "QbKey"}
    new_stance = [param_name, param_stance]
    if "cycle" in args:
        new_stance.append({"param": "no_id", "data": "cycle", "type": "QbKey"})
    if "no_wait" in args:
        new_stance.append({"param": "no_id", "data": "no_wait", "type": "QbKey"})
    if "repeat" in args:
        new_stance.append({"param": "repeat_count", "data": int(args[args.index("repeat")+1]), "type": "Integer"})
    return new_stance




# LZSS code

RINGBUFFERSIZE = 4096
MATCHLIMIT = 18
THRESHOLD = 2


def write_out(x, p_out):
    p_out.append(x)
    return p_out


def read_into(p_in, decode_len):
    if decode_len == 0:
        return None, decode_len
    decode_len -= 1
    return p_in.pop(0), decode_len


def decode_lzss(p_in, p_out, decode_len):
    r = RINGBUFFERSIZE - MATCHLIMIT
    flags = 0
    while True:
        if (flags >> 1) & 256 == 0:
            c, decode_len = read_into(p_in, decode_len)
            if c is None:
                break
            flags = c | 0xff00
        if flags & 1:
            c, decode_len = read_into(p_in, decode_len)
            if c is None:
                break
            p_out = write_out(c, p_out)
            r = (r + 1) % RINGBUFFERSIZE
        else:
            i, decode_len = read_into(p_in, decode_len)
            j = p_in.pop(0)
            i |= ((j & 0xf0) << 4)
            j = (j & 0x0f) + THRESHOLD
            for k in range(j + 1):
                c = p_out[(i + k) % RINGBUFFERSIZE]
                p_out = write_out(c, p_out)
                r = (r + 1) % RINGBUFFERSIZE
    return p_out
