"""
This script automates converting an offical song and merging it with its animations.
It's kind of a special use case right now, but this will be updated for an easier conversion later.
"""
import sys
sys.path.append("../")
sys.path.append("../create_audio")
sys.path.append("../midqb_gen")
sys.path.append("../pak_extract")

from create_audio.audio_functions import *
from toolkit_functions import convert_to_5, pak2mid, modify_strobe
from midqb_gen import CreatePAK
from pak_extract import QB2Text, Text2QB
import os
import time

console = "xen"

ids_pre = ["_song_scripts",
           "_scriptevents",
           "_anim_notes",
           "_anim",
           "_drums_notes",
           "_scripts",
           "_cameras_notes",
           "_cameras",
           "_performance",
           "_crowd_notes",
           "_crowd",
           "_lightshow_notes",
           "_lightshow",
           "_facial",
           "_localized_strings"
           ]

ids_post = ["car_male_anim_struct_",
            "car_male_alt_anim_struct_",
            "car_female_anim_struct_",
            "car_female_alt_anim_struct_"]

ids_song = [".mid.qb",
            ".mid.qs",
            ".note",
            ".perf",
            ".perf.xml.qb",
            "_song_scripts.qb"
            ]

ghsh_reanim = {
    406: "CaughtInAMosh",
    409: "CultofPersonality",
    411: "FreeBird",
    412: "Freya",
    414: "HeartShapedBox",
    415: "HeyYou",
    416: "HitMeWithYourBestShot",
    417: "ILoveRockAndRoll",
    418: "IWannaRock",
    423: "MessageInABottle",
    424: "MissMurder",
    425: "MonkeyWrench",
    428: "NoOneKnows",
    429: "NothinButAGoodTime",
    430: "PlayWithMe",
    431: "PsychobillyFreakout",
    433: "RockAndRollAllNite",
    435: "ShoutAtTheDevil",
    442: "TheTrooper",
    447: "Woman",
    448: "YYZ",
}

def generate_ids(shortname):
    id_list = [int.to_bytes(int(QBKey(shortname),16), 4, "big")]

    for x in ids_pre:
        id_list.append(int.to_bytes(int(QBKey(f"{shortname}{x}"),16), 4, "big"))

    for x in ids_post:
        id_list.append(int.to_bytes(int(QBKey(f"{x}{shortname}"), 16), 4, "big"))

    for x in ids_song:
        id_list.append(int.to_bytes(int(QBKey(f"songs\\{shortname}{x}"), 16), 4, "big"))

    return id_list

if __name__ == "__main__":
    t0 = time.process_time()
    song_files = []
    filesfolder = sys.argv[1]

    with os.scandir(filesfolder) as songs:
        for x in songs:
            dlc_name = x.name.split(" - ")[0]
            filepath = x.path
            song_files.append([dlc_name, filepath])


    old_file_root = ""
    new_file_root = ""


    for x in song_files:
        filepath = f"{x[1]}"
        folderpath = os.path.dirname(filepath)
        just_file = os.path.basename(filepath)
        savepath = f"{x[1]}"
        pak_data = ""
        pak_anim = ""
        override_mid = ""
        if "bdlc" in just_file.lower():
            dlc_num = int(just_file[4:7])
            dlc_name = f"dlc{dlc_num}"
            print(f"Processing dlc{dlc_num}")
            song_name = f"{folderpath}\\{ghsh_reanim[dlc_num]}_song.pak.xen"
            qb_sections, file_headers, file_headers_hex, song_files_dlc = pak2mid(filepath, dlc_name)

            new_dlc = []
            for y in song_files_dlc:
                if any([".ska" in y["file_name"], ".perf" in y["file_name"]]):
                    continue
                elif ".mid.qb" in y["file_name"]:
                    mid_qb = QB2Text.convert_qb_file(QB2Text.qb_bytes(y["file_data"]), song_name, file_headers)
                    for z in mid_qb:
                        if "performance" in z.section_id:
                            z.make_empty(f"{dlc_name}_performance")
                        elif "cameras_notes" in z.section_id:
                            z.make_empty(f"{dlc_name}_cameras_notes")
                        elif "lightshow_notes" in z.section_id:
                            strobe_counter = 0
                            for enum, light in enumerate(z.section_data):
                                if enum % 2 == 0:
                                    continue
                                else:
                                    orig_note = light
                                    z.section_data[enum] = modify_strobe(light)
                                    if z.section_data[enum] != orig_note:
                                        strobe_counter += 1
                            if strobe_counter > 0:
                                print(f"Changed {strobe_counter} strobe lights")
                    result = StringIO()
                    orig_stdout = sys.stdout
                    sys.stdout = result
                    QB2Text.print_qb_text_file(mid_qb)
                    sys.stdout = orig_stdout
                    qb_text = result.getvalue()
                    mid_qb_bytes = Text2QB.main(qb_text , console="PC", endian="big", game="GH5")
                    y["file_data"] = mid_qb_bytes
                    new_dlc.append(y)
                    #print()
                else:
                    new_dlc.append(y)
            if "World Tour" in filesfolder:
                decomp_ska = True
            else:
                decomp_ska = False
            song_files_convert = convert_to_5(song_name, dlc_name, "gh5", decomp_ska = decomp_ska)
            for y in song_files_convert:
                if any([".ska" in y["file_name"], ".perf" in y["file_name"]]):
                    new_dlc.append(y)
                else:
                    continue
            try:
                os.mkdir(f"{folderpath}\\Re-animated")
            except:
                pass
            pak_file = CreatePAK.pakMaker([[y["file_data"], y["file_name"]] for y in new_dlc], dlc_name)
            with open(f"{folderpath}\\Re-animated\\bdlc{dlc_num}_song.pak.xen", "wb") as f:
                f.write(pak_file)
    t1 = time.process_time()
    print(t1 - t0)

