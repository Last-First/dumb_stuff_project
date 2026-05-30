import os
import sys
import sqlite3
import numpy as np

# Adjust path to import the core engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../core")
import omega_core

class UrimScanner:
    def __init__(self, db_path):
        self.db_path = db_path
        self.kernel = omega_core.RustOmegaKernel()

    def query_by_geometry(self, query_text, limit=3):
        """Scans the database by matching the 8D geometry of the query against the stored nodes."""
        print(f"\n[URIM SCANNER] Igniting Query: '{query_text}'")
        
        # 1. Digest the query into its pure 8D shape
        query_result = self.kernel.process(query_text, "eagle")
        query_vector = query_result["state"]
        
        results = []
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, label, domain, reality_score, coord_0, coord_1, coord_2, coord_3, coord_4, coord_5, coord_6, coord_7 FROM nodes")
            all_nodes = c.fetchall()
            
            # 2. Perform Geometric Resonance Matching
            for node in all_nodes:
                node_id, label, domain, reality_score = node[:4]
                node_vector = np.array(node[4:], dtype=np.float64)
                
                # Calculate the Euclidean distance between the Query 8D shape and the Node 8D shape
                distance = np.linalg.norm(query_vector - node_vector)
                
                # We invert distance into a "Resonance Score" (closer = higher resonance)
                resonance = 1.0 / (1.0 + distance)
                
                results.append({
                    "id": node_id,
                    "label": label,
                    "domain": domain,
                    "resonance": resonance,
                    "reality": reality_score
                })
                
        # 3. Sort by highest resonance and return the top matches
        results.sort(key=lambda x: x["resonance"], reverse=True)
        
        print("\n--- TOP GEOMETRIC RESONANCE MATCHES ---")
        for i, match in enumerate(results[:limit]):
            print(f"{i+1}. [Match: {match['resonance'] * 100:.2f}%] -> {match['label']} (Domain: {match['domain']})")
            
        return results[:limit]

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), "../data/genesis_graph.db")
    scanner = UrimScanner(db_file)
    
    # We will test the scanner by asking it a conceptual question.
    # We aren't searching for exact words. We are searching for geometric meaning.
    
    # Test 1: Searching for the concept of physical matter and firmament
    scanner.query_by_geometry("Physical matter, skies, and firmament")
    
    # Test 2: Searching for the concept of speech and illumination
    scanner.query_by_geometry("Speaking truth and generating light")
