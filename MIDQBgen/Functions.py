from mido import tick2second as t2s
from Classes import *
import numpy as np
from definitions import *
from Sections import sections


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


def rollingAverage(x, y, z, a):  # x = prevTime, y = curTime, z = avgTempo, a = curTempo
    newTempo = ((x / y) * z) + (a * (y - x) / y)
    return newTempo


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


def timeInSecs(currChange, mid, time):
    return int(round(
        t2s(currChange.time, mid.ticks_per_beat, currChange.avgTempo) + t2s(time - currChange.time, mid.ticks_per_beat,
                                                                            currChange.tempo), 3) * 1000)


def parseGH3QB(mid, spNote=116):
    changes, ticks = tempMap(mid)

    ticksArray = np.array(ticks)
    changesArray = np.array(changes)

    GH2Tracks = ["PART GUITAR COOP", "PART RHYTHM", "TRIGGERS", "BAND BASS", "BAND DRUMS", "BAND SINGER", "BAND KEYS"]

    for x in mid.tracks:
        if x.name in GH2Tracks:
            spNote = 103
            break

    playTracksDict = {
        "PART GUITAR": "Guitar",
        "PART BASS": "Bass",
        "PART GUITAR COOP": "Guitar_Coop",
        "PART RHYTHM": "Rhythm_Coop"
    }

    playableQB = {
        "Guitar": {},
        "Bass": {},
        "Guitar_Coop": {},
        "Rhythm_Coop": {}
    }

    leftHandAnims = {
        "Guitar": [],
        "Bass": []
    }

    faceOffs = {
        "P1": [],
        "P2": []
    }

    drumNotes = []
    timeSigs = []
    markers = []
    fretbars = []

    for trackNum, track in enumerate(mid.tracks):
        diffs = {
            "Easy": [],
            "Medium": [],
            "Hard": [],
            "Expert": []
        }

        starPowerList = []

        starPowerDiffs = {
            "Easy": [],
            "Medium": [],
            "Hard": [],
            "Expert": []
        }

        starBM = {
            "Easy": [],
            "Medium": [],
            "Hard": [],
            "Expert": []
        }

        time = 0
        activeNote = {
            "Easy": 0,
            "Medium": 0,
            "Hard": 0,
            "Expert": 0
        }

        qbItems = []

        try:
            instrument = playTracksDict[track.name]
        except:
            print(f"Processing non-instrument track {track.name}")
        else:
            print(f"Processing instrument track {track.name}")
        for x in track:
            time += x.time
            currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
            timeSec = timeInSecs(currChange, mid, time)
            if trackNum == 0:
                if x.type == "time_signature":
                    timeSigs.append(timeSigEvent(timeSec, x.numerator, x.denominator))
            elif track.name == "EVENTS":
                if x.type == 'text':
                    # print(msg, timeSec)
                    if x.text.startswith("[section"):
                        markers.append(markerNode(timeSec, sections[x.text.split(" ")[1][:-1]].title()))
                    elif x.text.startswith("[prc_"):
                        markers.append(markerNode(timeSec, sections[x.text[1:-1]].title()))
                    elif x.text == '[end]':
                        endEvent = time
                        break
            elif track.name == "PART DRUMS":
                if x.type == "note_on":
                    if x.note in drumKeyMapRB.keys():
                        drumNotes.append(AnimNote(timeSec, drumKeyMapRB[x.note]))
            else:
                if x.type == "note_on":
                    if track.name in playTracksDict:
                        if x.velocity == 0:
                            if x.note in noteMapping:
                                chartDiff = noteMapping[x.note].split("_")[0]
                                noteColour = noteMapping[x.note].split("_")[1]
                                if activeNote[chartDiff] == 1:
                                    activeNote[chartDiff] = 0
                                    diffs[chartDiff][-1].setLength(timeSec - diffs[chartDiff][-1].time,
                                                                   currChange.tempo,
                                                                   mid.ticks_per_beat)

                            elif x.note == spNote:
                                starPowerList[-1].setLength(timeSec - starPowerList[-1].time)
                            elif instrument == "Guitar":
                                if x.note in faceOffMapping:
                                    faceOffs[faceOffMapping[x.note]][-1].setLength(
                                        timeSec - faceOffs[faceOffMapping[x.note]][-1].time - 1)
                            elif instrument != "Guitar_Coop":
                                if x.note in leftHandMappingGtr:
                                    if instrument == "Rhythm_Coop":
                                        leftIns = "Bass"
                                    else:
                                        leftIns = instrument
                                    leftHandAnims[leftIns][-1].setLength(timeSec - leftHandAnims[leftIns][-1].time)
                        else:
                            if x.note in noteMapping:
                                chartDiff = noteMapping[x.note].split("_")[0]
                                noteColour = noteMapping[x.note].split("_")[1]

                                if not diffs[chartDiff]:  # Check for empty note array and adds a note
                                    diffs[chartDiff].append(Note(timeSec))
                                    activeNote[chartDiff] = 1
                                elif diffs[chartDiff][
                                    -1].time != timeSec:  # Check if the note shows up at the same time as the previous note
                                    if activeNote[
                                        chartDiff] == 1:  # If a note has already been placed before a note_off event occured
                                        if timeSec - diffs[chartDiff][
                                            -1].time <= 16:  # Broken chord check. If the note is within 16ms (approx 1/60, i.e. one frame) assume it's part of the same note as before
                                            setattr(diffs[chartDiff][-1], noteColour, 1)
                                        else:  # If not, it's assumed to be a new note. Old note gets cut off at the time stamp and new note is created
                                            diffs[chartDiff][-1].setLength(timeSec - diffs[chartDiff][-1].time,
                                                                           currChange.tempo,
                                                                           mid.ticks_per_beat)
                                            diffs[chartDiff].append(Note(timeSec))
                                            activeNote[chartDiff] = 1
                                    else:  # If no note is currently active at this note_on event, create one.
                                        diffs[chartDiff].append(Note(timeSec))
                                        activeNote[chartDiff] = 1
                                if noteColour in colours:
                                    setattr(diffs[chartDiff][-1], noteColour, 1)
                            if x.note == spNote:
                                if not starPowerList:
                                    starPowerList.append(StarPower(timeSec))
                                elif starPowerList[-1].time != timeSec:
                                    starPowerList.append(StarPower(timeSec))
                            if instrument == "Guitar":
                                if x.note in leftHandMappingGtr:
                                    if not leftHandAnims[instrument]:
                                        leftHandAnims[instrument].append(AnimNote(timeSec, leftHandMappingGtr[x.note]))
                                    elif leftHandAnims[instrument][-1].time != timeSec:
                                        leftHandAnims[instrument].append(AnimNote(timeSec, leftHandMappingGtr[x.note]))
                                if x.note in faceOffMapping:
                                    if not faceOffs[faceOffMapping[x.note]]:
                                        faceOffs[faceOffMapping[x.note]].append(FaceOffSection(timeSec))
                                    elif faceOffs[faceOffMapping[x.note]][-1].time != timeSec:
                                        faceOffs[faceOffMapping[x.note]].append(FaceOffSection(timeSec))
                            if instrument == "Bass" or instrument == "Rhythm_Coop":
                                if x.note in leftHandMappingBass:
                                    if not leftHandAnims["Bass"]:
                                        leftHandAnims["Bass"].append(AnimNote(timeSec, leftHandMappingBass[x.note]))
                                    elif leftHandAnims["Bass"][-1].time != timeSec:
                                        leftHandAnims["Bass"].append(AnimNote(timeSec, leftHandMappingBass[x.note]))

                elif x.type == "note_off":
                    if track.name in playTracksDict:
                        if x.note in noteMapping:
                            chartDiff = noteMapping[x.note].split("_")[0]
                            noteColour = noteMapping[x.note].split("_")[1]
                            if activeNote[chartDiff] == 1:
                                activeNote[chartDiff] = 0
                                diffs[chartDiff][-1].setLength(timeSec - diffs[chartDiff][-1].time, currChange.tempo,
                                                               mid.ticks_per_beat)

                        if x.note == spNote:
                            starPowerList[-1].setLength(timeSec - starPowerList[-1].time)
                        if instrument == "Guitar":
                            if x.note in faceOffMapping:
                                faceOffs[faceOffMapping[x.note]][-1].setLength(
                                    timeSec - faceOffs[faceOffMapping[x.note]][-1].time - 1)
                        if instrument != "Guitar_Coop":
                            if x.note in leftHandMappingGtr:
                                leftHandAnims[instrument][-1].setLength(timeSec - leftHandAnims[instrument][-1].time)

        for x in diffs:
            spCounter = 0
            for y in diffs[x]:
                if not starPowerDiffs[x]:
                    try:
                        starPowerDiffs[x].append(
                            StarPowerPhrase(starPowerList[spCounter].time, starPowerList[spCounter].length))
                    except:
                        print(f"No Star Power found for track {track.name} on {x} difficulty")
                        break
                if y.time >= starPowerList[spCounter].time and y.time <= starPowerList[spCounter].time + starPowerList[
                    spCounter].length:
                    starPowerDiffs[x][-1].incNotes()
                    # print(spCounter, x, y, len(starPowerList))
                elif y.time > starPowerList[spCounter].time + starPowerList[spCounter].length:
                    if len(starPowerList) == spCounter + 1:
                        pass
                    else:
                        while y.time > starPowerList[spCounter].time + starPowerList[spCounter].length:
                            spCounter += 1
                            starPowerDiffs[x].append(
                                StarPowerPhrase(starPowerList[spCounter].time, starPowerList[spCounter].length))

        if track.name in playTracksDict:
            for x in diffs:
                playableQB[instrument][x] = Difficulty(x, instrument, diffs[x], starPowerDiffs[x], starBM[x])
    # print(playableQB)

    time = 0
    currTS = 0
    numer = timeSigs[currTS].numerator
    denom = timeSigs[currTS].denominator
    # print(numer, denom)
    currTS += 1
    while time < endEvent:
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

    for x in playableQB:
        for i, y in enumerate(playableQB[x]):
            for j, z in enumerate(playableQB[x][y].song):
                if j != 0:
                    prev = playableQB[x][y].song[j - 1]
                    if z.time == prev.time + prev.length:
                        prev.noNoteTouch()
                        # print(y, z.time, prev.time + prev.length)

    return {"playableQB": playableQB, "drumNotes": drumNotes, "timesig": timeSigs, "markers": markers,
            "fretbars": fretbars, "leftHandAnims": leftHandAnims, "faceOffs": faceOffs}
