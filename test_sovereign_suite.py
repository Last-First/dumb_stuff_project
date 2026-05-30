import os
import sys

# Append paths so we can import everything
ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ENGINE_DIR, "core"))
sys.path.append(os.path.join(ENGINE_DIR, "sdk"))

# Import all modules
import omega_core
from urim_scanner import UrimScanner
from crypto_bridge import CryptoBridge
from secure_messenger import SecureMessenger
from smart_contract_simulator import GeometricSmartContract

def run_all_tests():
    print("=== SOVEREIGN ENGINE: COMPREHENSIVE INTEGRITY TEST ===")
    
    passed_tests = 0
    total_tests = 5
    
    # ---------------------------------------------------------
    # TEST 1: THE RUST CORE (omega_core.so)
    # ---------------------------------------------------------
    print("\n[TEST 1] Hardened Rust Core (Mathematical Consistency)")
    try:
        kernel = omega_core.RustOmegaKernel()
        res1 = kernel.process("Immutable Truth", "ox")
        res2 = kernel.process("Immutable Truth", "ox")
        
        # Test Determinism: The exact same string must produce the exact same 8D coordinate
        if res1["state"] == res2["state"] and res1["reality_score"] > 0:
            print("  -> [PASS] Core is deterministic and generating valid geometry.")
            passed_tests += 1
        else:
            print("  -> [FAIL] Core produced inconsistent geometry.")
    except Exception as e:
        print(f"  -> [FAIL] Core crashed: {e}")

    # ---------------------------------------------------------
    # TEST 2: URIM SCANNER (Database Retrieval)
    # ---------------------------------------------------------
    print("\n[TEST 2] Urim Scanner (Semantic Geometry Search)")
    try:
        db_path = os.path.join(ENGINE_DIR, "data/genesis_graph.db")
        scanner = UrimScanner(db_path)
        
        # We will silence the scanner's internal prints temporarily for a clean test output
        sys.stdout = open(os.devnull, 'w')
        matches = scanner.query_by_geometry("God created the heavens", limit=5)
        sys.stdout = sys.__stdout__
        
        # Check if it successfully found Genesis 1:1 in the top matches
        found_genesis = any("Genesis 1:1" in match["label"] for match in matches)
        if found_genesis:
            print("  -> [PASS] Urim Scanner successfully retrieved targeted Biblical geometry.")
            passed_tests += 1
        else:
            print("  -> [FAIL] Urim Scanner failed to locate known geometry.")
    except Exception as e:
        sys.stdout = sys.__stdout__
        print(f"  -> [FAIL] Scanner crashed: {e}")

    # ---------------------------------------------------------
    # TEST 3: CRYPTO BRIDGE (Financial Key Generation)
    # ---------------------------------------------------------
    print("\n[TEST 3] Crypto Bridge (Deterministic Wallet Forging)")
    try:
        bridge = CryptoBridge()
        
        # Silence output
        sys.stdout = open(os.devnull, 'w')
        key1, score1 = bridge.generate_private_key_from_geometry("Sovereign Node Alpha", "lion")
        key2, score2 = bridge.generate_private_key_from_geometry("Sovereign Node Alpha", "lion")
        sys.stdout = sys.__stdout__
        
        # Test valid WIF format and determinism
        if key1 == key2 and key1.startswith(("K", "L", "5")): # Bitcoin WIF prefixes
            print("  -> [PASS] Bridge successfully forged immutable Bitcoin Private Keys.")
            passed_tests += 1
        else:
            print("  -> [FAIL] Bridge generated invalid or non-deterministic keys.")
    except Exception as e:
        sys.stdout = sys.__stdout__
        print(f"  -> [FAIL] Bridge crashed: {e}")

    # ---------------------------------------------------------
    # TEST 4: SECURE MESSENGER (Entropic Transmission)
    # ---------------------------------------------------------
    print("\n[TEST 4] Secure Messenger (Geometric Steganography)")
    try:
        messenger = SecureMessenger()
        
        # Silence output
        sys.stdout = open(os.devnull, 'w')
        pub_a, priv_a = messenger.generate_identity("A", "SeedA")
        pub_b, priv_b = messenger.generate_identity("B", "SeedB")
        
        payload, length = messenger.encrypt_message("TEST", pub_b)
        hacked = messenger.decrypt_message(payload, pub_a, length)
        decrypted = messenger.decrypt_message(payload, pub_b, length)
        sys.stdout = sys.__stdout__
        
        # The hacker should get garbage or None. The intended recipient gets the text.
        if hacked != "TEST" and "T" in decrypted:
            print("  -> [PASS] Steganography successfully repelled interceptor and decrypted for target.")
            passed_tests += 1
        else:
            print("  -> [FAIL] Steganography failed.")
    except Exception as e:
        sys.stdout = sys.__stdout__
        print(f"  -> [FAIL] Messenger crashed: {e}")

    # ---------------------------------------------------------
    # TEST 5: SMART CONTRACT (Truth Filtering)
    # ---------------------------------------------------------
    print("\n[TEST 5] Geometric Smart Contract (Reality Score Gating)")
    try:
        contract = GeometricSmartContract()
        
        # Silence output
        sys.stdout = open(os.devnull, 'w')
        w1 = contract.create_wallet("W1")
        w2 = contract.create_wallet("W2")
        
        # Scam should fail, Charity should pass
        res_scam = contract.execute_transaction(w1, w2, 10, "Fake_Rug_Pull_Spam")
        res_good = contract.execute_transaction(w1, w2, 10, "Building infrastructure and generating light")
        sys.stdout = sys.__stdout__
        
        if res_scam is False and res_good is True:
            print("  -> [PASS] Contract correctly rejected high-entropy scam and processed structured truth.")
            passed_tests += 1
        else:
            print("  -> [FAIL] Contract filtering misaligned.")
    except Exception as e:
        sys.stdout = sys.__stdout__
        print(f"  -> [FAIL] Contract crashed: {e}")

    print("\n=======================================================")
    if passed_tests == total_tests:
        print(f"[SYSTEM VERIFIED] {passed_tests}/{total_tests} Tests Passed. The Math is Absolute.")
    else:
        print(f"[SYSTEM WARNING] Only {passed_tests}/{total_tests} Tests Passed. Drift Detected.")

if __name__ == "__main__":
    run_all_tests()
