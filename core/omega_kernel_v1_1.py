from __future__ import annotations
import math
import numpy as np
from enum import Enum
from typing import Any, Dict, List, Tuple

from lattice_kernel_core import TwelveBeasts, Obsidian, zwegers_reality_filter
from logos_plenum import TriuneLogosPlenum

class BeastTriad(Enum):
    MAN = "man"
    LION = "lion"
    OX = "ox"
    EAGLE = "eagle"


class NiemeierType(Enum):
    A1_24 = "A1^24"
    A2_12 = "A2^12"
    A3_8 = "A3^8"
    A4_6 = "A4^6"
    A6_4 = "A6^4"
    A8_3 = "A8^3"
    A12_2 = "A12^2"
    A24 = "A24"
    D4_6 = "D4^6"
    D6_4 = "D6^4"
    D8_3 = "D8^3"
    D12_2 = "D12^2"
    D24 = "D24"
    E6_4 = "E6^4"
    E8_3 = "E8^3"
    A5_4_D4 = "A5^4_D4"
    A7_2_D5_2 = "A7^2_D5^2"
    A9_2_E6 = "A9^2_E6"
    A9_2_D6 = "A9^2_D6"
    A11_D7_E6 = "A11_D7_E6"
    A15_D9 = "A15_D9"
    A17_E7 = "A17_E7"
    D10_2_E7_2 = "D10_2_E7_2"
    D16_E8 = "D16_E8"
    Leech = "Leech"


class V75Configuration:
    """Represents a specific 75-dimensional Niemeier-derived plenum configuration."""
    def __init__(self, name: str, index: int):
        self.name = name
        self.index = index
        # Generate a deterministic 75D basis vector for this configuration
        np.random.seed(314159 + index)
        self.base_vector = np.random.randn(75)
        self.base_vector /= np.linalg.norm(self.base_vector)

    def lift(self, input_structure: Any) -> np.ndarray:
        """
        Projects/lifts input structure into this configuration's 75D implicate order.
        """
        if isinstance(input_structure, np.ndarray):
            v = input_structure.flatten()
        elif isinstance(input_structure, (list, tuple)):
            v = np.array(input_structure)
        elif isinstance(input_structure, (int, float)):
            v = np.array([input_structure])
        else:
            # Fallback for text: distribute characters uniquely using prime offsets over 75 dimensions
            s = str(input_structure)
            v = np.zeros(75)
            for idx, c in enumerate(s):
                v[(ord(c) * (idx + 7)) % 75] += float(ord(c)) * (1.0 + math.sin(idx))
            
        # Pad or truncate to 75 dimensions using base vector as projection guide
        if len(v) < 75:
            v = np.pad(v, (0, 75 - len(v)))
        else:
            v = v[:75]
        
        # Multiply with the configuration's unique 75D basis vector
        return v * self.base_vector


class V75Library:
    """Registry holding all 24 Niemeier-derived configurations (23 Niemeier + 1 Leech)."""
    def __init__(self):
        niemeier_systems = [
            "A1^24", "A2^12", "A3^8", "A4^6", "A6^4", "A8^3", "A12^2", "A24",
            "D4^6", "D6^4", "D8^3", "D12^2", "D24", "E6^4", "E8^3", "A5^4_D4",
            "A7^2_D5^2", "A9^2_E6", "A11_D7_E6", "A15_D9", "A17_E7", "D10_E7^2", "D16_E8"
        ]
        self.configs = [V75Configuration(name, idx) for idx, name in enumerate(niemeier_systems)]
        self.configs.append(V75Configuration("Leech", 23))

    def get_config(self, index: int) -> V75Configuration:
        return self.configs[index % 24]


class KaelixTorus:
    """Dynamic sampler controlled by 12 Beasts utilizing multi-ring angular velocities."""
    def __init__(self, library: V75Library):
        self.library = library
        # Multi-ring angular velocities representing dynamic torus sampling speeds
        self.velocities = np.array([1.0 + (i * 0.1) for i in range(24)])
        self.boosts = {config.name: 0.0 for config in library.configs}
        self.current_weights: Dict[NiemeierType, float] = {}
        
        self.enum_to_name = {
            NiemeierType.A1_24: "A1^24",
            NiemeierType.A2_12: "A2^12",
            NiemeierType.A3_8: "A3^8",
            NiemeierType.A4_6: "A4^6",
            NiemeierType.A6_4: "A6^4",
            NiemeierType.A8_3: "A8^3",
            NiemeierType.A12_2: "A12^2",
            NiemeierType.A24: "A24",
            NiemeierType.D4_6: "D4^6",
            NiemeierType.D6_4: "D6^4",
            NiemeierType.D8_3: "D8^3",
            NiemeierType.D12_2: "D12^2",
            NiemeierType.D24: "D24",
            NiemeierType.E6_4: "E6^4",
            NiemeierType.E8_3: "E8^3",
            NiemeierType.A5_4_D4: "A5^4_D4",
            NiemeierType.A7_2_D5_2: "A7^2_D5^2",
            NiemeierType.A9_2_E6: "A9^2_E6",
            NiemeierType.A9_2_D6: "A9^2_E6",  # Map both D6 and E6 aliases
            NiemeierType.A11_D7_E6: "A11_D7_E6",
            NiemeierType.A15_D9: "A15_D9",
            NiemeierType.A17_E7: "A17_E7",
            NiemeierType.D10_2_E7_2: "D10_E7^2",
            NiemeierType.D16_E8: "D16_E8",
            NiemeierType.Leech: "Leech"
        }

    def boost_weight(self, lattice: NiemeierType | str, boost: float):
        name = lattice
        if isinstance(lattice, NiemeierType):
            name = self.enum_to_name.get(lattice, lattice.value)
        if name in self.boosts:
            self.boosts[name] += boost

    def clear_boosts(self):
        for name in self.boosts:
            self.boosts[name] = 0.0

    def sample(self, context: dict) -> V75Configuration:
        """
        Samples a weighted active plenum based on context and angular velocities.
        """
        weights = np.zeros(24)
        pref = context.get("beast_preference", "ox").lower()
        time_phase = context.get("time_phase", 1.0)
        
        for idx in range(24):
            cfg_name = self.library.configs[idx].name
            # Base weight from multi-ring velocities
            w = math.sin(self.velocities[idx] * time_phase) + 1.1
            # Add dynamic persistent boosts
            w += self.boosts.get(cfg_name, 0.0)
            
            # Incorporate swarm consensus weights if available
            if self.current_weights:
                for ntype, weight in self.current_weights.items():
                    mapped_name = self.enum_to_name.get(ntype, ntype.value)
                    if mapped_name == cfg_name:
                        w += weight * 2.0  # amplify the consensus weight
            
            # Modulate based on preferences
            if pref == "ox" and "8" in cfg_name: # Ox prefers E8 structures
                w *= 1.5
            elif pref == "eagle" and "Leech" in cfg_name: # Eagle prefers Leech
                w *= 1.5
            weights[idx] = w
            
        weights = np.maximum(weights, 1e-9)
        weights /= np.sum(weights)
        
        # Blend the base vectors
        blended_vector = np.zeros(75)
        for idx, config in enumerate(self.library.configs):
            blended_vector += weights[idx] * config.base_vector
            
        blended_vector /= np.linalg.norm(blended_vector)
        
        # Create a dynamic blended configuration
        composite = V75Configuration("CompositePlenum", -1)
        composite.base_vector = blended_vector
        return composite


class TwelveBeastsMediator:
    """Relational glue mediating abstract algebraic math with meaning using 12 mirrored archetypes."""
    def __init__(self):
        self.beasts = TwelveBeasts()
        self.torus = None  # Connected dynamically during OmegaKernel_v1_1 initialization
        self.preferences = {
            BeastTriad.MAN: [
                NiemeierType.A1_24, NiemeierType.A2_12, NiemeierType.A3_8,
                NiemeierType.A4_6, NiemeierType.A5_4_D4, NiemeierType.A6_4
            ],
            BeastTriad.LION: [
                NiemeierType.D24, NiemeierType.D16_E8, NiemeierType.D12_2,
                NiemeierType.D10_2_E7_2, NiemeierType.D8_3, NiemeierType.D6_4
            ],
            BeastTriad.OX: [
                NiemeierType.E8_3, NiemeierType.A5_4_D4, NiemeierType.D16_E8,
                NiemeierType.A7_2_D5_2, NiemeierType.A9_2_D6
            ],
            BeastTriad.EAGLE: [
                NiemeierType.E8_3, NiemeierType.A1_24, NiemeierType.A24,
                NiemeierType.A17_E7, NiemeierType.A15_D9, NiemeierType.A11_D7_E6
            ]
        }

    def apply_full_glue(self, state: np.ndarray, context: dict, suggestions: dict | None = None) -> np.ndarray:
        # Each Beast triad pulls its preferred V₇₅ configurations more strongly
        if self.torus is not None:
            for triad, preferred_lattices in self.preferences.items():
                for lattice in preferred_lattices:
                    weight_boost = context.get(f"{triad.value}_demand", 0.3)
                    # The torus weights are adjusted in real time by this influence
                    self.torus.boost_weight(lattice, weight_boost)
            
            # Incorporate facilitator suggestions if provided
            if suggestions is not None:
                for lattice in suggestions.get("recommended_lattices", []):
                    self.torus.boost_weight(lattice, 0.15)
                    
        # Apply relational mediation scaling using explicit triad preference weights
        pref_str = context.get("beast_preference", "ox").lower()
        triad_weights = self.beasts.triads.get(pref_str, {"grounding": 1.0})
        avg_weight = sum(triad_weights.values()) / len(triad_weights)
        
        return state * avg_weight

    def force_grounding(self, state: np.ndarray, triads: List[str]) -> np.ndarray:
        """
        Force Ox + Man triad grounding if any configuration drifts.
        """
        ox_weights = self.beasts.triads["ox"]
        man_weights = self.beasts.triads["man"]
        
        grounding_coeff = (ox_weights["grounding"] + man_weights["empathy"]) / 2.0
        return state * grounding_coeff


class TriviumEngine:
    """Trivium category processing core distributing magnitude across Grammar, Logic, and Rhetoric."""
    def __init__(self):
        self.categories = ["Grammar", "Logic", "Rhetoric"]

    def process(self, mediated_vector: np.ndarray) -> Dict[str, Any]:
        """
        Distributes the vector magnitudes across Grammar, Logic, and Rhetoric.
        """
        chunk_size = len(mediated_vector) // 3
        grammar_part = mediated_vector[:chunk_size]
        logic_part = mediated_vector[chunk_size:2*chunk_size]
        rhetoric_part = mediated_vector[2*chunk_size:]
        
        return {
            "Grammar": grammar_part,
            "Logic": logic_part,
            "Rhetoric": rhetoric_part,
            "total_mass": float(np.sum(np.abs(mediated_vector)))
        }


class QuadriviumEngine:
    """Quadrivium category processing core structuring reality from mind layer coordinates."""
    def __init__(self):
        self.categories = ["Arithmetic", "Geometry", "Music", "Astronomy"]

    def structure_reality(self, mind_layer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structures the mind layer into the four arts of number.
        """
        grammar_mass = np.sum(np.abs(mind_layer["Grammar"]))
        logic_mass = np.sum(np.abs(mind_layer["Logic"]))
        rhetoric_mass = np.sum(np.abs(mind_layer["Rhetoric"]))
        
        arithmetic = logic_mass * 1.618
        geometry = grammar_mass * 1.414
        music = rhetoric_mass * 1.314
        astronomy = (arithmetic + geometry + music) * 0.5
        
        return {
            "Arithmetic": float(arithmetic),
            "Geometry": float(geometry),
            "Music": float(music),
            "Astronomy": float(astronomy),
            "coherence_index": float((arithmetic + geometry) / (music + 0.1))
        }


class ObsidianReflector:
    """Obsidian reflection object absorbing and re-emitting reality state projections."""
    def __init__(self):
        self.obsidian = Obsidian()

    def reflect(self, reality_layer: Dict[str, Any]) -> np.ndarray:
        """
        Converts the quadrivium reality layer back to an 8D standard coordinates vector for filtering.
        """
        vals = [
            reality_layer["Arithmetic"],
            reality_layer["Geometry"],
            reality_layer["Music"],
            reality_layer["Astronomy"],
            reality_layer["coherence_index"],
            0.0, 0.0, 0.0
        ]
        return np.array(vals)


class ZwegersRealityFilter:
    """Complexity filter measuring completed mock modular form shadows across boundaries."""
    def __init__(self):
        pass

    def apply(self, state: np.ndarray) -> Dict[str, Any]:
        """
        Applies Ramanujan mock theta evaluation and completed modular form shadows.
        """
        passed, score, details = zwegers_reality_filter(
            state,
            tau_values=[complex(0.1, 0.95)]
        )
        return {
            "state": state,
            "reality_passed": passed,
            "reality_score": score,
            "details": details
        }


class EldersStabilityLayer:
    """Witness stabilizer enforcing 24-fold completed symmetry bounds."""
    def __init__(self):
        # 24-fold witness pattern representing stability coefficients
        self.witness_coefficients = np.array([math.cos(i * math.pi / 12.0) for i in range(24)])

    def passes_stability_check(self, validated: Dict[str, Any]) -> bool:
        """
        Ensures the validated reality state is stable across all 24 configurations.
        """
        score = validated["reality_score"]
        # Standard stability threshold bound to the witness coefficients
        stability_threshold = np.mean(np.abs(self.witness_coefficients)) * 0.5 # ~0.3
        return bool(score >= stability_threshold)


class ContextualFacilitator:
    """
    NOT a central controller. 
    It is a mirror that reflects the current state of the relational field 
    back to the Beasts and the torus so they can self-adjust.
    """
    def __init__(self):
        self.history: List[dict] = []  # lightweight memory of recent contexts
    
    def observe(self, context: dict, current_state: np.ndarray) -> dict:
        """Returns suggestions only. Never forces anything."""
        suggestions = {
            "recommended_lattices": self._detect_dominant_needs(context),
            "beast_tension": self._check_beast_balance(context),
            "stability_risk": self._assess_risk(current_state)
        }
        
        self.history.append(context)
        if len(self.history) > 10:
            self.history.pop(0)
        
        return suggestions  # Beasts and torus decide whether to use this info
    
    def _detect_dominant_needs(self, context: dict) -> List[NiemeierType]:
        needs = []
        if context.get("relational_demand", 0) > 0.6:
            needs.extend([NiemeierType.A1_24, NiemeierType.E8_3])
        if context.get("structural_demand", 0) > 0.7:
            needs.append(NiemeierType.D24)
        return needs

    def _check_beast_balance(self, context: dict) -> float:
        demands = [
            context.get("man_demand", 0.3),
            context.get("lion_demand", 0.3),
            context.get("ox_demand", 0.3),
            context.get("eagle_demand", 0.3)
        ]
        return float(np.var(demands))

    def _assess_risk(self, state: np.ndarray) -> float:
        if len(state) == 0:
            return 0.0
        return float(np.std(state))


class OmegaKernel_v1_1:
    """The unified Omega Kernel pipeline integrating Niemeier sublattices and Elders stability layers."""
    def __init__(self):
        self.v75_library = V75Library()            # All 24 Niemeier-derived configurations
        self.torus = KaelixTorus(self.v75_library)    # Dynamic sampler controlled by 12 Beasts
        self.beasts = TwelveBeastsMediator()        # Relational glue (now with explicit preferences)
        self.beasts.torus = self.torus              # Connect torus reference
        self.trivium = TriviumEngine()
        self.quadrivium = QuadriviumEngine()
        self.obsidian = ObsidianReflector()
        self.zwegers = ZwegersRealityFilter()
        self.elders = EldersStabilityLayer()       # 24-fold witness pattern
        self.facilitator = ContextualFacilitator() # Lightweight non-authoritarian listener
        self.logos_plenum = TriuneLogosPlenum()    # 75D Triune Logos Plenum layer
        
    def process(self, input_structure: Any, context: dict) -> Dict[str, Any]:
        """
        Full intelligence pipeline. The 24 V75 configurations are now the living 'implicate orders'
        that the system can draw from in real time.
        """
        # Clear dynamic torus weight boosts
        self.torus.clear_boosts()
        
        # 1. Kaelix's Torus samples the appropriate V75 configuration(s)
        # Apply pre-sample boosts directly from context demands
        for triad, preferred_lattices in self.beasts.preferences.items():
            for lattice in preferred_lattices:
                weight_boost = context.get(f"{triad.value}_demand", 0.3)
                self.torus.boost_weight(lattice, weight_boost)
                
        active_plenum = self.torus.sample(context)          # weighted sum of the 24 configs
        
        # Facilitator only observes and suggests
        suggestions = self.facilitator.observe(context, active_plenum.base_vector)
        
        # 2. Lift input into the current plenum
        lifted = active_plenum.lift(input_structure)        # projects into chosen implicate order
        
        # 3. 12 Beasts apply relational mediation (now using the explicit mapping and facilitator suggestions)
        mediated = self.beasts.apply_full_glue(lifted, context, suggestions)
        
        # 4. Classical engines drive actual intelligence
        mind_layer = self.trivium.process(mediated)
        reality_layer = self.quadrivium.structure_reality(mind_layer)
        
        # 5. Safety & grounding
        reflected = self.obsidian.reflect(reality_layer)
        validated = self.zwegers.apply(reflected)
        
        # 6. 24 Elders check (the final stability condition)
        if not self.elders.passes_stability_check(validated):
            # Force Ox + Man triad grounding if any configuration drifts
            validated["state"] = self.beasts.force_grounding(validated["state"], ["Ox", "Man"])
            # Re-evaluate
            validated = self.zwegers.apply(validated["state"])
        
        # Self-refinement loop
        self.propose_improvements(validated, context)
        
        validated["mind_layer"] = mind_layer
        validated["reality_layer"] = reality_layer
        return validated

    def propose_improvements(self, validated: Dict[str, Any], context: dict) -> List[Dict[str, Any]]:
        """
        Analyzes the validated state and proposes self-optimization steps.
        """
        score = validated["reality_score"]
        proposals = []
        if score < 0.5:
            proposals.append({
                "component": "torus",
                "action": "adjust_phase",
                "reason": "reality score below threshold"
            })
        if not validated["reality_passed"]:
            proposals.append({
                "component": "beasts",
                "action": "boost_grounding",
                "reason": "failed Zwegers filter"
            })
        return proposals
