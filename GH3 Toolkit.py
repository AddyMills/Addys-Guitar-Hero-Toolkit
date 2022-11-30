import os
import sys
import mido

sys.path.append(f"{os.getcwd()}\\pak_extract")
sys.path.append(f"{os.getcwd()}\\midqb_gen")
from pak_extract import PAKExtract, QB2Text, Text2QB
from midqb_gen import MidQbGen as mid_qb

menu_options = ["make_mid - Create a PAK file for a custom song",
                "extract_pak - Extract all files from a PAK file",
                "qb2text - Convert a single QB file to a text file",
                "text2qb - Convert a text file back into a QB file",
                "midqb2mid - Convert a song PAK to a normal MIDI (Currently only camera and light events)"
                ]

menu_mods = ["-o: Specify an output folder (default is the same folder as your input file)",
             "-hopo: Set the HO/PO threshold in ticks for make_mid (default is 170)"
             ]


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_track_type(track_name):
    diffs = ["Easy", "Medium", "Hard", "Expert"]
    instrument = ["guitarcoop", "rhythmcoop", "rhythm"]
    if(any(x in track_name for x in diffs)):
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
        return {"track_type": track_name[track_name.find("_")+1:]}


def midqb2mid(pakmid, output=f'{os.getcwd()}'):
    if not "_song.pak" in pakmid:
        warning = input(
            "WARNING: File does not appear to be a validly named mid PAK file. Do you want to continue? (Y/N): ")
        if not warning.lower().startswith("y"):
            return -1

    song_name = pakmid[len(os.path.dirname(pakmid)) + 1:pakmid.find("_song")]

    with open(pakmid, 'rb') as pak:
        mid_bytes = pak.read()
    mid_files = PAKExtract.main(mid_bytes, "")
    for x in mid_files:
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
    midi_export.tracks[0].append(mido.MetaMessage("set_tempo", tempo = 500000))

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
                for z,y in enumerate(x.section_data):
                    if z % 3 == 0:
                        note_time = y
                    elif z % 3 == 1:
                        note_length = y
                    elif z % 3 == 2:
                        note_type = format(y, '#010b')[2:]
                        playableQB[track_type["instrument"]][track_type["difficulty"]].append([note_time,note_length,note_type])
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
                    new_track.append(blank_off.copy(note=prev_note, velocity = 0, time=int(round(mido.second2tick(y[0]/1000, 480, 500000) - prev_time, 0))))
                if prev_time != -1:
                    new_track.append(blank_on.copy(note=y[1], time=0))
                else:
                    new_track.append(blank_on.copy(note = y[1], time = int(round(mido.second2tick(y[0]/1000, 480, 500000), 0))))
                prev_note = y[1]
                prev_time = mido.second2tick(y[0]/1000, 480, 500000)
            tracks.append(new_track.copy())
        elif track_type["track_type"] == "lightshow":
            blank = mido.MetaMessage("text")
            new_track = mido.MidiTrack()
            # midi_export.add_track(track_type["track_type"])
            prev_time = -1
            for y in x.section_data:
                if prev_time != -1:
                    new_track.append(blank.copy(text=f"SetBlendTime {str(y.data_value[2].struct_data_struct[0].data_value)}", time=int(round(mido.second2tick(y.data_value[0].data_value/1000, 480, 500000) - prev_time, 0))))
                else:
                    new_track.append(blank.copy(text=f"SetBlendTime {str(y.data_value[2].struct_data_struct[0].data_value)}",time = int(round(mido.second2tick(y.data_value[0].data_value/1000, 480, 500000), 0))))
                prev_time = mido.second2tick(y.data_value[0].data_value/1000, 480, 500000)
            tracks.append(new_track.copy())
    midi_export.add_track(name = "GH3 VENUE")
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


def manual_input():
    main_menu = 0
    # QB 2 Text, Text 2 QB, Extract PAK, Extract All
    while True:
        print("Beginner Mode - Main Menu\n")
        print("Please type in the number from the following options (type -1 to exit):\n")

        # 5: extract_all - Extract a PAK file and converts all qb files into text files (beta)
        for y, x in enumerate(menu_options):
            print(f"{y + 1}: {x}")
        print("\n")
        try:
            main_menu = int(input("Selection: "))
        except:
            cls()
            input("Please only enter whole numbers. Press Enter to continue")
        print("")
        if main_menu == 1:
            mid_file = input(
                "Drag in your mid file (make sure the name of the file is the internal name of your custom): ").replace(
                "\"", "")
            output_mid(mid_file)
            input("Done! Press Enter to go back to the Main Menu. ")
        elif main_menu == 2:
            pak_file = input("Drag in your PAK file: ").replace("\"", "")
            output = f'{os.path.dirname(pak_file)}\\extract'
            extract_pak(pak_file, output)
            input("Done! Press Enter to go back to the Main Menu. ")
        elif main_menu == 3:
            qb_file = input("Drag in your QB file: ").replace("\"", "")
            output = f'{os.path.dirname(qb_file)}'
            qb_to_text(qb_file, output)
        elif main_menu == 4:
            text_file = input("Drag in your text file: ").replace("\"", "")
            output = f'{os.path.dirname(text_file)}'
            text_to_qb(text_file, output)
        elif main_menu == 5:
            song_pak_file = input("Drag in your song PAK file: ").replace("\"", "")
            output = f'{os.path.dirname(song_pak_file)}'
            text_to_qb(song_pak_file, output)
        elif main_menu == 1337:
            input("Ha! Got ourselves a leet hacker over here ")
        elif main_menu < 0:
            break

        main_menu = 0
        cls()


def print_instructions():
    print("\nTo run this program in advanced mode, call the program along with a command and input file.\n")
    print("The available commands are:")
    for y, x in enumerate(menu_options):
        print(f"{x}")
    print("\n")
    print("Options:")
    for y, x in enumerate(menu_mods):
        print(f"{x}")
    return


if __name__ == "__main__":
    print("Guitar Hero III Tools\n")
    if len(sys.argv) == 1:

        begin_mode = input("No argument detected, did you want to use beginner mode? (Y/N) ")
        if begin_mode[0].lower() == "y":
            manual_input()
        else:
            print_instructions()
    else:
        if "-o" in sys.argv:
            output = sys.argv[sys.argv.index("-o") + 1]
        if '-hopo' in sys.argv:
            hopo = int(sys.argv[sys.argv.index("-hopo") + 1])
        else:
            hopo = 170
        if sys.argv[1] == "make_mid":
            mid_file = sys.argv[2]
            if mid_file.lower().endswith(".mid"):
                if "output" not in locals():
                    output = ""
                # raise Exception
                output_mid(mid_file, output, hopo)
            else:
                print("Error: No mid file found.")
                # print_instructions()
        elif sys.argv[1] == "extract_pak":
            pak_file = sys.argv[2].replace("\"", "")
            if pak_file.lower().endswith(".pak.xen"):
                if "output" not in locals():
                    output = f'{os.path.dirname(pak_file)}\\extract'
                extract_pak(pak_file, output)
            else:
                print("Error: No PAK file found.")
        elif sys.argv[1] == "qb2text":
            qb_file = sys.argv[2].replace("\"", "")
            if qb_file.lower().endswith(".qb"):
                if "output" not in locals():
                    output = f'{os.path.dirname(qb_file)}'
                qb_to_text(qb_file, output)
            else:
                print("Error: No QB file found.")
        elif sys.argv[1] == "text2qb":
            text_file = sys.argv[2].replace("\"", "")
            if text_file.lower().endswith(".txt"):
                if "output" not in locals():
                    output = f'{os.path.dirname(text_file)}'
                text_to_qb(text_file, output)
            else:
                print("Error: No text file found.")
        elif sys.argv[1] == "midqb2mid":
            midqb_file = sys.argv[2].replace("\"", "")
            if "_song.pak" in midqb_file.lower():
                if "output" not in locals():
                    output = f'{os.path.dirname(midqb_file)}'
                midqb2mid(midqb_file, output)
            else:
                print("Error: No song PAK file found.")
        else:
            print("No valid input found.\n")
            print_instructions()
