import os
import sys
import hashlib
import binascii
import numpy as np
import base58

# Adjust path to import the core engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../core")
from omega_kernel_v1_1 import OmegaKernel_v1_1

class CryptoBridge:
    def __init__(self):
        self.kernel = OmegaKernel_v1_1()

    def generate_private_key_from_geometry(self, concept, beast_tuning="lion"):
        print(f"\n=== BRIDGING CONCEPT TO LEDGER: '{concept}' ===")
        # 1. Digest the concept through the Omega Kernel to get the 8D Coordinate
        # We use the 'Lion' because it represents financial weight, law, and structure.
        result = self.kernel.process(concept, {"beast_preference": beast_tuning})
        state_8d = result["state"]
        reality = result["reality_score"]
        
        print(f"[1] Omega Geometry Calculated.")
        print(f"    Reality Score: {reality:.4f}")
        print(f"    8D Anchor: [{state_8d[0]:.4f}, {state_8d[1]:.4f}, {state_8d[2]:.4f} ...]")

        # 2. Collapse the 8D coordinate array into a highly deterministic 256-bit hash
        # We use SHA-256 to convert the floating point geometry into cryptographic bytes
        geometry_bytes = state_8d.tobytes()
        sha256_hash = hashlib.sha256(geometry_bytes).digest()
        
        # 3. Format as a Bitcoin Private Key (WIF - Wallet Import Format)
        # Add 0x80 byte in front for Bitcoin Mainnet
        extended_key = b"\x80" + sha256_hash
        # Add 0x01 byte at the end to indicate compressed public key
        extended_key += b"\x01"
        
        # 4. Calculate Checksum (Double SHA-256)
        checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
        
        # 5. Append checksum and encode to Base58
        final_key = extended_key + checksum
        wif_key = base58.b58encode(final_key).decode('utf-8')
        
        print(f"[2] Geometric Hash collapsed to 256-Bit Ledger Key.")
        print(f"[3] Bitcoin Private Key (WIF) Forged:")
        print(f"    -> {wif_key}")
        
        return wif_key, reality

if __name__ == "__main__":
    bridge = CryptoBridge()
    
    # Test 1: Generate a wallet from the ultimate truth anchor
    bridge.generate_private_key_from_geometry("The Logos", "man")
    
    # Test 2: Generate a wallet from a financial structure concept
    bridge.generate_private_key_from_geometry("Jubilee Wealth Transfer", "lion")
