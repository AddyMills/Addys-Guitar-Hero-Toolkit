from LookupTable import binaryReverse as br
import time
import os
import sys
import subprocess
import re
import shutil
import sox
import json

from crypt_keys import ghwor_keys, ghwor_cipher
from struct import pack as floatPack, unpack as f_up
from time import gmtime, strftime
root_folder = os.path.realpath(os.path.dirname(__file__))
sys.path.append(f"{root_folder}\\..\\")
from CRC import QBKey
from Crypto.Cipher import AES
from Crypto.Util import Counter
from io import StringIO, BytesIO
import random

mp3_sampling = {
    "00": 44100,
    "01": 48000,
    "10": 32000
}

blank_48k_mp3 = b'\xFF\xFB\x94\x64\x51\x8F\xF0\x00\x00\x69\x00\x00\x00\x08\x00\x00\x0D\x20\x00\x00\x01\x00\x00\x01\xA4\x00\x00\x00\x20\x00\x00\x34\x80\x00\x00\x04\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x4C\x41\x4D\x45\x33\x2E\x31\x30\x30\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55'



def get_audio_duration_sox(input_file):
    # Get the input file duration
    duration_output = sox.file_info.duration(input_file)

    return duration_output

def pad_wav_file_sox(input_file, target_length, file_num = 0):
    print(f"Converting {os.path.basename(input_file)} to MP3")
    # Get the input file duration
    duration = get_audio_duration_sox(input_file)
    sample_rate = sox.file_info.sample_rate(input_file)
    # Calculate the required padding
    padding = target_length - duration

    # Set up SoX transform parameters
    tfm = sox.Transformer()
    transform_args = ["mp3"]
    if sample_rate != 48000:
        transform_args.append(48000)
    tfm.set_output_format(*transform_args)

    # Add the padding to the input file and convert it to an MP3
    if padding > 0:
        tfm.pad(end_duration=padding)
    # Run the sox command, save temp file, and re-read
    temp_dir = ".\\temp"
    temp_out = temp_dir + f"\\temp_{file_num}.mp3"

    try:
        os.mkdir(temp_dir)
    except:
        pass

    try:
        tfm.build_file(input_filepath=input_file, output_filepath=temp_out)
    except Exception as E:
        raise E

    with open(temp_out, "rb") as f:
        padded_mp3_data = f.read()

    return padded_mp3_data

def make_preview_sox(start_time, end_time):
    # Create SoX Combiner
    cbn = sox.Combiner()
    cbn.set_output_format("mp3", 48000)
    cbn.trim(start_time, end_time)
    cbn.fade(1.0, 1.0)
    cbn.vol(-7.0, "db")
    cbn.set_input_format(["mp3"]*9)

    # Run the sox command, save temp file, and re-read
    temp_dir = ".\\temp"
    temp_out = temp_dir + "\\temp.mp3"

    if os.path.exists(temp_out):
        os.remove(temp_out)

    audio_list = []
    for file in os.listdir(temp_dir):
        audio_list.append(temp_dir + "\\" + file)

    try:
        cbn.build(audio_list, temp_out, "mix")
    except Exception as E:
        raise E

    with open(temp_out, "rb") as f:
        preview_data = f.read()

    shutil.rmtree(temp_dir)

    return preview_data


def get_audio_duration_ffmpeg(input_file):
    command = [
        'ffprobe',
        '-v',
        'quiet',
        '-print_format',
        'json',
        '-show_format',
        '-i',
        input_file
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = json.loads(result.stdout)

    return float(output['format']['duration'])


def pad_wav_file_ffmpeg(input_file, target_length, file_num=0):
    print(f"Converting {os.path.basename(input_file)} to MP3")

    # Get the input file duration
    duration = get_audio_duration_ffmpeg(input_file)

    # Calculate the required padding
    padding = target_length - duration

    # Define output file
    temp_dir = ".\\temp"
    temp_out = temp_dir + f"\\temp_{file_num}.mp3"
    silent_file = temp_dir + "\\silent.mp3"

    try:
        os.mkdir(temp_dir)
    except:
        pass

    if padding > 0:
        # Use FFmpeg to add silence to the end of the audio
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo:d={padding}',
            '-acodec', 'libmp3lame', '-b:a', '128k', '-map_metadata', '-1', silent_file
        ], check=True)

        subprocess.run([
            'ffmpeg', '-y', '-i', input_file, '-ar', '48000', '-acodec', 'libmp3lame', '-b:a', '128k', '-map_metadata', '-1', temp_out
        ], check=True)

        with open(f"{temp_dir}\\temp_concat.txt", "w") as f:
            f.write(f"file temp_{file_num}.mp3\n")
            f.write(f"file silent.mp3\n")

        # Concatenate the input audio file and the silent audio file
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', f"{temp_dir}\\temp_concat.txt", '-c', 'copy', '-map_metadata', '-1',
            temp_out
        ], check=True)

        os.remove(f"{temp_dir}\\temp_concat.txt")
        os.remove(f"{temp_dir}\\silent.mp3")

    else:
        # Convert audio to mp3 with 48000 sample rate
        subprocess.run([
            'ffmpeg', '-y', '-i', input_file, '-ar', '48000', '-acodec', 'libmp3lame', '-b:a', '128k', '-map_metadata', '-1', temp_out
        ], check=True)

    # Read the padded mp3 file
    with open(temp_out, "rb") as f:
        padded_mp3_data = f.read()

    return padded_mp3_data

def make_preview_ffmpeg(start_time, end_time):
    # Set temp directory and output file
    temp_dir = ".\\temp"
    temp_out = temp_dir + "\\temp.mp3"

    if os.path.exists(temp_out):
        os.remove(temp_out)

    # Get a list of all audio files in temp directory
    audio_list = [os.path.join(temp_dir, file) for file in os.listdir(temp_dir)]

    trim_duration = end_time - start_time
    fade_duration = 1.0

    # Build filtergraph for mixing and trimming audio
    mix_filter = ''.join([f'[{i}:0]' for i in range(len(audio_list))]) + f'amix=inputs={len(audio_list)}:duration=first:dropout_transition=2:normalize=0[mixout]'
    # trim_filter = f'[mixout]atrim=start={start_time}:duration={trim_duration}[final]'
    trim_filter = f'[mixout]atrim=start={start_time}:duration={trim_duration},afade=t=in:st={start_time}:d=1,afade=t=out:st={start_time+trim_duration - 1}:d=1,volume=-7.0dB[final]'
    #trim_filter = f'[mixout]atrim=start={start_time}:duration={trim_duration},afade=t=in:ss=0:d={fade_duration},afade=t=out:st={trim_duration-fade_duration}:d={fade_duration}[final]'
    filtergraph = mix_filter + ';' + trim_filter

    command = ['ffmpeg']

    # Add each input file to the command
    for audio_file in audio_list:
        command.extend(['-i', audio_file])

    # Add the rest of the command
    command.extend([
        '-filter_complex', filtergraph, '-map', '[final]',
        '-ar', '48000', '-acodec', 'libmp3lame', '-b:a', '128k', '-map_metadata', '-1', temp_out
    ])

    try:
        # Run FFmpeg command
        subprocess.run(command, check=True)
    except Exception as E:
        raise E

    # Read the output file
    with open(temp_out, "rb") as f:
        preview_data = f.read()

    shutil.rmtree(temp_dir)

    return preview_data

def is_program_in_path(program_name):
    return shutil.which(program_name) is not None

def get_padded_audio(all_audio, shortname, start_time = 30, end_time = 60, *args):
    # Get the maximum length
    time_0 = time.time()
    encrypt = False
    if "encrypt" in args:
        encrypt = True
    max_length = 0
    extra_args = []
    print("Converting all files to MP3 and padding to the longest")
    if is_program_in_path("sox") and "ffmpeg" not in args:
        print("Using SoX to convert")
        for input_file in all_audio:
            duration = get_audio_duration_sox(input_file)
            max_length = max(max_length, duration)
        # Pad each input file and store the output in a list
        print(f"Padding all files to match the longest file ({strftime('%M:%S', gmtime(max_length))})")
        # Pad each input file and store the output in a list
        padded_mp3_data_list = []
        for enum, input_file in enumerate(all_audio):
            padded_mp3_data_list.append(pad_wav_file_sox(input_file, max_length, enum))
        preview = make_preview_sox(start_time, end_time)
    elif is_program_in_path("ffmpeg"):
        print("Using FFmpeg to convert")
        for input_file in all_audio:
            duration = get_audio_duration_ffmpeg(input_file)
            max_length = max(max_length, duration)
        # Pad each input file and store the output in a list
        padded_mp3_data_list = []
        for enum, input_file in enumerate(all_audio):
            padded_mp3_data_list.append(pad_wav_file_ffmpeg(input_file, max_length, enum))
        preview = make_preview_ffmpeg(start_time, end_time)
        stream_size = 0
        for x in padded_mp3_data_list:
            stream_size = max(len(pullMP3Frames(x)[0]), stream_size)
        extra_args.extend(["-stream_size", stream_size])
    elif "ffmpeg" in args:
        print("FFmpeg was asked to use, but cannot find it in PATH")
        return 0
    else:
        print("Could not find ffmpeg or SoX in PATH")
        return 0
    print("Creating Drum Audio")
    drum_files = createFSB4(padded_mp3_data_list[:4], f"{shortname}_1", encrypt, *extra_args)
    print("Creating Other Instruments Audio")
    inst_files = createFSB4(padded_mp3_data_list[4:7], f"{shortname}_2", encrypt, *extra_args)
    print("Creating Non-Playable Audio")
    song_files = createFSB4(padded_mp3_data_list[7:], f"{shortname}_3", encrypt, *extra_args)
    print("Creating Preview Audio")
    preview = createFSB4([preview], f"{shortname}_preview", encrypt)
    time_1 = time.time()

    print(f"Audio generation took {time_1-time_0} seconds")
    return drum_files, inst_files, song_files, preview

def flipBits(audio):
    return bytes(br[x] for x in audio)

def parse_dat(datfile, songname, extension = ".mp3"):
    audio_ends = ["guitar", "rhythm", "song", "crowd", "coop_guitar", "coop_rhythm", "coop_song", "preview"]
    audio_qb = [int(QBKey(f"{songname}_{name}"),16) for name in audio_ends]
    song_files = {}
    dat = BytesIO(datfile)
    file_count = int.from_bytes(dat.read(4), "big")
    filesize = int.from_bytes(dat.read(4), "big")

    for tracks in range(file_count):
        trackname = int.from_bytes(dat.read(4), "big")
        if trackname in audio_qb:
            trackname = f"{songname}_{audio_ends[audio_qb.index(trackname)]}{extension}"
        else:
            print(f"Unknown track found while parsing {songname}")
            trackname = -1
        fsb_index = int.from_bytes(dat.read(4), "big")
        song_files[fsb_index] = trackname
        dat.read(12)

    song_sorted = []
    for position in sorted(song_files.keys()):
        song_sorted.append(song_files[position])
    return song_sorted

def extract_fsb(fsb, filename = "", **kwargs):
    if fsb[0:3] != b'FSB':
        fsb = decrypt_file(fsb, filename)
    dat = False
    fsb = BytesIO(fsb)
    fsb_type = fsb.read(4)
    # print()
    if fsb_type == b'FSB3':
        try:
            dat = parse_dat(kwargs["datfile"], filename[:filename.find(".fsb")])
        except:
            pass
        file_count = int.from_bytes(fsb.read(4), "little")
        head_length = int.from_bytes(fsb.read(4), "little")
        data_length = int.from_bytes(fsb.read(4), "little")
        unk = int.from_bytes(fsb.read(2), "little")
        version = int.from_bytes(fsb.read(2), "little")
        flags = int.from_bytes(fsb.read(4), "little")
        data_start = head_length + fsb.tell()
        audio_files = {}
        audio_order = []
        for file in range(file_count):
            file_entry_length = int.from_bytes(fsb.read(2), "little")
            file_name = str(fsb.read(30).replace(b'\x00', b''), "utf-8")
            try:
                if dat[file] != -1:
                    file_name = dat[file]
            except:
                pass
            sample_length = int.from_bytes(fsb.read(4), "little")
            comp_length = int.from_bytes(fsb.read(4), "little")
            loop_start = int.from_bytes(fsb.read(4), "little")
            loop_end = int.from_bytes(fsb.read(4), "little")
            mode = int.from_bytes(fsb.read(4), "little")
            sample_rate = int.from_bytes(fsb.read(4), "little")
            volume = int.from_bytes(fsb.read(2), "little")
            pan = int.from_bytes(fsb.read(2), "little")
            priority = int.from_bytes(fsb.read(2), "little")
            channels = int.from_bytes(fsb.read(2), "little")
            min_distance = f_up("<f", fsb.read(4))
            max_distance = f_up("<f", fsb.read(4))
            var_freq = int.from_bytes(fsb.read(4), "little")
            var_vol = int.from_bytes(fsb.read(2), "little")
            var_pan = int.from_bytes(fsb.read(2), "little")
            audio_files[file_name] = {"size": comp_length}
            audio_order.append(file_name)
        fsb.seek(data_start)
        for fsb_audio in audio_order:
            audio_files[fsb_audio]["data"] = fsb.read(audio_files[fsb_audio]["size"])
        return audio_files

def crypt(audio, key):
    # Update the encryption key by repeating it
    # to match the length of the audio to be processed.
    repetitions = 1 + (len(audio) // len(key))
    key = key * repetitions
    key = key[:len(audio)]

    # XOR audio and key above and return the en/decrypted bytes
    return bytes([b ^ k for b, k in zip(audio, key)])

# Warriors of Rock encryption converted from FsbDecrypt.java by Quidrex
# https://www.fretsonfire.org/forums/viewtopic.php?t=60499

#It's incomplete and encryption does not yet work. Decryption should, though

def decrypt_wor(audio):
    if len(audio) < 0x800:
        return False

    iv = b'\x00' * 16
    cipher = AES.new(ghwor_keys[0], AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, "big")))
    footer = cipher.decrypt(audio[-0x800:])

    key = ghwor_keys[sum(footer[4:8]) & 0xFF]
    cipher = AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, "big")))
    decrypt = bytearray(len(audio) - 0x800)

    decrypt[:16] = cipher.decrypt(audio[:16])
    if decrypt[0:4] != b'FSB4':
        return False

    decrypt[16:] = cipher.decrypt(audio[16:-0x800])
    return decrypt

def encrypt_wor(decrypted_audio):
    if len(decrypted_audio) < 16:
        return False

    iv = b'\x00' * 16

    audio_key = ghwor_keys[sum(ghwor_cipher[4:8]) & 0xFF]
    audio_cipher = AES.new(audio_key, AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, "big")))

    encrypted_audio = audio_cipher.encrypt(decrypted_audio)

    footer_cipher = AES.new(ghwor_keys[0], AES.MODE_CTR, counter=Counter.new(128, initial_value=int.from_bytes(iv, "big")))

    b_footer = bytes(ghwor_cipher)

    enc_footer = footer_cipher.encrypt(b_footer)

    return encrypted_audio + enc_footer

def decrypt_fsb4(audio, key):
    decrypt = flipBits(audio)
    decrypt = crypt(decrypt, key)

    return decrypt


def decrypt_fsb3(audio):
    decrypt = crypt(audio, b'5atu6w4zaw')
    decrypt = flipBits(decrypt)

    return decrypt

def decrypt_file(audio, filename = ""):
    crypted = decrypt_fsb3(audio[0:4])
    if crypted == b'FSB3':
        crypted = decrypt_fsb3(audio)
    else:
        no_ext = file_renamer(os.path.basename(filename[:-8]).lower())
        key = generate_fsb_key(no_ext)
        crypted = decrypt_fsb4(audio[0:4], key)
        if crypted == b'FSB4':
            crypted = decrypt_fsb4(audio, key)
        else:
            crypted = decrypt_wor(audio)
            if crypted == False:
                print(f"Could not decrypt {filename}. Skipping...")
    return crypted


def encrypt_fsb4(audio, key):
    encrypt = crypt(audio, key)
    encrypt = flipBits(encrypt)

    return encrypt


def encrypt_fsb3(audio):
    encrypt = flipBits(audio)
    encrypt = crypt(encrypt, b'5atu6w4zaw')

    return encrypt


def generate_fsb_key(to_gen):
    xor = 0xffffffff
    encstr = ""
    cycle = 32

    for i in range(0,cycle):
        ch = to_gen[i % len(to_gen)]
        crc = int(QBKey(ch), 16)
        xor = crc ^ xor

        index = xor % len(to_gen)
        encstr += to_gen[index]

    key = []

    for i in range(0, cycle - 1):
        ch = encstr[i]
        crc = int(QBKey(ch), 16)
        xor = crc ^ xor

        c = i & 0x03

        xor = xor >> c

        z = 0 # Set to 0
        for x in range(0, 32-c):
            z += (1<<x)

        xor = xor & z

        checkByte = int(hex(xor)[-2:],16)

        if checkByte == 0:
            break

        key.append(checkByte)

    key_bytes = bytearray(key)
    return key_bytes


def parseMP3header(header):

    return {"frameSync": header[0:11],
            "version": header[11:13],
            "layer": header[13:15],
            "protection": header[15],
            "bitrate": header[16:20],
            "samplingRate": mp3_sampling[header[20:22]],
            "padding": header[22],
            "private": header[23],
            "channelMode": header[24:26],
            "modeExt": header[26:28],
            "copyright": header[28],
            "original": header[29],
            "emphasis": header[30:]}

def badMp3(reason):
    print(f"Bad MP3. Reason: {reason}")
    exit()

def toBytes(a, b=4, endian = "little"):
    return a.to_bytes(b, endian)

def pullMP3Frames(audio):
    filesize = len(audio)
    frames = []
    position = audio.find(b"\xFF\xFB\x94")
    if position == -1:
        badMp3("No sync bytes found")
    header = audio[position:position + 4]
    headerBin = "{:08b}".format(int(header.hex(), 16))
    first_frame = parseMP3header(headerBin)
    min_frame_size = int(128 * 1000/8 * 1152 / first_frame["samplingRate"])
    while filesize - position >= min_frame_size:
        header = audio[position:position + 4]
        headerBin = "{:08b}".format(int(header.hex(), 16))
        headerParsed = parseMP3header(headerBin)
        if headerParsed["frameSync"] != "1" * 11:
            badMp3("MP3 out of sync (is this a VBR file?)")
        if headerParsed["version"] != "11":
            badMp3("Not MPEG Version 1")
        if headerParsed["layer"] != "01":
            badMp3("Not MPEG Layer 3 file")
        if headerParsed["bitrate"] != "1001":
            badMp3("Not a CBR MP3 file at 128kbps")
        to_pull = min_frame_size + int(headerParsed["padding"])
        if to_pull != min_frame_size:
            print()
        frames.append(audio[position:position + to_pull])
        position += to_pull
    return frames, first_frame

def FSBentry(data, filename):
    filesize = len(data)
    frameSize = 1152
    frames = len(pullMP3Frames(data))
    file_entry_len = 80
    fsb_file = bytes(filename if len(filename) <= 30 else filename[:30], "latin-1")
    while len(fsb_file) < 30:
        fsb_file += toBytes(0, 1)
    samples_length = frames * frameSize
    loop_start = 0
    loop_end = samples_length - 1
    mode = 576
    sample_rate = 44100
    volume, priority = 255, 255
    pan = 128
    channels = 2
    min_distance = 1  # Float
    max_distance = 10000  # Float
    var_freq, var_vol, var_pan = 0, 0, 0
    toAdd = [samples_length, filesize, loop_start, loop_end, mode, sample_rate]
    toAdd2 = [volume, pan, priority, channels]
    floats = [min_distance, max_distance]
    toAdd3 = [var_vol, var_pan]

    fsb_entry = bytearray()
    fsb_entry += toBytes(file_entry_len, 2)
    fsb_entry += fsb_file
    for x in toAdd:
        fsb_entry += toBytes(x)
    for x in toAdd2:
        fsb_entry += toBytes(x, 2)
    for x in floats:
        fsb_entry += floatPack('<f', x)
    fsb_entry += toBytes(var_freq)
    for x in toAdd3:
        fsb_entry += toBytes(x, 2)

    return fsb_entry

def createFSB3(file, shortname):
    headers = []
    audio = bytearray()
    dat_entries = []
    for x in file:
        audio_name = f"{shortname}_{os.path.basename(x)}"
        with open(x, 'rb') as f:
            audio_data = f.read()
        headers.append(FSBentry(audio_data, audio_name)[0])
        dat_entries.append(os.path.splitext(audio_name)[0])
        audio += audio_data
    print(dat_entries)
    fsb_file = bytearray()
    fsb_file += b'FSB3' # FSB3 header
    fsb_file += toBytes(len(headers)) # File count
    # print(80 * len(headers) + 8, len(audio))
    dir_length = 80 * len(headers) + 8 # 80 for each entry, 8 because of eight 00 bytes
    fsb_file += toBytes(dir_length)
    fsb_file += toBytes(len(audio))
    fsb_file += toBytes(0x0100030000000000, 8, "big") # Same in all fsb files
    for x in headers:
        fsb_file += x
    fsb_file += toBytes(0, 8)
    fsb_file += audio

    fsb_dat = bytearray()
    fsb_dat += toBytes(len(headers), 4, "big")
    fsb_dat += toBytes(len(fsb_file), 4, "big")
    for y, x in enumerate(dat_entries):
        fsb_dat += toBytes(int(QBKey(x), 16), 4, "big")
        fsb_dat += toBytes(y, 4, "big")
        fsb_dat += toBytes(0, 12)

    raise Exception
    with open(f"{shortname}.fsb.xen", 'wb') as f:
        f.write(encrypt_fsb3(fsb_file))
    with open(f"{shortname}.dat.xen", 'wb') as f:
        f.write(fsb_dat)
    # print(binascii.hexlify(fsb_dat, ' ', 1))
    return

def splitFSBFrames(audio):
    filesize = len(audio)
    frameSize = 1152
    frames = []
    position = 0
    while filesize-position > 417:
        pass
    return



def createFSB4(files, shortname, encrypt = False, *args):
    headers = []
    audio_frames = []
    stream_length = 0
    first_frame = 0
    append_blanks = False
    for x in files:
        if type(x) == str:
            to_open = x
            """if not x.lower().endswith(".mp3"):
                subprocess.Popen()"""
            with open(to_open, 'rb') as f:
                curr_stream = f.read()
        else:
            curr_stream = x
        if not curr_stream:
            raise("Empty audio stream")
        stream_frames, temp_frame = pullMP3Frames(curr_stream)
        if not stream_length:
            stream_length = len(stream_frames)
        if not first_frame:
            first_frame = temp_frame
        if audio_frames:
            if len(audio_frames[-1]) != len(stream_frames):
                append_blanks = True
                stream_length = max(len(audio_frames[-1]), len(stream_frames))
        audio_frames.append(stream_frames)
    if "-stream_size" in args:
        stream_length = int(args[args.index("-stream_size") + 1])
        append_blanks = True
    for stream in audio_frames:
        if len(stream) != stream_length:
            if append_blanks:
                stream.extend([blank_48k_mp3] * (stream_length - len(stream)))
            else:
                raise("Audio streams are not the same length")
    # Interleave all audio streams
    interleaved = b''.join([val for tup in zip(*audio_frames) for val in tup])
    frameSize = 1152 # Samples/frame as per https://hydrogenaud.io/index.php/topic,32036.0.html
    samples_length = stream_length * frameSize
    comp_length = len(interleaved)
    loop_start = 0
    loop_end = samples_length - 878
    mode = 67109376
    sample_rate = first_frame["samplingRate"]
    volume = 255
    pan, priority = 128, 128
    channels = len(audio_frames) * 2
    min_distance = 1  # Float
    max_distance = 10000  # Float
    var_freq, var_vol, var_pan = 0, 0, 0
    toAdd = [samples_length, comp_length, loop_start, loop_end, mode, sample_rate]
    toAdd2 = [volume, pan, priority, channels]
    floats = [min_distance, max_distance]
    toAdd3 = [var_vol, var_pan]


    fsb_hash = b'\xda\xddMade by Addy\xdd\xad'
    file_entry_len = 80

    fsb_file = bytearray()
    fsb_file += b'FSB4' # FSB4 header
    fsb_file += toBytes(1) # File count, it's 1 multitrack file
    fsb_file += toBytes(file_entry_len) # Header length per file
    fsb_file += toBytes(comp_length)
    fsb_file += toBytes(0, 2) # Unknown, but it's always 0
    fsb_file += toBytes(4, 2) # FSB version
    fsb_file += toBytes(0) # Flags
    fsb_file += toBytes(0)  # FSB4 Null A
    fsb_file += toBytes(0)  # FSB4 Null B
    fsb_file += fsb_hash

    fsb_file += toBytes(file_entry_len, 2)
    fsb_file += bytes(shortname, "utf-8") + (b'\x00' * (30 - len(shortname))) if len(shortname) <= 30 else bytes(shortname[:30])

    for x in toAdd:
        fsb_file += toBytes(x)
    for x in toAdd2:
        fsb_file += toBytes(x, 2)
    for x in floats:
        fsb_file += floatPack('<f', x)
    fsb_file += toBytes(var_freq)
    for x in toAdd3:
        fsb_file += toBytes(x, 2)

    fsb_file += interleaved

    if encrypt:
        print(f"Encrypting audio file with key {shortname}")
        fsb_file = encrypt_fsb4(fsb_file, generate_fsb_key(shortname))

    return fsb_file

def file_renamer(file_name):
    if file_name.startswith("adlc"):
        file_name = file_name[1:]
    return file_name



def main(gh3 = False):
    dirin = f".\\input"
    dirout = f".\\output"
    for filename in os.listdir(dirin):
        t0 = time.process_time()
        with open(f"{dirin}\\{filename}", 'rb') as f:
            audio = f.read()
        if filename.lower().endswith(".fsb.xen"):
            crypted = decrypt_file(audio, filename)
        elif filename.endswith(".fsb"):
            if gh3:
                crypted = encrypt_fsb3(audio)
            else:
                no_ext = file_renamer(os.path.basename(filename[:-4]).lower())
                key = generate_fsb_key(no_ext)
                crypted = encrypt_fsb4(audio, key)
        else:
            print(f"Unknown file {filename} found, skipping...")
            continue
        t1 = time.process_time()
        fileout = (f"{filename}.xen" if filename.endswith(".fsb") else filename[:-4])
        with open(f"{dirout}\\{fileout}", 'wb') as f:
            f.write(crypted)
        print(filename, t1 - t0)

    return

def test_make():
    dirin = f".\\input"
    dirout = f".\\output"
    song_name = ""
    files = []
    songs = {}
    for filename in os.listdir(dirin):
        files.append(os.path.join(dirin,filename))
        song_name = os.path.basename(filename[:filename.find(".")])
        if song_name.startswith("adlc"):
            song_name = song_name[1:]
        if song_name in songs:
            songs[song_name].append(os.path.join(dirin,filename))
        else:
            songs[song_name] = [os.path.join(dirin,filename)]
    for song_name, song_b in songs.items():
        fsb_file = createFSB4(song_b, song_name)
        # fsb_file = encrypt_wor(fsb_file)
        with open(f"{dirout}\\{'a' if song_name.startswith('dlc') else ''}{song_name}.fsb.xen", 'wb') as f:
            f.write(fsb_file)
    return

def test_combine():
    dirin = f".\\input"
    dirout = f".\\output"
    song_name = "test"
    files = []
    for filename in os.listdir(dirin):
        files.append(f"{os.path.join(dirin,filename)}")
    drum, inst, other, preview = get_padded_audio(files, song_name)
    for enum, x in enumerate([drum, inst, other, preview]):
        if enum != 3:
            with open(f"{dirout}\\{song_name}_{enum+1}.fsb.xen", 'wb') as f:
                f.write(x)
        else:
            with open(f"{dirout}\\{song_name}_preview.fsb.xen", 'wb') as f:
                f.write(x)
    return

 # Playable:
 # Preview: sox -m D:\RB\Songs\Pleymo\Sept\GH3\Guitar.wav D:\RB\Songs\Pleymo\Sept\GH3\Bass.wav D:\RB\Songs\Pleymo\Sept\GH3\Backing.wav -C 128 output.mp3 trim 0:35 1:05
if __name__ == "__main__":
    #main()
    test_combine()
    #test_make()


