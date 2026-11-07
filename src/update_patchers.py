"""Copy a new build into the two patchers (../index.html, ../matsuri_patch.py) and the MiSTer .mra.

Usage:
    python3 update_patchers.py ORIGINAL_matsuri15.zip PATCHED_u4_FILE BUILD_NUMBER

PATCHED_u4_FILE is the output of build.py. The changed bytes (runs closer than 16 bytes are merged)
are embedded in both patchers together with the new CRC and build number.
"""
import sys, os, re, zipfile, zlib, base64, json

orig_zip, new_u4, build = sys.argv[1], sys.argv[2], sys.argv[3]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
z = zipfile.ZipFile(orig_zip)
o = z.read([n for n in z.namelist() if n.endswith('u4')][0])
p = open(new_u4, 'rb').read()
assert zlib.crc32(o) == 0x6AF99F0E, 'original u4 CRC is not 6af99f0e'
assert len(o) == len(p)
crc = zlib.crc32(p)
diff = [i for i in range(len(o)) if o[i] != p[i]]
runs = []
for i in diff:
    if runs and i - runs[-1][1] <= 16: runs[-1][1] = i + 1
    else: runs.append([i, i + 1])
blocks = [(a, p[a:b]) for a, b in runs]
print('build', build, 'u4 CRC %08x' % crc, '%d blocks, %d bytes' % (len(blocks), sum(len(d) for _, d in blocks)))

def pyblocks():
    out = 'PATCHES = [\n'
    for a, d in blocks:
        b = base64.b64encode(d).decode()
        lines = '\n'.join('        "%s"' % b[k:k + 76] for k in range(0, len(b), 76))
        out += '    (0x%X, base64.b64decode(\n%s)),\n' % (a, lines)
    return out + ']'

py = os.path.join(root, 'matsuri_patch.py')
s = open(py).read()
s = re.sub(r'PATCHED_CRC = 0x[0-9A-Fa-f]{8}', 'PATCHED_CRC = 0x%08X' % crc, s)
s = re.sub(r'checked to be [0-9a-f]{8}', 'checked to be %08x' % crc, s)
s = re.sub(r'build \d+', 'build %s' % build, s)
s = re.sub(r'(<part name="matsuriarr_u4" crc=")[0-9a-f]{8}', lambda m: m.group(1) + '%08x' % crc, s)
i = s.index('PATCHES = ['); j = s.index('\n]\n', i) + 2
s = s[:i] + pyblocks() + s[j:]
open(py, 'w').write(s)

ht = os.path.join(root, 'index.html')
h = open(ht).read()
h = re.sub(r'PATCHED_CRC = 0x[0-9a-f]{8}', 'PATCHED_CRC = 0x%08x' % crc, h)
h = re.sub(r'build \d+', 'build %s' % build, h)
h = re.sub(r'(<td class="mono">)[0-9a-f]{8}(</td><td class="mono" id="outcrc">)', lambda m: m.group(1) + '%08x' % crc + m.group(2), h)
i = h.index('const PATCH = ['); j = h.index('\n  ];', i) + 5
h = h[:i] + 'const PATCH = [\n' + ',\n'.join('    [0x%X, "%s"]' % (a, base64.b64encode(d).decode()) for a, d in blocks) + '\n  ];' + h[j:]
h = re.sub(r'(<part name=\\"matsuriarr_u4\\" crc=\\")[0-9a-f]{8}', lambda m: m.group(1) + '%08x' % crc, h)
open(ht, 'w').write(h)

# MRA from the python template
ns = {}
src = s[s.index('MRA_TEMPLATE = """'):]
exec(src[:src.index('"""', 20) + 3], ns)
m = re.sub(r'(<part name="matsuriarr_u4" crc=")[0-9a-fA-F]{8}', lambda x: x.group(1) + '%08x' % crc, ns['MRA_TEMPLATE'])
open(os.path.join(root, 'Mushihimesama Matsuri Arrange.mra'), 'w', newline='\n').write(m)
