from CRC import QBKey as qb_key
import struct
from pak_definitions import console_lookup, console_endian, qbNodeHeaders
import os

class qb_string:
    def __init__(self, qb_data):
        self.qb_data = qb_data
        self.counter = 0

    def curr_char(self):
        curr_char = self.qb_data[self.counter]
        self.counter += 1
        return curr_char

    def skip_data(self, amount):
        self.counter += amount

    def data_length(self):
        return len(self.qb_data)

    def end_of_data(self):
        if self.counter < self.data_length():
            return False
        else:
            return True


class basic_data:
    def __init__(self, id_name, item_data):
        self.id_name = id_name
        self.item_data = item_data

    def __str__(self):
        return f"{self.id_name}: {self.item_data}"

    def set_type(self, qb_type):
        self.qb_type = qb_type

    def set_bin_data(self, bin_data):
        self.bin_data = bin_data

    def set_array_type(self, array_type):
        self.array_type = array_type

    def set_subarray_types(self, subarray_types):
        self.subarray_types = subarray_types

    def set_qb_name(self, qb_name):
        self.qb_name = qb_name

class script_data:
    def __init__(self, id_name, script_data):
        self.id_name = id_name
        self.script_data = script_data
        self.qb_type = "Script"

    def __str__(self):
        return f"{self.id_name}: {self.script_data}"

class struct_data:
    def __init__(self):
        self.data_type = "Struct"
        self.data = []

    def add_data(self, var_name, var_data):
        self.data.append(basic_data(var_name, var_data))

    def set_name(self, sect_name):
        self.sect_name = sect_name

    def __str__(self):
        return f"Struct container with {len(self.data)} items"


def parse_array(qb_string):
    array_data = []
    while True:
        if qb_string.end_of_data():
            break
        array_entry = read_data(qb_string)
        if type(array_entry) == list:
            array_data.append(array_entry)
        else:
            if array_entry.strip() == "":
                pass
            elif array_entry.strip() == "{":
                array_data.append(parse_struct(qb_string))
            elif array_entry.endswith("]"):
                if array_entry != "]":
                    array_data.append(array_entry[:-1])
                break
            else:
                array_data.append(array_entry)
    # raise Exception

    return array_data


def parse_script(qb_string):
    var_name = read_data(qb_string)
    quotes = 0
    script_info = ""
    while quotes < 2:
        curr_data = qb_string.curr_char()
        if curr_data == "\"":
            quotes += 1
        else:
            script_info += curr_data
    script_info = script_info.split()
    script_bytes = bytearray()
    for x in script_info:
        script_bytes += int.to_bytes(int(x,16),1,"big")
    if len(script_bytes) % 4 != 0:
        script_bytes += b'\x00' * (4 - len(script_bytes) % 4)
    # raise Exception

    return script_data(var_name, script_bytes)


def parse_struct(qb_string):
    struct_item = struct_data()
    while True:
        var_name = read_data(qb_string)
        if var_name == "}":
            break
        elif var_name == "Empty":
            read_data(qb_string)
            break
        var_data = read_data(qb_string)
        if var_data == "{":
            struct_item.add_data(var_name, parse_struct(qb_string))
        else:
            struct_item.add_data(var_name, var_data)

    return struct_item

def read_data(qb_string, array_mode = False): # Read until next whitespace and return the result
    parsed_data = ""
    string_mode = False
    is_string = False
    wide_string = False
    special_chars = [" ", ",", "["]
    while True:
        if qb_string.end_of_data():
            break
        curr_char = qb_string.curr_char()
        if curr_char not in special_chars:
            if curr_char == "\"":
                string_mode = not string_mode
                if string_mode:
                    is_string = True
                    if parsed_data.startswith("w"):
                        wide_string = True
                    parsed_data = ""
            else:
                parsed_data += curr_char
        elif string_mode:
            parsed_data += curr_char
        elif curr_char == "[":
            parsed_data = parse_array(qb_string)
            break
        else:
            break
    if is_string:
        if wide_string:
            parsed_data = f'w\"{parsed_data}\"'
            w_string = bytearray()
            """for x in parsed_data:
                w_string += int.to_bytes(0, 1, "big")
                w_string += bytearray(x, "latin-1")"""
            # raise Exception
        else:
            parsed_data = f'\"{parsed_data}\"'
            # parsed_data = bytearray(parsed_data, "latin-1")




    return parsed_data

def parse_data(to_parse):
    qb_name = ""
    sections = []

    # print(len(line_items))

    len_data = to_parse.data_length()
    # print(to_parse)
    while True:
        if to_parse.end_of_data():
            break
        var_name = read_data(to_parse)
        if var_name == "script":
            sections.append(parse_script(to_parse))
            continue
        if var_name.strip() == "":
            continue
        var_data = read_data(to_parse)
        if var_name == "qb_file":
            qb_name = var_data
            continue
        if var_data == "{":
            sections.append(basic_data(var_name, parse_struct(to_parse)))

            # break
        else:
            sections.append(basic_data(var_name, var_data))
            # break
    if qb_name == "":
        raise Exception("No qb file name found. Please add it to the beginning of your text file.")

    return qb_name, sections

def num_type(x):
    if "." in x:
        return "Float"
    else:
        return "Integer"

def find_type(x):
    if type(x) == str:
        if x == "Empty":
            return "Floats"
        elif x.startswith("w\""):
            return "StringW"
        elif x.startswith("\""):
            return "String"
        elif x.startswith("0x"):
            return "QbKey"
        elif x[0].isnumeric():
            return num_type(x)
        elif x.startswith("-"):
            return num_type(x[1:])
        elif x.startswith("$"):
            return "QbKeyString"
        else:
            return "QbKey"
    else:
        # raise Exception
        if type(x) == struct_data:
            return "Struct"
        else:
            raise Exception
    return None

def assign_data(data_type, raw_data, endian = "big"):
    if data_type == "StringW":
        bin_data = bytearray()
        for y in raw_data[2:-1]:
            bin_data += ord(y).to_bytes(2, endian)
        bin_data += b'\x00' * 2
        if len(bin_data) % 4 != 0:
            bin_data += b'\x00' * (4 - len(bin_data) % 4)
    elif data_type == "String":
        bin_data = bytearray(raw_data[1:-1], 'latin-1')
        bin_data += b'\x00'
        if len(bin_data) % 4 != 0:
            bin_data += b'\x00' * (4 - len(bin_data) % 4)
    elif data_type == "QbKey":
        bin_data = conv_key(raw_data, endian)
    elif data_type == "QbKeyHex":
        bin_data = conv_key(raw_data, endian)
        # raise Exception
    elif data_type == "QbKeyString":
        bin_data = conv_key(raw_data[1:], endian)
        # bin_data = conv_key(qb_key(raw_data[1:]))
    elif data_type == "QbKeyStringHex":
        # bin_data = int.to_bytes(int(raw_data, 16), 4, endian)
        bin_data = conv_key(raw_data[3:], endian)
    elif data_type == "Float":
        bin_data = struct.pack(f'{">" if endian == "big" else "<"}f', float(raw_data))
    elif data_type == "Integer":
        try:
            bin_data = int.to_bytes(int(raw_data), 4, endian)
        except OverflowError:
            bin_data = int.to_bytes(int(raw_data)+2**32, 4, endian)
    elif data_type == "Floats":
        bin_data = b'\x00' * 8


    else:
        bin_data = b''
    return bin_data

def assign_types(sections, endian = "big"):

    for x in sections:
        if type(x) == basic_data:
            if type(x.item_data) == struct_data:
                x.set_type("Struct")
                assign_types(x.item_data.data)
            elif type(x.item_data) == str:
                x.set_type(find_type(x.item_data))
                x.set_bin_data(assign_data(x.qb_type, x.item_data, endian))
            elif type(x.item_data) == list:
                x.set_type("Array")
                if type(x.item_data[0]) == list:
                    x.set_array_type("Array")
                    subarray_types = []
                    subarray_bin_data = []
                    for y in x.item_data:
                        item_bin_data = []
                        subarray_item = find_type(y[0])
                        subarray_types.append(subarray_item)
                        if subarray_item == struct_data:
                            assign_types(y.data)
                        x.set_subarray_types(subarray_types)
                        for z in y:
                            item_bin_data.append(assign_data(subarray_item, z, endian))
                        subarray_bin_data.append(item_bin_data.copy())
                    x.set_bin_data(subarray_bin_data)
                    # raise Exception
                else:
                    x.set_array_type(find_type(x.item_data[0]))
                    array_bin_data = []
                    for y in x.item_data:
                        if type(y) == struct_data:
                            assign_types(y.data)
                        else:
                            array_bin_data.append(assign_data(x.array_type, y, endian))
                    x.set_bin_data(array_bin_data)

    return

def bin_type(a, b): # Combine names to look up qb item types
    return a + b

def to_bin(a, b=4, c="big"): # Create a 4-byte anything
    return int.to_bytes(a, b, c)

def update_pos(a, b, c, d=0): # Update the position of the current byte in the binary file
    return a + len(b) + len(c) + d

def get_node(a, b = "PC"): # Pull the hex value of the item type
    return qbNodeHeaders[a][console_lookup[b]]

def conv_key(a, endian):
    if a.startswith("0x"):
        return int.to_bytes(int(a, 16), 4, endian)
    else:
        return int.to_bytes(int(qb_key(a), 16), 4, endian)


def output_bin_data(x, curr_pos, endian = "big", console = "PC"):
    item_bin = bytearray()
    return_data = ["String", "StringW"]
    if x.qb_type == "Array":
        item_bin += bin_array_data(x, curr_pos)
    elif x.qb_type == "Struct":
        item_bin += bin_struct_data(x.item_data.data, curr_pos, endian, console)
    elif x.qb_type in return_data:
        return x.bin_data
    else:
        raise Exception

    return item_bin

def bin_struct_data(item_data, curr_pos, endian = "big", console = "PC"):
    struct_bytes = bytearray()
    struct_bytes += to_bin(get_node("StructHeader", console))
    if not item_data:
        struct_bytes += to_bin(0)  # First item = 0 to indicate an empty struct
    else:
        easy_struct = ["Float", "Integer", "QbKey", "QbKeyString"]
        first_item = curr_pos + len(struct_bytes) + 4
        struct_bytes += to_bin(first_item)  # First item of the struct
        for j, i in enumerate(item_data):
            item_type = bin_type("StructItem", i.qb_type)
            struct_bytes += to_bin(get_node(item_type, console))
            struct_item_id = i.id_name if i.id_name != "no_id" else 0
            if struct_item_id == 0:
                struct_bytes += to_bin(0)
            else:
                struct_bytes += conv_key(i.id_name, endian) # Add CRC of item id
            if i.qb_type not in easy_struct:
                if i.qb_type == "Struct":
                    substruct_start = first_item + len(struct_bytes)
                    struct_bytes += to_bin(substruct_start, 4, endian)
                    substruct_data = bin_struct_data(i.item_data.data, substruct_start, endian, console)
                    struct_next = substruct_start + len(substruct_data) if j + 1 != len(item_data) else 0
                    struct_bytes += to_bin(struct_next, 4, endian)
                    struct_bytes += substruct_data
                    # break # raise Exception
                elif i.qb_type == "Array":
                    array_start = first_item + len(struct_bytes)
                    struct_bytes += to_bin(array_start, 4, endian)
                    array_bytes = bin_array_data(i, array_start)
                    array_next = array_start + len(array_bytes) if j + 1 != len(item_data) else 0
                    struct_bytes += to_bin(array_next, 4, endian)
                    struct_bytes += array_bytes
                    # raise Exception
                elif "String" in i.qb_type:
                    if "StringPointer" in i.qb_type:
                        raise Exception
                    item_start = first_item + len(struct_bytes)
                    struct_bytes += to_bin(item_start, 4, endian)
                    struct_bytes += to_bin(item_start + len(i.bin_data) if j + 1 != len(item_data) else 0, 4, endian)
                    struct_bytes += i.bin_data
                    # raise Exception
                else:
                    raise Exception
            else:

                # struct_bytes += to_bin(get_node(item_type, console))

                struct_bytes += i.bin_data
                struct_next = curr_pos + len(struct_bytes) + 4 if j + 1 != len(item_data) else 0
                struct_bytes += to_bin(struct_next)
    return struct_bytes

def bin_array_data(array_data, curr_pos, console = "PC"):
    array_bytes = bytearray()
    easy_arrays = ["Integer", "QbKey", "QbKeyString"]
    complex_arrays = ["Array", "Struct"]
    bin_array_type = bin_type(array_data.qb_type, array_data.array_type)
    if array_data.array_type != "Floats":
        array_bytes += to_bin(get_node(bin_array_type, console))  # Add Array type in bytes
        item_count = len(array_data.item_data)
        """if item_count == 1:
            raise Exception"""
        array_bytes += to_bin(item_count)  # Add item count of array items
        """if item_count != 1:"""
        # array_bytes += to_bin(curr_pos + len(array_bytes) + 4) # Start of list, To offset the 4 bytes
        # raise Exception
        if array_data.array_type in easy_arrays:
            if item_count != 1:
                array_bytes += to_bin(curr_pos + len(array_bytes) + 4)  # Start of list, To offset the 4 bytes
            for z in array_data.bin_data:
                array_bytes += z
        elif array_data.array_type in complex_arrays:
            array_bytes += to_bin(curr_pos + len(array_bytes) + 4)  # Start of list, To offset the 4 bytes
            fake_pos = curr_pos + len(array_bytes)
            fake_pos += len(array_data.item_data)*4
            subarray_positions = []
            subarray_data = bytearray()
            if array_data.array_type == "Array":
                for y, x in enumerate(array_data.bin_data):
                    # raise Exception
                    subarray_positions.append(fake_pos)
                    if item_count != 1:
                        array_bytes += to_bin(fake_pos, 4, console_endian[console])
                    else:
                        fake_pos -= 4
                    fake_data = basic_data(0,x)
                    fake_data.set_type(array_data.array_type)
                    fake_data.set_array_type(array_data.subarray_types[y])
                    fake_data.set_bin_data(x)

                    subarray_bytes = bin_array_data(fake_data, fake_pos, console)
                    fake_pos += len(subarray_bytes)
                    subarray_data += subarray_bytes
            elif array_data.array_type == "Struct":
                for y, x in enumerate(array_data.item_data):
                    subarray_positions.append(fake_pos)
                    if item_count != 1:
                        array_bytes += to_bin(fake_pos, 4, console_endian[console])
                    else:
                        fake_pos -= 4
                    subarray_bytes = bin_struct_data(x.data, fake_pos, console_endian[console], console)
                    fake_pos += len(subarray_bytes)
                    subarray_data += subarray_bytes
                    # raise Exception
            array_bytes += subarray_data
            # raise Exception


        else:
            raise Exception
    else:
        array_bytes += to_bin(get_node("Floats"))
        array_bytes += array_data.bin_data[0]

    # raise Exception

    return array_bytes

def create_qb(sections, section_type, qb_name, endian = "big", console = "PC"):
    qbFileHeader = b'\x1C\x08\x02\x04\x10\x04\x08\x0C\x0C\x08\x02\x04\x14\x02\x04\x0C\x10\x10\x0C\x00'
    qb_pos = 28
    qb_bytes = bytearray()
    all_bytes = bytearray()
    all_bytes += to_bin(0)
    no_value_pointer = ["Integer"]
    testing = 0
    item_test = 54
    for y, x in enumerate(sections):
        section_bytes = bytearray() # Bytearray for the section
        node_type = bin_type(section_type, x.qb_type)
        section_bytes += to_bin(get_node(node_type, console)) # Add the node in bytes
        section_bytes += conv_key(x.id_name, endian) # Add CRC of item id
        section_bytes += conv_key(qb_name, endian) # Add CRC of file name
        if x.qb_type in no_value_pointer:
            section_bytes += x.bin_data
            section_bytes += to_bin(0)  # This is the "next item" but is always 0 I believe
            # raise Exception
        else:
            section_bytes += to_bin(update_pos(qb_pos, qb_bytes, section_bytes, 8)) # Add when the data starts
            section_bytes += to_bin(0) # This is the "next item" but is always 0 I believe

            curr_pos = update_pos(qb_pos, qb_bytes, section_bytes)

            if "Script" not in node_type:
                section_bytes += output_bin_data(x, curr_pos, endian, console)
            else:
                section_bytes += x.script_data

        qb_bytes += section_bytes
        if testing:
            if y == item_test:
                break

    all_bytes += to_bin(28 + len(qb_bytes))
    all_bytes += qbFileHeader
    all_bytes += qb_bytes
    # raise Exception

    return all_bytes

def strip_but_not_quotes(text_data):
    to_replace = "xxxxyyyyzzzz"
    text_data_alt = text_data
    strings = {}
    read_string = ""
    counter = 0
    string_mode = False
    for x in text_data:
        if x == "\"":
            string_mode = not string_mode
            if string_mode == False:
                if read_string != "":
                    substitute = f"{to_replace}_{counter}"
                    strings[substitute] = read_string
                    text_data_alt = text_data_alt.replace(read_string, substitute, 1)
                    read_string = ""
                    counter += 1

        else:
            if string_mode:
                read_string += x

    # raise Exception

    return text_data_alt, strings


def main(line_items, console = "PC", endian = "big"):

    stripped_string, strings = strip_but_not_quotes(line_items)
    # Need to remove all strings so that when it's stripped, any double/triple/etc. spaces remain
    stripped_string = " ".join(stripped_string.split()).replace(" = ", " ")

    for x in strings.keys(): # This adds the strings back into the file
        stripped_string = stripped_string.replace(x, strings[x], 1)
    # raise Exception
    to_parse = qb_string(stripped_string)
    qb_name, sections = parse_data(to_parse)
    assign_types(sections, endian)
    qb_file = create_qb(sections, "Section", qb_name, endian, console)


    return qb_file




if __name__ == "__main__":
    directory = f".\\input Text"
    console = "PC"
    endian = "big"
    for file in os.listdir(directory):
        if not file.endswith(".txt"):
            continue
        filename = os.path.join(directory, file)
        file_name = file[:-4]
        with open(filename, "r") as f:
            lines = f.read()
        output_file = f'.\\output\\Text\\{file_name}.qb'
        dir_name = os.path.dirname(output_file)
        try:
            os.makedirs(dir_name)
        except:
            pass
        qb_file = main(lines, console, endian)
        with open(output_file, 'wb') as f:
            f.write(qb_file)