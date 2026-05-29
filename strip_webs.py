"""Strip primitives whose material name starts with 'Web' from a GLB and rebuild a compact file."""
import struct, json, copy, sys

inp = r'C:\Users\Little Nineveh\TLS GLB Model Viewer\clinton.glb'
out = r'C:\Users\Little Nineveh\TLS GLB Model Viewer\clinton.noweb.glb'

data = open(inp, 'rb').read()
mag, ver, total = struct.unpack('<III', data[:12])
assert mag == 0x46546C67 and ver == 2
off = 12; jchunk = None; bchunk = None
while off < total:
    cl, ct = struct.unpack('<II', data[off:off+8])
    c = data[off+8:off+8+cl]
    if ct == 0x4E4F534A: jchunk = c
    elif ct == 0x004E4942: bchunk = c
    off += 8 + cl
g = json.loads(jchunk.decode('utf-8'))

# 1) Web materials by name prefix
web_mats = {i for i, m in enumerate(g.get('materials', [])) if m.get('name','').lower().startswith('web')}
print('web material indices:', web_mats, 'names:', [g['materials'][i].get('name') for i in web_mats])

# 2) Filter mesh primitives
before = sum(len(m.get('primitives', [])) for m in g.get('meshes', []))
for mesh in g.get('meshes', []):
    mesh['primitives'] = [p for p in mesh.get('primitives', []) if p.get('material') not in web_mats]
after = sum(len(m.get('primitives', [])) for m in g.get('meshes', []))
print(f'primitives: {before} -> {after}  (dropped {before-after})')

# 3) Used accessors
used_acc = set()
for mesh in g.get('meshes', []):
    for p in mesh.get('primitives', []):
        if 'indices' in p: used_acc.add(p['indices'])
        for a in p.get('attributes', {}).values(): used_acc.add(a)
        for tgt in p.get('targets', []):
            for a in tgt.values(): used_acc.add(a)
for sk in g.get('skins', []):
    if 'inverseBindMatrices' in sk: used_acc.add(sk['inverseBindMatrices'])
for an in g.get('animations', []):
    for s in an.get('samplers', []):
        used_acc.add(s['input']); used_acc.add(s['output'])

# 4) Used bufferViews (from accessors + images)
used_bv = set()
for i in used_acc:
    a = g['accessors'][i]
    if 'bufferView' in a: used_bv.add(a['bufferView'])
    sp = a.get('sparse')
    if sp:
        used_bv.add(sp['indices']['bufferView']); used_bv.add(sp['values']['bufferView'])
for img in g.get('images', []):
    if 'bufferView' in img: used_bv.add(img['bufferView'])

# 5) Repack bufferViews + binary
new_bin = bytearray(); new_bvs = []; bv_map = {}
for old in sorted(used_bv):
    bv = g['bufferViews'][old]; bo = bv.get('byteOffset', 0); bl = bv['byteLength']
    while len(new_bin) % 4 != 0: new_bin.append(0)
    nb = copy.deepcopy(bv); nb['byteOffset'] = len(new_bin); nb['buffer'] = 0
    new_bin.extend(bchunk[bo:bo+bl])
    bv_map[old] = len(new_bvs); new_bvs.append(nb)
g['bufferViews'] = new_bvs

# 6) Repack accessors and renumber refs
new_accs = []; acc_map = {}
for i, a in enumerate(g['accessors']):
    if i not in used_acc: continue
    if 'bufferView' in a: a['bufferView'] = bv_map[a['bufferView']]
    sp = a.get('sparse')
    if sp:
        sp['indices']['bufferView'] = bv_map[sp['indices']['bufferView']]
        sp['values']['bufferView'] = bv_map[sp['values']['bufferView']]
    acc_map[i] = len(new_accs); new_accs.append(a)
g['accessors'] = new_accs
for mesh in g.get('meshes', []):
    for p in mesh.get('primitives', []):
        if 'indices' in p: p['indices'] = acc_map[p['indices']]
        for k, v in list(p.get('attributes', {}).items()): p['attributes'][k] = acc_map[v]
        for tgt in p.get('targets', []):
            for k, v in list(tgt.items()): tgt[k] = acc_map[v]
for sk in g.get('skins', []):
    if 'inverseBindMatrices' in sk: sk['inverseBindMatrices'] = acc_map[sk['inverseBindMatrices']]
for an in g.get('animations', []):
    for s in an.get('samplers', []):
        s['input'] = acc_map[s['input']]; s['output'] = acc_map[s['output']]
for img in g.get('images', []):
    if 'bufferView' in img: img['bufferView'] = bv_map[img['bufferView']]

g['buffers'] = [{'byteLength': len(new_bin)}]

# 7) Encode GLB
nj = json.dumps(g, separators=(',', ':')).encode('utf-8')
while len(nj) % 4 != 0: nj += b' '
while len(new_bin) % 4 != 0: new_bin.append(0)
tl = 12 + 8 + len(nj) + 8 + len(new_bin)
out_buf = bytearray()
out_buf.extend(struct.pack('<III', 0x46546C67, 2, tl))
out_buf.extend(struct.pack('<II', len(nj), 0x4E4F534A)); out_buf.extend(nj)
out_buf.extend(struct.pack('<II', len(new_bin), 0x004E4942)); out_buf.extend(new_bin)
open(out, 'wb').write(out_buf)
print(f'Wrote {out}: {len(out_buf)/1048576:.2f} MB  (was {len(data)/1048576:.2f} MB)')
