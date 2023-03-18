from ska_classes import ska_bytes, lipsync_dict
from ska_functions import make_gh5_ska, make_gh3_ska
import os

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

def debug_test(old, new):
    if old == new:
        result = "Success!!"
    else:
        result = "Failure!!"
    return result
def debug(func):
    with open(ska_9, 'rb') as f:
        ska_orig = f.read()
        ska_file = ska_bytes(ska_orig)
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
            ska_switch = lipsync_dict[kwargs["ska_switch"]]
        except Exception as e:
            print(e)
            ska_switch = 0
    else:
        ska_switch = 0
    directory = f"{root_folder}/in"
    out_dir = f"{root_folder}/out"
    with os.scandir(directory) as songs:
        for x in songs:
            with open(x, 'rb') as f:
                ska_orig = f.read()
                ska_file = ska_bytes(ska_orig)

            new_ska = func(ska_file, quats_mult = quats_mult, ska_switch = ska_switch)

            if write == True:
                with open(f"{out_dir}\\{x.name}", 'wb') as f:
                    f.write(new_ska)
            """result = debug_test(ska_orig, new_ska)
            print(x.name, result)"""

    return new_ska

if __name__ == "__main__":
    # debug(make_gh5_ska)
    main(make_gh3_ska, True, quats_mult = 0.5, ska_switch = "gh3_singer")