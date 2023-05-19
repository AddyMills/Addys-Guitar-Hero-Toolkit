import os.path
import sys
import traceback
import re

from toolkit_functions import *
from random import randint
from create_audio import audio_functions

debug = 0

menu_options = ["make_gh3_mid - Create a PAK file for a custom song",
                "extract_pak - Extract all files from a PAK file",
                "qb2text - Convert QB files to text files",
                "text2qb - Convert text files back into QB files",
                "convert_to_gha - Convert a GH3 song to GH:A (adding rhythm anims, porting lights and cameras)",
                "convert_to_gh3 - Convert a GH:A song to GH3 (removing rhythm anims/special mocap calls, porting lights and cameras)",
                "convert_to_5 - Convert a WT song to Guitar Hero 5 format",
                "create_mid_from_pak - Convert any Guitar Hero song pak file to a MIDI and pull anim loop data"
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
            print(f"Beginner Mode - Main Menu ({'GH3' if wt_mode == 0 else 'WT/5/BH/WoR'} Mode)\n")
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

                output = f'{os.path.dirname(mid_file)}'
                pak_file, filename = output_mid_gh3(mid_file)

                with open(f"{output}\\{filename}_song.pak.xen", 'wb') as f:
                    f.write(pak_file)
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
                song_name, song_pak = convert_to_gha(midqb_file, output, lipsync_dict[singer])
                if midqb_file.lower().endswith(".mid"):
                    pak_name = f'\\{song_name}_song.pak.xen'
                else:
                    pak_name = f'\\{song_name}_song_GHA.pak.xen'
                with open(output + pak_name, 'wb') as f:
                    f.write(song_pak)
            elif main_menu == 6:
                midqb_file = input("Drag in your song PAK file: ").replace("\"", "")
                output = f'{os.path.dirname(midqb_file)}'
                song_name, song_pak = convert_to_gh3(midqb_file, output)
                with open(output + f'\\{song_name}_song_GH3.pak.xen', 'wb') as f:
                    f.write(song_pak)
            elif main_menu == 7:
                midqb_file = input("Drag in your song PAK file: ").replace("\"", "")
                output = f'{os.path.dirname(midqb_file)}'
                new_name = randint(10000,1000000000)
                print(f"DLC number for this file will be {new_name}\n")
                new_name = f"dlc{new_name}"
                print("Converting World Tour song to Guitar Hero 5")
                try:
                    pak_data = convert_to_5(midqb_file, new_name)
                    pak_file = mid_qb.pakMaker([[x["file_data"], x["file_name"]] for x in pak_data], new_name)
                    with open(output + f'\\{new_name}_song.pak.xen', 'wb') as f:
                        f.write(pak_file)
                    input("\nComplete! Press any key to exit.")
                except Exception as E:
                    print("Conversion failed!")
                    print(E)
                    input("\nPress any key to exit.")
            elif main_menu == 8:
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
            elif main_menu == 1337:
                input("Ha! Got ourselves a leet hacker over here ")
            elif main_menu < 0:
                break
        except Exception as e:
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
        launch_gui()
        '''print("Guitar Hero III Tools\n")
        begin_mode = input("No argument detected, did you want to use beginner mode? (Y/N) ")
        if begin_mode[0].lower() == "y":
            manual_input()
        else:
            print_instructions()'''
    elif sys.argv[1].endswith(".ghproj"):
        launch_gui(ghproj = sys.argv[1])
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
            elif sys.argv[1] == "convert_to_5":
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
