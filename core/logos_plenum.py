from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Tuple, Any

from rust_accelerator import project_griess_rust

# ====================== GRIESS ALGEBRA PROJECTOR ======================

class GriessAlgebraProjector:
    """
    Procedural mapping representing the high-dimensional projection from the
    196,883-dimensional Griess Algebra (the representation space of the Monster Group M)
    down to the 75-dimensional Triune Logos Plenum space.
    
    Accelerated with compiled Rust FFI to maintain real-time performance without memory allocation overhead.
    """
    def __init__(self):
        self.num_dimensions = 196883
        self.target_dimensions = 75
        self.theta = 0.1234567  # Irrational scaling factor for deterministic projection

    def project(self, griess_state: np.ndarray | List[float]) -> np.ndarray:
        """
        Projects a high-dimensional Griess Algebra state (represented sparsely or as a procedural signal)
        down to the 75D Logos space.
        """
        if isinstance(griess_state, np.ndarray):
            state = griess_state
        else:
            state = np.array(griess_state, dtype=float)
            
        # Call the Rust-accelerated projection function
        out = project_griess_rust(state, self.theta)
                
        # Normalize the projected vector
        norm = np.linalg.norm(out)
        if norm > 1e-9:
            out /= norm
        return out


# ====================== NEBE LATTICE LAYER ======================

class NebeLatticeLayer:
    """
    Represents the 72-dimensional extremal even unimodular Nebe Lattice boundary.
    Performs homological projections and reflection dampening on the 72D tripartite base.
    """
    def __init__(self):
        self.dimension = 72
        # Ideal extremal squared norm bound for the Nebe lattice
        self.extremal_norm_bound = 8.0

    def stabilize_72d(self, base_72d: np.ndarray) -> np.ndarray:
        """
        Stabilizes a 72-dimensional base vector against the Nebe lattice boundary.
        Enforces exact scaling to the extremal sphere packing shell boundary.
        """
        if len(base_72d) != self.dimension:
            raise ValueError(f"Nebe Lattice requires exactly 72 dimensions, got {len(base_72d)}")
            
        norm_sq = np.dot(base_72d, base_72d)
        scale = math.sqrt(self.extremal_norm_bound / (norm_sq + 1e-9))
        return base_72d * scale


# ====================== TRIUNE LOGOS PLENUM ======================

class TriuneLogosPlenum:
    """
    The unified 75-dimensional Triune Logos Plenum.
    Constructs the master meta-vector shape:
    - 72D Base: Direct sum of the three 24D E8/Leech Trees (Life, Knowledge, Wisdom)
    - 3D Coupling: Moduli metrics representing the relational linking coordinates (Father/Son/Holy Spirit)
    """
    def __init__(self):
        self.griess_projector = GriessAlgebraProjector()
        self.nebe_layer = NebeLatticeLayer()

    def synthesize_plenum(
        self, 
        tree_life: np.ndarray, 
        tree_knowledge: np.ndarray, 
        tree_wisdom: np.ndarray
    ) -> np.ndarray:
        """
        Synthesizes the complete 75-dimensional Triune Logos Plenum vector from
        the three E8 tree vectors, stabilizing the base through the 72D Nebe lattice layer.
        """
        # Ensure correct dimension of inputs (24D)
        v_life = self._ensure_24d(tree_life)
        v_knowledge = self._ensure_24d(tree_knowledge)
        v_wisdom = self._ensure_24d(tree_wisdom)
        
        # 1. Construct 72D Tripartite Base
        base_72d = np.concatenate([v_life, v_knowledge, v_wisdom])
        
        # 2. Stabilize base via the 72D extremal Nebe Lattice boundary
        stabilized_72d = self.nebe_layer.stabilize_72d(base_72d)
        
        # 3. Compute the 3 coupling coordinates (the Triune relational linking parameters)
        # Representing the normalized inner-product resonances between the three trees
        c_life_knowledge = float(np.dot(v_life, v_knowledge) / (np.linalg.norm(v_life) * np.linalg.norm(v_knowledge) + 1e-9))
        c_knowledge_wisdom = float(np.dot(v_knowledge, v_wisdom) / (np.linalg.norm(v_knowledge) * np.linalg.norm(v_wisdom) + 1e-9))
        c_life_wisdom = float(np.dot(v_life, v_wisdom) / (np.linalg.norm(v_life) * np.linalg.norm(v_wisdom) + 1e-9))
        
        coupling_3d = np.array([c_life_knowledge, c_knowledge_wisdom, c_life_wisdom])
        
        # 4. Concatenate base and coupling to form the 75D Triune Logos Plenum
        plenum_75d = np.concatenate([stabilized_72d, coupling_3d])
        return plenum_75d

    def _ensure_24d(self, vec: np.ndarray) -> np.ndarray:
        if len(vec) < 24:
            return np.pad(vec, (0, 24 - len(vec)))
        elif len(vec) > 24:
            return vec[:24]
        return vec
