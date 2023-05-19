from midqb_functions import *
from CreatePAK import pakMaker
from mido import MidiFile, MidiTrack
from io import StringIO
import os
import sys


sys.path.append("..\\pak_extract")

from pak_extract.pak_functions import createHeaderDict
from pak_extract.QB2Text import convert_qb_file, qb_bytes, print_qb_text_file
from pak_extract.Text2QB import main as t2q_main


tbp = 480



def make_mid(midfile, hopo, filename = "", *args, **kwargs):
    mid = MidiFile(midfile)
    midQS = ""
    consoleType = 1
    if filename == "":
        filename = os.path.splitext(os.path.basename(midfile))[0]

    headerDict = createHeaderDict(filename)
    # print(headerDict)
    if "ghwt" in args:
        qb_dict = parse_wt_qb(mid, hopo, *args)
        if "replace_perf" in args:
            with open(args[args.index("replace_perf") + 1], "rb") as f:
                qb_sections = convert_qb_file(qb_bytes(f.read()), filename, headerDict,
                                              "PC")
                for x in qb_sections:
                    if "_performance" in x.section_id and not "notes" in x.section_id:
                        qb_dict["performance"] = x
                        break
        QBSections, midQS = create_wt_qb_sections(qb_dict, filename)
        midQB = create_wt_qb(QBSections, filename)
        if "performance" in qb_dict:
            midQB = convert_qb_file(qb_bytes(midQB), filename, headerDict, "PC")
            for x in midQB:
                if "_performance" in x.section_id and not "notes" in x.section_id:
                    x.array_node_type = qb_dict["performance"].array_node_type
                    x.section_data = qb_dict["performance"].section_data
                    break
            result = StringIO()
            orig_stdout = sys.stdout
            sys.stdout = result
            print_qb_text_file(midQB)
            sys.stdout = orig_stdout
            qb_text = result.getvalue()
            midQB = t2q_main(qb_text, game = "GHWT")
            # print()
    else:
        midParsed = parseGH3QB(mid, hopo)
        midQB = makeMidQB(midParsed, filename, headerDict, consoleType)
    """with open(f"{filename}_song.mid.qb", 'wb') as f:
        f.write(midQB)"""
    if "qb" in args:
        pakFile = {"qb": midQB, "qs": midQS}
    else:
        to_pak = [[midQB, f"songs\\{filename}.mid.qb"]]
        if midQS:
            to_pak.append([midQS, f"songs\\{filename}.mid.qs"])
        pakFile = pakMaker(to_pak)

    return pakFile, filename

if __name__ == "__main__":
    consoleType = 1  # 0 for Wii, 1 for PC, 2 for 360, 3 for XBX, 4 for PS2, 5 for WPC
    midfile = sys.argv[1]
    if len(sys.argv) == 3:
        hopo = int(sys.argv[2])
    else:
        hopo = 170

    pakFile, filename = make_mid(midfile, hopo, "", *sys.argv)

    if "qb" in sys.argv:
        with open(f".\\Pak Input\\songs\\{filename}.mid.qb.xen", 'wb') as f:
            f.write(pakFile["qb"])
        if pakFile["qs"]:
            with open(f".\\Pak Input\\songs\\{filename}.mid.qs.xen", 'wb') as f:
                f.write(pakFile["qs"])
    else:
        with open(f"{filename}_song.pak.xen", 'wb') as f:
            f.write(pakFile)

