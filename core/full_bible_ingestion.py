import os
import sys
import json
import sqlite3
import re
import time
import numpy as np

# Import the Blazingly Fast Rust Core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import omega_core

class FullBibleIngestion:
    def __init__(self, db_path, json_path):
        self.db_path = db_path
        self.json_path = json_path
        self.kernel = omega_core.RustOmegaKernel()
        
        # Regex to find Strongs tags like {H1234} or {(H8798)}
        self.strongs_regex = re.compile(r'\{(?:\()?[HG]\d+(?:\))?\}')
        
        # Cache for root words to prevent redundant processing
        self.root_cache = {} 
        self.next_node_id = self._get_next_node_id()

    def _get_next_node_id(self):
        """Retrieve the next auto-increment ID to manually track links during batching"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Ensure tables exist
            c.execute('''CREATE TABLE IF NOT EXISTS nodes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            label TEXT NOT NULL,
                            domain TEXT NOT NULL,
                            reality_score REAL NOT NULL,
                            coord_0 REAL, coord_1 REAL, coord_2 REAL, coord_3 REAL,
                            coord_4 REAL, coord_5 REAL, coord_6 REAL, coord_7 REAL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS functors (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            source_id INTEGER, target_id INTEGER, operator_type TEXT,
                            FOREIGN KEY(source_id) REFERENCES nodes(id),
                            FOREIGN KEY(target_id) REFERENCES nodes(id))''')
            c.execute("SELECT MAX(id) FROM nodes")
            max_id = c.fetchone()[0]
            return (max_id or 0) + 1

    def run(self):
        print(f"=== OMEGA KERNEL: FULL SCRIPTURE INGESTION ===")
        print(f"Loading dataset: {self.json_path}")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)["verses"]
            
        print(f"Loaded {len(data)} verses. Igniting Rust Core...")
        
        nodes_batch = []
        functors_batch = []
        
        start_time = time.time()
        
        for i, entry in enumerate(data):
            if not isinstance(entry, dict) or "book_name" not in entry:
                continue
                
            raw_text = entry.get("text", "")
            book = entry.get("book_name", "")
            chapter = entry.get("chapter", "")
            verse = entry.get("verse", "")
            reference = f"{book} {chapter}:{verse}"
            
            # 1. Extract Strongs Roots and clean the English text
            strongs_tags = self.strongs_regex.findall(raw_text)
            clean_text = self.strongs_regex.sub('', raw_text).replace('  ', ' ').strip()
            
            # 2. Process Verse Geometry via Rust
            verse_result = self.kernel.process(clean_text, "man")
            verse_state = verse_result["state"]
            
            verse_id = self.next_node_id
            self.next_node_id += 1
            
            nodes_batch.append((
                verse_id, reference, "SCRIPTURE_VERSE", verse_result["reality_score"],
                verse_state[0], verse_state[1], verse_state[2], verse_state[3],
                verse_state[4], verse_state[5], verse_state[6], verse_state[7]
            ))
            
            # 3. Process Root Words via Rust
            for tag in set(strongs_tags):
                tag_clean = tag.replace('{', '').replace('}', '').replace('(', '').replace(')', '')
                
                # Check if we already anchored this root word
                if tag_clean not in self.root_cache:
                    root_result = self.kernel.process(tag_clean, "ox")
                    root_state = root_result["state"]
                    
                    root_id = self.next_node_id
                    self.next_node_id += 1
                    
                    self.root_cache[tag_clean] = root_id
                    
                    nodes_batch.append((
                        root_id, tag_clean, "BIBLICAL_ROOT", root_result["reality_score"],
                        root_state[0], root_state[1], root_state[2], root_state[3],
                        root_state[4], root_state[5], root_state[6], root_state[7]
                    ))
                else:
                    root_id = self.root_cache[tag_clean]
                    
                # Forge the link
                functors_batch.append((root_id, verse_id, "CONSTITUENT_ROOT"))
                
            # Print progress every 5000 verses
            if (i + 1) % 5000 == 0:
                print(f"Processed {i + 1} verses... ({len(self.root_cache)} unique roots mapped)")

        print(f"\nAll {len(data)} verses projected to 8D. Writing to Universal Graph...")
        
        # 4. Batch Insert into SQLite
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.executemany('''
                INSERT INTO nodes (id, label, domain, reality_score, 
                coord_0, coord_1, coord_2, coord_3, coord_4, coord_5, coord_6, coord_7)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', nodes_batch)
            
            c.executemany('''
                INSERT INTO functors (source_id, target_id, operator_type)
                VALUES (?, ?, ?)
            ''', functors_batch)
            
            conn.commit()
            
        elapsed = time.time() - start_time
        print(f"\n[SUCCESS] Genesis Database Compiled in {elapsed:.2f} seconds.")
        print(f"Total Verse Nodes: {len(data)}")
        print(f"Total Root Nodes: {len(self.root_cache)}")
        print(f"Total Interlocking Functors: {len(functors_batch)}")

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), "../data/genesis_graph.db")
    # Make sure to place kjv_strongs.json in the data directory if recompiling the DB
    json_file = os.path.join(os.path.dirname(__file__), "../data/kjv_strongs.json")
    
    if not os.path.exists(json_file):
        print(f"CRITICAL ERROR: Dataset not found at {json_file}")
        sys.exit(1)
        
    ingestion = FullBibleIngestion(db_file, json_file)
    ingestion.run()
