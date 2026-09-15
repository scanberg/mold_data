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
  functions, in Molden's Cartesian ordering and with the normalisation a `[6D]` writer uses.

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

## What is not here

The vibrational fixture for `[FREQ]`, `[INT]` and `[FR-NORM-COORD]` is written into
`test_molden.c` itself rather than stored here. Its numbers are placeholders chosen so that a
transposed axis or an off-by-one is obvious, and keeping them in the test is how they stay visibly
synthetic instead of looking like a calculation somebody ran.
