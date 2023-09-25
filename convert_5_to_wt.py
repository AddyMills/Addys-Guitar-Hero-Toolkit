import subprocess
import os
import shutil

pak_name = os.path.basename(input("Drag in your pak file: ")).replace("\"","")
root_folder = os.path.realpath(os.path.dirname(__file__))
perf = "_performance.txt" if os.path.isfile("_performance.txt") else ""
scripts = "_song_scripts_anim_loops.txt" if os.path.isfile("_song_scripts_anim_loops.txt") else ""
ska_files = "SKA Files" if os.path.isdir("SKA Files") else ""

toolkit_path = os.path.join(root_folder, "GHToolkit.py")
subprocess.run(["python", toolkit_path, "convert_5_to_wt", pak_name, perf])