# Guitar Hero III Tools
 
A WIP toolkit to create more legitimate-looking Guitar Hero III customs

## Introduction

I've always enjoyed Guitar Hero III, but the customs scene is, for a lack of a better word, lacking. The only thing you get is the note charts (maybe face off sections) and star power. You are stuck with looping animations, an idle singer and drummer, random camera cuts, and no venue animations.

These tools, while in its infancy, plan to start fixing this aspect of the customs scene.

There is now just one executable for all available functions. This program will be updated to include more functions as time goes, but it'll allow you to just use one executable:



The image above explains the functions. You can either use beginner mode, or advanced mode. Beginner mode is activated when starting the program without any arguments (i.e. just double clicking on the executable). It'll confirm you want to start in beginner mode, and then you can use the step-by-step instructions to perform your tasks.

Advanced mode is actiavated by calling the program and giving it arguments. The first argument always needs to be the function (make_midi, pak_extract, etc.) followed by the file you want to process. You can also type the following modifers **after** the input file:

*  -o: Specify an output folder
*  -hopo: Specify the HO/PO threshold in ticks (default is 170) -- For *make_midi* only.

## Make MIDI

The first tool is a MIDI parser. This will take a Rock Band style MIDI file and, in addition to giving you all the playable stuff you get with GHTCP, give you a game file that has left-hand animations, and drumming animations.

Note: In order for drum animations to show up, the input MIDI must have drum animations charted as per Rock Band's specifications.

How to use:

This program is for GH3 PC only and you will need GHTCP to use this tool for now.

*  Create a custom with your RB MIDI in GHTCP and remember the "short name" you made. This is the name found on the left-hand side, once created. 

![image](https://user-images.githubusercontent.com/74471839/193481392-baa1b954-bb82-4f74-b890-2b422cda14d9.png)
*  Rename the RB MIDI file to your "short name" (in my case it's "youshouldbeashamed.mid"), with the same case. If any part of the name is different, this will not work.
*  For Beginner Mode:
   * After starting Beginner Mode, choose option 1
   * Drag in your MIDI file and hit enter
   * Your compiled PAK file will be in the same directory as your MIDI file
*  For Advanced Mode:
   * Call the program with *make_midi* as it's first argument and your MIDI file as its second
   * Optional: Use *-o* to specify an output folder
   * Optional: Use *-hopo* afterwards to override the default HO/PO threshold (see the list below)

*  Simply copy and paste the PAK file into your SONGS folder
*  Play your song

A GH2 style MIDI will also work. However, since there are no drum animations found inside those MIDIs, there will not be any animations made for him. The left-hand stuff will work though!

Forcing HO/POs using the notes directly above the playable notes as in RB, including on Medium and Easy if you wanted to. The script will assume you're using a 170 ho/po threshold like RB, but that can be overridden if you're using a different HOPO setting in GHTCP.

When adding songs to GHTCP, it's highly recommended to use a slightly different HO/PO threshold of 2.8 or 2.85 (technically 2.8235, but GHTCP only allows you to set it in increments of 0.05. You can change this using QueenBee for now if you really want to get precise). The way GH3 calculates hopos is using the following formula: 1/(4\*x). Any note slower than this number will result in a strummed note. The default is 2.95. 1/(4\*2.95) is 11.8 so slightly slower than 1/12th note. HMX's default of 170 converts to roughly 11.3 which I find is better. Fast BPM 8th triplets will sometimes have strummed notes in there using the default GH3 HO/PO value.
![image](https://user-images.githubusercontent.com/74471839/193668661-b96636b7-19f0-4211-a2e7-3f73fbbb4c9e.png)

Common HMX thresholds and their NS counterparts to enter in GHTCP:
|HMX Ticks|NS HOPO value|Largest HOPO Distance|
|:----------:|:----------:|:------:|
|250|1.92|8th Note|
|170|2.8235|8th Triplet (12th note)|
|130|3.6923|16th Note|
|90|5.3333|16th Triplet (24th Note)|

### Venues
As of V0.5, you can now add a MIDI track to your MIDI to create a custom lightshow and camera cuts! A full guide will come soon(tm), but here's a summary for now.

To take advantage of this, you'll need to create a new MIDI track named "GH3 VENUE" (make sure you also create a "Track Name" event inside this MIDI track!)

You can use the Reaper templates in the repo to figure out where to place notes. 

For cameras (notes 79-117), simply place notes where you want cuts. Some cuts last longer than others, but there's generally no harm in having as little or many camera cuts in a song. The names can be a bit confusing as these are the internal names. I will update the names in a future update to make them more clear.

Lights in GH3 is a bit more complicated. 

I'll start with the "mood" notes. These are different lighting presets. All except blackout and flare have multiple states. Of the ones that have multiple states, strobe gets toggled using note 60, and the others with 57 and 58. Think of these as your *next* and *previous* events in Rock Band venues. Strobe does not have a preset speed like in RB. Note 60 turns the lights on or off when it's called.

The light override notes will change the colour of the current mood, except for blackout and flare. These are unaffected by the override. The rest of the moods will all change, even strobe!

56 is the pyro note. It's similar to the *bonusfx* event in RB. If you want a long lasting pyro like in "My Curse", you can keep calling it every quarter note or so until you want them to be done.

Notes 39-53 control the speed at which lights blend into each other. The blending starts when a mood or lighting override is called. For example, if you have your lighting blend set to 200ms, and you then call a flare, it will take 200ms from the note before the stage is fully set to the flare mood.

Lighting blend notes must be called before the mood or light override note (it can even be as little as 1ms, but it needs to be placed before). If a blend note is placed the same time as a mood note, the blend won't activate until the next mood/colour note.

You can also cancel blends. If you have a blend of 700ms, and at 300ms into the blend place a blend note of 0ms followed by a light note before the initial 700ms are up, the blend gets cancelled and it cuts to your note immediately. "My Curse" uses this effect during the part of the song where the band comes in.

Blends lasting longer than 1 second are not yet possible with this tool, but it is possible to do in the engine. This functionality will hopefully come in the near future.

For an example of both venue tracks, please see my "example.mid" in the Reaper template folder. It is the MIDI file I used for my video here: 

[![Venue Showoff](http://img.youtube.com/vi/7_Wd9ZNnqLA/0.jpg)](http://www.youtube.com/watch?v=7_Wd9ZNnqLA "Custom Cameras and Lightshow")

## Extract PAK

*extract_pak* will take in a PAK file and extract all the files inside. If using beginner mode, it'll extract it to the same folder as your input in an "extract" folder, and in advanced mode it can be specified where it saves (if no folder is specified, it'll follow the same logic as beginner mode)

For files that have .PAB files (such as qb.pak, or global.pak), you just need to point the program to the .PAK file and have the .PAB file in the same folder. It'll read it automatically.

## QB2Text

*qb2text* will take in a .qb file and attempt to convert it to a text file for easy editing. It won't work on *every* qb file yet (but is guaranteed to work on songlist, store_data, and guitar_download), but if there's one that you really want to edit that fails, please let me know, and I can work on implementing it.

## Text2QB

*text2qb* will take in a .txt file and attempt to convert it to a qb file for use in-game.

## Roadmap

There are a lot of things that can be added to this program. Here is what I plan to include at some point:

### Completed

*  Create a guitar and bass note chart directly from a MIDI without converting to chart first
*  Create your own GH3 style venue with an added MIDI track called "GH3 VENUE".
*  Drummer animations from the PART DRUMS track in the MIDI
*  Harmonix-style HO/POs by default (if a single note follows a chord containing that note, it'll never be a HO/PO unless forced)
*  Left-hand animations for both instrument parts
*  Light blending times of longer than 1 second using the game's scripting functionality
*  QB parser to allow quick edits a la DTA editing in HMX games (beta, should work for most qb files, will need QueenBee to re-insert into the game for now)
*  RB's forced notes, either on or off
*  Read Face-off sections
*  Read Star Power Phrases

### Very soon

*  Create GH3-compatible audio
*  Create a MIDI file from a song.PAK file (with venues, drum animations, etc.)
*  Create a PAK compiler
*  Custom sections with spaces and without abbreviations. Currently, only sections found in HMX style games will have nicely formatted names in the "More Stats" screen. If there's a custom section in your song, it'll just be called the name of the text event (without "section" or "prc_") in-game with the underscores.
*  Make an icon for the executable
*  Utilize the in-game count off notes

### Further off

*  Automatically create a song package and add it to the game
*  Autogen a venue based off of an RB3 style venue
*  Autogen a venue based off of an RB1/2 style venue
*  Create Battle Mode Stars

### Way off

*  Nothing for now

### Probably won't happen, but who knows?

*  Create singer mouth movements
