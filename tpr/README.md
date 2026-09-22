# tpr

GROMACS run input files for the tpr reader. A Trp-Ile dipeptide (from ../tryptophan.pdb, the Thr
removed) in a small box of water with two NA and two CL, amber99sb-ildn, written by GROMACS 2023.3
(tpx version 129):

    peptide_tip3p.tpr         single precision, TIP3P water (SETTLE)
    peptide_tip3p_double.tpr  the same written by gmx_d
    peptide_tip4p.tpr         single precision, TIP4P water (SETTLE + a virtual site per water)

The .gro files are the reference for each: `gmx editconf -f peptide_X.tpr -o peptide_X.gro`.

To regenerate (em.mdp: integrator md, nsteps 0, cutoff-scheme Verlet, coulombtype PME,
constraints h-bonds, pbc xyz):

    gmx pdb2gmx -f dipep.pdb -o p.gro -p topol.top -ff amber99sb-ildn -water tip3p -ignh
    gmx editconf -f p.gro -o b.gro -d 0.6 -bt cubic
    gmx solvate -cp b.gro -cs spc216.gro -o s.gro -p topol.top
    gmx grompp -f em.mdp -c s.gro -p topol.top -o ions.tpr -maxwarn 2
    echo SOL | gmx genion -s ions.tpr -o i.gro -p topol.top -pname NA -nname CL -np 2 -nn 2
    gmx grompp -f em.mdp -c i.gro -p topol.top -o peptide_tip3p.tpr -maxwarn 2

and with -water tip4p / -cs tip4p.gro for the TIP4P one.

    martini3.tpr              Martini 3: the dipeptide through martinize2 (vermouth 0.15, -ff
                              martini3001), two POPC, two NA, two CL and 583 W beads placed with
                              gmx insert-molecules, grompp'ed against martini_v3.0.0*.itp from
                              github.com/marrink-lab/martini-forcefields. No particle has an atomic
                              number, one (Trp SC3) is a virtual site with Lennard-Jones interactions.
    martini3.gro              gmx editconf -f martini3.tpr -o martini3.gro
