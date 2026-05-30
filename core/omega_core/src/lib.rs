use pyo3::prelude::*;
use pyo3::types::PyDict;
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;
use sha2::{Digest, Sha256};
use std::f64::consts::PI;

/// The Zwegers Reality Filter (Mathematical cutoff)
/// Strips high-entropy chaos from the vector, forcing structural truth.
fn zwegers_filter(value: f64) -> f64 {
    let limit = 0.5 * PI;
    if value > limit {
        limit
    } else if value < -limit {
        -limit
    } else {
        value
    }
}

/// The Beast Archetypes acting as geometric weights/biases
fn get_beast_tuning(preference: &str) -> (f64, f64) {
    match preference.to_lowercase().as_str() {
        "ox" => (1.5, 0.8),    // Heavy, structural, foundational
        "lion" => (1.2, 1.2),  // Kingship, law, balanced aggression
        "eagle" => (0.8, 1.5), // High frequency, spiritual, fast
        "man" => (1.0, 1.0),   // The balanced center
        _ => (1.0, 1.0),
    }
}

/// Convert an input string into a deterministic 256-bit geometric seed
fn deterministic_seed(input: &str) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(input.as_bytes());
    hasher.finalize().into()
}

#[pyclass]
struct RustOmegaKernel {}

#[pymethods]
impl RustOmegaKernel {
    #[new]
    fn new() -> Self {
        RustOmegaKernel {}
    }

    /// The core 8D projection engine
    fn process<'py>(&self, py: Python<'py>, data: &str, beast_preference: &str) -> PyResult<Bound<'py, PyDict>> {
        let (weight, bias) = get_beast_tuning(beast_preference);
        
        // 1. Digest the concept into a deterministic geometric seed
        let seed = deterministic_seed(data);
        
        // 2. Initialize a fast, cryptographically secure PRNG using the exact seed
        // This ensures the same word ALWAYS produces the exact same 8D geometry.
        let mut rng = ChaCha8Rng::from_seed(seed);
        
        let mut vector_8d = [0.0f64; 8];
        let mut raw_mass = 0.0f64;

        // 3. Project into 8 Dimensions (The E8 lattice slice)
        for i in 0..8 {
            // Generate a deterministic float based on the input text
            let raw_val: f64 = rng.gen_range(-2.0..2.0);
            
            // Apply Beast tuning (Gravity)
            let tuned_val = (raw_val * weight) + bias;
            
            // Apply Zwegers Boundary (Truth constraint)
            let filtered_val = zwegers_filter(tuned_val);
            
            vector_8d[i] = filtered_val;
            raw_mass += filtered_val.abs();
        }

        // 4. Calculate the Reality Score (Structural Integrity)
        // Highly chaotic inputs hit the Zwegers boundary more often, 
        // lowering their physical reality score in the projection.
        let reality_score = raw_mass / (8.0 * (0.5 * PI));

        // 5. Pack into a Python dictionary and return across the C-boundary
        let result = PyDict::new_bound(py);
        result.set_item("state", vector_8d.to_vec())?;
        result.set_item("reality_score", reality_score)?;

        Ok(result)
    }
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn omega_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustOmegaKernel>()?;
    Ok(())
}
