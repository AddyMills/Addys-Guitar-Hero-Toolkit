import os.path
import sys
import traceback
import re

from toolkit_functions import *
from random import randint
from create_audio import audio_functions

debug = 0

# Menu Options
menu_options_var = ["compile_wt_song", "convert_ska_file", "convert_to_5", "convert_to_gh3", "convert_to_gha", "convert_to_ghwor",
                    "create_mid_from_pak", "extract_pak", "make_gh3_mid", "qb2text", "text2qb"]

menu_options = [
                "compile_wt_song - Compile a Guitar Hero: World Tour song pak file from audio and a MIDI file",
                "convert_ska_file - Convert a SKA file from one game to another (for conversions)",
                # "convert_5_to_wt - Convert a song from Guitar Hero 5 or Warriors of Rock to the World Tour format",
                "convert_to_5 - Convert a WT song to Guitar Hero 5 format",
                "convert_to_gh3 - Convert a GH:A song to GH3 (removing rhythm anims/special mocap calls, porting lights and cameras)",
                "convert_to_gha - Convert a GH3 song to GH:A (adding rhythm anims, porting lights and cameras)",
                "convert_to_ghwor - Convert a WT song to Guitar Hero Warriors of Rock format",
                "create_mid_from_pak - Convert any Guitar Hero song pak file to a MIDI and pull anim loop data",
                "extract_pak - Extract all files from a PAK file",
                "make_gh3_mid - Create a PAK file for a custom song",
                "qb2text - Convert QB files to text files",
                "text2qb - Convert text files back into QB files",
                ]

menu_mods = [
    "-o: Specify an output folder (default is the same folder as your input file)",
    "-i: Set an input folder compile_pak to use",
    "-hopo: Set the HO/PO threshold in ticks for make_gh3_mid (default is 170)",
    "-singer: Set the singer type for GH3->GHA conversion"
             ]


def manual_input():
    main_menu = 0
    wt_mode = 0
    # QB 2 Text, Text 2 QB, Extract PAK, Extract All
    while True:
        try:
            print(f"Beginner Mode - Main Menu\n")
            print("Please type in the number from the following options (type -1 to exit):\n")

            # 5: extract_all - Extract a PAK file and converts all qb files into text files (beta)
            for y, x in enumerate(menu_options):
                print(f"{y + 1}: {x}")
            print("\n")
            try:
                main_menu = int(input("Selection: "))
                if main_menu == -1:
                    break
                main_menu = menu_options_var[main_menu - 1]
            except:
                cls()
                input("Please only enter whole numbers. Press Enter to continue")
            print("")
            if main_menu == "make_gh3_mid":
                mid_file = input(
                    "Drag in your mid file (make sure the name of the file is the internal name of your custom): ").replace(
                    "\"", "")

                output = f'{os.path.dirname(mid_file)}'
                pak_file, filename = output_mid_gh3(mid_file)

                with open(f"{output}\\{filename}_song.pak.xen", 'wb') as f:
                    f.write(pak_file)
                input("Done! Press Enter to go back to the Main Menu. ")
            elif main_menu == "extract_pak":
                pak_file = input("Drag in your PAK file: ").replace("\"", "")
                output = f'{os.path.dirname(pak_file)}\\extract'
                extract_pak(pak_file, output)
                input("Done! Press Enter to go back to the Main Menu. ")
            elif main_menu == "qb2text":
                qb_file = input("Drag in your QB file: ").replace("\"", "")
                output = f'{os.path.dirname(qb_file)}'
                qb_to_text(qb_file, output)
            elif main_menu == "text2qb":
                text_file = input("Drag in your text file: ").replace("\"", "")
                output = f'{os.path.dirname(text_file)}'
                text_to_qb(text_file, output)
            elif main_menu == "convert_to_gha":
                singer_dict = {
                    "1": "gha_singer",
                    "2": "steve",
                    "3": "dmc",
                    "4": "gha_guitarist"
                }
                midqb_file = input("Drag in your song PAK or MIDI file: ").replace("\"", "")
                output = f'{os.path.dirname(midqb_file)}'
                if midqb_file.lower().endswith(".mid"):
                    singer = singer_dict["1"]
                else:
                    print("Choose your singer: ")
                    print("1.) Default\n2.) Steven Tyler\n3.) Run DMC\n4.) Joe Perry")
                    singer = singer_dict[input("Type in the number corresponding to your singer: ")]
                song_name, song_pak = convert_to_gha(midqb_file, output, singer)
                if midqb_file.lower().endswith(".mid"):
                    pak_name = f'\\{song_name}_song.pak.xen'
                else:
                    pak_name = f'\\{song_name}_song_GHA.pak.xen'
                with open(output + pak_name, 'wb') as f:
                    f.write(song_pak)
                input("Convert complete! Press Enter to continue. ")
            elif main_menu == "convert_to_gh3":
                midqb_file = input("Drag in your song PAK file: ").replace("\"", "")
                output = f'{os.path.dirname(midqb_file)}'
                song_name, song_pak = convert_to_gh3(midqb_file, output)
                with open(output + f'\\{song_name}_song_GH3.pak.xen', 'wb') as f:
                    f.write(song_pak)
                input("Convert complete! Press Enter to continue. ")
            elif main_menu == "convert_to_5" or main_menu == "convert_to_ghwor":
                compile_args = []
                if main_menu == "convert_to_ghwor":
                    compiler_args = ["compiler"]
                midqb_file = input("Drag in your song PAK file: ").replace("\"", "")
                output = f'{os.path.dirname(midqb_file)}'
                while True:
                    try:
                        dlc_num = input("Enter a DLC number higher than 10,000 (if converting to WoR, this should match the DLC number Onyx assigned)\nLeave blank for a random number: ")
                        new_name = int(dlc_num)
                        if not dlc_num:
                            raise Exception
                        else:
                            if new_name < 10000:
                                raise Exception
                            else:
                                break
                    except:
                        print("No valid dlc number found, using random number")
                        new_name = randint(10000,1999999999)
                        print(f"DLC number for this file will be {new_name}\n")
                new_name = f"dlc{new_name}"
                print("Converting World Tour song to Guitar Hero 5")
                try:
                    pak_data = convert_to_5(midqb_file, new_name, *compiler_args)
                    pak_file = mid_qb.pakMaker([[x["file_data"], x["file_name"]] for x in pak_data], new_name)
                    with open(output + f'\\b{new_name}_song.pak.xen', 'wb') as f:
                        f.write(pak_file)
                    input("\nComplete! Press any key to exit.")
                except Exception as E:
                    print("Conversion failed!")
                    print(E)
                    input("\nPress any key to exit.")
            elif main_menu == "create_mid_from_pak":
                midqb_file = input("Drag in your song PAK file: ").replace("\"", "")
                output = f'{os.path.dirname(midqb_file)}'
                midname = os.path.basename(midqb_file)[:os.path.basename(midqb_file).find(".")]
                print(midname)
                mid_file, anim_string = create_mid_from_qb(midqb_file)
                mid_file.save(f"{output}\\{midname}.mid")
                if anim_string:
                    anim_string = f"qb_file = songs/{midname}_scripts.qb".lower() + "\n" + anim_string
                    with open(f"{output}\\{midname}_scripts.txt", "w") as f:
                        f.write(anim_string)
                input("\nComplete! Press any key to go to the main menu.")
            elif main_menu == "compile_wt_song":
                launch_gui()
            elif main_menu == "convert_ska_file":
                while True:
                    ska_files = input("Drag in your SKA file or a folder containing multiple SKA files: ")
                    if not os.path.exists(ska_files):
                        print("File path does not exist")
                    else:
                        break
                if os.path.isdir(ska_files):
                    ska_folder = ska_files
                else:
                    ska_folder = os.path.dirname(ska_files)
                output = f'{ska_folder}\\converted_ska_files'
                target_dict = {
                    "1": "GH3",
                    "2": "GHA",
                    "3": "GHWT",
                    "4": "GH5"
                }
                print("Choose a target skeleton")
                for y, x in enumerate(target_dict):
                    print(f"\t{x}) {target_dict[x]}")
                while True:
                    ska_game = target_dict[input("Type in the number corresponding to your target game: ")]
                    if ska_game in target_dict.values():
                        if ska_game == "GH3" or ska_game == "GHA":
                            while True:
                                print("1 - Singer\n2 - Guitarist"+ ("\n3 - Steven Tyler" if ska_game == "GHA" else ""))
                                ska_type = input("Choose a skeleton: ")
                                if ska_type == "1":
                                    ska_target = f"{ska_game}_singer".lower()
                                    break
                                elif ska_type == "2":
                                    ska_target = f"gh3_guitarist"
                                    break
                                elif ska_type == "3" and ska_game == "GHA":
                                    ska_target = "steve"
                                    break
                                else:
                                    print("Invalid target")
                        else:
                            ska_target = "wt_rocker"
                        break
                    else:
                        print("Invalid target")
                if os.path.isdir(ska_files):
                    ska_files = [x for x in os.listdir(ska_files) if any([x.lower().endswith(".ska"), x.lower().endswith(".ska.xen"), x.lower().endswith(".ska.ps3")])]
                else:
                    ska_files = [ska_files]
                quat_check = 0
                for x in ska_files:
                    with open(f"{ska_folder}\\{x}", "rb") as f:
                        ska = ska_bytes(f.read())
                    print(f"Processing {os.path.basename(x)}")
                    try:
                        if ska_game == "GHWT" or ska_game == "GH5":
                            if ska.version == 0x48 and not quat_check:
                                gha_check = input(f"{'Are' if len(ska_files) > 1 else 'Is'} your SKA {'files' if len(ska_files) > 1 else 'file'} from GHA? (y/n): ")[0].lower()
                                if gha_check == "y":
                                    quats_mult = 1
                                    quat_check = 1
                                else:
                                    quats_mult = 2
                                    quat_check = 2
                            elif quat_check:
                                quats_mult = quat_check
                            else:
                                quats_mult = 1
                            ska_file = make_modern_ska(ska, game = ska_game, ska_switch = ska_target, quats_mult = quats_mult)
                        else:
                            quats_mult = 0.5 if ska_game == "GH3" else 1
                            ska_file = make_gh3_ska(ska, ska_switch = ska_target, quats_mult = quats_mult)
                        if ska_file == None:
                            continue
                        if not os.path.isdir(output):
                            os.mkdir(output)
                        with open(f'{output}\\{os.path.basename(x)}', "wb") as f:
                            f.write(ska_file)
                    except Exception as E:
                        print("Conversion failed!")
                        # raise E
                        print(E)
                        input("\nPress any key to exit.")

                input("Complete! Press any key to exit.")
            elif main_menu == "convert_5_to_wt":
                midqb_file = input("Drag in your song PAK file: ").replace("\"", "")
                output = f'{os.path.dirname(midqb_file)}'
                midname = os.path.basename(midqb_file)[:os.path.basename(midqb_file).find(".")]
                if re.search(r'^[a-c]dlc', midname, flags=re.IGNORECASE):
                    midname = midname[1:]
                print("""\nYou can add a performance override file to be added to the song.\nFor example, you can add tapping animation events or for WoR songs, add PlayIdle events.""".replace("\t",""))
                perf_override = input("Drag in your perf override file (or leave this blank) and press Enter to continue: ").replace("\"", "")
                music_override = input("Drag in the folder containing your audio files from the PS3 version.\nLeave blank to skip: ").replace("\"", "")
                if music_override:
                    try:
                        audio_functions.strip_mp3(music_override)
                    except Exception as E:
                        raise E
                        print("Could not convert audio.")
                print(midname)
                wt_pak = convert_5_to_wt(midqb_file, perf_override)
                with open(f"{output}\\a{midname}.pak.xen".lower(), "wb") as f:
                    f.write(wt_pak)

            elif main_menu == 1337:
                input("Ha! Got ourselves a leet hacker over here ")
            elif main_menu < 0:
                break
        except Exception as e:
            raise e
            cls()
            print("Action failed due to the following:")
            print(e)
            print()
            input("Press Enter to go back to the main menu")

        main_menu = 0
        print()


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

def launch_gui(ghproj = ""):
    root_folder = os.path.realpath(os.path.dirname(__file__))
    sys.path.append(f"{root_folder}\\gui")
    from gui import toolkit_gui
    toolkit_gui.open_gui(sys.argv, proj_file = ghproj)


if __name__ == "__main__":
    if len(sys.argv) == 1:

        print("Addy's Guitar Hero Toolkit\n")
        manual_input()
    elif sys.argv[1].endswith(".ghproj"):
        launch_gui(ghproj = sys.argv[1])
    elif sys.argv[1] == "-debug":
        manual_input()
    else:
        try:
            root_folder = os.path.realpath(os.path.dirname(__file__))
            input_file = os.path.abspath(sys.argv[2])
            if "-pak_name" in sys.argv:
                pak_name = sys.argv[sys.argv.index("-pak_name") + 1]
            if "-i" in sys.argv:
                in_file = sys.argv[sys.argv.index("-i") + 1]
                if not os.path.isdir(in_file):
                    raise Exception("Input folder is not a proper folder")
            if "-o" in sys.argv:
                output = sys.argv[sys.argv.index("-o") + 1]
            if "-anim_pak" in sys.argv:
                pak_name = sys.argv[sys.argv.index("-anim_pak") + 1]
            if '-hopo' in sys.argv:
                hopo = int(sys.argv[sys.argv.index("-hopo") + 1])
            else:
                hopo = 170
            if '-singer' in sys.argv:
                singer = sys.argv[sys.argv.index("-singer") + 1]
            if "-debug" in sys.argv:
                debug = 1
            if sys.argv[1] == "make_gh3_mid":
                mid_file = sys.argv[2]
                if mid_file.lower().endswith(".mid"):
                    if "output" not in locals():
                        output = ""
                    # raise Exception
                    pak_file, filename = output_mid_gh3(mid_file, hopo)
                    if output == "":
                        output = os.path.dirname(mid_file)
                    with open(f"{output}\\{filename}_song.pak.xen", 'wb') as f:
                        f.write(pak_file)
                else:
                    print("Error: No mid file found.")
                    # print_instructions()
            elif sys.argv[1] == "compile_wt_song":
                if len(sys.argv) > 2:
                    launch_gui(sys.argv[2])
                else:
                    launch_gui()
            elif sys.argv[1] == "extract_pak":
                pak_file = input_file.replace("\"", "")
                if pak_file.lower().endswith(".pak.xen"):
                    if "output" not in locals():
                        output = f'{os.path.dirname(pak_file)}\\extract'
                    extract_pak(pak_file, output)
                else:
                    print("Error: No PAK file found.")
            elif sys.argv[1] == "qb2text":
                qb_file = input_file.replace("\"", "")
                if qb_file.lower().endswith(".qb"):
                    if "output" not in locals():
                        output = f'{os.path.dirname(qb_file)}'
                    qb_to_text(qb_file, output)
                else:
                    print("Error: No QB file found.")
            elif sys.argv[1] == "text2qb":
                text_file = input_file.replace("\"", "")
                if text_file.lower().endswith(".txt"):
                    if "output" not in locals():
                        output = f'{os.path.dirname(text_file)}'
                    text_to_qb(text_file, output)
                else:
                    print("Error: No text file found.")
            elif sys.argv[1] == "convert_to_gh3":
                midqb_file = input_file.replace("\"", "")
                if "_song.pak" in midqb_file.lower():
                    if "output" not in locals():
                        output = f'{os.path.dirname(midqb_file)}'
                    if "singer" not in locals():
                        singer = "gh3_singer"
                    song_name, song_pak = convert_to_gh3(midqb_file, output, lipsync_dict[singer])
                    with open(output + f'\\{song_name}_song_GH3.pak.xen', 'wb') as f:
                        f.write(song_pak)
                else:
                    print("Error: No song PAK file found.")
            elif sys.argv[1] == "convert_to_gha":
                midqb_file = input_file.replace("\"", "")
                if "_song.pak" in midqb_file.lower() or ".mid" in midqb_file.lower():
                    if "output" not in locals():
                        output = f'{os.path.dirname(midqb_file)}'
                    if "singer" not in locals():
                        singer = "gha_singer"
                    song_name, song_pak = convert_to_gha(midqb_file, output, lipsync_dict[singer])
                    with open(output + f'\\{song_name}_song_GHA.pak.xen', 'wb') as f:
                        f.write(song_pak)
                else:
                    print("Error: No song PAK file found.")
            elif sys.argv[1] == "convert_to_5" or sys.argv[1] == "convert_to_ghwor":
                compile_args = []
                midqb_file = input_file.replace("\"", "")
                if "_song.pak" in midqb_file.lower():
                    if "output" not in locals():
                        output = f'{os.path.dirname(midqb_file)}'
                    if "pak_name" not in locals():
                        pak_name = f"dlc{randint(10000,1000000000)}"
                    pak_data = convert_to_5(midqb_file, pak_name)
                    pak_file = mid_qb.pakMaker([[x["file_data"], x["file_name"]] for x in pak_data], pak_name)
                    with open(output + f'\\b{pak_name}_song.pak.xen', 'wb') as f:
                        f.write(pak_file)

            elif sys.argv[1] == "compile_pak":
                if "in_file" not in locals():
                    in_file = f'{root_folder}\\midqb_gen\\Pak Input'
                if "output" not in locals():
                    output = f'{in_file}\\..\\PAK compile'
                if "pak_name" not in locals():
                    pak_name = 0
                if "-pab" in sys.argv:
                    pab = True
                else:
                    pab = False
                pak_data = []
                try:
                    for root, dirs, file in os.walk(in_file, topdown = False):
                        for name in file:
                            to_add = os.path.join(root,name)
                            """if pak_name == 0:
                                if ".mid.qb.xen" in to_add:
                                    pak_name = os.path.basename(to_add[len(in_file)+1:-11])"""
                            with open(to_add, 'rb') as f:
                                pak_data.append({"file_name": to_add[len(in_file)+1:], "file_data": f.read()})
                except Exception as e:
                    print("Error compiling PAK file. Could not find the input folder.")
                    raise e
                if pab:
                    pak_file, pab_file = mid_qb.pakMaker([[x["file_data"], x["file_name"]] for x in pak_data], pak_name, pab)
                else:
                    pak_file = mid_qb.pakMaker([[x["file_data"], x["file_name"]] for x in pak_data], pak_name)
                    pab_file = 0
                try:
                    os.makedirs(output)
                except:
                    pass
                with open(f"{output}\\{pak_name}.pak.xen", 'wb') as f:
                    f.write(pak_file)
                if pab:
                    with open(f"{output}\\{pak_name}.pab.xen", 'wb') as f:
                        f.write(pab_file)

                        #print(os.path.join(root,name)[len(in_file)+1:])
                # print()
            elif sys.argv[1] == "create_mid_from_pak":
                if "output" not in locals():
                    output = f'{os.path.dirname(input_file)}'
                midname = os.path.basename(input_file)[:os.path.basename(input_file).find(".")]
                print(midname)
                mid_file, anim_string = create_mid_from_qb(input_file)
                mid_file.save(f"{output}\\{midname}.mid")
                if anim_string:
                    anim_string = f"qb_file = songs/{midname}_scripts.qb".lower() + "\n" + anim_string
                    with open(f"{output}\\{midname}_scripts.txt", "w") as f:
                        f.write(anim_string)
            elif sys.argv[1] == "convert_5_to_wt":
                if "output" not in locals():
                    output = f'{os.path.dirname(input_file)}'
                midname = os.path.basename(input_file)[:os.path.basename(input_file).find(".")]
                if re.search(r'^[a-c]dlc', midname, flags=re.IGNORECASE):
                    midname = midname[1:]
                compile_args = []
                if len(sys.argv) > 3:
                    compile_args.extend(sys.argv[3:])
                wt_pak = convert_5_to_wt(input_file, *compile_args)
                with open(f"{output}\\a{midname}.pak.xen".lower(), "wb") as f:
                    f.write(wt_pak)
            elif sys.argv[1] == "make_wt_mid":
                qb_file = mid_qb.make_wt_qb(sys.argv[2])
            elif sys.argv[1] == "extract_fsb":
                if "output" not in locals():
                    output = f'{os.path.dirname(input_file)}'
                fsbpath = sys.argv[2]
                dat = b''
                with open(fsbpath, "rb") as f:
                    fsb = f.read()
                if ".fsb" in fsbpath:
                    datpath = f"{fsbpath[:fsbpath.find('.fsb')]}.dat.xen"
                    if os.path.isfile(datpath):
                        with open(datpath, 'rb') as f:
                            dat = f.read()
                filename = os.path.basename(fsbpath)
                if re.search(r'^[a-c]dlc', filename, flags=re.IGNORECASE):
                    filename = filename[1:]
                fsb_ext = audio_functions.extract_fsb(fsb, filename, datfile = dat)
                for key, value in fsb_ext.items():
                    output_file = os.path.join(output, key)
                    with open(output_file, 'wb') as f:
                        f.write(value["data"])
                    # print(output_file)
            else:
                print("No valid input found.\n")
                print_instructions()
        except Exception as e:
            print("Action failed due to the following:")
            if debug:
                raise e
            traceback.print_exc()
            print_instructions()
            input("Press Enter to go back to the main menu")
