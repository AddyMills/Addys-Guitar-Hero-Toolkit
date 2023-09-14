from mido import tick2second as t2s, MidiTrack, MidiFile
from midqb_classes import *
import numpy as np
from midqb_definitions import *
from Sections import sections
import re
import sys
import struct
from copy import deepcopy
import binascii
from math import ceil

sys.path.append("..\\pak_extract")
from pak_extract.Text2QB import basic_data, struct_data, assign_data, assign_types, create_qb
from pak_extract.pak_functions import make_script_struct, round_time, round_cam_len, new_stance_gh3

sys.path.append("..\\")
import CRC


def create_wt_qb_sections(qb_dict, filename, *args):
    qb_sections = {}
    playable_qb = qb_dict["playable_qb"]
    star_power = qb_dict["star_power"]
    bm_star_power = qb_dict["bm_star_power"]
    tap = qb_dict["tap"]
    fo_star_note = qb_dict["fo_star_power"]
    face_off = qb_dict["face_off"]
    whammy_cont = ""
    boss_battle = {}
    parsing = [playable_qb, star_power, bm_star_power, tap, whammy_cont, fo_star_note, face_off]
    if "wtde" in args:
        parsing.append(qb_dict["solo_markers"])

    qb_sections[f"{filename}_timesig"] = basic_data(f"{filename}_timesig",
                                                    [[x.time, x.numerator, x.denominator] for x in qb_dict["timesigs"]])
    qb_sections[f"{filename}_fretbars"] = basic_data(f"{filename}_fretbars", qb_dict["fretbars"])

    no_diff = ["tap", "fo_star_note", "face_off"]
    # Create playable notes array
    for track in ["Guitar", "Bass", "Drums", "_aux", "_guitarcoop", "_rhythmcoop"]:
        if track in inst_name_lookup:
            instrument = inst_name_lookup[track]
        else:
            instrument = track

        for section in parsing:
            for diff in ["Easy", "Medium", "Hard", "Expert"]:
                if section == playable_qb:
                    chart_name = f"{filename}_song{instrument}_{diff}"
                elif section == star_power:
                    chart_name = f"{filename}{instrument}_{diff}_Star"
                elif section == bm_star_power:
                    chart_name = f"{filename}{instrument}_{diff}_StarBattleMode"
                elif section == tap:
                    chart_name = f"{filename}{instrument}_{diff}_Tapping"
                    if track in tap:
                        qb_sections[chart_name] = basic_data(chart_name, tap[track])
                    else:
                        qb_sections[chart_name] = basic_data(chart_name, [])
                    continue
                elif section == whammy_cont:
                    chart_name = f"{filename}{instrument}_{diff}_WhammyController"
                    qb_sections[chart_name] = basic_data(chart_name, [])
                    continue
                elif section == fo_star_note:
                    chart_name = f"{filename}{instrument}_FaceOffStar"
                    qb_sections[chart_name] = basic_data(chart_name, [])
                    break
                elif section == qb_dict["solo_markers"]:
                    if "wtde" in args:
                        chart_name = f"{filename}{instrument}_{diff}_SoloMarkers"
                        if track in qb_dict["solo_markers"]:
                            qb_sections[chart_name] = basic_data(chart_name, qb_dict["solo_markers"][track])
                        else:
                            qb_sections[chart_name] = basic_data(chart_name, [])
                        continue
                    else:
                        break
                else:
                    for player in ["P1", "P2"]:
                        chart_name = f"{filename}{instrument}_FaceOff{player}"
                        try:
                            if track in inst_name_lookup:
                                qb_sections[chart_name] = basic_data(chart_name, face_off[track][player])
                            else:
                                qb_sections[chart_name] = basic_data(chart_name, [])
                        except:
                            qb_sections[chart_name] = basic_data(chart_name, [])
                    break
                if track in inst_name_lookup:
                    try:
                        if section == playable_qb:
                            qb_sections[chart_name] = basic_data(chart_name, section[track][diff].notes)
                        else:
                            qb_sections[chart_name] = basic_data(chart_name, section[track][diff])
                    except:
                        qb_sections[chart_name] = basic_data(chart_name, [])
                else:
                    qb_sections[chart_name] = basic_data(chart_name, [])

    qb_sections[f"{filename}_BassBattleP1"] = basic_data(chart_name, [])
    qb_sections[f"{filename}_BassBattleP2"] = basic_data(chart_name, [])

    for marker in ["guitar", "rhythm", "drum"]:
        chart_name = f"{filename}_{marker}_markers"
        if marker == "guitar" and qb_dict["gtr_markers"]:
            gtr_markers = []
            for gtr in qb_dict["gtr_markers"]:
                gtr_markers.append(struct_data())
                temp_struct = gtr_markers[-1]
                temp_struct.add_data("time", str(gtr.time))
                temp_struct.add_data("marker", f"w\"{gtr.marker}\"")
            qb_sections[chart_name] = basic_data(chart_name, gtr_markers)
        else:
            qb_sections[chart_name] = basic_data(chart_name, [])

    for drum_track in ["DrumFill", "DrumUnmute"]:
        for diff in ["Easy", "Medium", "Hard", "Expert"]:
            chart_name = f"{filename}_{diff}_{drum_track}"
            qb_sections[chart_name] = basic_data(chart_name, qb_dict["drum_fills"] if drum_track == "DrumFill" else [])

    for anim, value in qb_dict["anim"].items():
        if anim in anim_lookup:
            chart_name = f"{filename}_{anim_lookup[anim]}"
        else:
            chart_name = f"{filename}_{anim}"
        if value:
            if type(value) == dict:
                anim_list = []
                for timing, notes in sorted(value.items()):
                    for anim_stuff in notes:
                        bin_len = bin(anim_stuff.length)[2:].zfill(16)
                        bin_mid_note = bin(anim_stuff.note)[2:].zfill(8)
                        bin_velocity = bin(anim_stuff.velocity)[2:].zfill(8)
                        note_val = int(bin_velocity + bin_mid_note + bin_len, 2)
                        anim_list.append(timing)
                        anim_list.append(note_val)
                qb_sections[chart_name] = basic_data(chart_name, anim_list.copy())
            elif type(value) == list:
                anim_list = []
                for anim_stuff in value:
                    anim_list.append(make_script_struct(anim_stuff))
                qb_sections[chart_name] = basic_data(chart_name, anim_list)
        else:
            qb_sections[chart_name] = basic_data(chart_name, [])
    # "performance",
    for temp in ["song_vocals", "vocals_freeform", "vocals_phrases", "vocals_note_range", "lyrics", "vocals_markers"]:
        chart_name = f"{filename}_{temp}"
        try:
            '''if temp == "performance":
                qb_sections[chart_name] = basic_data(chart_name, [])'''
            if type(playable_qb["Vocals"][temp][0]) == markerNode:
                temp_markers = []
                temp_array = playable_qb["Vocals"][temp]
                for node in temp_array:
                    temp_markers.append(struct_data())
                    temp_struct = temp_markers[-1]
                    temp_struct.add_data("time", str(node.time))
                    temp_struct.add_data("marker" if temp != "lyrics" else "text", f"{node.marker}")
                qb_sections[chart_name] = basic_data(chart_name, temp_markers.copy())
            else:
                qb_sections[chart_name] = basic_data(chart_name, playable_qb["Vocals"][temp].copy())
        except:
            qb_sections[chart_name] = basic_data(chart_name, [])
    if "wor" in args and qb_dict["vox_sp"]:
        chart_name = f"{filename}_vox_sp"
        qb_sections[chart_name] = basic_data(chart_name, qb_dict["vox_sp"])
    if "wor" in args and qb_dict["ghost_notes"]:
        chart_name = f"{filename}_ghost_notes"
        qb_sections[chart_name] = basic_data(chart_name, qb_dict["ghost_notes"])
    if "wtde" in args and qb_dict["xplus"]:
        chart_name = f"{filename}_song_drums_expertplus"
        qb_sections[chart_name] = basic_data(chart_name, qb_dict["xplus"].notes)

    if qb_dict["has_2x_kick"]:
        chart_name = f"{filename}_double_kick"
        qb_sections[chart_name] = basic_data(chart_name, [])

    qs_file = ""
    if playable_qb["Vocals"]["qs_file"]:
        for lyric, qs in playable_qb["Vocals"]["qs_file"].items():
            qs_file += f"{qs} \"{lyric}\"\n"
        qs_file += "\n\n"
        qs_file = b'\xFF\xFE' + qs_file.encode("utf-16-le")

    return qb_sections, qs_file


def create_game_qb(qb_sections, filename, game="GHWT"):
    if type(qb_sections) == dict:
        qb_list = [value for key, value in qb_sections.items()]
    else:
        qb_list = qb_sections
    assign_types(qb_list, game=game)
    qb_file = create_qb(qb_list, "Section", f"songs/{filename}.mid.qb", game=game)

    return qb_file


def midiProcessing(mid):
    tempoMap, ticks = tempMap(mid)
    endEvent = 0
    for track in mid.tracks:
        if track.name == "EVENTS":
            for msg in track:
                endEvent += msg.time
                if msg.type == 'text':
                    if msg.text == '[end]':
                        break
    for x, y in enumerate(tempoMap):
        y.seconds = t2s(y.time, mid.ticks_per_beat, y.avgTempo)
    return tempoMap  # tickList


def rollingAverage(x, y, z, a):  # x = prevTime, y = curTime, z = avgTempo, a = curTempo
    newTempo = ((x / y) * z) + (a * (y - x) / y)
    return newTempo


def song_array(songMap):
    songTime = []
    songSeconds = []
    songTempo = []
    songAvgTempo = []
    for x, y in enumerate(songMap):
        songTime.append(y.time)
        songSeconds.append(y.seconds)
        songTempo.append(y.tempo)
        songAvgTempo.append(y.avgTempo)
    return songTime, songSeconds, songTempo, songAvgTempo


def tempMap(mid):
    x = []  # Tempo changes
    z = []  # Ticks of tempo changes
    y = 0  # Event counter
    totalTime = 0  # Cumulative total time
    avgTempo = 0
    for msg in mid.tracks[0]:
        totalTime = totalTime + msg.time
        if msg.type == "set_tempo":  # Just in case there are other events in the tempo map
            if y == 0:
                x.append(tempoMapItem(totalTime, msg.tempo, msg.tempo))
                z.append(totalTime)
                y = y + 1
            elif y == 1:
                avgTempo = x[y - 1].tempo
                x.append(tempoMapItem(totalTime, msg.tempo, avgTempo))
                z.append(totalTime)
                y = y + 1
            else:
                avgTempo = rollingAverage(x[y - 1].time, totalTime, avgTempo, x[y - 1].tempo)
                x.append(tempoMapItem(totalTime, msg.tempo, avgTempo))
                z.append(totalTime)
                y = y + 1

    return x, z


def timeInSecs(currChange, mid, time):
    return int(round(
        t2s(currChange.time, mid.ticks_per_beat, currChange.avgTempo) + t2s(time - currChange.time, mid.ticks_per_beat,
                                                                            currChange.tempo), 3) * 1000)


def convertVenue(mid, track, changes, ticksArray):
    time = 0
    for x in track:
        time += x.time
        currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
        timeSec = timeInSecs(currChange, mid, time)
    venue = 1
    return venue


def note_range_count(n_range, time_array, arr_diff):
    for sp in n_range:
        sp_notes = mod_notes(time_array, sp)[0]
        sp_len = sp[1] - sp[0]
        arr_diff.append([sp[0], sp_len, sp_notes.size])
    return arr_diff


def mod_notes(time_array, compare):
    return np.where((time_array >= compare[0]) & (time_array < compare[1]))


def set_gems(gem):
    notes_bin = 0
    for temp_colour in gem["colours"]:
        notes_bin += 1 << temp_colour
    return notes_bin


def make_bin_notes(gem):
    notes_bin = set_gems(gem)
    return bin(notes_bin)[2:].zfill(7)


def parse_fretbars(timeSigs, end_event_ticks, changes, ticksArray, mid):
    fretbars = []
    time = 0
    currTS = 0
    numer = timeSigs[currTS].numerator
    denom = timeSigs[currTS].denominator
    currTS += 1
    while time < end_event_ticks:
        currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
        timeSec = timeInSecs(currChange, mid, time)
        try:
            if timeSec >= timeSigs[currTS].time:
                numer = timeSigs[currTS].numerator
                denom = timeSigs[currTS].denominator
                # print(numer, denom)
                currTS += 1
        except IndexError:
            pass
        except Exception as e:
            print("Failed to parse fret bars")
        fretbarDistance = int(mid.ticks_per_beat * 4 / denom)
        # print(time, timeSec)
        fretbars.append(timeSec)
        time += fretbarDistance

    return fretbars


def active_note_check(x, active_notes, timeSec, midi_track, track):  # midi_track is usually anim_notes
    if x.velocity != 0:
        if x.note in active_notes:
            return -1
        active_notes[x.note] = AnimNoteWT(timeSec, x.note, x.velocity)
    else:
        try:
            active_notes[x.note].setLength(timeSec - active_notes[x.note].time)
            if active_notes[x.note].time in midi_track[track.name]:
                midi_track[track.name][active_notes[x.note].time].append(active_notes[x.note])
            else:
                midi_track[track.name][active_notes[x.note].time] = [active_notes[x.note]]
            active_notes.pop(x.note)
        except KeyError:
            pass
        except:
            raise Exception(f"Something went wrong parsing the {track.name} track.")
    return 0


def create_diff_dicts():
    play_notes = {
        "Easy": [],
        "Medium": [],
        "Hard": [],
        "Expert": []
    }

    active_notes = {
        "Easy": {},
        "Medium": {},
        "Hard": {},
        "Expert": {}
    }
    forced_notes = {
        "Easy": {"off": [], "on": []},
        "Medium": {"off": [], "on": []},
        "Hard": {"off": [], "on": []},
        "Expert": {"off": [], "on": []}
    }
    play_face_off = {"P1": [], "P2": []}
    play_star = {
        "Easy": [],
        "Medium": [],
        "Hard": [],
        "Expert": []
    }
    play_star_bm = {
        "Easy": [],
        "Medium": [],
        "Hard": [],
        "Expert": []
    }
    play_star_fo = {
        "Easy": [],
        "Medium": [],
        "Hard": [],
        "Expert": []
    }
    return play_notes, active_notes, forced_notes, play_face_off, play_star, play_star_bm, play_star_fo


def split_list(l_in):
    return [l_in[i:i + 2] for i in range(0, len(l_in), 2)]


def parse_wt_qb(mid, hopo, *args, **kwargs):
    changes, ticks = tempMap(mid)
    if "force_only" in args:
        time_hopos = False
    else:
        time_hopos = True

    global sp_note
    if "star_power" in kwargs:
        sp_note = kwargs["star_power"]
    else:
        sp_note = 116

    if "wor" in args:
        drum_key_map = drumKeyMapRB_wor
    else:
        drum_key_map = drumKeyMapRB_wt

    ticksArray = np.array(ticks)
    changesArray = np.array(changes)
    xplus_chart = False
    make_xplus = False

    ghost_notes = {}
    has_2x_kick = False

    play_notes_dict = {
        "PART GUITAR": "Guitar",
        "PART BASS": "Bass",
        "PART DRUMS": "Drums",
        "PART VOCALS": "Vocals"
    }

    playable_qb = {
        "Guitar": {},
        "Bass": {},
        "Drums": {},
        "Vocals": {
            "song_vocals": [],
            "vocals_freeform": [],
            "vocals_phrases": [],
            "vocals_note_range": [60, 60],
            "lyrics": [],
            "vocals_markers": [],
            "qs_file": {}
        }
    }

    playable_face_off = {
        "Guitar": {},
        "Bass": {},
        "Drums": {}
    }

    playable_fo_star_power = {
        "Guitar": {},
        "Bass": {},
        "Drums": {}
    }

    playable_star_power = {
        "Guitar": {},
        "Bass": {},
        "Drums": {}
    }

    playable_bm_star_power = {
        "Guitar": {},
        "Bass": {},
        "Drums": {}
    }

    playable_tap = {
        "Guitar": [],
        "Bass": []
    }

    playable_solo_markers = {
        "Guitar": [],
        "Bass": [],
        "Drums": []
    }

    playable_drum_fills = []

    valid_anims = {
        "LIGHTSHOW": valid_lightshow_notes_wt,
        "CAMERAS": valid_camera_notes_wt,
        "CROWD": valid_crowd_wt
    }

    if "wor" in args:
        valid_anims["LIGHTSHOW"].extend(valid_lightshow_notes_wor)
        valid_anims["CAMERAS"].extend(valid_camera_notes_wor)

    if "wtde" in args:
        valid_anims["LIGHTSHOW"].extend(valid_lightshow_notes_wor)
        valid_anims["CAMERAS"].extend(valid_camera_notes_wtde)

    anim_notes = {
        "scripts_notes": {},
        "left_hand": {},
        "triggers_notes": {},
        "CAMERAS": {},
        "LIGHTSHOW": {},
        "CROWD": {},
        "drum_anims": {},
        "scripts": {},
        "anim": {},
        "triggers": {},
        "cameras": [],
        "lightshow": [],
        "crowd": {},
        "drums": {},
        "performance": []
    }

    fo_star_power = {
        "Guitar": [],
        "Bass": [],
        "Drums": []
    }

    star_power = {
        "Guitar": [],
        "Bass": [],
        "Drums": []
    }

    bm_star_power = {
        "Guitar": [],
        "Bass": [],
        "Drums": []
    }
    open_hh = []

    vocals_notes = {}
    vocals_freeform = {
        0: [],
        1: []
    }  # 0 is freeform, 1 is hype
    vocals_freeform_playable = []
    vocals_phrases = {105: [],
                      106: []}  # 105 is star power, 106 is bm star power# Type 0 is blank, playable phrases alternate between 1 and 2
    vocals_phrase_dict = {0: {}}
    # 3 exists too. Maybe to do with face-off?
    vocals_lyrics = {}
    vocals_lyrics_playable = {}
    lyrics_qs = []
    lyrics_qs_dict = {}
    vocal_sp = []

    drum_notes = {}
    timeSigs = []
    markers = []
    last_event_secs = 0
    last_event_tick = 0
    end_event_secs, end_event_ticks = 0, 0
    for track_num, track in enumerate(mid.tracks):

        try:
            instrument = play_notes_dict[track.name]
        except:
            print(f"Processing non-instrument track {track.name}")
            playable = False
        else:
            print(f"Processing instrument track {track.name}")
            playable = True

        if playable:
            if re.search(r'(guitar|bass)', instrument, flags=re.IGNORECASE):
                inst_map = note_mapping_gh3 | forceMapping | note_mapping_wt_gtr
                drums = False
            elif re.search(r'(drums)', instrument, flags=re.IGNORECASE):
                inst_map = note_mapping_gh3 | forceMapping | note_mapping_wt_drum
                if "2x_check" in args:
                    inst_map.pop(96)
                    inst_map[95] = 'Expert_purple'
                    xplus_chart = True

                drums = True
            else:
                inst_map = note_mapping_gh3 | forceMapping | note_mapping_wt_drum
                drums = False

            play_notes, active_notes, forced_notes, play_face_off, play_star, play_star_bm, play_star_fo = create_diff_dicts()

            play_tap = []
            play_solo = []

            sysex_taps = []
            sysex_opens = {
                0: [],  # Easy
                1: [],  # Medium
                2: [],  # Hard
                3: [],  # Expert
            }
            sysex_opens_check = 0


        else:
            active_notes = {}
        time = 0
        for y, x in enumerate(track):
            time += x.time
            currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
            time_sec = timeInSecs(currChange, mid, time)
            if track_num == 0:
                if x.type == "time_signature":
                    timeSigs.append(timeSigEvent(time_sec, x.numerator, x.denominator))
            elif track.name == "EVENTS":
                if x.type == 'text':
                    end_event_secs, end_event_ticks = process_text_event(x, markers, time, time_sec)
                    if end_event_secs and end_event_ticks:
                        continue
            elif re.search(track.name, rf'{venue_track}|cameras_wt', flags=re.IGNORECASE):
                if re.search(track.name, r'cameras_wt', flags=re.IGNORECASE):
                    track.name = "CAMERAS"
                else:
                    track.name = track.name.upper()
                valid_check = valid_anims[track.name]
                if x.type == "note_on" or x.type == "note_off":
                    if x.note in valid_check:
                        create_anim_note(x, active_notes, track.name, anim_notes, time_sec,
                                         AnimNoteWT(time_sec, x.note, x.velocity))
                        '''if x.velocity != 0:
                            if x.note in active_notes:
                                continue
                            active_notes[x.note] = AnimNoteWT(time_sec, x.note, x.velocity)
                        else:
                            try:
                                active_notes[x.note].setLength(time_sec - active_notes[x.note].time)
                                if active_notes[x.note].time in anim_notes[track.name]:
                                    anim_notes[track.name][active_notes[x.note].time].append(active_notes[x.note])
                                else:
                                    anim_notes[track.name][active_notes[x.note].time] = [active_notes[x.note]]
                                active_notes.pop(x.note)
                            except KeyError:
                                pass
                            except:
                                raise Exception(f"Something went wrong parsing the {track.name} track.")'''

                elif x.type == "text":
                    if re.search(r'^(SetBlendTime|LightShow_Set)', x.text, flags=re.IGNORECASE):
                        # if x.text.startswith("SetBlendTime") or x.text.startswith("LightShow_Set"):
                        blendtime = lightshow_script(x)
                        anim_notes["lightshow"].append(scriptsNode(time_sec, "LightShow_SetTime", [blendtime]))
                    elif re.search(r'(zoom_(in|out)_(quick|slow)_(small|large)|pulse[1-5]) [0-9]+', x.text,
                                   flags=re.IGNORECASE):
                        zoom_type = x.text.split(" ")[0]
                        zoom_length = float(x.text.split(" ")[1])
                        if zoom_length.is_integer():
                            zoom_length = int(zoom_length)
                        param_type, param_time = camera_script(zoom_type, zoom_length)
                        anim_notes["performance"].append(
                            scriptsNode(time_sec, "CameraCutsEffect_FOVPulse", [param_type, param_time]))
            elif playable:
                if re.search(r'(guitar|bass|drums)', instrument, flags=re.IGNORECASE):
                    if x.type == "note_on" or x.type == "note_off":
                        if x.note in inst_map:
                            chart_diff = inst_map[x.note].split("_")[0]
                            note_colour = inst_map[x.note].split("_")[1]
                            if note_colour not in ["off", "on"]:
                                to_add = {"time_sec": time_sec, "time_tick": time, "curr_change": currChange,
                                          "velocity": x.velocity}
                                if note_colour in active_notes[chart_diff]:
                                    temp = active_notes[chart_diff]
                                    temp[note_colour].append(to_add)
                                else:
                                    active_notes[chart_diff][note_colour] = [to_add]
                                if all([drums, x.note >= 97, x.velocity == 1]):
                                    ghost = (1 << note_bit_vals[note_colour])
                                    if time_sec in ghost_notes:
                                        if not ghost & ghost_notes[time_sec]:
                                            ghost_notes[time_sec] += ghost
                                    else:
                                        ghost_notes[time_sec] = ghost
                            else:
                                forced_notes[chart_diff][note_colour].append(time_sec)
                        elif x.note == sp_note:
                            star_power[instrument].append(time_sec)
                        elif x.note == bm_star_note:
                            bm_star_power[instrument].append(time_sec)
                        elif x.note == fo_star_note:
                            fo_star_power[instrument].append(time_sec)
                        elif x.note in faceOffMapping:
                            play_face_off[faceOffMapping[x.note]].append(time_sec)
                        elif x.note == tap_note:
                            play_tap.append(time_sec)
                        elif x.note == solo_note:
                            play_solo.append(time_sec)
                        elif x.note in leftHandGtr_wt and not drums:
                            new_note = anim_maps[instrument][x.note]
                            if x.velocity != 0 and x.type == "note_on":
                                if new_note in active_notes:
                                    continue
                                active_notes[new_note] = AnimNoteWT(time_sec, new_note, x.velocity)
                            else:
                                try:
                                    active_notes[new_note].setLength(time_sec - active_notes[new_note].time)
                                    if active_notes[new_note].time in anim_notes["left_hand"]:
                                        anim_notes["left_hand"][active_notes[new_note].time].append(
                                            active_notes[new_note])
                                    else:
                                        anim_notes["left_hand"][active_notes[new_note].time] = [active_notes[new_note]]
                                    active_notes.pop(new_note)
                                except KeyError:
                                    pass
                                except:
                                    raise Exception(f"Something went wrong parsing the {track.name} track.")
                        elif x.note in drum_key_map and drums:
                            new_note = drum_key_map[x.note]
                            if all([x.note in range(50, 52), x.channel == 1, "wor" in args]):
                                new_note -= 1
                            if x.velocity != 0 and x.type == "note_on":
                                if new_note in active_notes:
                                    continue
                                active_notes[new_note] = AnimNoteWT(time_sec, new_note, x.velocity)
                            else:
                                try:
                                    drum_anim_note(x, active_notes, new_note, anim_notes, time_sec, args)
                                    '''new_len = time_sec - active_notes[new_note].time
                                    active_notes[new_note].setLength(new_len)
                                    if active_notes[new_note].time in anim_notes["drum_anims"]:
                                        anim_notes["drum_anims"][active_notes[new_note].time].append(
                                            active_notes[new_note])
                                    else:
                                        anim_notes["drum_anims"][active_notes[new_note].time] = [active_notes[new_note]]
                                    if x.note not in practice_mode_wt:
                                        temp = anim_notes["drum_anims"][active_notes[new_note].time]
                                        if "wor" in args:
                                            if new_note < 22:
                                                practice_note = new_note + 86
                                            elif new_note < 105:
                                                practice_note = new_note + 56
                                            else:
                                                active_notes.pop(new_note)
                                                continue
                                        else:
                                            practice_note = new_note - 13
                                        temp.append(AnimNoteWT(time_sec, practice_note, temp[-1].velocity))
                                        temp[-1].setLength(new_len)
                                    active_notes.pop(new_note)'''
                                except KeyError as E:
                                    # raise E
                                    pass

                                except:
                                    raise Exception(f"Something went wrong parsing the {track.name} track.")

                        elif x.note == 25 and drums:
                            open_hh.append(time_sec)
                        if all([x.note == 95, drums, "wtde" in args, not make_xplus]):
                            make_xplus = True
                        # if x.note in faceOffMapping:
                    elif x.type == "sysex":
                        sys_head = x.data[:3]
                        if not sys_head == (80, 83, 0):
                            continue
                        if x.data[5] == 4 and x.data[4] in [3, 127]:
                            sysex_taps.append(time_sec)
                        elif x.data[5] == 1 and x.data[4] != 127:
                            try:
                                sysex_opens[x.data[4]].append(time_sec)
                                if not sysex_opens_check:
                                    sysex_opens_check = 1
                            except:
                                print(f"{track.name}: Invalid SysEx event found at {time_sec}")
                        # print()

                else:  # vocals. Note range 36-84 inclusive probably
                    if x.type == "lyrics":
                        vocals_lyrics[time_sec] = x.text
                    elif x.type == "text":
                        if "[" not in x.text:
                            vocals_lyrics[time_sec] = x.text
                    elif x.type == "note_on" or x.type == "note_off":
                        if x.note in playable_range:
                            if x.note in vocals_notes:
                                vocals_notes[x.note].append(time_sec)
                            else:
                                vocals_notes[x.note] = [time_sec]
                        elif x.note in phrase_marker:
                            vocals_phrases[x.note].append(time_sec)
                        elif x.note == freeform_marker:
                            vocals_freeform[x.channel].append(time_sec)
                        elif x.note == sp_note:
                            vocal_sp.append(time_sec)

        if time > last_event_tick:
            last_event_tick = time
            last_event_secs = time_sec
        if playable and not re.search(r'(vocal)', instrument, flags=re.IGNORECASE):
            if sysex_taps and not play_tap:
                play_tap = sysex_taps
            star_power[instrument] = split_list(star_power[instrument])
            bm_star_power[instrument] = split_list(bm_star_power[instrument])
            fo_star_power[instrument] = split_list(fo_star_power[instrument])

            for player, fo in play_face_off.items():
                if fo:
                    play_face_off[player] = split_list(fo)
            for diff, notes in active_notes.items():
                timestamps = create_playable_notes(notes, drums)
                # colour_time[-1]["length"] = playtime - colour_time[-1]["time"]
                if all([drums, "2x_kick" in args, diff == "Expert", "2x" in notes]):
                    has_2x_kick = True
                    d_kick_list = []
                    for counter, kick in enumerate(notes["2x"]):
                        if counter % 2 == 0:
                            d_kick_list.append(kick)
                        else:
                            d_kick_list[-1]["length_sec"] = kick["time_sec"] - d_kick_list[-1]["time_sec"]
                    for x in d_kick_list:
                        if x["time_sec"] in timestamps:
                            timestamps[x["time_sec"]]["2x_kick"] = 1
                        else:
                            timestamps[x["time_sec"]] = {"colours": [], "colour_name": [], "2x_kick": 1,
                                                         "length_sec": x["length_sec"], "velocity": x["velocity"],
                                                         "accents": [], "length_sec_kick": 0}
                timestamps = dict(sorted(timestamps.items()))
                if drums and diff == "Expert":
                    drum_notes = dict(sorted(timestamps.items()))
                time_array = np.array(list(timestamps.keys()))
                if sysex_opens_check:
                    sys_diff = sysex_opens[difficulties.index(diff)]
                    if sys_diff:
                        sys_split = split_list(sys_diff)
                        for opens in sys_split:
                            if opens[0] == opens[1]:
                                opens[1] += 1
                            to_open = mod_notes(time_array, opens)
                            for index in np.nditer(to_open):  # Loop through indexes in timestamps
                                temp_colour = timestamps[time_array[index]]["colours"]
                                if temp_colour == [0]:
                                    timestamps[time_array[index]]["colours"] = [5]
                                    timestamps[time_array[index]]["colour_name"] = ["purple"]
                prev_time = 0
                prev_colours = ""
                if not drums:
                    for enum, (timing, gem) in enumerate(timestamps.items()):
                        # Set extended sustains
                        extend_check = mod_notes(time_array, [timing, timing + gem["length_sec"]])[0]
                        if extend_check.size > 1:
                            extended = []
                            for index in np.nditer(extend_check):  # Loop through indexes in timestamps
                                curr_in = timestamps[time_array[index]]
                                if curr_in == gem:
                                    continue
                                elif min(curr_in["colours"]) < min(gem["colours"]):
                                    gem["length_sec"] = curr_in["time_sec"] - gem["time_sec"]
                                    extend_check = mod_notes(time_array, [timing, timing + gem["length_sec"]])[0]
                                    break
                                else:
                                    extended.extend(q for q in curr_in["colours"] if q not in extended)
                                    extended.extend(s for s in gem["colours"] if s not in extended)
                            if extended:
                                for index in np.nditer(extend_check):
                                    curr_in = timestamps[time_array[index]]
                                    curr_in["extended"].extend(
                                        q for q in extended if q not in curr_in["extended"] + curr_in["colours"])
                            # print()
                        curr_colours = "".join(sorted(gem["colour_name"]))
                        # Set hopos
                        if not prev_time == 0:
                            if all([gem["time_tick"] - prev_time <= hopo, len(gem["colours"]) == 1,
                                    prev_colours != curr_colours, time_hopos]):
                                gem["colours"].append(6)
                                if "rb_mode" in args:
                                    if curr_colours in prev_colours:
                                        gem["colours"].remove(6)

                        prev_time = gem["time_tick"]
                        prev_colours = curr_colours
                    force_on = forced_notes[diff]["on"]
                    if force_on:
                        force_on = split_list(force_on)
                        for forced in force_on:
                            if forced[0] == forced[1]:
                                forced[1] += 1
                            # Pull all timestamps that need to be forced
                            to_force = mod_notes(time_array, forced)
                            for index in np.nditer(to_force):  # Loop through indexes in timestamps
                                temp_colour = timestamps[time_array[index]]["colours"]
                                if index == 0:
                                    continue
                                elif temp_colour == timestamps[time_array[index - 1]]["colours"]:
                                    continue
                                elif len(temp_colour) > 1 and "gh5_mode" not in args:
                                    if "gh3_mode" in args and 6 in temp_colour:
                                        temp_colour.remove(6)
                                    continue
                                else:
                                    timestamps[time_array[index]]["colours"].append(6)
                            # print()
                    force_off = forced_notes[diff]["off"] if not "gh3_mode" in args else 0
                    if force_off:
                        force_off = split_list(force_off)
                        for forced in force_off:
                            if forced[0] == forced[1]:
                                forced[1] += 1
                            to_force = mod_notes(time_array, forced)
                            for index in np.nditer(to_force):
                                if 6 in timestamps[time_array[index]]["colours"]:
                                    timestamps[time_array[index]]["colours"].remove(6)

                if star_power[instrument]:
                    note_range_count(star_power[instrument], time_array, play_star[diff])
                if bm_star_power[instrument]:
                    note_range_count(bm_star_power[instrument], time_array, play_star_bm[diff])
                if fo_star_power[instrument]:
                    note_range_count(fo_star_power[instrument], time_array, play_star_fo[diff])
                playable_face_off[instrument] = play_face_off.copy()

                play_notes[diff] = NoteChart(instrument, diff)

                if "ghwt" in args:
                    make_wt_bin_notes(timestamps, play_notes, diff, drums)

            playable_qb[instrument] = play_notes.copy()
            playable_star_power[instrument] = play_star.copy()
            playable_fo_star_power[instrument] = play_star_fo.copy()
            playable_bm_star_power[instrument] = play_star_bm.copy()
            if play_tap:
                if drums:
                    playable_drum_fills = split_list(play_tap)
                else:
                    # playable_tap[instrument]
                    split_taps = split_list(play_tap)
                    for tap in split_taps:
                        tap_ranges = []
                        all_taps = mod_notes(time_array, tap)[0]
                        curr_taps = []
                        if not np.any(all_taps):
                            print("No notes found under any tap note on Expert track.")
                            no_tap_notes = input(
                                "Type 'Continue' to compile without taps, or press enter to cancel compilation: ")
                            if not no_tap_notes.lower() == "continue":
                                raise Exception("Cancelled compilation by user")
                            else:
                                break
                        for note_check in list(timestamps.values())[all_taps[0]:all_taps[-1] + 1]:
                            if len(note_check['colour_name']) > 1:
                                if curr_taps:
                                    curr_taps.append(note_check["time_sec"])
                                    tap_ranges += curr_taps
                                    curr_taps = []
                            elif not curr_taps:
                                curr_taps.append(note_check["time_sec"])
                        if curr_taps:
                            tap_ranges += curr_taps
                        tap_ranges.append(tap[1])
                        for sp_tap_ranges in split_list(tap_ranges):
                            sp_tap_ranges[1] = sp_tap_ranges[1] - sp_tap_ranges[0]
                            sp_tap_ranges.append(1)
                            playable_tap[instrument].append(sp_tap_ranges.copy())
            if play_solo:
                playable_solo_markers[instrument] = split_list(play_solo)
        elif playable and re.search(r'(vocal)', instrument, flags=re.IGNORECASE):
            temp_lyrics = []
            vocals_notes_time = {}
            for pitch, t in vocals_notes.items():
                t_temp = split_list(t)
                for t2 in t_temp:
                    t_length = t2[1] - t2[0]
                    vocals_notes_time[t2[0]] = {"note": pitch, "length": t_length}

            next_hyphen = False
            for t, lyric in vocals_lyrics.items():
                if lyric.endswith("+"):
                    continue
                elif lyric.endswith("$"):
                    lyric = lyric[:-1]

                if re.search(r'[#^]$', lyric):
                    temp_text = lyric[:-1]
                    vocals_notes_time[t]["note"] = 26
                else:
                    temp_text = lyric

                if next_hyphen:
                    temp_text = "=" + temp_text
                    next_hyphen = False

                if temp_text.endswith("-"):
                    next_hyphen = True
                    temp_text = temp_text[:-1]
                elif temp_text.endswith("="):
                    next_hyphen = True
                    temp_text = temp_text[:-1] + "-"

                if "§" in temp_text:
                    temp_text = temp_text.replace("§", " ")

                temp_text = "\\L" + temp_text
                if temp_text not in lyrics_qs:
                    lyrics_qs.append(temp_text)
                vocals_lyrics[t] = temp_text

            master_phrases = {0: [0, 0]}
            for t, phrase_l in vocals_phrases.items():
                for phrase in split_list(phrase_l):
                    if phrase[0] not in master_phrases:
                        master_phrases[phrase[0]] = phrase.copy()
            master_phrases = dict(sorted(master_phrases.items()))
            keys = list(master_phrases.keys())
            values = list(master_phrases.values())
            phrase_dist = 5000
            for i in range(len(keys) - 1):
                current_key = values[i][1]
                next_key = keys[i + 1]
                t_diff = next_key - current_key
                if t_diff > phrase_dist:  # difference is greater than 5 seconds
                    num_keys_to_add = ceil(t_diff / phrase_dist)  # number of keys to add
                    interval = t_diff // num_keys_to_add  # interval between new keys
                    for j in range(0, num_keys_to_add):
                        new_key = current_key + j * (interval + 1)
                        master_phrases[new_key] = [new_key, next_key - 1]
            master_phrases[values[-1][1]] = [values[-1][1], values[-1][1]]
            master_phrases[time_sec] = [time_sec, time_sec]
            master_phrases = dict(sorted(master_phrases.items()))
            vocals_phrases = [phrase for phrase in master_phrases.values()]
            lyrics_array = np.array(list(vocals_lyrics.keys()))

            for phrase in vocals_phrases:
                to_open = mod_notes(lyrics_array, phrase)
                try:
                    temp_string = ["\\L"]
                    for index in np.nditer(to_open):  # Loop through indexes in vocals notes
                        temp_text = vocals_lyrics[lyrics_array[index]]
                        if not "+" in temp_text:
                            temp_string.append(temp_text.replace("\\L", ""))
                    temp_string = " ".join(temp_string)
                    temp_string = temp_string.replace(" =", "")
                    temp_string = temp_string.replace("\\L ", "\\L")
                    if temp_string not in lyrics_qs:
                        lyrics_qs.append(temp_string)
                    vocals_phrase_dict[phrase[0]] = {"text": temp_string}
                except:
                    vocals_phrase_dict[phrase[0]] = {}
            vocals_phrase_dict[vocals_phrases[-1][1]] = {}

            lyrics_qs = sorted(lyrics_qs)
            for f_type, freeform in vocals_freeform.items():
                f_split = split_list(freeform)
                for f2 in f_split:
                    f_len = f2[1] - f2[0]
                    f_unk = 0 if f_type == 1 else f_len // 6
                    if f2[0] in vocals_phrase_dict:
                        vocals_phrase_dict[f2[0]] = {"freeform_marker": "freeform" if f_type == 0 else "hype"}
                        vocals_freeform_playable.append([f2[0], f_len, f_unk])
                    else:
                        for key in list(vocals_phrase_dict.keys())[::-1]:
                            if key <= f2[0]:
                                if not vocals_phrase_dict[key]:
                                    vocals_phrase_dict[key] = {"freeform_marker": "freeform" if f_type == 0 else "hype"}
                                    vocals_freeform_playable.append([key, f_len, f_unk])
                                    break
                                else:
                                    print(
                                        f"Freeform marker at {f2[0]} does not coincide with a free phrase marker. Skipping...")
            playable_freeform_dict = {}
            for t in vocals_freeform_playable:
                playable_freeform_dict[t[0]] = t
            vocals_freeform_playable = []
            playable_freeform_dict = dict(sorted(playable_freeform_dict.items()))
            for t, freeform in playable_freeform_dict.items():
                vocals_freeform_playable.append(freeform)
            for lyrics in lyrics_qs:
                lyrics_qs_dict[lyrics] = CRC.QBKey_qs(lyrics)

            vox_player = 0
            for t, phrase in vocals_phrase_dict.items():
                if phrase:
                    phrase["type"] = vox_player % 2 + 1
                    vox_player += 1
                else:
                    phrase["type"] = 0

            prev_time = 0
            slides = {}
            # vocals_notes_time = dict(sorted((vocals_notes_time.items())))
            for t, lyrics in vocals_lyrics.items():
                if lyrics == "+":
                    prev_len = vocals_notes_time[prev_time]["length"]
                    slide_time = prev_time + prev_len
                    slide_len = t - slide_time
                    slides[slide_time] = {"note": 2, "length": slide_len}
                else:
                    vocals_lyrics_playable[t] = lyrics_qs_dict[lyrics]
                prev_time = t
            max_range = 0
            min_range = 127
            for t, pitch in vocals_notes_time.items():
                if pitch["note"] in playable_range:
                    if pitch["note"] > max_range:
                        max_range = pitch["note"]
                    if pitch["note"] < min_range:
                        min_range = pitch["note"]
            vocals_notes_time = dict(sorted((vocals_notes_time | slides).items()))
            playable_vocals = playable_qb["Vocals"]
            playable_vocals["vocals_note_range"] = [min_range, max_range]
            for t, v_note in vocals_notes_time.items():
                playable_vocals["song_vocals"] += [t, v_note["length"], v_note["note"]]
            playable_vocals["vocals_freeform"] = vocals_freeform_playable
            for t, v_note in vocals_phrase_dict.items():
                playable_vocals["vocals_phrases"] += [t, v_note["type"]]
                if "text" in v_note:
                    playable_vocals["vocals_markers"].append(markerNode(t, f"qbs(0x{CRC.QBKey_qs(v_note['text'])})"))
                elif "freeform_marker" in v_note:
                    playable_vocals["vocals_markers"].append(
                        markerNode(t, f"$vocal_marker_{v_note['freeform_marker']}"))
            for t, v_note in vocals_lyrics_playable.items():
                playable_vocals["lyrics"].append(markerNode(t, f"qbs(0x{v_note})"))
            playable_vocals["qs_file"] = lyrics_qs_dict

            # print()
    if anim_notes["CAMERAS"]:
        prev_time = 0
        for k, v in anim_notes["CAMERAS"].items():
            if prev_time:
                prev_note = anim_notes["CAMERAS"][prev_time][0]
                prev_note.setLength(v[0].time - prev_note.time)
            prev_time = v[0].time
            if len(v) > 1:
                to_keep = -1
                to_keep_2 = -1
                for enum, cut in enumerate(v):
                    if cut.note in moment_cams:
                        to_keep = enum
                    elif cut.note in range(33,37):
                        to_keep_2 = enum
                if to_keep >= 0:
                    anim_notes["CAMERAS"][k] = [v[to_keep]]
                elif to_keep_2 >= 0:
                    anim_notes["CAMERAS"][k] = [v[to_keep_2]]
                else:
                    anim_notes["CAMERAS"][k] = [v[0]]
    temp_sp = []
    for enum, sp in enumerate(vocal_sp):
        if enum % 2 == 0:
            temp_sp.append(sp)
        else:
            temp_sp.append(sp - temp_sp[-1])

    vocal_sp = split_list(temp_sp)

    if not end_event_secs:
        end_event_ticks = last_event_tick
        end_event_secs = last_event_secs

    fretbars = parse_fretbars(timeSigs, end_event_ticks, changes, ticksArray, mid)
    if anim_notes["drum_anims"]:
        drum_anim = anim_notes["drum_anims"]
        open_hh = split_list(open_hh)
        hh_array = np.array(list(drum_anim.keys()))
        for hh in open_hh:
            to_open = mod_notes(hh_array, hh)[0]
            try:
                for index in np.nditer(to_open):  # Loop through indexes in drum anims
                    temp_anim = drum_anim[hh_array[index]]
                    temp_notes = [x.note for x in temp_anim]
                    for x in [78, 65, 39, 9]:
                        if x in temp_notes:
                            temp_anim[temp_notes.index(x)].note += 1
            except:
                continue

    if not anim_notes["CAMERAS"]:
        print("Generating cameras")
        anim_notes["CAMERAS"] = auto_gen_camera(fretbars[::8])

    if not anim_notes["LIGHTSHOW"]:
        print("Generating lightshow")
        anim_notes["LIGHTSHOW"] = auto_gen_lightshow(fretbars, markers)

    if not anim_notes["drum_anims"] and drum_notes:
        print("Generating drum animations")
        anim_notes["drum_anims"] = auto_gen_drums(drum_notes)

    if ghost_notes:
        ghost_notes = split_list([elem for pair in ghost_notes.items() for elem in pair])
    to_return = {"playable_qb": playable_qb, "star_power": playable_star_power, "bm_star_power": playable_bm_star_power,
                 "tap": playable_tap, "fo_star_power": playable_fo_star_power, "face_off": playable_face_off,
                 "gtr_markers": markers, "drum_fills": playable_drum_fills, "anim": anim_notes, "timesigs": timeSigs,
                 "fretbars": fretbars, "vox_sp": vocal_sp, "ghost_notes": ghost_notes,
                 "solo_markers": playable_solo_markers,
                 "has_2x_kick": has_2x_kick, "xplus": 0
                 }
    xplus_track = 0
    '''if "wtde" in args and make_xplus and not "2x_check" in args:
        x_args = list(args) + ["2x_check"]
        xplus_track = parse_wt_qb(mid, hopo, *x_args)

    if xplus_track:
        to_return["wtde_xplus"] = xplus_track'''

    return to_return


def make_open(temp_anim, temp_notes, from_note):
    temp_anim[temp_notes.index(from_note)].note = from_note + 1


def create_playable_notes(notes, drums=False):
    timestamps = {}
    for colour, times in notes.items():
        if colour == "2x":
            continue
        note_bit = note_bit_vals[colour]
        colour_time = []
        for count, playtime in enumerate(times):
            if count % 2 == 0:
                colour_time.append(playtime)
            else:
                if colour_time[-1]["time_sec"] in timestamps:
                    s_time = colour_time[-1]["time_sec"]
                    test_colour = timestamps[s_time]
                    t_time = colour_time[-1]["time_tick"]
                    test_colour["colours"].append(note_bit)
                    test_colour["colour_name"].append(colour)
                    temp_len = playtime["time_sec"] - s_time
                    if temp_len < 13:
                        temp_len = 13
                    temp_other_len = test_colour["length_sec"]
                    if drums:
                        if colour_time[-1]["velocity"] == 127:
                            timestamps[s_time]["accents"].append(note_bit)
                        if temp_len != test_colour["length_sec"]:
                            temp_len_t = playtime["time_tick"] - t_time
                            other_temp_t = timestamps[s_time]["length_tick"]
                            if temp_len_t <= 180 and other_temp_t <= 180:
                                timestamps[s_time]["length_sec"] = min(temp_len, temp_other_len)
                                timestamps[s_time]["length_tick"] = min(temp_len_t, other_temp_t)
                                del temp_len
                                del temp_other_len
                                del temp_len_t
                                del other_temp_t
                            elif colour == "purple":
                                test_colour["length_sec_kick"] = temp_len
                            elif 5 in test_colour["colours"]:
                                test_colour["length_sec_kick"] = test_colour["length_sec"]
                                test_colour["length_sec"] = temp_len
                            else:
                                timestamps[s_time]["length_sec"] = min(temp_len, temp_other_len)
                                timestamps[s_time]["length_tick"] = min(temp_len_t, other_temp_t)
                                del temp_len
                                del temp_other_len
                                del temp_len_t
                                del other_temp_t
                    else:
                        if temp_len != timestamps[s_time]["length_sec"]:
                            temp_len_t = playtime["time_tick"] - t_time
                            other_temp_t = timestamps[s_time]["length_tick"]
                            timestamps[s_time]["length_sec"] = min(temp_len, temp_other_len)
                            timestamps[s_time]["length_tick"] = min(temp_len_t, other_temp_t)
                            del temp_len
                            del temp_other_len
                            del temp_len_t
                            del other_temp_t
                else:
                    s_time = colour_time[-1]["time_sec"]
                    t_time = colour_time[-1]["time_tick"]
                    len_sec = playtime["time_sec"] - s_time
                    if len_sec < 13:
                        len_sec = 13
                    len_tick = playtime["time_tick"] - t_time
                    if not drums:
                        timestamps[s_time] = {"colours": [note_bit], "colour_name": [colour],
                                              "length_sec": len_sec,
                                              "length_tick": playtime["time_tick"] - t_time,
                                              "extended": []} | colour_time[-1]
                    else:
                        timestamps[s_time] = {"colours": [note_bit], "colour_name": [colour],
                                              "length_sec": len_sec,
                                              "length_tick": len_tick,
                                              "accents": [], "length_sec_kick": 0} | colour_time[-1]
                        if colour_time[-1]["velocity"] == 127:
                            timestamps[s_time]["accents"].append(note_bit)
    return timestamps


def auto_gen_camera(fretbars, gh3=False):
    cam_cycle = [10, 18, 23, 15, 43, 11, 19, 24, 16, 30]
    if gh3:
        cam_cycle = [wor_camera_converts["gh3"][x] for x in cam_cycle]
    cameras = {}
    for enum, fb in enumerate(fretbars):
        note_start = round_time(fb)
        try:
            note_len = round_cam_len(round_time(fretbars[enum + 1]) - note_start)
        except IndexError:
            note_len = 20000
        if gh3:
            cameras[note_start] = [AnimNote(note_start, cam_cycle[enum % len(cam_cycle)])]
        else:
            cameras[note_start] = [AnimNoteWT(note_start, cam_cycle[enum % len(cam_cycle)], 96)]
        cameras[note_start][0].setLength(note_len)
    return cameras


def auto_gen_drums(drum_notes):
    anim_lookup = {
        0: 74,
        1: 77,
        2: 78,
        3: 75,
        4: 80,
        5: 73
    }
    drum_anim = {}
    for note_time, note in drum_notes.items():
        anim_array = []
        note_len = note["length_sec"]
        for colour in note['colours']:
            mid_note = anim_lookup[colour]
            anim_array.append(AnimNoteWT(note_time, mid_note, 96, note_len))
            anim_array.append(AnimNoteWT(note_time, mid_note - 13, 96, note_len))
        drum_anim[note_time] = anim_array
    return drum_anim


def auto_gen_lightshow(fretbars, markers, gh3=False):
    fb_array = np.array(fretbars)
    lightshow = {}
    if gh3:
        lightshow[0] = [AnimNote(0, 39, 25), AnimNote(0, 76, 25)]
    else:
        lightshow[0] = [AnimNoteWT(0, 39, 96, 25), AnimNoteWT(0, 84, 96, 25)]

    gh3_lights = {
        74: 74,
        75: 74,
        76: 75,
        77: 74,
        78: 75,
        79: 78
    }

    for enum, marker in enumerate(markers):
        try:
            next_time = markers[enum + 1].time
        except IndexError:
            break
        if re.search(r'intro( [0-9]?[a-z]?)?', marker.marker, flags=re.IGNORECASE):
            light = 79  # Prelude
            light_steps = 0
        elif re.search(r'(verse( [0-9]?a))|verse$', marker.marker, flags=re.IGNORECASE):
            light = 78  # Exposition
            light_steps = 4
        elif re.search(r'((pre)-?(chorus)( [0-9]?a))|(pre)-?(chorus)$', marker.marker, flags=re.IGNORECASE):
            light = 74  # Falling Action
            light_steps = 2
        elif re.search(r'(chorus( [0-9]?a))|chorus$', marker.marker, flags=re.IGNORECASE):
            light = 75  # Climax
            light_steps = 1
        elif re.search(r'(bridge( [0-9]?a))|bridge$', marker.marker, flags=re.IGNORECASE):
            light = 77  # Falling Action
            light_steps = 2
        elif re.search(r'(main riff( [0-9]?a))|main riff$', marker.marker, flags=re.IGNORECASE):
            light = 76  # Tension
            light_steps = 2
        else:
            light = 78  # Exposition
            light_steps = 4
        if gh3:
            light = gh3_lights[light]
            lightshow[marker.time] = [AnimNote(marker.time, light, 25)]
        else:
            lightshow[marker.time] = [AnimNoteWT(marker.time, light, 96, 25)]
        if light_steps != 0:
            curr_steps = 1
            frets_in_range = fb_array[(fb_array > marker.time) & (fb_array < next_time)]
            for x in frets_in_range:
                if curr_steps % light_steps == 0:
                    light_time = int(x)
                    if gh3:
                        lightshow[light_time] = [AnimNote(light_time, 58, 25)]
                    else:
                        lightshow[light_time] = [AnimNoteWT(light_time, 58, 96, 25)]
                curr_steps += 1
    return lightshow


def process_text_event(event, markers, time, time_sec):
    if event.text.startswith("[section"):
        if event.text.startswith("[section_"):
            event.text = event.text.replace("_", " ", 1)
        try:
            markers.append(markerNode(time_sec, sections[event.text.split(" ")[1][:-1]].title()))
        except:
            new_marker = " ".join(
                w.capitalize() for w in event.text.replace("_", " ").replace("\"", "\'").split(" ")[1:])
            if new_marker[-1] == "]":
                new_marker = new_marker[:-1]
            markers.append(markerNode(time_sec, new_marker))
            # print()
    elif event.text.startswith("[prc_"):
        try:
            markers.append(markerNode(time_sec, sections[event.text[1:-1]].title()))
        except:
            markers.append(markerNode(time_sec, event.text[1:-1].title()))
    elif event.text == '[end]':
        end_event_secs = time_sec
        end_event_ticks = time
        markers.append(markerNode(time_sec, "_ENDOFSONG"))
        return end_event_secs, end_event_ticks
    return 0, 0


def make_gh3_bin_notes(timestamps, play_notes, diff):
    for enum, gem in timestamps.items():
        play_notes[diff].notes.append(enum)
    return


def make_wt_bin_notes(timestamps, play_notes, diff, drums):
    for enum, gem in timestamps.items():
        play_notes[diff].notes.append(enum)
        len_bin = bin(gem["length_sec"])[2:].zfill(16)
        if not drums:
            mod_bin = "11111"
            if gem["extended"]:
                mod_bin = int(mod_bin, 2)
                for mod in gem["extended"]:
                    mod_bin -= 1 << mod
                mod_bin = bin(mod_bin)[2:]
        elif gem["accents"]:
            mod_bin = int("11111", 2)
            for mod in gem["colours"]:
                if mod not in gem["accents"] and mod < 5:
                    mod_bin -= 1 << mod
            mod_bin = bin(mod_bin)[2:]
        else:
            mod_bin = "00000"

        if drums and "2x_kick" in gem:
            double_bits = "0010"
            mod_bin = double_bits + mod_bin

        mod_bin = mod_bin.zfill(9)
        sep_kick = 0
        if not drums:
            notes_bin = make_bin_notes(gem)
        elif gem["length_sec_kick"]:
            gem["colours"].remove(5)
            notes_bin = make_bin_notes(gem)
            kick_note = make_bin_notes({"colours": [5]})
            len_bin_kick = bin(gem["length_sec_kick"])[2:].zfill(16)
            sep_kick = int(mod_bin + kick_note + len_bin_kick, 2)
            mod_bin = "0000" + mod_bin[4:]
        else:
            notes_bin = make_bin_notes(gem)

        note_val = mod_bin + notes_bin + len_bin
        play_notes[diff].notes.append(int(note_val, 2))
        if sep_kick:
            play_notes[diff].notes.append(enum)
            play_notes[diff].notes.append(sep_kick)
    return


def parse_gh3_qb(mid, hopo, *args, **kwargs):
    hmxmode = 1
    changes, ticks = tempMap(mid)

    ticksArray = np.array(ticks)
    changesArray = np.array(changes)

    GH2Tracks = ["PART GUITAR COOP", "PART RHYTHM", "TRIGGERS", "BAND BASS", "BAND DRUMS", "BAND SINGER", "BAND KEYS"]
    gh3venue = 0
    hmxvenue = 0

    for x in mid.tracks:
        if x.name in GH2Tracks:
            spNote = 103
        elif x.name == "GH3 VENUE":
            gh3venue = x.copy()

    # Converting an RB venue will take a bit of figuring out the math. Do it later
    """if hmxvenue and not gh3venue:
        gh3venue = convertVenue(mid, hmxvenue, changes, ticksArray)"""

    play_notes_dict = {
        "PART GUITAR": "Guitar",
        "PART BASS": "Bass",
        "PART GUITAR COOP": "Guitar_Coop",
        "PART RHYTHM": "Rhythm_Coop"
    }

    playable_qb = {
        "Guitar": {},
        "Bass": {},
        "Guitar_Coop": {},
        "Rhythm_Coop": {}
    }

    leftHandAnims = {
        "Guitar": [],
        "Bass": []
    }

    face_offs = {
        "P1": [],
        "P2": []
    }

    venue_track = "LIGHTSHOWCAMERASCROWD"

    valid_anims = {
        "LIGHTSHOW": valid_lightshow_notes_gh3,
        "CAMERAS": valid_camera_notes_gha if "gha" in args else valid_camera_notes_gh3,
        "CROWD": valid_crowd_wt
    }

    anim_notes = {
        "scripts_notes": {},
        "left_hand": {},
        "triggers_notes": {},
        "CAMERAS": {},
        "LIGHTSHOW": {},
        "CROWD": {},
        "drum_anims": {},
        "scripts": {},
        "anim": {},
        "triggers": {},
        "cameras": [],
        "lightshow": [],
        "crowd": {},
        "drums": {},
        "performance": []
    }

    fo_star_power = {
        "Guitar": [],
        "Bass": [],
        "Guitar_Coop": [],
        "Rhythm_Coop": []
    }

    star_power = {
        "Guitar": [],
        "Bass": [],
        "Guitar_Coop": [],
        "Rhythm_Coop": []
    }

    bm_star_power = {
        "Guitar": [],
        "Bass": [],
        "Guitar_Coop": [],
        "Rhythm_Coop": []
    }

    playable_star_power = {
        "Guitar": {},
        "Bass": {},
        "Guitar_Coop": {},
        "Rhythm_Coop": {}
    }

    playable_bm_star_power = {
        "Guitar": {},
        "Bass": {},
        "Guitar_Coop": {},
        "Rhythm_Coop": {}
    }

    open_hh = []
    inst_map = note_mapping_gh3 | forceMapping

    note_len_mode = 0  # Convert WoR lighting to GH3 style blend events
    drum_key_map = drumKeyMapRB_gh3

    cameraNotes = []
    lightshowNotes = []
    lightshowScripts = []
    drumNotes = []
    timeSigs = []
    markers = []
    fretbars = []

    last_event_secs = 0
    last_event_tick = 0
    end_event_secs, end_event_ticks = 0, 0

    for track_num, track in enumerate(mid.tracks):
        try:
            instrument = play_notes_dict[track.name]
        except:
            print(f"Processing non-instrument track {track.name}")
            playable = False
        else:
            print(f"Processing instrument track {track.name}")
            playable = True
        if playable:
            play_notes, active_notes, forced_notes, play_face_off, play_star, play_star_bm, play_star_fo = create_diff_dicts()

            starPowerList = []

            activeNote = {
                "Easy": 0,
                "Medium": 0,
                "Hard": 0,
                "Expert": 0
            }

            forcing = {
                "Easy": {"force_on": 0, "force_off": 0},
                "Medium": {"force_on": 0, "force_off": 0},
                "Hard": {"force_on": 0, "force_off": 0},
                "Expert": {"force_on": 0, "force_off": 0}
            }

        else:
            active_notes = {}
        time = 0
        for y, x in enumerate(track):
            time += x.time
            currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
            time_sec = timeInSecs(currChange, mid, time)
            if track_num == 0:
                if x.type == "time_signature":
                    timeSigs.append(timeSigEvent(time_sec, x.numerator, x.denominator))
            elif track.name == "EVENTS":
                if x.type == 'text':
                    # print(msg, time_sec)
                    end_event_secs, end_event_ticks = process_text_event(x, markers, time, time_sec)
                    if end_event_secs and end_event_ticks:
                        continue
            elif re.search(track.name, venue_track, flags=re.IGNORECASE):
                track.name = track.name.upper()
                valid_check = valid_anims[track.name]
                if track.name == "CAMERAS" and not "gha" in args:
                    alt_check = wor_camera_converts["gh3"]
                else:
                    alt_check = []
                if x.type == "note_on" or x.type == "note_off":
                    if x.note in valid_check:
                        if track.name == "LIGHTSHOW":
                            if x.note == 107:
                                note_len_mode = 1
                                continue
                            if all([x.note in range(39, 54), note_len_mode]):
                                continue
                        create_anim_note(x, active_notes, track.name, anim_notes, time_sec,
                                         AnimNote(time_sec, x.note))
                    elif x.note in alt_check and "gha" not in args:
                        create_anim_note(x, active_notes, track.name, anim_notes, time_sec,
                                         AnimNote(time_sec, alt_check[x.note]))
                elif x.type == "text":
                    if re.search(r'^(SetBlendTime|LightShow_Set)', x.text, flags=re.IGNORECASE) and not note_len_mode:
                        # if x.text.startswith("SetBlendTime") or x.text.startswith("LightShow_Set"):
                        blendtime = {"param": "time", "data": float(x.text.split(" ")[1]),
                                     "type": "Float"}  # Blend time is in seconds
                        anim_notes["lightshow"].append(scriptsNode(time_sec, "LightShow_SetTime", [blendtime]))
            elif track.name == "PART DRUMS":
                if x.type == "note_on" or x.type == "note_off":
                    if x.note in drum_key_map:
                        new_note = drum_key_map[x.note]
                        if x.velocity != 0 and x.type == "note_on":
                            if new_note in active_notes:
                                continue
                            active_notes[new_note] = AnimNote(time_sec, drumKeyMapRB_gh3[x.note])
                        else:
                            try:
                                drum_anim_note(x, active_notes, new_note, anim_notes, time_sec, args)
                            except KeyError as E:
                                # raise E
                                pass
                            except:
                                raise Exception(f"Something went wrong parsing the {track.name} track.")
                    elif x.note == 25:
                        open_hh.append(time_sec)
            elif track.name == "PART VOCALS":
                if x.type == "text":
                    check_to_add_stance(x, time_sec, anim_notes, "Vocalist", singer_stances, singer_anims)
            elif playable:
                if x.type == "note_on" or x.type == "note_off":
                    if x.note in inst_map:
                        chart_diff = inst_map[x.note].split("_")[0]
                        note_colour = inst_map[x.note].split("_")[1]
                        if note_colour not in ["off", "on"]:
                            to_add = {"time_sec": time_sec, "time_tick": time, "curr_change": currChange,
                                      "velocity": x.velocity}
                            if note_colour in active_notes[chart_diff]:
                                temp = active_notes[chart_diff]
                                temp[note_colour].append(to_add)
                            else:
                                active_notes[chart_diff][note_colour] = [to_add]
                        else:
                            forced_notes[chart_diff][note_colour].append(time_sec)
                    elif x.note == sp_note:
                        star_power[instrument].append(time_sec)
                    if track.name == "PART GUITAR":
                        if x.note == bm_star_note:
                            bm_star_power[instrument].append(time_sec)
                        elif x.note in faceOffMapping:
                            play_face_off[faceOffMapping[x.note]].append(time_sec)
                    if not "COOP" in track.name and x.note in leftHandGtr_gh3:
                        lh_name = instrument if instrument != "Rhythm_Coop" else "Bass"
                        new_note = anim_maps_gh3[lh_name][x.note]
                        if x.velocity != 0 and x.type == "note_on":
                            if new_note in active_notes:
                                continue
                            active_notes[new_note] = AnimNote(time_sec, new_note)
                        else:
                            try:
                                active_notes[new_note].setLength(time_sec - active_notes[new_note].time)
                                if active_notes[new_note].time in anim_notes["left_hand"]:
                                    anim_notes["left_hand"][active_notes[new_note].time].append(
                                        active_notes[new_note])
                                else:
                                    anim_notes["left_hand"][active_notes[new_note].time] = [active_notes[new_note]]
                                active_notes.pop(new_note)
                            except KeyError:
                                pass
                            except:
                                raise Exception(f"Something went wrong parsing the {track.name} track.")
                elif x.type == "text":
                    if instrument == "Bass" or instrument == "Guitar":
                        player = "Bassist" if instrument == "Bass" else "Guitarist"
                        check_to_add_stance(x, time_sec, anim_notes, player, guit_stances, guit_anims)
        if playable:
            star_power[instrument] = split_list(star_power[instrument])
            bm_star_power[instrument] = split_list(bm_star_power[instrument])
            if track.name == "PART GUITAR":
                for player, fo in play_face_off.items():
                    if fo:
                        play_face_off[player] = split_list(fo)
            for diff, notes in active_notes.items():
                timestamps = create_playable_notes(notes)
                timestamps = dict(sorted(timestamps.items()))
                time_array = np.array(list(timestamps.keys()))

                prev_time = 0
                prev_colours = ""
                for enum, (timing, gem) in enumerate(timestamps.items()):
                    curr_colours = "".join(sorted(gem["colour_name"]))
                    if prev_time != 0:
                        if all([gem["time_tick"] - prev_time <= hopo, len(gem["colours"]) == 1,
                                prev_colours != curr_colours]):
                            gem["is_hopo"] = True
                        else:
                            gem["is_hopo"] = False
                        if all([gem["is_hopo"], "rb_mode" in args, curr_colours in prev_colours]):
                            gem["colours"].append(5)
                        elif all([gem["is_hopo"], "force_only" in args]):
                            gem["colours"].append(5)
                    else:
                        gem["is_hopo"] = False

                    prev_time = gem["time_tick"]
                    prev_colours = curr_colours
                    # print()
                force_on = forced_notes[diff]["on"]
                if force_on:
                    force_on = split_list(force_on)
                    for forced in force_on:
                        if forced[0] == forced[1]:
                            forced[1] += 1
                        # Pull all timestamps that need to be forced
                        to_force = mod_notes(time_array, forced)
                        for index in np.nditer(to_force):  # Loop through indexes in timestamps
                            temp_colour = timestamps[time_array[index]]["colours"]
                            if index == 0:
                                continue
                            elif temp_colour == timestamps[time_array[index - 1]]["colours"]:
                                continue
                            elif len(temp_colour) > 1:
                                continue
                            elif timestamps[time_array[index]]["is_hopo"]:
                                if 5 in timestamps[time_array[index]]["colours"] and not "gh3_mode" in args:
                                    timestamps[time_array[index]]["colours"].remove(5)
                                continue
                            else:
                                timestamps[time_array[index]]["colours"].append(5)

                force_off = forced_notes[diff]["off"] if not "gh3_mode" in args else 0
                if force_off:
                    force_off = split_list(force_off)
                    for forced in force_off:
                        if forced[0] == forced[1]:
                            forced[1] += 1
                        to_force = mod_notes(time_array, forced)
                        for index in np.nditer(to_force):
                            if not timestamps[time_array[index]]["is_hopo"] and 5 in timestamps[time_array[index]][
                                "colours"]:
                                timestamps[time_array[index]]["colours"].remove(5)
                            elif timestamps[time_array[index]]["is_hopo"]:
                                timestamps[time_array[index]]["colours"].append(5)

                if star_power[instrument]:
                    note_range_count(star_power[instrument], time_array, play_star[diff])
                if bm_star_power[instrument]:
                    note_range_count(bm_star_power[instrument], time_array, play_star_bm[diff])

                play_notes[diff] = NoteChart(instrument, diff, True)
                for enum, gem in timestamps.items():
                    play_notes[diff].notes.append(enum)
                    play_notes[diff].notes.append(gem["length_sec"])
                    play_notes[diff].notes.append(set_gems(gem))

            playable_qb[instrument] = play_notes.copy()
            playable_star_power[instrument] = play_star.copy()
            playable_bm_star_power[instrument] = play_star_bm.copy()

    if note_len_mode:
        blend_lookup = {
            1000: 53,
            900: 52,
            800: 51,
            700: 50,
            600: 49,
            500: 48,
            400: 47,
            300: 46,
            250: 45,
            200: 44,
            150: 43,
            100: 42,
            50: 41,
            0: 40
        }
        strobe_mode = 0
        prev_len = -1
        new_lights = {}
        for key, value in anim_notes["LIGHTSHOW"].items():
            blend_time = key - 20
            max_len = 0
            blended = False
            for lights in value:
                if lights.note in range(70, 77) or lights.note in range(57,59):
                    blended = True
                if lights.note == 70:
                    strobe_mode = 1
                elif lights.note in range(71, 77):
                    strobe_mode = 0
                if lights.note == 56:
                    continue
                max_len = max(max_len, lights.length)
            if not blended:
                continue
            if not strobe_mode:
                if max_len > 1020:
                    max_len = round((max_len) / 1000, 3)
                    blendtime = {"param": "time", "data": float(max_len),
                                 "type": "Float"}  # Blend time is in seconds
                    anim_notes["lightshow"].append(scriptsNode(blend_time, "LightShow_SetTime", [blendtime]))
                elif max_len % 100 < 50:
                    max_len = round(max_len, -2)
                    blend_note = AnimNote(blend_time, blend_lookup[max_len])
                    blend_note.setLength(20)
                    if max_len == prev_len:
                        continue
                    if blend_time in new_lights:
                        new_lights[blend_time].append(blend_note)
                    else:
                        new_lights[blend_time] = [blend_note]
                elif max_len % 100 < 100 and max_len % 100 >= 50 and max_len < 300:
                    max_len = round(max_len) // 50 * 50
                    blend_note = AnimNote(blend_time, blend_lookup[max_len])
                    blend_note.setLength(20)
                    if max_len == prev_len:
                        continue
                    if blend_time in new_lights:
                        new_lights[blend_time].append(blend_note)
                    else:
                        new_lights[blend_time] = [blend_note]
                else:
                    max_len = round((max_len) / 1000, 3)
                    blendtime = {"param": "time", "data": float(max_len),
                                 "type": "Float"}  # Blend time is in seconds
                    anim_notes["lightshow"].append(scriptsNode(blend_time, "LightShow_SetTime", [blendtime]))
            else:
                blend_note = AnimNote(blend_time, 40)
                blend_note.setLength(20)
                if blend_time in new_lights:
                    new_lights[blend_time].append(blend_note)
                else:
                    new_lights[blend_time] = [blend_note]
            prev_len = max_len
        for key, value in new_lights.items():
            if key in anim_notes["LIGHTSHOW"]:
                for note in value:
                    anim_notes["LIGHTSHOW"][key].append(note)
            else:
                anim_notes["LIGHTSHOW"][key] = value
        anim_notes["LIGHTSHOW"] = dict(sorted((anim_notes["LIGHTSHOW"].items())))


    if not "end_event_secs" in locals():
        raise Exception("Invalid MIDI: No [end] event found. Cannot parse MIDI.")
    if cameraNotes:
        cameraNotes[-1].setLength(end_event_secs - cameraNotes[-1].time)

    fretbars = parse_fretbars(timeSigs, end_event_ticks, changes, ticksArray, mid)
    if anim_notes["drum_anims"]:
        drum_anim = anim_notes["drum_anims"]
        open_hh = split_list(open_hh)
        hh_array = np.array(list(drum_anim.keys()))
        for hh in open_hh:
            to_open = mod_notes(hh_array, hh)[0]
            try:
                for index in np.nditer(to_open):  # Loop through indexes in drum anims
                    temp_anim = drum_anim[hh_array[index]]
                    temp_notes = [x.note for x in temp_anim]
                    for x in [65, 53, 41]:
                        if x in temp_notes:
                            temp_anim[temp_notes.index(x)].note += 1
            except:
                continue

    if not anim_notes["CAMERAS"] and "gha" not in args:
        print("Generating cameras")
        anim_notes["CAMERAS"] = auto_gen_camera(fretbars[::8], True)

    if not anim_notes["LIGHTSHOW"]:
        print("Generating lightshow")
        anim_notes["LIGHTSHOW"] = auto_gen_lightshow(fretbars, markers, True)

    return {"playable_qb": playable_qb, "star_power": playable_star_power, "bm_star_power": playable_bm_star_power,
            "timesig": timeSigs, "markers": markers,
            "fretbars": fretbars, "face_offs": play_face_off, "anim": anim_notes}


def create_gh3_sections(qb_dict, filename, headerDict, consoleType):
    QBItems = []
    # print(midQB)

    for x in qb_dict["playable_qb"]:
        QBChart = []
        QBStar = []
        QBStarBM = []
        # print(x)
        if not qb_dict["playable_qb"][x]:
            for y in difficulties:
                instrument = x.replace("_", "").lower() if x != "Bass" else "rhythm"
                chart_name = f"{filename}_song_{instrument}_{y}"
                starName = f"{filename}_{instrument}_{y}_Star"
                BMStarName = f"{filename}_{instrument}_{y}_StarBattleMode"
                QBChart.append(basic_data(chart_name, []))
                QBStar.append(basic_data(chart_name, []))
                QBStarBM.append(basic_data(chart_name, []))
        else:
            for i, y in enumerate(qb_dict["playable_qb"][x]):
                song = qb_dict["playable_qb"][x][y].notes
                star = qb_dict["star_power"][x][y]
                star_bm = qb_dict["bm_star_power"][x][y]
                if x == "Guitar":
                    chart_name = f"{filename}_song_{y}"
                    starName = f"{filename}_{y}_Star"
                    BMStarName = f"{filename}_{y}_StarBattleMode"
                else:
                    instrument = x.replace("_", "").lower() if x != "Bass" else "rhythm"
                    chart_name = f"{filename}_song_{instrument}_{y}"
                    starName = f"{filename}_{instrument}_{y}_Star"
                    BMStarName = f"{filename}_{instrument}_{y}_StarBattleMode"
                QBChart.append(basic_data(chart_name, song))
                QBStar.append(basic_data(starName, star))
                QBStarBM.append(basic_data(BMStarName, star_bm))

        for y in [QBChart, QBStar, QBStarBM]:
            for z in y:
                QBItems.append(z)

    # print(midQB["faceOffs"])
    for x in qb_dict["face_offs"]:
        chart_name = f"{filename}_FaceOff{x}"
        if not qb_dict["face_offs"][x]:
            QBItems.append(basic_data(chart_name, []))
        else:
            QBItems.append(basic_data(chart_name, []))

    # Boss Battle Array
    for x in qb_dict["face_offs"]:
        chart_name = f"{filename}_BossBattle{x}"
        QBItems.append(basic_data(chart_name, []))

    # timesig (array), markers (struct), fretbars (integer)
    chart_name = f"{filename}_timesig"
    QBItems.append(basic_data(chart_name, [[x.time, x.numerator, x.denominator] for x in qb_dict["timesig"]]))

    chart_name = f"{filename}_fretbars"
    QBItems.append(basic_data(chart_name, qb_dict["fretbars"]))
    chart_name = f"{filename}_markers"
    gtr_markers = []
    if qb_dict["markers"]:
        for gtr in qb_dict["markers"]:
            gtr_markers.append(struct_data())
            temp_struct = gtr_markers[-1]
            temp_struct.add_data("time", str(gtr.time))
            temp_struct.add_data("marker", f"w\"{gtr.marker}\"")
    QBItems.append(basic_data(chart_name, gtr_markers))

    for anim, value in qb_dict["anim"].items():
        if anim in anim_lookup:
            chart_name = f"{filename}_{anim_lookup[anim]}"
        else:
            chart_name = f"{filename}_{anim}"
        anim_list = []
        if value:
            if type(value) == dict:
                prev_time = 0
                for timing, notes in sorted(value.items()):
                    for anim_stuff in notes:
                        anim_list.append([timing, anim_stuff.note, anim_stuff.length])
                    prev_time = timing
            elif type(value) == list:
                for anim_stuff in value:
                    anim_list.append(make_script_struct(anim_stuff, False))
        QBItems.append(basic_data(chart_name, anim_list.copy()))

    return QBItems


def check_to_add_stance(x, time_sec, anim_notes, player, stances, anims):
    while True:
        extra = []
        if re.search(r'(cycle)', x.text, re.IGNORECASE):
            extra.append("cycle")
        if re.search(r'(no_wait)', x.text, re.IGNORECASE):
            extra.append("no_wait")
        if re.search(r'( [1-9]+)$', x.text, re.IGNORECASE):
            extra.append("repeat")
            extra.append(re.search(r'( [1-9]+)$', x.text, re.IGNORECASE).group(0).strip())
        pattern = re.search(rf'({"|".join(stances)})', x.text, re.IGNORECASE)
        if pattern:
            new_stance = stance_script(time_sec, "Band_ChangeStance", player, pattern.group(0), *extra)
            break
        pattern = re.search(rf'^({"|".join(anims)})', x.text, re.IGNORECASE)
        if pattern:
            new_stance = stance_script(time_sec, "Band_PlayAnim", player, pattern.group(0), *extra)
            break
        new_stance = 0
        break
    if new_stance:
        anim_notes["performance"].append(new_stance)


def stance_script(time_sec, script, player, event, *args):
    if script == "Band_ChangeStance":
        params = new_stance_gh3(player, event, "stance", *args)
    elif script == "Band_PlayAnim":
        params = new_stance_gh3(player, event, "anim", *args)
    else:
        print(f"Script {script} at {time_sec} not recognized.")
        return 0
    script_node = scriptsNode(time_sec, script, params)
    return script_node


def create_anim_note(x, active_notes, track_name, anim_notes, time_sec, anim_entry):
    if x.velocity != 0 and x.type == "note_on":
        if x.note in active_notes:
            return
        active_notes[x.note] = anim_entry
    else:
        try:
            anim_len = time_sec - active_notes[x.note].time
            if anim_len < 13 or anim_len > 2**32:
                anim_len = 13
            active_notes[x.note].setLength(anim_len)
            if active_notes[x.note].time in anim_notes[track_name]:
                anim_notes[track_name][active_notes[x.note].time].append(active_notes[x.note])
            else:
                anim_notes[track_name][active_notes[x.note].time] = [active_notes[x.note]]
            active_notes.pop(x.note)
        except KeyError:
            pass
        except:
            raise Exception(f"Something went wrong parsing the {track_name} track.")
    return

def camera_script(zoom_type, zoom_length):
    param_type = {"param": "type", "data": zoom_type, "type": "QbKey"}
    param_time = {"param": "time", "data": zoom_length,
                  "type": "Integer" if type(zoom_length) == int else "Float"}
    return param_type, param_time

def lightshow_script(x):
    if type(x) == float or type(x) == int:
        t = x
    else:
        t = x.text.split(" ")[1]
    blendtime = {"param": "time", "data": float(t),
                 "type": "Float"}  # Blend time is in seconds
    return blendtime

def drum_anim_note(x, active_notes, new_note, anim_notes, time_sec, args):
    new_len = time_sec - active_notes[new_note].time
    active_notes[new_note].setLength(new_len)
    if active_notes[new_note].time in anim_notes["drum_anims"]:
        anim_notes["drum_anims"][active_notes[new_note].time].append(
            active_notes[new_note])
    else:
        anim_notes["drum_anims"][active_notes[new_note].time] = [active_notes[new_note]]
    if x.note not in practice_mode_wt:
        temp = anim_notes["drum_anims"][active_notes[new_note].time]
        if "wor" in args:
            if new_note < 22:
                practice_note = new_note + 86
            elif new_note < 105:
                practice_note = new_note + 56
            else:
                active_notes.pop(new_note)
                return
        elif "gh3" in args:
            if new_note < 47:
                practice_note = new_note + 24
            elif new_note < 59:
                practice_note = new_note + 12
            else:
                active_notes.pop(new_note)
                return
        else:
            practice_note = new_note - 13
        if "gh3" in args:
            temp.append(AnimNote(time_sec, practice_note))
        else:
            temp.append(AnimNoteWT(time_sec, practice_note, temp[-1].velocity))
        temp[-1].setLength(new_len)
    active_notes.pop(new_note)
    return


def make_wt_drum_anims(midi_track, tempo_data):
    active_note = {}
    drums_notes = {}
    curr_time = 0
    for event in midi_track:
        curr_time += event.time
        curr_secs = tempo_data.get_seconds(curr_time)  # Actually milliseconds
        if "note" in event.type:
            event_name = f"{event.note}-{event.channel}"
            if event.type == "note_on" and event.velocity != 0:
                active_note[event_name] = {"time": curr_secs, "note": event.note, "velocity": event.velocity}
            else:
                if event_name in active_note:
                    new_note = active_note[event_name]
                    new_note["length"] = curr_secs - new_note["time"]
                    active_note.pop(event_name)
                    velo_bin = bin(new_note["velocity"])[2:].zfill(8)
                    midi_bin = bin(new_note["note"])[2:].zfill(8)
                    len_bin = bin(new_note["length"])[2:].zfill(16)
                    bin_val = int(velo_bin + midi_bin + len_bin, 2)
                    if new_note["time"] in drums_notes:
                        drums_notes[new_note["time"]].append(bin_val)
                    else:
                        drums_notes[new_note["time"]] = [bin_val]
    drum_array = []
    for x in sorted(drums_notes.keys()):
        for y in drums_notes[x]:
            drum_array += [x, y]
    return drum_array


def get_song_tempo_data(mid_file):
    song_map = midiProcessing(mid_file)
    tempo_data = MidiInsert(song_array(song_map))
    tempo_data.set_seconds_array(np.array(tempo_data.songSeconds))
    tempo_data.set_ticks_array(np.array(tempo_data.songTime))

    return tempo_data


def make_wt_qb(mid_file):
    mid_file = MidiFile(mid_file)
    tempo_data = get_song_tempo_data(mid_file)
    for track in mid_file.tracks:
        if track.name == "drums":
            drum_anims = make_wt_drum_anims(track, tempo_data)
    return
