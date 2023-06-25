from ska_classes import ska_bytes, lipsync_dict
from ska_functions import make_modern_ska, make_gh3_ska
import os
import sys

ska_1 = "GHM_Singer_Male_One_1.ska.xen"

ska_2 = "GH3_Singer_Male_DreamPolice_1.ska.xen"

ska_3 = "G_SpinJumps01.ska.xen"

ska_4 = "SpinJump01_GUIT.ska.xen"

ska_5 = "Evil_S_01.ska.xen"

ska_6 = "Evil_S_01_1.ska.xen"

ska_7 = "WT_GH4_Singer_Female_Heartbreaker_1.ska.xen"

ska_8 = "Xport_GH4_Singer_Female_Heartbreaker_1.ska.xen"

ska_9 = "BeatIt_SingToCam_SING.ska.xen"

ska_10 = "BeatIt_SingToCam_SING_Camera01.ska.xen"

ska_11 = "GH3_Singer_JPface_BrightLight_1.ska.xen"

ska_12 = "gh3_singer_steven_loveinelev01.ska.xen"

ska_13 = "gh3_singer_male_med_singidle1.ska.xen"

ska_14 = "GH_Rocker_LarsU_HardRockFace_1.ska.xen"

ska_15 = ".\\heights\\gh_rocker_female_heels_med_d.ska.xen"

ska_16 = ".\\singleframe\\gh3_ped_default.ska.xen"

ska_17 = "gh3_camera_steven_loveinelev01.ska.xen"

ska_18 = "S_MoonwalkToSing.ska.xen"

def debug_test(old, new):
    if old == new:
        result = "Success!!"
    else:
        result = "Failure!!"
    return result

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
    with open("test.txt", "w") as f:
        f.write(t)
    return

def debug(func):
    with open(ska_18, 'rb') as f:
        ska_orig = f.read()
        ska_file = ska_bytes(ska_orig)
    #ska_to_text(ska_file)
    new_ska = func(ska_file, 1)
    debug_test(ska_orig, new_ska)
    return new_ska
def main(func, write = False, **kwargs):
    root_folder = os.path.realpath(os.path.dirname(__file__))
    if "quats_mult" in kwargs:
        quats_mult = kwargs["quats_mult"]
        kwargs.pop("quats_mult")
    else:
        quats_mult = 1

    if "ska_switch" in kwargs:
        try:
            ska_switch = kwargs["ska_switch"]
        except Exception as e:
            print(e)
            ska_switch = 0
    else:
        ska_switch = 0

    if "game" in kwargs:
        game = kwargs["game"]
    else:
        game = "GH3"
    directory = f"{root_folder}/in"
    out_dir = f"{root_folder}/out"
    with os.scandir(directory) as songs:
        for x in songs:
            with open(x, 'rb') as f:
                ska_orig = f.read()
                ska_file = ska_bytes(ska_orig)

            """if ska_file.comp_bits:
                print(x.name)
                continue
            else:
                continue"""
            new_ska = func(ska_file, game = game, quats_mult = quats_mult, ska_switch = ska_switch)

            if write == True:
                with open(f"{out_dir}\\{x.name}", 'wb') as f:
                    f.write(new_ska)
            """result = debug_test(ska_orig, new_ska)
            print(x.name, result)"""

    return new_ska

if __name__ == "__main__":
    if "-debug" in sys.argv:
        debug(make_modern_ska)
    else:
        main(make_modern_ska, True, game = "GHWT", quats_mult=1, ska_switch = "wt_rocker")