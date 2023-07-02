"""
This script automates converting an offical song and merging it with its animations.
It's kind of a special use case right now, but this will be updated for an easier conversion later.
"""
import sys
sys.path.append("../")
sys.path.append("../create_audio")
sys.path.append("../midqb_gen")
sys.path.append("../pak_extract")

from create_audio.audio_functions import *
from toolkit_functions import convert_to_5, pak2mid, modify_strobe
from midqb_gen import CreatePAK
from pak_extract import QB2Text, Text2QB
import os
import time

console = "ps3"

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

gh_reanim = {
    255: "areyougonnagomyway",
    257: "BandOnTheRun",
    264: "Dammit",
    265: "DemolitionMan",
    266: "DoItAgain",
    268: "Everlong",
    276: "Heartbreaker",
    278: "HollywoodNights",
    283: "LazyEye",
    284: "LivingOnAPrayer",
    287: "LoveSpreads",
    288: "LViaLViaquez",
    293: "NeverTooLate",
    294: "NoSleepTillBrooklyn",
    296: "Obstacle1",
    297: "OneArmedScissor",
    298: "OneWayOrAnother",
    300: "OurTruth",
    301: "Overkill",
    309: "ReEdThroughLabor",
    311: "Santeria",
    315: "Shiver",
    317: "SoulDoubt",
    318: "Spiderwebs",
    319: "Stillborn",
    320: "Stranglehold",
    321: "SweetHomeAlabama",
    322: "TheJoker",
    323: "TheKill",
    324: "TheMiddle",
    326: "Today",
    328: "ToyBoy",
    330: "UpAroundTheBend",
    336: "YoureGonnaSayYeah",

    351: "AceOfSpades",
    354: "AmIEvil",
    357: "BeautifulMourning",
    358: "BlackRiver",
    359: "BloodAndThunder",
    361: "DemonCleaner",
    365: "Evil",
    376: "MommysLittleMonster",
    377: "MotherOfMercy",
    388: "TheBoysAreBack",
    394: "TuesdaysGone",
    395: "TurnThePage",

    406: "CaughtInAMosh",
    407: "CherryPie",
    409: "CultofPersonality",
    411: "FreeBird",
    412: "Freya",
    414: "HeartShapedBox",
    415: "HeyYou",
    416: "HitMeWithYourBestShot",
    417: "ILoveRockAndRoll",
    418: "IWannaRock",
    419: "KillerQueen",
    423: "MessageInABottle",
    424: "MissMurder",
    425: "MonkeyWrench",
    428: "NoOneKnows",
    429: "NothinButAGoodTime",
    430: "PlayWithMe",
    431: "PsychobillyFreakout",
    433: "RockAndRollAllNite",
    435: "ShoutAtTheDevil",
    442: "TheTrooper",
    443: "ThroughTheFire",
    447: "Woman",
    448: "YYZ",

    451: "AintTalkinBoutLove",
    452: "AndTheCradleWillRock",
    453: "AtomicPunk",
    454: "BeautifulGirls",
    455: "BestOfYou",
    456: "Cathedral",
    457: "ComeToLife",
    458: "DanceTheNightAway",
    459: "DopeNose",
    460: "DoubleVision",
    461: "EndOfHeartache",
    462: "Eruption",
    463: "EverybodyWantsSome",
    464: "FeelYourLoveTonight",
    465: "FirstDate",
    466: "HangEmHigh",
    467: "HearAboutItLater",
    468: "HotForTeacher",
    469: "IceCreamMan",
    470: "ImTheOne",
    471: "IWantItAll",
    472: "jamiescryin",
    473: "jump",
    474: "LittleGuitars",
    475: "LossOfControl",
    476: "MasterExploder",
    477: "MeanStreet",
    478: "Painkiller",
    479: "Pain",
    480: "panama",
    481: "PrettyFlyForAWhiteGuy",
    482: "PrettyWoman",
    483: "RockAndRollIsDead",
    484: "RomeoDelight",
    485: "RunningWithTheDevil",
    486: "SafeEuropeanHome",
    487: "SemiCharmedLife",
    488: "SickSickSick",
    489: "SomebodyGetMeADoctor",
    490: "SoThisIsLove",
    491: "SpaceTruckin",
    492: "SpanishFly",
    493: "StacysMom",
    494: "TheTakedown",
    495: "Unchained",
    496: "WhiteWedding",
    497: "YouReallyGotMe"

}

vh_anims = {
    "AintTalkinBoutLove": "AintTalkin_anims.pak.xen",
    "AndTheCradleWillRock": "Cradle_anims.pak.xen",
    "AtomicPunk": "Atomic_anims.pak.xen",
    "BeautifulGirls": "Beautiful_anims.pak.xen",
    "Cathedral": "Cathedral_anims.pak.xen",
    "DanceTheNightAway": "Dance_anims.pak.xen",
    "Eruption": "Eruption_anims.pak.xen",
    "EverybodyWantsSome": "Everybody_anims.pak.xen",
    "FeelYourLoveTonight": "FeelLove_anims.pak.xen",
    "HangEmHigh": "HangEm_anims.pak.xen",
    "HearAboutItLater": "HearAboutIt_anims.pak.xen",
    "HotForTeacher": "HotForTeacher_anims.pak.xen",
    "IceCreamMan": "Icecream_anims.pak.xen",
    "ImTheOne": "ImTheOne_anims.pak.xen",
    "jamiescryin": "Jamie_anims.pak.xen",
    "jump": "Jump_anims.pak.xen",
    "LittleGuitars": "Guitars_anims.pak.xen",
    "LossOfControl": "Control_anims.pak.xen",
    "MeanStreet": "Meanstreet_anims.pak.xen",
    "panama": "Panama_anims.pak.xen",
    "PrettyWoman": "Pretty_anims.pak.xen",
    "RomeoDelight": "Romeo_anims.pak.xen",
    "RunningWithTheDevil": "Devil_anims.pak.xen",
    "SomebodyGetMeADoctor": "SomebodyGetMeADoctor_anims.pak.xen",
    "SoThisIsLove": "ThisIsLove_anims.pak.xen",
    "SpanishFly": "SpanishFly_anims.pak.xen",
    "Unchained": "Unchained_anims.pak.xen",
    "YouReallyGotMe": "Gotme_anims.pak.xen"
}

def generate_ids(shortname):
    id_list = [int.to_bytes(int(QBKey(shortname),16), 4, "big")]

    for x in ids_pre:
        id_list.append(int.to_bytes(int(QBKey(f"{shortname}{x}"),16), 4, "big"))

    for x in ids_post:
        id_list.append(int.to_bytes(int(QBKey(f"{x}{shortname}"), 16), 4, "big"))

    for x in ids_song:
        id_list.append(int.to_bytes(int(QBKey(f"songs\\{shortname}{x}"), 16), 4, "big"))

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


    old_file_root = ""
    new_file_root = ""

    """if os.path.exists(f"{filesfolder}\\Audio"):
        gh_audio = {}
        for dict_key, value in gh_reanim.items():
            audio_check = f"{filesfolder}\\Audio\\{value}"
            if os.path.isfile(f"{audio_check}_1.fsb.ps3"):
                audio_exts = [1, 2, 3, "preview"]
                for x in audio_exts:
                    audio_file = f"{audio_check}_{x}.fsb.ps3"
                    no_ext = os.path.basename(audio_file[:-8]).lower()
                    key = generate_fsb_key(no_ext)
                    print(f"Processing {no_ext}")
                    with open(f"{audio_file}", 'rb') as f:
                        audio = f.read()
                    audio = decrypt_fsb4(audio, key)
                    if audio[:3] != b'FSB':
                        raise Exception("Error Decrypting. Please check your song name.")
                    print("Successfully Decrypted")
                    new_id = f"adlc{dict_key}_{x}"
                    no_ext = file_renamer(new_id.lower())
                    key = generate_fsb_key(no_ext)
                    print(f"Re-encrypting with id {no_ext}")
                    audio = encrypt_fsb4(audio, key)
                    print("Successfully Encrypted")
                    try:
                        os.makedirs(f"{filesfolder}\\Audio-DLC")
                    except:
                        pass
                    file_name = f"{filesfolder}\\Audio-DLC\\{new_id}.fsb.{console}"
                    if console == "ps3":
                        file_name = file_name.upper()
                    with open(file_name, 'wb') as f:
                        f.write(audio)"""
    for x in song_files:
        filepath = f"{x[1]}"
        folderpath = os.path.dirname(filepath)
        just_file = os.path.basename(filepath)
        savepath = f"{x[1]}"
        pak_data = ""
        pak_anim = ""
        override_mid = ""
        vh_pak = 0
        if "bdlc" in just_file.lower():
            dlc_num = just_file.split("_")[0]
            dlc_num = int(dlc_num[4:])
            dlc_name = f"dlc{dlc_num}"
            print(f"Processing dlc{dlc_num}")
            if "DLC" in folderpath:
                if os.path.isfile(f"{folderpath}\\Orig_DLC\\adlc{dlc_num}_s.pak.xen"):
                    song_name = f"{folderpath}\\Orig_DLC\\adlc{dlc_num}_s.pak.xen"
                else:
                    song_name = f"{folderpath}\\Orig_DLC\\adlc{dlc_num}_song.pak.xen"
            else:
                short_name = gh_reanim[dlc_num]
                song_name = f"{folderpath}\\{short_name}_song.pak.xen"
                if short_name in vh_anims:
                    vh_pak = f"{folderpath}\\VH_anims\\{vh_anims[short_name]}"
            qb_sections, file_headers, file_headers_hex, song_files_dlc = pak2mid(filepath, dlc_name)

            new_dlc = []
            for y in song_files_dlc:
                if any([".ska" in y["file_name"], ".perf" in y["file_name"]]):
                    continue
                elif ".mid.qb" in y["file_name"]:
                    mid_qb = QB2Text.convert_qb_file(QB2Text.qb_bytes(y["file_data"]), song_name, file_headers)
                    for z in mid_qb:
                        if "performance" in z.section_id:
                            z.make_empty(f"{dlc_name}_performance")
                        elif "cameras_notes" in z.section_id:
                            z.make_empty(f"{dlc_name}_cameras_notes")
                        elif "lightshow_notes" in z.section_id:
                            strobe_counter = 0
                            for enum, light in enumerate(z.section_data):
                                if enum % 2 == 0:
                                    continue
                                else:
                                    orig_note = light
                                    z.section_data[enum] = modify_strobe(light)
                                    if z.section_data[enum] != orig_note:
                                        strobe_counter += 1
                            if strobe_counter > 0:
                                print(f"Changed {strobe_counter} strobe lights")
                    result = StringIO()
                    orig_stdout = sys.stdout
                    sys.stdout = result
                    QB2Text.print_qb_text_file(mid_qb)
                    sys.stdout = orig_stdout
                    qb_text = result.getvalue()
                    mid_qb_bytes = Text2QB.main(qb_text , console="PC", endian="big", game="GH5")
                    y["file_data"] = mid_qb_bytes
                    new_dlc.append(y)
                    #print()
                else:
                    new_dlc.append(y)
            override_folder = f"{filesfolder}\\{dlc_name}"
            if "GHWT" in filesfolder:
                decomp_ska = True
            else:
                decomp_ska = False
            convert_flags = ["gh5"]
            if "GHVH" in filesfolder:
                convert_flags.append("super_gimp")
            if vh_pak:
                song_files_convert = convert_to_5(song_name, dlc_name, *convert_flags, decomp_ska=decomp_ska, anim_pak=vh_pak)
            else:
                song_files_convert = convert_to_5(song_name, dlc_name, *convert_flags, decomp_ska = decomp_ska)
            if os.path.isdir(override_folder):
                print("Overwriting SKA files with files from override folder")
                for y in song_files_convert:
                    if ".perf" in y["file_name"]:
                        new_dlc.append(y)
                for y in os.listdir(override_folder):
                    with open(f"{override_folder}\\{y}", 'rb') as f:
                        override_file = f.read()
                    new_dlc.append({"file_name": y[:-4], "file_data": override_file})
            else:
                for y in song_files_convert:
                    if any([".ska" in y["file_name"], ".perf" in y["file_name"]]):
                        new_dlc.append(y)
                    else:
                        continue
            try:
                os.mkdir(f"{folderpath}\\Re-animated")
            except:
                pass
            pak_file = CreatePAK.pakMaker([[y["file_data"], y["file_name"]] for y in new_dlc], dlc_name)
            if "GHVH" in folderpath or "PS3" in folderpath:
                with open(f"{folderpath}\\Re-animated\\bdlc{dlc_num}_song.pak.ps3".upper(), "wb") as f:
                    f.write(pak_file)
            else:
                with open(f"{folderpath}\\Re-animated\\bdlc{dlc_num}_song.pak.xen", "wb") as f:
                    f.write(pak_file)
            print()

    t1 = time.process_time()
    print(t1 - t0)

