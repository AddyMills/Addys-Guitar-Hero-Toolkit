pyinstaller -p "D:\GitHub\Guitar-Hero-III-Tools\create_audio" ^
-p D:\GitHub\Guitar-Hero-III-Tools\midqb_gen ^
-p D:\GitHub\Guitar-Hero-III-Tools\pak_extract ^
-p D:\GitHub\Guitar-Hero-III-Tools\ska_converter ^
-p D:\GitHub\Guitar-Hero-III-Tools ^
-p "D:\GitHub\Guitar-Hero-III-Tools\gui" ^
--add-data "anim_loops.txt;." ^
--add-data "debug.txt;." ^
--add-data "conversion_files_prod;conversion_files" ^
--add-data "create_audio\default_audio\blank.mp3;create_audio\default_audio" ^
"GH Toolkit.py"
pause