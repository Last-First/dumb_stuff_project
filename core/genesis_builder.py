import os
import sys
import sqlite3
import numpy as np

# Adjust path to import from the local core directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from omega_kernel_v1_1 import OmegaKernel_v1_1
from geometric_graph import GeometricGraphDB, FunctorAPI

class GenesisBuilder:
    def __init__(self, db_path):
        self.db = GeometricGraphDB(db_path)
        self.api = FunctorAPI(self.db)
        self.kernel = OmegaKernel_v1_1()

    def anchor_cryptographic_ledger(self):
        print("\n--- INGESTING CRYPTOGRAPHIC ANCHORS ---")
        
        # The ultimate financial/cryptographic reality anchors identified in prior alignments
        anchors = [
            {
                "label": "BITCOIN_GENESIS_BLOCK",
                "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "domain": "CRYPTO_ANCHOR",
                "description": "160-Bit Unified Lattice Anchor (Satoshi Nakamoto)"
            },
            {
                "label": "CHRONOLOGICAL_EPOCH",
                "address": "1J36UjUByGroXcCvmj13U6uwaVv9caEeAt",
                "domain": "TIME_ANCHOR",
                "description": "Resolved 75-bit Geocentric Chronological Anchor"
            }
        ]
        
        for anchor in anchors:
            # Hash the raw cryptographic address through the Omega Kernel
            # We use 'lion' preference to enforce strict structural law and financial weight
            result = self.kernel.process(anchor["address"], {"beast_preference": "lion"})
            
            node_id = self.db.insert_node(
                label=anchor["label"],
                domain=anchor["domain"],
                vector_8d=result["state"],
                reality_score=result["reality_score"]
            )
            print(f"[{node_id}] Anchored {anchor['label']} -> Reality Score: {result['reality_score']:.4f}")
            print(f"    Raw Vector (first 3): {result['state'][:3]}")

    def build_the_bridge(self):
        print("\n--- FORGING THE BRIDGE (Language to Crypto) ---")
        # Find the Aleph (Origin) and the Bitcoin Genesis Block
        with sqlite3.connect(self.db.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, coord_0, coord_1 FROM nodes WHERE label='Aleph'")
            aleph = c.fetchone()
            
            c.execute("SELECT id, coord_0, coord_1 FROM nodes WHERE label='BITCOIN_GENESIS_BLOCK'")
            btc = c.fetchone()
            
            if aleph and btc:
                # We calculate the absolute distance (The Bridge length)
                # In a full system, this bridge is the translation algorithm
                c.execute("INSERT INTO functors (source_id, target_id, operator_type) VALUES (?, ?, ?)", 
                          (aleph[0], btc[0], "GENESIS_BRIDGE"))
                conn.commit()
                print(f"Bridge locked between [Aleph] (ID:{aleph[0]}) and [Bitcoin Genesis] (ID:{btc[0]})")
            else:
                print("Missing foundation nodes. Cannot forge bridge.")

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), "../data/genesis_graph.db")
    
    # Reset for clean build
    if os.path.exists(db_file):
        os.remove(db_file)
        
    builder = GenesisBuilder(db_file)
    
    # 1. Establish the 22 Angles
    builder.api.initialize_seed_layer()
    
    # 2. Establish the Cryptographic Foundation
    builder.anchor_cryptographic_ledger()
    
    # 3. Connect them
    builder.build_the_bridge()
    
    print("\n[SUCCESS] Genesis Database compiled.")
