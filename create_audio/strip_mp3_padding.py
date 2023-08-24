import subprocess
import os
import shutil

def delete_files_in_directory(directory_path):
   try:
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
       elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
     print("All files deleted successfully.")
   except OSError:
     print("Error occurred while deleting files.")

def main():
    try:
        delete_files_in_directory("output")
        subprocess.run(["python","audio_functions.py"])
        for filename in os.listdir("output"):
            print(filename)
            subprocess.run(["fsbext", "-M","-d","output", f"output\\{filename}"])
            if filename.endswith("_1.FSB"):
                new_folder = "drums"
            elif filename.endswith("_2.FSB"):
                new_folder = "playable"
            elif filename.endswith("_3.FSB"):
                new_folder = "non-playable"
            elif filename.lower().endswith("_preview.FSB"):
                new_folder = "preview"
            else:
                continue
            os.rename("output\\multichannel sound.mp3_channels", f"output\\{new_folder}")
        for filename in os.listdir("output"):
            if filename == "playable":
                modifier = 4
            elif filename == "non-playable":
                modifier = 7
            elif filename == "preview":
                modifier = 9
            else:
                continue
            for file in os.listdir(f"output\\{filename}"):
                audio_name = int(os.path.splitext(file)[0])
                audio_name += modifier
                shutil.copy(f"output\\{filename}\\{file}",f"output\\drums\\{audio_name}.mp3")
        for filename in os.listdir("output\\drums"):
            shutil.copy(f"output\\drums\\{filename}", f"input\\{filename}")
        delete_files_in_directory("output")
        subprocess.run(["combine_fsb.bat"])

    except Exception as e:
        raise e
        print(f"Error: {e}")
        os.system('pause')

if __name__ == "__main__":
    main()