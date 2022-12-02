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
        self.pak_name = pak_name

    def set_data(self, qb_data):
        self.section_data = qb_data

    def set_array_node_type(self, node_type):
        self.array_node_type = node_type
        self.subarray_types = []

    def make_empty(self):
        self.section_type = "SectionArray"
        self.section_id = 0
        self.section_pak_name = 0
        self.section_data_start = 0
        self.section_next_item = 0
        self.section_data = [0, 0]
        self.array_node_type = "Floats"

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

class struct_item:
    def __init__(self, data_type, data_id, data_value, next_item):
        self.data_type = data_type
        self.data_id = data_id
        self.data_value = data_value
        self.next_item = next_item

    def __str__(self):
        if self.data_type == "StructItemStruct":
            return
        else:
            return f"{self.data_type} {self.data_value}"

    def set_string_w(self, stringw):
        self.struct_data_string_w = stringw

class script_item:
    def __init__(self, uncom_size, com_size, data):
        self.uncom_size = 0
        self.com_size = 0
        self.data = 0