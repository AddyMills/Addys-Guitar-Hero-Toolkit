import sys
import os
import random
import re
import mido
import CRC
import numpy as np

root_folder = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{root_folder}\\pak_extract")
sys.path.append(f"{root_folder}\\midqb_gen")
sys.path.append(f"{root_folder}\\ska_switcher")
from pak_extract import PAKExtract, QB2Text, Text2QB
from midqb_gen import MidQbGen as mid_qb
from ska_converter import ska_switch
from gh_sections import gh_sections
from toolkit_variables import *
from io import StringIO, BytesIO
from debug_qs import qs_debug
from copy import deepcopy
from CRC import qbkey_hex, QBKey
from dbg import checksum_dbg
from mido import MidiFile, MidiTrack, second2tick as s2t, Message, MetaMessage
from random import randint


def round_time(entry):
    time_trunc = int(str(entry).zfill(6)[-2:])
    if time_trunc == 99:
        new_time = entry + 1
    elif time_trunc >= 67:
        new_time = entry - (time_trunc - 67)
    elif time_trunc >= 33:
        new_time = entry - (time_trunc - 33)
    else:
        new_time = entry - time_trunc
    return new_time


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
    with open(pakmid, 'rb') as pak:
        mid_bytes = pak.read()
    mid_bytes = PAKExtract.check_decomp(mid_bytes, output_decomp=False)
    song_files = PAKExtract.main(mid_bytes, f"{song_name}_song.pak", toolkit_mode=True)
    song_names = [song_name]
    starts = ["a", "b"]
    if song_name[0] in starts:
        song_names.append(song_name[1:])
    for x in song_files:
        if "0x" in x['file_name']:
            file_name_scrubbed = x['file_name'].replace("\\", "")
            if file_name_scrubbed.endswith(".qb"):
                qb_string = f'songs/{song_name}.mid.qb'
                crc_name = int(PAKExtract.QBKey(f'songs/{song_name}.mid.qb'), 16)
                hex_name = int(file_name_scrubbed[:-3], 16)
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


def convert_to_gh3(pakmid, output=f'{os.getcwd()}', singer=ska_switch.lipsync_dict["gh3_singer"]):
    if not "_song.pak" in pakmid:
        warning = input(
            "WARNING: File does not appear to be a validly named mid PAK file. Do you want to continue? (Y/N): ")
        if not warning.lower().startswith("y"):
            return -1

    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")].lower()

    track_types = []
    qb_sections, file_headers, file_headers_hex, song_files = pak2mid(pakmid, song_name)
    rhythm_sections, rhythm_dict = get_rhythm_headers(song_name)

    sections_dict = {}
    for x in qb_sections:
        if x.section_id in file_headers_hex.keys():
            x.set_new_id(file_headers_hex[x.section_id])
        if x.section_id not in rhythm_sections:
            sections_dict[x.section_id] = x

    # Swap camera cuts
    for x in sections_dict[f"{song_name}_cameras_notes"].section_data:
        if type(gha_to_gh3[x[1]]) == list:
            raise Exception("Fatal error when processing camera swaps.")
        else:
            x[1] = gha_to_gh3[x[1]]

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
    perf_to_ignore = ["SpecialCamera_PlayAnim".lower(), "Band_PlaySimpleAnim".lower()]
    new_perf = []
    for x in sections_dict[f"{song_name}_performance"].section_data:
        if x.data_value[1].data_value.lower() in perf_to_ignore:
            continue
        elif x.data_value[1].data_value == 'Band_ChangeStance':
            if x.data_value[2].struct_data_struct[0].data_value.lower() == "rhythm":
                continue
        elif x.data_value[1].data_value == 'Band_PlayAnim':
            if x.data_value[2].struct_data_struct[0].data_value.lower() == "rhythm":
                continue
        # else:
        new_perf.append(x)

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
            x["file_data"] = ska_switch.main(x["file_data"], singer)

    gh3_array = []
    for x in song_files:
        gh3_array.append([x["file_data"], x['file_name']])

    # Create the song PAK file
    song_pak = mid_qb.pakMaker(gh3_array)

    # raise Exception

    return song_name, song_pak


def convert_to_gha(pakmid, output=f'{os.getcwd()}', singer=ska_switch.lipsync_dict["gha_singer"]):
    if not "_song.pak" in pakmid:
        warning = input(
            "WARNING: File does not appear to be a validly named mid PAK file. Do you want to continue? (Y/N): ")
        if not warning.lower().startswith("y"):
            return -1

    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")]

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
            rhythm_section.set_data(sections_dict[f"{song_name}_song_Expert"].section_data)
            rhythm_section.set_new_id(x)
            rhythm_section.set_array_node_type("ArrayInteger")
            rhythm_section.set_pak_name(sections_dict[f"{song_name}_song_Expert"].section_pak_name)
            rhythm_parts.append(rhythm_section)

    # Swap camera cuts
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
                x["file_data"] = ska_switch.main(x["file_data"], ska_switch.lipsync_dict["gha_guitarist"])
            else:
                x["file_data"] = ska_switch.main(x["file_data"], singer)
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
                                raise Exception(
                                    f"{'Lyric' if item.name == 'vocallyrics' else 'Phrase'} \'{notes}\' is longer than {int((item.size - 4) / 2)} characters long.")
                            else:
                                utf_16 += b'\x00' * ((item.size - 4) - len(utf_16))
                                # print(len(utf_16))
                                n_info += utf_16
                    elif item.name == "bandmoment":
                        n_info += int.to_bytes(notes, 4, "big")
    return n_info


def perf_2_bin(perf_file, song_name):
    p_info = bytearray()
    for x in ["autocutcameras", "momentcameras"]:
        item = perf_file[x]
        p_info += qbkey_hex(x)  # QB key of camera type
        p_info += int.to_bytes(round(len(item) / 3), 4, "big")
        p_info += qbkey_hex("gh5_camera_note")
        for enum, camera_cut in enumerate(item):
            p_info += int.to_bytes(camera_cut, 4 if enum % 3 == 0 else 2 if enum % 3 == 1 else 1, "big")
    for x in ["female", "male"]:
        item = perf_file[x]
        for y in ["", "_alt"]:
            p_info += qbkey_hex(f"car_{x}{y}_anim_struct_{song_name}")
            p_info += int.to_bytes(1, 4, "big")
            p_info += qbkey_hex("gh5_actor_loops")
            for anim_loop in item:
                p_info += qbkey_hex(anim_loop)
    return p_info


def convert_to_gh5_bin(raw_file, file_type, song_name="", **kwargs):
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
            return header + perf_2_bin(raw_file, song_name)
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
        anims.append(x)

    return wor_anim


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

    for x in qb_sections:
        if x.section_id in file_headers_hex.keys():
            x.set_new_id(file_headers_hex[x.section_id])
        sections_dict[x.section_id] = x
    return sections_dict


def perf_struct(female_struct, male_struct):
    for struct in [female_struct, male_struct]:
        struct_perf = []
        for instrument in ["guitar", "bass"]:
            for perf_type in ["pak", "anim_set", "finger_anims", "fret_anims", "strum_anims", "facial_anims"]:
                struct_perf.append(struct[instrument][perf_type])
        # Vocals anims in GH5/6 use 3 exclusive values, and 3 the same
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


def compile_perf_anims(script_sections, anim_data_dict, use_anims=1, **kwargs):
    perf_file = {}
    if not use_anims:
        female_struct, male_struct = default_anim_structs()
    else:
        male_struct = deepcopy(anim_struct)
        female_struct = deepcopy(anim_struct)
        female_anims = ["judita", "ginger", "morgan", "amanda", "debbie", "natalie", "haley"]
        special_anim_names = {"l_guit_chrisvance_bulls_anims": "L_GUIT_ChrisV_Bulls_F_anims",
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
                              }

        for section in script_sections:
            if re.search(r"^(car_female|car_male)", section.section_id, flags=re.IGNORECASE):
                for anims in section.section_data:
                    anims.data_id = grab_debug_2(anims.data_id, checksum_dbg)
                    for anim_types in anims.struct_data_struct:
                        anim_types.data_id = grab_debug_2(anim_types.data_id, checksum_dbg)
                        anim_types.data_value = grab_debug_2(anim_types.data_value, checksum_dbg)
                        car_name = anim_types.data_value
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
                                female_struct[anims.data_id.lower()][anim_types.data_id] = anim_types.data_value
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
                                male_struct[anims.data_id.lower()][anim_types.data_id] = anim_types.data_value
            elif "Struct" in section.section_type:
                if section.section_id not in anim_data_dict:
                    anim_data_dict[section.section_id] = section
            else:
                pass

    female_struct, male_struct = perf_struct(female_struct, male_struct)

    perf_file["female"] = female_struct["perf"]
    perf_file["male"] = male_struct["perf"]
    return perf_file


def wt_to_5_file(sections_dict, qs_dict, song_name, new_name="", convert="gh5", **kwargs):
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

                for marker_struct in sections_dict[x].section_data:
                    g_markers.append(marker_struct.data_value[0].data_value)
                    str_start = '\\u[m]'
                    str_check = '\\L_ENDOFSONG'
                    if marker_struct.data_value[1].data_type != "StructItemString":
                        try:
                            qs_key = QBKey(marker_struct.data_value[1].data_value)
                            try:
                                qs_1 = qs_debug_qb[int(qs_key, 16)]
                            except Exception as E:
                                raise E
                                qs_1 = qs_debug_qb[int(marker_struct.data_value[1].data_value, 16)]
                            qs_2 = f"{str_start if qs_vals[qs_1] != str_check else ''}{qs_vals[qs_1]}"
                            qs_file.append(qs_2)
                            marker_names[qs_vals[qs_1]] = g_markers[-1]
                            g_markers.append(CRC.QBKey_qs(qs_2))
                            qb_file[f"{new_name}_localized_strings"].section_data.append(
                                hex(int(CRC.QBKey_qs(qs_2), 16)))
                        except Exception as E:
                            raise E
                            g_markers.append("")
                            print(f"Failed to find section marker in {new_name} at {g_markers[-1]}")
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

    return note_file, qb_file, qs_file, cameras, marker_names


def convert_to_5(pakmid, new_name, **kwargs):
    root_folder = os.path.realpath(os.path.dirname(__file__))
    if not "_song.pak" in pakmid.lower():
        warning = input(
            "WARNING: File does not appear to be a validly named mid PAK file (ending in '_song.pak'). Do you want to continue? (Y/N): ")
        if not warning.lower().startswith("y"):
            return -1

    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")].lower()

    qb_sections, file_headers, file_headers_hex, song_files = pak2mid(pakmid, song_name)
    if kwargs:
        if "anim_pak" in kwargs:
            anim_pak = kwargs["anim_pak"]
        else:
            anim_pak = 0
        if "drum_anim" in kwargs:
            try:
                drum_anim_mid = MidiFile(kwargs["drum_anim"])
                for x in drum_anim_mid.tracks:
                    if x.name == "drums":
                        drum_anim = x
                        tempo_data = mid_qb.get_song_tempo_data(drum_anim_mid)
                        break
                else:
                    print("Midi file found, but no drum anims to replace!")
                    tempo_data = 0
                del (drum_anim_mid)
            except:
                drum_anim = 0
        else:
            drum_anim = 0
        if "simple_anim" in kwargs:
            simple_anim = 1
        else:
            simple_anim = 0
    else:
        anim_pak = 0
        drum_anim = 0
        simple_anim = 0

    if anim_pak:
        song_files += pak2mid(anim_pak, song_name)[3]
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
    perf_xml_file = {}
    perf_xml_file[f"{new_name}_scriptevents"] = PAKExtract.qb_section("SectionArray")
    perf_xml_file[f"{new_name}_scriptevents"].set_pak_name(f"songs/{new_name}.perf.xml.qb")
    perf_xml_file[f"{new_name}_scriptevents"].set_new_id(f"{new_name}_scriptevents")
    perf_xml_file[f"{new_name}_scriptevents"].set_array_node_type("ArrayStruct")

    anim_data_dict = gen_wt_anim_dict(song_name, file_headers)  # Dictionary for all special animations

    note_file, qb_file, qs_file, cameras, marker_names = wt_to_5_file(sections_dict, qs_dict, song_name, new_name)

    if script_sections:
        perf_file = compile_perf_anims(script_sections, anim_data_dict, use_anims)
    else:
        perf_file = compile_perf_anims(script_sections, anim_data_dict, 0)
    perf_file["autocutcameras"] = cameras.autocut
    perf_file["momentcameras"] = cameras.moment

    other_skas = {}
    for x in os.scandir(f"{root_folder}\\conversion_files\\ska"):
        other_skas[x.name[:x.name.find(".ska.xen")].lower()] = x.path

    for qb_item in ["cameras_notes", "facial"]:
        qb_file[f"{new_name}_{qb_item}"] = PAKExtract.qb_section("SectionArray")
        qb_file[f"{new_name}_{qb_item}"].make_empty()
        qb_file[f"{new_name}_{qb_item}"].set_pak_name(f"songs/{new_name}.mid.qb")
        qb_file[f"{new_name}_{qb_item}"].set_new_id(f"{new_name}_{qb_item}")
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
                        vox_star_entry += [p_time + 4, note_file["vocalsmarkers"].entries[y + 1] - 3 - (p_time + 4)]
                    start_pos = (start_pos + 1) % len(rand_phrase)
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
                        "Band_ForceAllToIdle", "Band_ShowMicStand", "Band_HideMicStand", "Band_ShowMic_Stand"]
    allowed_converts += [hex(int(CRC.QBKey(x), 16)) for x in allowed_converts]
    ignored_converts = ["Band_PlaysimpleAnim", "dummy_function", "Band_SetStrumStyle", "VH_UndergroundLogo_On",
                        "VH_UndergroundLogo_Off"]
    ignored_converts += [hex(int(CRC.QBKey(x), 16)) for x in ignored_converts]

    params_check = ["ff_anims", "mf_anims"]
    params_check += [hex(int(CRC.QBKey(x), 16)) for x in params_check]

    # First add some looping anims
    for x in ["guitarist", "bassist", "vocalist", "drummer"]:
        perf_xml_file[f"{new_name}_scriptevents"].section_data.append(PAKExtract.new_play_loop(0, x))

    play_clip_count = 0
    first_moment = cameras.moment[0] if cameras.moment[0] != 0 else cameras.moment[3]
    first_bass = get_first_note(note_file["bassexpertinstrument"].entries)
    first_guit = get_first_note(note_file["guitarexpertinstrument"].entries)
    first_note = int(round(min(first_moment, cameras.autocut[6], first_bass, first_guit) / 1000 * 30))
    for x in qb_file[f"{new_name}_performance"].section_data:
        for struct_num, script_val in enumerate(x.data_value):
            if script_val.data_value in allowed_converts:
                if script_val.data_value in check_dbg("Band_ChangeFacialAnims"):
                    """if simple_anim:
                        continue"""
                    for y in x.data_dict["params"].keys():
                        if y in check_dbg("ff_anims") or y in check_dbg("mf_anims"):
                            new_rock = x.data_dict["params"][y]
                            face_type = new_rock[new_rock.rfind("_"):]
                            perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                                PAKExtract.new_facial_anim_gh5(x.data_dict["time"],
                                                               x.data_dict["params"]["name"], f"{face_type}"))
                            break
                        elif y in check_dbg("fa_type"):
                            if x.data_dict["params"]["name"].lower() == "basssist":
                                perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                                    PAKExtract.new_facial_anim_gh5(round_time(x.data_dict["time"]),
                                                                   "Bassist", x.data_dict["params"]["fa_type"]))
                            else:
                                perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)
                elif script_val.data_value in check_dbg("Band_PlayClip") or script_val.data_value in check_dbg(
                        "BandPlayClip"):
                    if script_val.data_value in check_dbg("BandPlayClip"):
                        print(f"Found broken script BandPlayClip. Fixing to Band_PlayClip")
                    params = x.data_dict["params"]
                    try:
                        clip_to_parse = anim_data_dict[params["clip"]]
                    except:
                        continue
                    anim_skas = clip_to_parse.data_dict["anims"]
                    for ska in anim_skas.keys():
                        if f"{anim_skas[ska]}.ska" not in song_files_dict:
                            if f"{anim_skas[ska].lower()}" in other_skas:
                                with open(other_skas[anim_skas[ska].lower()], 'rb') as f:
                                    new_anim = f.read()
                                song_files_dict[f"{anim_skas[ska]}.ska"] = {
                                    "file_name": f"{anim_skas[ska]}.ska", "file_data": new_anim}
                    """
                    Add support for "secondary, bassist, guitarist, etc. cameras
                    Secondary seems to be camera 99, i.e. slot 10
                    Bassist cam seems to be camera 6, or camera 93, i.e. slot 4
                    Guitarist seems to be camera 94, i.e. slot 5
                    """
                    if x.data_dict["time"] != 0:
                        new_clip_data, startf, endf = band_clip_from_wt(clip_to_parse, params, song_files_dict,
                                                                        ven_cams=cameras, use_anims=use_anims)
                    else:
                        new_clip_data, startf, endf = band_clip_from_wt(clip_to_parse, params, song_files_dict,
                                                                        ven_cams=cameras, next_note=first_note,
                                                                        use_anims=use_anims)
                    if new_clip_data == -1:
                        print(f"Invalid anim: {clip_to_parse.section_id}. Skipping")
                        continue
                    clip_name = clip_to_parse.section_id + f"_{str(play_clip_count).zfill(2)}"
                    play_clip_count += 1
                    perf_xml_file[clip_name] = PAKExtract.qb_section("SectionStruct")
                    perf_xml_file[clip_name].set_all(clip_name, new_clip_data, f"songs/{new_name}.perf.xml.qb")
                    perf_xml_file[f"{new_name}_scriptevents"].section_data.append(
                        PAKExtract.new_play_clip(round_time(x.data_dict["time"]), clip_name, startf, endf))
                    # print()
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
                    perf_xml_file[f"{new_name}_scriptevents"].section_data.append(x)

                    # print()
                break
            elif script_val.data_id == "scr":
                if script_val.data_value not in ignored_converts:
                    print(f"{script_val.data_value} found. Not sure what to do with it")

    ska_data = []
    for pak_file in song_files_dict.keys():
        if song_files_dict[pak_file]["file_name"].endswith(".ska"):
            # if pak_file["file_name"].startswith("gh4_"):
            ska_data.append(song_files_dict[pak_file])

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
    if "rainingblood" in pakmid:  # I need to make an exception for Raining Blood due to the steady stream of green notes
        band_moments = [[66532, 3167], [120541, 3300], [169491, 3100]]
    note_file["bandmoment"].add_item([j for i in band_moments for j in i])

    perf_xml_file = reorg_perfqb(perf_xml_file)
    qb_file = reorg_qb(qb_file, new_name)

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
    # Replace drum anims if found
    if drum_anim:
        print("Drum animation override found. Converting...")
        qb_file[f"{new_name}_drums_notes"].section_data = mid_qb.make_wt_drum_anims(drum_anim, tempo_data)
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
        {"file_name": f"songs/{new_name}.perf", "file_data": convert_to_gh5_bin(perf_file, "perf", new_name)})
    song_data.append(
        {"file_name": f"songs/{new_name}.perf.xml.qb",
         "file_data": convert_to_gh5_bin(perf_xml_file, "perf_xml", console="PC", endian="big")})
    return song_data + ska_data


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
    pak_bytes += pab_bytes
    if pak_bytes[:4] == b'CHNK':  # Check for xbox compressed file
        pak_bytes = PAKExtract.decompress_pak(pak_bytes)
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


def output_mid(mid_file, output="", hopo=170, filename=""):
    pak_file, filename = mid_qb.make_mid(mid_file, hopo, filename)
    if output == "":
        output = os.path.dirname(mid_file)
    with open(f"{output}\\{filename}_song.pak.xen", 'wb') as f:
        f.write(pak_file)


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


def band_clip_from_wt(band_clip, params, anim_data, ven_cams, **kwargs):
    ven_cams.create_cam_dict()
    if "use_anims" in kwargs:
        use_anims = kwargs["use_anims"]
    else:
        use_anims = 1
    to_pull = ["startnodes", "anims", "cameras", "arms", "secondary_cameras", "guitarist_cameras", "vocalist_cameras",
               "bassist_cameras"]
    band = ["guitarist", "bassist", "drummer", "vocalist"]
    camera_slots = {"cameras": 0, "vocalist_cameras": 0, "bassist_cameras": 3, "guitarist_cameras": 6}
    cam_spec = ["name", "anim"]
    spelling_errors = {"guitairstist": "guitarist",
                       "basssist": "bassist"}
    arms_dict = {"off": "False", "on": "True"}
    data = band_clip.data_dict
    characters = {}
    for player in band:
        characters[player] = {}
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
                                raise Exception
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
    for param in params.keys():
        if param == "startframe":
            startframe = params[param]
        if param == "endframe":
            endframe = params[param]
    char_dict = []
    for player in band:
        curr = characters[player]
        if characters[player]:
            if player == "drummer" and not use_anims:
                continue
            if "startnode" not in curr:
                curr["startnode"] = f"{player}_start"
            if "anim" not in curr:
                # curr["anim"] = 0
                continue
            else:
                if curr[
                    "anim"].lower() == "none":  # Skip the character if there's no animation played (GHM has this sometimes)
                    continue
            curr_char = mid_qb.gh5_band_clip(player, curr["startnode"], curr["anim"])
            if "arms" in curr:
                for arms in curr["arms"].keys():
                    x_arm = curr["arms"][arms]  # current armature
                    setattr(curr_char, arms, (x_arm if x_arm.lower() not in arms_dict else arms_dict[x_arm.lower()]))

            setattr(curr_char, "startframe", startframe)
            if endframe:  # Set the endframe if it exists
                setattr(curr_char, "endframe", endframe)
            elif "next_note" in kwargs and use_anims:  # If it's the first Clip event (most likely an idle event). Play until first note/camera cut
                endframe = startframe + kwargs["next_note"]
                setattr(curr_char, "endframe", startframe + kwargs["next_note"] - 1)
            else:  # Nuclear option. Since endframe is kind of needed, this will grab the last frame of the ska file and insert it.
                try:
                    import struct
                    endframe = anim_data[f"{characters[player]['anim']}.ska"]["file_data"][40:44]
                    endframe = struct.unpack(">f", endframe)[0]
                    endframe = round(endframe * 30)
                    setattr(curr_char, "endframe", endframe)
                except:
                    return -1, -1, -1

            char_dict.append(deepcopy(curr_char))
    char_data = []
    camera_qb = PAKExtract.camera_band_clip(cameras)
    if not cameras:
        camera_qb.make_empty_array()
    for char in char_dict:
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


def set_note_type(note, accents, ghost = 0):
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


def read_gh5_note(note_bin, drum_mode=False):
    note_file = BytesIO(note_bin)
    read_int = lambda a=4, note=note_file: int.from_bytes(note.read(a), "big")
    dbg = lambda check: PAKExtract.pull_dbg_name(check)
    game = {0x40a000d2: "gh5", 0x40c001a3: "gh6"}
    game_id = game[read_int()]
    dlc_id = dbg(read_int())
    entries = read_int()
    file_type = dbg(read_int())
    assert file_type == "note"
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
                raise Exception
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
        elif entry_id == "vocals":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_length = read_int(2)
                entry_note = read_int(1)
                note_file_dict[entry_id].append({"time": entry_time, "length": entry_length, "note": entry_note})
        elif entry_id == "vocalfreeform":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_length = read_int()
                entry_unk = read_int(2)
                note_file_dict[entry_id].append({"time": entry_time, "length": entry_length, "note": 104})
        elif entry_id == "vocalphrase":
            for enum, entry in enumerate(range(entry_count)):
                entry_time = read_int()
                if enum != 0:
                    note_file_dict[entry_id][-1]["length"] = entry_time - note_file_dict[entry_id][-1]["time"]
                if enum != entry_count - 1:
                    note_file_dict[entry_id].append({"time": entry_time, "length": 1, "note": 105})
        elif entry_id == "vocalsmarkers" or entry_id == "vocallyrics":
            for entry in range(entry_count):
                entry_time = read_int()
                entry_text = note_file.read(element_size - 4)
                entry_text = entry_text.decode("utf-16-be").replace("\x00", "")
                if entry_id == "vocallyrics":
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
            anim_name[hex(int(QBKey(struct_name),16))] = struct_name
    game = {0x40a001a3: "gh5"}
    game_id = game[read_int()]
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



def add_to_midi(notes, tempo_data, tpb, vox=False, anim=False):
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
            elif note in range(84, 105):
                bass_track.append(MidiTrack())
                new_note = 40 + (103 - note)
                bass_track[-1].append(
                    Message("note_on", time=timeVal, note=new_note, velocity=velocity))

                bass_track[-1].append(Message("note_on", time=timeVal_2, note=new_note, velocity=0))
            else:
                print(f"Unknown anim event found at {round(event.time / 1000, 3)}")

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
    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.lower().find("_song")].lower()
    if song_name.startswith("bdlc"):
        song_name = song_name[1:]
    qb_sections, file_headers, file_headers_hex, song_files = pak2mid(pakmid, song_name)
    sections_dict = get_section_dict(qb_sections, file_headers_hex)
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
    try:
        timesig = sections_dict[f"{song_name}_timesig"].section_data
        fretbars = sections_dict[f"{song_name}_fretbars"].section_data
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
    start_temp = last_time * 1000

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
            inst.pop("name")
            all_tracks = [new_mid.tracks[-1]]
            for track in inst.keys():
                if "instrument" in track or "expert" in track:
                    all_tracks.append(mido.merge_tracks(add_to_midi(inst[track], tempo_data, tpb)))
                elif "vocal" in track:
                    all_tracks.append(mido.merge_tracks(add_to_midi(inst[track], tempo_data, tpb, vox=True)))
            new_mid.tracks[-1] = mido.merge_tracks(all_tracks)

    non_play = ["scripts", "anim", "triggers", "cameras", "lightshow", "crowd", "drums"]
    for x in non_play:
        try:
            if not sections_dict[f"{song_name}_{x}_notes"].array_node_type == "Floats":
                anim_notes = read_wt_event(sections_dict[f"{song_name}_{x}_notes"].section_data)
                if x == "anim":
                    gtr_track, bass_track = add_to_midi(anim_notes, tempo_data, tpb, anim=True)
                    new_mid.tracks[gtr_index] = mido.merge_tracks([new_mid.tracks[gtr_index]] + gtr_track)
                    new_mid.tracks[bass_index] = mido.merge_tracks([new_mid.tracks[bass_index]] + bass_track)
                else:
                    new_mid.add_track(f"{x}")
                    anim_tracks = [new_mid.tracks[-1]] + add_to_midi(anim_notes, tempo_data, tpb)
                    anim_notes_midi = mido.merge_tracks(anim_tracks)
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

                anim_tracks = [new_mid.tracks[-1]] + add_to_midi(anim_notes, tempo_data, tpb)

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
        anim_tracks = [new_mid.tracks[-1]] + add_to_midi(moments, tempo_data, tpb)
        anim_tracks += add_to_midi(autocuts, tempo_data, tpb)
        anim_notes_midi = mido.merge_tracks(anim_tracks)
        new_mid.tracks[-1] = anim_notes_midi

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
