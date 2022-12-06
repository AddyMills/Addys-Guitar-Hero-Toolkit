import sys
import os


sys.path.append(f"{os.getcwd()}\\pak_extract")
from pak_extract import PAKExtract, QB2Text, Text2QB

def get_rhythm_headers(song_name):
    rhythm_parts = []
    rhythm_dict = {}
    for x in PAKExtract.charts:
        for y in PAKExtract.difficulties:
            if x == "song":
                rhythm_parts.append(f"{song_name}_{x}_aux_{y}")
            else:
                rhythm_parts.append(f"{song_name}_aux_{y}_{x}")

    for x in rhythm_parts:
        rhythm_dict[x] = int(PAKExtract.QBKey(x), 16)

    return rhythm_parts, rhythm_dict

def get_track_type(track_name):
    diffs = ["Easy", "Medium", "Hard", "Expert"]
    instrument = ["guitarcoop", "rhythmcoop", "rhythm"]
    if(any(x in track_name for x in diffs)):
        for x in diffs:
            if x in track_name:
                if "Battle" in track_name:
                    track_type = "Battle"
                elif "Star" in track_name:
                    track_type = "Star"
                else:
                    track_type = "Notes"
                track_diff = x
                for y in instrument:
                    if y in track_name:
                        track_play = y
                        break
                    else:
                        track_play = "song"
                return {"instrument": track_play, "track_type": track_type, "difficulty": track_diff}
    else:
        return {"track_type": track_name[track_name.find("_")+1:]}

def pak2mid(pakmid, song_name):
    with open(pakmid, 'rb') as pak:
        mid_bytes = pak.read()
    song_files = PAKExtract.main(mid_bytes, "")
    for x in song_files:
        if "0x" in x['file_name']:
            file_name_scrubbed = x['file_name'].replace("\\", "")
            if file_name_scrubbed.endswith(".qb"):
                qb_string = f'songs/{song_name}.mid.qb'
                crc_name = int(PAKExtract.QBKey(f'songs/{song_name}.mid.qb'), 16)
                hex_name = int(file_name_scrubbed[:-3], 16)
                if crc_name == hex_name:
                    mid_qb = qb_string
                    mid_data_bytes = x['file_data']
        elif ".mid.qb" in x['file_name']:
            mid_qb = x['file_name'].replace("\\", "")
            mid_data_bytes = x['file_data']
    if "mid_data_bytes" not in locals():
        raise Exception("No MIDI data found in PAK file.")
    file_headers = QB2Text.createHeaderDict(song_name)
    file_header_keys = file_headers.keys()
    file_headers_hex = {}
    for x in file_headers.keys():
        file_headers_hex[hex(file_headers[x])] = x
    qb_sections = QB2Text.convert_qb_file(QB2Text.qb_bytes(mid_data_bytes), song_name, file_headers)

    return qb_sections, file_headers, file_headers_hex, song_files



if __name__ == "__main__":

    pass