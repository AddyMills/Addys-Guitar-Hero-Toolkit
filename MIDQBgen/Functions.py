from mido import tick2second as t2s
from Classes import *
import numpy as np
from definitions import *
from Sections import sections
import CRC


def createHeaderDict(filename):
    headers = []
    headerDict = {}
    for x in playableParts:
        for z in charts:
            for y in difficulties:
                if z == "song":
                    if x == "":
                        headers.append(f"{filename}_{z}_{y}")
                    else:
                        headers.append(f"{filename}_{z}_{x}_{y}")
                else:
                    if x == "":
                        headers.append(f"{filename}_{y}_{z}")
                    else:
                        headers.append(f"{filename}_{x}_{y}_{z}")

    for x in others:
        headers.append(f"{filename}{x}")

    for x in headers:
        headerDict[x] = CRC.QBKey(x)

    return headerDict


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


def parseGH3QB(mid, hopoThreshold, hmxmode = 1, spNote=116):
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

    cameraNotes = []
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
        forcing = {
            "Easy": {"force_on": 0, "force_off": 0},
            "Medium": {"force_on": 0, "force_off": 0},
            "Hard": {"force_on": 0, "force_off": 0},
            "Expert": {"force_on": 0, "force_off": 0}
        }
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
                        try:
                            markers.append(markerNode(timeSec, sections[x.text.split(" ")[1][:-1]].title()))
                        except:
                            markers.append(markerNode(timeSec, x.text.split(" ")[1].title()))
                    elif x.text.startswith("[prc_"):
                        try:
                            markers.append(markerNode(timeSec, sections[x.text[1:-1]].title()))
                        except:
                            markers.append(markerNode(timeSec, x.text[1:-1].title()))
                    elif x.text == '[end]':
                        endEvent = time
                        break
            elif track.name == "GH3 CAMERA":
                if x.type == "note_on":
                    if x.note in valid_camera_notes:
                        if x.velocity != 0:
                            if len(cameraNotes) >= 1:
                                cameraNotes[-1].setLength(timeSec - cameraNotes[-1].time)
                            cameraNotes.append(AnimNote(timeSec, x.note))
            elif track.name == "PART DRUMS":
                if x.type == "note_on":
                    if x.note in drumKeyMapRB.keys():
                        if x.velocity != 0:
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
                            elif x.note in forceMapping:
                                chartDiff = forceMapping[x.note].split("_")[0]
                                forceType = "force_" + forceMapping[x.note].split("_")[1]
                                forcing[chartDiff][forceType] = 0
                                if diffs[chartDiff]:
                                    if timeSec == diffs[chartDiff][-1].time:
                                        setattr(diffs[chartDiff][-1], forceType, 0)
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
                                    diffs[chartDiff].append(Note(timeSec, 0, currChange))
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
                                            diffs[chartDiff].append(Note(timeSec, diffs[chartDiff][-1], currChange))
                                            activeNote[chartDiff] = 1
                                    else:  # If no note is currently active at this note_on event, create one.
                                        diffs[chartDiff].append(Note(timeSec, diffs[chartDiff][-1], currChange))
                                        activeNote[chartDiff] = 1
                                if noteColour in colours:
                                    setattr(diffs[chartDiff][-1], noteColour, 1)
                                if "forceType" in locals():
                                    if forcing[chartDiff][forceType] == 1:
                                        setattr(diffs[chartDiff][-1], forceType, 1)
                            if x.note in forceMapping:
                                chartDiff = forceMapping[x.note].split("_")[0]
                                forceType = "force_" + forceMapping[x.note].split("_")[1]
                                forcing[chartDiff][forceType] = 1
                                if diffs[chartDiff]:
                                    if timeSec == diffs[chartDiff][-1].time:
                                        setattr(diffs[chartDiff][-1], forceType, 1)
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
                        if x.note in forceMapping:
                            chartDiff = forceMapping[x.note].split("_")[0]
                            forceType = "force_" + forceMapping[x.note].split("_")[1]
                            forcing[chartDiff][forceType] = 0
                            if diffs[chartDiff]:
                                if timeSec == diffs[chartDiff][-1].time:
                                    setattr(diffs[chartDiff][-1], forceType, 0)
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
                for y in playableQB[instrument][x].song:
                    y.setForcing(hopoThreshold, mid.ticks_per_beat, hmxmode)

    # print(playableQB)
    if not "endEvent" in locals():
        raise Exception("Invalid MIDI: No [end] event found. Cannot parse MIDI.")
    if cameraNotes:
        cameraNotes[-1].setLength(endEvent - cameraNotes[-1].time)
        for x in cameraNotes:
            print(x)
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

    return {"playableQB": playableQB, "drums": drumNotes, "timesig": timeSigs, "markers": markers,
            "fretbars": fretbars, "leftHandAnims": leftHandAnims, "faceOffs": faceOffs, "cameras": cameraNotes}


def makeMidQB(midQB, filename, headerDict, consoleType):
    QBItems = []
    qbFileHeader = b'\x1C\x08\x02\x04\x10\x04\x08\x0C\x0C\x08\x02\x04\x14\x02\x04\x0C\x10\x10\x0C\x00'
    # print(midQB)

    for x in midQB["playableQB"]:
        QBChart = []
        QBStar = []
        QBStarBM = []
        # print(x)
        if not midQB["playableQB"][x]:
            for y in difficulties:
                instrument = x.replace("_", "").lower() if x != "Bass" else "rhythm"
                chartName = f"{filename}_song_{instrument}_{y}"
                starName = f"{filename}_{instrument}_{y}_Star"
                BMStarName = f"{filename}_{instrument}_{y}_StarBattleMode"
                QBChart.append(
                    QBItem("ArrayInteger", chartName, headerDict[chartName], [], consoleType))
                QBStar.append(QBItem("ArrayArray", starName, headerDict[starName], [], consoleType))
                QBStarBM.append(QBItem("ArrayArray", BMStarName, headerDict[BMStarName], [], consoleType))

        for i, y in enumerate(midQB["playableQB"][x]):
            data = [midQB["playableQB"][x][y].song, midQB["playableQB"][x][y].star, midQB["playableQB"][x][y].starBM]
            if x == "Guitar":
                chartName = f"{filename}_song_{y}"
                starName = f"{filename}_{y}_Star"
                BMStarName = f"{filename}_{y}_StarBattleMode"
                QBChart.append(
                    QBItem("ArrayInteger", chartName, headerDict[chartName], data[0], consoleType))
                QBStar.append(QBItem("ArrayArray", starName, headerDict[starName], data[1], consoleType))
                QBStarBM.append(QBItem("ArrayArray", BMStarName, headerDict[BMStarName], data[2], consoleType))
            else:
                instrument = x.replace("_", "").lower() if x != "Bass" else "rhythm"
                chartName = f"{filename}_song_{instrument}_{y}"
                starName = f"{filename}_{instrument}_{y}_Star"
                BMStarName = f"{filename}_{instrument}_{y}_StarBattleMode"
                QBChart.append(
                    QBItem("ArrayInteger", chartName, headerDict[chartName], data[0], consoleType))
                QBStar.append(QBItem("ArrayArray", starName, headerDict[starName], data[1], consoleType))
                QBStarBM.append(QBItem("ArrayArray", BMStarName, headerDict[BMStarName], data[2], consoleType))

        for y in [QBChart, QBStar, QBStarBM]:
            for z in y:
                QBItems.append(z)

    # print(midQB["faceOffs"])
    for x in midQB["faceOffs"]:
        chartName = f"{filename}_FaceOff{x}"
        if not midQB["faceOffs"][x]:
            QBItems.append(QBItem("ArrayInteger", chartName, headerDict[chartName], [], consoleType))
        else:
            QBItems.append(QBItem("ArrayArray", chartName, headerDict[chartName], midQB["faceOffs"][x], consoleType))

    # Boss Battle Array
    for x in midQB["faceOffs"]:
        chartName = f"{filename}_BossBattle{x}"
        QBItems.append(QBItem("ArrayArray", chartName, headerDict[chartName], [], consoleType))

    # timesig (array), markers (struct), fretbars (integer)
    chartName = f"{filename}_timesig"
    QBItems.append(QBItem("ArrayArray", chartName, headerDict[chartName], midQB["timesig"], consoleType))
    chartName = f"{filename}_fretbars"
    QBItems.append(QBItem("ArrayInteger", chartName, headerDict[chartName], midQB["fretbars"], consoleType))
    chartName = f"{filename}_markers"
    QBItems.append(QBItem("ArrayStruct", chartName, headerDict[chartName], midQB["markers"], consoleType))

    P1count = 0
    P2count = 0
    mergedAnim = []
    while True:
        try:
            if midQB["leftHandAnims"]["Guitar"][P1count].time < midQB["leftHandAnims"]["Bass"][P2count].time:
                mergedAnim.append(midQB["leftHandAnims"]["Guitar"][P1count])
                P1count += 1
            else:
                mergedAnim.append(midQB["leftHandAnims"]["Bass"][P2count])
                P2count += 1
        except:
            if P1count == len(midQB["leftHandAnims"]["Guitar"]):
                mergedAnim += midQB["leftHandAnims"]["Bass"][P2count:]
            else:
                mergedAnim += midQB["leftHandAnims"]["Guitar"][P1count:]
            break

    misc = ["scripts", "anim", "triggers", "cameras", "lightshow", "crowd", "drums", "performance"]

    QBNotes = []
    QBScripts = []

    for x in misc:
        xscript = f"{filename}_{x}"
        xnote = f"{xscript}_notes"
        if x == "anim":
            QBNotes.append(QBItem("ArrayArray", xnote, headerDict[xnote], mergedAnim, consoleType))
        elif x == "drums" or x == "cameras":
            if not midQB[x]:
                QBNotes.append(QBItem("ArrayInteger", xnote, headerDict[xnote], [], consoleType))
            else:
                QBNotes.append(QBItem("ArrayArray", xnote, headerDict[xnote], midQB[x], consoleType))
        else:
            QBNotes.append(QBItem("ArrayInteger", xnote, headerDict[xnote], [], consoleType))
        QBScripts.append(QBItem("ArrayInteger", xscript, headerDict[xscript], [], consoleType))

    for x in QBNotes:
        QBItems.append(x)

    for x in QBScripts:
        QBItems.append(x)

    positionStart = 28

    qbbytes = bytearray()

    toBytes = lambda a, b=4: a.to_bytes(b, "big")
    updatePos = lambda a, b: a + b

    # binascii.hexlify(bytes("Intro Slow", "latin-1"), ' ', 1))
    # print(bytes("Intro Slow", "utf-8"))
    packname = f"songs/{filename}.mid.qb"
    for i, x in enumerate(QBItems):
        x.processData(consoleType)  # Convert data in classes to numbers for use

        sectionbytes = bytearray()

        # QB Item Header
        sectionbytes += toBytes(qbNodeHeaders["SectionArray"][consoleType])
        sectionbytes += toBytes(int(headerDict[x.name], 16))  # CRC of the header name
        sectionbytes += toBytes(int(QBKey(packname), 16))  # CRC of the mid.qb name (e.g. "songs\slowride.mid.qb")

        position = positionStart + len(sectionbytes)
        sectionbytes += toBytes(position + 8)  # +8 to account for the next 8 bytes
        sectionbytes += toBytes(0)  # Next Item = 0 for mid.qb

        sectionbytes += toBytes(x.qbType)
        if x.node == "ArrayInteger":
            sectionbytes += toBytes(x.itemcount)
            position = positionStart + len(sectionbytes)
            sectionbytes += toBytes(position + 4)  # List starts 4 bytes after where the offset is defined
            for y in x.data:
                if isinstance(y, Note):
                    sectionbytes += toBytes(y.time)
                    sectionbytes += toBytes(y.length)
                    sectionbytes += toBytes(int(y.binForm(), 2))
                else:
                    sectionbytes += toBytes(y)
        elif x.node == "ArrayArray":
            sectionbytes += toBytes(x.itemcount)
            position = positionStart + len(sectionbytes)
            liststart = position + 4  # To cover the 4 bytes that point to the start of list
            sectionbytes += toBytes(liststart)
            firstitem = position + 4 + (x.itemcount * 4)
            # print(firstitem)
            for j, y in enumerate(x.arraydata):  # Add all starts of array entries to the mid
                arraynodelength = 4 + 4 + 4 + (len(y) * 4)
                # print(arraynodelength)
                sectionbytes += toBytes(firstitem + (arraynodelength * j))
                # print(y)
            position = positionStart + len(sectionbytes)
            for y in x.arraydata:
                sectionbytes += toBytes(x.subarraytype)
                sectionbytes += toBytes(len(y))
                position = positionStart + len(sectionbytes) + 4
                sectionbytes += toBytes(position)
                for z in y:
                    sectionbytes += toBytes(z)
                position = positionStart + len(sectionbytes)
        elif x.node == "ArrayStruct":
            sectionbytes += toBytes(x.itemcount)
            position = positionStart + len(sectionbytes)
            liststart = position + 4  # To cover the 4 bytes that point to the start of list
            sectionbytes += toBytes(liststart)
            # sectionbytes += toBytes(0) * x.itemcount
            # print(firstitem)
            if "markers" in x.name:
                offsets = []
                markerBytes = bytearray()  # 4 for header_marker, 4 for "first item" in struct
                for y in x.arraydata:
                    # time
                    offsets.append(positionStart + len(sectionbytes) + 4 * x.itemcount + len(markerBytes))
                    markerBytes += toBytes(qbNodeHeaders["StructHeader"][consoleType])

                    position = positionStart + len(sectionbytes) + len(markerBytes) + 4 * x.itemcount
                    markerBytes += toBytes(position + 4)
                    markerBytes += toBytes(qbNodeHeaders["StructItemInteger"][consoleType])
                    markerBytes += toBytes(int(QBKey("time"), 16))
                    markerBytes += toBytes(y[0])  # Add the time of the marker
                    position = positionStart + len(sectionbytes) + len(markerBytes) + 4 * x.itemcount
                    markerBytes += toBytes(position + 4)

                    # marker
                    markerBytes += toBytes(qbNodeHeaders["StructItemStringW"][consoleType])
                    markerBytes += toBytes(int(QBKey("marker"), 16))
                    position = positionStart + len(sectionbytes) + len(markerBytes) + 4 * x.itemcount + 8
                    markerBytes += toBytes(position)
                    markerBytes += toBytes(0)
                    markername = y[1]
                    # print(markername, len(markername))
                    markernamebytes = bytes(markername, "latin-1")
                    for z in markernamebytes:
                        markerBytes += toBytes(z, 2)
                    markerBytes += toBytes(0, 2)
                    if len(markername) % 2 == 0:
                        markerBytes += toBytes(0, 2)
                for y in offsets:
                    sectionbytes += toBytes(y)
                sectionbytes += markerBytes
                # print(offsets)

        elif x.node == "Floats":
            sectionbytes += toBytes(0)
            sectionbytes += toBytes(0)
            # print(position)
            # print(position)
            # print(x.name, x.itemcount)
        # Add the section to the overall bytearray
        qbbytes += sectionbytes
        positionStart = 28 + len(qbbytes)

        # print(positionStart)

    # print(binascii.hexlify(qbbytes, ' ', 1))

    filesize = len(qbbytes) + 28
    fullqb = bytearray()
    fullqb += toBytes(0) + toBytes(filesize) + qbFileHeader + qbbytes

    return fullqb
