class pak_header:
    def __init__(self, ext):
        self.extension = ext
        self.offset = 0
        self.filesize = 0
        self.context_checksum = 0
        self.full_name_checksum = 0
        self.no_ext_name_checksum = 0
        self.parent_object = 0
        self.flags = 0

class compressed_pak:
    def __init__(self, data, endian = "big"):
        self.data = data
        self.endian = endian
        self.last_chnk = 0
        self.position = 0

    def readBytes(self, amount=4):
        x = []
        currPlace = self.position
        for y in range(amount):  # Iterate through the x bytes that make up the starting number
            x.append(self.data[y + self.position])
            currPlace += 1
        xBytes = bytearray(x)
        self.position = currPlace
        x = int.from_bytes(xBytes, self.endian)
        return x

    def updateChnk(self, update):
        self.last_chnk = update

    def grabData(self, length):
        chunk_data = self.data[self.position:self.position+length]
        return chunk_data


    def getPosition(self):
        return self.position

    def setPosition(self, update_val):
        self.position = update_val

    def addToPos(self, add):
        self.position += add



class qb_bytes:
    def __init__(self, data, endian = "big"):
        self.data = data
        self.position = 28
        self.endian = endian

    def readBytes(self, amount = 4):
        x = []
        currPlace = self.position
        for y in range(amount):  # Iterate through the x bytes that make up the starting number
            x.append(self.data[y + self.position])
            currPlace += 1
        xBytes = bytearray(x)
        self.position = currPlace
        x = int.from_bytes(xBytes, self.endian)
        return x

    def getEndian(self):
        return self.endian

    def getFilesize(self):
        return int.from_bytes(self.data[4:8], self.endian)

    def getPosition(self):
        return self.position

    def setPosition(self, update_val):
        self.position = update_val


class qb_section:
    def __init__(self, section_type):
        self.section_type = section_type
        self.section_id = 0
        self.section_pak_name = 0
        self.section_data_start = 0
        self.section_next_item = 0
        self.section_data = 0

    def __str__(self):
        return f"{self.section_type} {self.section_id}"

    def set_new_id(self, new_id):
        self.section_id = new_id

    def set_pak_name(self, pak_name):
        self.section_pak_name = pak_name

    def set_data(self, qb_data):
        self.section_data = qb_data

    def set_all(self, id, qb_data, pak_name):
        self.set_new_id(id)
        self.set_data(qb_data)
        self.set_pak_name(pak_name)

    def set_array_node_type(self, node_type):
        self.array_node_type = node_type
        self.subarray_types = []
        self.section_data = []

    def swap_names(self, old_name, new_name):
        for x in vars(self):
            if type(getattr(self, x)) != str:
                continue
            if old_name in getattr(self, x):
                setattr(self, x, getattr(self, x).replace(old_name, new_name))

    def make_empty(self):
        self.section_type = "SectionArray"
        self.section_id = 0
        self.section_pak_name = 0
        self.section_data_start = 0
        self.section_next_item = 0
        self.section_data = [0, 0]
        self.array_node_type = "Floats"

    def make_dict(self):
        if "SectionStruct" in self.section_type:
            if type(self.section_data) == list:
                self.data_dict = {}
                for x in self.section_data:
                    if x.data_type.endswith("Struct"):
                        self.data_dict[x.data_id] = x.data_dict
                    elif x.data_type.endswith("Array"):
                        self.data_dict[x.data_id] = x.struct_data_array
                    elif x.data_type.endswith("ItemString"):
                        self.data_dict[x.data_id] = x.struct_data_string
                    elif x.data_type.endswith("StringW"):
                        self.data_dict[x.data_id] = x.struct_data_string_w
                    else:
                        self.data_dict[x.data_id] = x.data_value


class array_item:
    def __init__(self, array_type, item_count, list_start):
        self.array_type = array_type
        self.item_count = item_count
        self.list_start = list_start

    def __str__(self):
        return f"{self.array_type} containing {self.item_count} items"


class struct_header:
    def __init__(self, struct_header, data_start):
        self.struct_header = struct_header
        self.data_start = data_start

    def __str__(self):
        return f"Struct item"

    def set_game(self, game_type):
        self.game_type = game_type

class struct_item:
    def __init__(self, data_type, data_id, data_value, next_item):
        self.data_type = data_type
        self.data_id = data_id
        self.data_value = data_value
        self.next_item = next_item
        self.data_dict = {}
        if data_type == "StructItemStruct":
            self.struct_data_struct = data_value
        elif data_type == "StructItemString":
            self.struct_data_string = data_value
        elif data_type == "StructItemArray":
            self.struct_data_array = data_value
            self.struct_data_array_type = "ArrayStruct"
            self.subarray_types = 0

    def __str__(self):
        if self.data_type == "StructItemStruct":
            return f"{self.data_id} {self.data_dict}"
        elif self.data_type == "StructItemArray":
            return f"{self.data_type} {self.data_id} with {len(self.struct_data_array)} items"
        else:
            return f"{self.data_type} {self.data_value}"

    def make_dict(self):
        if "struct_data_struct" in self.__dict__:
            if type(self.struct_data_struct) != struct_header:
                for x in self.struct_data_struct:
                    if x.data_type.endswith("Struct"):
                        self.data_dict[x.data_id] = x.data_dict
                    elif x.data_type.endswith("Array"):
                        self.data_dict[x.data_id] = x.struct_data_array
                    elif x.data_type.endswith("ItemString"):
                        self.data_dict[x.data_id] = x.struct_data_string
                    elif x.data_type.endswith("StringW"):
                        self.data_dict[x.data_id] = x.struct_data_string_w
                    else:
                        self.data_dict[x.data_id] = x.data_value
        elif self.data_type == "StructHeader":
            if type(self.data_value) != struct_header:
                for x in self.data_value:
                    if x.data_type.endswith("Struct"):
                        self.data_dict[x.data_id] = x.data_dict
                    elif x.data_type.endswith("Array"):
                        self.data_dict[x.data_id] = x.struct_data_array
                    elif x.data_type.endswith("ItemString"):
                        self.data_dict[x.data_id] = x.struct_data_string
                    elif x.data_type.endswith("StringW"):
                        self.data_dict[x.data_id] = x.struct_data_string_w
                    else:
                        self.data_dict[x.data_id] = x.data_value

    def reprocess_dict(self):
        for ind, item in enumerate(self.data_dict):
            if self.data_type == 'StructHeader':
                curr_data = self.data_value[ind]
            elif self.data_type == 'StructItemStruct':
                curr_data = self.struct_data_struct[ind]
            else:
                raise Exception("Data Type not yet implemented for reprocessing. Please contact me")
            data_check = curr_data.data_type
            if data_check == 'StructItemInteger' or data_check == 'StructItemQbKey':
                if self.data_dict[item] != curr_data.data_value:
                    curr_data.data_value = self.data_dict[item]
            elif type(self.data_dict[item]) == dict:
                curr_data.reprocess_dict()
            else:
                raise Exception("Data Type not yet implemented for reprocessing. Please contact me")
        # print()

    def make_empty_array(self):
        self.data_type = "StructItemArray"
        self.data_value = [0]
        self.struct_data_array = [0]
        self.struct_data_array_type = "Floats"

    def set_string_w(self, stringw):
        self.struct_data_string_w = stringw



class script_item:
    def __init__(self, uncom_size, com_size, data):
        self.uncom_size = 0
        self.com_size = 0
        self.data = 0