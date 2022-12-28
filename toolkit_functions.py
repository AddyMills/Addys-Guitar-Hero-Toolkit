import sys
import os
import random
import re
import mido

sys.path.append(f"{os.getcwd()}\\pak_extract")
sys.path.append(f"{os.getcwd()}\\midqb_gen")
sys.path.append(f"{os.getcwd()}\\ska_switcher")
from pak_extract import PAKExtract, QB2Text, Text2QB
from midqb_gen import MidQbGen as mid_qb
from ska_switcher import ska_switcher
from gh_sections import gh_sections
from toolkit_variables import *
from io import StringIO


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
    song_files = PAKExtract.main(mid_bytes, "")
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
    if "mid_data_bytes" not in locals():
        raise Exception("No MIDI data found in PAK file.")
    file_headers = QB2Text.createHeaderDict(song_name)
    file_header_keys = file_headers.keys()
    file_headers_hex = {}
    for x in file_headers.keys():
        file_headers_hex[hex(file_headers[x])] = x
    qb_sections = QB2Text.convert_qb_file(QB2Text.qb_bytes(mid_data_bytes), song_name, file_headers)

    return qb_sections, file_headers, file_headers_hex, song_files


def convert_to_gh3(pakmid, output=f'{os.getcwd()}', singer=ska_switcher.lipsync_dict["gh3_singer"]):
    if not "_song.pak" in pakmid:
        warning = input(
            "WARNING: File does not appear to be a validly named mid PAK file. Do you want to continue? (Y/N): ")
        if not warning.lower().startswith("y"):
            return -1

    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")]

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
            x["file_data"] = ska_switcher.main(x["file_data"], singer)

    gh3_array = []
    for x in song_files:
        gh3_array.append([x["file_data"], x['file_name']])

    # Create the song PAK file
    song_pak = mid_qb.pakMaker(gh3_array)

    # raise Exception

    return song_name, song_pak


def convert_to_gha(pakmid, output=f'{os.getcwd()}', singer=ska_switcher.lipsync_dict["gha_singer"]):
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
                x["file_data"] = ska_switcher.main(x["file_data"], ska_switcher.lipsync_dict["gha_guitarist"])
            else:
                x["file_data"] = ska_switcher.main(x["file_data"], singer)
            # raise Exception

    # Convert dict to array of arrays
    gha_array = []
    for x in song_files:
        gha_array.append([x["file_data"], x['file_name']])

    # Create the song PAK file
    song_pak = mid_qb.pakMaker(gha_array)

    return song_name, song_pak

    # raise Exception


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def midqb2mid(pakmid, output=f'{os.getcwd()}'):
    if not "_song.pak" in pakmid:
        warning = input(
            "WARNING: File does not appear to be a validly named mid PAK file. Do you want to continue? (Y/N): ")
        if not warning.lower().startswith("y"):
            return -1

    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")]

    qb_sections, file_headers, file_headers_hex = pak2mid(pakmid, song_name)

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


def qb_to_text(file, output=f'{os.getcwd()}'):
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


if __name__ == "__main__":
    pass
