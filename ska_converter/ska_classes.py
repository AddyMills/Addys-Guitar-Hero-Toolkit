import struct

"""
Flag 32-bit values
"""

TRANS_FLOAT_TIME = 1 << 31 # If set, translation values are in floats and overall simpler to parse
NO_SEP_TIME = 1 << 28 # If set, only 2 bytes for time, else 4
COMP_FLAGS = 1 << 23 # If set, compression flags exist in the time values
PARTIAL_ANIM = 1 << 19 # If set, the ska file has a partial anim footer
BIG_TIME = 1 << 8 # Time goes above 2047 if set
SINGLE_FRAME = 1 << 6 # Single anim frames.


class ska_bytes:
    def __init__(self, ska, endian = r"big"): # Assumes all ska files are big
        self.debug = 0
        self.bone_count = 0
        self.flags = 0
        self.quat_pos = 0
        self.trans_pos = 0
        self.bonesize_quat_pos = 0
        self.bonesize_trans_pos = 0
        self.pointerblock_offset = 0
        self.custom_keys = 0
        self.partial_bones = 0
        self.data = ska
        self.endian = endian
        self.big_time = 0
        self.pointerframes = {}


        self.read_header()
        self.quat_sizes = self.get_bone_size(self.bonesize_quat_pos)
        self.trans_sizes = self.get_bone_size(self.bonesize_trans_pos)
        self.comp_bits = self.flags & COMP_FLAGS
        if self.flags & PARTIAL_ANIM:
            self.partial_anim()
        if self.flags & SINGLE_FRAME:
            self.quat_frames = self.read_single(self.quat_pos, self.quat_sizes)
            self.trans_frames = self.read_single(self.trans_pos, self.trans_sizes)
        else:
            self.quat_frames = self.read_quats()
            self.trans_frames = self.read_trans()
        if self.custom_keys:
            self.custom_key_data = self.read_custom_keys()
        if self.pointerblock_offset > 0 and self.pointerblock_offset < len(self.data):
            self.read_pointer_block()



    def read_header(self):
        self.version = int.from_bytes(self.data[0x20:0x24], self.endian)
        if self.version == 0x48: # GH3 and GHA style headers
            # Header is 128 bytes long
            self.data_start = 0x80
            self.position = 0x08
            ska_order = ["file_size", "anim_offset", "null_offset", "pointerblock_offset", "partial_anim_offset",
                         "d_offset", "version", "flags"]
        elif self.version == 0x68: # GHWT and up style headers
            # Header is 256 bytes long
            self.data_start = 0x100
            self.position = 0x00
            ska_order = ["file_size", "anim_offset", "null_offset", "pointerblock_offset", "b_offset", "c_offset",
                         "partial_anim_offset", "d_offset",
                         "version", "flags"]
        else:
            raise TypeError(f"Unknown ska type {self.version} found.")

        for x in ska_order:
            setattr(self, x, self.readBytes())

        if self.flags & BIG_TIME:
            self.big_time = 1
            
        if self.flags & COMP_FLAGS:
            self.compressed = 1
        else:
            self.compressed = 0

        self.duration = self.readFloat()
        self.duration_frames_60 = round(self.duration * 60)
        self.duration_frames_30 = round(self.duration * 30)
        self.unk_byte = self.readBytes(1)
        setattr(self, "bone_count", self.readBytes(1))
        if self.bone_count == 128 and self.version == 0x48:
            self.ska_source = "steve"
        elif self.bone_count == 128:
            self.ska_source = "wt_rocker"
        elif self.bone_count == 125:
            self.ska_source = "gh3_guitarist"
        elif self.bone_count == 121:
            self.ska_source = "gh3_singer"
        elif self.bone_count == 118:
            self.ska_source = "gha_singer"
        elif self.bone_count == 115:
            self.ska_source = "dmc_singer"
        elif self.bone_count <= 3 and not (self.flags & PARTIAL_ANIM):
            self.ska_source = "camera"
        else:
            self.ska_source = "other"
        setattr(self, "quat_changes",  self.readBytes(2)) # Total # of quaternion changes in file
        if self.version == 0x48:
            floats = 2
        else:
            floats = 4
        self.float_pairs = []
        for vec in range(0, floats):
            float_pair = []
            for y in range(0, 4):
                float_pair.append(self.readFloat())
            self.float_pairs.append(float_pair.copy())
            setattr(self, f"float_pair_{vec}", float_pair.copy())
        setattr(self, "trans_changes", self.readBytes(2))
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
        if amount == 0:
            return 0
        start = self.position
        end = start + amount
        self.position = end
        bytes_ = self.data[start:end]
        return int.from_bytes(bytes_, byteorder=self.endian)

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

    def partial_anim(self):
        self.position = self.partial_anim_offset
        self.partial_bone_count = self.readBytes()
        self.partial_bin = []
        self.partial_bones = []
        for x in range(4):
            unk = bin(self.readBytes())[2:].zfill(32)
            self.partial_bin.append(unk)
            for y in range(32):
                if unk[y] == "1":
                    bone_num = ((32 - y) + (32*x)) - 1
                    if bone_num < self.bone_count:
                        self.partial_bones.append(bone_num)
        self.partial_bones.sort()
        return

    def read_single(self, pos, bone_sizes):
        if pos == 0:
            return
        self.setPosition(pos)
        frames = {}
        for bone in range(self.bone_count):
            if bone_sizes[bone] == 0:
                continue
            bone_ref = 0
            bone_check = bone_sizes[bone]
            while bone_ref < bone_check:
                x_val, y_val, z_val, w_val = self.readFloat(), self.readFloat(), self.readFloat(), self.readFloat()
                bone_ref += 16

            frames[bone] = [x_val, y_val, z_val, w_val].copy()
        return frames



    def read_quats(self):
        if self.quat_pos == 0:
            return
        NEG_W = 1 << 15
        COMP_FLAG = 1 << 14
        COMP_X = 1 << 13
        COMP_Y = 1 << 12
        COMP_Z = 1 << 11
        self.setPosition(self.quat_pos)
        if self.flags & COMP_FLAGS:
            if self.flags & NO_SEP_TIME or not self.flags & BIG_TIME:
                time_a = 0 # Time value if separate from compression flags
                MASK = 0b11111111111  # mask to extract time later on
            else:
                time_a = 2
                MASK = 0  # mask to extract time later on
        else:
            time_a = 0
            MASK = 0  # mask to extract time later on
        time_b = 2 # Time value if together with compression flags or on its own
        quat_frames = {}
        total_changes = 0
        for bone in range(self.bone_count):
            if self.quat_sizes[bone] == 0:
                continue
            frames = {}
            bone_ref = 0
            bone_check = self.quat_sizes[bone]
            while bone_ref < bone_check:
                bone_ref += time_a + time_b
                total_read = 0

                if self.flags & COMP_FLAGS:
                    x_bits = 0
                    y_bits = 0
                    z_bits = 0
                    quat_time = self.readBytes(time_a)
                    comp_time = self.readBytes(time_b)
                    if comp_time & NEG_W:
                        print(f"Negative W value found. Bone {bone}, at time {quat_time}")
                        input("Press Enter to Continue")
                    quat_time += comp_time & MASK
                    """if quat_time == 3006:
                        print()"""
                    read_time = 0

                    if comp_time & COMP_FLAG:
                        if not (comp_time & (COMP_X | COMP_Y | COMP_Z)):
                            # COMP_FLAG is set, but COMP_X, COMP_Y, and COMP_Z are not set
                            x_val, y_val, z_val = 0, 0, 0
                            self.readBytes(2)
                            total_read += 2
                        elif comp_time & COMP_X:
                            x_bits = 1
                            x_val = self.readBytes(x_bits)
                            if comp_time & COMP_Y:
                                y_bits = 1
                            else:
                                self.readBytes(1) # Skip a byte
                                total_read += 1
                                y_bits = 2
                            y_val = self.readBytes(y_bits)
                            if comp_time & COMP_Z:
                                z_bits = 1
                            else:
                                z_bits = 2
                            z_val = self.readBytes(z_bits)
                        else:
                            x_bits = 2
                            x_val = self.readBytes(x_bits)
                            if comp_time & COMP_Y:
                                y_bits = 1
                                y_val = self.readBytes(y_bits)
                                if comp_time & COMP_Z:
                                    z_bits = 1
                                else:
                                    self.readBytes(1)
                                    total_read += 1
                                    z_bits = 2
                                z_val = self.readBytes(z_bits)
                            else:
                                y_bits = 2
                                y_val = self.readBytes(y_bits)
                                if comp_time & COMP_Z:
                                    z_bits = 1
                                    z_val = self.readBytes(z_bits)
                                    self.readBytes(1)
                                    total_read += 1
                                else:
                                    z_bits = 2
                                    z_val = self.readBytes(z_bits)
                        total_read += x_bits + y_bits + z_bits
                        if total_read % 2 == 1:
                            self.readBytes(1)
                            total_read += 1
                    else:
                        x_val = self.readBytes(2)
                        y_val = self.readBytes(2)
                        z_val = self.readBytes(2)
                        total_read += 6
                else:
                    quat_time = self.readBytes(2)
                    x_val = self.readBytes(2)
                    y_val = self.readBytes(2)
                    z_val = self.readBytes(2)
                    total_read += 6
                if self.debug:
                    x_val = x_val - 65536 if x_val > 32767 else x_val
                    y_val = y_val - 65536 if y_val > 32767 else y_val
                    z_val = z_val - 65536 if z_val > 32767 else z_val
                if quat_time in frames:
                    print("Something weird happened with the quat time")
                if quat_time != 57005: # DEAD DEAD signifying the end of the quat
                    frames[quat_time] = [x_val, y_val, z_val].copy()
                """else:
                    print()"""
                """if len(frames.keys()) == 982 and bone == 65:
                    print()"""
                bone_ref += total_read
                # print()

            if bone_ref != self.quat_sizes[bone]:
                raise Exception
            quat_frames[bone] = frames
            if not self.flags & COMP_FLAGS:
                check_F = self.position % 16
                if check_F != 0:
                    self.readBytes(16-check_F)
                    # print()
            total_changes += len(frames.keys())
        '''if total_changes % (1<<16) != self.quat_changes: # You can apparently have more than 65536 changes
            raise Exception("Total Quaternion changes read does not match given quat changes")'''
        # Commented out because it doesn't matter. Once re-writing them, it adds the proper vals
        return quat_frames

    def read_trans(self):
        if self.trans_pos == 0:
            return
        self.setPosition(self.trans_pos)
        if self.partial_bones:
            first_bone = self.partial_bones[0]
        else:
            first_bone = 0
        trans_frames = {}
        total_changes = 0
        for bone in range(self.bone_count):
            if self.partial_bones:
                if bone not in self.partial_bones:
                    continue
            frames = {}
            bone_ref = 0
            bone_check = self.trans_sizes[bone]
            while bone_ref < bone_check:
                if self.flags & TRANS_FLOAT_TIME:
                    real_time, trans_x, trans_y, trans_z = self.readFloat(), self.readFloat(), self.readFloat(), self.readFloat()
                    if not real_time.is_integer():
                        raise Exception("Frame is not a whole number!")
                    real_time = int(real_time)
                    bone_ref += 16
                else:
                    flag_time = self.readBytes(1)
                    long_time = self.readBytes(2)
                    zero = self.readBytes(1)
                    real_time = flag_time - 64 if long_time == 0 else long_time
                    bone_ref += 4
                    if zero != 0:
                        print("Values that should be 0 are not! Contact me!")
                    if bone == first_bone and not frames:
                        unk_a, unk_b, unk_c = self.readBytes(), self.readBytes(), self.readBytes()
                        bone_ref += 12
                        if any([unk_a != 0, unk_b != 0, unk_c != 0]):
                            print("Values that should be 0 are not! Contact me!")
                    trans_x, trans_y, trans_z = self.readFloat(), self.readFloat(), self.readFloat()
                    bone_ref += 12
                frames[real_time] = [trans_x, trans_y, trans_z].copy()
            total_changes += len(frames.keys())
            trans_frames[bone] = frames

        '''if total_changes % (1<<16) != self.trans_changes:
            raise Exception("Total Translation changes read does not match given changes")'''
        return trans_frames

    def read_custom_keys(self):
        if self.custom_keys == 0:
            return -1
        self.position = self.customkey_pos
        custom_keys = []
        for x in range(self.custom_keys):
            curr_key = []
            key_time = self.readFloat()
            key_type = self.readBytes()
            key_value = self.readBytes()
            curr_key.append(key_time)
            curr_key.append(key_type)
            curr_key.append(key_value)
            if key_type == 1:
                key_mod = self.readFloat()
                curr_key.append(key_mod)
            elif key_type == 9:
                pass
            else:
                raise Exception("Custom keys found in unsupported ska file. Contact me.")
            custom_keys.append(curr_key)


        return custom_keys

    def read_pointer_block(self):
        self.position = self.pointerblock_offset
        pointer_offsets = []
        for pointer in range(20):
            offset = self.readBytes()
            pointer_offsets.append(offset + self.pointerblock_offset)
        bone_offsets = {}
        times = {}
        for offset in pointer_offsets:
            self.position = offset
            for x in range(self.bone_count):
                bone_off = self.readBytes() + self.data_start
                if bone_off != 0xffffffff + self.data_start:
                    if x in bone_offsets:
                        bone_offsets[x].append(bone_off)
                    else:
                        bone_offsets[x] = [bone_off]

                    curr_off = self.position
                    self.setPosition(bone_off)
                    curr_time = self.readBytes(2)
                    if curr_time >= 0b100000000000000:
                        curr_time = curr_time & 0b11111111111
                    if x in times:
                        times[x].append(curr_time)
                    else:
                        times[x] = [curr_time]
                    self.setPosition(curr_off)
        self.pointerframes = times
        # print()

    def getEndian(self):
        return self.endian

    def getPosition(self):
        return self.position

    def setPosition(self, update_val):
        self.position = update_val

class ska_type:
    def __init__(self, ska_name, bone_count, bone_range, partial_anim):
        self.name = ska_name
        self.bone_count = bone_count
        self.bone_range_low = bone_range[0]
        self.bone_range_high = bone_range[1]
        self.partial_anim = partial_anim

gh3_singer = ska_type("GH3 Singer", 121, [68,97], b'\x00\x00\x00\x79\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xF0\xFE\x00\x00\x03')
gh3_guitarist = ska_type("GH3 Guitarist", 121, [68,97], b'\x00\x00\x00\x79\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xF0\xFE\x00\x00\x03')
gha_singer = ska_type("GH:A Singer",118, [67,96], b'\x00\x00\x00\x76\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xF8\xFF\xC0\x00\x01')
dmc_singer = ska_type("DMC Singer", 115, [67,96], b'\x00\x00\x00\x73\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xF8\xFF\xF8\x00\x01')
gha_guitarist = ska_type("GH:A Guitarist", 125, [68,97], b'\x00\x00\x00\x7D\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xF0\xE0\x00\x00\x03')
# ^ Also Joe Perry
steve_singer = ska_type("Steven Tyler", 128, [63,92], b'\x00\x00\x00\x80\x00\x00\x00\x00\x80\x00\x00\x00\x1F\xFF\xFF\xFF\x00\x00\x00\x00')

wt_singer = ska_type("World Tour",128, [63,92], b'\x00\x00\x00\x80\x00\x00\x00\x00\x80\x00\x00\x00\x1F\xFF\xFF\xFF\x00\x00\x00\x00')
# ^ Has a different header

lipsync_types = [gh3_singer, gh3_guitarist, gha_singer, steve_singer, gha_guitarist, dmc_singer]
lipsync_dict = {"gh3_singer": gh3_singer,
                "gh3_guitarist": gh3_guitarist,
                "gha_singer": gha_singer,
                "gha_guitarist": gha_guitarist,
                "dmc": dmc_singer,
                "steve": steve_singer,
                "wt_singer": wt_singer
                }