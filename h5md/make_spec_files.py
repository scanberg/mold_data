"""
Writes the two synthetic H5MD fixtures of unittest/test_h5md.c. Every value follows from a formula the
test repeats, so nothing here has to be copied into the test by hand:

    position[f][i][k] = 0.1 f + 0.01 i + 0.001 k       (nm, or no unit)

Run with h5py >= 3: python make_spec_files.py
"""
import h5py
import numpy as np

N, F = 4, 6

def position(frames):
    f = np.arange(frames)[:, None, None]
    i = np.arange(N)[None, :, None]
    k = np.arange(3)[None, None, :]
    return 0.1 * f + 0.01 * i + 0.001 * k

def meta(h, name):
    g = h.create_group("h5md")
    g.attrs["version"] = np.array([1, 1], dtype=np.int32)
    g.create_group("author").attrs["name"] = np.bytes_("mdlib unittest")
    c = g.create_group("creator")
    c.attrs["name"] = np.bytes_(name)
    c.attrs["version"] = np.bytes_("1.0")

def unit(ds, u):
    ds.attrs["unit"] = np.bytes_(u)
    return ds

# spec_fixed.h5md: the core as the specification spells it out, and every choice it leaves open taken
# the other way from GROMACS.
with h5py.File("spec_fixed.h5md", "w") as h:
    meta(h, "make_spec_files.py fixed")
    units = h["h5md"].create_group("modules/units")
    units.attrs["version"] = np.array([1, 0], dtype=np.int32)
    units.attrs["system"] = np.bytes_("SI")

    g = h.create_group("particles/all")
    box = g.create_group("box")
    box.attrs["dimension"] = np.int32(3)
    # Variable length strings, where GROMACS writes fixed ones; z is not periodic
    box.attrs.create("boundary", ["periodic", "periodic", "none"], dtype=h5py.string_dtype())
    unit(box.create_dataset("edges", data=np.array([2.0, 3.0, 4.0])), "nm")        # cuboid, fixed in time

    # Fixed step and time: a scalar increment and an offset, frames every 10 steps from step 100
    pos = g.create_group("position")
    s = pos.create_dataset("step", data=np.int64(10)); s.attrs["offset"] = np.int64(100)
    t = unit(pos.create_dataset("time", data=np.float64(0.02)), "ps"); t.attrs["offset"] = np.float64(0.2)
    # Big endian doubles, contiguous: read straight from the file
    unit(pos.create_dataset("value", data=position(F), dtype=">f8"), "nm")

    # Velocity every other frame, explicit steps and no time: the time comes from the run's
    vel = g.create_group("velocity")
    vel.create_dataset("step", data=np.array([100, 120, 140], dtype=np.int64))
    unit(vel.create_dataset("value", data=position(3) * 2.0, dtype="<f4", chunks=(2, N, 3)), "nm ps-1")   # two frames per chunk

    # Force in every frame: beside the positions. Chunked with a filter, so read through HDF5
    frc = g.create_group("force")
    frc.create_dataset("step", data=100 + 10 * np.arange(F, dtype=np.int64))
    frc.create_dataset("time", data=0.2 + 0.02 * np.arange(F))
    unit(frc.create_dataset("value", data=-position(F), dtype="<f4", chunks=(1, N, 3), compression="gzip"), "kJ mol-1 nm-1")

    # Species as an enumeration, which names the particles
    species_t = h5py.enum_dtype({"C": 0, "O": 1, "H": 2}, basetype="i1")
    g.create_dataset("species", data=np.array([0, 1, 2, 2], dtype="i1"), dtype=species_t)
    unit(g.create_dataset("mass", data=np.array([12.011, 15.999, 1.008, 1.008])), "u")
    charge = g.create_dataset("charge", data=np.array([0.5, -0.8, 0.15, 0.15], dtype=np.float32))
    unit(charge, "e"); charge.attrs["type"] = np.bytes_("effective")
    g.create_dataset("id", data=np.array([10, 11, 12, 13], dtype=np.int64))

    # A second, smaller group: not the one read, and connectivity naming it is not used
    sub = h.create_group("particles/oxygen")
    sub.create_dataset("id", data=np.array([11], dtype=np.int64))

    # Bonds by id, with -1 as the fill value: C-O, O-H, O-H, one to fill, and one naming no particle
    con = h.create_group("connectivity")
    bonds = con.create_dataset("bonds", shape=(5, 2), dtype=np.int64, fillvalue=-1)
    bonds[0:3] = [[10, 11], [11, 12], [11, 13]]
    bonds[4] = [11, 99]
    bonds.attrs["particles_group"] = g.ref
    other = con.create_dataset("other_bonds", data=np.array([[11, 11]], dtype=np.int64))
    other.attrs["particles_group"] = sub.ref
    con.create_dataset("angles", data=np.array([[10, 11, 12]], dtype=np.int64)).attrs["particles_group"] = g.ref

    obs = h.create_group("observables")
    e = obs.create_group("potential_energy")
    e.create_dataset("step", data=np.array([100, 130], dtype=np.int64))
    unit(e.create_dataset("time", data=np.array([0.2, 0.26])), "ps")
    unit(e.create_dataset("value", data=np.array([-10.5, -11.25])), "kJ mol-1")
    c = obs.create_group("center/of_mass")
    s = c.create_dataset("step", data=np.int64(10)); s.attrs["offset"] = np.int64(100)
    unit(c.create_dataset("value", data=np.arange(F * 3, dtype=np.float32).reshape(F, 3)), "nm")
    unit(obs.create_dataset("volume", data=np.float64(24.0)), "nm+3")
    obs.create_dataset("label", data=np.bytes_("not a number"))

# spec_bare.h5md: as little as the specification allows. No units, no time, no connectivity, integer
# species, a triclinic box per frame that misses a step, and positions compressed in chunks of two
# frames.
with h5py.File("spec_bare.h5md", "w") as h:
    meta(h, "make_spec_files.py bare")
    g = h.create_group("particles/atoms")
    box = g.create_group("box")
    box.attrs["dimension"] = np.int32(3)
    box.attrs["boundary"] = np.array([b"periodic"] * 3, dtype="S8")
    edges = box.create_group("edges")
    edges.create_dataset("step", data=np.array([0, 1, 3, 4, 5], dtype=np.int64))    # no box at step 2
    m = np.array([[20.0, 0, 0], [5.0, 30.0, 0], [1.0, 2.0, 40.0]])
    edges.create_dataset("value", data=np.stack([m * (1 + 0.1 * s) for s in [0, 1, 3, 4, 5]]))

    pos = g.create_group("position")
    pos.create_dataset("step", data=np.arange(F, dtype=np.int64))
    pos.create_dataset("value", data=position(F).astype(np.float32), chunks=(2, N, 3), compression="gzip", shuffle=True)

    img = g.create_group("image")
    img["step"] = pos["step"]                                                     # a hard link, as the specification asks
    img.create_dataset("value", data=np.ones((F, N, 3), dtype=np.int32))

    g.create_dataset("species", data=np.array([6, 6, 8, 1], dtype=np.int32))
    g.create_dataset("mass", data=np.array([12.011, 12.011, 15.999, 1.008]))
