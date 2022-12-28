import struct
import sys
import os

class ska_type:
    def __init__(self, ska_name, bone_count, bone_range, partial_anim):
        self.name = ska_name
        self.bone_count = bone_count
        self.bone_range_low = bone_range[0]
        self.bone_range_high = bone_range[1]
        self.partial_anim = partial_anim

class ska_bytes:
    def __init__(self, data, endian = "big"):
        self.data = data
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

def read_gh3(ska_file):
    ska_dict = {}
    ska_file.setPosition(8)
    # Read all the header information
    ska_order = ["file_size", "anim_offset", "null_offset", "bonepointers_offset", "partial_anim_offset", "d_offset", "version", "flags"]
    for x in ska_order:
        ska_dict[x] = ska_file.readBytes()
    ska_dict["duration"] = ska_file.readFloat()
    ska_dict["unk_byte"] = ska_file.readBytes(1)
    ska_dict["bone_count"] = ska_file.readBytes(1)
    ska_dict["unk_b"] = ska_file.readBytes(2)
    for x in ["float_pair_1", "float_pair_2"]:
        float_pair = []
        for y in range(0,4):
            float_pair.append(ska_file.readFloat())
        ska_dict[x] = float_pair.copy()
    ska_dict["unk_c"] = ska_file.readBytes(2)
    ska_dict["custom_keys"] = ska_file.readBytes(2)
    ska_dict["customkey_pos"] = ska_file.readBytes()
    ska_dict["quat_pos"] = ska_file.readBytes()
    ska_dict["trans_pos"] = ska_file.readBytes()
    ska_dict["bonesize_quat_pos"] = ska_file.readBytes()
    ska_dict["bonesize_trans_pos"] = ska_file.readBytes()

    #Read the bone information
    ska_file.setPosition(ska_dict["bonesize_quat_pos"])
    quat_sizes = {}
    trans_sizes = {}
    for x in range(0, ska_dict["bone_count"]):
        info_size = ska_file.readBytes(2)
        if info_size != 0:
            quat_sizes[x] = info_size
    ska_file.setPosition(ska_dict["bonesize_trans_pos"])
    for x in range(0, ska_dict["bone_count"]):
        info_size = ska_file.readBytes(2)
        if info_size != 0:
            trans_sizes[x] = info_size
    ska_dict["quat_sizes"] = quat_sizes
    ska_dict["trans_sizes"] = trans_sizes
    ska_dict["bone_range_low"] = sorted(quat_sizes.keys())[0]
    ska_dict["quats"] = ska_file.data[ska_dict["quat_pos"]:ska_dict["trans_pos"]]
    ska_dict["trans"] = ska_file.data[ska_dict["trans_pos"]:ska_dict["bonesize_quat_pos"]]
    ska_dict["partial_anim"] = ska_file.data[ska_dict["partial_anim_offset"]:ska_dict["partial_anim_offset"]+20]
    # raise Exception

    return ska_dict

def read_wt(ska_file):
    ska_dict = {}
    ska_file.setPosition(0)
    # Read all the header information
    ska_order = ["file_size", "anim_offset", "null_offset", "bonepointers_offset", "b_offset", "c_offset", "partial_anim_offset", "d_offset",
                 "version", "flags"]
    for x in ska_order:
        ska_dict[x] = ska_file.readBytes()
    ska_dict["duration"] = ska_file.readFloat()
    ska_dict["unk_byte"] = ska_file.readBytes(1)
    ska_dict["bone_count"] = ska_file.readBytes(1)
    ska_dict["unk_b"] = ska_file.readBytes(2)
    for x in ["float_pair_1", "float_pair_2", "float_pair_3", "float_pair_4"]:
        float_pair = []
        for y in range(0, 4):
            float_pair.append(ska_file.readFloat())
        ska_dict[x] = float_pair.copy()
    ska_dict["unk_c"] = ska_file.readBytes(2)
    ska_dict["custom_keys"] = ska_file.readBytes(2)
    ska_dict["customkey_pos"] = ska_file.readBytes()
    ska_dict["quat_pos"] = ska_file.readBytes()
    ska_dict["trans_pos"] = ska_file.readBytes()
    ska_dict["bonesize_quat_pos"] = ska_file.readBytes()
    ska_dict["bonesize_trans_pos"] = ska_file.readBytes()

    # Read the bone information
    ska_file.setPosition(ska_dict["bonesize_quat_pos"])
    quat_sizes = {}
    trans_sizes = {}
    for x in range(0, ska_dict["bone_count"]):
        info_size = ska_file.readBytes(2)
        if info_size != 0:
            quat_sizes[x] = info_size
    ska_file.setPosition(ska_dict["bonesize_trans_pos"])
    for x in range(0, ska_dict["bone_count"]):
        info_size = ska_file.readBytes(2)
        if info_size != 0:
            trans_sizes[x] = info_size
    ska_dict["quat_sizes"] = quat_sizes
    ska_dict["trans_sizes"] = trans_sizes
    ska_dict["bone_range_low"] = sorted(quat_sizes.keys())[0]
    ska_dict["quats"] = ska_file.data[ska_dict["quat_pos"]:ska_dict["trans_pos"]]
    ska_dict["trans"] = ska_file.data[ska_dict["trans_pos"]:ska_dict["bonesize_quat_pos"]]
    ska_dict["partial_anim"] = ska_file.data[ska_dict["partial_anim_offset"]:ska_dict["partial_anim_offset"] + 20]

    # raise Exception

    return ska_dict

def read_ska(ska_file):
    split_ska = -1
    if ska_file.startswith(b'\x00\x00\x00\x00'):
        for x in lipsync_types:
            if ska_file.endswith(x.partial_anim):
                split_ska = read_gh3(ska_bytes(ska_file))
                break
    else:
        split_ska = read_wt(ska_bytes(ska_file))

    return split_ska

def compile_ska(split_ska, target):
    to_bytes = lambda a, b=4: int.to_bytes(a, b, "big")
    new_ska = bytearray()

    anim_start = 128 if target.name != "World Tour" else 256
    bone_count = target.bone_count
    quats = split_ska["quats"]
    trans = split_ska["trans"]
    quat_start = anim_start
    trans_start = quat_start + len(quats)
    bonesize_quat_start = trans_start + len(trans)
    bonesize_trans_start = bonesize_quat_start + 256
    part_anim_start = bonesize_trans_start + (bone_count*2)
    part_anim_start += 0 if part_anim_start % 4 == 0 else 4 - part_anim_start % 4
    part_anim = target.partial_anim
    bone_start_diff = split_ska["bone_range_low"] - target.bone_range_low

    #Define bone sizes
    bonesize_quat = b''
    for x in range(0, target.bone_range_low):
        bonesize_quat += b'\x00'*2
    for x in split_ska["quat_sizes"].keys():
        bonesize_quat += int.to_bytes(split_ska["quat_sizes"][x], 2, "big")
    bonesize_quat += b'\x00' * (256 - len(bonesize_quat))

    bonesize_trans = b''
    for x in range(0, target.bone_range_low):
        bonesize_trans += b'\x00' * 2
    for x in split_ska["quat_sizes"].keys():
        bonesize_trans += int.to_bytes(split_ska["trans_sizes"][x], 2, "big")
    bonesize_trans += b'\x00' * ((bone_count*2) - len(bonesize_trans))
    bonesize_trans += b'' if len(bonesize_trans) % 4 == 0 else b'\x00' * (4 - len(bonesize_trans) % 4)

    filesize = part_anim_start + len(part_anim)

    #Set up ska file
    if target.name != "World Tour":
        new_ska += b'\x00' * 4 + b'\xff' * 4

    # raise Exception

    new_ska += to_bytes(filesize)
    new_ska += to_bytes(split_ska["anim_offset"])
    if target.name != "World Tour":
        new_ska += to_bytes(split_ska["null_offset"])
    else:
        new_ska += b'\x00' * 4
    new_ska += to_bytes(split_ska["bonepointers_offset"])
    if target.name == "World Tour":
        try:
            new_ska += to_bytes(split_ska["b_offset"])
        except:
            new_ska += b'\xff' * 4
        try:
            new_ska += to_bytes(split_ska["c_offset"])
        except:
            new_ska += b'\xff' * 4
    new_ska += to_bytes(part_anim_start)
    new_ska += to_bytes(split_ska["d_offset"])

    # Anim Header
    if target.name == "World Tour":
        new_ska += to_bytes(104)
    else:
        new_ska += to_bytes(72)
    new_ska += to_bytes(split_ska["flags"])
    new_ska += struct.pack(">f", split_ska["duration"])

    new_ska += to_bytes(split_ska["unk_byte"], 1)
    new_ska += to_bytes(bone_count, 1)
    new_ska += to_bytes(split_ska["unk_b"], 2)

    #Float Pairs
    for x in ["float_pair_1", "float_pair_2"]:
        for y in split_ska[x]:
            new_ska += struct.pack(">f", y)

    if target.name == "World Tour":
        new_ska += to_bytes(0, 32)

    new_ska += to_bytes(split_ska["unk_c"], 2)
    new_ska += to_bytes(split_ska["custom_keys"], 2)
    new_ska += to_bytes(split_ska["customkey_pos"])

    new_ska += to_bytes(quat_start)
    new_ska += to_bytes(trans_start)
    new_ska += to_bytes(bonesize_quat_start)
    new_ska += to_bytes(bonesize_trans_start)

    if len(new_ska) % 128 != 0:
        new_ska += b'\x00' * (128 - len(new_ska) % 128)

    new_ska += quats
    new_ska += trans

    new_ska += bonesize_quat
    new_ska += bonesize_trans

    new_ska += part_anim



    # raise Exception
    return new_ska

def main(ska_data, singer):
    split_ska = read_ska(ska_data)
    output_ska = compile_ska(split_ska, singer)
    return output_ska

def error_message():
    print("Not enough arguments to run this script. Please run this script with the ska file and your target")
    print("Or run this script with files in the 'in' folder and a ska target.")
    print("Allowable targets are:")
    for x in lipsync_dict.keys():
        print(f"\t{x}")
    # input()
    exit()

if __name__ == "__main__":

    if len(sys.argv) < 2:
        error_message()

    elif len(sys.argv) == 2:
        if sys.argv[1] not in lipsync_dict.keys():
            error_message()
        directory = "./in"
        out_dir = "./out"
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            with open(f, 'rb') as file:
                ska_data = file.read()
            # checking if it is a file
            if os.path.isfile(f):
                singer = lipsync_dict[sys.argv[1]]
                output_ska = main(ska_data, singer)
                try:
                    os.makedirs(out_dir)
                except:
                    pass
                with open(out_dir + "\\" + filename, 'wb') as f:
                    ska_file = f.write(output_ska)

    else:
        with open(sys.argv[1], 'rb') as f:
            ska_file = f.read()

        singer = lipsync_dict[sys.argv[2]]

        output_ska = main(ska_file, singer)

        out_dir = os.path.dirname(os.path.abspath(sys.argv[1])) +"\\ska_converts"
        try:
            os.makedirs(out_dir)
        except:
            pass

        with open(out_dir+"\\"+os.path.basename(sys.argv[1]), 'wb') as f:
            ska_file = f.write(output_ska)

    # raise Exception