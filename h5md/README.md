# h5md

Fixtures for `unittest/test_h5md.c`.

## GROMACS

The Trp-Ile dipeptide of `../tpr` (`dipep.pdb`, from `../tryptophan.pdb` with the Thr removed) in a
small box of water with two NA and two CL, amber99sb-ildn, simulated for 20 steps by GROMACS 2026
(release-2026 branch, 2026.4-dev, built with `-DGMX_USE_HDF5=ON`) writing its trajectory as H5MD:

    peptide_tip3p.h5md   1577 atoms, TIP3P water (SETTLE)
    peptide_tip3p.tpr    the run input it was simulated from
    peptide_tip4p.h5md   2074 atoms, TIP4P water (SETTLE + a massless virtual site per water)
    peptide_tip4p.tpr

`md.mdp` writes positions every 5 steps, velocities every 10 and forces every 20 (5, 3 and 2 frames),
so each has its own step and time datasets, and couples the pressure, so the box changes from frame
to frame. The tpr beside each file is what the system read from the trajectory is held against: the
same topology has to become the same system. To regenerate:

    gmx pdb2gmx -f dipep.pdb -o p.gro -p topol.top -ff amber99sb-ildn -water tip3p -ignh
    gmx editconf -f p.gro -o b.gro -d 0.6 -bt cubic
    gmx solvate -cp b.gro -cs spc216.gro -o s.gro -p topol.top
    gmx grompp -f em.mdp -c s.gro -p topol.top -o ions.tpr -maxwarn 2
    echo SOL | gmx genion -s ions.tpr -o i.gro -p topol.top -pname NA -nname CL -np 2 -nn 2
    gmx grompp -f em.mdp -c i.gro -p topol.top -o em.tpr -maxwarn 2
    gmx mdrun -s em.tpr -c em.gro -nt 1 -deffnm em
    gmx grompp -f md.mdp -c em.gro -p topol.top -o peptide_tip3p.tpr -maxwarn 2
    gmx mdrun -s peptide_tip3p.tpr -o peptide_tip3p.h5md -nt 1

and with `-water tip4p` / `-cs tip4p.gro` for the TIP4P one. The runs are not bitwise reproducible
across builds; the reference values in the test were read from these files with h5py.

What GROMACS writes, as of this version: `/h5md` with the `gromacs`, `units` and `gromacs_topology`
modules (version 0.1), `/particles/system/{position,velocity,force,box}` with explicit step and time
datasets, each frame one uncompressed chunk, and `/connectivity/bonds` without a `particles_group`
reference. `gromacs_topology/<moltype>/residue_id` is the topology's residue number plus one.

## The specification

`make_spec_files.py` (h5py) writes two small files that take every choice the specification leaves
open the other way from GROMACS. Every value follows from a formula the test repeats.

    spec_fixed.h5md   fixed step and time (a scalar increment with an offset), a cuboid box fixed in
                      time with z not periodic, big endian double positions stored contiguously,
                      velocities every other frame without a time, in chunks of two frames, forces
                      compressed, an enumerated species, particle ids, bonds by id with a fill value
                      and a particles_group reference, a second particle group, and observables
    spec_bare.h5md    no units and no time, integer species, positions compressed in chunks of two
                      frames, a triclinic box per frame that misses one step, and integer images
