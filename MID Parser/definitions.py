qbNodeHeaders = {
                                #   Wii         PC          XBox      XBox XBX      PS2        PC WPC
    "Unknown":                  [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000],
    "SectionInteger":           [0x00200100, 0x00200100, 0x00200100, 0x00010400, 0x00010400, 0x00010400],
    "SectionFloat":             [0x00200200, 0x00200200, 0x00200200, 0x00020400, 0x00020400, 0x00020400],
    "SectionString":            [0x00200300, 0x00200300, 0x00200300, 0x00030400, 0x00030400, 0x00030400],
    "SectionStringW":           [0x00200400, 0x00200400, 0x00200400, 0x00040400, 0x00040400, 0x00040400],
    "SectionFloatsX2":          [0x00200500, 0x00200500, 0x00200500, 0x00050400, 0x00050400, 0x00050400],
    "SectionFloatsX3":          [0x00200600, 0x00200600, 0x00200600, 0x00060400, 0x00060400, 0x00060400],
    "SectionScript":            [0x00200700, 0x00200700, 0x00200700, 0x00070400, 0x00070400, 0x00070400],
    "SectionStruct":            [0x00200A00, 0x00200A00, 0x00200A00, 0x000A0400, 0x000A0400, 0x000A0400],
    "SectionArray":             [0x00200C00, 0x00200C00, 0x00200C00, 0x000C0400, 0x000C0400, 0x000C0400],
    "SectionQbKey":             [0x00200D00, 0x00200D00, 0x00200D00, 0x000D0400, 0x000D0400, 0x000D0400],
    "SectionQbKeyString":       [0x00201A00, 0x00201A00, 0x00201A00, 0x00041A00, 0x00041A00, 0x00041A00],
    "SectionStringPointer":     [0x00201B00, 0x00201B00, 0x00201B00, 0x001A0400, 0x001A0400, 0x001A0400],
    "SectionQbKeyStringQs":     [0x00201C00, 0x00201C00, 0x00201C00, 0x001C0400, 0x001C0400, 0x001C0400],
    "ArrayInteger":             [0x00010100, 0x00010100, 0x00010100, 0x00010100, 0x00010100, 0x00010100],
    "ArrayFloat":               [0x00010200, 0x00010200, 0x00010200, 0x00020100, 0x00020100, 0x00020100],
    "ArrayString":              [0x00010300, 0x00010300, 0x00010300, 0x00030100, 0x00030100, 0x00030100],
    "ArrayStringW":             [0x00010400, 0x00010400, 0x00010400, 0x00040100, 0x00040100, 0x00040100],
    "ArrayFloatsX2":            [0x00010500, 0x00010500, 0x00010500, 0x00050100, 0x00050100, 0x00050100],
    "ArrayFloatsX3":            [0x00010600, 0x00010600, 0x00010600, 0x00060100, 0x00060100, 0x00060100],
    "ArrayStruct":              [0x00010A00, 0x00010A00, 0x00010A00, 0x000A0100, 0x000A0100, 0x000A0100],
    "ArrayArray":               [0x00010C00, 0x00010C00, 0x00010C00, 0x000C0100, 0x000C0100, 0x000C0100],
    "ArrayQbKey":               [0x00010D00, 0x00010D00, 0x00010D00, 0x000D0100, 0x000D0100, 0x000D0100],
    "ArrayQbKeyString":         [0x00011A00, 0x00011A00, 0x00011A00, 0x001A0100, 0x001A0100, 0x001A0100],
    "ArrayStringPointer":       [0x00011B00, 0x00011B00, 0x00011B00, 0x001B0100, 0x001B0100, 0x001B0100],
    "ArrayQbKeyStringQs":       [0x00011C00, 0x00011C00, 0x00011C00, 0x001C0100, 0x001C0100, 0x001C0100],
    "StructItemInteger":        [0x00810000, 0x00810000, 0x00810000, 0x00000300, 0x00000300, 0x00000300],
    "StructItemFloat":          [0x00820000, 0x00820000, 0x00820000, 0x00000500, 0x00000500, 0x00000500],
    "StructItemString":         [0x00830000, 0x00830000, 0x00830000, 0x00000700, 0x00000700, 0x00000700],
    "StructItemStringW":        [0x00840000, 0x00840000, 0x00840000, 0x00000900, 0x00000900, 0x00000900],
    "StructItemFloatsX2":       [0x00850000, 0x00850000, 0x00850000, 0x00000B00, 0x00000B00, 0x00000B00],
    "StructItemFloatsX3":       [0x00860000, 0x00860000, 0x00860000, 0x00000D00, 0x00000D00, 0x00000D00],
    "StructItemStruct":         [0x008A0000, 0x008A0000, 0x008A0000, 0x00001500, 0x00001500, 0x00001500],
    "StructItemArray":          [0x008C0000, 0x008C0000, 0x008C0000, 0x00001900, 0x00001900, 0x00001900],
    "StructItemQbKey":          [0x008D0000, 0x008D0000, 0x008D0000, 0x00001B00, 0x00001B00, 0x00001B00],
    "StructItemQbKeyString":    [0x009A0000, 0x009A0000, 0x009A0000, 0x00003500, 0x00003500, 0x00003500],
    "StructItemStringPointer":  [0x009B0000, 0x009B0000, 0x009B0000, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF],
    "StructItemQbKeyStringQs":  [0x009C0000, 0x009C0000, 0x009C0000, 0xFFFFFFFF, 0x001A0400, 0xFFFFFFFF],
    "Floats":                   [0x00010000, 0x00010000, 0x00010000, 0x00000100, 0x00000100, 0x00000100],
    "StructHeader":             [0x00000100, 0x00000100, 0x00000100, 0x00010000, 0x00010000, 0x00010000]

}

playableParts = ["", "rhythm", "guitarcoop", "rhythmcoop"]  # Blank one is for guitar in the headers
difficulties = ["Easy", "Medium", "Hard", "Expert"]
charts = ["song", "Star", "StarBattleMode"]
others = ["_FaceOffP1", "_FaceOffP2", "_BossBattleP1", "_BossBattleP2", "_timesig", "_fretbars", "_markers",
          "_scripts_notes", "_anim_notes", "_triggers_notes", "_cameras_notes", "_lightshow_notes", "_crowd_notes",
          "_drums_notes", "_performance_notes", "_scripts", "_anim", "_triggers", "_cameras", "_lightshow", "_crowd",
          "_drums", "_performance"]

anims_guitar = []  # MIDI Note 127-118 is Lead left hand anims, 110-101 is Bass/Rhythm left hand notes
stances = ["Stance_A", "Stance_B", "Stance_C", "jump", "special", "Solo", "kick"]
drumKeyMapGH3 = {  # More FYI, but may use this dict in later code
    36: "Kick_R",  # Budokan and Hell venues only
    37: "Tom_3_L",
    38: "Tom_2_L",
    39: "Tom_1_L",
    40: "Snare_L",
    41: "HiHat_L",
    42: "HiHat_L",  # Seems to be a duplicate. Probably won't use this one, but is defined just in case
    43: "Crash_2_L",  # Cymbal moves, but hand will not
    44: "Crash_1_L",
    45: "Ride_L",

    48: "Kick_L",
    49: "Tom_3_R",
    50: "Tom_2_R",
    51: "Tom_1_R",
    52: "Snare_R",
    53: "HiHat_R",
    54: "HiHat_R",  # Seems to be a duplicate. Probably won't use this one, but is defined just in case
    55: "Crash_2_R",
    56: "Crash_1_R",
    57: "Ride_R",

    70: "Count"
}

drumKeyMapRB = {
    51: 49,
    50: 37,
    49: 50,
    48: 38,
    47: 51,
    46: 39,
    45: 43,
    44: 43,
    43: 45,
    42: 57,
    41: 55,
    40: 56,
    39: 55,
    38: 55,
    37: 56,
    36: 56,
    35: 44,
    34: 44,
    32: 50,
    31: 53,
    30: 41,
    29: 52,
    28: 40,
    27: 52,
    26: 40,
    24: 48
}

leftHandMappingGtr = {
    40: 127,
    41: 127,
    42: 126,
    43: 126,
    44: 125,
    45: 125,
    46: 124,
    47: 124,
    48: 123,
    49: 123,
    50: 122,
    51: 122,
    52: 121,
    53: 121,
    54: 120,
    55: 120,
    56: 119,
    57: 119,
    58: 118,
    59: 118
}

leftHandMappingBass = {
    40: 110,
    41: 110,
    42: 109,
    43: 109,
    44: 108,
    45: 108,
    46: 107,
    47: 107,
    48: 106,
    49: 106,
    50: 105,
    51: 105,
    52: 104,
    53: 104,
    54: 103,
    55: 103,
    56: 102,
    57: 102,
    58: 101,
    59: 101

}

noteMapping = {
    60: 'Easy_green',
    61: 'Easy_red',
    62: 'Easy_yellow',
    63: 'Easy_blue',
    64: 'Easy_orange',

    72: 'Medium_green',
    73: 'Medium_red',
    74: 'Medium_yellow',
    75: 'Medium_blue',
    76: 'Medium_orange',

    84: 'Hard_green',
    85: 'Hard_red',
    86: 'Hard_yellow',
    87: 'Hard_blue',
    88: 'Hard_orange',

    96: 'Expert_green',
    97: 'Expert_red',
    98: 'Expert_yellow',
    99: 'Expert_blue',
    100: 'Expert_orange',
}

faceOffMapping = {
    105: "P1",
    106: "P2"
}
