import sys
import os
import random
import re
import mido
import CRC
import numpy as np
import struct

root_folder = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{root_folder}\\pak_extract")
sys.path.append(f"{root_folder}\\midqb_gen")
sys.path.append(f"{root_folder}\\ska_converter")
sys.path.append(f"{root_folder}\\create_audio")
from pak_extract import PAKExtract, QB2Text, Text2QB
from midqb_gen import MidQbGen as mid_qb
from ska_converter.ska_functions import make_modern_ska, make_gh3_ska
from ska_converter.ska_classes import ska_bytes, lipsync_dict
from gh_sections import gh_sections
from toolkit_variables import *
from io import StringIO, BytesIO
from debug_qs import qs_debug
from copy import deepcopy
from CRC import qbkey_hex, QBKey
from dbg import checksum_dbg
from mido import MidiFile, MidiTrack, second2tick as s2t, Message, MetaMessage

orig_std = sys.stdout

round_time = PAKExtract.round_time

def set_std_out(loc):
    sys.stdout = loc


def cam_len_check(cam_len):
    if str(cam_len).endswith("34"):
        cam_len -= 1
    elif str(cam_len).endswith("66"):
        cam_len += 1
    return cam_len

def get_rhythm_headers(song_name):
    rhythm_parts = []
    rhythm_dict = {}
    for x in PAKExtract.charts:
        for y in PAKExtract.difficulties:
            if x == "song":
                rhythm_parts.append(f"{song_name}_{x}_aux_{y}")
            else:
                rhythm_parts.append(f"{song_name}_aux_{y}_{x}")

    for x in rhythm_parts:
        rhythm_dict[x] = int(PAKExtract.QBKey(x), 16)

    return rhythm_parts, rhythm_dict


def get_qs_strings(qs_bytes):
    qs_dict = {}
    qs_split = qs_bytes[2:].decode('utf-16-le').split("\n")
    for count, item in enumerate(qs_split):
        if item == "":
            continue
        qs_line = item.split(maxsplit=1)
        qs_line[1] = qs_line[1][1:-1].replace("\\L", "")
        qs_dict[int(qs_line[0], 16)] = qs_line[1]

    return qs_dict


def get_track_type(track_name):
    diffs = ["Easy", "Medium", "Hard", "Expert"]
    instrument = ["guitarcoop", "rhythmcoop", "rhythm"]
    if (any(x in track_name for x in diffs)):
        for x in diffs:
            if x in track_name:
                if "Battle" in track_name:
                    track_type = "Battle"
                elif "Star" in track_name:
                    track_type = "Star"
                else:
                    track_type = "Notes"
                track_diff = x
                for y in instrument:
                    if y in track_name:
                        track_play = y
                        break
                    else:
                        track_play = "song"
                return {"instrument": track_play, "track_type": track_type, "difficulty": track_diff}
    else:
        return {"track_type": track_name[track_name.find("_") + 1:]}


def pak2mid(pakmid, song_name):
    if type(pakmid) == bytes or type(pakmid) == bytearray:
        mid_bytes = pakmid
    elif pakmid.lower().endswith(".mid"):
        with open(os.devnull, "w") as fake:
            set_std_out(fake)
            mid_bytes, song_name = output_mid_gh3(pakmid, 170)
        set_std_out(orig_std)
    else:
        with open(pakmid, 'rb') as pak:
            mid_bytes = pak.read()
        mid_bytes = PAKExtract.check_decomp(mid_bytes, output_decomp=False)
    song_files = PAKExtract.main(mid_bytes, f"{song_name}_song.pak", toolkit_mode=True)
    song_names = [song_name]
    starts = ["a", "b", "c"]
    if song_name[0] in starts:
        song_names.append(song_name[1:])
    for x in song_files:
        if "0x" in x['file_name']:
            file_name_scrubbed = x['file_name'].replace("\\", "")
            if file_name_scrubbed.endswith(".qb"):
                qb_string = f'songs/{song_name}.mid.qb'
                crc_name = int(PAKExtract.QBKey(f'songs/{song_name}.mid.qb'), 16)
                try:
                    hex_name = int(file_name_scrubbed[:-3], 16)
                except:
                    continue
                if crc_name == hex_name:
                    mid_qb = qb_string
                    mid_data_bytes = x['file_data']
        elif ".mid.qb" in x['file_name']:
            mid_qb = x['file_name'].replace("\\", "")
            mid_data_bytes = x['file_data']
    if "mid_data_bytes" in locals():
        file_headers = {}
        for s_name in song_names:
            file_headers |= QB2Text.createHeaderDict(s_name)
        file_headers_hex = QB2Text.create_hex_headers(file_headers)
        qb_sections = QB2Text.convert_qb_file(QB2Text.qb_bytes(mid_data_bytes), song_name, file_headers)
    else:
        qb_sections = 0
        file_headers = 0
        file_headers_hex = 0

    return qb_sections, file_headers, file_headers_hex, song_files

'''def swap_checksums(filepath,):
    for y in os.listdir(f"{filepath}"):
        if os.path.isfile(f"{filepath}\\{y}"):
            # continue
            if "_song.pak.xen" in y.lower():
                pak_data = f"{filepath}\\{y}"
                old_name = y.split("_")[0]
                old_ids = generate_ids(old_name)
                # raise Exception
            elif "_anim" in y.lower():
                pak_anim = f"{filepath}\\{y}"
            elif ".mid" in y.lower():
                override_mid = f"{filepath}\\{y}"
                print(f"MIDI File: {y} found.")
            else:
                print(f"Unknown file {y} found. Skipping...")

            """ Only for BH/GH5 style PAKs
            with open(f"{filepath}\\{y}", 'rb') as f:
                decomp_pak = f.read()
                if decomp_pak[:4] == b"CHNK":
                    decomp_pak = decompress_pak(decomp_pak)
            for i, z in enumerate(old_ids):
                decomp_pak = decomp_pak.replace(z, dlc_ids[i])  
            """

        else:

            folderpath = f"{filepath}\\{y}"
            foldersavepath = f"{savepath}\\{y}"
            for z in os.listdir(f"{folderpath}"):
                file_console = file_renamer(os.path.basename(z[-3:]).lower())
                if file_console != console:
                    continue
                no_ext = file_renamer(os.path.basename(z[:-8]).lower())
                key = generate_fsb_key(no_ext)
                print(f"Processing {z}")
                with open(f"{folderpath}\\{z}", 'rb') as f:
                    audio = f.read()
                if audio[:3] != b'FSB':
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
                file_name = f"{foldersavepath}\\a{no_ext}.fsb.{console}"
                if console == "ps3":
                    file_name = file_name.upper()
                with open(file_name, 'wb') as f:
                    f.write(audio)
                # raise Exception
'''

def qb_2_sections(qb_sections):
    qb_array = []
    for x in qb_sections.keys():
        qb_array.append(qb_sections[x])
    result = StringIO()
    orig_stdout = sys.stdout
    sys.stdout = result
    QB2Text.print_qb_text_file(qb_array)
    sys.stdout = orig_stdout
    qb_text = result.getvalue()
    return qb_text


def sections_2_qb(qb_sections, console="PC", endian="big", game="GH3"):
    qb_text = qb_2_sections(qb_sections)
    qb_file = Text2QB.main(qb_text, console, endian, game)
    return qb_file


def add_to_dict(p_dict, t, entry):
    if t in p_dict:
        p_dict[t].append(entry)
    else:
        p_dict[t] = [entry] if type(entry) != list else entry
    return


def convert_to_gh3(pakmid, output=f'{os.getcwd()}', singer=lipsync_dict["gh3_singer"]):
    if not "_song.pak" in pakmid:
        warning = input(
            "WARNING: File does not appear to be a validly named mid PAK file. Do you want to continue? (Y/N): ")
        if not warning.lower().startswith("y"):
            return -1

    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")].lower()

    track_types = []
    qb_sections, file_headers, file_headers_hex, song_files = pak2mid(pakmid, song_name)
    rhythm_sections, rhythm_dict = get_rhythm_headers(song_name)

    ska_dict = {}
    for file in song_files:
        if file["file_name"].lower().endswith(".ska"):
            file["file_data"] = ska_bytes(file["file_data"])
            ska_dict[file["file_name"]] = file["file_data"]

    sections_dict = {}

    for x in qb_sections:
        if x.section_id in file_headers_hex.keys():
            x.set_new_id(file_headers_hex[x.section_id])
        if x.section_id not in rhythm_sections:
            sections_dict[x.section_id] = x

    new_cams = []

    # Swap camera cuts
    for x in sections_dict[f"{song_name}_cameras_notes"].section_data:
        try:
            if type(gha_to_gh3[x[1]]) == list:
                raise Exception("Fatal error when processing camera swaps.")
            else:
                x[1] = gha_to_gh3[x[1]]
                new_cams.append(x)
        except:
            print(f"Bad Camera Cut {x[1]} found. Skipping")

    # Remove Rhythm left-hand anims
    new_anims = []
    new_anims_type = []
    for x in sections_dict[f"{song_name}_anim_notes"].section_data:
        if x[1] > 94:
            new_anims.append(x)
            new_anims_type.append("ArrayInteger")
    sections_dict[f"{song_name}_anim_notes"].section_data = new_anims
    sections_dict[f"{song_name}_anim_notes"].subarray_types = new_anims_type

    for x in sections_dict[f"{song_name}_markers"].section_data:
        if x.data_value[1].data_type == "StructItemQbKeyString":
            x.data_value[1].data_type = "StructItemStringW"
            marker_hex = x.data_value[1].data_value
            if "markers_text" in marker_hex:
                new_marker = gh_sections[int(marker_hex[-8:], 16)]
            else:
                new_marker = "No Section Name"
            x.data_value[1].set_string_w(new_marker)
            x.data_value[1].data_value = new_marker

    # Delete GH:A Exclusive events (special mocap, Rhythm events, etc)
    perf_to_ignore = ['dummy_function', 'ChangeNodeFlag'.lower(), 'super_airbag_hide', "SpecialCamera_PlayAnim".lower(),
                      "Band_PlaySimpleAnim".lower(), "super_Shakin_guitar_unhide".lower(),
                      "super_Shakin_guitar_hide".lower()]
    to_ignore_start = ["Z_".lower()]
    new_perf = []
    stances = {"guitarist": [],
               "bassist": [],
               "vocalist": []}
    for x in sections_dict[f"{song_name}_performance"].section_data:
        if x.data_value[1].data_value.lower() in perf_to_ignore:
            continue
        elif x.data_value[1].data_value.lower() in allowed_anims_gha:
            continue

        elif x.data_value[1].data_value == 'Band_ChangeStance':
            stance = x.data_dict["params"]["stance"].lower()
            player = x.data_dict["params"]["name"]
            if player.lower() == "rhythm":
                continue

            if stance == "stance_d":
                # print()
                try:
                    if stances[player][-1].lower().endswith("a"):
                        x.data_dict["params"]["stance"] = "stance_b"
                    elif stances[player][-1].lower().endswith("b"):
                        x.data_dict["params"]["stance"] = "stance_c"
                    else:
                        x.data_dict["params"]["stance"] = "stance_a"
                except:
                    x.data_dict["params"]["stance"] = "stance_a"
                x.reprocess_dict()
            if player in stances:
                stances[player].append(stance)
        elif x.data_value[1].data_value == 'Band_PlayAnim':
            if x.data_value[2].struct_data_struct[0].data_value.lower() == "rhythm":
                continue
            anim = x.data_dict["params"]["anim"]
            player = x.data_dict["params"]["name"]
            if anim.lower() in gha_anim_swaps:
                x.data_dict["params"]["anim"] = gha_anim_swaps[x.data_dict["params"]["anim"].lower()]
                x.reprocess_dict()
        elif x.data_value[1].data_value.lower() in allowed_anims_gh3:
            pass
        else:
            for a_check in to_ignore_start:
                if not x.data_value[1].data_value.lower().startswith(a_check):
                    print(x.data_value[1].data_value)
            continue
        # else:
        new_perf.append(x)

    if not stances["vocalist"]:
        vox_stances = {}
        a_stances = []
        b_stances = [0]
        perf_dict = {}
        for x in new_perf:
            t = x.data_dict["time"]
            add_to_dict(perf_dict, t, x)
            if x.data_dict["scr"] == "Band_PlayFacialAnim":
                if x.data_dict["params"]["name"] == "vocalist":
                    a_time = t - 5000 if t > 5000 else 0
                    stance_a = PAKExtract.new_stance_gh3(a_time, "vocalist", "stance_b")
                    ska_length = round(ska_dict[f'{x.data_dict["params"]["anim"]}.ska'].duration * 1000)
                    b_time = t + ska_length + 1000
                    stance_b = PAKExtract.new_stance_gh3(b_time, "vocalist", "stance_a")
                    add_to_dict(vox_stances, a_time, stance_a)
                    a_stances.append(a_time)
                    add_to_dict(vox_stances, b_time, stance_b)
                    b_stances.append(b_time)
                    # print()
        if a_stances:
            for a, b in zip(a_stances, b_stances):
                if b == 0:
                    add_to_dict(perf_dict, a, vox_stances[a])
                elif a < b:
                    continue
                else:
                    add_to_dict(perf_dict, b, vox_stances[b])
                    add_to_dict(perf_dict, a, vox_stances[a])
            add_to_dict(perf_dict, b_stances[-1], vox_stances[b_stances[-1]])
            new_perf = []
            for perfs in sorted(list(perf_dict.keys())):
                for perf in perf_dict[perfs]:
                    new_perf.append(perf)
    sections_dict[f"{song_name}_performance"].set_data(new_perf)

    gh3_qb_sections = []
    for x in sections_dict.keys():
        gh3_qb_sections.append(sections_dict[x])

    result = StringIO()
    orig_stdout = sys.stdout
    sys.stdout = result
    QB2Text.print_qb_text_file(gh3_qb_sections)
    sys.stdout = orig_stdout
    gh3_text = result.getvalue()
    gh3_qb = Text2QB.main(gh3_text, "PC", "big")

    for x in song_files:
        x['file_name'] = x['file_name'].replace("\\", "")
        if x['file_name'] == f'songs/{song_name}.mid.qb':
            x["file_data"] = gh3_qb
        if ".ska" in x['file_name']:
            x["file_data"] = make_gh3_ska(x["file_data"], ska_switch=singer, quats_mult=0.5)

    gh3_array = []
    for x in song_files:
        gh3_array.append([x["file_data"], x['file_name']])

    # Create the song PAK file
    song_pak = mid_qb.pakMaker(gh3_array)

    # raise Exception

    return song_name, song_pak


def convert_to_gha(pakmid, output=f'{os.getcwd()}', singer=lipsync_dict["gha_singer"]):
    if "_song.pak" in pakmid:
        song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")]
    elif ".mid" in pakmid:
        print("MIDI file found for GHA conversion.")
        print("This tool cannot convert directly to GHA yet.")
        print("Converting to GH3 first.")
        song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find(".mid")]

    track_types = []
    qb_sections, file_headers, file_headers_hex, song_files = pak2mid(pakmid, song_name)
    rhythm_sections, rhythm_dict = get_rhythm_headers(song_name)
    rhythm_parts = []

    sections_dict = {}
    for x in qb_sections:
        if x.section_id in file_headers_hex.keys():
            x.set_new_id(file_headers_hex[x.section_id])
        sections_dict[x.section_id] = x

    for x in rhythm_sections:
        if x != f"{song_name}_song_aux_Expert":
            fake_section = PAKExtract.qb_section("SectionArray")
            fake_section.make_empty()
            fake_section.set_new_id(x)
            fake_section.set_pak_name(sections_dict[f"{song_name}_song_Expert"].section_pak_name)
            rhythm_parts.append(fake_section)
        else:
            rhythm_section = PAKExtract.qb_section("SectionArray")
            rhythm_section.set_new_id(x)
            rhythm_section.set_array_node_type("ArrayInteger")
            rhythm_section.set_data(sections_dict[f"{song_name}_song_Expert"].section_data)
            rhythm_section.set_pak_name(sections_dict[f"{song_name}_song_Expert"].section_pak_name)
            rhythm_parts.append(rhythm_section)

    # Swap camera cuts
    if not sections_dict[f"{song_name}_cameras_notes"].is_empty():
        for x in sections_dict[f"{song_name}_cameras_notes"].section_data:
            if type(gh3_to_gha[x[1]]) == list:
                x[1] = random.choice(gh3_to_gha[x[1]])
            else:
                x[1] = gh3_to_gha[x[1]]

    # Add left-hand anims to rhythm player
    if sections_dict[f"{song_name}_anim_notes"].section_data != [0, 0]:
        new_anims = []
        new_anims_type = []
        for x in sections_dict[f"{song_name}_anim_notes"].section_data:
            if x[1] in range(118, 128):
                new_anims.append([x[0], x[1] - 34, x[2]])
                new_anims_type.append("ArrayInteger")
            new_anims.append(x)
            new_anims_type.append("ArrayInteger")
        sections_dict[f"{song_name}_anim_notes"].section_data = new_anims
        sections_dict[f"{song_name}_anim_notes"].subarray_types = new_anims_type

    if not sections_dict[f"{song_name}_markers"].is_empty():
        for x in sections_dict[f"{song_name}_markers"].section_data:
            if x.data_value[1].data_type == "StructItemQbKeyString":
                x.data_value[1].data_type = "StructItemStringW"
                marker_hex = x.data_value[1].data_value
                if "markers_text" in marker_hex:
                    new_marker = gh_sections[int(marker_hex[-8:], 16)]
                else:
                    new_marker = "No Section Name"
                x.data_value[1].set_string_w(new_marker)
                x.data_value[1].data_value = new_marker

    # Add rhythm notes to total package
    gha_dict = {}
    for x in sections_dict.keys():
        if x != f"{song_name}_rhythm_Expert_StarBattleMode":
            gha_dict[x] = sections_dict[x]
        else:
            gha_dict[x] = sections_dict[x]
            for y in rhythm_parts:
                gha_dict[y.section_id] = y
    gha_qb_sections = []
    for x in gha_dict.keys():
        gha_qb_sections.append(gha_dict[x])

    result = StringIO()
    orig_stdout = sys.stdout
    sys.stdout = result
    QB2Text.print_qb_text_file(gha_qb_sections)
    sys.stdout = orig_stdout
    gha_text = result.getvalue()
    gha_qb = Text2QB.main(gha_text, "PC", "big")

    # QB2Text.output_qb_file(gha_qb_sections, output+f'\\{song_name}.txt')
    for x in song_files:
        x['file_name'] = x['file_name'].replace("\\", "")
        if x['file_name'] == f'songs/{song_name}.mid.qb':
            x["file_data"] = gha_qb
        if ".ska" in x['file_name']:
            if re.search("[0-9][bB]\.ska", x['file_name'].lower()):
                # raise Exception

                x["file_data"] = make_gh3_ska(ska_bytes(x["file_data"]), ska_switch=lipsync_dict["gha_guitarist"],
                                              quats_mult=2)
            else:
                x["file_data"] = make_gh3_ska(ska_bytes(x["file_data"]), ska_switch=singer, quats_mult=2)
            # raise Exception

    # Convert dict to array of arrays
    gha_array = []
    for x in song_files:
        gha_array.append([x["file_data"], x['file_name']])

    # Create the song PAK file
    song_pak = mid_qb.pakMaker(gha_array)

    return song_name, song_pak

    # raise Exception


def process_base_gh5(data_array, gh5_name, gh5_entry, size, modulo=1):
    gh5_base = mid_qb.gh5_base_entry()
    if data_array == [0, 0]:
        data_array = []
    elif data_array == [0] and gh5_name == "gh5_vocal_phrase":
        data_array = []
    gh5_base.process_vox(data_array, gh5_name, gh5_entry, size, modulo)
    return gh5_base


def read_qs_debug():
    qs_debug_qb = {}
    qs_vals = {}
    for x in qs_debug.keys():
        qs_debug_qb[int(CRC.QBKey(x), 16)] = qs_debug[x]
    # curr_folder = os.getcwd()
    with open(f"{root_folder}\\conversion_files\\qs_e.txt", encoding="utf-16-le") as f:
        qs_text = f.readlines()
    for x in qs_text:
        quoted_text = ""
        quote_mode = False
        for char in x:
            if char == "\"":
                quote_mode = not quote_mode
                continue
            if quote_mode:
                quoted_text += char
        if not quoted_text:
            continue
        placeholder = "zxcvasdfqwer"
        split_line = x.replace(quoted_text, placeholder)
        split_line = " ".join(split_line.split()).split(maxsplit=1)
        if len(split_line) == 2:
            new_text = split_line[1].replace(placeholder, quoted_text).replace("\"", "")
            qs_test = CRC.QBKey_qs(new_text)
            if int(qs_test, 16) == int(split_line[0], 16):
                qs_vals[int(split_line[0], 16)] = new_text
            else:
                print(f"Invalid qb key {split_line[0]} to {split_line[1]}")

    return qs_vals, qs_debug_qb


def note_2_bin(raw_file):
    n_info = bytearray()
    for note_item in raw_file.keys():
        item = raw_file[note_item]
        n_info += qbkey_hex(item.name)  # QB key of item type (hard drums, easy guitar, etc.)
        n_info += int.to_bytes(round(len(item.entries) / item.modulo), 4, "big")
        n_info += qbkey_hex(item.qb_string)  # QB key of entry type (instrument_note)
        n_info += int.to_bytes(item.size, 4, "big")
        if len(item.entries) != 0:
            if type(item) != mid_qb.gh5_base_entry:
                for enum, notes in enumerate(item.entries):
                    if type(item) == mid_qb.gh5_star_note:
                        n_info += int.to_bytes(notes, 4 if enum % 2 == 0 else 2, "big")
                    elif type(item) == mid_qb.gh5_instrument_note:
                        if item.qb_string == 'gh6_expert_drum_note':
                            n_info += int.to_bytes(notes, 1 if enum % 3 == 2 else 4, "big")
                        else:
                            n_info += int.to_bytes(notes, 4, "big")
                    elif type(item) == mid_qb.gh5_special_note:
                        n_info += int.to_bytes(notes, 4, "big")
            else:
                for enum, notes in enumerate(item.entries):
                    if item.name == "timesig":
                        n_info += int.to_bytes(notes, 4 if enum % 3 == 0 else 1, "big")
                    elif item.name == "fretbar":
                        n_info += int.to_bytes(notes, 4, "big")
                    elif item.name == "guitarmarkers":
                        n_info += int.to_bytes(notes if enum % 2 == 0 else int(notes, 16), 4, "big")
                    elif item.name == "vocals":
                        n_info += int.to_bytes(notes, 4 if enum % 3 == 0 else 2 if enum % 3 == 1 else 1, "big")
                    elif item.name == "vocalfreeform":
                        n_info += int.to_bytes(notes, 4 if enum % 3 != 2 else 2, "big")
                    elif item.name == "vocalphrase":
                        n_info += int.to_bytes(notes, 4, "big")
                    elif item.name == "vocallyrics" or item.name == "vocalsmarkers":
                        if enum % 2 == 0:
                            n_info += int.to_bytes(notes, 4, "big")
                        else:
                            utf_16 = b''
                            for letter in notes:
                                utf_16 += ord(letter).to_bytes(2, "big")
                            if len(utf_16) > item.size - 4:
                                print(
                                    f"{'Lyric' if item.name == 'vocallyrics' else 'Phrase'} \'{notes}\' is longer than {int((item.size - 4) / 2)} characters long.")
                                utf_16 = utf_16[:(item.size - 4)]
                                print(f"Truncating to {int((item.size - 4) / 2)} characters.")
                                print(
                                    f"{'Lyric' if item.name == 'vocallyrics' else 'Phrase'} is now {utf_16.decode('utf-16-be')}")
                            utf_16 += b'\x00' * ((item.size - 4) - len(utf_16))
                            # print(len(utf_16))
                            n_info += utf_16
                    elif item.name == "bandmoment":
                        n_info += int.to_bytes(notes, 4, "big")
    return n_info


def perf_2_bin(perf_file, song_name, loop_anims):
    p_info = bytearray()
    for x in ["autocutcameras", "momentcameras"]:
        item = perf_file[x]
        p_info += qbkey_hex(x)  # QB key of camera type
        p_info += int.to_bytes(round(len(item) / 3), 4, "big")
        p_info += qbkey_hex("gh5_camera_note")
        for enum, camera_cut in enumerate(item):
            p_info += int.to_bytes(camera_cut, 4 if enum % 3 == 0 else 2 if enum % 3 == 1 else 1, "big")
    if loop_anims:
        for x in ["Female", "Male"]:
            item = loop_anims[x]
            loop_bytes = b''
            for player in ["guitarist", "bassist", "vocalist"]:
                player_loops = b''
                for loop in item[player]:
                    player_loops += qbkey_hex(loop)
                player_loops += b'\x00' * (200 - len(player_loops))
                loop_bytes += player_loops
            loop_bytes += b'\x00' * 400
            for y in ["", "_alt"]:
                p_info += qbkey_hex(f"car_{x}{y}_anim_struct_{song_name}")
                p_info += int.to_bytes(1, 4, "big")
                p_info += qbkey_hex("gh6_actor_loops")
                p_info += loop_bytes
    else:
        for x in ["female", "male"]:
            item = perf_file[x]
            for y in ["", "_alt"]:
                p_info += qbkey_hex(f"car_{x}{y}_anim_struct_{song_name}")
                p_info += int.to_bytes(1, 4, "big")
                p_info += qbkey_hex("gh5_actor_loops")
                for anim_loop in item:
                    p_info += qbkey_hex(anim_loop)
    return p_info


def convert_to_gh5_bin(raw_file, file_type, song_name="", *args, **kwargs):
    if file_type == "note" or file_type == "perf":
        header = bytearray()
        header += b'\x40\xa0\x00\xd2' if file_type == "note" else b'\x40\xa0\x01\xa3'  # Game id
        header += qbkey_hex(song_name)  # DLC_id
        header += int.to_bytes(len(raw_file) if file_type == "note" else 6, 4, "big")  # Number of entries
        header += qbkey_hex(file_type)  # "Note" or "Perf" to hex
        header += b'\x00' * 12  # Padding
        if file_type == "note":
            return header + note_2_bin(raw_file)
        else:
            return header + perf_2_bin(raw_file, song_name, *args)
    elif file_type == "qs":
        qs_bin = bytearray()
        qs_bin += b'\xFF\xFE'
        for qs in raw_file:
            qs_key = CRC.QBKey_qs(qs)
            for char in qs_key:
                qs_bin += ord(char).to_bytes(2, "little")
            qs_bin += ord(" ").to_bytes(2, "little")
            qs_bin += ord("\"").to_bytes(2, "little")
            for char in qs:
                qs_bin += ord(char).to_bytes(2, "little")
            qs_bin += ord("\"").to_bytes(2, "little")
            qs_bin += b'\x0A\x00'  # new line
        qs_bin += b'\x0A\x00\x0A\x00'
        return qs_bin
    elif file_type in ["qb", "perf_xml"]:
        if "console" in kwargs and "endian" in kwargs:
            return sections_2_qb(raw_file, kwargs["console"], kwargs["endian"], game="GH5")
    else:
        raise Exception(f"Unknown file type {file_type} found")

    return


def reorg_qb(qb_file, song_name):
    new_qb = {}
    for x in ["_anim_notes", "_anim", "_drums_notes", "_scripts", "_cameras_notes", "_cameras", "_performance",
              "_crowd_notes", "_crowd", "_lightshow_notes", "_lightshow", "_facial", "_localized_strings"]:
        new_qb[f"{song_name}{x}"] = qb_file[f"{song_name}{x}"]
    return new_qb


def reorg_perfqb(qb_file):
    scripty = 0
    new_perf = {}
    for x in qb_file.keys():
        if x.endswith("scriptevents"):
            scripty = qb_file[x]
        else:
            new_perf[x] = qb_file[x]
    new_perf[scripty.section_id] = scripty

    return new_perf


def grab_debug_2(string, dbg_dict):
    if string.startswith("0x"):
        string = dbg_dict[f"0x{hex(int(string, 16))[2:].zfill(8)}"]
    return string


def gen_wt_anim_dict(song_name, file_headers):
    anim_data_dict = {}
    to_open = ["ghwt", "ghm", "ghsh", "ghvh"]

    for game in to_open:  # Grab all the animation structs to convert potentially
        with open(f"{root_folder}/conversion_files/{game}_guitar_animation_data.txt") as f:
            anim_data = Text2QB.main(f.read())
            anim_data = QB2Text.convert_qb_file(QB2Text.qb_bytes(anim_data), song_name, file_headers)
            for x in anim_data:
                if x.section_type == "SectionStruct":
                    if x.section_id not in anim_data_dict:
                        anim_data_dict[x.section_id] = x
    return anim_data_dict


def gen_wor_anim_sets():
    root_folder = os.path.realpath(os.path.dirname(__file__))
    wor_anim = {}
    anims = []
    anim_nogen = []
    with open(f"{root_folder}/conversion_files/wor_anim_sets.txt") as f:
        anim_data = Text2QB.main(f.read())
        anim_data = QB2Text.convert_qb_file(QB2Text.qb_bytes(anim_data), "0", {"0": "0"})
    for x in anim_data[0].data_dict.keys():
        anims.append(x.lower())

    return anims


def default_anim_structs():
    female_struct = {
        "guitar": {
            "pak": "L_GUIT_JeffS_LowKey_anims",
            "anim_set": "L_GUIT_JeffS_Lowkey_anims_set",
            "finger_anims": "guitarist_finger_anims_car_female",
            "fret_anims": "fret_anims_rocker",
            "strum_anims": "CAR_Female_Normal",
            "facial_anims": "facial_anims_female_rocker"
        },
        "bass": {
            "pak": "L_GUIT_JeffS_LowKey_anims",
            "anim_set": "L_GUIT_JeffS_Lowkey_anims_set",
            "finger_anims": "guitarist_finger_anims_car_female",
            "fret_anims": "fret_anims_rocker",
            "strum_anims": "CAR_Female_Normal",
            "facial_anims": "facial_anims_female_rocker"
        },
        "drum": {
            "pak": "L_DRUM_Loops_Standard_anims",
            "anim_set": "L_DRUM_Loops_standard_anims_set",
            "facial_anims": "facial_anims_female_rocker"
        },
        "vocals": {
            "pak": "L_SING_JeffS_LowKey_anims",
            "anim_set": "L_SING_JeffS_Lowkey_anims_set",
            "facial_anims": "facial_anims_female_rocker"
        }
    }
    male_struct = {
        "guitar": {
            "pak": "L_GUIT_JeffS_LowKey_anims",
            "anim_set": "L_GUIT_JeffS_Lowkey_anims_set",
            "finger_anims": "guitarist_finger_anims_car_male",
            "fret_anims": "fret_anims_rocker",
            "strum_anims": "CAR_male_Normal",
            "facial_anims": "facial_anims_male_rocker"
        },
        "bass": {
            "pak": "L_GUIT_JeffS_LowKey_anims",
            "anim_set": "L_GUIT_JeffS_Lowkey_anims_set",
            "finger_anims": "guitarist_finger_anims_car_male",
            "fret_anims": "fret_anims_rocker",
            "strum_anims": "CAR_male_Normal",
            "facial_anims": "facial_anims_male_rocker"
        },
        "drum": {
            "pak": "L_DRUM_Loops_Standard_anims",
            "anim_set": "L_DRUM_Loops_standard_anims_set",
            "facial_anims": "facial_anims_male_rocker"
        },
        "vocals": {
            "pak": "L_SING_JeffS_LowKey_anims",
            "anim_set": "L_SING_JeffS_Lowkey_anims_set",
            "facial_anims": "facial_anims_male_rocker"
        }
    }
    return female_struct, male_struct


def get_song_file_dict(song_files):
    song_files_dict = {}
    for key in song_files:
        song_files_dict[key["file_name"]] = key

    return song_files_dict


def get_section_dict(qb_sections, file_headers_hex):
    sections_dict = {}
    if not qb_sections:
        return sections_dict
    for x in qb_sections:
        if x.section_id in file_headers_hex.keys():
            x.set_new_id(file_headers_hex[x.section_id])
        sections_dict[x.section_id] = x
    return sections_dict


def perf_struct(female_struct, male_struct):
    wor_anims = gen_wor_anim_sets()
    for enum, struct in enumerate([female_struct, male_struct]):
        struct_perf = []
        for instrument in ["guitar", "bass"]:
            for perf_type in ["pak", "anim_set", "finger_anims", "fret_anims", "strum_anims", "facial_anims"]:
                if perf_type == "pak":
                    if struct[instrument]["pak"].lower() not in wor_anims:
                        input(f"{struct[instrument]['pak']} is not a WOR anim, please check")
                struct_perf.append(struct[instrument][perf_type])
        # Vocals anims in GH5/6 use 3 exclusive values, and 3 the same
        try:
            if struct["vocals"]["pak"].lower() not in wor_anims:
                input(f"{struct['vocals']['pak']} is not a WOR anim, please check")
        except:
            struct["vocals"] = {'pak': "L_SING_JeffS_LowKey_anims",'anim_set': "L_SING_JeffS_Lowkey_anims_set", 'facial_anims': f"facial_anims_{'fe' if enum == 0 else ''}male_rocker"}
        struct_perf += [struct["vocals"]["pak"], struct["vocals"]["anim_set"], "guitarist_finger_anims_car_female",
                        "fret_anims_rocker", "car_female_normal", struct["vocals"]["facial_anims"]]
        # Drums are all default
        struct_perf += ["L_GUIT_Jeffs_LowKey_anims", "L_GUIT_Jeffs_LowKey_anims_set",
                        "guitarist_finger_anims_car_female", "fret_anims_rocker", "car_female_normal",
                        "facial_anims_female_rocker"]
        for perf_type in ["L_DRUM_Loops_Standard_anims",
                          "l_drum_loops_standard_anims_set"]:  # GHM songs have custom drum loops. Don't use
            struct_perf.append(perf_type)
        struct_perf.append(struct["drum"]["facial_anims"])
        struct["perf"] = struct_perf.copy()

    return female_struct, male_struct


def compile_perf_anims(script_sections, anim_data_dict, use_anims=1, *args, **kwargs):
    perf_file = {}
    if not use_anims:
        female_struct, male_struct = default_anim_structs()
    else:
        male_struct = deepcopy(anim_struct)
        female_struct = deepcopy(anim_struct)
        female_anims = ["judita", "ginger", "morgan", "amanda", "debbie", "natalie", "haley"]
        special_anim_names = {
            "l_guit_chrisvance_bulls_anims": "L_GUIT_ChrisV_Bulls_F_anims",
            "l_guit_chrisvance_damnit_anims": "L_GUIT_ChrisV_Damnit_F_anims",
            "l_guit_chrisvance_joker_anims": "L_GUIT_ChrisV_Joker_F_anims",
            "l_guit_davidicus_bulls_anims": "L_GUIT_Davdics_Bulls_F_anims",
            "l_guit_davidicus_damnit2_anims": "L_GUIT_Davdics_Damnit2_F_anims",
            "l_guit_davidicus_damnit_anims": "L_GUIT_Davdics_Damnit_F_anims",
            "l_guit_davidicus_joker_anims": "L_GUIT_Davdics_Joker_F_anims",
            "l_guit_morgan_4horsemen_anims": "L_GUIT_Morgan_4Horse_M_anims",
            "l_guit_morgan_bleedingme_anims": "L_GUIT_Morgan_BleedMe_M_anims",
            "l_sing_morgan_bleedingns_anims": "L_SING_Morgan_BleedNS_M_anims",
            "l_guit_chrisvance_bulls_anims_set": "L_GUIT_ChrisV_Bulls_F_anims_set",
            "l_guit_chrisvance_damnit_anims_set": "L_GUIT_ChrisV_Damnit_F_anims_set",
            "l_guit_chrisvance_joker_anims_set": "L_GUIT_ChrisV_Joker_F_anims_set",
            "l_guit_davidicus_bulls_anims_set": "L_GUIT_Davdics_Bulls_F_anims_set",
            "l_guit_davidicus_damnit2_anims_set": "L_GUIT_Davdics_Damnit2_F_anims_set",
            "l_guit_davidicus_damnit_anims_set": "L_GUIT_Davdics_Damnit_F_anims_set",
            "l_guit_davidicus_joker_anims_set": "L_GUIT_Davdics_Joker_F_anims_set",
            "l_guit_morgan_4horsemen_anims_set": "L_GUIT_Morgan_4Horse_M_anims_set",
            "l_guit_morgan_bleedingme_anims_set": "L_GUIT_Morgan_BleedMe_M_anims_set",
            "l_sing_morgan_bleedingns_anims_set": "L_SING_Morgan_BleedNS_M_anims_set",
            "l_guit_joes_hot_150_anims": "L_GUIT_JoeS_Hot_150_anims",
            "l_guit_joes_hot_150_anims_set": "L_GUIT_JoeS_Hot_150_anims_set",
            "l_guit_dvdicus_bulls_150_anims": "L_GUIT_Dvdicus_Bulls_150_anims",
            "l_guit_dvdicus_bulls_150_anims_set": "L_GUIT_Dvdicus_Bulls_150_anims_set",
        }

        wt_anim_swap = {
            "l_sing_haley_joker_anims": "L_SING_Amanda_Joker_anims",
            "l_sing_haley_bulls_anims": "L_SING_Amanda_Bulls_anims",
            "l_sing_haley_dammit_anims": "L_SING_Amanda_Dammit_anims",
            "l_guit_jimi_joker_anims": "l_guit_dan_joker_anims",
            "l_sing_haley_joker_anims_set": "L_SING_Amanda_Joker_anims_set",
            "l_sing_haley_bulls_anims_set": "L_SING_Amanda_Bulls_anims_set",
            "l_sing_haley_dammit_anims_set": "L_SING_Amanda_Dammit_anims_set",
            "l_guit_jimi_joker_anims_set": "l_guit_dan_joker_anims_set",
            "l_guit_zakk_stillborn_anims": "L_GUIT_Sonny_Stillborn_anims",
            "l_guit_zakk_stillborn_anims_set": "L_GUIT_Sonny_Stillborn_anims_set",
            "l_guit_sting_demolition_anims": "L_GUIT_Dan_Joker_anims",
            "l_guit_sting_demolition_anims_set": "L_GUIT_Dan_Joker_anims_set"
        }

        no_swap = []

        for section in script_sections:
            if section.section_id == "0x6c8d898f":
                print("Found odd animation structs. Changing...")
                section.section_id = "car_male_anim_struct_dlc35"
                section.section_data[1].struct_data_struct[1].data_value = "L_GUIT_JoeS_AreYou_anims_set"
            if re.search(r"^(car_female|car_male)", section.section_id, flags=re.IGNORECASE):
                if re.search(r"(purplehaze|windcriesmary|dlc22|dlc23|dlc24|dlc92|dlc96|dlc97)$", section.section_id,
                             flags=re.IGNORECASE):
                    for anims in section.section_data:
                        if anims.data_type == "StructItemStruct":
                            if anims.data_id.lower() == "vocalist":
                                anims.data_id = "vocals"
                            if anims.data_id.lower() == "vocals":
                                anims.struct_data_struct[0].data_value = "L_SING_JeffS_LowKey_anims"
                                anims.struct_data_struct[1].data_value = "L_SING_JeffS_LowKey_anims_set"
                for anims in section.section_data:
                    anims.data_id = grab_debug_2(anims.data_id, checksum_dbg)
                    if anims.data_id == "drum":
                        anims.struct_data_struct[0].data_value = "L_DRUM_Loops_Standard_anims"
                        anims.struct_data_struct[1].data_value = "l_drum_loops_standard_anims_set"
                    if anims.data_id.lower() in anim_struct:
                        for anim_types in anims.struct_data_struct:
                            if anim_types.data_id == '0x0':
                                continue
                            anim_types.data_id = grab_debug_2(anim_types.data_id, checksum_dbg)
                            try:
                                anim_types.data_value = grab_debug_2(anim_types.data_value, checksum_dbg)
                            except:
                                if anim_types.data_id == "facial_anims":
                                    anim_types.data_value = f"facial_anims_{'fe' if 'female' in section.section_id else ''}male_rocker"
                            car_name = anim_types.data_value
                            if car_name.lower() in wt_anim_swap:
                                car_name = wt_anim_swap[car_name.lower()]
                            car_animator = car_name.split("_")[2].lower()
                            if car_animator in female_anims:
                                if "car_male" in section.section_id:
                                    if re.search(r"^L_", car_name, flags=re.IGNORECASE):
                                        if car_name.lower() in special_anim_names:
                                            car_name = special_anim_names[car_name.lower()]
                                        elif not re.search(r"^L_drum", car_name, flags=re.IGNORECASE):
                                            if not re.search(r"_M_", car_name, flags=re.IGNORECASE):
                                                f_pos = car_name.rfind("_anim")
                                                car_name = f"{car_name[:f_pos]}_M{car_name[f_pos:]}"
                                        # print()
                                    male_struct[anims.data_id.lower()][anim_types.data_id] = car_name
                                else:
                                    female_struct[anims.data_id.lower()][anim_types.data_id] = car_name
                            else:
                                if "car_female" in section.section_id:
                                    if re.search(r"^L_", car_name, flags=re.IGNORECASE):
                                        if car_name.lower() in special_anim_names:
                                            car_name = special_anim_names[car_name.lower()]
                                        elif not re.search(r"^L_drum", car_name, flags=re.IGNORECASE):
                                            if not re.search(r"_F_", car_name, flags=re.IGNORECASE):
                                                f_pos = car_name.rfind("_anim")
                                                car_name = f"{car_name[:f_pos]}_F{car_name[f_pos:]}"
                                        # print()
                                    female_struct[anims.data_id.lower()][anim_types.data_id] = car_name
                                else:
                                    male_struct[anims.data_id.lower()][anim_types.data_id] = car_name
            elif "Struct" in section.section_type:
                if section.section_id not in anim_data_dict:
                    anim_data_dict[section.section_id] = section
            else:
                pass

    female_struct, male_struct = perf_struct(female_struct, male_struct)

    perf_file["female"] = female_struct["perf"]
    perf_file["male"] = male_struct["perf"]
    return perf_file


def wt_to_5_file(sections_dict, qs_dict, song_name, new_name="", convert="gh5", *args, **kwargs):
    # If convert = False, it does not filter out illegal camera cuts
    # If set to a game ("gh3", "gha, "ghwt", "gh5"), it will convert or filter out illegal cameras
    if not new_name:
        new_name = song_name
    if "dlc" in new_name.lower():
        dlc_int = int(new_name[3:])
    else:
        dlc_int = 0
    note_file = {}
    qb_file = {}
    marker_names = {}
    qs_file = []
    qs_vals, qs_debug_qb = read_qs_debug()
    counter = 0

    for x in sections_dict.keys():
        if not re.search(r"(rhythmcoop|guitarcoop|aux)", x, flags=re.IGNORECASE):
            # Pull all note data
            sec_split = x.split("_")
            rhy_drum = re.search(r"(rhythm|drum)", x, flags=re.IGNORECASE)
            if re.search(r"(Easy|Medium|Hard|Expert)\Z", x, flags=re.IGNORECASE):
                if rhy_drum:
                    difficulty = sec_split[-1]
                    instrument = sec_split[-2]
                    if instrument.lower() == "rhythm":
                        instrument = "Bass"
                    else:
                        instrument = "Drums"
                else:
                    difficulty = sec_split[-1]
                    instrument = "Guitar"
                # print(f"Diff: {x}")
                note_chart = mid_qb.gh5_instrument_note(instrument, difficulty)
                note_chart.add_entry(
                    sections_dict[x].section_data if not sections_dict[x].array_node_type == "Floats" else -1)
                note_file[note_chart.name] = note_chart
                counter += 1
            elif re.search(r"(Expert_Star)\Z", x, flags=re.IGNORECASE):
                if rhy_drum:
                    instrument = sec_split[-3]
                    if instrument.lower() == "rhythm":
                        instrument = "Bass"
                    else:
                        instrument = "Drums"
                else:
                    instrument = "Guitar"
                difficulty = sec_split[-2]
                # print(f"Star: {x}")
                star_note = mid_qb.gh5_star_note(instrument, difficulty)
                star_note.add_array_entry(
                    sections_dict[x].section_data if not sections_dict[x].array_node_type == "Floats" else -1)
                # note_file[star_note.name] = star_note
                for diff in ["easy", "medium", "hard", "expert"]:
                    temp_ins = star_note.instrument.lower()
                    note_file[f"{temp_ins}{diff}starpower"] = mid_qb.gh5_star_note(instrument, diff.title())
                    note_file[f"{temp_ins}{diff}starpower"].add_array_entry(
                        sections_dict[x].section_data if not sections_dict[x].array_node_type == "Floats" else -1)
                counter += 4
            elif re.search(r"(Easy|Medium|Hard|Expert)_Tapping\Z", x, flags=re.IGNORECASE):
                if not re.search("(drum)", x, flags=re.IGNORECASE):
                    if rhy_drum:
                        instrument = sec_split[-3]
                        if instrument.lower() == "rhythm":
                            instrument = "Bass"
                    else:
                        instrument = "Guitar"
                    difficulty = sec_split[-2]
                    # print(f"Tapping: {x}")
                    tap_note = mid_qb.gh5_special_note(instrument, difficulty, "Tapping")
                    tap_note.add_array_entry(
                        sections_dict[x].section_data if not sections_dict[x].array_node_type == "Floats" else -1)
                    note_file[tap_note.name] = tap_note
                    counter += 1
            elif re.search(r"(_DrumFill)\Z", x, flags=re.IGNORECASE):
                # print(f"DrumFill: {x}")
                instrument = ""
                difficulty = sec_split[-2]
                drumfill_note = mid_qb.gh5_special_note(instrument, difficulty, "drumfill")
                drumfill_note.add_array_entry(
                    sections_dict[x].section_data if not sections_dict[x].array_node_type == "Floats" else -1)
                note_file[drumfill_note.name] = drumfill_note
                counter += 1
            elif re.search(r"(vocals|lyrics)", x, flags=re.IGNORECASE):
                if re.search(r"(markers)", x, flags=re.IGNORECASE):
                    # print(f"Vox Markers: {x}")
                    if not sections_dict[x].array_node_type == "Floats":
                        v_markers = []
                        for marker_struct in sections_dict[x].section_data:
                            v_markers.append(marker_struct.data_value[0].data_value)
                            if marker_struct.data_value[1].data_type != "StructItemString":
                                try:
                                    v_markers.append(qs_dict[marker_struct.data_value[1].data_value])
                                except:
                                    v_markers.append("")
                            else:
                                new_marker = marker_struct.data_value[1].struct_data_string.replace("\\L", "")
                                v_markers.append(new_marker)
                    else:
                        v_markers = [0, 0]
                    note_file["vocalsmarkers"] = process_base_gh5(v_markers, "gh5_vocal_marker_note", "vocalsmarkers",
                                                                  260, 2)
                elif re.search(r"(freeform)", x, flags=re.IGNORECASE):
                    # print(f"Vox Freeform: {x}")
                    note_file["vocalfreeform"] = process_base_gh5(sections_dict[x].section_data,
                                                                  "gh5_vocal_freeform_note", "vocalfreeform", 10, 3)
                elif re.search(r"(phrases)", x, flags=re.IGNORECASE):
                    # print(f"Vox Phrases: {x}")
                    note_file["vocalphrase"] = process_base_gh5(sections_dict[x].section_data[::2], "gh5_vocal_phrase",
                                                                "vocalphrase", 4)
                elif re.search(r"(note_range)", x, flags=re.IGNORECASE):
                    # print(f"Vox Note Range: {x}")
                    pass
                elif re.search(r"(lyrics)\Z", x, flags=re.IGNORECASE):
                    # print(f"Vox Lyrics: {x}")
                    if not sections_dict[x].array_node_type == "Floats":
                        lyrics = []
                        for lyric_struct in sections_dict[x].section_data:
                            lyrics.append(lyric_struct.data_value[0].data_value)
                            if lyric_struct.data_value[1].data_type != "StructItemString":
                                lyrics.append(qs_dict[lyric_struct.data_value[1].data_value])
                            else:
                                new_lyric = lyric_struct.data_value[1].struct_data_string.replace("\\L", "")
                                lyrics.append(new_lyric)
                    else:
                        lyrics = [0, 0]
                    note_file["vocallyrics"] = process_base_gh5(lyrics, "gh5_vocal_lyric", "vocallyrics", 68, 2)
                else:
                    # print(f"Vox Notes: {x}")
                    note_file["vocals"] = process_base_gh5(sections_dict[x].section_data, "gh5_vocal_note", "vocals", 7,
                                                           3)
                counter += 1
            elif re.search(r"(_timesig)\Z", x, flags=re.IGNORECASE):
                # print(f"Time Sigs: {x}")
                note_file["timesig"] = mid_qb.gh5_base_entry()
                note_file["timesig"].set_type("Timesig")
                note_file["timesig"].set_qb_string("gh5_timesig_note")
                note_file["timesig"].set_name("timesig")
                note_file["timesig"].set_modulo(3)
                note_file["timesig"].set_size(6)
                for timesig in sections_dict[x].section_data:
                    note_file["timesig"].add_item(timesig)
                counter += 1
            elif re.search(r"(_fretbars)\Z", x, flags=re.IGNORECASE):
                # print(f"Fret Bars: {x}")
                note_file["fretbar"] = mid_qb.gh5_base_entry()
                note_file["fretbar"].set_type("Fretbar")
                note_file["fretbar"].set_qb_string("gh5_fretbar_note")
                note_file["fretbar"].set_name("fretbar")
                note_file["fretbar"].add_item(sections_dict[x].section_data)
                note_file["fretbar"].set_size(4)
                counter += 1
            elif re.search(r"(_guitar_markers)\Z", x, flags=re.IGNORECASE):
                # print(f"Section Markers: {x}")
                g_markers = []
                qb_file[f"{new_name}_localized_strings"] = PAKExtract.qb_section("SectionArray")
                qb_file[f"{new_name}_localized_strings"].set_array_node_type("ArrayQbKeyStringQs")
                qb_file[f"{new_name}_localized_strings"].set_pak_name(f"songs/{new_name}.mid.qb")
                qb_file[f"{new_name}_localized_strings"].set_new_id(f"{new_name}_localized_strings")
                section_errors = 0
                for marker_struct in sections_dict[x].section_data:
                    g_markers.append(marker_struct.data_value[0].data_value)
                    str_start = '\\u[m]'
                    str_check = '\\L_ENDOFSONG'
                    if marker_struct.data_value[1].data_type != "StructItemString" and marker_struct.data_value[
                        1].data_type != "StructItemStringW":
                        try:
                            try:
                                qs_key = QBKey(marker_struct.data_value[1].data_value)
                                qs_1 = qs_debug_qb[int(qs_key, 16)]
                                qs_2 = f"{str_start if qs_vals[qs_1] != str_check else ''}{qs_vals[qs_1]}"
                                qs_file.append(qs_2)
                                marker_names[qs_vals[qs_1]] = g_markers[-1]
                                g_markers.append(CRC.QBKey_qs(qs_2))
                                qb_file[f"{new_name}_localized_strings"].section_data.append(
                                    hex(int(CRC.QBKey_qs(qs_2), 16)))
                            except Exception as E:
                                temp_marker = f"Section {section_errors}"
                                qs_2 = f"{str_start}{temp_marker}"
                                section_errors += 1
                                qs_file.append(qs_2)
                                marker_names[temp_marker] = g_markers[-1]
                                g_markers.append(CRC.QBKey_qs(qs_2))
                                qb_file[f"{new_name}_localized_strings"].section_data.append(
                                    hex(int(CRC.QBKey_qs(qs_2), 16)))
                        except Exception as E:
                            raise E
                            g_markers.append("")
                            print(f"Failed to find section marker in {new_name} at {g_markers[-1]}")
                    else:
                        if marker_struct.data_value[1].data_type.endswith("W"):
                            new_marker = marker_struct.data_value[1].struct_data_string_w
                        else:
                            new_marker = marker_struct.data_value[1].struct_data_string
                        marker_names[new_marker] = g_markers[-1]
                        new_marker = f"{str_start if new_marker != str_check else ''}{new_marker}"
                        qs_file.append(new_marker)
                        g_markers.append(CRC.QBKey_qs(new_marker))
                        qb_file[f"{new_name}_localized_strings"].section_data.append(
                            hex(int(CRC.QBKey_qs(new_marker), 16)))
                        # g_markers.append(new_marker)

                note_file["guitarmarkers"] = process_base_gh5(g_markers, "gh5_marker_note", "guitarmarkers", 8, 2)

            # Pull perf data
            elif re.search(r"(_cameras_notes)\Z", x, flags=re.IGNORECASE):
                cameras = mid_qb.gh5_cameras(convert)
                cameras.add_entry(sections_dict[x].section_data)

            # Pull qb file data
            elif re.search(r"(_anim_notes|_anim|_drums_notes|_scripts|_cameras_notes|_cameras|performance|crowd_notes|"
                           r"crowd|lightshow_notes|lightshow)\Z", x, flags=re.IGNORECASE):
                if song_name in x:
                    new_qb = x.replace(song_name, new_name)
                elif song_name[1:] in x:
                    new_qb = x.replace(song_name[1:], new_name)
                else:
                    raise Exception
                qb_file[new_qb] = sections_dict[x]
                qb_file[new_qb].swap_names(song_name, new_name)

    if f"{song_name}_ghost_notes" in sections_dict and "wor" in args:
        qs_file.append("ghost")
        edits = note_file["drumsexpertinstrument"]
        edits.qb_string = "gh6_expert_drum_note"
        edits.size = 9
        edits.modulo = 3
        times = edits.entries[::2]
        notes = edits.entries[1::2]
        times_dict = {}
        for i, j in zip(times, notes):
            times_dict[i] = split_note_vals(j)
        for ghost in sections_dict[f"{song_name}_ghost_notes"].section_data:
            times_dict[ghost[0]].append(ghost[1])
            times_dict[ghost[0]][1] -= ghost[1]
        new_notes = []
        for k, v in times_dict.items():
            new_notes.extend([k, combine_note_vals(v)])
            if len(v) == 4:
                new_notes.append(v[3])
            else:
                new_notes.append(0)
        edits.entries = new_notes


    return note_file, qb_file, qs_file, cameras, marker_names

def split_note_vals(value):
    return [
        (value >> 16) & 0xFFFF,
        (value >> 8) & 0xFF,
        value & 0xFF
    ]

def combine_note_vals(value):
    return (value[0] << 16) | (value[1] << 8) | value[2]


def check_ska_anims(anim_skas, song_files_dict, other_skas):
    for ska in anim_skas.keys():
        if f"{anim_skas[ska]}.ska" not in song_files_dict:
            if f"{anim_skas[ska].lower()}" in other_skas:
                with open(other_skas[anim_skas[ska].lower()], 'rb') as f:
                    new_anim = f.read()
                song_files_dict[f"{anim_skas[ska]}.ska"] = {
                    "file_name": f"{anim_skas[ska]}.ska", "file_data": new_anim}
    return song_files_dict

def parse_anim_loops():
    with open(f"{root_folder}\\anim_loops.txt", "r") as f:
        anim_file = f.readlines()
    anim_loops = {}
    for x in anim_file:
        try:
            if re.search(r'_c0[1-9]$', x, flags = re.IGNORECASE):
                anim_loops[x.strip()[:-4]].append(x.strip())
            else:
                anim_loops[x.strip()] = []
        except:
            #print(f"{x} failed to parse")
            pass
    return anim_loops



def modify_strobe(n):
    # Extract the 2nd 8-bit integer
    second_byte = (n & 0x00ff0000) >> 16
    strobe_mod = 0
    # If it equals 60, modify it to be 58
    if second_byte == 60:
        # Clear the second byte
        n = n & 0xff00ffff

        # Set the second byte to 58
        n = n | (58 << 16)

    return n


def convert_to_5(pakmid, new_name, *args, **kwargs):
    root_folder = os.path.realpath(os.path.dirname(__file__))
    if "song_name" in kwargs:
        song_name = kwargs["song_name"]
    else:
        if not "_song.pak" in pakmid.lower() and not "_s.pak" in pakmid.lower():
            warning = input(
                "WARNING: File does not appear to be a validly named mid PAK file (ending in '_song.pak'). Do you want to continue? (Y/N): ")
            if not warning.lower().startswith("y"):
                return -1

        if "_song.pak" in pakmid.lower():
            song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")].lower()
        else:
            song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_s.pak")].lower()

        if song_name[1:4] == "dlc":
            song_name = song_name[1:]

    anim_loop_master = parse_anim_loops()

    other_skas = {}
    for x in os.scandir(f"{root_folder}\\conversion_files\\ska"):
        other_skas[x.name[:x.name.find(".ska.xen")].lower()] = x.path

    qb_sections, file_headers, file_headers_hex, song_files = pak2mid(pakmid, song_name)
    vox_star_entry = []  # Setting this up now since there's a chance it can be overridden later.
    ghost_notes = []
    # This will make comparisons easier later on.
    for section in qb_sections:
        if re.search(rf'{song_name}_vox_sp', section.section_id, flags=re.IGNORECASE):
            vox_star_entry = section.section_data

    anim_pak = 0
    drum_anim, override_sections, override_midqs = 0, 0, 0
    simple_anim = 0
    if "wt_mode" in args:
        wt_mode = 1
    else:
        wt_mode = 0
    if kwargs:
        if "anim_pak" in kwargs:
            anim_pak = kwargs["anim_pak"]
        else:
            anim_pak = 0
        if "override_mid" in kwargs:
            try:
                override_mid = MidiFile(kwargs["override_mid"])
                override_tempo = mid_qb.get_song_tempo_data(override_mid)
                override_args = ["2x_kick", "gh5_mode"]
                if "wor" in args:
                    override_args.append("wor")
                if "force_only" in args:
                    override_args.append("force_only")
                override_parsed = mid_qb.parse_wt_qb(override_mid, 170, *override_args)
                override_sections, override_midqs = mid_qb.create_wt_qb_sections(override_parsed, song_name)
                if override_midqs:
                    override_midqs = get_qs_strings(override_midqs)
                for track in override_mid.tracks:
                    if track.name == "drums":
                        override_sections[f"{song_name}_drums_notes"].section_data = mid_qb.make_wt_drum_anims(track,
                                                                                                               override_tempo)
                        override_sections[f"{song_name}_drums_notes"].item_data = override_sections[
                            f"{song_name}_drums_notes"].section_data
                        override_sections[f"{song_name}_drums_notes"].array_type = "Integer"
                        break
                if override_parsed["vox_sp"]:
                    vox_star_entry = override_parsed["vox_sp"]
                temp_sections = {}
                for x, y in override_sections.items():
                    if any(["timesig" in x, "fretbars" in x, y.item_data == ["Empty"]]):
                        continue
                    if "vocals_note_range" in x:
                        continue
                    temp_sections[x] = y
                override_sections = mid_qb.create_wt_qb(temp_sections, song_name)
                override_sections = QB2Text.convert_qb_file(QB2Text.qb_bytes(override_sections), song_name,
                                                            file_headers)
                del (temp_sections)
                del (override_mid)
            except Exception as E:
                # raise E
                drum_anim, override_sections, override_midqs = 0, 0, 0
        if "simple_anim" in kwargs:
            simple_anim = 1
        if "decomp_ska" in kwargs:
            if kwargs["decomp_ska"]:
                print("Converting World Tour SKA files to GHM+ format")
                for x in song_files:
                    # continue
                    if x["file_name"].lower().endswith("ska"):
                        to_compare = 0
                        other_ska_check = x["file_name"][:-4].lower()
                        if "gh3_hnd" in x["file_name"].lower():
                            print("Skipping Hand Chord File")
                            continue
                        elif "male_strum_jimi" in x["file_name"].lower():
                            print("Skipping Hand Strum File")
                            continue
                        elif other_ska_check in other_skas:
                            with open(other_skas[other_ska_check], 'rb') as f:
                                uncomp_ska = f.read()
                            to_compare = uncomp_ska
                            del(uncomp_ska)
                        #print(f"Converting {x['file_name']}")
                        if to_compare:
                            converted = make_modern_ska(ska_bytes(x["file_data"]), game="GH5")
                            # print(f"Using lower-size {'converted' if len(converted) < len(to_compare) else 'borrowed'} {x['file_name']}")
                            x["file_data"] = converted if len(converted) < len(to_compare) else to_compare
                            #print()
                        else:
                            # print(f"Using converted {x['file_name']}")
                            x["file_data"] = make_modern_ska(ska_bytes(x["file_data"]), game="GH5")
                print("Done!")
    song_file_len = len(song_files)
    if anim_pak:
        anim_file = pak2mid(anim_pak, song_name)[3]
        song_files += anim_file
        use_anims = 0  # This assumes that _anim comes from GHM or VH
        # This will also not use drum mocap data
    else:
        use_anims = 1

    song_files_dict = get_song_file_dict(song_files)
    sections_dict = get_section_dict(qb_sections, file_headers_hex)

    # Create Note, Perf, song_scripts, etc. files

    script_sections = []
    for files in song_files:
        if re.search(fr"songs/{song_name}\.mid\.qs", files["file_name"], flags=re.IGNORECASE):
            qs_dict = get_qs_strings(files["file_data"])
        elif re.search(fr"songs/{song_name}_song_scripts\.qb", files["file_name"], flags=re.IGNORECASE):
            script_sections = QB2Text.convert_qb_file(QB2Text.qb_bytes(files["file_data"]), song_name, file_headers)

    if "qs_dict" not in locals():
        qs_dict = 0
    if override_midqs:
        qs_dict = override_midqs
    if override_sections:
        for x in override_sections:
            sections_dict[x.section_id] = x
            print(f"Injecting {x.section_id} into song")
    perf_xml_file = {}
    perf_xml_file[f"{new_name}_scriptevents"] = PAKExtract.qb_section("SectionArray")
    perf_xml_file[f"{new_name}_scriptevents"].set_pak_name(f"songs/{new_name}.perf.xml.qb")
    perf_xml_file[f"{new_name}_scriptevents"].set_new_id(f"{new_name}_scriptevents")
    perf_xml_file[f"{new_name}_scriptevents"].set_array_node_type("ArrayStruct")

    anim_data_dict = gen_wt_anim_dict(song_name, file_headers)  # Dictionary for all special animations

    note_file, qb_file, qs_file, cameras, marker_names = wt_to_5_file(sections_dict, qs_dict, song_name, new_name, "gh5", *args)

    other_flags = []
    loop_anims = {
        "vocalist": [],
        "bassist": [],
        "guitarist": []
    }
    if f"{song_name}_double_kick" in sections_dict or f"{song_name}_ghost_notes" in sections_dict:
        other_flags.append("double_kick")

    if script_sections:
        for x in script_sections:
            if "struct" in x.section_id:
                perf_file = compile_perf_anims(script_sections, anim_data_dict, use_anims)
                break
        else:
            perf_file = compile_perf_anims(script_sections, anim_data_dict, 0)
    else:
        perf_file = compile_perf_anims(script_sections, anim_data_dict, 0)
    check_150 = []
    for gender in ["male", "female"]:
        for x in perf_file[gender]:
            if x == "L_GUIT_Dvdicus_Bulls_150_anims":
                if "Guit_Davidicus_Bulls_150" not in check_150:
                    check_150.append("Guit_Davidicus_Bulls_150")
            elif x == "L_GUIT_JoeS_Hot_150_anims":
                if "guit_joes_hot_150_01" not in check_150:
                    check_150.append("guit_joes_hot_150_01")
    perf_file["autocutcameras"] = cameras.autocut
    perf_file["momentcameras"] = cameras.moment

    for qb_item in ["cameras_notes", "facial"]:
        qb_file[f"{new_name}_{qb_item}"] = PAKExtract.qb_section("SectionArray")
        qb_file[f"{new_name}_{qb_item}"].make_empty()
        qb_file[f"{new_name}_{qb_item}"].set_pak_name(f"songs/{new_name}.mid.qb")
        qb_file[f"{new_name}_{qb_item}"].set_new_id(f"{new_name}_{qb_item}")
    if not vox_star_entry:
        vox_star_entry = gen_vox_sp(song_name, note_file)

    # print(counter)
    vox_star = mid_qb.gh5_star_note("Vocal", "")
    vox_star.add_item(vox_star_entry)
    note_file["vocalstarpower"] = vox_star
    check_dbg = lambda a: [a, hex(int(CRC.QBKey(a), 16))]
    # Convert performance Struct Array to perf_xml
    allowed_converts = ["SetSongHandCamParams", "Band_ChangeFacialAnims", "Band_PlayIdle", "Band_PlayFacialAnim",
                        "Band_PlayClip", "BandPlayClip", "CameraCutsEffect_FOVPulse", "Band_SetAnimTempo",
                        "Band_HideMic", "Band_ShowMic", "Band_HideMic_stand", "Band_EnableAutoChords",
                        "Band_EnableAutoFret", "Band_SetIKChainTarget", "Band_DisableAutoChords",
                        "Band_DisableAutoFret", "Band_EnableAutoStrums", "Band_DisableAutoStrums",
                        "Band_ForceAllToIdle", "Band_ShowMicStand", "Band_HideMicStand", "Band_ShowMic_Stand",
                        "Band_MoveToNode", "band_setikchain", "Band_PlayRockinFacialAnim", "Band_ShowMic_microphone",
                        "Band_HideMic_microphone", "Band_ClearAnimTempo", "Band_PlayLoop"]
    allowed_converts += [hex(int(CRC.QBKey(x), 16)) for x in allowed_converts]
    ignored_converts = ["Band_PlaysimpleAnim", "dummy_function", "Band_SetStrumStyle", "VH_UndergroundLogo_On",
                        "VH_UndergroundLogo_Off", "Crowd_StartLighters", "Crowd_StopLighters"]
    ignored_converts += [hex(int(CRC.QBKey(x), 16)) for x in ignored_converts]

    params_check = ["ff_anims", "mf_anims"]
    params_check += [hex(int(CRC.QBKey(x), 16)) for x in params_check]

    # First add some looping anims
    for x in ["guitarist", "bassist", "vocalist", "drummer"]:
        perf_xml_file[f"{new_name}_scriptevents"].section_data.append(PAKExtract.new_play_loop(0, x))

    play_clip_count = 0
    last_clip_start = 0
    last_clip_end = 0
    clips_processed = []
    try:
        first_moment = cameras.moment[0] if cameras.moment[0] != 0 else cameras.moment[3]
    except:
        first_moment = 1
    first_bass = get_first_note(note_file["bassexpertinstrument"].entries)
    first_guit = get_first_note(note_file["guitarexpertinstrument"].entries)
    first_note = int(round(min(first_moment, cameras.autocut[6], first_bass, first_guit) / 1000 * 30))
    if "super_gimp" in args:
        perf_file["momentcameras"] = []
    moment_cams = perf_file["momentcameras"][::3]
    autocut_cams = perf_file["autocutcameras"][::3]
    orig_clip_times = {}
    all_anims_used = []
    loop_genders = {
        "Male": {
            "vocalist": [],
            "bassist": [],
            "guitarist": []
        },
        "Female": {
            "vocalist": [],
            "bassist": [],
            "guitarist": []
        }
    } # This is for WoR generation only, and only if Band_PlayLoop exists in the song
    if qb_file[f"{new_name}_performance"].array_node_type != "Floats":
        print("Converting Performance array")
        wt_clip_time = []
        if wt_mode:
            for x in qb_file[f"{new_name}_performance"].section_data:
                if x.data_dict["scr"] == "Band_PlayClip":
                    wt_clip_time.append(round_time(x.data_dict["time"]))
            if new_name == "DLC292":
                wt_clip_time = sorted(wt_clip_time + [2767, 40233])
        else:
            wt_clip_time = [0]

        for x in qb_file[f"{new_name}_performance"].section_data:
            for struct_num, script_val in enumerate(x.data_value):
                if script_val.data_value in allowed_converts:
                    if script_val.data_value in check_dbg("Band_ChangeFacialAnims"):
                        """if simple_anim:
                            continue"""
                        if "0xa8f45644" in x.data_dict["params"].keys():
                            x.data_value[2].struct_data_struct[1].data_id = "ff_anims"
                            x.data_value[2].struct_data_struct[2].data_id = "mf_anims"
                            print("Fixing broken facial marker")
                        if x.data_value[2].struct_data_struct[0].data_id == "0x0":
                            x.data_value[2].struct_data_struct[0].data_id = "name"
                            x.data_dict["params"]["name"] = x.data_dict["params"]["0x0"]
                            print("Fixing broken name marker")
                        for y in x.data_dict["params"].keys():
                            if y in check_dbg("ff_anims") or y in check_dbg("mf_anims"):
                                if x.data_dict["params"]["name"].lower() == "basssist":
                                    x.data_value[2].struct_data_struct[0].data_value = "bassist"
                                perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
                                break
                            elif y in check_dbg("fa_type"):
                                if x.data_dict["params"]["name"].lower() == "basssist":
                                    perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                                        PAKExtract.new_facial_anim_gh5(round_time(x.data_dict["time"]),
                                                                       "Bassist", x.data_dict["params"]["fa_type"]))
                                else:
                                    perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
                                break
                        if all([any([new_name == "DLC289", new_name == "DLC263"]),
                                x.data_dict["params"]["name"] == "guitarist"]):
                            perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                                PAKExtract.new_facial_anim_gh5_gender(round_time(x.data_dict["time"]),
                                                                      "Bassist", [x.data_dict["params"]["ff_anims"],
                                                                                  x.data_dict["params"]["mf_anims"]]))
                    elif script_val.data_value in check_dbg("Band_PlayClip") or script_val.data_value in check_dbg(
                            "BandPlayClip"):
                        if "super_gimp" in args:
                            print(f"Skipping {script_val.data_value} due to size")
                            break
                        if script_val.data_value in check_dbg("BandPlayClip"):
                            print(f"Found broken script BandPlayClip. Fixing to Band_PlayClip")
                        params = x.data_dict["params"]
                        try:
                            clip_to_parse = anim_data_dict[params["clip"]]
                        except:
                            continue
                        rounded_time = round_time(x.data_dict["time"])

                        if "positionfix" in clip_to_parse.section_id.lower():
                            if rounded_time in orig_clip_times:
                                rounded_time = orig_clip_times[rounded_time]
                            print(f"Adding Force All to Idle at {rounded_time}")
                            perf_xml_file[f"{new_name}_scriptevents"].section_data.append(PAKExtract.force_all_to_idle(rounded_time))
                            continue

                        if all([wt_mode, rounded_time in wt_clip_time, wt_clip_time[-1] != rounded_time]):
                            next_time = wt_clip_time[wt_clip_time.index(rounded_time) + 1]
                            frames_till_next = round((next_time - rounded_time) / 1000 * 30)
                        else:
                            frames_till_next = 0

                        camera_skas = {}
                        all_cams = []
                        if "cameras" in clip_to_parse.data_dict:
                            all_cams += clip_to_parse.data_dict["cameras"]
                        if "bassist_cameras" in clip_to_parse.data_dict:
                            all_cams += clip_to_parse.data_dict["bassist_cameras"]
                        if "guitarist_cameras" in clip_to_parse.data_dict:
                            all_cams += clip_to_parse.data_dict["guitarist_cameras"]
                        if "vocalist_cameras" in clip_to_parse.data_dict:
                            all_cams += clip_to_parse.data_dict["vocalist_cameras"]
                        if "secondary_cameras" in clip_to_parse.data_dict:
                            all_cams += clip_to_parse.data_dict["secondary_cameras"]
                        if all_cams and not all_cams == [0]:
                            for enum, cam_ska in enumerate(all_cams):
                                camera_skas[f"camera_{enum}"] = cam_ska.data_dict["anim"]
                        else:
                            print(f"No cameras for {clip_to_parse.section_id}")
                        if "anims" in clip_to_parse.data_dict:
                            anim_skas = clip_to_parse.data_dict["anims"]
                            song_files_dict = check_ska_anims(anim_skas | camera_skas, song_files_dict, other_skas)
                            no_clip_trunc = 1
                            if x.data_dict["time"] == 0 and wt_mode:
                                for no_temp in anim_skas.values():
                                    if re.search(r"notempo", no_temp, flags=re.IGNORECASE):
                                        no_clip_trunc = 0
                                        print("Checking no tempo anim...")
                                        break
                            """
                            Add support for "secondary, bassist, guitarist, etc. cameras
                            Secondary seems to be camera 99, i.e. slot 10
                            Bassist cam seems to be camera 6, or camera 93, i.e. slot 4
                            Guitarist seems to be camera 94, i.e. slot 5
                            """
                            if no_clip_trunc or new_name.lower() in ["dlc22", "dlc23", "dlc24", "dlc92", "dlc96",
                                                                                "dlc97", "dlc105", "dlc306"]:
                                new_clip_data, startf, endf = band_clip_from_wt(clip_to_parse, params, song_files_dict,
                                                                                ven_cams=cameras,
                                                                                wt_frames=frames_till_next,
                                                                                use_anims=use_anims)
                            else:
                                new_clip_data, startf, endf = band_clip_from_wt(clip_to_parse, params, song_files_dict,
                                                                                ven_cams=cameras, next_note=first_note,
                                                                                wt_frames=frames_till_next,
                                                                                use_anims=use_anims)
                            if new_clip_data == -1:
                                print(f"Invalid anim: {clip_to_parse.section_id}. Reason: {endf}.\nSkipping")
                                continue
                            clip_name = clip_to_parse.section_id + f"_{str(play_clip_count).zfill(2)}"
                            if clip_name.startswith("0x"):
                                clip_name = clip_name[2:]
                            play_clip_count += 1
                            if "gh5" in args:
                                new_clip_data = [PAKExtract.struct_item("StructItemInteger", "dataformat", 2,
                                                                        0)] + new_clip_data
                                new_clip_data.pop()
                        else:
                            new_clip_data = clip_to_parse.section_data
                            startf = clip_to_parse.data_dict["characters"][0].data_dict["startframe"]
                            endf = clip_to_parse.data_dict["characters"][0].data_dict["endframe"]
                            clip_name = clip_to_parse.section_id
                        # Check if moment cams need to be adjusted
                        clip_len = round((endf - startf) / 30 * 1000)
                        anim_ska_lens = []
                        skip_clip = False
                        curr_clip = clip_to_parse.section_id
                        if "anims" in clip_to_parse.data_dict:
                            for key, value in anim_skas.items():
                                if key == "drummer":
                                    continue
                                if value == "None":
                                    continue
                                if "G_Attached" in value:
                                    skip_clip = True
                                if "_120" in value:
                                    skip_clip = True
                                if value.startswith("0x"):
                                    ska_name = f"{value}.{value}.ska"
                                    anim_ska_lens.append(round(
                                        struct.unpack(">f", song_files_dict[ska_name]["file_data"][40:44])[0] * 1000))
                                else:
                                    ska_name = f"{value}.ska"
                                    anim_ska_lens.append(round(struct.unpack(">f", song_files_dict[ska_name]["file_data"][40:44])[0]*1000))
                                if ska_name not in all_anims_used:
                                    all_anims_used.append(ska_name.lower())
                        else:
                            for value in clip_to_parse.data_dict["characters"]:
                                value_anim = value.data_dict["anim"]
                                if value_anim.startswith("0x"):
                                    ska_name = f"{value_anim}.{value_anim}.ska"
                                    anim_ska_lens.append(round(
                                        struct.unpack(">f", song_files_dict[ska_name]["file_data"][40:44])[0] * 1000))
                                else:
                                    ska_name = f"{value_anim}.ska"
                                    anim_ska_lens.append(round(struct.unpack(">f", song_files_dict[ska_name]["file_data"][40:44])[0]*1000))
                                if ska_name not in all_anims_used:
                                    all_anims_used.append(ska_name.lower())
                        for key, value in camera_skas.items():
                            if value.startswith("0x"):
                                ska_name = f"{value}.{value}.ska"
                            else:
                                ska_name = f"{value}.ska"
                            if ska_name not in all_anims_used:
                                all_anims_used.append(ska_name.lower())
                        min_length = min(anim_ska_lens)
                        min_length_frame = round(min_length/1000 * 30)
                        if rounded_time in orig_clip_times:
                            print(f"Moving moment {curr_clip} from {rounded_time} back to {orig_clip_times[rounded_time]}")
                            rounded_time = orig_clip_times[rounded_time]
                        if not any([rounded_time in autocut_cams, rounded_time in moment_cams]):
                            closest_cam = min(autocut_cams, key=lambda x: abs(x - rounded_time))
                            clip_offset = closest_cam - rounded_time
                            if abs(clip_offset) < 350:
                                rounded_time = closest_cam
                            elif rounded_time < last_clip_end:
                                if curr_clip == clips_processed[-1] and last_clip_start == rounded_time:
                                    print(f"Duplicate Band Clip {curr_clip} found. Ignoring.")
                                    break
                                elif curr_clip[:-4] == clips_processed[-1][:-4]:
                                    print(f"{curr_clip} seems to continue from {clips_processed[-1]}. No adjustments made")
                                elif not wt_mode:
                                    pass
                                else:
                                    print(f"Previous moment isn't finished! Moving current from {rounded_time} to {last_clip_end}")
                                    rounded_time = last_clip_end

                        cam_check = rounded_time + clip_len
                        cam_check = cam_len_check(cam_check)

                        if not any([cam_check in autocut_cams, cam_check in moment_cams]):
                            closest = min(autocut_cams, key=lambda x: abs(x - cam_check))
                            clip_end_off = closest - cam_check
                            clip_end_frames = round(clip_end_off/1000*30)
                            if abs(clip_end_off) <= 350 and not skip_clip:
                                if clip_end_off < 0:
                                    endf += clip_end_frames
                                    #print()
                                else:
                                    if startf >= clip_end_frames:
                                        startf -= clip_end_frames
                                    else:
                                        if startf > 0:
                                            clip_end_frames -= startf
                                            startf = 0
                                        if (min_length_frame - endf) > clip_end_frames:
                                            endf += clip_end_frames
                                        elif clip_end_frames <= 10:
                                            # rounded_time = round_time(rounded_time+1)
                                            print(f"Moving camera back by {clip_end_frames} {'frame' if clip_end_frames == 1 else 'frames'}.")
                                            auto_in = autocut_cams.index(closest)
                                            new_cam_len_1 = perf_file["autocutcameras"][((auto_in - 1) * 3) + 1]
                                            new_cam_len_2 = perf_file["autocutcameras"][(auto_in * 3) + 1]

                                            new_cam_len_1 -= round(clip_end_frames * 1/30 * 1000)
                                            new_cam_len_2 += round(clip_end_frames * 1 / 30 * 1000)

                                            new_cam_time = cam_len_check(closest - round(clip_end_frames * 1/30 * 1000))

                                            new_cam_len_1 = cam_len_check(new_cam_len_1)
                                            new_cam_len_2 = cam_len_check(new_cam_len_2)

                                            perf_file["autocutcameras"][((auto_in - 1) * 3) + 1] = new_cam_len_1
                                            perf_file["autocutcameras"][(auto_in * 3) + 1] = new_cam_len_2
                                            perf_file["autocutcameras"][(auto_in * 3)] = new_cam_time
                                            if closest in moment_cams:
                                                moment_in = moment_cams.index(closest)
                                                perf_file["momentcameras"][(moment_in * 3) + 1] = new_cam_len_2
                                                perf_file["momentcameras"][(moment_in * 3)] = new_cam_time
                                                if autocut_cams[auto_in - 1] in moment_cams:
                                                    perf_file["momentcameras"][
                                                        ((moment_in - 1) * 3) + 1] = new_cam_len_1
                                                if not perf_file["momentcameras"][(moment_in * 3) + 2] in range(33,37):
                                                    orig_clip_times[closest] = new_cam_time
                                                    # input("Anim shorter than camera cut")
                                                moment_cams = perf_file["momentcameras"][::3]
                                            autocut_cams = perf_file["autocutcameras"][::3]
                                        else:
                                            input("Anim shorter than camera cut")
                            '''if not any([cam_check in autocut_cams, cam_check in moment_cams]):
                            closest = min(autocut_cams, key=lambda x: abs(x - cam_check))
                            """if abs(closest - cam_check) > 500:
                                continue"""
                            try:
                                close_index = autocut_cams.index(closest)
                                next_auto = autocut_cams[close_index + 1]
                                new_len = next_auto - cam_check
                                if str(new_len).endswith("34"):
                                    new_len -= 1
                                elif str(new_len).endswith("66"):
                                    new_len += 1
                                perf_file["autocutcameras"][close_index * 3] = cam_check
                                perf_file["autocutcameras"][(close_index * 3) + 1] = new_len
                                if closest in moment_cams:
                                    perf_file["momentcameras"][close_index * 3] = cam_check
                                    perf_file["momentcameras"][(close_index * 3) + 1] = new_len
                            except Exception as E:
                                raise E'''
                        last_clip_start = rounded_time
                        last_clip_end = cam_check
                        clips_processed.append(curr_clip)
                        if "anims" in clip_to_parse.data_dict:
                            perf_xml_file[clip_name] = PAKExtract.qb_section("SectionStruct")
                            perf_xml_file[clip_name].set_all(clip_name, new_clip_data, f"songs/{new_name}.perf.xml.qb")
                            perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                                PAKExtract.new_play_clip(rounded_time, clip_name, startf, endf))
                        else:
                            perf_xml_file[clip_name] = clip_to_parse
                            perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                                PAKExtract.new_play_clip(rounded_time, clip_name, startf, endf))

                    elif script_val.data_value in check_dbg("Band_PlayIdle"):
                        if x.data_value[0].data_id == "time":
                            x.data_value[0].data_value = round_time(x.data_value[0].data_value)
                        perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
                        # print()
                    elif "MicStand" in script_val.data_value:
                        script_val.data_value = script_val.data_value.replace("MicStand", "Mic_Stand")
                        if x.data_value[0].data_id == "time":
                            x.data_value[0].data_value = round_time(x.data_value[0].data_value)
                        perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
                    else:
                        if x.data_value[0].data_id == "time":
                            x.data_value[0].data_value = round_time(x.data_value[0].data_value)

                        if "Band_PlayFacialAnim" in script_val.data_value:
                            fac_params = x.data_dict["params"]
                            if "anim" in fac_params:
                                if "gimp" in args and re.search(r"(^face_|backing)", fac_params["anim"], flags=re.IGNORECASE):
                                    break
                                curr_ska = f'{fac_params["anim"].lower()}.ska' if not fac_params["anim"].lower().startswith("0x") else f'{fac_params["anim"].lower()}.{fac_params["anim"].lower()}.ska'
                                all_anims_used.append(curr_ska)
                            elif "mf_anims" in fac_params:
                                all_anims_used.append(f'{fac_params["mf_anims"].lower()}.ska')
                                if not "ff_anims" in fac_params:
                                    x.data_value[2].struct_data_struct.append(PAKExtract.struct_item('StructItemQbKey', 'ff_anims', fac_params["mf_anims"], 0))
                                    print("Added ff_anims")
                            elif "ff_anims" in fac_params:
                                all_anims_used.append(f'{fac_params["ff_anims"].lower()}.ska')
                                if not "mf_anims" in fac_params:
                                    x.data_value[2].struct_data_struct.append(PAKExtract.struct_item('StructItemQbKey', 'mf_anims', fac_params["ff_anims"], 0))
                                    print("Added mf_anims")
                            else:
                                print(f"No Facial Anim at {x.data_dict['time']}")
                        elif "Band_PlayLoop" in script_val.data_value:
                            loop_params = x.data_dict["params"]
                            curr_ska = ""
                            if "Male" in loop_params:
                                curr_ska = loop_params["Male"].lower()
                                if curr_ska not in loop_anims[loop_params["name"]]:
                                    loop_anims[loop_params["name"]].append(curr_ska)
                                if curr_ska not in loop_genders["Male"][loop_params["name"]]:
                                    loop_genders["Male"][loop_params["name"]].append(curr_ska)
                                    loop_genders["Male"][loop_params["name"]].extend(anim_loop_master[curr_ska])
                            if "Female" in loop_params:
                                curr_ska = loop_params["Female"].lower()
                                if curr_ska not in loop_anims[loop_params["name"]]:
                                    loop_anims[loop_params["name"]].append(curr_ska)
                                if curr_ska not in loop_genders["Female"][loop_params["name"]]:
                                    loop_genders["Female"][loop_params["name"]].append(curr_ska)
                                    loop_genders["Female"][loop_params["name"]].extend(anim_loop_master[curr_ska])
                        if all([new_name == "DLC289", "Band_PlayFacialAnim" in script_val.data_value]):
                            if x.data_dict["params"]["name"] == "guitarist":
                                perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                                    PAKExtract.new_lipsync(x.data_dict["time"], "bassist",
                                                           x.data_dict["params"]["anim"]))
                        else:
                            print(f"Adding {script_val.data_value}")
                            perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
                    break
                elif script_val.data_id == "scr":
                    if new_name == "DLC289":
                        pass
                    elif new_name == "DLC292" or new_name == "DLC263":
                        # break
                        frames_till_next = 0
                        if "CrazyTrain_Bassist_Moment" in script_val.data_value:
                            clip_to_parse = anim_data_dict["B_JamOnRiser01_CrazyTrain"]
                            params = {
                                "clip": "B_JamOnRiser01_CrazyTrain",
                                "startframe": 74,
                                "endframe": 438
                            }
                        elif "crowley_moment_bassist_01" in script_val.data_value:
                            clip_to_parse = anim_data_dict["B_JamHard01_Crowley"]
                            params = {
                                "clip": "B_JamHard01_Crowley",
                                "startframe": 34,
                                "endframe": 111
                            }
                        elif "crowley_moment_bassist_02" in script_val.data_value:
                            clip_to_parse = anim_data_dict["B_JamStagger01_Crowley"]
                            params = {
                                "clip": "B_JamStagger01_Crowley",
                                "startframe": 38,
                                "endframe": 126
                            }
                        elif "crowley_moment_bassist_03" in script_val.data_value:
                            clip_to_parse = anim_data_dict["GSB_slowIntro_Crowley"]
                            params = {
                                "clip": "GSB_slowIntro_Crowley",
                                "startframe": 1
                            }
                            next_time = wt_clip_time[wt_clip_time.index(x.data_dict["time"]) + 1]
                            frames_till_next = round((next_time - x.data_dict["time"]) / 1000 * 30)
                        else:
                            break
                        rounded_time = round_time(x.data_dict["time"])
                        anim_skas = clip_to_parse.data_dict["anims"]
                        song_files_dict = check_ska_anims(anim_skas, song_files_dict, other_skas)

                        new_clip_data, startf, endf = band_clip_from_wt(clip_to_parse, params, song_files_dict,
                                                                        ven_cams=cameras,
                                                                        wt_frames=frames_till_next, use_anims=use_anims)
                        if new_clip_data == -1:
                            print(f"Invalid anim: {clip_to_parse.section_id}. Reason: {endf}.\nSkipping")
                            break
                        clip_name = clip_to_parse.section_id + f"_{str(play_clip_count).zfill(2)}"
                        play_clip_count += 1
                        perf_xml_file[clip_name] = PAKExtract.qb_section("SectionStruct")
                        perf_xml_file[clip_name].set_all(clip_name, new_clip_data, f"songs/{new_name}.perf.xml.qb")
                        perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                            PAKExtract.new_play_clip(rounded_time, clip_name, startf, endf))
                    elif script_val.data_value == "0xf7fbdb26":
                        print("0xf7fbdb26 found. Assumed to be SetSongHandCamParams")
                        x.data_value[1].data_value = "SetSongHandCamParams"
                        x.data_value[2].struct_data_struct[0].data_id = "amplitudeposition"
                        x.data_value[2].struct_data_struct[1].data_id = "amplituderotation"
                        perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
                    elif script_val.data_value == "LightShow_SetTime":
                        print(f"Lightshow blend time script found at {x.data_dict['time']}. Weird, but I'll allow it.")
                        perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
                    elif script_val.data_value not in ignored_converts:
                        print(f"{script_val.data_value} found. Not sure what to do with it")
                    else:
                        print(f"Ignoring {script_val.data_value}")
    all_loop_anims = []
    for key, value in loop_anims.items():
        if value:
            diff_files = ["", "_c01", "_c02", "_c03"]
            for x in value:
                for diff in diff_files:
                    curr_loop = f"{x + diff}.ska".lower()
                    all_anims_used.append(curr_loop)
                    all_loop_anims.append(curr_loop)

    scriptevents = {}
    for x in perf_xml_file[f"{new_name}_scriptevents"].section_data:
        if x.data_value[0].data_value not in scriptevents:
            scriptevents[x.data_value[0].data_value] = [x]
        elif x.data_value[1].data_value == "Band_ForceAllToIdle":
            scriptevents[x.data_value[0].data_value].insert(0, x)
        else:
            scriptevents[x.data_value[0].data_value].append(x)
    perf_xml_file[f"{new_name}_scriptevents"].section_data = []
    scriptevents = sorted(scriptevents.items())
    for key, value in scriptevents:
        for x in value:
            perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
    qb_file[f"{new_name}_performance"].make_empty(f"{new_name}_performance")
    ska_data = []
    for pak_file in song_files_dict.keys():
        if song_files_dict[pak_file]["file_name"].endswith(".ska"):
            anim_name = song_files_dict[pak_file]["file_name"].lower()
            if anim_name in all_anims_used and anim_name not in all_loop_anims:
                ska_data.append(song_files_dict[pak_file])
            elif anim_name in all_loop_anims:
                print(f"Removing loop anim {song_files_dict[pak_file]['file_name']} from pak and adding to perf file.")
            else:
                print(f"Removing unused anim {song_files_dict[pak_file]['file_name']} to save space.")



    note_file["bandmoment"] = mid_qb.gh5_base_entry()
    note_file["bandmoment"].set_qb_string("gh5_band_moment_note")
    note_file["bandmoment"].set_name("bandmoment")
    note_file["bandmoment"].set_size(8)
    note_file["bandmoment"].set_modulo(2)

    band_moments = []
    dbg_moments = []
    fret_arr = np.array(note_file["fretbar"].entries)
    for name in marker_names.keys():
        if re.search(r'endofsong', name, flags=re.IGNORECASE):
            continue
        t_sec = marker_names[name]
        if t_sec < 3000:
            continue
        band_start = fret_arr[fret_arr <= t_sec - 3000].max()  # 3 seconds should be enough for a band moment
        band_length = round_time(t_sec - band_start + 33)  # Round the end to the nearest frame
        if re.search(r'^chorus.*[0-9]+[a-z]?$', name, flags=re.IGNORECASE):
            band_moments.append([int(band_start), int(band_length)])
            dbg_moments.append([int(band_start), int(band_length)])
            # print(name)  # For debug
        else:
            dbg_moments.append([int(band_start), int(band_length)])
    if len(band_moments) < 3:
        band_moments = dbg_moments.copy()
    while len(band_moments) > 3:
        short_loc = 0
        for num, moment in enumerate(band_moments):
            if num == 0:
                shortest_dist = band_moments[num][0]
            else:
                dist = band_moments[num][0] - band_moments[num - 1][0]
                if dist < shortest_dist:
                    shortest_dist = dist
                    short_loc = num
        band_moments.pop(short_loc)
    '''if "rainingblood" in pakmid:  # I need to make an exception for Raining Blood due to the steady stream of green notes
        band_moments = [[66532, 3167], [120541, 3300], [169491, 3100]]'''
    note_file["bandmoment"].add_item([j for i in band_moments for j in i])

    perf_xml_file = reorg_perfqb(perf_xml_file)
    qb_file = reorg_qb(qb_file, new_name)

    for enum, light in enumerate(qb_file[f"{new_name}_lightshow_notes"].section_data):
        if enum % 2 == 0:
            continue
        else:
            qb_file[f"{new_name}_lightshow_notes"].section_data[enum] = modify_strobe(light)

    # To do:
    """mid.qb:
        _anim_notes
        _anim
        _drums_notes
        _scripts
        _cameras_notes
        _cameras
        _performance
        _crowd_notes
        _crowd
        _lightshow_notes
        _lightshow
        _facial
        _localized_strings"""

    # Convert files to binary and add to dictionary for pak creation
    song_data = []
    song_data.append(
        {"file_name": f"songs/{new_name}.mid.qb",
         "file_data": convert_to_gh5_bin(qb_file, "qb", console="PC", endian="big")})
    for x in PAKExtract.qs_extensions:
        song_data.append(
            {"file_name": f"songs/{new_name}.mid{x}", "file_data": convert_to_gh5_bin(sorted(qs_file), "qs")})
    song_data.append(
        {"file_name": f"songs/{new_name}.note", "file_data": convert_to_gh5_bin(note_file, "note", new_name)})
    song_data.append(
        {"file_name": f"songs/{new_name}.perf", "file_data": convert_to_gh5_bin(perf_file, "perf", new_name, loop_genders)})
    song_data.append(
        {"file_name": f"songs/{new_name}.perf.xml.qb",
         "file_data": convert_to_gh5_bin(perf_xml_file, "perf_xml", console="PC", endian="big")})
    if anim_pak:
        ska_data = ska_data[:song_file_len - len(song_data)]
    elif re.search(r'(purplehaze|windcriesmary|dlc22|dlc23|dlc24|dlc92|dlc96|dlc97)', song_name, flags = re.IGNORECASE):
        print("Adding left-hand anims for future proofing")
        new_ska = []
        for x in ska_data:
            if re.search(r'(^GH3_Hnd)|(Strum_Jimi)', x["file_name"], flags=re.IGNORECASE):
                continue
            else:
                new_ska.append(x)
        left_path = "D:\\RB\\GHWoR\\Convert Creations\\Left-Hand Anims"
        for x in os.listdir(f"{left_path}"):
            with open(f"{left_path}\\{x}", 'rb') as f:
                ska_file = f.read()
            new_ska.append({"file_name": x[:-4], "file_data": ska_file})
        ska_data = new_ska
    # elif re.search(r'ReEdThroughLabor', song_name, flags= re.IGNORECASE):
    elif check_150:
        onefifty_path = "D:\\RB\\GHWoR\\Convert Creations\\150 anims"
        diff_files = ["", "_c01", "_c02", "_c03"]
        for x in check_150:
            print(f"Adding 150 anim: {x}")
            for y in diff_files:
                with open(f"{onefifty_path}\\{x}{y}.ska.xen", 'rb') as f:
                    ska_file = f.read()
                ska_data.append({"file_name": f"{x}{y}.ska", "file_data": ska_file})
        # print()
    if "compiler" in args:
        ska_data += other_flags
    return song_data + ska_data


def gen_vox_sp(song_name, note_file):
    vox_star_entry = []
    p_time = 0
    star_count = 0
    rand_phrase = [5]  # Try to add some novelty into the SP generation
    start_pos = len(song_name) % len(rand_phrase)
    for y, x in enumerate(note_file["vocalsmarkers"].entries):
        if y % 2 == 0:
            p_time = x
        else:
            p_text = x
            if p_text != "":
                star_count += 1
                if star_count % rand_phrase[start_pos] == 0:
                    if y + 1 != len(note_file["vocalsmarkers"].entries):
                        phrase_end = note_file["vocalphrase"].entries.index(p_time) + 1
                        vox_star_entry += [p_time + 4, note_file["vocalphrase"].entries[phrase_end] - 3 - (p_time + 4)]
                    start_pos = (start_pos + 1) % len(rand_phrase)
    return vox_star_entry


def get_first_note(entry):
    try:
        first_note = entry[0]
    except:
        first_note = 9999
    return first_note


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def midqb2mid(pakmid, output=f'{os.getcwd()}'):
    if not "_song.pak" in pakmid:
        warning = input(
            "WARNING: File does not appear to be a validly named mid PAK file. Do you want to continue? (Y/N): ")
        if not warning.lower().startswith("y"):
            return -1

    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")]

    qb_sections, file_headers, file_headers_hex, song_files = pak2mid(pakmid, song_name)

    inst_types = ["Notes", "Star", "Battle"]

    playableQB = {
        "song": {
            "Easy": [],
            "Medium": [],
            "Hard": [],
            "Expert": []

        },
        "rhythm": {

            "Easy": [],
            "Medium": [],
            "Hard": [],
            "Expert": []

        },
        "guitarcoop": {

            "Easy": [],
            "Medium": [],
            "Hard": [],
            "Expert": []

        },
        "rhythmcoop": {

            "Easy": [],
            "Medium": [],
            "Hard": [],
            "Expert": []

        }
    }

    leftHandAnims = {
        "Guitar": [],
        "Bass": []
    }

    faceOffs = {
        "P1": [],
        "P2": []
    }

    cameraNotes = []
    lightshowNotes = []
    lightshowScripts = []
    drumNotes = []
    timeSigs = []
    markers = []
    fretbars = []

    midi_export = mido.MidiFile()
    midi_export.add_track()
    midi_export.tracks[0].append(mido.MetaMessage("set_tempo", tempo=500000))

    track_types = []
    anim_tracks_notes = ["lightshow_notes", "cameras_notes"]
    tracks = []

    for x in qb_sections:
        if x.section_id in file_headers_hex.keys():
            x.set_new_id(file_headers_hex[x.section_id])
        track_type = get_track_type(x.section_id)
        track_types.append(track_type)
        if track_type["track_type"] in inst_types:
            if track_type["track_type"] == "Notes":
                note_time = 0
                note_length = 0
                note_type = 0
                for z, y in enumerate(x.section_data):
                    if z % 3 == 0:
                        note_time = y
                    elif z % 3 == 1:
                        note_length = y
                    elif z % 3 == 2:
                        note_type = format(y, '#010b')[2:]
                        playableQB[track_type["instrument"]][track_type["difficulty"]].append(
                            [note_time, note_length, note_type])
                    else:
                        print("Huh?")
            if track_type["track_type"] == "Star":
                pass
            if track_type["track_type"] == "Battle":
                pass
        elif track_type["track_type"] in anim_tracks_notes:
            blank_on = mido.Message("note_on")
            blank_off = mido.Message("note_off")
            new_track = mido.MidiTrack()
            # midi_export.add_track(track_type["track_type"])
            prev_note = -1
            prev_time = -1
            for y in x.section_data:
                if prev_note != -1:
                    new_track.append(blank_off.copy(note=prev_note, velocity=0, time=int(
                        round(mido.second2tick(y[0] / 1000, 480, 500000) - prev_time, 0))))
                if prev_time != -1:
                    new_track.append(blank_on.copy(note=y[1], time=0))
                else:
                    new_track.append(
                        blank_on.copy(note=y[1], time=int(round(mido.second2tick(y[0] / 1000, 480, 500000), 0))))
                prev_note = y[1]
                prev_time = mido.second2tick(y[0] / 1000, 480, 500000)
            tracks.append(new_track.copy())
        elif track_type["track_type"] == "lightshow":
            blank = mido.MetaMessage("text")
            new_track = mido.MidiTrack()
            # midi_export.add_track(track_type["track_type"])
            prev_time = -1
            for y in x.section_data:
                if prev_time != -1:
                    new_track.append(
                        blank.copy(text=f"SetBlendTime {str(y.data_value[2].struct_data_struct[0].data_value)}",
                                   time=int(round(
                                       mido.second2tick(y.data_value[0].data_value / 1000, 480, 500000) - prev_time,
                                       0))))
                else:
                    new_track.append(
                        blank.copy(text=f"SetBlendTime {str(y.data_value[2].struct_data_struct[0].data_value)}",
                                   time=int(
                                       round(mido.second2tick(y.data_value[0].data_value / 1000, 480, 500000), 0))))
                prev_time = mido.second2tick(y.data_value[0].data_value / 1000, 480, 500000)
            tracks.append(new_track.copy())
    midi_export.add_track(name="GH3 VENUE")
    midi_export.tracks[-1] = mido.merge_tracks(x for x in tracks)
    midi_export.save(filename=f'{output}\\{song_name}.mid')

    # raise Exception

    return


def extract_pak(pak_file, output=f'{os.getcwd()}\\PAK extract'):
    pab_file = os.path.dirname(pak_file) + f"\\{os.path.basename(pak_file[:pak_file.find('.pak')])}.pab.xen"
    if os.path.isfile(pab_file):
        print("Found PAB file")
        with open(pab_file, "rb") as pab:
            pab_bytes = pab.read()
    else:
        print("No PAB file found")
        pab_bytes = b''
    with open(pak_file, 'rb') as pak:
        pak_bytes = pak.read()
    if pak_bytes[:4] == b'CHNK':  # Check for xbox compressed file
        pak_bytes = PAKExtract.decompress_pak(pak_bytes)
    if pak_bytes[:4] == b'CHNK':
        pab_bytes = PAKExtract.decompress_pak(pab_bytes)
    pak_bytes += pab_bytes
    pak_files = PAKExtract.main(pak_bytes, "")
    # raise Exception
    for x in pak_files:
        output_file = f"{output}\\{x['file_name']}"
        dir_name = os.path.dirname(output_file)
        try:
            os.makedirs(dir_name)
        except:
            pass
        with open(output_file, 'wb') as write_file:
            write_file.write(x["file_data"])

    # print(len(pak_bytes))

    return


def output_mid_gh3(mid_file, hopo=170, filename="", gh3_plus=True):
    pak_file, filename = mid_qb.make_mid(mid_file, hopo, filename)
    return pak_file, filename


def qb_to_text(file, output=f'{os.getcwd()}', game="GH3"):
    qb_sections, file_name = QB2Text.main(file)
    output_file = f'{output}\\{file_name}.txt'
    dir_name = os.path.dirname(output_file)
    try:
        os.makedirs(dir_name)
    except:
        pass
    QB2Text.output_qb_file(qb_sections, output_file)
    return


def text_to_qb(text_file, output=os.getcwd()):
    with open(text_file, 'r') as f:
        lines = f.read()

    qb_file = Text2QB.main(lines)
    qb_name = f'{os.path.splitext(os.path.basename(text_file))[0]}.qb'
    # raise Exception
    qb_check = f'{output}\\{qb_name}'
    if os.path.isfile(qb_check):
        try:
            print("Backing up QB file found of corresponding text file.\n")
            os.rename(qb_check, qb_check + "_backup")
        except FileExistsError:
            print("Backup of QB file found of corresponding text file. Will not overwrite\n")
            pass
    with open(f'{output}\\{qb_name}', 'wb') as f:
        f.write(qb_file)

    return


def band_clip_from_wt(band_clip, params, anim_data, ven_cams, *args, **kwargs):
    # This function converts the animations from one game (GHWT) to another (GH5 and up)
    import struct
    ven_cams.create_cam_dict()
    if "use_anims" in kwargs:
        use_anims = kwargs["use_anims"]
    else:
        use_anims = 1

    # Setting up key lists
    to_pull = ["startnodes", "anims", "cameras", "arms", "secondary_cameras", "guitarist_cameras", "vocalist_cameras",
               "bassist_cameras"]
    band = ["guitarist", "bassist", "drummer", "vocalist"]
    camera_slots = {"cameras": 0, "vocalist_cameras": 0, "bassist_cameras": 3, "guitarist_cameras": 6}
    cam_spec = ["name", "anim"]

    # Setting up spelling error correction and armatures dictionary
    spelling_errors = {"guitairstist": "guitarist",
                       "basssist": "bassist"}
    arms_dict = {"off": "False", "on": "True"}

    # Getting data dictionary from band_clip
    data = band_clip.data_dict

    # Initializing characters dictionary
    characters = {}
    for player in band:
        characters[player] = {}

    # Initializing camera list
    cameras = []
    for clip_data in to_pull:
        if clip_data in data.keys():
            if clip_data == "anims":
                for anim in data["anims"].keys():
                    characters[anim.lower()] |= {"anim": deepcopy(data[clip_data][anim])}
            elif "cameras" in clip_data:
                for enum, shot in enumerate(data[clip_data]):
                    if shot == 0:
                        continue
                    if clip_data == "secondary_cameras":
                        if ven_cams.sec_cam == 99:
                            for midi_cam in range(1, 10):
                                upper_cam = ven_cams.sec_cam - midi_cam
                                lower_cam = upper_cam - 87
                                if upper_cam in ven_cams.moment_cuts_used:
                                    continue
                                elif lower_cam in ven_cams.moment_cuts_used and lower_cam <= 6:  # Just in case there are other notes in the moment array
                                    continue
                                else:
                                    ven_cams.set_secondary_cam(upper_cam)
                                    break
                            else:  # If for loop completes, which we don't want.
                                return -1, -1, "Could not place secondary camera in an open camera slot"
                        curr_cam = {"slot": ven_cams.sec_cam - 90}
                        # print()
                    else:
                        curr_cam = {"slot": enum + camera_slots[clip_data]}
                    for spec in cam_spec:
                        curr_cam[spec] = shot.data_dict[spec]
                    cameras.append(deepcopy(curr_cam))
            elif clip_data == "startnodes":
                for sn in data["startnodes"].keys():
                    try:
                        characters[sn.lower()] |= {"startnode": deepcopy(data[clip_data][sn])}
                    except KeyError:
                        characters[spelling_errors[sn.lower()]] |= {"startnode": deepcopy(data[clip_data][sn])}
            else:
                for arms in data["arms"].keys():
                    characters[arms.lower()] |= {"arms": deepcopy(data[clip_data][arms])}
    startframe = 0
    endframe = 0
    all_endframes = []
    for param in params.keys():
        if param == "startframe":
            startframe = params[param]
        if param == "endframe":
            endframe = params[param]
    if "wt_frames" in kwargs:
        if kwargs["wt_frames"]:
            all_endframes.append(kwargs["wt_frames"] + startframe)
    char_dict = []
    for player in band:
        curr = characters[player]
        if characters[player]:
            if player == "drummer":
                continue
            if "startnode" not in curr:
                curr["startnode"] = f"{player}_start"
            if "anim" not in curr:
                # curr["anim"] = 0
                continue
            if curr["anim"] == "None":
                continue
            else:
                if curr["anim"].lower() == "none":
                    # Skip the character if there's no animation played (GHM has this sometimes)
                    continue
            curr_char = mid_qb.gh5_band_clip(player, curr["startnode"], curr["anim"])
            if "arms" in curr:
                for arms in curr["arms"].keys():
                    x_arm = curr["arms"][arms]  # current armature
                    setattr(curr_char, arms, (x_arm if x_arm.lower() not in arms_dict else arms_dict[x_arm.lower()]))
            ska_to_check = characters[player]['anim']
            if ska_to_check.startswith("0x"):
                ska_to_check = f"{ska_to_check}.{ska_to_check}"
            try:
                ska_length = anim_data[f"{ska_to_check}.ska"]["file_data"][40:44]
            except Exception as E:
                raise E
            ska_length = struct.unpack(">f", ska_length)[0]
            ska_length = round(ska_length * 30)
            setattr(curr_char, "startframe", startframe)
            if endframe:  # Set the endframe if it exists
                setattr(curr_char, "endframe", endframe)
                # print()
                all_endframes.append(endframe)

            elif "next_note" in kwargs and use_anims:  # If it's the first Clip event (most likely an idle event). Play until first note/camera cut
                endframe = startframe + kwargs["next_note"]
                setattr(curr_char, "endframe", startframe + kwargs["next_note"] - 1)
                all_endframes.append(endframe)
            else:  # Nuclear option. Since endframe is kind of needed, this will grab the last frame of the ska file and insert it.
                try:
                    endframe = anim_data[f"{ska_to_check}.ska"]["file_data"][40:44]
                    endframe = struct.unpack(">f", endframe)[0]
                    endframe = round(endframe * 30)
                    setattr(curr_char, "endframe", endframe)

                    all_endframes.append(endframe)
                    endframe = 0
                except Exception as E:
                    debug_except = E
                    return -1, -1, f"Could not find end frame on {characters[player]['anim']}.ska"

            char_dict.append(deepcopy(curr_char))
    char_data = []
    camera_qb = PAKExtract.camera_band_clip(cameras)
    if not cameras:
        camera_qb.make_empty_array()
    endframe = min(all_endframes)
    if endframe < startframe:
        startframe, endframe = endframe, startframe
        print(f"Swapping endframe and startframe due to endframe being smaller...")
        # return -1, -1, "Endframe is less than startframe"
    for char in char_dict:
        if char.endframe > endframe:
            char.endframe = endframe
        char_data.append(PAKExtract.struct_item("StructHeader", 0, PAKExtract.new_band_clip_gh5(char), 0))
    char_qb = PAKExtract.struct_item("StructItemArray", "characters", char_data, 0)
    commands = PAKExtract.struct_item("StructItemArray", "commands", [], 0)
    commands.make_empty_array()
    return [char_qb, camera_qb, commands], startframe, endframe


def parse_wt_anim_event(entry):
    value_bin = '{0:032b}'.format(entry)
    velocity = value_bin[0:8]
    midi_note = value_bin[8:16]
    length = value_bin[16:]
    velocity_val = int(velocity, 2)
    midi_note_val = int(midi_note, 2)
    length_val = int(length, 2)
    return velocity_val, midi_note_val, length_val


def read_wt_event(events, lights=0, vh=0):
    event_arr = []
    last_time = 0
    if lights:
        for enum, entry in enumerate(events):
            last_time = entry.data_dict["time"]
            scr_type = entry.data_dict["scr"]
            length = entry.data_dict["params"]["time"]
            event_arr.append({"time": last_time, "text": f"{scr_type} {length}"})
    else:
        for enum, entry in enumerate(events):
            if enum % 2 == 0:  # Time value
                last_time = entry
            else:
                velocity_val, midi_note_val, length_val = parse_wt_anim_event(entry)
                event_arr.append({"time": last_time, "velocity": velocity_val, "note": midi_note_val,
                                  "length": length_val})

    return event_arr


def set_note_type(note, accents, ghost=0):
    note_type = {"green": 1 << 0,
                 "red": 1 << 1,
                 "yellow": 1 << 2,
                 "blue": 1 << 3,
                 "orange": 1 << 4,
                 "purple": 1 << 5,
                 "hopo": 1 << 6,
                 "other": 1 << 7}

    note_entry = []

    for colour, value in note_type.items():
        if value & note:
            note_dict = {"colour": colour}
            if value & accents:
                note_dict["velocity"] = 127
            else:
                note_dict["velocity"] = 100
            note_entry.append(note_dict)
        elif value & ghost:
            note_dict = {"colour": colour}
            note_dict["velocity"] = 1
            note_entry.append(note_dict)

    return note_entry


def rename_track(avatar):
    if avatar.lower() == "bassist":
        track = "Bass"
    elif avatar.lower() == "guitarist":
        track = "Guitar"
    elif avatar.lower() == "vocalist":
        track = "Vocals"
    elif avatar.lower() == "drummer":
        track = "drums"
    else:
        track = "Rhythm"
    return track


def read_gh3_note(sections_dict, tempo_data, tpb, game="GH3"):
    if game == "GH3":
        gtr_anims = range(117, 128)
        bass_anims = range(100, 111)
        aux_anims = range(83, 94)
    else:
        gtr_anims = range(109, 128)
        bass_anims = range(85, 104)
        aux_anims = range(61, 79)

    gh3 = True if game == "GH3" else False
    if gh3:
        bin_notes = {
            1 << 0: "green",
            1 << 1: "red",
            1 << 2: "yellow",
            1 << 3: "blue",
            1 << 4: "orange",
            1 << 5: "force",
            1 << 6: "other",
            1 << 7: "other2",
        }
    else:
        bin_notes = {
            1 << 0: "green",
            1 << 1: "red",
            1 << 2: "yellow",
            1 << 3: "blue",
            1 << 4: "orange",
            1 << 5: "purple",

            1 << 6: "force",

            1 << 13: "2x_kick",
        }
        mod_notes = {
            1 << 7: "green",
            1 << 8: "red",
            1 << 9: "yellow",
            1 << 10: "blue",
            1 << 11: "orange",
        }
    base_notes = {
        "2x_kick": 58,
        "purple": 59,
        "green": 60,
        "red": 61,
        "yellow": 62,
        "blue": 63,
        "orange": 64,
        "force": 65,
        "other": 67,
        "other2": 68
    }
    note_mult = {
        "easy": 0,
        "medium": 1,
        "hard": 2,
        "expert": 3
    }
    note_charts = {
        "Guitar": [],
        "Bass": [],
        "Rhythm": [],
        "Guitar Coop": [],
        "Drums": [],
        "Aux": [],
        "Vocals": []
    }
    misc_charts = {
        "scripts": [],
        "anim": [],
        "triggers": [],
        "cameras": [],
        "lightshow": [],
        "crowd": [],
        "drums": [],
        "performance": []
    }
    for key, value in sections_dict.items():  # This code is like wt_to_5, but with enough changes it wasn't worth it to merge
        # Pull all note data
        if value.section_data == [0, 0]:
            continue
        if re.search(r"(timesig|fretbars)\Z", key, flags=re.IGNORECASE):
            continue
        sec_split = key.split("_")
        not_guitar = re.search(r"(rhythm|aux|coop|drum)", key, flags=re.IGNORECASE)
        if re.search(r"(Easy|Medium|Hard|Expert)\Z", key, flags=re.IGNORECASE):
            if not_guitar:
                difficulty = sec_split[-1]
                instrument = sec_split[-2]
                if instrument.lower() == "rhythm":
                    instrument = "Bass"
                elif instrument.lower() == "rhythmcoop":
                    instrument = "Rhythm"
                elif instrument.lower() == "guitarcoop":
                    instrument = "Guitar Coop"
                elif instrument.lower() == "drum":
                    instrument = "Drums"
                else:
                    instrument = "Aux"
            else:
                difficulty = sec_split[-1]
                instrument = "Guitar"
            t_sec = 0
            length = 0
            notes = []
            for loc, entry in enumerate(value.section_data):
                if gh3:
                    if loc % 3 == 0:
                        t_sec = entry
                    elif loc % 3 == 1:
                        length = entry
                    else:
                        for note_type, colour in bin_notes.items():
                            if note_type & entry:
                                notes.append({"time": t_sec, "length": length,
                                              "note": base_notes[colour] + (12 * note_mult[difficulty.lower()])})
                else:
                    if loc % 2 == 0:
                        t_sec = entry
                    else:
                        value_bin = '{0:032b}'.format(entry)
                        length = int(value_bin[16:], 2)
                        notes_bin = value_bin[:16]
                        notes_int = int(notes_bin, 2)
                        accents = {"2x_kick": 100,
                                   "purple": 100,
                                   "force": 100}
                        for note_type, colour in mod_notes.items():
                            if note_type & notes_int:
                                accents[colour] = 127
                            else:
                                accents[colour] = 100
                        for note_type, colour in bin_notes.items():
                            if note_type & notes_int:
                                notes.append({"time": t_sec, "length": length,
                                              "note": base_notes[colour] + (12 * note_mult[difficulty.lower()]),
                                              "velocity": accents[colour]})

                        # print()
            note_charts[instrument] += notes.copy()
        elif re.search(r"(_Star)", key, flags=re.IGNORECASE):
            if not re.search(r"(Expert_Star)", key, flags=re.IGNORECASE):
                continue
            if not_guitar:
                instrument = sec_split[-3]
                if instrument.lower() == "rhythm":
                    instrument = "Bass"
                elif instrument.lower() == "rhythmcoop":
                    instrument = "Rhythm"
                elif instrument.lower() == "guitarcoop":
                    instrument = "Guitar Coop"
                else:
                    instrument = "Aux"
            else:
                instrument = "Guitar"
            difficulty = sec_split[-2]
            star_note = []
            for entry in value.section_data:
                t_sec = entry[0]
                length = entry[1]
                if re.search(r"(Expert_Star)\Z", key, flags=re.IGNORECASE):
                    star_note.append({"time": t_sec, "length": length, "note": 116})
                else:
                    star_note.append({"time": t_sec, "length": length, "note": 115})
            note_charts[instrument] += star_note.copy()
        elif re.search(r"(_FaceOff)", key, flags=re.IGNORECASE):
            face_off = []
            for entry in value.section_data:
                t_sec = entry[0]
                length = entry[1]
                if re.search(r"(FaceOffP1)\Z", key, flags=re.IGNORECASE):
                    face_off.append({"time": t_sec, "length": length, "note": 105})
                elif re.search(r"(FaceOffP2)\Z", key, flags=re.IGNORECASE):
                    face_off.append({"time": t_sec, "length": length, "note": 106})
                elif re.search(r"(FaceOffStar)\Z", key, flags=re.IGNORECASE):
                    face_off.append({"time": t_sec, "length": length, "note": 107})
            if gh3:
                note_charts["Guitar"] += face_off.copy()
            else:
                print()
        elif re.search(r"(markers)", key, flags=re.IGNORECASE):
            continue
        else:
            misc_type = sec_split[1]
            if "notes" in sec_split:
                misc_note = []
                for entry in value.section_data:
                    t_sec = entry[0]
                    note_val = entry[1]
                    length = entry[2]
                    if misc_type == "anim":
                        if note_val in gtr_anims:
                            note_val -= min(gtr_anims)
                            track = "Guitar"
                        elif note_val in bass_anims:
                            note_val -= min(bass_anims)
                            track = "Bass"
                        elif note_val in aux_anims:
                            note_val -= min(aux_anims)
                            track = "Rhythm"
                        else:
                            print(
                                f"Unknown anim note {note_val} found at {t_sec}. Adding to anim track instead of instrument.")
                            misc_note.append({"time": t_sec, "length": length, "note": note_val})
                            continue
                        note_val = int((20 - (20 * note_val / 10)) // 1) + 40
                        note_val -= 1 if note_val != 40 else 0
                        note_charts[track].append({"time": t_sec, "length": length, "note": note_val})
                        continue
                    # if misc_type == "drum":

                    misc_note.append({"time": t_sec, "length": length, "note": note_val})
                misc_charts[misc_type] += misc_note.copy()
            elif re.search(r"(lightshow)", misc_type, flags=re.IGNORECASE):
                misc_event = []
                for entry in value.section_data:
                    t_sec = entry.data_dict["time"]
                    t_event = f"{entry.data_dict['scr']} {round(entry.data_dict['params']['time'], 4)}"
                    misc_event.append({"time": t_sec, "event": t_event})
                misc_charts["lightshow"] += misc_event.copy()
            elif re.search(r"(performance)", misc_type, flags=re.IGNORECASE):
                misc_event = []
                for entry in value.section_data:
                    t_sec = entry.data_dict["time"]
                    script = entry.data_dict['scr']
                    params = []
                    if "params" in entry.data_dict:
                        if re.search(r"(Band_ChangeStance)", script, flags=re.IGNORECASE):
                            avatar = entry.data_dict["params"]["name"]
                            stance = entry.data_dict["params"]["stance"]
                            band_event = {"time": t_sec, "event": stance.lower()}
                            track = rename_track(avatar)
                            if track == "drums":
                                misc_charts[track].append(band_event)
                            else:
                                note_charts[track].append(band_event)
                            continue
                        elif re.search(r"Band_PlayFacialAnim", script, flags=re.IGNORECASE):
                            avatar = entry.data_dict["params"]["name"]
                            anim = entry.data_dict["params"]["anim"]
                            band_event = {"time": t_sec, "event": f"Band_PlayFacialAnim {anim}"}
                            track = rename_track(avatar)
                            note_charts[track].append(band_event)
                            continue
                        elif re.search(r"Band_PlayAnim\Z", script, flags=re.IGNORECASE):
                            param2 = entry.data_dict["params"]
                            avatar = param2["name"]
                            track = rename_track(avatar)
                            anim = param2["anim"]
                            if len(param2.keys()) == 3:
                                anim_re = re.search(r"(repeat_count|0x0|allow_in_2player)", list(param2.keys())[2],
                                                    flags=re.IGNORECASE)
                                if anim_re:
                                    if anim_re.string == "allow_in_2player":
                                        p2_bool = "1p" if param2[anim_re.string] == "false" else "2p"
                                        band_event = {"time": t_sec, "event": f"{anim.lower()} {p2_bool}"}
                                    else:
                                        modifier = param2[anim_re.string]
                                        band_event = {"time": t_sec, "event": f"{anim.lower()} {modifier}"}

                                else:
                                    print(f"Unknown key {list(param2.keys())[2]} found in PlayAnim. Skipping...")
                                    continue
                            elif len(param2.keys()) > 3:
                                print(f"Unknown values {param2.keys()} found in PlayAnim")
                                continue
                            else:
                                band_event = {"time": t_sec, "event": f"{anim}"}
                            if track == "drums":
                                misc_charts[track].append(band_event)
                            else:
                                note_charts[track].append(band_event)
                            continue
                        elif re.search(r'Band_WalkToNode\Z', script, flags=re.IGNORECASE):
                            param2 = entry.data_dict["params"]
                            avatar = param2["name"]
                            track = rename_track(avatar)
                            node = f"{param2['node']}"
                            # node = f"Band_WalkToNode {param2['node']}" - Potential alternative
                            if len(param2.keys()) == 3:
                                if re.search(r"(0x0)", list(param2.keys())[2], flags=re.IGNORECASE):
                                    if "0x0" in param2:
                                        other = param2["0x0"]
                                        band_event = {"time": t_sec, "event": f"{node} {other}"}
                                else:
                                    print(f"Unknown key {param2.keys()[2]} found in PlayAnim. Skipping...")
                                    continue
                            elif len(param2.keys()) > 3:
                                print(f"Unknown values {param2.keys()} found in PlayAnim")
                                continue
                            else:
                                band_event = {"time": t_sec, "event": f"{node}"}
                            if track == "drums":
                                misc_charts[track].append(band_event)
                            else:
                                note_charts[track].append(band_event)
                            continue
                        elif re.search(r"Crowd_StageDiver_Jump\Z", script, flags=re.IGNORECASE):
                            if "params" in entry.data_dict:
                                temp_par = entry.data_dict["params"]
                                if "0x0" in temp_par:
                                    script += f" {temp_par['0x0']}"
                            spec_event = {"time": t_sec, "event": f"{script}"}
                            misc_charts["performance"].append(spec_event)
                            continue
                        else:
                            for obj, parameter in entry.data_dict['params'].items():
                                if re.search(r"SpecialCamera_PlayAnim", script, flags=re.IGNORECASE):
                                    params.append(f"{obj} {parameter}")
                                else:
                                    print(f"{script} not yet supported. Skipping...")
                    params = ' '.join(params)
                    t_event = f"{script} {params}"
                    misc_event.append({"time": t_sec, "event": t_event})
                misc_charts["performance"] += misc_event.copy()
            else:
                print(f"{misc_type} not yet implemented. Skipping for now...\n")

    mid = []
    to_make = [note_charts, misc_charts]
    for enum, mid_stuff in enumerate(to_make):
        for chart, events in mid_stuff.items():
            timeStart = 0
            temp_tracks = []
            for event in events:
                temp_tracks.append(MidiTrack())
                ev_time = event["time"] / 1000
                map_lower = tempo_data.secondsArray[tempo_data.secondsArray <= ev_time].max()
                arrIndex = tempo_data.songSeconds.index(map_lower)
                timeFromChange = ev_time - tempo_data.songSeconds[arrIndex]
                ticksFromChange = s2t(timeFromChange, tpb, tempo_data.songTempo[arrIndex])
                timeVal = tempo_data.songTime[arrIndex] + round(ticksFromChange) - timeStart
                if "event" in event:
                    temp_tracks[-1].append(MetaMessage("text", time=timeVal, text=event["event"]))
                else:
                    note = event["note"]
                    ev_time_2 = (event["time"] + event["length"]) / 1000
                    map_lower_2 = tempo_data.secondsArray[tempo_data.secondsArray <= ev_time_2].max()
                    arrIndex_2 = tempo_data.songSeconds.index(map_lower_2)
                    timeFromChange_2 = ev_time_2 - tempo_data.songSeconds[arrIndex_2]
                    ticksFromChange_2 = s2t(timeFromChange_2, tpb, tempo_data.songTempo[arrIndex_2])
                    timeVal_2 = tempo_data.songTime[arrIndex_2] + round(ticksFromChange_2) - timeVal
                    temp_tracks[-1].append(Message("note_on", time=timeVal, note=note, velocity=100))
                    temp_tracks[-1].append(Message("note_on", time=timeVal_2, note=note, velocity=0))
            if temp_tracks:
                temp_tracks = mido.merge_tracks(temp_tracks)
                mid.append(temp_tracks)
                if enum == 0:
                    mid[-1].name = f"PART {chart.upper()}"
                else:
                    mid[-1].name = f"{chart.upper()}"

    return mid


def read_gh5_note(note_bin, drum_mode=False):
    note_file = BytesIO(note_bin)
    read_int = lambda a=4, note=note_file: int.from_bytes(note.read(a), "big")
    dbg = lambda check: PAKExtract.pull_dbg_name(check)
    game = {0x40a000d2: "gh5", 0x40c001a3: "gh6"}
    game_id = read_int()
    dlc_id = dbg(read_int())
    entries = read_int()
    file_type = dbg(read_int())
    # assert file_type == "note"
    other_base_notes = {
        "green": 60,
        "red": 61,
        "yellow": 62,
        "blue": 63,
        "orange": 64,
        "purple": 59,
        "hopo": 65,
        "other": 66
    }
    drum_base_notes = {
        "green": 65,
        "red": 61,
        "yellow": 62,
        "blue": 63,
        "orange": 64,
        "purple": 60,
        "hopo": 59,  # aka 2x Kick
        "other": 66
    }
    note_mult = {
        "easy": 0,
        "medium": 1,
        "hard": 2,
        "expert": 3
    }
    note_file.seek(28)
    note_file_dict = {}
    for note_entry in range(entries):
        entry_id = dbg(read_int())
        entry_count = read_int()
        entry_type = dbg(read_int())
        element_size = read_int()
        note_file_dict[entry_id] = []
        if entry_type == "gh5_star_note":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_length = read_int(2)
                note_file_dict[entry_id].append({"time": entry_time, "length": entry_length, "note": 116})
        elif entry_type == "gh5_tapping_note":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_length = read_int()
                note_file_dict[entry_id].append({"time": entry_time, "length": entry_length, "note": 104})
        elif entry_type == "gh5_drumfill_note":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_end = read_int()
                note_file_dict[entry_id].append({"time": entry_time, "length": entry_end - entry_time, "note": 104})
        elif entry_type == "gh5_instrument_note" or entry_type == "gh6_expert_drum_note":
            for diff in note_mult.keys():
                if diff in entry_id:
                    entry_diff = diff
                    break
            else:  # If the for loop completes, that's no bueno
                raise Exception("Unknown difficulty found while parsing note file.")
            if "drum" in entry_id:
                base_notes = drum_base_notes
            else:
                base_notes = other_base_notes
            for entry in range(entry_count):
                entry_time = read_int()
                entry_length = read_int(2)
                drum_note = read_int(1)
                drum_accent = read_int(1)
                if entry_type == "gh6_expert_drum_note":
                    drum_ghost = read_int(1)
                    entry_note = set_note_type(drum_note, drum_accent, drum_ghost)

                else:
                    entry_note = set_note_type(drum_note, drum_accent)
                for note in entry_note:
                    note_file_dict[entry_id].append({"time": entry_time, "length": entry_length,
                                                     "note": base_notes[note["colour"]] + (12 * note_mult[entry_diff]),
                                                     "velocity": note["velocity"]})
        elif entry_type == "gh5_band_moment_note":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_length = read_int()
                note_file_dict[entry_id].append({"time": entry_time, "length": entry_length, "note": 104})
        elif entry_id == "fretbar":
            for entry in range(entry_count):
                note_file_dict[entry_id].append(read_int())
        elif entry_id == "timesig":
            for entry in range(entry_count):
                note_file_dict[entry_id].append([read_int(), read_int(1), read_int(1)])
        elif entry_id == "guitarmarkers":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_text = dbg(read_int())
                note_file_dict[entry_id].append(
                    {"time": entry_time, "text": entry_text})
        elif entry_id == "vocals" or entry_id == "backup_vocals":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_length = read_int(2)
                entry_note = read_int(1)
                note_file_dict[entry_id].append({"time": entry_time, "length": entry_length, "note": entry_note})
        elif entry_type == 'gh5_vocal_freeform_note':
            for entry in range(entry_count):
                entry_time = read_int()
                entry_length = read_int()
                entry_unk = read_int(2)
                note_file_dict[entry_id].append({"time": entry_time, "length": entry_length, "note": 104})
        elif entry_type == 'gh5_vocal_phrase':
            for enum, entry in enumerate(range(entry_count)):
                entry_time = read_int()
                if enum != 0:
                    note_file_dict[entry_id][-1]["length"] = entry_time - note_file_dict[entry_id][-1]["time"]
                if enum != entry_count - 1:
                    note_file_dict[entry_id].append({"time": entry_time, "length": 1, "note": 105})
        elif entry_type == 'gh5_vocal_marker_note' or entry_type == 'gh5_vocal_lyric':
            for entry in range(entry_count):
                entry_time = read_int()
                entry_text = note_file.read(element_size - 4)
                if all([element_size == 132, entry_type == "gh5_vocal_marker_note"]) or all(
                        [element_size == 36, entry_type == "gh5_vocal_lyric"]):
                    entry_text = entry_text.decode("utf-8").replace("\x00", "")
                else:
                    entry_text = entry_text.decode("utf-16-be").replace("\x00", "")
                if entry_type == 'gh5_vocal_lyric':
                    if entry_text.endswith("-"):
                        entry_text = entry_text[:-1] + "="
                    if entry_text.startswith("="):
                        entry_text = entry_text[1:]
                        note_file_dict[entry_id][-1]["text"] += "-" if not note_file_dict[entry_id][-1][
                            "text"].endswith("=") else ""
                note_file_dict[entry_id].append(
                    {"time": entry_time, "text": entry_text})
        else:
            raise Exception
    return note_file_dict


def read_gh5_perf(perf_bin, song_name):
    perf_file = BytesIO(perf_bin)
    perf_size = perf_file.getbuffer().nbytes
    read_int = lambda a=4, note=perf_file: int.from_bytes(note.read(a), "big")
    dbg = lambda check: PAKExtract.pull_dbg_name(check)
    anim_name = {}
    for x in ["female", "male"]:
        for y in ["", "_alt"]:
            struct_name = f"car_{x}{y}_anim_struct_{song_name}"
            anim_name[hex(int(QBKey(struct_name), 16))] = struct_name
    game = {0x40a001a3: "gh5"}
    game_id = read_int()
    # assert game_id == "gh5"
    dlc_id = dbg(read_int())
    entries = read_int()
    file_type = dbg(read_int())
    assert file_type == "perf"
    perf_file.seek(28)
    perf_file_dict = {}
    cameras = {}
    for perf_entry in range(entries):
        entry_id = dbg(read_int())
        if entry_id in anim_name:
            entry_id = anim_name[entry_id]
        entry_count = read_int()
        entry_type = dbg(read_int())
        if "cameras" in entry_id:
            cameras[entry_id] = []
            for cuts in range(entry_count):
                cut_time = read_int()
                cut_length = read_int(2)
                cut_note = read_int(1)
                cameras[entry_id].append({"time": cut_time, "length": cut_length, "note": cut_note})
        elif "gh5_actor_loops" in entry_type:
            if "type" not in perf_file_dict.keys():
                perf_file_dict["type"] = "gh5"
            try:
                perf_file_dict[entry_id] = {"guitar": {}, "bass": {}, "drum": {}, "vocals": {}}
                for anim in ["guitar", "bass", "vocals", "drum"]:
                    for anim_type in ["pak", "anim_set", "finger_anims", "fret_anims", "strum_anims", "facial_anims"]:
                        if anim != "drum":
                            perf_file_dict[entry_id][anim][anim_type] = dbg(read_int())
                        else:
                            dbg(read_int())
                for anim_type in ["pak", "anim_set", "facial_anims"]:
                    perf_file_dict[entry_id]["drum"][anim_type] = dbg(read_int())
            except:
                perf_file_dict = {}
                break
        elif "gh6_actor_loops" in entry_type:
            if "type" not in perf_file_dict.keys():
                perf_file_dict["type"] = "gh6"
            perf_file_dict[entry_id] = {"guitar": [], "bass": [], "vocals": [], "drum": [], "other": []}
            curr_sect = 0
            anim_loops = []
            for actor in ["guitar", "bass", "vocals", "drum", "other"]:
                for loop in range(50):
                    curr_loop = read_int()
                    if curr_loop == 0:
                        if anim_loops:
                            perf_file_dict[entry_id][actor] = anim_loops.copy()
                            anim_loops = []
                        continue
                    else:
                        anim_loops.append(dbg(curr_loop))
            # perf_file_dict[entry_id] = anim_loops.copy()

    return cameras, perf_file_dict


def midi_entry_time(tempo_data, ev_time, prev_time, tpb):
    map_lower = tempo_data.secondsArray[tempo_data.secondsArray <= ev_time].max()
    arrIndex = tempo_data.songSeconds.index(map_lower)
    timeFromChange = ev_time - tempo_data.songSeconds[arrIndex]
    ticksFromChange = s2t(timeFromChange, tpb, tempo_data.songTempo[arrIndex])
    time_val = tempo_data.songTime[arrIndex] + round(ticksFromChange) - prev_time
    return time_val


def gh5_to_midi(notes, tempo_data, tpb, vox=False, anim=False, drums=False):
    timeStart = 0

    if type(notes) != list:
        notes = notes.entries
    if anim:
        gtr_track = []
        bass_track = []
        rhythm_track = []
        for event in notes:
            note = event["note"]
            ev_time = event["time"] / 1000
            map_lower = tempo_data.secondsArray[tempo_data.secondsArray <= ev_time].max()
            arrIndex = tempo_data.songSeconds.index(map_lower)
            timeFromChange = ev_time - tempo_data.songSeconds[arrIndex]
            ticksFromChange = s2t(timeFromChange, tpb, tempo_data.songTempo[arrIndex])
            timeVal = tempo_data.songTime[arrIndex] + round(ticksFromChange) - timeStart
            try:
                velocity = event["velocity"]
            except:
                velocity = 100
            ev_time_2 = (event["time"] + event["length"]) / 1000
            map_lower_2 = tempo_data.secondsArray[tempo_data.secondsArray <= ev_time_2].max()
            arrIndex_2 = tempo_data.songSeconds.index(map_lower_2)
            timeFromChange_2 = ev_time_2 - tempo_data.songSeconds[arrIndex_2]
            ticksFromChange_2 = s2t(timeFromChange_2, tpb, tempo_data.songTempo[arrIndex_2])
            timeVal_2 = tempo_data.songTime[arrIndex_2] + round(ticksFromChange_2) - timeVal
            if note in range(108, 128):
                gtr_track.append(MidiTrack())
                new_note = 40 + (126 - note)
                gtr_track[-1].append(
                    Message("note_on", time=timeVal, note=new_note, velocity=velocity))

                gtr_track[-1].append(Message("note_on", time=timeVal_2, note=new_note, velocity=0))
            elif note in range(84, 108):
                bass_track.append(MidiTrack())
                new_note = 40 + (103 - note)
                bass_track[-1].append(
                    Message("note_on", time=timeVal, note=new_note, velocity=velocity))

                bass_track[-1].append(Message("note_on", time=timeVal_2, note=new_note, velocity=0))
            else:
                print(f'Unknown anim event {event["note"]} found at {round(event["time"] / 1000, 3)}')

        return gtr_track, bass_track
    else:
        temp_tracks = []
        for event in notes:
            temp_tracks.append(MidiTrack())
            ev_time = event["time"] / 1000
            map_lower = tempo_data.secondsArray[tempo_data.secondsArray <= ev_time].max()
            arrIndex = tempo_data.songSeconds.index(map_lower)
            timeFromChange = ev_time - tempo_data.songSeconds[arrIndex]
            ticksFromChange = s2t(timeFromChange, tpb, tempo_data.songTempo[arrIndex])
            timeVal = tempo_data.songTime[arrIndex] + round(ticksFromChange) - timeStart
            try:
                velocity = event["velocity"]
            except:
                velocity = 100
            if "text" in event.keys():
                temp_tracks[-1].append(
                    MetaMessage("lyrics" if vox else "text", time=timeVal, text=event["text"]))
            else:
                ev_time_2 = (event["time"] + event["length"]) / 1000
                map_lower_2 = tempo_data.secondsArray[tempo_data.secondsArray <= ev_time_2].max()
                arrIndex_2 = tempo_data.songSeconds.index(map_lower_2)
                timeFromChange_2 = ev_time_2 - tempo_data.songSeconds[arrIndex_2]
                ticksFromChange_2 = s2t(timeFromChange_2, tpb, tempo_data.songTempo[arrIndex_2])
                timeVal_2 = tempo_data.songTime[arrIndex_2] + round(ticksFromChange_2) - timeVal

                if vox and event["note"] == 2:
                    temp_tracks[-1].append(
                        MetaMessage("lyrics", time=timeVal + timeVal_2, text="+"))
                else:
                    temp_tracks[-1].append(
                        Message("note_on", time=timeVal, note=event["note"], velocity=velocity))

                    temp_tracks[-1].append(Message("note_on", time=timeVal_2, note=event["note"], velocity=0))

        return temp_tracks


def create_mid_from_qb(pakmid):
    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.lower().find("_s")].lower()
    if re.search(r'^[a-c]dlc', song_name, flags=re.IGNORECASE):
        song_name = song_name[1:]
    qb_sections, file_headers, file_headers_hex, song_files = pak2mid(pakmid, song_name)
    sections_dict = get_section_dict(qb_sections, file_headers_hex)
    game_check = ''.join(x for x in sections_dict.keys())
    gh3 = False
    ghwt = False
    if not re.search(rf"{song_name}_song_easy", game_check, flags=re.IGNORECASE):
        print("GH5+ song found")
    elif not re.search(rf"{song_name}_drum_easy", game_check, flags=re.IGNORECASE):
        print("GH3 song found")
        gh3 = True
    else:
        print("GHWT song found")
        ghwt = True
    band_clips = []
    instruments = 0
    use_cams = 0
    pull_struct = 0
    struct_string = ""
    anim_structs = []
    for files in song_files:
        if re.search(fr"songs/{song_name}\.mid\.qs$", files["file_name"], flags=re.IGNORECASE):
            qs_dict = get_qs_strings(files["file_data"])
            note_file, qb_file, qs_file, cameras, marker_names = wt_to_5_file(sections_dict, qs_dict, song_name,
                                                                              convert="")
            instruments = read_gh5_note(convert_to_gh5_bin(note_file, "note", song_name))
        elif re.search(fr"songs/{song_name}\.note$", files["file_name"], flags=re.IGNORECASE):
            instruments = read_gh5_note(files["file_data"])
        elif re.search(fr"songs/{song_name}\.perf$", files["file_name"], flags=re.IGNORECASE):
            cameras, anim_structs = read_gh5_perf(files["file_data"], song_name)
            use_cams = 1
            pull_struct = 1
        elif re.search(fr"songs/{song_name}\.perf.xml.qb$", files["file_name"], flags=re.IGNORECASE):
            perf_xml_file = QB2Text.convert_qb_file(QB2Text.qb_bytes(files["file_data"]), song_name, file_headers)
            for x in perf_xml_file:
                if x.section_id.endswith("scriptevents"):
                    for y in x.section_data:
                        if y.data_dict["scr"] == "Band_PlayClip":
                            clip_params = y.data_dict["params"]
                            clip_len = round((clip_params["endframe"] - clip_params["startframe"]) / 30 / clip_params["timefactor"] * 1000)
                            band_clips.append([clip_params["clip"],y.data_dict["time"], clip_len+y.data_dict["time"]])
            #print()
    try:
        timesig = sections_dict[f"{song_name}_timesig"].section_data
        fretbars = sections_dict[f"{song_name}_fretbars"].section_data
        if not any([gh3, ghwt]):
            instruments.pop("timesig")
            instruments.pop("fretbar")
    except:
        timesig = instruments["timesig"]
        fretbars = instruments["fretbar"]
        instruments.pop("timesig")
        instruments.pop("fretbar")
    timesig = {x[0]: {"num": x[1], "denom": x[2]} for x in timesig}
    to_add = {}
    for t in timesig.keys():
        if t not in fretbars:
            closest = min(fretbars, key=lambda x: abs(x - t))
            to_add[closest] = timesig[t]
    timesig |= to_add
    curr_timesig = timesig[0]
    last_time = fretbars[1]
    start_temp = int(last_time * 1000 * curr_timesig["denom"] / 4)

    new_mid = MidiFile()
    tpb = new_mid.ticks_per_beat
    tempo_track = MidiTrack()  # Tempo Track
    tempo_track.append(
        MetaMessage("time_signature", time=0, numerator=timesig[0]["num"], denominator=timesig[0]["denom"]))
    tempo_track.append(MetaMessage("set_tempo", time=0, tempo=start_temp))

    for bar in fretbars[2:]:
        delta = bar - last_time
        curr_time = int(tpb * 4 / curr_timesig["denom"])
        if last_time in timesig:
            tempo_track.append(
                MetaMessage("time_signature", time=curr_time, numerator=timesig[last_time]["num"],
                            denominator=timesig[last_time]["denom"]))
            curr_timesig = timesig[last_time]
            curr_temp = delta * 1000 * curr_timesig["denom"] / 4
            tempo_track.append(MetaMessage("set_tempo", time=0, tempo=int(curr_temp)))
        else:
            curr_temp = delta * 1000 * curr_timesig["denom"] / 4
            tempo_track.append(MetaMessage("set_tempo", time=curr_time, tempo=int(curr_temp)))

        last_time = bar
    new_mid.tracks.append(tempo_track)

    song_map = mid_qb.midiProcessing(new_mid)
    tempo_data = mid_qb.MidiInsert(mid_qb.song_array(song_map))
    tempo_data.set_seconds_array(np.array(tempo_data.songSeconds))

    if gh3:
        new_mid.tracks += read_gh3_note(sections_dict, tempo_data, tpb)
        return new_mid, struct_string
    """elif ghwt:
        new_mid.tracks += read_gh3_note(sections_dict, tempo_data, tpb, "GHWT")"""


    drum_events = {"name": "PART DRUMS"}
    gtr_events = {"name": "PART GUITAR"}
    bass_events = {"name": "PART BASS"}
    vox_events = {"name": "PART VOCALS"}
    to_pop = []

    if instruments:
        for x in instruments.keys():
            if "drum" in x:
                drum_events[x] = instruments[x]
                to_pop.append(x)
            elif "bass" in x:
                bass_events[x] = instruments[x]
                to_pop.append(x)
            elif "guitar" in x and not "marker" in x:
                gtr_events[x] = instruments[x]
                to_pop.append(x)
            elif "vocal" in x and not "marker" in x:
                vox_events[x] = instruments[x]
                to_pop.append(x)
        for x in to_pop:
            instruments.pop(x)
        for inst in [drum_events, gtr_events, bass_events, vox_events]:
            new_mid.add_track(inst["name"])
            if "GUITAR" in inst["name"]:
                gtr_index = len(new_mid.tracks) - 1
            elif "BASS" in inst["name"]:
                bass_index = len(new_mid.tracks) - 1
            elif "DRUMS" in inst["name"]:
                drum_index = len(new_mid.tracks) - 1
            inst.pop("name")
            all_tracks = [new_mid.tracks[-1]]
            for track in inst.keys():
                if "instrument" in track or "expert" in track:
                    all_tracks.append(mido.merge_tracks(gh5_to_midi(inst[track], tempo_data, tpb)))
                elif "vocal" in track:
                    all_tracks.append(mido.merge_tracks(gh5_to_midi(inst[track], tempo_data, tpb, vox=True)))
            new_mid.tracks[-1] = mido.merge_tracks(all_tracks)

    non_play = ["scripts", "anim", "triggers", "cameras", "lightshow", "crowd", "drums"]
    for x in non_play:
        try:
            if not sections_dict[f"{song_name}_{x}_notes"].array_node_type == "Floats":
                anim_notes = read_wt_event(sections_dict[f"{song_name}_{x}_notes"].section_data)
                if x == "anim":
                    gtr_track, bass_track = gh5_to_midi(anim_notes, tempo_data, tpb, anim=True)
                    new_mid.tracks[gtr_index] = mido.merge_tracks([new_mid.tracks[gtr_index]] + gtr_track)
                    new_mid.tracks[bass_index] = mido.merge_tracks([new_mid.tracks[bass_index]] + bass_track)
                else:
                    new_mid.add_track(f"{x}")
                    anim_tracks = [new_mid.tracks[-1]] + gh5_to_midi(anim_notes, tempo_data, tpb)
                    anim_notes_midi = mido.merge_tracks(anim_tracks)
                    if x == "drums":
                        drum_anims = []
                        other_drum = []
                        time = 0
                        for drum_note in anim_notes_midi:
                            time += drum_note.time
                            drum_note.time = time
                            if not drum_note.is_meta:
                                if drum_note.note in mid_qb.wor_to_rb_drums and not ghwt:
                                    drum_anims.append(MidiTrack())
                                    drum_anim_note = mid_qb.wor_to_rb_drums[drum_note.note]
                                    drum_anims[-1].append(
                                        Message("note_on", time=time, note=drum_anim_note, velocity=drum_note.velocity))
                            other_drum.append(MidiTrack())
                            other_drum[-1].append(drum_note)
                            # print()
                        anim_notes_midi = mido.merge_tracks(other_drum)
                        new_mid.tracks[drum_index] = mido.merge_tracks([new_mid.tracks[drum_index]] + drum_anims)

                    new_mid.tracks[-1] = anim_notes_midi
        except KeyError:
            continue
        except Exception as E:
            raise E
        try:
            if not sections_dict[f"{song_name}_{x}"].array_node_type == "Floats":
                if new_mid.tracks[-1].name != x:
                    new_mid.add_track(f"{x}")
                anim_notes = read_wt_event(sections_dict[f"{song_name}_{x}"].section_data, 1)

                anim_tracks = [new_mid.tracks[-1]] + gh5_to_midi(anim_notes, tempo_data, tpb)

                anim_notes_midi = mido.merge_tracks(anim_tracks)
                new_mid.tracks[-1] = anim_notes_midi
        except KeyError:
            continue
        except Exception as E:
            raise E


    if use_cams:
        new_mid.add_track(f"cameras")
        moments = cameras["momentcameras"]
        autocuts = cameras["autocutcameras"]
        anim_tracks = [new_mid.tracks[-1]] + gh5_to_midi(moments, tempo_data, tpb)
        anim_tracks += gh5_to_midi(autocuts, tempo_data, tpb)
        anim_notes_midi = mido.merge_tracks(anim_tracks)
        new_mid.tracks[-1] = anim_notes_midi
        gh3_cams = []
        gh3_notes = mid_qb.wor_camera_converts["gh3"]
        time = 0
        for anims in anim_notes_midi:
            time += anims.time
            if not anims.is_meta:
                if anims.note in gh3_notes:
                    gh3_cams.append(MidiTrack())
                    gh3_cams[-1].append(
                        Message("note_on", time=time, note=gh3_notes[anims.note], velocity=anims.velocity))
        new_mid.add_track()
        new_mid.tracks[-1] = mido.merge_tracks(gh3_cams)
        new_mid.tracks[-1].name = "GH3 VENUE"

    if band_clips:
        band_midi = []
        for enum, x in enumerate(band_clips):
            time1 = x[1]/1000
            time2 = x[2]/1000
            map_lower = tempo_data.secondsArray[tempo_data.secondsArray <= time1].max()
            map_lower2 = tempo_data.secondsArray[tempo_data.secondsArray <= time2].max()
            arrIndex = tempo_data.songSeconds.index(map_lower)
            arrIndex2 = tempo_data.songSeconds.index(map_lower2)
            timeFromChange = time1 - tempo_data.songSeconds[arrIndex]
            timeFromChange2 = time2 - tempo_data.songSeconds[arrIndex2]
            ticksFromChange = s2t(timeFromChange, tpb, tempo_data.songTempo[arrIndex])
            ticksFromChange2 = s2t(timeFromChange2, tpb, tempo_data.songTempo[arrIndex2])
            timeVal = tempo_data.songTime[arrIndex] + round(ticksFromChange)
            timeVal2 = tempo_data.songTime[arrIndex2] + round(ticksFromChange2) - timeVal

            band_midi.append(MidiTrack())
            clip_note = (enum % 40) + 40
            band_midi[-1].append(Message("note_on", time=timeVal, note=clip_note, velocity=100))
            band_midi[-1].append(Message("note_on", time=timeVal2, note=clip_note, velocity=0))

        band_midi = mido.merge_tracks(band_midi)
        band_midi.name = "Band_Clips"
        new_mid.tracks.append(band_midi)

    if pull_struct and anim_structs:
        if anim_structs["type"] == "gh5":
            anim_structs.pop("type")
            for x in anim_structs.keys():
                struct_string += f"{x}" + " = {\n"
                for structs in anim_structs[x].keys():
                    struct_string += "\t" + f"{structs}" + " = {\n"
                    for anims in anim_structs[x][structs].keys():
                        struct_string += "\t\t" + f"{anims}" + f" = {anim_structs[x][structs][anims]}" + "\n"
                    struct_string += "\t}\n"
                struct_string += "}\n"
        else:
            anim_structs.pop("type")
            for x in anim_structs.keys():
                struct_string += f"{x}" + " = {\n"
                for structs in anim_structs[x].keys():
                    struct_string += "\t" + f"{structs}" + " = {\n"
                    for anims in anim_structs[x][structs]:
                        struct_string += "\t\t" + f"{anims}" + "\n"
                    struct_string += "\t}\n"
                struct_string += "}\n"

    return new_mid, struct_string


if __name__ == "__main__":
    pass
