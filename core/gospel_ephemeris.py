from __future__ import annotations
import os
import sys
import csv
import math
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Any

# Skyfield imports for rigorous astronomical ephemeris processing
from skyfield.api import load, wgs84
from skyfield.timelib import Time

# Project imports
from python.logos_plenum import TriuneLogosPlenum

class GospelEphemerisHarmonizer:
    """
    Harmonizes astronomical ephemeris data (NASA JPL DE421),
    biblical/gospel literary alignments (Mark = Sun, Matthew = Moon, etc.),
    and the cryptographic 160-bit Bitcoin puzzles into the 75D Triune Logos Plenum.
    """
    def __init__(
        self,
        bsp_path: str = os.path.join(os.path.dirname(__file__), "../data/de406.bsp"),
        puzzle_csv_path: str = os.path.join(os.path.dirname(__file__), "../data/the_160_unified.csv")
    ):
        self.bsp_path = bsp_path
        self.puzzle_csv_path = puzzle_csv_path
        
        # Load Skyfield Ephemeris
        if os.path.exists(bsp_path):
            self.eph = load(bsp_path)
            self.sun = self.eph['sun']
            self.earth = self.eph['earth']
            self.moon = self.eph['moon']
            self.mercury = self.eph['mercury']
            self.venus = self.eph['venus']
            self.mars = self.eph['mars']
            self.jupiter = self.eph['jupiter_barycenter']
            self.saturn = self.eph['saturn_barycenter']
        else:
            raise FileNotFoundError(f"JPL Ephemeris file not found at {bsp_path}")
            
        self.ts = load.timescale()
        self.plenum_synthesizer = TriuneLogosPlenum()
        
        # Load 160 Cryptographic Puzzles
        self.puzzles = self._load_puzzles()

    def _load_puzzles(self) -> List[Dict[str, Any]]:
        puzzles = []
        if os.path.exists(self.puzzle_csv_path):
            with open(self.puzzle_csv_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert WIF private key to a deterministic seed vector
                    wif = row.get("WIF", "")
                    if wif:
                        # Convert WIF chars to simple seed list
                        seed_vector = [ord(c) for c in wif]
                        # Pad or truncate to 1000 dimensions for Griess projector compatibility
                        if len(seed_vector) < 1000:
                            seed_vector = seed_vector + [0] * (1000 - len(seed_vector))
                        else:
                            seed_vector = seed_vector[:1000]
                        
                        # Project down to 75D using the Griess projector
                        projected_75d = self.plenum_synthesizer.griess_projector.project(seed_vector)
                        
                        puzzles.append({
                            "bits": int(row.get("Bits", 0)),
                            "actual_addr": row.get("Actual_Addr", ""),
                            "wif": wif,
                            "status": row.get("Status", ""),
                            "vector_75d": projected_75d
                        })
        return puzzles

    def compute_gospel_alignment(self, year: int, month: int, day: int, hour: int = 12) -> Dict[str, Any]:
        """
        Computes the planetary positions for a given date/time and maps them directly to the
        symbolic Triune Trees based on the Gospel astronomical associations:
        - Tree of Life (Mark: Solar & Inner Planetary paths: Sun, Mercury, Venus)
        - Tree of Knowledge (Matthew/Luke: Lunar & Local Planetary paths: Moon, Mars, Jupiter)
        - Tree of Wisdom (John: Cosmic/Stellar coordinates: Saturn + Pole Star/Constellation vectors)
        """
        # 1. Resolve Skyfield Time
        t = self.ts.utc(year, month, day, hour, 0, 0)
        
        # 2. Extract geocentric astronomical coordinates (right ascension/declination converted to 24D features)
        pos_sun = self.earth.at(t).observe(self.sun).apparent().position.au
        pos_moon = self.earth.at(t).observe(self.moon).apparent().position.au
        pos_mercury = self.earth.at(t).observe(self.mercury).apparent().position.au
        pos_venus = self.earth.at(t).observe(self.venus).apparent().position.au
        pos_mars = self.earth.at(t).observe(self.mars).apparent().position.au
        pos_jupiter = self.earth.at(t).observe(self.jupiter).apparent().position.au
        pos_saturn = self.earth.at(t).observe(self.saturn).apparent().position.au
        
        # 3. Formulate the Three Trees (24D each, constructed deterministically from 3D astronomical positions)
        v_life = self._astronomical_to_24d(pos_sun, pos_mercury, pos_venus)
        v_knowledge = self._astronomical_to_24d(pos_moon, pos_mars, pos_jupiter)
        v_wisdom = self._astronomical_to_24d(pos_saturn, pos_saturn * 1.5, pos_sun * -1.0) # John stellar opposition
        
        # 4. Synthesize the 75-dimensional Triune Logos Plenum
        v75_plenum = self.plenum_synthesizer.synthesize_plenum(v_life, v_knowledge, v_wisdom)
        
        # 5. Harmonize with the 160 Cryptographic Puzzles
        # Calculate which Bitcoin puzzle private key aligns closest homologically
        best_puzzle = None
        max_similarity = -2.0
        
        for p in self.puzzles:
            similarity = float(np.dot(v75_plenum, p["vector_75d"]))
            if similarity > max_similarity:
                max_similarity = similarity
                best_puzzle = p
                
        return {
            "date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:00 UTC",
            "julian_date": float(t.tt),
            "v75_plenum": v75_plenum,
            "trees": {
                "life_mark": v_life,
                "knowledge_matthew": v_knowledge,
                "wisdom_john": v_wisdom
            },
            "best_cryptographic_anchor": {
                "bits": best_puzzle["bits"] if best_puzzle else 0,
                "actual_addr": best_puzzle["actual_addr"] if best_puzzle else "",
                "wif": best_puzzle["wif"] if best_puzzle else "",
                "similarity": max_similarity
            }
        }

    def _astronomical_to_24d(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> np.ndarray:
        """
        Deterministically expands three 3D planetary coordinate vectors into a 24D tree feature space.
        """
        combined = np.concatenate([p1, p2, p3]) # 9D
        # Pad with cross-products and harmonics to reach exactly 24 dimensions
        cross12 = np.cross(p1, p2)
        cross23 = np.cross(p2, p3)
        cross13 = np.cross(p1, p3)
        combined = np.concatenate([combined, cross12, cross23, cross13]) # 18D
        
        # Add 6 structural harmonics
        harmonics = np.array([
            np.linalg.norm(p1),
            np.linalg.norm(p2),
            np.linalg.norm(p3),
            np.dot(p1, p2),
            np.dot(p2, p3),
            np.dot(p1, p3)
        ])
        combined = np.concatenate([combined, harmonics]) # 24D
        
        # Normalize the 24D tree vector
        norm = np.linalg.norm(combined)
        if norm > 1e-9:
            combined /= norm
        return combined
