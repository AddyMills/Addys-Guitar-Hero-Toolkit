@echo off

cd "D:\GitHub\Guitar-Hero-III-Tools\ska_converter"

REM Set the name of the PAK file as the first argument
set SONG_NAME=%1
set PAK_NAME=a%SONG_NAME%_song

REM Run the read_ska.py script
python read_ska.py

REM Copy files from out folder to Pak Input folder
xcopy out "D:\GitHub\Guitar-Hero-III-Tools\midqb_gen\Pak Input\" /E /I /Y

REM Run the CreatePAK.py script with arguments
cd "D:\GitHub\Guitar-Hero-III-Tools\midqb_gen"
python CreatePAK.py -pak_name %PAK_NAME% no_check

REM Copy the generated PAK file to the destination folder
copy "PAK compile\%PAK_NAME%.pak.xen" "C:\Program Files (x86)\Aspyr\Guitar Hero World Tour\DATA\MODS\%SONG_NAME%\Content\"

cd "D:\GitHub\Guitar-Hero-III-Tools\ska_converter"

echo Done.