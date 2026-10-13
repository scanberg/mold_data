# martini

Martini coarse grained systems simulated with GROMACS 2023.3, for testing what mdlib infers from coordinates alone
(bead masses, sizes and particle kinds, residue kinds, roles, bonds) against the topology of each. Each system is a
frame of a short MD run as `.gro` and its topology as `.tpr`, which `gmx grompp` wrote for that frame:

- The frame is one of the run (its last, or the one with the most stretched backbone bond), with the molecules broken
  across the box as the trajectory has them, and all but 30 of each kind of water left out (atoms renumbered,
  velocities dropped).
- The `.tpr` is of the frame with the trimmed topology. Where the model has an elastic network written as bonds
  (`#ifdef RUBBER_BANDS`: the DNA and RNA of Martini 2), it is left out: it is not chemistry.

| file | force field | contents |
|---|---|---|
| martini3_membrane | Martini 3, v2 lipidome | POPC, POPE, POPS, CHOL (virtual sites) bilayer (insane), W, NA, CL |
| martini3_lipids | Martini 3, v2 lipidome | 24 lipids: PC, PE, PS, PG, PA, PI, PIP2, PIP3, SM, ceramide, cardiolipin, BMPs, mono-, di- and triglycerides, fatty acids, ether and plasmalogen lipids, DOTAP, CHOL, hydrocarbons (polyply, insane) |
| martini3_peptides | Martini 3 (martinize2, vermouth 0.15) | BPTI 13-40 with charged termini (Pro, Ala) and a disulfide; chignolin with neutral termini (Gly) |
| martini3_rna | Martini 3 RNA (reForge) | a 22 bp RNA duplex, virtual sites in the bases |
| martini3_small_molecules | Martini 3 | 16 small molecules (small_molecules_v1 of 2021-11-01: rings of virtual sites), 9 solvents, 5 sugars (v2: GLC, FRUF, GYN, GLA, SUCR), 16 ions, SW, TW, W |
| martini3_polymer | Martini 3 (polyply) | PEO 20-mer with OH ends, a polystyrene 10-mer |
| martini2_membrane_protein | Martini 2.2 (martinize2) | ubiquitin on a DPPC, DOPC, CHOL bilayer; W, WF, NA+, CL- |
| martini2_lipids | Martini 2 lipidome | 24 lipids, sterols and surfactants |
| martini2p_protein | polarizable Martini 2.2 (martinize2) | villin: charge dummies, massless virtual sites; PW |
| martini2_dna | Martini 2 DNA (martinize-dna, ds-stiff) | a 12 bp DNA duplex (1BNA), W, NA |
| martini2_rna | Martini 2 RNA (martinize-nucleotide, ds-stiff) | a 14 bp RNA duplex, W, NA |
| martini2_small_molecules | Martini 2 | the solvents, sugars and ions of Martini 2 |

The force field files are those of the Martini force field (cgmartini.nl, github.com/marrink-lab,
github.com/Martini-Force-Field-Initiative/M3-Lipid-Parameters), vermouth 0.15, polyply 1.8 and reForge
(github.com/DanYev/reForge). Each run: steepest descent, then 30-50 ps at 10 fs and 100 ps (Martini 3) or 200 ps
(Martini 2) at 20 fs, reaction field (eps_r 15, 2.5 with polarizable water), V-rescale at 310 K, C-rescale at 1 bar.
SW and TW have atom types in martini_v3.0.0.itp but no molecule type; they were given one of a bead each.

Left out of martini3_small_molecules, as no reader of coordinates can tell them: trehalose (sugars v2), whose second
virtual site is numbered residue 1 after residue 2, and so runs into the first residue of the next trehalose; and
acetate (ions v1), whose residue and bead are named ION and CL as chloride's are.

To trim a frame (`trim.py` keeps the first N molecules of each water, leaves out the molecule types to drop and writes the topology with the counts):

    gmx trjconv -s topol.tpr -f traj.xtc -dump 200 -o frame.gro
    python3 trim.py <system> frame.gro out martini3_membrane --keep-water 30 [--undefine RUBBER_BANDS] [--drop TREH]
    gmx grompp -f em.mdp -c martini3_membrane.gro -p martini3_membrane.top -o martini3_membrane.tpr -maxwarn 10
