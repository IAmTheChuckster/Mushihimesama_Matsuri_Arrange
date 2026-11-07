#!/usr/bin/env python3
"""Build the Matsuri Arrange patch from an original matsuri15 u4.

The u4 file stores every 16-bit word byte-swapped; text and code are edited in the
swapped ("natural") domain and written back swapped.  The patch is emitted as a
list of (file offset, bytes) pieces so the patchers carry no ROM data.
"""
import sys, zipfile, zlib, struct, subprocess, os

ORIG_CRC = 0x6af99f0e          # matsuri15_u4 as dumped
U4_SIZE = 0x200000

def swap(b):
    b = bytearray(b); b[0::2], b[1::2] = b[1::2], b[0::2]; return bytes(b)

# ---- change 1: warning screen (Japan table, 14 slots of 30 chars at 0x169764, stride 0x20)
WARN_SLOT0 = 0x169764
def ctr(t, w=30):
    l = (w - len(t) + 1) // 2
    return " " * l + t + " " * (w - len(t) - l)
def warning_lines():
    body = ["THIS PROJECT IS UNOFFICIAL",
            "AND IS NOT AFFILIATED WITH,",
            "ENDORSED BY, OR AUTHORIZED",
            "BY CAVE. ALL RIGHTS TO THE",
            "ORIGINAL GAME AND ITS",
            "ASSOCIATED INTELLECTUAL",
            "PROPERTY REMAIN WITH THEIR",
            "RESPECTIVE RIGHTS HOLDERS."]
    lines = ["  " + t for t in body]
    lines += [""] * (14 - len(lines))
    lines[9] = ctr("HAVE FUN!!!")
    lines[13] = ctr("2026/11/8 MATSURI ARRANGE")
    return [l.ljust(30) for l in lines]


# ---- change 3: title menu (code patch)
HERE = os.path.dirname(os.path.abspath(__file__))
STUB_AT, IMAGE_AT = 0x1FBE00, 0x1FBE80          # free tail of the u4 (the game never touches it)
PATCH_RAM = 0x0C7C0000
BOOT_LIT = 0x1B4                                 # literal holding the game's main (0x0C059970)

def asm(name):
    o = "/tmp/_%s.o" % name
    subprocess.check_call(["sh4-linux-gnu-as", "-big", "-isa=sh3", "-o", o, os.path.join(HERE, name + ".s")])
    b = o + ".bin"
    subprocess.check_call(["sh4-linux-gnu-objcopy", "-O", "binary", "-j", ".text", o, b])
    syms = {}
    for l in subprocess.check_output(["sh4-linux-gnu-nm", o]).decode().split("\n"):
        f = l.split()
        if len(f) == 3: syms[f[2]] = int(f[0], 16)
    return open(b, "rb").read(), syms

# (address, expected long, symbol) hooks in the unpacked program
SITES = [(0x0C0A31E0, 0x0C0548D8, "coin_draw"),    # coin message task: draw text
         (0x0C0A3738, 0x0C0548D8, "cred_text"),    # credits line: draw text
         (0x0C0A3744, 0x0C054D74, "cred_num"),     # credits line: draw number
         (0x0C0A210C, 0x0C0548D8, "gate_text"),    # marquee: draw text
         (0x0C0A2204, 0x0C0548D8, "gate_text"),
         (0x0C0A2110, 0x0C054D74, "gate_num"),     # marquee: draw number
         # MATSURI ARRANGE (Ultra)
         (0x0C05B6FC, 0x0C05FCF0, "gem_wrap"),     # gem collected -> gem counter, extra bomb
         (0x0C0ABFC0, 0x0C0AB7B0, "hud_wrap"),     # in-game per-frame callback -> counter display
         (0x0C059AF8, 0x0C054330, "poll1_wrap"),   # input poll -> 2P start off
         (0x0C059950, 0x0C054260, "poll2_wrap"),
         # crystal gem spawner entry: mov.l @(1,pc),r0 / jmp @r0 / nop / nop / .long spawn_c_wrap
         (0x0C0A6790, 0x2F862F96, 0xD001402B),
         (0x0C0A6794, 0x2FA62FB6, 0x00090009),
         (0x0C0A6798, 0x2FC62FD6, "spawn_c_wrap"),
         # gold gem spawner entry
         (0x0C0A6C30, 0x2F862F96, 0xD001402B),
         (0x0C0A6C34, 0x2FA62FB6, 0x00090009),
         (0x0C0A6C38, 0x2FC62FD6, "spawn_g_wrap"),
         (0x0C05FEBC, 0x0C05DB30, "bomb_wrap"),
         (0x0C05F168, 0x0C0602A0, "bombfx_wrap"),
         (0x0C05ED98, 0x0C0602A0, "bombfx_wrap"),
         (0x0C05FEB8, 0x0C0E3B90, "bombgo_wrap"),
         (0x0C05B700, 0x0C05F9F0, "inv_wrap"),
         (0x0C05B7E0, 0x0C05F9F0, "inv_wrap")]  # bomb trigger -> cancel bullets into gems

def title_image():
    code, syms = asm("title")
    assert syms["sites"] == len(code)
    tab = b"".join(struct.pack(">III", a, old, sym if isinstance(sym, int) else PATCH_RAM + syms[sym]) for a, old, sym in SITES) + b"\0" * 12
    assert syms["patcher"] == 0
    return code + tab

def build_stub(image_len):
    code, syms = asm("stub")
    code = bytearray(code)
    cnt = (image_len + 3) // 4
    code[-4:] = struct.pack(">I", cnt)
    return bytes(code)

def build(u4):
    s = bytearray(swap(u4))
    for i, l in enumerate(warning_lines()):
        o = WARN_SLOT0 + 0x20 * i
        assert len(l) == 30 and s[o + 30:o + 32] == b"\0\0", hex(o)
        s[o:o + 30] = l.encode("ascii")
    # ---- change 3: boot stub + patch image + boot hook
    assert s[STUB_AT:] == b"\xff" * (U4_SIZE - STUB_AT)
    assert struct.unpack(">I", s[BOOT_LIT:BOOT_LIT + 4])[0] == 0x0C059970
    img = title_image()
    assert len(img) <= U4_SIZE - IMAGE_AT and len(img) <= 0xF000
    stub = build_stub(len(img))
    assert len(stub) <= 0x80
    s[STUB_AT:STUB_AT + len(stub)] = stub
    s[IMAGE_AT:IMAGE_AT + len(img)] = img
    s[BOOT_LIT:BOOT_LIT + 4] = struct.pack(">I", 0xA0000000 + STUB_AT)
    return swap(bytes(s))

def load_u4(path):
    if zipfile.is_zipfile(path):
        z = zipfile.ZipFile(path)
        n = [n for n in z.namelist() if n.lower().endswith("u4")][0]
        return z.read(n)
    return open(path, "rb").read()

if __name__ == "__main__":
    u4 = load_u4(sys.argv[1])
    assert len(u4) == U4_SIZE and zlib.crc32(u4) == ORIG_CRC, "not the original matsuri15 u4"
    out = build(u4)
    open(sys.argv[2], "wb").write(out)
    print("patched crc %08x" % zlib.crc32(out))
