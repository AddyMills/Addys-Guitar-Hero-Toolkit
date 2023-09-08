pyinstaller -p ".\create_audio" ^
-p .\midqb_gen ^
-p .\pak_extract ^
-p .\ska_converter ^
-p . ^
-p ".\gui" ^
--add-data "anim_loops.txt;." ^
--add-data "debug.txt;." ^
--add-data "conversion_files_prod;conversion_files" ^
--add-data "create_audio\default_audio\blank.mp3;create_audio\default_audio" ^
"GH Toolkit.py"
pause