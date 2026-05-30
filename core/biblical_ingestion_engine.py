import os
import sys
import sqlite3
import numpy as np

# Adjust path to import the core engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from omega_kernel_v1_1 import OmegaKernel_v1_1
from geometric_graph import GeometricGraphDB

class BiblicalIngestionEngine:
    def __init__(self, db_path):
        self.db = GeometricGraphDB(db_path)
        self.kernel = OmegaKernel_v1_1()

    def ingest_verse(self, book, chapter, verse, text, root_words=None):
        """Processes a Biblical verse through the Omega Kernel and stores it as an 8D Node"""
        reference = f"{book} {chapter}:{verse}"
        print(f"\n[INGESTING] {reference} -> '{text}'")
        
        # Digest the raw text through the Kernel (Using John/Wisdom for high-level semantic reality)
        result = self.kernel.process(text, {"beast_preference": "man"})
        
        # Insert the Verse Node
        verse_id = self.db.insert_node(
            label=reference,
            domain="SCRIPTURE_VERSE",
            vector_8d=result["state"],
            reality_score=result["reality_score"]
        )
        print(f"  -> Anchored in Database (ID: {verse_id}) | Reality Score: {result['reality_score']:.4f}")
        
        # If Hebrew/Greek root words are provided, we anchor them individually
        # and create a Functor edge linking them to the Verse.
        if root_words:
            for root in root_words:
                # Digest the root word
                root_result = self.kernel.process(root, {"beast_preference": "ox"}) # Ox for foundational structure
                
                root_id = self.db.insert_node(
                    label=root,
                    domain="BIBLICAL_ROOT",
                    vector_8d=root_result["state"],
                    reality_score=root_result["reality_score"]
                )
                
                # Forge the geometric link (Edge) in the graph
                with sqlite3.connect(self.db.db_path) as conn:
                    c = conn.cursor()
                    c.execute("INSERT INTO functors (source_id, target_id, operator_type) VALUES (?, ?, ?)", 
                              (root_id, verse_id, "CONSTITUENT_ROOT"))
                    conn.commit()
                print(f"  -> Linked Root Word: [{root}] (ID: {root_id}) to Verse")

def run_genesis_ingestion():
    db_file = os.path.join(os.path.dirname(__file__), "../data/genesis_graph.db")
    engine = BiblicalIngestionEngine(db_file)
    
    print("=== OMEGA KERNEL: BIBLICAL INGESTION PIPELINE ACTIVE ===")
    
    # Mock dataset of Genesis 1:1-3 (In reality, this would read from a massive CSV/JSON)
    dataset = [
        {
            "book": "Genesis", "chapter": 1, "verse": 1,
            "text": "In the beginning God created the heavens and the earth.",
            "roots": ["Bereshit", "Elohim", "Bara", "Shamayim", "Erets"]
        },
        {
            "book": "Genesis", "chapter": 1, "verse": 2,
            "text": "Now the earth was formless and empty, darkness was over the surface of the deep, and the Spirit of God was hovering over the waters.",
            "roots": ["Tohu", "Bohu", "Choshek", "Ruach"]
        },
        {
            "book": "Genesis", "chapter": 1, "verse": 3,
            "text": "And God said, Let there be light, and there was light.",
            "roots": ["Amar", "Or"]
        }
    ]
    
    for data in dataset:
        engine.ingest_verse(
            book=data["book"],
            chapter=data["chapter"],
            verse=data["verse"],
            text=data["text"],
            root_words=data["roots"]
        )
        
    print("\n[SUCCESS] Pipeline Execution Complete. Data physically anchored to the E8 Lattice.")

if __name__ == "__main__":
    run_genesis_ingestion()
