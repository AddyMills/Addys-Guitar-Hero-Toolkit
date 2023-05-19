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

playableParts = ["", "rhythm", "guitarcoop", "rhythmcoop"]  # Blank one is for guitar in the headers
difficulties = ["Easy", "Medium", "Hard", "Expert"]
charts = ["song", "Star", "StarBattleMode"]
others = ["_FaceOffP1", "_FaceOffP2", "_BossBattleP1", "_BossBattleP2", "_timesig", "_fretbars", "_markers",
          "_scripts_notes", "_anim_notes", "_triggers_notes", "_cameras_notes", "_lightshow_notes", "_crowd_notes",
          "_drums_notes", "_performance_notes", "_scripts", "_anim", "_triggers", "_cameras", "_lightshow", "_crowd",
          "_drums", "_performance", "_facial", "_localized_strings"]

play_events = ["[mellow]", "[play]", "[intense]", "[play_solo]"]
idle_events = ["[idle]", "[idle_realtime]", "[idle_intense]"]
percussion_start = ["[clap_start]", "[cowbell_start]", "[tambourine_start]"]
percussion_end = ["[clap_end]", "[cowbell_end]", "[tambourine_end]"]

venue_states = ["[verse]", "[chorus]", "[solo]"]

valid_camera_notes_gh3 = [77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
                          100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117]

valid_camera_notes_gha = [10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35,
                          36, 38, 39, 40, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 56, 57, 59, 60, 61, 62, 64,
                          65, 67, 68, 69, 70, 72, 73, 74, 75, 77, 78, 79, 80, 82, 84, 85, 87, 88, 89]

valid_camera_notes_wt = [0, 1, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 18, 19, 20, 21, 23, 24, 25, 26, 28, 29, 30, 31,
                         33, 34, 35, 36, 38, 40, 41, 43, 45, 46, 48]

valid_lightshow_notes_gh3 = [39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 56, 57, 58, 60, 61, 62, 63, 64,
                             65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76]

valid_lightshow_notes_wt = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42, 43,
                            44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 57, 58, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 71,
                            72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 87, 88, 90, 91, 92, 93, 94, 95, 96, 97,
                            98, 99, 100, 101, 102, 103, 104, 105]

valid_crowd_gh3 = [72, 73, 74, 75, 76, 77, 78, 79, 80]

valid_crowd_wt = [82, 83, 84, 85, 86, 87, 88, 90, 91, 92, 93, 94, 95, 96]

valid_wt = {
    "LIGHTSHOW": valid_lightshow_notes_wt,
    "CAMERAS": valid_camera_notes_wt,
    "CROWD": valid_crowd_wt
}

gh5_camera_dict = {  # This dict is to grab camera cuts to add to a gh5-style perf file
    33: 8,
    34: 13,
    35: 23,
    36: 18
}

anims_guitar = []  # MIDI Note 127-118 is Lead left hand anims, 110-101 is Bass/Rhythm left hand notes
stances = ["Stance_A", "Stance_B", "Stance_C", "jump", "special", "Solo", "kick"]
drumKeyMapGH3 = {  # More FYI, but may use this dict in later code
    36: "Kick_R",  # Budokan and Hell venues only
    37: "Tom_3_L",
    38: "Tom_2_L",
    39: "Tom_1_L",
    40: "Snare_L",
    41: "HiHat_L_Open",
    42: "HiHat_L",  # Seems to be a duplicate. Probably won't use this one, but is defined just in case
    43: "Crash_2_L",  # Cymbal moves, but hand will not
    44: "Crash_1_L",
    45: "Ride_L",

    48: "Kick_L",
    49: "Tom_3_R",
    50: "Tom_2_R",
    51: "Tom_1_R",
    52: "Snare_R",
    53: "HiHat_R_Open",
    54: "HiHat_R",  # Seems to be a duplicate. Probably won't use this one, but is defined just in case
    55: "Crash_2_R",
    56: "Crash_1_R",
    57: "Ride_R",

    70: "Count"
}

drumKeyMapRB_gh3 = {
    51: 49,
    50: 37,
    49: 50,
    48: 38,
    47: 51,
    46: 39,
    45: 45,
    44: 45,
    43: 43,
    42: 55,
    41: 57,
    40: 56,
    39: 57,
    38: 57,
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
    24: 48,
    22: 70
}

wor_to_rb_drums = {
    # Right Hand
    51: 41,
    50: 40,
    49: 41,
    48: 38,
    47: 36,
    46: 36,
    45: 38,
    44: 36,
    43: 42,
    42: 42,
    41: 32,
    # 40: [31, 25],
    40: 31,
    39: 31,
    38: 27,
    37: 27,
    36: 29,
    35: 27,
    34: 47,
    33: 49,
    32: 51,
    31: 51,
    30: 24,
    # Left Hand
    21: 40,
    20: 41,
    19: 40,
    18: 44,
    17: 34,
    16: 34,
    15: 44,
    14: 34,
    13: 43,
    12: 43,
    11: 46,
    # 10: [30, 25],
    10: 30,
    9: 30,
    8: 26,
    7: 26,
    6: 28,
    5: 26,
    4: 46,
    3: 48,
    2: 50,
    1: 50,
    0: 23,
}

wor_camera_converts = {
    "gh3": {
        75: 94,
        74: 93,
        69: 114,
        68: 89,
        67: 79,
        66: 79,
        65: 101,
        64: 100,
        63: 99,
        62: 104,
        61: 87,
        60: 85,
        59: 97,
        58: 102,
        57: 101,
        48: 79,
        46: 113,
        45: 112,
        43: 79,
        38: 79,
        34: 104,
        33: 90,
        31: 79,
        30: 85,
        29: 94,
        28: 114,
        26: 105,
        25: 105,
        24: 87,
        23: 89,
        21: 105,
        20: 105,
        19: 110,
        18: 97,
        16: 88,
        15: 101,
        14: 103,
        13: 104,
        11: 105,
        10: 106,
        9: 87,
        8: 95,
    },
    "gha": {

    },
}

leftHandGtr_gh3 = {
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

leftHandBass_gh3 = {
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

leftHandMappingRhythm = {  # Guitar Hero Aerosmith only
    40: 93,
    41: 93,
    42: 92,
    43: 92,
    44: 91,
    45: 91,
    46: 90,
    47: 90,
    48: 89,
    49: 89,
    50: 88,
    51: 88,
    52: 87,
    53: 87,
    54: 86,
    55: 86,
    56: 85,
    57: 85,
    58: 84,
    59: 84
}

note_mapping_gh3 = {
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

note_mapping_wt_gtr = {
    71: 'Medium_purple',

    83: 'Hard_purple',

    95: 'Expert_purple',
}

note_mapping_wt_drum = {
    60: 'Easy_purple',
    65: 'Easy_green',

    72: 'Medium_purple',
    77: 'Medium_green',

    84: 'Hard_purple',
    89: 'Hard_green',

    95: 'Expert_2x',
    96: 'Expert_purple',
    101: 'Expert_green',
}

leftHandGtr_wt = {
    40: 127,
    41: 126,
    42: 125,
    43: 124,
    44: 123,
    45: 122,
    46: 121,
    47: 120,
    48: 119,
    49: 119,
    50: 118,
    51: 117,
    52: 116,
    53: 115,
    54: 114,
    55: 113,
    56: 112,
    57: 111,
    58: 110,
    59: 109,
}

leftHandBass_wt = {
    40: 103,
    41: 102,
    42: 101,
    43: 100,
    44: 99,
    45: 98,
    46: 97,
    47: 96,
    48: 95,
    49: 95,
    50: 94,
    51: 93,
    52: 92,
    53: 91,
    54: 90,
    55: 89,
    56: 88,
    57: 87,
    58: 86,
    59: 85,
}

anim_maps = {
    "Guitar": leftHandGtr_wt,
    "Bass": leftHandBass_wt
}

drumKeyMapRB_wt = {
    51: 74,
    50: 74,
    49: 75,
    48: 75,
    47: 76,
    46: 76,
    45: 82,
    44: 82,
    43: 80,
    42: 80,
    41: 82,
    40: 81,
    39: 82,
    38: 82,
    37: 81,
    36: 81,
    35: 81,
    34: 81,
    32: 75,
    31: 78,
    30: 78,
    29: 77,
    28: 77,
    27: 77,
    26: 77,
    24: 73,
    23: 73,
    22: 83,
    21: 65,
    20: 83,
}

practice_mode_wt = [21, 20]

inst_name_lookup = {
    "Guitar": "",
    "Bass": "_rhythm",
    "Drums": "_drum"
}

anim_lookup = {
    "left_hand": "anim_notes",
    "CAMERAS": "cameras_notes",
    "LIGHTSHOW": "lightshow_notes",
    "CROWD": "crowd_notes",
    "drum_anims": "drums_notes",

}

note_bit_vals = {
    "green": 0,
    "red": 1,
    "yellow": 2,
    "blue": 3,
    "orange": 4,
    "purple": 5,
    "on": 6
}

note_bit_2x = {
    "2x": 7
}

faceOffMapping = {
    105: "P1",
    106: "P2"
}

tap_note = 104
bm_star_note = 115
sp_note = 116
fo_star_note = 107

playable_range = range(36, 85)
phrase_marker = [105, 106]
freeform_marker = tap_note


forceMapping = {
    102: "Expert_off",
    101: "Expert_on",

    90: "Hard_off",
    89: "Hard_on",

    78: "Medium_off",
    77: "Medium_on",

    66: "Easy_off",
    65: "Easy_on"
}
