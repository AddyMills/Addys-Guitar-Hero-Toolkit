from mido import second2tick as s2t
from definitions import *
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
        if self.prev_note == 0:
            return

        value = self.getValue()
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


class NoteChart:
    def __init__(self, part, diff):
        self.part = part
        self.diff = diff
        self.notes = []

    def __str__(self):
        return f"Part {self.part if self.part != '' else 'Guitar'}, {self.diff}, {self.notes} in chart"


class AnimNote:
    def __init__(self, time, note):
        self.time = time
        self.note = note
        self.length = 1

    def __str__(self):
        return f"Anim note {self.note} at {self.time} lasting {self.length}"

    def setLength(self, length):
        if length != 1:
            self.length = length - 1
        else:
            self.length = length


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
                    arraydata.append([x.time, x.marker])
            self.arraydata = arraydata
            # print(self.arraydata)


    def __str__(self):
        return f"QB Item {self.name}, type {self.node}, CRC {''.join('{:02x}'.format(x) for x in self.hexname)}"