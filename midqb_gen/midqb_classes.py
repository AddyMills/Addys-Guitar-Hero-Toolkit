from mido import second2tick as s2t, tick2second as t2s
from midqb_definitions import *
from CRC import QBKey

colours = {
    "green": 1, "red": 2, "yellow": 4, "blue": 8, "orange": 16, "force": 32, "tap": 64}
single_notes = {1: "green", 2: "red", 4: "yellow", 8: "blue", 16: "orange"}



class Note:  # Every note will be its own class to determine what kind of chord is played, the length, and if it needs to be forced or not
    def __init__(self, time, prevNote, currTempChange):
        self.time = time
        self.green = 0
        self.red = 0
        self.yellow = 0
        self.blue = 0
        self.orange = 0
        self.chord = 0
        self.force = 0
        self.force_on = 0
        self.force_off = 0
        self.extended = 0
        self.tap = 0
        self.length = 1  # Default length of 1 ms to make note appear, but no sustain yet
        self.prev_note = prevNote
        self.tempo_change = currTempChange

    def setLength(self, length, tempo, tbp = 480):
        if s2t(length / 1000, tbp, tempo) < 240:
            self.length = 1
        else:
            self.length = length

    def setForcing(self, hopo = 170, tbp = 480, hmxmode = 1):
        value = self.getValue()
        if self.prev_note == 0:
            return
        if value == self.prev_note.getValue():
            self.force = 0
            return
        if value not in single_notes:
            return
        if self.prev_note.getValue() not in single_notes:
            if getattr(self, single_notes[value]) == getattr(self.prev_note,single_notes[value]):
                if self.force_on != 1:
                    self.force_off = 1
        prev_tempo = self.prev_note.tempo_change.tempo
        prev_time = self.prev_note.time
        # print(self.time, self.prev_note.time, prev_tempo, tbp)
        # print(self.time, self.prev_note.time, s2t((self.time - prev_time)/1000, tbp, prev_tempo))
        ticks_away = s2t((self.time - prev_time)/1000, tbp, prev_tempo)
        # print(self.time, ticks_away)
        if self.force_on != self.force_off:
            # print(self.time, "Forced")
            if self.force_on == 1:
                if ticks_away > hopo:
                    self.force = 1
                else:
                    self.force = 0
            elif self.force_off == 1:
                if ticks_away < hopo:
                    self.force = 1
                else:
                    self.force = 0
        return

    def getValue(self):
        return (self.green * 1) + (self.red * 2) + (self.yellow * 4) + (self.blue * 8) + (self.orange * 16)

    def noNoteTouch(self):
        if self.length != 1:
            self.length -= 1

    def binForm(self):
        total = 0
        for x in colours:
            if getattr(self, x) == 1:
                total += colours[x]
        # print(int(format(total, '08b'),2))
        return format(total, '08b')

    def __str__(self):
        notes = ""
        count = 0
        for x in colours:
            if getattr(self, x) == 1:
                if notes == "":
                    notes += x.title()
                else:
                    if x != "force":
                        notes += "-" + x.title()
                if x != "force":
                    count += 1
        return f"{notes} {'note' if count == 1 else 'chord'} at {self.time} with note length {self.length}.{' Forced' if self.force == 1 else ''}"

class WT_Note(Note):
    def __init__(self, time, prevNote, currTempChange, colour):
        super().__init__(time, prevNote, currTempChange)
        setattr(self, colour, 1)

class NoteChart:
    def __init__(self, part, diff):
        self.part = part
        self.diff = diff
        self.notes = []

    def __str__(self):
        return f"Part {self.part if self.part != '' else 'Guitar'}, {self.diff}, {int(len(self.notes)/2)} in chart"


class AnimNote:
    def __init__(self, time, note):
        self.time = time
        self.note = note
        self.length = 1

    def __str__(self):
        return f"Anim note {self.note} at {self.time} lasting {self.length}"

    def setLength(self, length):
        self.length = length

class AnimNoteWT(AnimNote):
    def __init__(self, time, note, velocity, length = 1):
        super().__init__(time, note)
        self.velocity = velocity
        self.length = length

    def __str__(self):
        return f"Anim note {self.note} at {self.time} with velocity {self.velocity} lasting {self.length}"


class StarPower:
    def __init__(self, time):
        self.time = time
        self.length = 0

    def __str__(self):
        return f"Star Power section at {self.time} lasting {self.length}"

    def setLength(self, length):
        self.length = length - 1


class StarPowerPhrase(StarPower):  # Star Power phrases. To be used for each difficulty
    def __init__(self, time, length):
        super().__init__(time)
        self.length = length
        self.notes = 0

    def __str__(self):
        return f"Star Power section at {self.time} lasting {self.length} containing {self.notes} notes"

    def incNotes(self):
        self.notes += 1



class FaceOffSection:  # Class to determine each section. Meant to be put into an array
    def __init__(self, time):
        self.time = time
        self.length = 1

    def __str__(self):
        return f"Face off section at {self.time} lasting {self.length}"

    def setLength(self, length):
        self.length = length


class Difficulty:
    def __init__(self, name, instrument, song=[], star=[], starBM=[]):
        self.name = name
        self.instrument = instrument
        self.song = song  # Note chart for the difficulty
        self.star = star  # Star Power phrases for each difficulty
        self.starBM = starBM  # Battle Mode phrases for each difficulty

    def __str__(self):
        return f"{self.name.title()} {self.instrument} chart containing {len(self.song)} notes and {len(self.star)} Star Power phrases"

class timeSigEvent:
    def __init__(self, time, numerator, denominator):
        self.time = time
        self.numerator = numerator
        self.denominator = denominator

    def __str__(self):
        return f"Time Sig event {self.numerator}/{self.denominator} at {self.time}"

class tempoMapItem:
    def __init__(self, time, tempo, avgTempo):
        self.time = time
        self.tempo = tempo
        self.avgTempo = avgTempo  # Avg Tempo up to that point

class markerNode:
    def __init__(self, time, marker):
        self.time = time
        self.marker = marker

    def __str__(self):
        return f"Section {self.marker} at time {self.time}"

class scriptsNode:
    def __init__(self, time, type, data):
        self.time = time
        self.type = type # Set time or colour override
        self.data = data

    def __str__(self):
        return f"{self.type} script at time {self.time}"

class QBItem:
    def __init__(self, node, name, hexname, data, console = 1, endian = "big"):
        self.qbType = qbNodeHeaders[node][console]
        self.node = node
        self.name = name # AKA id
        self.hexname = int(hexname, 16).to_bytes(4, endian)
        self.data = data

    def processData(self, console):
        arraydata = []
        if not self.data:
            self.node = "Floats"
            self.qbType = qbNodeHeaders[self.node][console]
        elif self.node == "ArrayInteger":
            self.offsets = 1
            if type(self.data[0]) == Note:
                self.itemcount = len(self.data)*3
            else:
                self.itemcount = len(self.data)
            # print(self.name, self.itemcount, len(self.data))
        elif self.node == "ArrayArray":
            self.itemcount = len(self.data)
            self.offsets = len(self.data)
            if "FaceOff" in self.name:
                for x in self.data:
                    arraydata.append([x.time, x.length])
            elif "Star" in self.name:
                for x in self.data:
                    arraydata.append([x.time, x.length, x.notes])
            elif "timesig" in self.name:
                for x in self.data:
                    arraydata.append([x.time, x.numerator, x.denominator])
            elif "_notes" in self.name:
                for x in self.data:
                    arraydata.append([x.time, x.note, x.length])
            self.arraydata = arraydata
            # print(self.arraydata)
            if type(self.arraydata[0][0]) == int:
                self.subarraytype = qbNodeHeaders["ArrayInteger"][console]
            else:
                raise Exception("Improper subarray found for song")
            #print(self.name, self.arraydata)
            # print(self.data)
        elif self.node == "ArrayStruct":
            self.itemcount = len(self.data)
            if "markers" in self.name:
                for x in self.data:
                    # print(x)
                    arraydata.append([x.time, x.marker])
            if "lightshow" in self.name:
                for x in self.data:
                    if x.type == "LightShow_SetTime":
                        arraydata.append([x.time, x.type, x.data])
                        # print(arraydata[-1])
            self.arraydata = arraydata
            # print(self.arraydata)


    def __str__(self):
        return f"QB Item {self.name}, type {self.node}, CRC {''.join('{:02x}'.format(x) for x in self.hexname)}"


class rbVenueCut:
    def __init__(self):
        return

class gh5_base_entry:
    def __init__(self):
        self.type = ""
        self.entries = []
        self.modulo = 1

    def set_type(self, type):
        self.type = type

    def set_name(self, name):
        self.name = name

    def set_size(self, size):
        self.size = size

    def set_qb_string(self, qb):
        self.qb_string = qb

    def set_modulo(self, modulo):
        self.modulo = modulo

    def add_item(self, item):
        if not item:
            return
        if type(item) == list:
            if type(item[0]) == list:
                for arrays in item:
                    self.add_item(arrays)
            else:
                self.entries += item
        else:
            self.entries.append(item)

    def process_vox(self, entry, qb_string, vox_name, size, modulo = 1):
        self.add_item(entry)
        self.set_name(vox_name)
        self.set_qb_string(qb_string)
        self.set_size(size)
        self.modulo = modulo

    def add_array_entry(self, stuff_array, endian = "big"):
        if stuff_array == -1:
            return
        for entry in stuff_array:
            adjust = 0
            entry_time = entry[0]
            if entry_time > 2**31:
                adjust = entry_time - 2**32
                entry_time = 0
            entry_length = entry[1] + adjust
            self.entries += [entry_time, entry_length]

    def trunc_time(self, entry):
        time_trunc = int(str(entry).zfill(6)[-2:])
        if time_trunc == 0 or time_trunc == 33 or time_trunc == 67:
            new_time = entry
        elif time_trunc == 99:
            new_time = entry + 1
        elif time_trunc < 33:
            new_time = int(str(entry)[:-2] + str(33))
        elif time_trunc < 67:
            new_time = int(str(entry)[:-2] + str(67))
        else:
            new_time = int(str(entry)[:-2] + str(99)) + 1
        return new_time

    def __str__(self):
        return f"{self.type} array with {int(len(self.entries)/self.modulo)} items"

class gh5_instrument_base(gh5_base_entry):
    def __init__(self, instrument, diff):
        super().__init__()
        self.instrument = instrument
        self.diff = diff
        self.skip_warning = "0"
        self.modulo = 2

    def weird_note(self, time, issue = "Weird note"):
        if self.skip_warning.lower() != "skip":
            print(f"{issue} found in {self.diff} {self.instrument} at {time}!\nContact me!")
            self.skip_warning = input("Should be fine to continue, though.\n\nPress Enter to continue or type 'skip' to skip future warnings: ")
        return

    def set_gh5_name(self):
        self.name = self.instrument.lower() + self.diff.lower() + self.type.lower().replace(" ", "")

    def __str__(self):
        return f"{self.diff} {self.instrument} {self.type} node containing {int(len(self.entries)/2)} items."

class gh5_star_note(gh5_instrument_base):
    def __init__(self, instrument, diff):
        super().__init__(instrument, diff)
        self.type = "Star Power"
        self.size = 6
        self.qb_string = "gh5_star_note"
        self.set_gh5_name()

class gh5_special_note(gh5_instrument_base):

    def __init__(self, instrument, diff, special_type):
        super().__init__(instrument, diff)
        self.type = special_type
        self.size = 8
        self.qb_string = f"gh5_{special_type.lower()}_note"
        self.set_gh5_name()


class gh5_instrument_note(gh5_instrument_base):
    def __init__(self, instrument, diff):
        super().__init__(instrument, diff)
        self.type = "Instrument"
        self.size = 8
        self.qb_string = "gh5_instrument_note"
        self.set_gh5_name()


    def add_entry(self, note_array, endian = "big"):
        if note_array == -1:
            return
        for enum, entry in enumerate(note_array):
            if enum % 2 == 0: # Time value
                self.entries.append(entry)
            else:
                prev_time = self.entries[-1]
                value_bin = '{0:032b}'.format(entry)
                green = value_bin[15]
                red = value_bin[14]
                yellow = value_bin[13]
                blue = value_bin[12]
                orange = value_bin[11]
                purple = value_bin[10]
                hopo_note = value_bin[9]
                green_sus = value_bin[8] # Sus notes are also accents on drums
                red_sus = value_bin[7]
                yellow_sus = value_bin[6]
                blue_sus = value_bin[5]
                orange_sus = value_bin[4]
                bit_3 = value_bin[3]
                double_kick = value_bin[2] # 2x drum note
                bit_1 = value_bin[1]
                bit_0 = value_bin[0]
                """if int(bit_3) or int(bit_1) or int(bit_0):
                    self.weird_note(self.entries[-1])"""

                length = value_bin[16:]
                """if prev_time == 249727 and self.name == "drumsexpertinstrument":
                    print("Test here")
                if self.name == "drumsexpertinstrument":
                    print("Test here")"""
                if self.instrument == "Drums":
                    """if not int(purple) and int(double_kick) and self.diff == "Expert":
                        self.weird_note(self.entries[-1], "2x note, but no 1x note")"""
                    notes_play = "0" + double_kick + purple + orange + blue + yellow + red + green
                    """if self.diff == "Expert":
                        print()"""
                else:
                    if int(double_kick):
                        self.weird_note(self.entries[-1], "Double kick note in non-drums instrument")
                    notes_play = "0"+hopo_note+purple+orange+blue+yellow+red+green
                sus_notes = "000" + orange_sus + blue_sus + yellow_sus + red_sus + green_sus
                bin_note = int(length+notes_play+sus_notes, 2)
                self.entries.append(bin_note)
                # raise Exception

    def __str__(self):
        return f"{self.diff} {self.instrument} {self.type} node containing {int(len(self.entries)/self.modulo)} items."

class gh5_cameras(gh5_base_entry):
    def __init__(self, convert = "gh5"):
        super().__init__()
        self.type = "Camera"
        self.autocut = []
        self.moment = []
        self.modulo = 3
        self.time_change = 0
        self.orig_time = 0
        self.sec_cam = 99
        self.convert = convert
        self.last_len = 0
        self.last_time = 0


    def add_entry(self, note_array, endian = "big"):
        for enum, entry in enumerate(note_array):
            if enum % 2 == 0: # Time value
                if entry != 0:
                    time_adj = entry-33
                else:
                    time_adj = 0
                time_adj = entry
                new_time = self.trunc_time(time_adj)
                self.autocut.append(new_time)
                self.orig_time = time_adj
                self.time_change = time_adj - new_time
                # self.autocut.append(entry)
            else:

                prev_time = self.autocut[-1]
                value_bin = '{0:032b}'.format(entry)
                velocity = value_bin[0:8]
                midi_note = value_bin[8:16]
                length = value_bin[16:]

                velocity_val = int(velocity, 2)
                midi_note_val = int(midi_note, 2)
                if self.convert == "gh5":
                    if midi_note_val >= 110 or midi_note_val == 2: # This is the "debug face cam" in GH5/BH/WoR resulting in an extreme closeup
                        self.autocut.pop()
                        continue # Since there are no post-process effects in GH5/BH/WoR, these will get deleted
                    if midi_note_val in range(40, 42):
                        print(f"Unsupported note {midi_note_val} found at {self.autocut[-1]}. Swapping cut for orbit")
                        midi_note_val = 74

                length_val_orig = int(length, 2) # - 33
                new_time = self.trunc_time(self.orig_time + length_val_orig)
                length_val = new_time - prev_time

                if str(length_val)[-1] == "4":
                    length_val -= 1
                elif str(length_val)[-1] == "6":
                    length_val += 1
                self.last_len = length_val
                self.last_time = self.orig_time
                #print()
                if midi_note_val < 7 or midi_note_val >= 90:
                    self.moment += [self.autocut[-1], length_val, midi_note_val]
                    self.autocut += [length_val, 31]
                elif midi_note_val in range(33,37):
                    self.moment += [prev_time, length_val, midi_note_val]
                    self.autocut += [length_val, gh5_camera_dict[midi_note_val]]
                else:
                    self.autocut += [length_val, midi_note_val]
        # print()

    def create_cam_dict(self):
        self.auto_dict = {}
        self.moment_dict = {}
        self.moment_cuts_used = []
        time = 0
        for count, x in enumerate(self.autocut):
            if count % 3 == 0:
                time = x
            elif count % 3 != 1:
                if not time in self.auto_dict:
                    self.auto_dict[time] = x
                else:
                    self.auto_dict[time] = [self.auto_dict[time]]
                    self.auto_dict[time].append(x)

        for count, x in enumerate(self.moment):
            if count % 3 == 0:
                time = x
            elif count % 3 != 1:
                if not time in self.moment_dict:
                    self.moment_dict[time] = x
                else:
                    self.moment_dict[time] = [self.moment_dict[time]]
                    self.moment_dict[time].append(x)
                if x not in self.moment_cuts_used:
                    self.moment_cuts_used.append(x)

    def set_secondary_cam(self, sec_cam):
        self.sec_cam = sec_cam
        new_moment = []
        for enum, moment in enumerate(self.moment):
            if enum % 3 == 2:
                if moment == 99:
                    new_moment.append(sec_cam)
                else:
                    new_moment.append(moment)
            else:
                new_moment.append(moment)
        self.moment = new_moment


    def __str__(self):
        return f"{self.type} array with {int(len(self.autocut)/self.modulo)} autocut and {int(len(self.moment)/self.modulo)} moment items"

class gh5_band_clip:
    def __init__(self, player, start, anim):
        self.name = player
        self.startnode = start
        self.anim = anim
        self.startframe = 0
        self.endframe = 0
        self.timefactor = 1
        if player == "guitarist" or player == "bassist":
            self.ik_targetl = "guitar"
            self.ik_targetr = "guitar"
        else:
            self.ik_targetl = "slave"
            self.ik_targetr = "slave"
        self.strum = "TRUE"
        self.fret = "TRUE"
        self.chord = "TRUE"

class MidiInsert:
    def __init__(self, data_tuple, tpb = 480):
        self.songTime = data_tuple[0]
        self.songSeconds = data_tuple[1]
        self.songTempo = data_tuple[2]
        self.songAvgTempo = data_tuple[3]
        self.tpb = tpb

    def set_seconds_array(self, seconds):
        self.secondsArray = seconds

    def set_ticks_array(self, ticks):
        self.ticksArray = ticks

    def get_seconds(self, curr_time):
        map_lower = self.ticksArray[self.ticksArray <= curr_time].max()
        arrIndex = self.songTime.index(map_lower)
        ticksFromChange = curr_time - self.songTime[arrIndex]
        timeFromChange = t2s(ticksFromChange, self.tpb, self.songTempo[arrIndex])
        true_time = timeFromChange + self.songSeconds[arrIndex]
        return int(round(true_time, 3)*1000)