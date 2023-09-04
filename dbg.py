def read_debug():
    import os
    root_folder = os.path.realpath(os.path.dirname(__file__))
    func_dict = {}
    with open(os.path.join(root_folder, "debug.txt"), 'r') as f:
        text_lines = f.readlines()

    """with open(f"{root_folder}\\debug_extra.txt", 'r') as f:
        text_lines += f.readlines()"""

    for x in text_lines:
        new_text = x[:-1].split(" ", maxsplit=1)
        try:
            func_dict[int(new_text[0], 16)] = new_text[1].replace("\"", "")
        except:
            pass

    return func_dict

checksum_dbg = read_debug()

def add_extra(qb_key, text):
    import os
    global checksum_dbg
    root_folder = os.path.realpath(os.path.dirname(__file__))
    if int(qb_key, 16) not in checksum_dbg:
        with open(f"{root_folder}\\debug_extra.txt", 'a') as f:
            f.write(f'\n{qb_key} "{text}"')
    # checksum_dbg[int(qb_key, 16)] = text



if __name__ == "__main__":
    import CRC
    for x in checksum_dbg.keys():
        str_check = checksum_dbg[x]
        dbg_check = hex(int(CRC.QBKey(checksum_dbg[x]), 16))
        if dbg_check != hex(int(x, 16)):
            print(f"{x} is not equal to {checksum_dbg[x]}")
