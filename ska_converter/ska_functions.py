import struct

NO_OFF = 0xFFFFFFFF


def quats_c(quats, quats_mult = 1, BIG_TIME = 0):  # Function to create quats/trans in compressed form
    quat_bytes = bytearray()
    quat_changes = 0  # Number of times quats change this file
    bone_lengths = {}
    for bones in range(128):
        bone_lengths[bones] = 0

    if not BIG_TIME:
        for frames in quats.keys():
            a_list = list(quats[frames].keys())[-1]
            if a_list > 2047:
                BIG_TIME = True
                break
    COMP_FLAG_MAIN = 1 << 14
    comp_flags = [1 << 13, 1 << 12, 1 << 11]

    for quat in sorted(quats.keys()):
        bone_bytes = bytearray()
        quat_f = quats[quat]
        quat_changes += len(quat_f.keys())
        for vals in sorted(quat_f.keys()):
            if BIG_TIME:
                bone_bytes += vals.to_bytes(2, "big")
                flag_time = 0
            else:
                flag_time = vals
            comp_bits = [0, 0, 0]
            comp_bytes = bytearray()
            for bit, x in enumerate(quat_f[vals]):
                if quats_mult != 1:
                    x = x - 65536 if x > 32767 else x  # Python doesn't convert well between signed and unsigned
                    x = round(x*quats_mult)
                    x = x + 65536 if x < 0 else x
                if x >= 0 and x < 256:
                    comp_bits[bit] = comp_flags[bit]
                    comp_bytes += x.to_bytes(1, "big")
                else:
                    if len(comp_bytes) % 2 == 1:
                        comp_bytes += b'\x00'
                    comp_bytes += x.to_bytes(2, "big")

            if len(comp_bytes) % 2 == 1:
                comp_bytes += b'\x00'
            if any(comp_bits):
                flag_time += sum(comp_bits) + COMP_FLAG_MAIN
            bone_bytes += flag_time.to_bytes(2, "big")
            bone_bytes += comp_bytes
            # print()
        bone_lengths[quat] = len(bone_bytes)  # How long the quats are for this bone
        quat_bytes += bone_bytes
        # print()
    if len(quat_bytes) % 128 != 0:
        quat_bytes += b'\x00' * (128 - len(quat_bytes) % 128)
    return quat_bytes, bone_lengths, quat_changes

def quats_u(quats, bone_pointers = {}):  # Function to create quats/trans in uncompressed form
    quat_bytes = bytearray()
    quat_changes = 0  # Number of times quats change this file
    bone_lengths = {}
    curr_bone_p = {}
    new_bone_pointers = {}
    for key, value in bone_pointers.items():
        new_bone_pointers[key] = []
    for x in range(128):
        bone_lengths[x] = 0
    for quat in sorted(quats.keys()):
        if bone_pointers:
            curr_bone_p = bone_pointers[quat]
        bone_bytes = bytearray()
        quat_f = quats[quat]
        quat_changes += len(quat_f.keys())
        for entry, vals in enumerate(sorted(quat_f.keys())):
            if vals in curr_bone_p:
                for value in range(curr_bone_p.count(vals)):
                    new_bone_pointers[quat].append(len(bone_bytes) + len(quat_bytes))
            bone_bytes += vals.to_bytes(2, "big")
            for x in quat_f[vals]:
                bone_bytes += x.to_bytes(2, "big")
        bone_lengths[quat] = len(bone_bytes)  # How long the quats are for this bone
        quat_bytes += bone_bytes
        # print()
        if len(quat_bytes) % 16 == 0:
            continue
        elif len(quat_bytes) % 16 == 8:
            quat_bytes += b'\xDE\xAD\xDE\xAD\xDE\xAD\xDE\xAD'
        else:
            raise Exception("Length of quats bytes stream not divisible by 8 or 16.")
    if len(quat_bytes) % 32 != 0:
        quat_bytes += b'\x00' * (32 - len(quat_bytes) % 32)
    return quat_bytes, bone_lengths, quat_changes, new_bone_pointers

def trans_c(trans):  # Function to create trans in compressed form
    trans_bytes = bytearray()
    add_0 = True
    trans_changes = 0  # Number of times transes change this file
    bone_lengths = {}
    for x in range(128):
        bone_lengths[x] = 0
    for bone_num, tran in enumerate(sorted(trans.keys())):
        bone_bytes = bytearray()
        tran_f = trans[tran]
        trans_changes += len(tran_f.keys())
        for vals in sorted(tran_f.keys()):
            if vals < 64:
                flag_time = vals + 64
                long_time = 0
            else:
                flag_time = 0
                long_time = vals
            bone_bytes += flag_time.to_bytes(1, "big")
            bone_bytes += long_time.to_bytes(2, "big")
            bone_bytes += int.to_bytes(0, 1, "big")
            if add_0:
                add_0 = False
                bone_bytes += struct.pack(">f", 0)
                bone_bytes += struct.pack(">f", 0)
                bone_bytes += struct.pack(">f", 0)
            for x in tran_f[vals]:
                bone_bytes += struct.pack(">f", x)
        bone_lengths[tran] = len(bone_bytes)  # How long the quats are for this bone
        trans_bytes += bone_bytes

    if len(trans_bytes) % 128 != 0:
        trans_bytes += b'\x00' * (128 - len(trans_bytes) % 128)
    return trans_bytes, bone_lengths, trans_changes

def trans_u(trans):  # Function to create trans in uncompressed form
    trans_bytes = bytearray()
    trans_changes = 0  # Number of times transes change this file
    bone_lengths = {}
    for x in range(128):
        bone_lengths[x] = 0
    for tran in sorted(trans.keys()):
        bone_bytes = bytearray()
        tran_f = trans[tran]
        trans_changes += len(tran_f.keys())
        for vals in sorted(tran_f.keys()):
            bone_bytes += struct.pack(">f", vals)
            for x in tran_f[vals]:
                bone_bytes += struct.pack(">f", x)
        bone_lengths[tran] = len(bone_bytes)  # How long the quats are for this bone
        trans_bytes += bone_bytes
        # print()
        if len(trans_bytes) % 16 == 0:
            continue
        elif len(trans_bytes) % 16 == 8:
            trans_bytes += b'\xDE\xAD\xDE\xAD\xDE\xAD\xDE\xAD'
        else:
            raise Exception("Length of quats bytes stream not divisible by 8 or 16.")
    if len(trans_bytes) % 32 != 0:
        trans_bytes += b'\x00' * (32 - len(trans_bytes) % 32)
    return trans_bytes, bone_lengths, trans_changes


def make_partial(partial_bin, bone_count):
    partial_anim = bytearray()
    partial_anim += bone_count.to_bytes(4, "big")
    for x in partial_bin:
        partial_anim += int(x, 2).to_bytes(4, "big")
    return partial_anim


def make_block_sizes(sizes, bone_count):
    block_sizes = bytearray()
    for x in sizes:
        for bone in range(bone_count):
            block_sizes += x[bone].to_bytes(2, "big")
        if len(block_sizes) < 256:
            block_sizes += b'\x00' * (256 - len(block_sizes))
    if len(block_sizes) % 4 != 0:
        block_sizes += b'\x00' * (4 - (len(block_sizes) % 4))

    return block_sizes

def add_new_quats():

    return

def add_new_trans(x, y, z):

    return

def float_to_quat(x):
    if x == 0:
        return x
    x *= 32768
    if x < 0:
        x+= 65536
    return int(round(x))

def make_custom_keys(keys):
    custom_keys = bytearray()
    for x in keys:
        for key in x:
            if type(key) == int:
                custom_keys += key.to_bytes(4, "big")
            else:
                custom_keys += struct.pack(">f", key)
    return custom_keys

def dmc_hack(ska, quat_frames, trans_frames, partials):
    if 122 in trans_frames:
        print("Applying translation change for mic stand.")
        for key, value in trans_frames[122].items():
            value[1] -= 0.8139

    if 125 in quat_frames:
        print("Adjusting microphone height and angle.\n")
        mic_height_x = 0
        mic_height_y = 0
        mic_height_z = 0
        height_adjust = .90
        front_adjust = .94
        side_adjust = .95
        last_frame = round(ska.duration * 60)
        quat_frames[123] = {0: [0,0,0], last_frame: [0,0,0]}
        trans_frames[123] = {0: [mic_height_x, mic_height_y, mic_height_z], last_frame: [mic_height_x, mic_height_y, mic_height_z]}
        partials[123] = "1"

        quat_frames[124] = {}
        for key, value in quat_frames[125].items():
            quat_frames[124][key] = value

        trans_frames[124] = {}
        min_height = 0
        max_height = 0
        for key, value in trans_frames[125].items():
            new_height = value[0] * height_adjust

            new_front = value[1] * front_adjust

            new_side = value[2] * side_adjust

            # trans_frames[124][key] = [new_height, value[1], value[2]]
            trans_frames[124][key] = [new_height, new_front, new_side]
            if min_height and value[0] < min_height:
                min_height = value[0]
            elif min_height == 0:
                min_height = value[0]

            if max_height and value[0] > max_height:
                max_height = value[0]
            elif max_height == 0:
                max_height = value[0]
        partials[124] = "1"

        quat_frames.pop(125)
        trans_frames.pop(125)
        partials[125] = "0"

    else:
        mic_height_x = 0
        mic_height_y = 0
        mic_height_z = 0
        last_frame = round(ska.duration * 60)
        quat_frames[123] = {0: [0, 0, 0], last_frame: [0, 0, 0]}
        trans_frames[123] = {0: [mic_height_x, mic_height_y, mic_height_z],
                             last_frame: [mic_height_x, mic_height_y, mic_height_z]}
        partials[123] = "1"

    ik_x = 0.3919
    ik_y = 0.00878
    ik_z = 0.22711


    if 126 in trans_frames:
        for key, value in trans_frames[126].items():  # Left hand IK
            value[0] += ik_x
            value[1] += ik_y
            value[2] += ik_z
    # ik_z -= .000001
    if 127 in trans_frames:
        for key, value in trans_frames[127].items():  # Right hand IK
            value[0] += ik_x
            value[1] += ik_y
            value[2] -= ik_z

    return

def steven_tyler_hack(ska, quat_frames, trans_frames, partials):
    if 122 in trans_frames:
        print("Applying translation change for mic stand.")
        for key, value in trans_frames[122].items():
            value[1] -= 0.8139

    if 125 in quat_frames:
        print("Adjusting microphone height and angle.\n")
        mic_height_x = -.0233
        mic_height_y = 0
        mic_height_z = 0
        last_frame = round(ska.duration * 60)
        quat_frames[123] = {0: [0,0,0], last_frame: [0,0,0]}
        trans_frames[123] = {0: [mic_height_x, mic_height_y, mic_height_z], last_frame: [mic_height_x, mic_height_y, mic_height_z]}
        partials[123] = "1"

        quat_frames[124] = {}
        for key, value in quat_frames[125].items():
            quat_frames[124][key] = value

        trans_frames[124] = {}
        for key, value in trans_frames[125].items():
            trans_frames[124][key] = value
        partials[124] = "1"

        quat_frames.pop(125)
        trans_frames.pop(125)
        partials[125] = "0"

    return
def swap_bones(ska, ska_to):
    display_warn = False
    bone_list = sorted(list(ska.quat_frames.keys()))
    bone_count = int((len(ska_to)+1)/2)
    ska_from = grab_ska_dict(ska.ska_source)
    bone_names = [ska_from[bone] for bone in bone_list]
    new_bone_nums = []
    for bone in bone_names:
        try:
            new_bone_nums.append(ska_to[bone])
        except KeyError:
            new_bone_nums.append(-1)
    new_quat_frames = {}
    new_quat_sizes = {}
    new_trans_frames = {}
    new_trans_sizes = {}
    new_partials = ["0"] * 128

    for x in range(bone_count):
        new_quat_sizes[x] = 0
        new_trans_sizes[x] = 0


    for new, old in zip(new_bone_nums, bone_list):
        if new == -1:
            display_warn = True
            print(f"Warning! No equivalent bone found for {ska_from[old]}.")
            continue
        new_quat_frames[new] = ska.quat_frames[old]
        new_quat_sizes[new] = ska.quat_sizes[old]
        new_trans_frames[new] = ska.trans_frames[old]
        new_trans_sizes[new] = ska.trans_sizes[old]
        new_partials[new] = "1"

    if display_warn:
        print("\nAnimations may look strange after conversion!\n")

    if bone_count < 128:
        new_partials[bone_count:] = ["1"] * (128 - bone_count)

    if any([ska.ska_source == "steve"]) and ska.to_ska == "wt_rocker":
        steven_tyler_hack(ska, new_quat_frames, new_trans_frames, new_partials)

    if ska.ska_source == "dmc_singer" and ska.to_ska == "wt_rocker":
        dmc_hack(ska, new_quat_frames, new_trans_frames, new_partials)

    split_partials = [new_partials[i:i+32] for i in range(0, 128, 32)]
    new_split = []
    for partial in split_partials:
        new_split.append("".join(reversed(partial)))

    ska.quat_frames = new_quat_frames
    ska.quat_sizes = new_quat_sizes
    ska.trans_frames = new_trans_frames
    ska.trans_sizes = new_trans_sizes
    ska.bone_count = bone_count
    ska.partial_bin = new_split
    ska.partial_bones = new_bone_nums
    ska.partial_bone_count = bone_count
    return


def pull_basic_data(ska, game, quats_mult = 1, big_time = 0):
    bone_count = ska.bone_count
    if game == "GH5":
        quat_data, quat_sizes, quat_changes, bone_pointers = quats_u(ska.quat_frames, ska.pointerframes)
        trans_data, trans_sizes, trans_changes = trans_u(ska.trans_frames)
        if bone_pointers:
            bone_pointers = make_bone_block(ska, bone_pointers)
        else:
            bone_pointers = b''
    else:
        quat_data, quat_sizes, quat_changes = quats_c(ska.quat_frames, quats_mult, big_time)
        trans_data, trans_sizes, trans_changes = trans_c(ska.trans_frames)
        bone_pointers = {}
    block_sizes = make_block_sizes([quat_sizes, trans_sizes], bone_count)

    if ska.partial_bones:
        partial_anim = make_partial(ska.partial_bin, ska.partial_bone_count)
    else:
        partial_anim = b''

    length = ska.duration

    custom_key_count = ska.custom_keys
    if custom_key_count:
        custom_keys = make_custom_keys(ska.custom_key_data)
    else:
        custom_keys = b''

    return bone_count, quat_data, quat_sizes, quat_changes, trans_data, trans_sizes, trans_changes, block_sizes, partial_anim, length, custom_key_count, custom_keys, bone_pointers

def make_bone_block(ska, bone_pointers):
    block_bytes = bytearray()
    for block in range(20):
        for bone in range(ska.bone_count):
            if bone in bone_pointers:
                to_add = bone_pointers[bone][block].to_bytes(4, "big")
                block_bytes.extend(to_add)
            else:
                block_bytes.extend(b'\xff\xff\xff\xff')
    return block_bytes

def grab_ska_dict(ska_type):
    import ska_definitions as ska

    if ska_type == "gh3_singer":
        return ska.gh3_singer_bones
    elif ska_type == "gh3_guitarist":
        return ska.gh3_guitarist_bones
    elif ska_type == "gha_singer":
        return ska.gha_singer_bones
    elif ska_type == "steve":
        return ska.steve_bones
    elif ska_type == "dmc_singer":
        return ska.dmc_bones
    elif ska_type == "wt_rocker":
        return ska.wt_bones
    else:
        raise Exception("Unknown SKA type found")

def make_gh3_ska(ska, **kwargs):
    if "quats_mult" in kwargs:
        quats_mult = kwargs["quats_mult"]
    else:
        quats_mult = 1

    if all(["ska_switch" in kwargs, ska.ska_source != "camera"]):
        try:
            ska.to_ska = kwargs["ska_switch"]
            if ska.to_ska == ska.ska_source:
                ska_switch = 0
            else:
                ska_switch = grab_ska_dict(ska.to_ska)
                swap_bones(ska, ska_switch)
        except Exception as e:
            raise e
            ska_switch = 0
    else:
        if ska.ska_source == "camera":
            print("Cameras are not yet supported to convert to GH3 or GHA\n")
            return None
        ska_switch = 0


    bone_count, quat_data, quat_sizes, quat_changes, trans_data, trans_sizes, \
        trans_changes, block_sizes, partial_anim, length, custom_key_count, custom_keys, bone_pointers = pull_basic_data(ska, "GH3", quats_mult, ska.big_time)


    anim_offset = 32
    null_offset = NO_OFF
    bonepointer_offset = NO_OFF
    offset_d = NO_OFF
    unk = 0

    float_pairs = [[1.0, 0, 0, 0], [1.0, 0, 0, 0]]

    version = 72
    flags = 0x068B5000
    if length > 34.11 or ska.big_time:
        flags += (1 << 8)

    quat_pos = 128

    total_size = len(quat_data) + len(trans_data) + len(block_sizes) + len(partial_anim) + len(custom_keys) + quat_pos

    custom_key_pos = (total_size - len(custom_keys)) if custom_keys else NO_OFF
    partial_anim_offset = (total_size - len(partial_anim)) if partial_anim else NO_OFF

    bone_start = custom_key_pos if partial_anim_offset == NO_OFF else partial_anim_offset
    bonesize_quat = bone_start - len(block_sizes)
    bonesize_trans = bonesize_quat + 256

    trans_pos = bonesize_quat - len(trans_data)

    to_add = [total_size, anim_offset, null_offset, bonepointer_offset, partial_anim_offset,
              offset_d, version, flags, length, unk, bone_count, quat_changes, float_pairs, trans_changes,
              custom_key_count, custom_key_pos, quat_pos, trans_pos, bonesize_quat, bonesize_trans]

    byte_sizes = [4, 4, 4, 4, 4,
                  4, 4, 4, 4, 1, 1, 2, 4, 2,
                  2, 4, 4, 4, 4, 4]

    header_bytes = bytearray()
    header_bytes += int('00000000ffffffff', 16).to_bytes(8, "big")
    for header, b_size in zip(to_add, byte_sizes):
        if type(header) == int:
            if header > (1 << (b_size*8)):
                header %= (1 << (b_size*8))
            header_bytes += header.to_bytes(b_size, "big")
        elif type(header) == float:
            header_bytes += struct.pack(">f", header)
        else:
            for x in header:
                for y in x:
                    header_bytes += struct.pack(">f", y)
    header_bytes += b'\x00' * (128 - len(header_bytes))
    ska_file = header_bytes + quat_data + trans_data + block_sizes + partial_anim + custom_keys

    return ska_file


def make_modern_ska(ska, game = "GH5", *args, **kwargs):
    if "quats_mult" in kwargs:
        quats_mult = kwargs["quats_mult"]
    else:
        quats_mult = 1

    if all(["ska_switch" in kwargs, ska.ska_source != "camera"]):
        try:
            ska.to_ska = kwargs["ska_switch"]
            if ska.to_ska == ska.ska_source:
                ska_switch = 0
            else:
                ska_switch = grab_ska_dict(ska.to_ska)
                swap_bones(ska, ska_switch)
        except Exception as e:
            raise e
            ska_switch = 0
    else:
        if ska.ska_source == "camera" and ska.bone_count == 2:
            ska.quat_frames[2] = {0: [0, 0, 0], ska.duration_frames_60: [0,0,0]}
            ska.trans_frames[2] = {0: [0, 0, 0], ska.duration_frames_60: [0, 0, 0]}
            ska.bone_count = 3
        ska_switch = 0

    bone_count, quat_data, quat_sizes, quat_changes, trans_data, trans_sizes, \
        trans_changes, block_sizes, partial_anim, length, custom_key_count, custom_keys, bone_pointers = pull_basic_data(ska, game, quats_mult, ska.big_time)

    anim_offset = 32
    if game == "GH5":
        null_offset = 500
    else:
        null_offset = 0

    offset_b = NO_OFF
    offset_c = NO_OFF
    offset_d = NO_OFF if game == "GHWT" else 0
    version = 104

    if game == "GH5":
        flags = 0x960B5000 if ska.ska_source != "camera" else 0x96011000
        if bone_pointers:
            flags += (1 << 22)
    else:
        flags = 0x068B5000 if ska.ska_source != "camera" else 0x06811000
    if length > 34.11 or ska.big_time:
        flags += (1 << 8)
    unk = 0

    # float_pairs = [ska.float_pair_0, ska.float_pair_1, ska.float_pair_2, ska.float_pair_3]
    # float_pairs = [[0,0,0,1], [-0.5,-0.5,-0.5,0.5],[0,0,0,1], [-0.5,-0.5,-0.5,0.5]]
    if len(ska.float_pairs) == 4:
        float_pairs = [ska.float_pairs[0], ska.float_pairs[1], ska.float_pairs[2], ska.float_pairs[3]]
    else:
        float_pairs = [
            [0, 0, 0, struct.unpack(">f", b'\x3F\x80\x00\x00')[0]],
            [struct.unpack(">f", b'\xBE\xFF\xFF\xFD')[0], struct.unpack(">f", b'\xBE\xFF\xFF\xFE')[0], struct.unpack(">f", b'\xBF\x00\x00\x00')[0], struct.unpack(">f", b'\x3F\x00\x00\x01')[0]],
            [0, 0, 0, struct.unpack(">f", b'\x3F\x80\x00\x00')[0]],
            [struct.unpack(">f", b'\xBE\xFF\xFF\xFD')[0], struct.unpack(">f", b'\xBE\xFF\xFF\xFE')[0], struct.unpack(">f", b'\xBF\x00\x00\x00')[0], struct.unpack(">f", b'\x3F\x00\x00\x01')[0]]
        ]

    total_size = len(quat_data) + len(trans_data) + len(block_sizes) + len(partial_anim) + len(custom_keys) + 256
    quat_pos = 256
    custom_key_pos = (total_size - len(custom_keys)) if custom_keys else NO_OFF
    partial_anim_offset = (total_size - len(partial_anim)) if partial_anim else NO_OFF
    if all([custom_key_pos == NO_OFF, partial_anim_offset == NO_OFF]):
        bone_start = total_size
    else:
        bone_start = custom_key_pos if partial_anim_offset == NO_OFF else partial_anim_offset
    if bone_pointers:
        bonepointer_offset = total_size
        bone_header = bytearray()
        for x in range(20):
            bone_header += struct.pack(">I", 80 + (bone_count*4*x))
        total_size += len(bone_header) + len(bone_pointers)
    else:
        bonepointer_offset = NO_OFF
        bone_header = b''
        bone_pointers = b''
    bonesize_quat = bone_start - len(block_sizes)
    bonesize_trans = bonesize_quat + 256
    trans_pos = bonesize_quat - len(trans_data)
    to_add = [total_size, anim_offset, null_offset, bonepointer_offset, offset_b, offset_c, partial_anim_offset,
              offset_d, version, flags, length, unk, bone_count, quat_changes, float_pairs, trans_changes,
              custom_key_count, custom_key_pos, quat_pos, trans_pos, bonesize_quat, bonesize_trans]
    byte_sizes = [4, 4, 4, 4, 4, 4, 4,
                  4, 4, 4, 4, 1, 1, 2, 4, 2,
                  2, 4, 4, 4, 4, 4]
    header_bytes = bytearray()
    for header, b_size in zip(to_add, byte_sizes):
        if type(header) == int:
            if header > (1 << (b_size*8)):
                header %= (1 << (b_size*8))
            header_bytes += header.to_bytes(b_size, "big")
        elif type(header) == float:
            header_bytes += struct.pack(">f", header)
        else:
            for x in header:
                for y in x:
                    header_bytes += struct.pack(">f", y)
    header_bytes += b'\x00' * (256 - len(header_bytes))
    ska_file = header_bytes + quat_data + trans_data + block_sizes + partial_anim + custom_keys + bone_header + bone_pointers
    return ska_file
