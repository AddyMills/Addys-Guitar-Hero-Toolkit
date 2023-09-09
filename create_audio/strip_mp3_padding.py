import subprocess
import os
import shutil
import audio_functions as af

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

def main(in_folder = "input", fsb_loc = ""):
    if fsb_loc:
        fsbext = fsb_loc
    elif not shutil.which("fsbext"):
        input("fsbext is not found.\nPress Enter to continue...")
        return 0
    else:
        fsbext = "fsbext"
    if in_folder == "input":
        out_folder = "output"
    else:
        if not os.path.isdir(in_folder):
            print("Invalid folder. Aborting audio function.")
            return 0
        out_folder = os.path.join(os.path.dirname(in_folder),"audio_stripped")
        try:
            os.mkdir(out_folder)
        except:
            pass
    try:
        if in_folder == "input":
            delete_files_in_directory("output")
            subprocess.run(["python","audio_functions.py"])
        else:
            for filename in os.listdir(in_folder):
                crypted, fileout = af.crypt_files(in_folder, filename)
                with open(f"{out_folder}\\{fileout}", 'wb') as f:
                    f.write(crypted)
        for filename in os.listdir(out_folder):
            print(filename)
            subprocess.run([fsbext, "-M","-d",out_folder, f"{out_folder}\\{filename}"])
            if filename.endswith("_1.FSB"):
                new_folder = "drums"
            elif filename.endswith("_2.FSB"):
                new_folder = "playable"
            elif filename.endswith("_3.FSB"):
                new_folder = "non-playable"
            elif filename.lower().endswith("_preview.fsb"):
                new_folder = "preview"
            else:
                continue
            os.rename(f"{out_folder}\\multichannel sound.mp3_channels", f"{out_folder}\\{new_folder}")
        for filename in os.listdir(out_folder):
            if filename == "playable":
                modifier = 4
            elif filename == "non-playable":
                modifier = 7
            elif filename == "preview":
                modifier = 9
            else:
                continue
            for file in os.listdir(f"{out_folder}\\{filename}"):
                audio_name = int(os.path.splitext(file)[0])
                audio_name += modifier
                shutil.copy(f"{out_folder}\\{filename}\\{file}",f"{out_folder}\\drums\\{audio_name}.mp3")
        for filename in os.listdir(f"{out_folder}\\drums"):
            shutil.copy(f"{out_folder}\\drums\\{filename}", f"{in_folder}\\{filename}")
        delete_files_in_directory(f"{out_folder}")
        if in_folder == "input":
            subprocess.run(["combine_fsb.bat"])
        else:
            song_name = input("Enter the checksum for this song: ")
            af.test_combine(song_name, in_folder, out_folder)
    except Exception as e:
        raise e
        print(f"Error: {e}")
        os.system('pause')
    return 1

if __name__ == "__main__":
    main()