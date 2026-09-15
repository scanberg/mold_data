# TREXIO test data

Fixtures for `unittest/test_trexio.c`.

## h2o.trexio

Water, cc-pVDZ, restricted Hartree-Fock, from **ORCA**, converted to TREXIO 2.6.1 (HDF5 back end).
Taken from the sample set in [viamd#150](https://github.com/scanberg/viamd/pull/150).

50 KB, and it covers more than its size suggests:

- **spherical atomic orbitals** (`ao_cartesian = 0`), including a d shell — which is the whole
  reason the ordering and normalisation code exists. TREXIO orders its spherical functions
  `m = 0, +1, -1, +2, -2` and md_gto orders them ascending in m, so a reader that forgets to permute
  produces orbitals that are visibly not orthonormal.
- **`basis_prim_factor` and `basis_shell_factor`**, so the normalisation path is exercised as TREXIO
  defines it rather than as a reader might assume.
- **`mo_spin` all zero with occupations of 2**, which is TREXIO's way of saying restricted — the
  case the per-spin split in md_trexio.c is for.
- **no `mo_energy` and no `nucleus_repulsion`**, which is what makes it useful for asserting that an
  absent block publishes nothing rather than a column of zeros.
- `ao_1e_int_overlap`, which this reader deliberately does NOT use — see `md_qm_publish_overlap` for
  why a spherical overlap cannot be converted into the Cartesian one the coefficients are stated
  against, and why integrating it is exact where converting it is not. It is still useful for
  checking the reader by hand.

The Molden files in `../molden/h2o_ccpvdz*.molden` are this calculation written out in that format,
which is what `trexio.agrees_with_the_same_calculation_in_molden` compares against.
