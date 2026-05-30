import ctypes
import os
import sys
import numpy as np

# Locate shared library
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SO_PATH = os.path.join(PROJECT_ROOT, "target", "release", "libverified_math_kernel.so")

_LIB = None
try:
    if os.path.exists(SO_PATH):
        _LIB = ctypes.CDLL(SO_PATH)
        
        # Configure rust_reflect_root
        _LIB.rust_reflect_root.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
        ]
        _LIB.rust_reflect_root.restype = None

        # Configure rust_snap_to_e8
        _LIB.rust_snap_to_e8.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_double),
        ]
        _LIB.rust_snap_to_e8.restype = None

        # Configure rust_orbit_under_reflections
        _LIB.rust_orbit_under_reflections.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        _LIB.rust_orbit_under_reflections.restype = ctypes.c_int

        # Configure rust_project_griess
        _LIB.rust_project_griess.argtypes = [
            ctypes.POINTER(ctypes.c_double),
            ctypes.c_int,
            ctypes.c_double,
            ctypes.POINTER(ctypes.c_double),
        ]
        _LIB.rust_project_griess.restype = None
except Exception as e:
    print(f"[-] Warning: Failed to load Rust acceleration library: {e}. Falling back to Python.", file=sys.stderr)

def is_rust_available():
    return _LIB is not None

def _to_floats(vec):
    from fractions import Fraction
    return [float(Fraction(x)) if isinstance(x, (str, Fraction)) else float(x) for x in vec]

def reflect_root_rust(x, alpha):
    """
    Reflect 8D coordinate list/tuple `x` across root `alpha` using Rust.
    """
    if _LIB is None:
        # Fallback to python
        from .e8_reflections import reflect
        return reflect(x, alpha)
    
    x_f = _to_floats(x)
    alpha_f = _to_floats(alpha)
    c_x = (ctypes.c_double * 8)(*x_f)
    c_alpha = (ctypes.c_double * 8)(*alpha_f)
    c_out = (ctypes.c_double * 8)()
    
    _LIB.rust_reflect_root(c_x, c_alpha, c_out)
    return tuple(c_out)

def snap_to_e8_rust(v):
    """
    Snap arbitrary 8D vector `v` to the nearest E8 lattice point using Rust.
    """
    if _LIB is None:
        # Fallback to simple python E8 snapping
        rounded = [round(x) for x in v]
        if sum(rounded) % 2 != 0:
            # find index with largest rounding error
            errors = [abs(v[i] - rounded[i]) for i in range(8)]
            idx = errors.index(max(errors))
            rounded[idx] += 1 if v[idx] > rounded[idx] else -1
        # Half-integer check
        shifted_rounded = [round(x - 0.5) for x in v]
        if sum(shifted_rounded) % 2 != 0:
            errors = [abs((v[i] - 0.5) - shifted_rounded[i]) for i in range(8)]
            idx = errors.index(max(errors))
            shifted_rounded[idx] += 1 if (v[idx] - 0.5) > shifted_rounded[idx] else -1
        recovered = [x + 0.5 for x in shifted_rounded]
        
        d8_dist = sum((a - b)**2 for a, b in zip(v, rounded))
        half_dist = sum((a - b)**2 for a, b in zip(v, recovered))
        return tuple(rounded) if d8_dist <= half_dist else tuple(recovered)

    v_f = _to_floats(v)
    c_v = (ctypes.c_double * 8)(*v_f)
    c_out = (ctypes.c_double * 8)()
    
    _LIB.rust_snap_to_e8(c_v, c_out)
    return tuple(c_out)

def orbit_under_reflections_rust(seed_index, roots, generator_indices=None, max_steps=1000):
    """
    Computes orbit under Weyl reflections using Rust.
    """
    if _LIB is None or generator_indices is None:
        # Fallback to python
        from .e8_orbits import orbit_under_reflections
        return orbit_under_reflections(seed_index, roots, generator_indices, max_steps)
    
    # Flatten roots for C array
    flat_roots = []
    for r in roots:
        flat_roots.extend(_to_floats(r))
    
    c_roots = (ctypes.c_double * len(flat_roots))(*flat_roots)
    c_generators = (ctypes.c_int * len(generator_indices))(*generator_indices)
    c_out = (ctypes.c_int * max_steps)()
    
    orbit_size = _LIB.rust_orbit_under_reflections(
        ctypes.c_int(seed_index),
        c_roots,
        ctypes.c_int(len(roots)),
        c_generators,
        ctypes.c_int(len(generator_indices)),
        ctypes.c_int(max_steps),
        c_out,
    )
    
    return [c_out[i] for i in range(orbit_size)]

def project_griess_rust(state, theta=0.1234567):
    """
    Fast projection of high-dimensional state space down to 75D plenum using Rust.
    """
    if _LIB is None:
        # Fallback to python procedural loop
        import math
        out = np.zeros(75)
        for i in range(75):
            for j, val in enumerate(state):
                out[i] += math.cos(i * j * theta) * val
        return out
        
    n = len(state)
    state_f = [float(x) for x in state]
    c_state = (ctypes.c_double * n)(*state_f)
    c_out = (ctypes.c_double * 75)()
    
    _LIB.rust_project_griess(c_state, ctypes.c_int(n), ctypes.c_double(theta), c_out)
    return np.array([c_out[i] for i in range(75)])
