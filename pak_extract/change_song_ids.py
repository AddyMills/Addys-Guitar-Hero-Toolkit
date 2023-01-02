"""
This script automates converting a song's id to another id.
It's kind of a special use case right now, but this will be updated for an easier conversion later.
"""
import sys
sys.path.append("../create_audio")
from PAKExtract import *
from create_audio.audio_functions import *
import os
import time


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

def generate_ids(shortname):
    id_list = [int.to_bytes(int(QBKey(shortname),16), 4, "big")]

    for x in ids_pre:
        id_list.append(int.to_bytes(int(QBKey(f"{shortname}{x}"),16), 4, "big"))

    for x in ids_post:
        id_list.append(int.to_bytes(int(QBKey(f"{x}{shortname}"), 16), 4, "big"))

    for x in ids_song:
        id_list.append(int.to_bytes(int(QBKey(f"songs\{shortname}{x}"), 16), 4, "big"))

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

    old_file_root = "03 Disk Files"
    new_file_root = "04 Re-Encrypted DLC Disk Files"



    for x in song_files:
        dlc_ids = generate_ids(x[0])
        filepath = f"{x[1]}\\{old_file_root}"
        savepath = f"{x[1]}\\{new_file_root}"
        for y in os.listdir(f"{filepath}"):
            if os.path.isfile(f"{filepath}\\{y}"):
                old_name = y.split("_")[0]
                old_ids = generate_ids(old_name)
                # raise Exception
                print(f"Switch song id references in {old_name} to {x[0]}")
                with open(f"{filepath}\\{y}", 'rb') as f:
                    decomp_pak = f.read()
                    if decomp_pak[:4] == b"CHNK":
                        decomp_pak = decompress_pak(decomp_pak)
                for i, z in enumerate(old_ids):
                    decomp_pak = decomp_pak.replace(z, dlc_ids[i])
                    # raise Exception
                with open(f"{savepath}\\b{x[0].lower()}_song.pak.xen", 'wb') as f:
                    f.write(decomp_pak)
            else:
                folderpath = f"{filepath}\\{y}"
                foldersavepath = f"{savepath}\\{y}"
                for z in os.listdir(f"{folderpath}"):
                    no_ext = file_renamer(os.path.basename(z[:-8]).lower())
                    key = generate_fsb_key(no_ext)
                    print(f"Processing {z}")
                    with open(f"{folderpath}\\{z}", 'rb') as f:
                        audio = f.read()
                    audio = decrypt_fsb4(audio, key)
                    if audio[:3] != b'FSB':
                        raise Exception("Error Decrypting. Please check your song name.")
                    print("Successfully Decrypted")
                    new_id = f"a{x[0]}{z[z.find('_'):z.find('.')]}"
                    no_ext = file_renamer(new_id.lower())
                    key = generate_fsb_key(no_ext)
                    print(f"Re-encrypting with id {no_ext}")
                    audio = encrypt_fsb4(audio, key)
                    print("Successfully Encrypted")
                    try:
                        os.makedirs(foldersavepath)
                    except:
                        pass
                    with open(f"{foldersavepath}\\a{no_ext}.fsb.xen", 'wb') as f:
                        f.write(audio)
                    # raise Exception
    t1 = time.process_time()
    print(t1 - t0)

