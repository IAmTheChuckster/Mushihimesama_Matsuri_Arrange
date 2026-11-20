#!/usr/bin/env python3
"""
Mushihimesama Matsuri Arrange (Cave CV1000) - patch build 30

Usage (GOD = your Xbox 360 Mushihimesama Games-on-Demand package as a .zip or .7z, any name; required):
    python3 patch.py matsuri15.zip --god GOD              -> writes matsuriarr_u4 next to the zip
    python3 patch.py matsuri15.zip --god GOD --zip        -> also writes mushimatsuriarr.zip (the set with u4 replaced by matsuriarr_u4)
    python3 patch.py matsuri15.zip --god GOD --mra        -> also writes "Mushihimesama Matsuri Arrange.mra" (MiSTer)
    python3 patch.py matsuri15.zip --god GOD -o OUT       -> writes the patched matsuriarr_u4 to OUT
    python3 patch.py u4 --god GOD                      -> a loose original u4 works too (no --zip)

The アレンジモード banner picture is cut from the GOD package at patch time; no game data is stored in this file.
The original u4 must have CRC32 6af99f0e; the result is checked to be 050412f4.
Only the Python standard library is used.
"""
import argparse, base64, os, sys, zipfile, zlib

ORIG_CRC = 0x6AF99F0E
PATCHED_CRC = 0x050412F4
U4_SIZE = 0x200000
OUT_NAME = "matsuriarr_u4"
SET_NAME = "mushimatsuriarr.zip"
MRA_NAME = "Mushihimesama Matsuri Arrange.mra"

# Patch blocks: (offset in the u4 file as stored in the MAME set, bytes)
PATCHES = [
    (0x1B4, base64.b64decode(
        "H6AAvg==")),
    (0x169766, base64.b64decode(
        "SFRTSVAgT1JFSlRDSSAgU05VRk9JRklDTEEgIAAAICBOQSBEU0lOIFRPQSBGRkxJQUlFVCBESVdI"
        "VCAsAAAgIE5FT0RTUkRFQiAsWU8gIFJVQUhUUk9aSURFICAAACAgWUJDIFZBLkVBIExMUiBHSVRI"
        "IFNPVFQgRUggIAAAICBST0dJTklMQUcgTUEgRU5BIERUSSBTICAgICAgAAAgIFNBT1NJQ1RBREVJ"
        "IFROTEVFTFRDQVUgTCAgICAAACAgUlBQT1JFWVRSIE1FSUEgTklXSFRUIEVIUkkgIAAAICBFUlBT"
        "Q0VJVEVWUiBHSVRIIFNPSERMUkUuUyAgAAAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAA"
        "ACAgICAgICAgICBBSEVWRiBOVSEhICEgICAgICAgIAAAICAgICAgICAgICAgICAgICAgICAgICAg"
        "ICAgICAgAAAgICAgICAgIA==")),
    (0x169904, base64.b64decode(
        "ICAwMjYyMS8vMTAyTSBUQVVTSVJBIFJSTkFFRyAg")),
    (0x1FBE00, base64.b64decode(
        "BdEG0gbTFmAQQwIi+48EcgLQK0AJAAkAH6CAvnwMAAAAAPgC")),
    (0x1FBE80, base64.b64decode(
        "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"
        "DCSefAywBwAAAAAAAAAAAAAAAA==")),
]


# MiSTer MRA (the matsuriarr_u4 CRC is filled in from PATCHED_CRC when written)
MRA_TEMPLATE = """<!--
  ikacore_CV1k MRA - Mushihimesama Matsuri Arrange (2026/11/20 MATSURI ARRANGE).
  Converted from the community MRA (same set, zip names, CRCs and
  <about>) to the DDR3-direct delivery format, 2026-09-17.

  DELIVERY: the NAND and YMZ images do not stream over the ioctl/SPI
  lane.  Both roms carry an `address=` attribute, so Main_MiSTer
  assembles them and memcpys them straight into DDR3; the fabric sees
  only a download pulse for those two.  Only u4 streams, so the ioctl
  lane carries 4 MiB instead of the old 152 MiB.  Needs a Main_MiSTer
  that parses `address` (2021 or later).  Rationale and evidence:
  docs/mra_ddr3_direct_upload_plan.md.

  Rom order is deliberate - DDR3 first, index 0 LAST.  Index 0's download
  is what finally releases the CPU, so every image is in place before the
  core runs, and any spurious run in an inter-rom gap is wiped by the u4
  download's own reset hold.

    <rom index="1">  DDR3 0x34400000  u2  NAND dump incl. spare (132 MiB,
                                          exact size)
    <rom index="2">  DDR3 0x3C800000  u23 YMZ chip 0, zero-padded to the
                                          8 MiB slot
                     DDR3 0x3D000000  u24 YMZ chip 1, zero-padded to the
                                          8 MiB slot
    <rom index="0">  ioctl stream     u4  program NOR x2 (2 MiB file listed
                                          twice = the undecoded-A21 mirror
                                          the boot ROM expects)
-->
<misterromdescription>
    <about author="ika-musume" source="https://github.com/ika-musume/ikacore_CV1k"/>
    <name>Mushihimesama Matsuri Arrange (2026/11/20 MATSURI ARRANGE)</name>
    <setname>mushimatsuriarr</setname>
    <year>2026</year>
    <manufacturer>Cave</manufacturer>
    <category>Shooter</category>
    <rbf>ikacore_CV1k</rbf>

    <rom index="1" address="0x34400000" zip="mushimatsuriarr.zip" md5="none">
        <part name="matsuri15_u2" crc="fbc6f3c1"/>
    </rom>

    <rom index="2" address="0x3C800000" zip="mushimatsuriarr.zip" md5="none">
        <part name="u23" crc="6dff634f"/>
        <part repeat="0x400000">00</part>
        <part name="u24" crc="f228b801"/>
        <part repeat="0x400000">00</part>
    </rom>

    <nvram index="3" size="135680"/>

    <rom index="0" zip="mushimatsuriarr.zip" md5="none">
        <part name="matsuriarr_u4" crc="050412f4"/>
        <part name="matsuriarr_u4" crc="050412f4"/>
    </rom>

    <buttons names="Shot,Bomb,Rapid Shot,Weapon Change,Start,Coin,Test,Service,Save State" default="A,B,X,Y,Start,R,L,Select"/>
</misterromdescription>
"""


# --- god banner: begin (Python standard library only) ---
# Builds the アレンジモード picture for the MATSURI ARRANGE banner from the user's own Xbox 360 Mushihimesama
# Games-on-Demand package (a .zip or .7z holding 5F9DF6331EAE85814989 and 5F9DF6331EAE85814989.data/DataNNNN,
# any folder, any name). Nothing of the game is stored in the patch: the picture is cut from the package at
# patch time (the zip/7z and disc readers are the ones from the Muchi Muchi Pork! patcher).
#
# Steps: archive -> GOD data files (hash blocks skipped) -> XDVDFS disc image -> /res/DISKDATA/C/h20.bin (Cave
# archive) -> entry 0_00_B.tga (Cave LZSS) -> 4096x4096 ARGB1555 sheet -> アレンジモード (stored sideways, like the
# arcade) at SRC_X,SRC_Y, 16 x 122 px -> halved with an integer 2x2 rule (opaque when 2+ of the 4 pixels are,
# grey = their average) -> 8 x 61 px in an 8 x 64 picture -> 'ARG1' + 12 zero bytes + 512 big-endian ARGB1555
# words, at u4 offset GLYPH_OFF (the patch code checks the magic and uploads it to VRAM in play).
import struct, lzma, re

GOD_ID = '5F9DF6331EAE85814989'
GOD_SHEET = ('res', 'DISKDATA', 'C', 'h20.bin')
SHEET_ENTRY = '0_00_B.tga'
SRC_X, SRC_Y, SRC_W, SRC_L = 3153, 2708, 16, 122
GLYPH_OFF = 0x1FF000          # in the u4 (16-bit words byte-swapped in the file, as everywhere in the u4)
GLYPH_MAGIC = b'ARG1'
GLYPH_LEN = 16 + 8 * 64 * 2
BLK = 0x1000
PER_FILE = 203 * 204


class _Stream:
    """Forward-only reader over one archive member, reopened when a read goes backwards."""
    def __init__(self, opener):
        self.opener = opener
        self.fh = None
        self.pos = 0

    def read_at(self, off, n):
        if self.fh is None or off < self.pos:
            self.fh = self.opener()
            self.pos = 0
        while self.pos < off:
            k = len(self.fh.read(min(off - self.pos, 1 << 20)))
            if not k:
                raise ValueError('a GOD data file is shorter than expected')
            self.pos += k
        data = self.fh.read(n)
        self.pos += len(data)
        if len(data) != n:
            raise ValueError('a GOD data file is shorter than expected')
        return data


def _data_re():
    return re.compile(r'(^|/)' + GOD_ID + r'\.data/Data(\d{4})$', re.I)


class _ZipSource:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        names = [n.replace('\\', '/') for n in self.z.namelist()]
        real = dict(zip(names, self.z.namelist()))
        rx = _data_re()
        self.has_pkg = any(n.split('/')[-1].upper() == GOD_ID for n in names)
        self.datas = sorted((n for n in names if rx.search(n)), key=lambda n: int(rx.search(n).group(2)))
        self.streams = [_Stream(lambda m=real[n]: self.z.open(m)) for n in self.datas]


# ---- 7z (only what is needed to stream the data files out of an LZMA / LZMA2 archive) ----
class _SevenZip:
    def __init__(self, path):
        self.f = open(path, 'rb')
        sh = self.f.read(32)
        if sh[:6] != b"7z\xbc\xaf\x27\x1c":
            raise ValueError('not a 7z file')
        nh_off, nh_size = struct.unpack_from('<QQ', sh, 12)
        self.f.seek(32 + nh_off)
        self.b = self.f.read(nh_size)
        self.p = 0
        t = self._byte()
        if t == 0x17:
            s = self._streams()
            fo = s['folders'][0]
            self.f.seek(32 + s['packpos'])
            packed = self.f.read(s['packsizes'][0])
            self.b = self._decode_folder(fo, packed, fo['sizes'][-1])
            self.p = 0
            t = self._byte()
        if t != 1:
            raise ValueError("this 7z's header can't be read")
        self.main = None
        self.files = []
        while True:
            t = self._byte()
            if t == 0:
                break
            if t == 2:
                while self._byte():
                    self.p += self._num()
            elif t == 3:
                self._streams()
            elif t == 4:
                self.main = self._streams()
            elif t == 5:
                self._files()
            else:
                self.p += self._num()

    def _byte(self):
        v = self.b[self.p]
        self.p += 1
        return v

    def _num(self):
        first = self._byte()
        mask, v = 0x80, 0
        for i in range(8):
            if not first & mask:
                return v + ((first & (mask - 1)) << (8 * i))
            v |= self._byte() << (8 * i)
            mask >>= 1
        return v

    def _bits(self, n, all_check):
        if all_check and self._byte():
            return [True] * n
        out, cur = [], 0
        for i in range(n):
            if not i & 7:
                cur = self._byte()
            out.append(bool(cur & (0x80 >> (i & 7))))
        return out

    def _digests(self, n):
        d = self._bits(n, True)
        self.p += 4 * sum(d)
        return d

    def _streams(self):
        s = {'packpos': 0, 'packsizes': [], 'folders': [], 'subsizes': None}
        while True:
            t = self._byte()
            if t == 0:
                break
            if t == 6:
                s['packpos'] = self._num()
                n = self._num()
                while True:
                    k = self._byte()
                    if k == 0:
                        break
                    if k == 9:
                        s['packsizes'] = [self._num() for _ in range(n)]
                    elif k == 10:
                        self._digests(n)
                    else:
                        self.p += self._num()
            elif t == 7:
                if self._byte() != 11:
                    raise ValueError("this 7z's header can't be read")
                nf = self._num()
                if self._byte():
                    raise ValueError("this 7z's header can't be read")
                for _ in range(nf):
                    coders, tin, tout = [], 0, 0
                    for _ in range(self._num()):
                        fl = self._byte()
                        cid = self.b[self.p:self.p + (fl & 15)].hex()
                        self.p += fl & 15
                        ni = no = 1
                        if fl & 0x10:
                            ni, no = self._num(), self._num()
                        pr = b''
                        if fl & 0x20:
                            k = self._num()
                            pr = self.b[self.p:self.p + k]
                            self.p += k
                        coders.append((cid, pr))
                        tin += ni
                        tout += no
                    for _ in range(tout - 1):
                        self._num()
                        self._num()
                    npk = tin - (tout - 1)
                    if npk > 1:
                        for _ in range(npk):
                            self._num()
                    s['folders'].append({'coders': coders, 'tout': tout, 'sizes': [], 'nsub': 1, 'crc': False})
                while True:
                    k = self._byte()
                    if k == 0:
                        break
                    if k == 12:
                        for fo in s['folders']:
                            fo['sizes'] = [self._num() for _ in range(fo['tout'])]
                    elif k == 10:
                        for fo, d in zip(s['folders'], self._digests(nf)):
                            fo['crc'] = d
                    else:
                        self.p += self._num()
            elif t == 8:
                k = self._byte()
                if k == 13:
                    for fo in s['folders']:
                        fo['nsub'] = self._num()
                    k = self._byte()
                subs = []
                for fo in s['folders']:
                    if not fo['nsub']:
                        continue
                    tot, acc = fo['sizes'][-1], 0
                    for _ in range(fo['nsub'] - 1):
                        v = self._num() if k == 9 else 0
                        subs.append(v)
                        acc += v
                    subs.append(tot - acc)
                if k == 9:
                    k = self._byte()
                while k:
                    if k == 10:
                        self._digests(sum(0 if (fo['nsub'] == 1 and fo['crc']) else fo['nsub'] for fo in s['folders']))
                    else:
                        self.p += self._num()
                    k = self._byte()
                s['subsizes'] = subs
            else:
                raise ValueError("this 7z's header can't be read")
        if s['subsizes'] is None:
            s['subsizes'] = [fo['sizes'][-1] for fo in s['folders']]
        return s

    def _files(self):
        n = self._num()
        empty = [False] * n
        names = []
        while True:
            t = self._byte()
            if t == 0:
                break
            size = self._num()
            end = self.p + size
            if t == 14:
                empty = self._bits(n, False)
            elif t == 17:
                self._byte()
                raw = self.b[self.p:end]
                names = raw.decode('utf-16-le').split('\0')[:n]
            self.p = end
        self.files = [(names[i].replace('\\', '/') if i < len(names) else '', empty[i]) for i in range(n)]

    @staticmethod
    def _filters(coders):
        out = []
        for cid, pr in reversed(coders):
            if cid == '21':
                out.append({'id': lzma.FILTER_LZMA2, 'dict_size': _lzma2_dict(pr[0])})
            elif cid == '030101':
                d = pr[0]
                out.append({'id': lzma.FILTER_LZMA1, 'lc': d % 9, 'lp': (d // 9) % 5, 'pb': d // 45,
                            'dict_size': struct.unpack_from('<I', pr, 1)[0]})
            elif cid == '00':
                continue
            else:
                raise ValueError("this 7z uses a compression the patcher can't read; re-pack it with LZMA or LZMA2")
        return out

    def _decode_folder(self, fo, packed, size):
        d = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=self._filters(fo['coders']))
        return d.decompress(packed, size)

    def opener(self, index):
        """Return a function that opens file `index` as a forward stream."""
        m = self.main
        # file -> (folder, offset in folder's output, size)
        fi = si = 0
        packpos = 32 + m['packpos']
        folder_pack = []
        for fo in m['folders']:
            folder_pack.append(packpos)
            packpos += m['packsizes'][len(folder_pack) - 1] if len(folder_pack) - 1 < len(m['packsizes']) else 0
        place, sub_left, off = {}, 0, 0
        for i, (name, isempty) in enumerate(self.files):
            if isempty:
                continue
            while sub_left == 0:
                sub_left = m['folders'][fi]['nsub']
                if sub_left == 0:
                    fi += 1
                else:
                    off = 0
                    cur_folder = fi
                    fi += 1
            place[i] = (cur_folder, off, m['subsizes'][si])
            off += m['subsizes'][si]
            si += 1
            sub_left -= 1
        folder, start, size = place[index]
        fo = m['folders'][folder]
        path, pk = self.f.name, folder_pack[folder]
        filters = self._filters(fo['coders'])

        class S:
            def __init__(s):
                s.fh = open(path, 'rb')
                s.fh.seek(pk)
                s.dec = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=filters)
                s.buf = b''
                s.skip = start
                s.left = size

            def _more(s):
                while not s.buf:
                    if s.dec.eof:
                        return False
                    chunk = s.fh.read(1 << 20) if s.dec.needs_input else b''
                    s.buf = s.dec.decompress(chunk, 1 << 22)
                    if not s.buf and s.dec.needs_input and not chunk:
                        return False
                return True

            def read(s, n):
                out = bytearray()
                while s.skip and s._more():
                    k = min(s.skip, len(s.buf))
                    s.buf = s.buf[k:]
                    s.skip -= k
                n = min(n, s.left)
                while len(out) < n and s._more():
                    k = min(n - len(out), len(s.buf))
                    out += s.buf[:k]
                    s.buf = s.buf[k:]
                s.left -= len(out)
                return bytes(out)
        return S


def _lzma2_dict(b):
    if b >= 40:
        return 0xFFFFFFFF
    return (2 | (b & 1)) << (b // 2 + 11)


class _SevenZipSource:
    def __init__(self, path):
        sz = _SevenZip(path)
        rx = _data_re()
        self.has_pkg = any(n.split('/')[-1].upper() == GOD_ID and not e for n, e in sz.files)
        idx = [(i, n) for i, (n, e) in enumerate(sz.files) if not e and rx.search(n)]
        idx.sort(key=lambda t: int(rx.search(t[1]).group(2)))
        self.datas = [n for _, n in idx]
        self.streams = [_Stream(sz.opener(i)) for i, _ in idx]


def open_god(path):
    with open(path, 'rb') as f:
        sig = f.read(6)
    if sig[:4] == b"7z\xbc\xaf":
        src = _SevenZipSource(path)
    elif sig[:2] == b'PK':
        src = _ZipSource(path)
    else:
        raise ValueError(path + " isn't a .zip or .7z file")
    missing = []
    if not src.has_pkg:
        missing.append(GOD_ID)
    if not src.datas:
        missing.append(GOD_ID + '.data/DataNNNN')
    if missing:
        raise ValueError('not found in ' + path + ': ' + ' and '.join(missing) +
                         '. Is it the Mushihimesama Xbox 360 GOD package?')
    return src


class _Disc:
    def __init__(self, src):
        self.src = src

    def read(self, off, size):
        out = bytearray()
        while size > 0:
            block, inner = divmod(off, BLK)
            f, b = divmod(block, PER_FILE)
            group, k = divmod(b, 204)
            n = min(size, BLK - inner)
            out += self.src.streams[f].read_at((1 + group * 205 + 1 + k) * BLK + inner, n)
            off += n
            size -= n
        return bytes(out)

    def find(self, path):
        """Sector and size of a file given as path components, e.g. ('res', 'DISKDATA', 'C', 'h20.bin')."""
        if self.read(0x10000, 20) != b'MICROSOFT*XBOX*MEDIA':
            raise ValueError("that GOD package doesn't hold an Xbox disc image")
        sec, size = struct.unpack('<II', self.read(0x10014, 8))
        for depth, name in enumerate(path):
            data = self.read(sec * 0x800, size)
            stack, hit = [0], None
            while stack:
                o = stack.pop()
                if o * 4 + 14 > len(data):
                    continue
                l, r, s, sz, attr, nl = struct.unpack_from('<HHIIBB', data, o * 4)
                if l == 0xFFFF:
                    continue
                if data[o * 4 + 14:o * 4 + 14 + nl].decode('latin-1').lower() == name.lower():
                    hit = (s, sz, attr)
                    break
                if l:
                    stack.append(l)
                if r:
                    stack.append(r)
            last = depth == len(path) - 1
            if hit is None or bool(hit[2] & 0x10) == last:
                raise ValueError('/'.join(path) + " wasn't found in the GOD package. Is it Mushihimesama?")
            sec, size = hit[0], hit[1]
        return sec, size


def _lzss(e, need):
    """Cave LZSS entry -> at least `need` bytes of output (+0 0x00080012, +4 tokens, +8 token data offset,
    flag bits from +12, MSB first: 1 = copy (BE u16: length (v & 31) + 3, distance v >> 5), 0 = literal)."""
    n, p = struct.unpack_from('>II', e, 4)
    out = bytearray()
    for i in range(n):
        if len(out) >= need:
            break
        if (e[12 + (i >> 3)] >> (7 - (i & 7))) & 1:
            v = (e[p] << 8) | e[p + 1]
            p += 2
            d, k = v >> 5, (v & 31) + 3
            if d >= k:
                s = len(out) - d
                out += out[s:s + k]
            else:
                for _ in range(k):
                    out.append(out[-d])
        else:
            out.append(e[p])
            p += 1
    if len(out) < need:
        raise ValueError('the 360 sheet is shorter than expected')
    return out


def banner_glyph(god_path):
    """The banner picture (GLYPH_LEN bytes, big-endian words as the CPU sees them) from the GOD package."""
    disc = _Disc(open_god(god_path))
    sec, size = disc.find(GOD_SHEET)
    arc = disc.read(sec * 0x800, min(size, 0x10000))
    magic, total, dstart, count = struct.unpack_from('>IIII', arc, 0)
    if magic != 0xC0090117:
        raise ValueError('h20.bin in the GOD package is not a Cave archive')
    ent = None
    for k in range(count):
        o = 0x24 + k * 0x114
        esize, eoff = struct.unpack_from('>II', arc, o + 8)
        if arc[o + 16:o + 16 + 256].split(b'\0')[0].decode('latin-1').endswith(SHEET_ENTRY):
            ent = (eoff, esize)
            break
    if ent is None:
        raise ValueError(SHEET_ENTRY + " wasn't found in h20.bin")
    e = disc.read(sec * 0x800 + ent[0], ent[1])
    w, h, bpp, desc = struct.unpack_from('<HHBB', _lzss(e, 18), 12)
    if (w, h, bpp, desc & 15) != (4096, 4096, 16, 1):
        raise ValueError('the 360 sheet is not the expected 4096x4096 ARGB1555 picture')
    top_down = bool(desc & 0x20)
    last_row = SRC_Y + SRC_L - 1
    need = 18 + ((last_row if top_down else 4095 - SRC_Y) + 1) * w * 2
    t = _lzss(e, need)

    def px(x, y):
        row = y if top_down else 4095 - y
        return struct.unpack_from('<H', t, 18 + (row * w + x) * 2)[0]
    src = [[px(SRC_X + i, SRC_Y + j) for i in range(SRC_W)] for j in range(SRC_L)]
    out = bytearray(GLYPH_MAGIC + bytes(12))
    for i in range(64):
        for j in range(8):
            v = 0
            if i < SRC_L // 2:
                quad = [src[2 * i + a][2 * j + b] for a in (0, 1) for b in (0, 1)]
                op = [q for q in quad if q & 0x8000]
                if len(op) >= 2:
                    g = sum((q >> 10) & 31 for q in op) // len(op)
                    v = 0x8000 | (g << 10) | (g << 5) | g
            out += struct.pack('>H', v)
    return bytes(out)
# --- god banner: end ---


def find_u4(zf):
    for name in zf.namelist():
        if os.path.basename(name).lower() in ("u4", "matsuri15_u4", OUT_NAME):
            return name
    return None


def apply_patch(data, glyph):
    """glyph: banner_glyph() of the GOD package (big-endian words); written byte-swapped like the rest of the u4."""
    if len(data) != U4_SIZE:
        raise ValueError("u4 is %d bytes, expected %d" % (len(data), U4_SIZE))
    crc = zlib.crc32(data) & 0xFFFFFFFF
    if crc == PATCHED_CRC:
        raise ValueError("this u4 is already patched (CRC %08x)" % crc)
    if crc != ORIG_CRC:
        raise ValueError("u4 CRC is %08x, expected the original %08x" % (crc, ORIG_CRC))
    out = bytearray(data)
    for off, blob in PATCHES:
        out[off:off + len(blob)] = blob
    g = bytearray(glyph)
    g[0::2], g[1::2] = glyph[1::2], glyph[0::2]
    out[GLYPH_OFF:GLYPH_OFF + GLYPH_LEN] = g
    out = bytes(out)
    crc = zlib.crc32(out) & 0xFFFFFFFF
    if crc != PATCHED_CRC:
        raise ValueError("patched CRC is %08x, expected %08x. Is the GOD package your Mushihimesama one?" % (crc, PATCHED_CRC))
    return out


def mra_text():
    import re
    return re.sub(r'(<part name="matsuriarr_u4" crc=")[0-9a-fA-F]{8}', lambda m: m.group(1) + "%08x" % PATCHED_CRC, MRA_TEMPLATE)


def main():
    ap = argparse.ArgumentParser(description="Patch Mushihimesama Matsuri 1.5 u4 into matsuriarr_u4 (Matsuri Arrange, build 30)")
    ap.add_argument("input", help="matsuri15.zip or a loose original u4 file")
    ap.add_argument("-o", "--output", help="where to write matsuriarr_u4")
    ap.add_argument("--zip", action="store_true", help="also write mushimatsuriarr.zip (input must be a zip)")
    ap.add_argument("--mra", action="store_true", help="also write the MiSTer .mra")
    ap.add_argument("--god", required=True, help="your Xbox 360 Mushihimesama GOD package (.zip or .7z, any name; "
                    "it must hold 5F9DF6331EAE85814989 and 5F9DF6331EAE85814989.data in any folder)")
    a = ap.parse_args()

    is_zip = zipfile.is_zipfile(a.input)
    if is_zip:
        with zipfile.ZipFile(a.input) as zf:
            name = find_u4(zf)
            if not name:
                sys.exit("error: no u4 inside %s" % a.input)
            data = zf.read(name)
    else:
        with open(a.input, "rb") as f:
            data = f.read()

    try:
        glyph = banner_glyph(a.god)
        patched = apply_patch(data, glyph)
    except (OSError, ValueError, KeyError, IndexError, struct.error, lzma.LZMAError, zipfile.BadZipFile) as e:
        sys.exit("error: %s" % e)

    folder = os.path.dirname(os.path.abspath(a.input))
    out = a.output or os.path.join(folder, OUT_NAME)
    with open(out, "wb") as f:
        f.write(patched)
    print("original u4 CRC %08x OK" % ORIG_CRC)
    print("wrote %s (CRC %08x)" % (out, PATCHED_CRC))

    if a.zip:
        if not is_zip:
            sys.exit("error: --zip needs matsuri15.zip as input")
        zout = os.path.join(folder, SET_NAME)
        with zipfile.ZipFile(a.input) as zi, zipfile.ZipFile(zout, "w", zipfile.ZIP_DEFLATED) as zo:
            for info in zi.infolist():
                if info.filename == name:
                    zo.writestr(OUT_NAME, patched)
                else:
                    zo.writestr(info.filename, zi.read(info.filename))
        print("wrote %s (u4 replaced by %s)" % (zout, OUT_NAME))
    if a.mra:
        mout = os.path.join(folder, MRA_NAME)
        with open(mout, "w", newline="\n") as f:
            f.write(mra_text())
        print("wrote %s" % mout)
    print("Back up your original u4 before flashing real hardware.")


if __name__ == "__main__":
    main()
