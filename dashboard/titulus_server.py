import os
import sys
import json
import sqlite3
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Append SDK path to utilize the Urim Scanner
ENGINE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ENGINE_DIR, "sdk"))
from urim_scanner import UrimScanner
from inner_manifold import InnerManifold

PORT = 8555
DB_PATH = os.path.join(ENGINE_DIR, "data", "genesis_graph.db")

class TitulusHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Static file routing
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self._serve_static('index.html', 'text/html')
        elif parsed_path.path == '/style.css':
            self._serve_static('style.css', 'text/css')
        elif parsed_path.path == '/app.js':
            self._serve_static('app.js', 'application/javascript')
        elif parsed_path.path == '/mirror.html':
            self._serve_static('mirror.html', 'text/html')
            
        # API Routes
        elif parsed_path.path == '/api/stats':
            self._handle_stats()
        elif parsed_path.path == '/api/lattice':
            self._handle_lattice()
        elif parsed_path.path.startswith('/api/scan'):
            self._handle_scan(parsed_path.query)
        elif parsed_path.path.startswith('/api/mirror/topology'):
            self._handle_mirror_topology(parsed_path.query)
        elif parsed_path.path.startswith('/api/mirror/role'):
            self._handle_mirror_role(parsed_path.query)
        elif parsed_path.path.startswith('/api/mirror/sprint'):
            self._handle_mirror_sprint(parsed_path.query)
        else:
            self.send_error(404, "Not Found")

    def _serve_static(self, filename, content_type):
        filepath = os.path.join(os.path.dirname(__file__), "static", filename)
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            self._set_headers(content_type)
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading static file: {str(e)}")

    def _handle_lattice(self):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                # Fetch 2000 points to render the background lattice structure (we only need the first 3 coordinates for 3D visualization)
                c.execute("SELECT coord_0, coord_1, coord_2 FROM nodes WHERE domain='SCRIPTURE_VERSE' LIMIT 2000")
                points = c.fetchall()
            self._set_headers()
            self.wfile.write(json.dumps(points).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))

    def _handle_stats(self):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM nodes WHERE domain='SCRIPTURE_VERSE'")
                verses = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM nodes WHERE domain='BIBLICAL_ROOT'")
                roots = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM functors")
                functors = c.fetchone()[0]
                
            data = {
                "verses": verses,
                "roots": roots,
                "functors": functors,
                "active_frequency": "320Hz", # Placeholder for Ephemeris logic
                "watch_date": "CURRENT EPOCH",
                "active_role": "Zerubbabel (Foundation)"
            }
            self._set_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))

    def _handle_scan(self, query_string):
        params = urllib.parse.parse_qs(query_string)
        query = params.get('q', [''])[0]
        
        if not query:
            self._set_headers()
            self.wfile.write(json.dumps([]).encode('utf-8'))
            return
            
        try:
            scanner = UrimScanner(DB_PATH)
            # Suppress scanner stdout printing
            sys.stdout = open(os.devnull, 'w')
            results = scanner.query_by_geometry(query, limit=10)
            sys.stdout = sys.__stdout__
            
            # Format results for the frontend
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "label": r["label"],
                    "domain": r["domain"],
                    "resonance": round(r["resonance"], 4),
                    "reality": round(r["reality"], 4)
                })
                
            self._set_headers()
            self.wfile.write(json.dumps(formatted_results).encode('utf-8'))
        except Exception as e:
            sys.stdout = sys.__stdout__
            self.send_error(500, str(e))

    def _handle_mirror_topology(self, query_string):
        params = urllib.parse.parse_qs(query_string)
        struggle = params.get('q', [''])[0]
        if not struggle:
            return self.send_error(400, "Missing query")
        try:
            manifold = InnerManifold(DB_PATH)
            sys.stdout = open(os.devnull, 'w')
            vec, category = manifold.map_entropy_friction(struggle)
            import numpy as np
            magnitude = float(np.sum(vec)) # Extract pure mathematical magnitude for audio
            sys.stdout = sys.__stdout__
            self._set_headers()
            self.wfile.write(json.dumps({"category": category, "magnitude": magnitude}).encode('utf-8'))
        except Exception as e:
            sys.stdout = sys.__stdout__
            self.send_error(500, str(e))

    def _handle_mirror_role(self, query_string):
        params = urllib.parse.parse_qs(query_string)
        history = params.get('q', [''])[0]
        if not history:
            return self.send_error(400, "Missing query")
        try:
            manifold = InnerManifold(DB_PATH)
            sys.stdout = open(os.devnull, 'w')
            role = manifold.christotelic_role_assignment(history)
            sys.stdout = sys.__stdout__
            self._set_headers()
            self.wfile.write(json.dumps(role).encode('utf-8'))
        except Exception as e:
            sys.stdout = sys.__stdout__
            self.send_error(500, str(e))

    def _handle_mirror_sprint(self, query_string):
        params = urllib.parse.parse_qs(query_string)
        current = params.get('current', [''])[0]
        target = params.get('target', [''])[0]
        if not current or not target:
            return self.send_error(400, "Missing current or target")
        try:
            manifold = InnerManifold(DB_PATH)
            sys.stdout = open(os.devnull, 'w')
            waypoints = manifold.generate_sanctification_sprint(current, target)
            sys.stdout = sys.__stdout__
            self._set_headers()
            self.wfile.write(json.dumps(waypoints).encode('utf-8'))
        except Exception as e:
            sys.stdout = sys.__stdout__
            self.send_error(500, str(e))

if __name__ == "__main__":
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, TitulusHandler)
    print(f"=== TITULUS DASHBOARD ONLINE ===")
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
