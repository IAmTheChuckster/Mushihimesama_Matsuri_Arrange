#!/usr/bin/env python3
"""
Mushihimesama Matsuri Arrange (Cave CV1000) - patch build 8

Usage:
    python3 matsuri_patch.py matsuri15.zip              -> writes matsuriarr_u4 next to the zip
    python3 matsuri_patch.py matsuri15.zip --zip        -> also writes mushimatsuriarr.zip (the set with u4 replaced by matsuriarr_u4)
    python3 matsuri_patch.py matsuri15.zip --mra        -> also writes "Mushihimesama Matsuri Arrange.mra" (MiSTer)
    python3 matsuri_patch.py matsuri15.zip -o OUT       -> writes the patched matsuriarr_u4 to OUT
    python3 matsuri_patch.py u4                      -> a loose original u4 works too (no --zip)

The original u4 must have CRC32 6af99f0e; the result is checked to be daeb79cb.
Only the Python standard library is used.
"""
import argparse, base64, os, sys, zipfile, zlib

ORIG_CRC = 0x6AF99F0E
PATCHED_CRC = 0xDAEB79CB
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
        "ICAyIDIwLzYxMTcvTSBUQVVTSVJBIFJSTkFFRyAg")),
    (0x1FBE00, base64.b64decode(
        "BdEG0gbTFmAQQwIi+48EcgLQK0AJAAkAH6CAvnwMAAAAAMMB")),
    (0x1FBE80, base64.b64decode(
        "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")),
]


# MiSTer MRA (the matsuriarr_u4 CRC is filled in from PATCHED_CRC when written)
MRA_TEMPLATE = """<!--
  ikacore_CV1k MRA - Mushihimesama Matsuri Arrange (2026/11/7 MATSURI ARRANGE).
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
    <name>Mushihimesama Matsuri Arrange (2026/11/7 MATSURI ARRANGE)</name>
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
        <part name="matsuriarr_u4" crc="daeb79cb"/>
        <part name="matsuriarr_u4" crc="daeb79cb"/>
    </rom>

    <buttons names="Shot,Bomb,Rapid Shot,Weapon Change,Start,Coin,Test,Service,Save State" default="A,B,X,Y,Start,R,L,Select"/>
</misterromdescription>
"""


def find_u4(zf):
    for name in zf.namelist():
        if os.path.basename(name).lower() in ("u4", "matsuri15_u4", OUT_NAME):
            return name
    return None


def apply_patch(data):
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
    out = bytes(out)
    crc = zlib.crc32(out) & 0xFFFFFFFF
    if crc != PATCHED_CRC:
        raise ValueError("patched CRC is %08x, expected %08x" % (crc, PATCHED_CRC))
    return out


def mra_text():
    import re
    return re.sub(r'(<part name="matsuriarr_u4" crc=")[0-9a-fA-F]{8}', lambda m: m.group(1) + "%08x" % PATCHED_CRC, MRA_TEMPLATE)


def main():
    ap = argparse.ArgumentParser(description="Patch Mushihimesama Matsuri 1.5 u4 into matsuriarr_u4 (Matsuri Arrange, build 8)")
    ap.add_argument("input", help="matsuri15.zip or a loose original u4 file")
    ap.add_argument("-o", "--output", help="where to write matsuriarr_u4")
    ap.add_argument("--zip", action="store_true", help="also write mushimatsuriarr.zip (input must be a zip)")
    ap.add_argument("--mra", action="store_true", help="also write the MiSTer .mra")
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
        patched = apply_patch(data)
    except ValueError as e:
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
