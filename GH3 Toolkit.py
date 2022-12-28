from toolkit_functions import *

menu_options = ["make_mid - Create a PAK file for a custom song",
                "extract_pak - Extract all files from a PAK file",
                "qb2text - Convert a single QB file to a text file",
                "text2qb - Convert a text file back into a QB file",
                "midqb2mid - Convert a song PAK to a normal MIDI (Currently only camera and light events)",
                "convert_to_gha - Convert a GH3 song to GH:A (adding rhythm anims, porting lights and cameras)\n\t\tLipsync does convert, but is glitchy!"
                ]

menu_mods = ["-o: Specify an output folder (default is the same folder as your input file)",
             "-hopo: Set the HO/PO threshold in ticks for make_mid (default is 170)"
             ]


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
        if '-singer' in sys.argv:
            singer = sys.argv[sys.argv.index("-singer") + 1]
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
        elif sys.argv[1] == "convert_to_gh3":
            midqb_file = sys.argv[2].replace("\"", "")
            if "_song.pak" in midqb_file.lower():
                if "output" not in locals():
                    output = f'{os.path.dirname(midqb_file)}'
                song_name, song_pak = convert_to_gh3(midqb_file, output)
                with open(output + f'\\{song_name}_song_GH3.pak.xen', 'wb') as f:
                    f.write(song_pak)
            else:
                print("Error: No song PAK file found.")
        elif sys.argv[1] == "convert_to_gha":
            midqb_file = sys.argv[2].replace("\"", "")
            if "_song.pak" in midqb_file.lower():
                if "output" not in locals():
                    output = f'{os.path.dirname(midqb_file)}'
                if "singer" not in locals():
                    singer = "gha_singer"
                song_name, song_pak = convert_to_gha(midqb_file, output, ska_switcher.lipsync_dict[singer])
                with open(output + f'\\{song_name}_song_GHA.pak.xen', 'wb') as f:
                    f.write(song_pak)
            else:
                print("Error: No song PAK file found.")
        else:
            print("No valid input found.\n")
            print_instructions()
