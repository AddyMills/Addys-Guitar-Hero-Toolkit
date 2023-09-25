import subprocess
import sys
import os
import shutil


root_folder = os.path.realpath(os.path.dirname(__file__))
args = sys.argv
toolkit_path = os.path.join(root_folder, "GH Toolkit.py")
subprocess.run(["python", toolkit_path, *sys.argv[1:]])