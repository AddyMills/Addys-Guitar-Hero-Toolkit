import os
import sys

sys.path.append(f"{os.getcwd()}\\pak_extract")
sys.path.append(f"{os.getcwd()}\\midqb_gen")
from pak_extract import PAKExtract, QB2Text, Text2QB
from midqb_gen import MidQbGen as mid_qb



menu_options = ["make_mid - Create a PAK file for a custom song",
                "extract_pak - Extract all files from a PAK file",
                "qb2text - Convert a single QB file to a text file",
                "text2qb - Convert a text file back into a QB file"
                ]

menu_mods = ["-o: Specify an output folder (default is the same folder as your input file)",
             "-hopo: Set the HO/PO threshold in ticks for make_mid (default is 170)"


]


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


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
    for x in pak_files:
        output_file = f"{output}\\{x['file_name']}"
        dir_name = os.path.dirname(output_file)
        try:
            os.makedirs(dir_name)
        except:
            pass
        with open(output_file, 'wb') as write_file:
            write_file.write(x["file_data"])
    # raise Exception
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
            output = sys.argv[sys.argv.index("-o")+1]
        if '-hopo' in sys.argv:
            hopo = int(sys.argv[sys.argv.index("-hopo")+1])
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
        else:
            print("No valid input found.\n")
            print_instructions()
