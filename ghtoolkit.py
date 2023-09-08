import subprocess
import sys
import os
import shutil


root_folder = os.path.realpath(os.path.dirname(__file__))
args = sys.argv
subprocess.run(["python",f"{root_folder}\\GH Toolkit.py", *sys.argv[1:]])