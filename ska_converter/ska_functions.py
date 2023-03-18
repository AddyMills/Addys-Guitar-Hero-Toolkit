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

def quats_u(quats):  # Function to create quats/trans in uncompressed form
    quat_bytes = bytearray()
    quat_changes = 0  # Number of times quats change this file
    bone_lengths = {}
    for x in range(128):
        bone_lengths[x] = 0
    for quat in sorted(quats.keys()):
        bone_bytes = bytearray()
        quat_f = quats[quat]
        quat_changes += len(quat_f.keys())
        for vals in sorted(quat_f.keys()):
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
    return quat_bytes, bone_lengths, quat_changes

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


def make_custom_keys(keys):
    custom_keys = bytearray()
    for x in keys:
        for key in x:
            if type(key) == int:
                custom_keys += key.to_bytes(4, "big")
            else:
                custom_keys += struct.pack(">f", key)
    return custom_keys

def swap_bones(ska, ska_switch):
    bone_list = sorted(list(ska.quat_frames.keys()))
    curr_b_start = bone_list[0]
    modifier = ska_switch.bone_range_low - curr_b_start
    new_quat_frames = {}
    new_quat_sizes = {}
    new_trans_frames = {}
    new_trans_sizes = {}

    for x in range(ska_switch.bone_count):
        new_quat_sizes[x] = 0
        new_trans_sizes[x] = 0

    for x in bone_list:
        new_quat_frames[x + modifier] = ska.quat_frames[x]
        new_quat_sizes[x + modifier] = ska.quat_sizes[x]
        new_trans_frames[x + modifier] = ska.trans_frames[x]
        new_trans_sizes[x + modifier] = ska.trans_sizes[x]
    ska.quat_frames = new_quat_frames
    ska.quat_sizes = new_quat_sizes
    ska.trans_frames = new_trans_frames
    ska.trans_sizes = new_trans_sizes
    ska.bone_count = ska_switch.bone_count
    return


def pull_basic_data(ska, game, quats_mult = 1, big_time = 0):
    bone_count = ska.bone_count
    if game == "GH5":
        quat_data, quat_sizes, quat_changes = quats_u(ska.quat_frames)
        trans_data, trans_sizes, trans_changes = trans_u(ska.trans_frames)
    else:
        quat_data, quat_sizes, quat_changes = quats_c(ska.quat_frames, quats_mult, big_time)
        trans_data, trans_sizes, trans_changes = trans_c(ska.trans_frames)
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

    return bone_count, quat_data, quat_sizes, quat_changes, trans_data, trans_sizes, trans_changes, block_sizes, partial_anim, length, custom_key_count, custom_keys


def make_gh3_ska(ska, **kwargs):
    if "quats_mult" in kwargs:
        quats_mult = kwargs["quats_mult"]
    else:
        quats_mult = 1

    if "ska_switch" in kwargs:
        try:
            ska_switch = kwargs["ska_switch"]
            swap_bones(ska, ska_switch)
        except:
            ska_switch = 0
    else:
        ska_switch = 0


    bone_count, quat_data, quat_sizes, quat_changes, trans_data, trans_sizes, \
        trans_changes, block_sizes, partial_anim, length, custom_key_count, custom_keys = pull_basic_data(ska, "GH3", quats_mult, ska.big_time)

    if ska_switch:
        partial_anim = ska_switch.partial_anim

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


def make_gh5_ska(ska, *args, **kwargs):
    bone_count, quat_data, quat_sizes, quat_changes, trans_data, trans_sizes, \
        trans_changes, block_sizes, partial_anim, length, custom_key_count, custom_keys = pull_basic_data(ska, "GH5")

    anim_offset = 32
    null_offset = 500
    bonepointer_offset = NO_OFF
    offset_b = NO_OFF
    offset_c = NO_OFF
    offset_d = 0
    version = 104

    flags = 0x964B5000
    if length > 34.11:
        flags += (1 << 8)
    unk = 0

    float_pairs = [ska.float_pair_0, ska.float_pair_1, ska.float_pair_2, ska.float_pair_3]

    total_size = len(quat_data) + len(trans_data) + len(block_sizes) + len(partial_anim) + len(custom_keys) + 256
    quat_pos = 256
    custom_key_pos = (total_size - len(custom_keys)) if custom_keys else NO_OFF
    partial_anim_offset = (total_size - len(partial_anim)) if partial_anim else NO_OFF
    bone_start = custom_key_pos if partial_anim_offset == NO_OFF else partial_anim_offset
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
            header_bytes += header.to_bytes(b_size, "big")
        elif type(header) == float:
            header_bytes += struct.pack(">f", header)
        else:
            for x in header:
                for y in x:
                    header_bytes += struct.pack(">f", y)
    header_bytes += b'\x00' * (256 - len(header_bytes))
    ska_file = header_bytes + quat_data + trans_data + block_sizes + partial_anim + custom_keys
    return ska_file
