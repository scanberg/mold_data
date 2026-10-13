#!/usr/bin/env python3
"""trim.py SYSTEM_DIR FRAME.gro OUT_DIR NAME [--keep-water N] [--undefine NAME] [--drop MOLECULE]
Writes OUT_DIR/NAME.gro: the frame without all but N of each water molecule type, and OUT_DIR/NAME.top: the topology
with those counts (and #define NAME lines removed). Molecule types are read from the topology's includes."""
import os, re, sys, argparse
ap = argparse.ArgumentParser()
ap.add_argument('sysdir'); ap.add_argument('frame'); ap.add_argument('outdir'); ap.add_argument('name')
ap.add_argument('--keep-water', type=int, default=40)
ap.add_argument('--undefine', action='append', default=[])
ap.add_argument('--drop', action='append', default=[], help='a molecule type to leave out')
a = ap.parse_args()
WATERS = {'W', 'PW', 'WF', 'SW', 'TW', 'BMW'}

top = open(os.path.join(a.sysdir, 'topol.top')).read().splitlines()
natoms = {}
def read_itp(path):
    sec = None; mol = None
    for raw in open(path, errors='ignore'):
        s = raw.split(';')[0].strip()
        if not s: continue
        if s.startswith('#include'):
            inc = s.split()[1].strip('"')
            p = os.path.join(os.path.dirname(path), inc)
            if os.path.exists(p): read_itp(p)
            continue
        if s.startswith('#'): continue
        m = re.match(r'\[\s*(\w+)\s*\]', s)
        if m: sec = m.group(1).lower(); continue
        if sec == 'moleculetype': mol = s.split()[0]; natoms[mol] = 0; sec = None
        elif sec == 'atoms' and mol: natoms[mol] += 1
read_itp(os.path.join(a.sysdir, 'topol.top'))

mols = []; out_top = []; in_mols = False
for line in top:
    s = line.split(';')[0].strip()
    if any(re.match(r'#define\s+%s\b' % d, s) for d in a.undefine): continue
    if re.match(r'\[\s*molecules\s*\]', s): in_mols = True; out_top.append(line); continue
    if in_mols and s and not s.startswith('['):
        n, c = s.split()[0], int(s.split()[1]); mols.append((n, c)); continue
    if in_mols and s.startswith('['): in_mols = False
    out_top.append(line)

gro = open(a.frame).read().splitlines()
title, n, atoms, box = gro[0], int(gro[1]), gro[2:-1], gro[-1]
assert n == len(atoms) == sum(natoms[m] * c for m, c in mols), (n, len(atoms), sum(natoms[m] * c for m, c in mols))
keep = []; pos = 0; new_mols = []
for m, c in mols:
    k = 0 if m in a.drop else min(c, a.keep_water) if m in WATERS else c
    keep.extend(atoms[pos:pos + natoms[m] * k]); pos += natoms[m] * c
    if k: new_mols.append((m, k))
out_top.append('')
out_top += ['%-12s %6d' % mc for mc in new_mols]
os.makedirs(a.outdir, exist_ok=True)
# Atom numbers renumbered (they wrap at 100000 anyway); velocities dropped
lines = []
for i, l in enumerate(keep):
    lines.append(l[:15] + '%5d' % ((i + 1) % 100000) + l[20:44])
open(os.path.join(a.outdir, a.name + '.gro'), 'w').write('\n'.join([title.strip(), '%5d' % len(lines)] + lines + [box]) + '\n')
open(os.path.join(a.outdir, a.name + '.top'), 'w').write('\n'.join(out_top) + '\n')
print(a.name, len(lines), 'atoms', new_mols)
