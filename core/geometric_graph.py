import sqlite3
import numpy as np
import math
import os
from omega_kernel_v1_1 import OmegaKernel_v1_1

# The 22 Hebrew Letters (The Seed Vectors)
HEBREW_ALPHABET = [
    "Aleph", "Beth", "Gimel", "Daleth", "He", "Waw", "Zayin", "Heth",
    "Teth", "Yodh", "Kaph", "Lamedh", "Mem", "Nun", "Samekh", "Ayin",
    "Pe", "Sadhe", "Qoph", "Resh", "Sin", "Taw"
]

class GeometricGraphDB:
    def __init__(self, db_path="universal_graph.db"):
        self.db_path = db_path
        self.kernel = OmegaKernel_v1_1()
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Nodes Table (Entities)
            c.execute('''
                CREATE TABLE IF NOT EXISTS nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    reality_score REAL NOT NULL,
                    coord_0 REAL, coord_1 REAL, coord_2 REAL, coord_3 REAL,
                    coord_4 REAL, coord_5 REAL, coord_6 REAL, coord_7 REAL
                )
            ''')
            # Edges Table (Functors / Relationships)
            c.execute('''
                CREATE TABLE IF NOT EXISTS functors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER,
                    target_id INTEGER,
                    operator_type TEXT,
                    FOREIGN KEY(source_id) REFERENCES nodes(id),
                    FOREIGN KEY(target_id) REFERENCES nodes(id)
                )
            ''')
            conn.commit()

    def insert_node(self, label, domain, vector_8d, reality_score):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO nodes (label, domain, reality_score, 
                coord_0, coord_1, coord_2, coord_3, coord_4, coord_5, coord_6, coord_7)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (label, domain, reality_score, *vector_8d[:8]))
            return c.lastrowid

class FunctorAPI:
    def __init__(self, graph: GeometricGraphDB):
        self.graph = graph
        self.kernel = graph.kernel

    def initialize_seed_layer(self):
        print("Initializing Level 1: The 22 Hebrew Seed Vectors...")
        # 360 degrees / 22 letters = ~16.3636 degrees per letter
        angle_increment = 360.0 / 22.0
        
        for i, letter in enumerate(HEBREW_ALPHABET):
            angle = i * angle_increment
            
            # Create a raw structural seed using sine/cosine of the geometric angle
            # This embeds the physical geometric angle directly into the high-dimensional projection
            base_signal = np.array([math.cos(math.radians(angle)), math.sin(math.radians(angle))])
            
            # Push through Omega Kernel to get 8D coordinates and Reality Score
            result = self.kernel.process(base_signal, {"beast_preference": "ox"})
            
            node_id = self.graph.insert_node(
                label=letter,
                domain="HEBREW_SEED",
                vector_8d=result["state"],
                reality_score=result["reality_score"]
            )
            print(f"[{node_id}] Seed Vector Anchored: {letter:<8} (Angle: {angle:>6.2f}°) | Reality Score: {result['reality_score']:.4f}")

    def phase_inversion(self, label_to_invert):
        # Retrieve the base node
        with sqlite3.connect(self.graph.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, coord_0, coord_1, coord_2, coord_3, coord_4, coord_5, coord_6, coord_7 FROM nodes WHERE label=?", (label_to_invert,))
            row = c.fetchone()
            
        if not row:
            print("Node not found.")
            return
            
        base_id = row[0]
        base_coords = np.array(row[1:])
        
        # Multiply by -1 to get the exact geometric shadow / spiritual opposite
        inverted_coords = base_coords * -1.0
        
        # Calculate reality drop (the opposite is inherently more entropic/chaotic out of the center)
        # We simulate the reality drop by scaling it through the Zwegers boundary
        inverted_result = self.kernel.process(inverted_coords, {"beast_preference": "lion"})
        
        inv_label = f"Inverse_{label_to_invert}"
        inv_id = self.graph.insert_node(
            label=inv_label,
            domain="SHADOW_INVERSE",
            vector_8d=inverted_coords,
            reality_score=inverted_result["reality_score"]
        )
        
        # Create a functor edge linking them
        with sqlite3.connect(self.graph.db_path) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO functors (source_id, target_id, operator_type) VALUES (?, ?, ?)", (base_id, inv_id, "PHASE_INVERSION"))
            conn.commit()
            
        print(f"\n[PHASE INVERSION EXECUTED]")
        print(f"Base Node: {label_to_invert} -> {base_coords[:3]}...")
        print(f"Shadow Node: {inv_label} -> {inverted_coords[:3]}...")
        print(f"Edge 'PHASE_INVERSION' registered between ID {base_id} and {inv_id}")

if __name__ == "__main__":
    # Remove old graph for clean execution
    if os.path.exists("universal_graph.db"):
        os.remove("universal_graph.db")
        
    db = GeometricGraphDB()
    api = FunctorAPI(db)
    
    # Execute Level 1: Lay the foundation
    api.initialize_seed_layer()
    
    # Demonstrate Phase Inversion (Opposites)
    api.phase_inversion("Aleph")
