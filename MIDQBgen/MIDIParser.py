import mido

if "markers" in x.name:
    offsets = []
    markerBytes = bytearray()  # 4 for header_marker, 4 for "first item" in struct
    for y in x.arraydata:
        # time
        offsets.append(positionStart + len(sectionbytes))
        sectionbytes += toBytes(qbNodeHeaders["StructItemInteger"][consoleType])
        sectionbytes += toBytes(int(QBKey("time"), 16))
        sectionbytes += toBytes(y[0])  # Add the time of the marker
        position = positionStart + len(sectionbytes)
        sectionbytes += toBytes(position + 4)

        # marker
        sectionbytes += toBytes(qbNodeHeaders["StructItemStringW"][consoleType])
        sectionbytes += toBytes(int(QBKey("marker"), 16))
        position = positionStart + len(sectionbytes) + 8
        sectionbytes += toBytes(0)
        markername = y[1]
        markernamebytes = bytes(markername, "latin-1")
        for z in markernamebytes:
            sectionbytes += toBytes(z, 2)
        sectionbytes += toBytes(0, 2)
    print(offsets)
"""for x in faceOffs:
    for y in faceOffs[x]:
        print(y)"""

"""for x in leftHandAnims["Bass"]:
    print(x)"""

"""for x in playableQB:
    for y in playableQB[x]:
        for z in y.song:
            print(z)"""

"""for x in playableQB["Guitar"][3].song:
    print(x, x.time, x.time+x.length)"""

"""print(playableQB["Guitar"][3])"""

"""for x in playableQB:
    for y in playableQB[x]:
        print(y)"""

"""for track in toParse:
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

    faceOffs = {
        "P1": [],
        "P2": []
    }

    leftHandAnims = {
        "Guitar": [],
        "Bass": []
    }
    qbItems = []
    instrument = track.split(" ")[1].title()
    for x in mid.tracks[tracksDict[track]]:

        time += x.time
        currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
        timeSec = timeInSecs(currChange, mid, time)
        if x.type == "note_on":
            if x.note in noteMapping:
                chartDiff = noteMapping[x.note].split("_")[0]
                noteColour = noteMapping[x.note].split("_")[1]
                activeNote[chartDiff] = 1
                if not diffs[chartDiff]:
                    diffs[chartDiff].append(Note(timeSec))
                elif diffs[chartDiff][-1].time != timeSec:
                    diffs[chartDiff].append(Note(timeSec))
                if noteColour in colours:
                    setattr(diffs[chartDiff][-1], noteColour, 1)
            if x.note in leftHandMappingGtr:
                if not leftHandAnims[instrument]:
                    leftHandAnims[instrument].append(AnimNote(timeSec, leftHandMappingGtr[x.note]))
                elif leftHandAnims[instrument][-1].time != timeSec:
                    leftHandAnims[instrument].append(AnimNote(timeSec, leftHandMappingGtr[x.note]))
            if x.note == spNote:
                if not starPowerList:
                    starPowerList.append(StarPower(timeSec))
                elif starPowerList[-1].time != timeSec:
                    starPowerList.append(StarPower(timeSec))
            if instrument == "Guitar":
                if x.note in faceOffMapping:
                    if not faceOffs[faceOffMapping[x.note]]:
                        faceOffs[faceOffMapping[x.note]].append(FaceOffSection(timeSec))
                    elif faceOffs[faceOffMapping[x.note]][-1].time != timeSec:
                        faceOffs[faceOffMapping[x.note]].append(FaceOffSection(timeSec))

        elif x.type == "note_off":
            if x.note in noteMapping:
                chartDiff = noteMapping[x.note].split("_")[0]
                noteColour = noteMapping[x.note].split("_")[1]
                if activeNote[chartDiff] == 1:
                    activeNote[chartDiff] = 0
                    diffs[chartDiff][-1].setLength(timeSec - diffs[chartDiff][-1].time, currChange.tempo, mid.ticks_per_beat)
            if x.note in leftHandMappingGtr:
                leftHandAnims[instrument][-1].setLength(timeSec - leftHandAnims[instrument][-1].time)
            if x.note == spNote:
                starPowerList[-1].setLength(timeSec - starPowerList[-1].time)
            if instrument == "Guitar":
                if x.note in faceOffMapping:
                    faceOffs[faceOffMapping[x.note]][-1].setLength(
                        timeSec - faceOffs[faceOffMapping[x.note]][-1].time - 1)

    for x in diffs:
        spCounter = 0
        for y in diffs[x]:
            if not starPowerDiffs[x]:
                starPowerDiffs[x].append(
                    StarPowerPhrase(starPowerList[spCounter].time, starPowerList[spCounter].length))
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

    for x in diffs:
        qbItems.append(Difficulty(x, instrument, diffs[x], starPowerDiffs[x], starBM[x]))
    playableQB[instrument] = qbItems.copy()"""

"""time = 0
timeSigs = []

for x in mid.tracks[0]:
    time += x.time
    currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
    timeSec = timeInSecs(currChange, mid, time)
    if x.type == "time_signature":
        timeSigs.append(timeSigEvent(timeSec, x.numerator, x.denominator))

endEvent = 0
markers = []
time = 0
for msg in mid.tracks[tracksDict["EVENTS"]]:
    time += msg.time
    currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
    timeSec = timeInSecs(currChange, mid, time)
    if msg.type == 'text':
        #print(msg, timeSec)
        if msg.text.startswith("[section"):
            markers.append(markerNode(timeSec, sections[msg.text.split(" ")[1][:-1]].title()))
        elif msg.text.startswith("[prc_"):
            markers.append(markerNode(timeSec, sections[msg.text[1:-1]].title()))
        elif msg.text == '[end]':
            endEvent = time
            break
time = 0
currTS = 0
numer = timeSigs[currTS].numerator
denom = timeSigs[currTS].denominator
# print(numer, denom)
currTS += 1
fretbars = []
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

drumNotes = []
time = 0
for x in mid.tracks[tracksDict["PART DRUMS"]]:
    time += x.time
    currChange = changes[len(ticksArray[ticksArray <= time]) - 1]  # time, tempo, avgTempo
    timeSec = timeInSecs(currChange, mid, time)
    if x.type == "note_on":
        if x.note in drumKeyMapRB.keys():
            drumNotes.append(AnimNote(timeSec, drumKeyMapRB[x.note]))"""

"""for x in drumNotes:
    print("Drum", x)"""

"""for x in markers:
    print(x)"""

"""for x in playableQB:
    for y in playableQB[x]:
        print(y)"""

"""for x in starPowerDiffs:
    for y in starPowerDiffs[x]:
        print(x, y)"""

"""with open("drumNotes.txt", "w") as f:
    f.write("\tArrayArray\n")
    f.write("\t[\n")
    for x in mid.tracks[tracksDict["PART DRUMS"]]:
        time += x.time
        if x.type == "note_on":
            if x.note in drumKeyMapRB.keys():
                f.write("\t\tArrayInteger\n\t\t[\n")
                currChange = changes[len(ticksArray[ticksArray <= time])-1] # time, tempo, avgTempo
                f.write(f"\t\t\t{int(round(t2s(currChange.time, mid.ticks_per_beat, currChange.avgTempo) + t2s(time - currChange.time, mid.ticks_per_beat, currChange.tempo),3)*1000)}\n\t\t\t{drumKeyMapRB[x.note]}\n\t\t\t1\n\t\t]\n")
                # print(drumKeyMapRB[x.note], t2s(currChange.time, mid.ticks_per_beat, currChange.avgTempo) + t2s(time - currChange.time, mid.ticks_per_beat, currChange.tempo),ticksArray[ticksArray <= time].max(), time)
    f.write("\t]\n")"""

"""for y, x in enumerate(changes):
    print(t2s(x.time,480,x.avgTempo))"""
