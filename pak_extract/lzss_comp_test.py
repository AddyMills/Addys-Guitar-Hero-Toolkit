RINGBUFFERSIZE = 4096
MATCHLIMIT = 18
THRESHOLD = 2


def write_out(x, p_out):
    p_out.append(x)
    return p_out


def read_into(p_in, decode_len):
    if decode_len == 0:
        return None, decode_len
    decode_len -= 1
    return p_in.pop(0), decode_len


def decode_lzss(p_in, p_out, decode_len):
    r = RINGBUFFERSIZE - MATCHLIMIT
    flags = 0
    while True:
        if (flags >> 1) & 256 == 0:
            c, decode_len = read_into(p_in, decode_len)
            if c is None:
                break
            flags = c | 0xff00
        if flags & 1:
            c, decode_len = read_into(p_in, decode_len)
            if c is None:
                break
            p_out = write_out(c, p_out)
            r = (r + 1) % RINGBUFFERSIZE
        else:
            i, decode_len = read_into(p_in, decode_len)
            j = p_in.pop(0)
            i |= ((j & 0xf0) << 4)
            j = (j & 0x0f) + THRESHOLD
            for k in range(j + 1):
                c = p_out[(i + k) % RINGBUFFERSIZE]
                p_out = write_out(c, p_out)
                r = (r + 1) % RINGBUFFERSIZE
    return p_out


test_script = b'\xFF\x01\x16\x0E\xC6\xE8\x2D\x4A\x48\x75\x00\xF6\xF2\x01\xF6\xF1\x08\x00\x83\xF6\xF3\xEA\xF6\xF0\x18\xF6\xF1\x21\x12\x09\x20\x46\x6C\xFF\x61\x73\x68\x20\x48\x69\x67\x68\x8F\x77\x61\x79\x20\x12\x0A\x12\x00\xF8\xF2\x16\x9F\x2D\xC0\x0D\xCD\x4A\x0D\x02\xFA\xF6\x8D\xFF\x00\x00\xA1\xDC\x81\xF9\x14\xF6\x7B\xC3\xE2\x3E\x03\xF7\x5A\xFA\x19\x48\x0F\x04\xF6\xF1\x5E\x06\x24'

test_script = decode_lzss(test_script)