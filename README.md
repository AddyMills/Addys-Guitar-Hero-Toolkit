# Guitar Hero III Tools
 
A WIP toolkit to create more legitimate-looking Guitar Hero III customs

## Introduction

I've always enjoyed Guitar Hero III, but the customs scene is, for a lack of a better word, lacking. The only thing you get is the note charts (maybe face off sections) and star power. You are stuck with looping animations, an idle singer and drummer, random camera cuts, and no venue animations.

These tools, while in its infancy, plan to start fixing this aspect of the customs scene.

## MidQBGen

My first released tool is a MIDI parser so far called "MidQBGen". This will take a Rock Band style MIDI file and, in addition to giving you all the playable stuff you get with GHTCP, give you a game file that has left-hand animations, and drumming animations.

Note: In order for drum animations to show up, the input MIDI must have drum animations charted as per Rock Band's specifications.

How to use:

This program is for GH3 PC only and you will need GHTCP to use this tool for now.

*  Create a custom with your RB MIDI in GHTCP and remember the "short name" you made. This is the name found on the left-hand side, once created. 

![image](https://user-images.githubusercontent.com/74471839/193481392-baa1b954-bb82-4f74-b890-2b422cda14d9.png)
*  Rename the RB MIDI file to your "short name" (in my case it's "youshouldbeashamed.mid"), with the same case. If any part of the name is different, this will not work.
*  Drag the MIDI file onto the executable.
*  A PAK file will be generated. Simply copy and paste this PAK file into your SONGS folder
*  Play your song

A GH2 style MIDI will also work. However, since there are no drum animations found inside those MIDIs, there will not be any animations made for him. The left-hand stuff will work though!

Forcing HO/POs using the notes directly above the playable notes as in RB, including on Medium and Easy if you wanted to. The script will assume you're using a 170 ho/po threshold like RB, but that can be overridden if you're using a different HOPO setting in GHTCP. To change the logic of the script with a different threshold, simply add the hopo threshold in ticks after calling the script and mid. For example "MidQbGen greengrassreal.mid 250" will handle the midi as if the hopo threshold was set to 250 in-game. If a note is forced on and off, the forcing will be ignored entirely.

When adding songs to GHTCP, it's highly recommended to use a slightly different HO/PO threshold of 2.8 or 2.85 (technically 2.8235, but GHTCP only allows you to set it in increments of 0.05. You can change this using QueenBee for now if you really want to get precise). The way GH3 calculates hopos is using the following formula: 1/(4\*x). Any note slower than this number will result in a strummed note. The default is 2.95. 1/(4\*2.95) is 11.8 so slightly slower than 1/12th note. HMX's default of 170 converts to roughly 11.3 which I find is better. Fast BPM triplets will sometimes have strummed notes in there using the default GH3 HO/PO value.
![image](https://user-images.githubusercontent.com/74471839/193668661-b96636b7-19f0-4211-a2e7-3f73fbbb4c9e.png)


## Roadmap

There are a lot of things that can be pulled from an RB MIDI that can be used inside a GH3 song. Here is what I plan to include at some point:

### Completed

*  Create a guitar and bass note chart directly from a MIDI without converting to chart first
*  Read Star Power Phrases
*  Read Face-off sections
*  Drummer animations
*  Left-hand animations for both instrument parts
*  Implement RB's forced notes, either on or off

### Very soon

*  Utilize the in-game count off notes
*  Add an option to create GH2-style HO/POs. Currently if a single note of one colour comes after a chord containing that colour, it's a HO/PO in GH3 while it's not in HMX style games. This feature would automatically add HO/PO force markers to those single notes to make them strummed
*  Allow you to create your own GH3 style venue with an added MIDI track called "GH3 Venue". There will also be a guide created for this.
*  Custom sections with spaces and without abbreviations. Currently, only sections found in HMX style games will have nicely formatted names in the "More Stats" screen. If there's a custom section in your song, it'll just be called the name of the text event (without "section" or "prc_") in-game with the underscores.

### Further off

*  Autogen a venue based off of an RB3 style venue
*  Autogen a venue based off of an RB1/2 style venue
*  Create Battle Mode Stars
*  Create GH3-compatible audio

### Way off

*  Automatically create a song package and add it to the game
*  Create a PAK/QB parser to allow quick edits a la DTA editing in HMX games

### Probably won't happen, but who knows?

*  Create singer mouth movements
