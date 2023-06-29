@echo off

cd "D:\GitHub\Guitar-Hero-III-Tools\ska_converter"

REM Set the name of the PAK file as the first argument
set SONG_NAME=%1
set PAK_NAME=a%SONG_NAME%_song

REM Run the read_ska.py script
python read_ska.py

REM Copy files from out folder to Pak Input folder
xcopy out "D:\GitHub\Guitar-Hero-III-Tools\scratchpad\wt_test\walkthiswayrundmc\Compile\SKA Files" /E /I /Y


cd "D:\GitHub\Guitar-Hero-III-Tools\ska_converter"

echo Done.