from pak_classes import *
from pak_definitions import *
from dbg import checksum_dbg as dbg

import CRC
import struct


def readFourBytes(file, start, endian="big"):
    x = []
    currPlace = start
    for y in range(4):  # Iterate through the 4 bytes that make up the starting number
        x.append(file[y + start])
        currPlace += 1
    xBytes = bytearray(x)
    x = int.from_bytes(xBytes, endian)
    return x, currPlace


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

    for x in others:
        headers.append(f"{filename}{x}")

    for x in headers:
        headerDict[x] = int(CRC.QBKey(x), 16)

    return headerDict


def read_node(node_lookup, qb_file):
    return qb_node_list[node_lookup.index(qb_file.readBytes())]


def get_dbg_name(qb_file, length=4):
    x = qb_file.readBytes(length)
    try:
        debug_name = dbg[x]
    except:
        debug_name = hex(x)
    return debug_name


def read_qb_item(qb_file, item_type):
    read_int_bytes = lambda a=4: qb_file.readBytes(a)
    read_dbg_bytes = lambda a=4: get_dbg_name(qb_file, a)
    if item_type.endswith("QbKey"):
        return read_dbg_bytes()
    elif item_type.endswith("QbKeyString"):
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
                if count % 2 != 0:
                    qb_file.readBytes(2)
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
                trash = qb_file.readBytes(4 - qb_modulo)
                # raise Exception
                break
            skinny_string += chr(char)
        return skinny_string
    elif item_type.endswith("Struct"):
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
                subarray = array_item(node_type(), read_int_bytes(), read_int_bytes())
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
                # raise Exception
        else:
            item_start = read_int_bytes()
            qb_file.setPosition(item_start)
            array_struct_header = struct_header(node_type(), read_int_bytes())
            subarray_data = process_struct_data(qb_file, array_struct_header, qb_node_lookup)
            array_data.append(struct_item("StructHeader", 0, subarray_data, 0))
    elif array_type in simple_array_types:
        for x in range(0, array_node.item_count):
            array_data.append(str(read_qb_item(qb_file, array_node.array_type)))
    else:
        raise Exception("Unknown Array Type found")
    return array_data, subarrays


def process_section_data(qb_file, section_entry, qb_node_lookup):
    node_type = lambda: read_node(qb_node_lookup, qb_file)
    read_int_bytes = lambda a=4: qb_file.readBytes(a)
    read_dbg_bytes = lambda a=4: get_dbg_name(qb_file, a)
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
                section_data, subarrays = process_array_data(qb_file, array_item(array_node_type, item_count, list_start),
                                                  qb_node_lookup)
            else:
                list_start = read_int_bytes()
                section_data, subarrays = process_array_data(qb_file, array_item(array_node_type, item_count, list_start),
                                              qb_node_lookup)
            setattr(section_entry, "subarray_types", subarrays)
    elif section_type.endswith("Struct"):
        section_data = process_struct_data(qb_file, struct_header(node_type(), read_int_bytes()), qb_node_lookup)
    elif section_type.endswith("Integer"):
        # raise Exception
        section_data = section_entry.section_data_start
        return section_data-(2**32) if section_data >= 2**31 else section_data
    else:
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
            data_id = read_dbg_bytes()
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
                # raise Exception
            elif data_type[len("StructItem"):] == "String":
                struct_data_string = read_qb_item(qb_file, data_type)
                qb_file.setPosition(next_item)
                setattr(struct_entry, "struct_data_string", struct_data_string)
                # raise Exception
            elif data_type[len("StructItem"):] == "StringW":
                struct_data_string_w = read_qb_item(qb_file, data_type)
                setattr(struct_entry, "struct_data_string_w", struct_data_string_w)
            elif data_type[len("StructItem"):] == "Float":
                byte_order = qb_file.getEndian()
                float_bytes = int.to_bytes(int(struct_entry.data_value,16), 4, byte_order)
                setattr(struct_entry, "data_value",
                        struct.unpack(f'{">" if byte_order == "big" else "<"}f', float_bytes)[0])
            elif data_type[len("StructItem"):] == "Array":
                array_node_type = node_type()
                array_item_count = read_int_bytes()
                if array_item_count == 1:
                    array_list_start = qb_file.getPosition()
                    raise Exception
                else:
                    array_list_start = read_int_bytes()
                struct_array = process_array_data(qb_file, array_item(array_node_type, array_item_count, array_list_start), qb_node_lookup)[0]
                setattr(struct_entry, "struct_data_array", struct_array)
                setattr(struct_entry, "struct_data_array_type", array_node_type)
                # raise Exception
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
                #print_array_data()
                array_type = item.struct_data_array_type
                print_array_data(item.struct_data_array, array_type, "", id_string, indent + 1)
                """if len(item.struct_data_array) > 3:
                    print(f"{indent_val}{id_string} = [")
                    for x in item.struct_data_array:
                        print(f"{indent_val}\t{output_item_data(x, array_type)},")
                    print(f"{indent_val}]")
                else:
                    array_string = ""
                    for y, x in enumerate(item.struct_data_array):
                        array_string += f"{output_item_data(x, array_type)}"
                        if y != len(item.struct_data_array) - 1:
                            array_string += ", "
                    print(f"{indent_val}{id_string}", f"= [{array_string}]")"""
                # raise Exception
            else:
                print(f"{indent_val}{id_string}",
                      f'= {"$" if item.data_type.endswith("QbKeyString") else ""}{item.data_value}')
    else:
        print_struct_data(item, indent)

    return

def print_array_data(array_data, array_type, sub_array = "", id_string = "", indent = 0):
    indent_val = '\t' * indent
    if sub_array == 1:
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
            print(f"{print_array_data(x, sub_array[y], 1, '', indent + 1)}{',' if y != len(array_data) - 1 else ''}")
        print(f"{indent_val}]")
    elif array_type.endswith("Struct"):
        print(f"{indent_val}{id_string} = [")
        for y, x in enumerate(array_data):
            print(f"{indent_val}\t" + "{")
            for z in x.data_value:
                print_struct_item(z, indent + 2)
            print(f"{indent_val}\t" + "}" + f"{',' if y != len(array_data) - 1 else ''}")
            # raise Exception
        print(f"{indent_val}]")
        # raise Exception
    elif len(array_data) > 3:
        print(f"{indent_val}{id_string} = [")
        for y, x in enumerate(array_data):
            print(f"{indent_val}\t{output_item_data(x, array_type)}{',' if y != len(array_data)-1 else ''}")
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
        for x in struct.struct_data_struct:
            print_struct_item(x, indent + 1)
        print(f"{indent_val}" + "}")
    else:
        print_struct_item(struct, indent)

    return

def output_item_data(item_data, item_type, endian = "big"):
    simple_data = ["Integer", "Float", "QbKey"]
    for x in simple_data:
        if item_type.endswith(x):
            return item_data
    if item_type.endswith("QbKeyString"):
        return f"${item_data}"
    elif item_type.endswith("String") or item_type.endswith("StringW"):
        return f'{"w" if item_type.endswith("StringW") else ""}\"{item_data}\"'

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
            if x.section_data == [0, 0]:
                print(f'{x.section_id} = [Empty]')
            else:
                print_array_data(x.section_data, array_type, x.subarray_types, x.section_id, 0)
            """elif array_type == int or array_type == list:
                if len(x.section_data) > 3:
                    print(f'{x.section_id} = [')
                    for y in x.section_data:
                        print(f"\t{y},")
                    print(']')
                else:
                    print(f'{x.section_id} = {x.section_data}')
            elif array_type == struct_item:
                print(x.section_id, "= [")
                for y in x.section_data:
                    print("\t{")
                    for z in y.data_value:
                        print_struct_item(z, 2)
                    print("\t},")
                print("]")
            else:
                print(
                    f'{x.section_id} = [' + (", ".join(x.section_data) if x.section_data != [0, 0] else "Empty") + "]")"""
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
        elif x.section_type == "SectionScript":
            print("script", f"{x.section_id} = \"{x.section_data}\"")
        else:
            raise Exception("Found a section type not yet supported. Please go bug me, AddyMills, to implement it!")

    return


def print_qb_text_file_old(mid_sections):
    for x in mid_sections:
        if x.section_type == "SectionArray":
            print("SectionArray", f'{x.section_id} =', (x.section_data if x.section_data != [0, 0] else "Empty"))

        elif x.section_type == "SectionStruct":
            print("SectionStruct", x.section_id, "= {")
            if type(x.section_data) == struct_header:
                print("\tEmpty")
            else:
                for y in x.section_data:
                    if type(y) == struct_item:
                        print_struct_item(y, 1)
            print("}")
        elif x.section_type == "SectionScript":
            print(x.section_type, x.section_id)

    return
