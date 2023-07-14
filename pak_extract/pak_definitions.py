qbNodeHeaders = {
    #   Wii         PC          XBox      XBox XBX      PS2        PC WPC
    "Unknown": [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000],
    "SectionInteger": [0x00200100, 0x00200100, 0x00200100, 0x00010400, 0x00010400, 0x00010400],
    "SectionFloat": [0x00200200, 0x00200200, 0x00200200, 0x00020400, 0x00020400, 0x00020400],
    "SectionString": [0x00200300, 0x00200300, 0x00200300, 0x00030400, 0x00030400, 0x00030400],
    "SectionStringW": [0x00200400, 0x00200400, 0x00200400, 0x00040400, 0x00040400, 0x00040400],
    "SectionFloatsX2": [0x00200500, 0x00200500, 0x00200500, 0x00050400, 0x00050400, 0x00050400],
    "SectionFloatsX3": [0x00200600, 0x00200600, 0x00200600, 0x00060400, 0x00060400, 0x00060400],
    "SectionScript": [0x00200700, 0x00200700, 0x00200700, 0x00070400, 0x00070400, 0x00070400],
    "SectionStruct": [0x00200A00, 0x00200A00, 0x00200A00, 0x000A0400, 0x000A0400, 0x000A0400],
    "SectionArray": [0x00200C00, 0x00200C00, 0x00200C00, 0x000C0400, 0x000C0400, 0x000C0400],
    "SectionQbKey": [0x00200D00, 0x00200D00, 0x00200D00, 0x000D0400, 0x000D0400, 0x000D0400],
    "SectionQbKeyString": [0x00201A00, 0x00201A00, 0x00201A00, 0x00041A00, 0x00041A00, 0x00041A00],
    "SectionStringPointer": [0x00201B00, 0x00201B00, 0x00201B00, 0x001A0400, 0x001A0400, 0x001A0400],
    "SectionQbKeyStringQs": [0x00201C00, 0x00201C00, 0x00201C00, 0x001C0400, 0x001C0400, 0x001C0400],
    "ArrayInteger": [0x00010100, 0x00010100, 0x00010100, 0x00010100, 0x00010100, 0x00010100],
    "ArrayFloat": [0x00010200, 0x00010200, 0x00010200, 0x00020100, 0x00020100, 0x00020100],
    "ArrayString": [0x00010300, 0x00010300, 0x00010300, 0x00030100, 0x00030100, 0x00030100],
    "ArrayStringW": [0x00010400, 0x00010400, 0x00010400, 0x00040100, 0x00040100, 0x00040100],
    "ArrayFloatsX2": [0x00010500, 0x00010500, 0x00010500, 0x00050100, 0x00050100, 0x00050100],
    "ArrayFloatsX3": [0x00010600, 0x00010600, 0x00010600, 0x00060100, 0x00060100, 0x00060100],
    "ArrayStruct": [0x00010A00, 0x00010A00, 0x00010A00, 0x000A0100, 0x000A0100, 0x000A0100],
    "ArrayArray": [0x00010C00, 0x00010C00, 0x00010C00, 0x000C0100, 0x000C0100, 0x000C0100],
    "ArrayQbKey": [0x00010D00, 0x00010D00, 0x00010D00, 0x000D0100, 0x000D0100, 0x000D0100],
    "ArrayQbKeyString": [0x00011A00, 0x00011A00, 0x00011A00, 0x001A0100, 0x001A0100, 0x001A0100],
    "ArrayStringPointer": [0x00011B00, 0x00011B00, 0x00011B00, 0x001B0100, 0x001B0100, 0x001B0100],
    "ArrayQbKeyStringQs": [0x00011C00, 0x00011C00, 0x00011C00, 0x001C0100, 0x001C0100, 0x001C0100],
    "StructItemInteger": [0x00810000, 0x00810000, 0x00810000, 0x00000300, 0x00000300, 0x00000300],
    "StructItemFloat": [0x00820000, 0x00820000, 0x00820000, 0x00000500, 0x00000500, 0x00000500],
    "StructItemString": [0x00830000, 0x00830000, 0x00830000, 0x00000700, 0x00000700, 0x00000700],
    "StructItemStringW": [0x00840000, 0x00840000, 0x00840000, 0x00000900, 0x00000900, 0x00000900],
    "StructItemFloatsX2": [0x00850000, 0x00850000, 0x00850000, 0x00000B00, 0x00000B00, 0x00000B00],
    "StructItemFloatsX3": [0x00860000, 0x00860000, 0x00860000, 0x00000D00, 0x00000D00, 0x00000D00],
    "StructItemStruct": [0x008A0000, 0x008A0000, 0x008A0000, 0x00001500, 0x00001500, 0x00001500],
    "StructItemArray": [0x008C0000, 0x008C0000, 0x008C0000, 0x00001900, 0x00001900, 0x00001900],
    "StructItemQbKey": [0x008D0000, 0x008D0000, 0x008D0000, 0x00001B00, 0x00001B00, 0x00001B00],
    "StructItemQbKeyString": [0x009A0000, 0x009A0000, 0x009A0000, 0x00003500, 0x00003500, 0x00003500],
    "StructItemStringPointer": [0x009B0000, 0x009B0000, 0x009B0000, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF],
    "StructItemQbKeyStringQs": [0x009C0000, 0x009C0000, 0x009C0000, 0xFFFFFFFF, 0x001A0400, 0xFFFFFFFF],
    "Floats": [0x00010000, 0x00010000, 0x00010000, 0x00000100, 0x00000100, 0x00000100],
    "StructHeader": [0x00000100, 0x00000100, 0x00000100, 0x00010000, 0x00010000, 0x00010000]
}

qb_node_list = ["Unknown", "SectionInteger", "SectionFloat", "SectionString", "SectionStringW", "SectionFloatsX2",
                "SectionFloatsX3", "SectionScript", "SectionStruct", "SectionArray", "SectionQbKey",
                "SectionQbKeyString", "SectionStringPointer", "SectionQbKeyStringQs", "ArrayInteger", "ArrayFloat",
                "ArrayString", "ArrayStringW", "ArrayFloatsX2", "ArrayFloatsX3", "ArrayStruct", "ArrayArray",
                "ArrayQbKey", "ArrayQbKeyString", "ArrayStringPointer", "ArrayQbKeyStringQs", "StructItemInteger",
                "StructItemFloat", "StructItemString", "StructItemStringW", "StructItemFloatsX2", "StructItemFloatsX3",
                "StructItemStruct", "StructItemArray", "StructItemQbKey", "StructItemQbKeyString",
                "StructItemStringPointer", "StructItemQbKeyStringQs", "Floats", "StructHeader"]

simple_array_types = ["ArrayFloat", "ArrayQbKey", "ArrayQbKeyString", "ArrayQbKeyStringQs"]
simple_struct_items = ["StructItemQbKeyString"]
hard_struct_items = ["StructItemStruct"]

qb_type_lookup = {
    "Wii": [0x00000000, 0x00200100, 0x00200200, 0x00200300, 0x00200400, 0x00200500, 0x00200600, 0x00200700, 0x00200A00,
            0x00200C00, 0x00200D00, 0x00201A00, 0x00201B00, 0x00201C00, 0x00010100, 0x00010200, 0x00010300, 0x00010400,
            0x00010500, 0x00010600, 0x00010A00, 0x00010C00, 0x00010D00, 0x00011A00, 0x00011B00, 0x00011C00, 0x00810000,
            0x00820000, 0x00830000, 0x00840000, 0x00850000, 0x00860000, 0x008A0000, 0x008C0000, 0x008D0000, 0x009A0000,
            0x009B0000, 0x009C0000, 0x00010000, 0x00000100],
    "PC": [0x00000000, 0x00200100, 0x00200200, 0x00200300, 0x00200400, 0x00200500, 0x00200600, 0x00200700, 0x00200A00,
           0x00200C00, 0x00200D00, 0x00201A00, 0x00201B00, 0x00201C00, 0x00010100, 0x00010200, 0x00010300, 0x00010400,
           0x00010500, 0x00010600, 0x00010A00, 0x00010C00, 0x00010D00, 0x00011A00, 0x00011B00, 0x00011C00, 0x00810000,
           0x00820000, 0x00830000, 0x00840000, 0x00850000, 0x00860000, 0x008A0000, 0x008C0000, 0x008D0000, 0x009A0000,
           0x009B0000, 0x009C0000, 0x00010000, 0x00000100],
    "XBox": [0x00000000, 0x00200100, 0x00200200, 0x00200300, 0x00200400, 0x00200500, 0x00200600, 0x00200700, 0x00200A00,
             0x00200C00, 0x00200D00, 0x00201A00, 0x00201B00, 0x00201C00, 0x00010100, 0x00010200, 0x00010300, 0x00010400,
             0x00010500, 0x00010600, 0x00010A00, 0x00010C00, 0x00010D00, 0x00011A00, 0x00011B00, 0x00011C00, 0x00810000,
             0x00820000, 0x00830000, 0x00840000, 0x00850000, 0x00860000, 0x008A0000, 0x008C0000, 0x008D0000, 0x009A0000,
             0x009B0000, 0x009C0000, 0x00010000, 0x00000100],
    "XBox XBX": [0x00000000, 0x00010400, 0x00020400, 0x00030400, 0x00040400, 0x00050400, 0x00060400, 0x00070400,
                 0x000A0400, 0x000C0400, 0x000D0400, 0x00041A00, 0x001A0400, 0x001C0400, 0x00010100, 0x00020100,
                 0x00030100, 0x00040100, 0x00050100, 0x00060100, 0x000A0100, 0x000C0100, 0x000D0100, 0x001A0100,
                 0x001B0100, 0x001C0100, 0x00000300, 0x00000500, 0x00000700, 0x00000900, 0x00000B00, 0x00000D00,
                 0x00001500, 0x00001900, 0x00001B00, 0x00003500, 0xFFFFFFFF, 0xFFFFFFFF, 0x00000100, 0x00010000],
    "PS2": [0x00000000, 0x00010400, 0x00020400, 0x00030400, 0x00040400, 0x00050400, 0x00060400, 0x00070400, 0x000A0400,
            0x000C0400, 0x000D0400, 0x00041A00, 0x001A0400, 0x001C0400, 0x00010100, 0x00020100, 0x00030100, 0x00040100,
            0x00050100, 0x00060100, 0x000A0100, 0x000C0100, 0x000D0100, 0x001A0100, 0x001B0100, 0x001C0100, 0x00000300,
            0x00000500, 0x00000700, 0x00000900, 0x00000B00, 0x00000D00, 0x00001500, 0x00001900, 0x00001B00, 0x00003500,
            0xFFFFFFFF, 0x001A0400, 0x00000100, 0x00010000],
    "PC WPC": [0x00000000, 0x00010400, 0x00020400, 0x00030400, 0x00040400, 0x00050400, 0x00060400, 0x00070400,
               0x000A0400, 0x000C0400, 0x000D0400, 0x00041A00, 0x001A0400, 0x001C0400, 0x00010100, 0x00020100,
               0x00030100, 0x00040100, 0x00050100, 0x00060100, 0x000A0100, 0x000C0100, 0x000D0100, 0x001A0100,
               0x001B0100, 0x001C0100, 0x00000300, 0x00000500, 0x00000700, 0x00000900, 0x00000B00, 0x00000D00,
               0x00001500, 0x00001900, 0x00001B00, 0x00003500, 0xFFFFFFFF, 0xFFFFFFFF, 0x00000100, 0x00010000]}

console_lookup = {
    "Wii": 0,
    "PC": 1,
    "XBox": 2,
    "XBox XBX": 3,
    "PS2": 4,
    "PC WPC": 5
}  # 0 for Wii, 1 for PC, 2 for 360, 3 for XBX, 4 for PS2, 5 for WPC

console_endian = {
    "Wii": "big",
    "PC": "big",
    "XBox": "big",
    "XBox XBX": "little",
    "PS2": "little",
    "PC WPC": "little"
}

playableParts = ["", "rhythm", "guitarcoop", "rhythmcoop", "drum", "aux"]  # Blank one is for guitar in the headers
difficulties = ["Easy", "Medium", "Hard", "Expert"]
charts = ["song", "Star", "StarBattleMode", "Tapping", "WhammyController", "SoloMarkers"]
face_off = ["FaceOffP1", "FaceOffP2", "FaceOffStar"]
others = ["_BossBattleP1", "_BossBattleP2", "_timesig", "_fretbars", "_markers",
          "_scripts_notes", "_anim_notes", "_triggers_notes", "_cameras_notes", "_lightshow_notes", "_crowd_notes",
          "_drums_notes", "_performance_notes", "_scripts", "_anim", "_triggers", "_cameras", "_lightshow", "_crowd",
          "_drums", "_performance"]

markers_wt = ["_guitar_markers", "_rhythm_markers", "_drum_markers"]

others_wt = ["_facial", "_localized_strings", "_scriptevents", "_song_startup", "_vox_sp", "_ghost_notes", "_double_kick"]

drum_wt = ["DrumFill", "DrumUnmute"]

vocals_wt = ["_freeform", "_phrases", "_note_range", "_markers"]

songs_folder = [f".mid.qb", f"_song_scripts.qb",
                f".mid.qs", f".note", f".perf",
                f".perf.xml.qb"]

qs_extensions = [".qs.de", ".qs.en", ".qs.es", ".qs.fr", ".qs.it"]

anims_pre = ["car_female_anim_struct_", "car_male_anim_struct_", "car_female_alt_anim_struct_", "car_male_alt_anim_struct_"]