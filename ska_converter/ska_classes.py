import struct

"""
Flag 32-bit values
"""

TRANS_FLOAT_TIME = 1 << 32 # If set, translation values are in floats and overall simpler to parse
NO_SEP_TIME = 1 << 28 # If set, only 2 bytes for time, else 4
COMP_FLAGS = 1 << 23 # If set, compression flags exist in the time values
PARTIAL_ANIM = 1 << 19 # If set, the ska file has a partial anim footer
BIG_TIME = 1 << 8 # Time goes above 2047 if set


class ska_bytes:
    def __init__(self, ska, endian = r"big"):
        self.data = ska
        self.endian = endian
        self.read_header()
        self.quat_sizes = self.get_bone_size(self.bonesize_quat_pos)
        self.trans_sizes = self.get_bone_size(self.bonesize_trans_pos)

    def read_header(self):
        self.version = int.from_bytes(self.data[0x20:0x24], self.endian)
        if self.version == 0x48:
            # Header is 128 bytes long
            self.data_start = 0x80
            self.position = 0x08
            ska_order = ["file_size", "anim_offset", "null_offset", "bonepointers_offset", "partial_anim_offset",
                         "d_offset", "version", "flags"]
        elif self.version == 0x68:
            # Header is 256 bytes long
            self.data_start = 0x100
            self.position = 0x00
            ska_order = ["file_size", "anim_offset", "null_offset", "bonepointers_offset", "b_offset", "c_offset",
                         "partial_anim_offset", "d_offset",
                         "version", "flags"]
        else:
            raise TypeError(f"Unknown ska type {self.version} found.")

        for x in ska_order:
            setattr(self, x, self.readBytes())



        self.duration = self.readFloat()
        self.unk_byte = self.readBytes(1)
        setattr(self, "bone_count", self.readBytes(1))
        setattr(self, "unk_b",  self.readBytes(2))
        if self.version == 0x48:
            floats = 2
        else:
            floats = 4
        for vec in range(0, floats):
            float_pair = []
            for y in range(0, 4):
                float_pair.append(self.readFloat())
            setattr(self, f"float_pair_{vec}", float_pair.copy())
        setattr(self, "unk_c", self.readBytes(2))
        setattr(self, "custom_keys", self.readBytes(2))
        setattr(self, "customkey_pos", self.readBytes())
        setattr(self, "quat_pos", self.readBytes())
        setattr(self, "trans_pos", self.readBytes())
        setattr(self, "bonesize_quat_pos", self.readBytes())
        setattr(self, "bonesize_trans_pos", self.readBytes())
        self.setPosition(self.data_start)

    def get_bone_size(self, size_start):
        self.setPosition(size_start)
        bone_sizes = {}
        for x in range(0, self.bone_count):
            bone_sizes[x] = self.readBytes(2)

        return bone_sizes

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

    def readFloat(self, amount = 4):
        x = []
        currPlace = self.position
        for y in range(amount):  # Iterate through the x bytes that make up the starting number
            x.append(self.data[y + self.position])
            currPlace += 1
        xBytes = bytearray(x)
        self.position = currPlace
        x = struct.unpack(">f", xBytes)
        return x[0]

    def getEndian(self):
        return self.endian

    def getPosition(self):
        return self.position

    def setPosition(self, update_val):
        self.position = update_val
