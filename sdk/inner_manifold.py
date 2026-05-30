import os
import sys
import numpy as np
from urim_scanner import UrimScanner

class InnerManifold:
    """
    Domain 2: Personal Diagnostics & Topological Healing
    This module maps a user's personal emotional/habit topology into the 8D E8 lattice 
    and prescribes structural resolutions based on the Genesis Graph.
    """
    def __init__(self, db_path):
        self.scanner = UrimScanner(db_path)
        
    def map_entropy_friction(self, personal_input):
        """
        Takes a user's personal struggle, habit, or emotional state and projects it 
        into the 8D manifold to identify the core structural distortion.
        """
        print(f"\n[INNER MANIFOLD] Mapping Topological Distortion for: '{personal_input}'")
        
        # Digest the personal input into its 8D shape
        result = self.scanner.kernel.process(personal_input, "lion") 
        distortion_vector = result["state"]
        
        # Determine the structural category:
        # We calculate the sum of the vector to roughly categorize it in our prototype.
        vector_sum = np.sum(distortion_vector)
        
        category = "Unknown"
        if vector_sum < -0.1:
            category = "ENTROPIC (Decay, Drift, Vanity)"
        elif vector_sum > 0.1:
            category = "FRICTION (Conflict, Resistance, Pain)"
        else:
            category = "EXPANDING (Growth, Striving)"
            
        print(f"-> Structural Topology Detected: {category}")
        return distortion_vector, category

    def christotelic_role_assignment(self, personal_history_text):
        """
        Maps the user's history and current topology against the E8 root vectors
        to identify their active archetypal role in the Body.
        """
        print(f"\n[INNER MANIFOLD] Identifying Christotelic Role based on personal history...")
        
        # Instead of a keyword search, we map the entire emotional/historical text 
        # to the nearest biblical archetype (person or concept).
        role_matches = self.scanner.query_by_geometry(personal_history_text, limit=1)
        
        if role_matches:
            primary_role = role_matches[0]
            print(f"-> Active Archetypal Resonance: {primary_role['label']}")
            print(f"-> Resonance Strength: {primary_role['resonance']*100:.1f}%")
            return primary_role
        return None

    def generate_sanctification_sprint(self, current_struggle_text, target_role_text):
        """
        Calculates the shortest geometric path (geodesic) from the user's current 
        'friction state' to their target resolved state, breaking it down into steps.
        """
        print(f"\n[INNER MANIFOLD] Generating Geodesic Sanctification Sprint...")
        print(f"From [Current State]: {current_struggle_text}")
        print(f"To   [Target Role]  : {target_role_text}")
        
        # 1. Get the 8D vector of where the user is currently stuck
        struggle_result = self.scanner.kernel.process(current_struggle_text, "ox")
        start_vec = np.array(struggle_result["state"])
        
        # 2. Get the 8D vector of where the user needs to be
        target_result = self.scanner.kernel.process(target_role_text, "eagle")
        end_vec = np.array(target_result["state"])
        
        # 3. Calculate 3 intermediate waypoints (Interpolation in 8D space)
        # This represents the "Geodesic Path" of transformation.
        steps = 3
        waypoints = []
        for i in range(1, steps + 1):
            fraction = i / (steps + 1)
            # Linear interpolation between the two vectors
            waypoint_vec = start_vec + (end_vec - start_vec) * fraction
            waypoints.append(waypoint_vec)
            
        # 4. For each waypoint, find the nearest biblical verse in the Genesis Graph
        print("\n--- SANCTIFICATION WAYPOINTS ---")
        
        # (For the prototype, we will just use the UrimScanner to find the closest text 
        # to a synthetic "bridge" concept between the two states, since passing raw vectors 
        # directly into the scanner requires a slight modification to urim_scanner.py. 
        # We will synthesize the bridge conceptually for now.)
        
        
        step_1 = self.scanner.query_by_geometry(f"{current_struggle_text} moving toward {target_role_text} step 1", limit=1)
        step_2 = self.scanner.query_by_geometry(f"{current_struggle_text} transforming into {target_role_text} step 2", limit=1)
        step_3 = self.scanner.query_by_geometry(f"The final resolution of {current_struggle_text} into {target_role_text}", limit=1)
        
        print("\n[STEP 1 - The Pivot]:")
        if step_1: print(f"-> Meditate on: {step_1[0]['label']} (Match: {step_1[0]['resonance']*100:.1f}%)")
        
        print("\n[STEP 2 - The Path]:")
        if step_2: print(f"-> Meditate on: {step_2[0]['label']} (Match: {step_2[0]['resonance']*100:.1f}%)")
        
        print("\n[STEP 3 - The Resolution]:")
        if step_3: print(f"-> Meditate on: {step_3[0]['label']} (Match: {step_3[0]['resonance']*100:.1f}%)")

        return {
            "step_1": step_1[0] if step_1 else None,
            "step_2": step_2[0] if step_2 else None,
            "step_3": step_3[0] if step_3 else None
        }

if __name__ == "__main__":
    # Test the Inner Manifold
    db_file = os.path.join(os.path.dirname(__file__), "../data/genesis_graph.db")
    manifold = InnerManifold(db_file)
    
    # 1. Test Entropy/Friction Tagging
    struggle = "I am constantly anxious about money and getting into arguments with my family about the future."
    manifold.map_entropy_friction(struggle)
    
    # 2. Test Role Assignment
    history = "I have spent years quietly fixing broken things behind the scenes, never seeking the spotlight, but always making sure others have what they need to succeed."
    manifold.christotelic_role_assignment(history)
    
    # 3. Test Sanctification Sprint
    manifold.generate_sanctification_sprint(
        current_struggle_text="Anger and resentment toward those who have wronged me",
        target_role_text="A peacemaker who brings reconciliation and grace"
    )
