from ska_classes import ska_bytes

import os
import sys

def ska_to_text(ska):
    import ska_definitions as ska_def
    ska_type = ska.ska_source
    if ska_type == "gh3_singer":
        bone_dict = ska_def.gh3_singer_bones
    elif ska_type == "gh3_guitarist":
        bone_dict = ska_def.gh3_guitarist_bones
    elif ska_type == "gha_singer":
        bone_dict = ska_def.gha_singer_bones
    elif ska_type == "steve":
        bone_dict = ska_def.steve_bones
    elif ska_type == "dmc_singer":
        bone_dict = ska_def.dmc_bones
    elif ska_type == "wt_rocker":
        bone_dict = ska_def.wt_bones
    else:
        bone_dict = ska_def.blank_bones
    t = ""
    t += f"Duration: {ska.duration} seconds ({round(ska.duration * 60)} frames)\n"
    t += f"Unknown: {ska.unk_byte}\n"
    t += f"Bone Count: {ska.bone_count}\n"
    t += f"Number of quaternion changes (in all frames): {ska.quat_changes}\n"
    t += "Float pairs:\n"
    for fp in ska.float_pairs:
        t += f"\t{fp}\n"
    t += f"Number of translation changes (in all frames): {ska.trans_changes}\n\n"
    if ska.ska_source != "other":
        multiplier = 1 if ska.ska_source == "wt_rocker" else 2
        t += "\nQuaternions:\n"
        for bone, quats in ska.quat_frames.items():
            t += f"{bone_dict[bone]} (bone {bone}):\n" if bone_dict[bone] else f"Bone {bone}:\n"
            for frame, values in quats.items():
                t += f"\t{frame} "
                for num, xyz in enumerate(values):
                    if xyz > 32767:
                        xyz -= 65536
                    t += f"{xyz/32768*multiplier}"
                    if num != len(values)-1:
                        t += ", "
                    else:
                        t += "\n"
        t += "\nTranslations:\n"
        for bone, trans in ska.trans_frames.items():
            t += f"{bone_dict[bone]} (bone {bone}):\n" if bone_dict[bone] else f"Bone {bone}:\n"
            for frame, values in trans.items():
                t += f"\t{frame} "
                for num, xyz in enumerate(values):
                    t += f"{xyz}"
                    if num != len(values)-1:
                        t += ", "
                    else:
                        t += "\n"

    return t


def main(*args):
    root_folder = os.path.realpath(os.path.dirname(__file__))
    if len(args) > 1:
        with open(args[1], 'rb') as f:
            ska_orig = f.read()
            ska_file = ska_bytes(ska_orig)
        text_file = ska_to_text(ska_file)
        out_name = args[1][:args[1].find(".ska")]
        with open(f"{out_name}.txt", 'w') as f:
            f.write(text_file)
    else:
        directory = f"{root_folder}/in"
        out_dir = f"{root_folder}/out"
        with os.scandir(directory) as songs:
            for x in songs:
                if ".ska" in x.name:
                    with open(x, 'rb') as f:
                        ska_orig = f.read()
                        ska_file = ska_bytes(ska_orig)
                    text_file = ska_to_text(ska_file)
                    out_name = x.name[:x.name.find(".ska")]
                    with open(f"{out_dir}\\{out_name}.txt", 'w') as f:
                        f.write(text_file)


    return

if __name__ == "__main__":
    main(*sys.argv)