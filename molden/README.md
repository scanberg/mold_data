# Molden test data

Fixtures for `unittest/test_molden.c`. Provenance matters more than size here, so each file says
where its numbers came from and what it is in the suite to prove.

## h2o_ccpvdz.molden, h2o_ccpvdz_6d.molden

Water, cc-pVDZ, restricted Hartree-Fock, from **ORCA**. These are a format conversion of
`../trexio/h2o.trexio` — the same calculation, the same geometry, the same molecular orbital
coefficients, written out as Molden. The orbital energies and the `Sym=` labels come from the ORCA
JSON dump the TREXIO file was itself produced from.

They exist as a pair because the format states its angular convention two ways and both paths
through the reader have to be exercised:

- `h2o_ccpvdz.molden` is `[5D]` — five spherical d functions, which is what ORCA actually computed.
- `h2o_ccpvdz_6d.molden` is `[6D]` — the same wavefunction re-expressed over six Cartesian d
  functions, in Molden's Cartesian ordering, each Cartesian function normalised on its own, as the
  format has them (Molden itself, PySCF, IOData). It was first written with the xy, xz and yz
  coefficients against functions sharing the xx normalisation - a convention some programs write
  (Turbomole, CFOUR 2.1, PSI4 <= 1.3.2, which IOData corrects on reading) and the reader then assumed,
  so the two agreed with each other and not with the format: PySCF read it as 10.008 electrons, with
  orbitals 1.7 from orthonormal. Restated by multiplying those coefficients by 1/sqrt(3); PySCF now
  reads it as the 5D file's wavefunction to 1e-15 in the density.

Converting rather than downloading a second file is deliberate: it makes
`trexio.agrees_with_the_same_calculation_in_molden` a real cross check. The two readers share
nothing but the contract, and if either drifts the two systems stop matching.

**These are the files to trust.** Their molecular orbitals are orthonormal to 1e-7 against the
overlap the reader integrates, and their total density integrates to exactly ten electrons.

## ammonia_sto3g.molden, ammonia_sto3g_sp.molden

Ammonia, STO-3G. Written by **GANSU**, and taken from the sample set in
[viamd#150](https://github.com/scanberg/viamd/pull/150).

They are here because they were written by something other than this repository, and they are
irregular in ways the generated files above are not: a parenthesised unit on `[Atoms]`, no angular
convention marker at all, `Sym=` before `Ene=`, and the primitives of a contraction listed out of
order.

**Their molecular orbital coefficients are NOT orthonormal** — `C S C^T` is off by 0.3 and the
density integrates to 8.6 electrons rather than 10. That is a property of the file, not of the
reader; the same numbers give the same answer under an independent implementation. So nothing in the
suite asserts physics against them, only what the parser recovered: atom count, shell structure,
primitive count, atomic orbital count, and the orbital energies as written.

`ammonia_sto3g_sp.molden` is the same file with the nitrogen's 2s and 2p shells folded into one `sp`
shell — the same exponents, the same two coefficient columns, one line of the format instead of two.
Nothing else was touched. It is what
`molden.sp_shells_expand_to_s_and_p` compares against, and the two must produce the same basis and
the same orbitals.

## he_ccpvdz.molden, oh_631gs_uhf.molden

Written by **PySCF 2.14** for the electron localization function tests in `unittest/test_gto_iso.c`
(`qm_elf.*`). Helium, cc-pVDZ, restricted Hartree-Fock: one occupied orbital, so ELF is exactly 1 wherever
there is density. The OH radical (O at the origin, H at z = 1.84 bohr), 6-31G*, unrestricted Hartree-Fock,
`Spin= Beta` orbitals of its own: the open shell. Spherical d, written `[5D]`.

The ELF and LOL values the test holds for the radical come from PySCF itself (`pyscf.dft.numint`, its own AO
evaluation) of this file, not from this library.

## h2o_ccpvqz_cart.molden

Water, cc-pVQZ, restricted Hartree-Fock, Cartesian `[6D10F15G]`, written by **PySCF 2.14**, with the five
occupied orbitals only. Their small f and g components are what make it a test of the Cartesian
normalisation and order of all three: read with the d, f or g functions normalised any other way, the
orbitals are not orthonormal. PySCF reads it as ten electrons, orthonormal to 2e-14.

## h2o_ccpvdz_6d_shell.molden, h2o_ccpvqz_cart_shell.molden

The two Cartesian files above with their Cartesian functions normalised as a shell: every function of a
shell with the constant of its (l,0,0) monomial, so xy is sqrt(3) smaller than xx, as Turbomole, CFOUR 2.1
and PSI4 <= 1.3.2 write them (IOData corrects those on reading). Nothing else differs: each coefficient of
a function that is not a power of one coordinate is divided by sqrt((2i-1)!!(2j-1)!!(2k-1)!! / (2l-1)!!).
`h2o_ccpvdz_6d_shell.molden` is the `[6D]` water as it was first written; `h2o_ccpvqz_cart_shell.molden`
was made from `h2o_ccpvqz_cart.molden`, over d, f and g.

The reader is to tell the two conventions apart by the orbitals, which are orthonormal in only one of them,
and read each pair to one density (`molden.cartesian_normalisation_is_read_from_the_orbitals`). PySCF,
which takes the format's convention for every file, reads these two as 10.008 and 10.365 electrons.

## What is not here

The vibrational fixture for `[FREQ]`, `[INT]` and `[FR-NORM-COORD]` is written into
`test_molden.c` itself rather than stored here. Its numbers are placeholders chosen so that a
transposed axis or an off-by-one is obvious, and keeping them in the test is how they stay visibly
synthetic instead of looking like a calculation somebody ran.
