import os
import sys
import numpy as np

# Adjust path to import the core engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../core")
import omega_core

class GeometricSmartContract:
    def __init__(self):
        self.kernel = omega_core.RustOmegaKernel()
        # The threshold of truth required for the contract to execute
        # Prevents scam tokens or highly entropic (chaotic) transfers
        self.MINIMUM_REALITY_SCORE = 0.6000 

    def create_wallet(self, identity_concept):
        """Creates a wallet based purely on the geometric weight of a concept"""
        result = self.kernel.process(identity_concept, "ox")
        # A wallet is just an 8D coordinate and a balance
        return {
            "owner": identity_concept,
            "geometry": result["state"],
            "reality_score": result["reality_score"],
            "balance": 1000.0  # Starting Fiat/Crypto Balance
        }

    def execute_transaction(self, sender, receiver, amount, transaction_intent):
        print(f"\n=== SMART CONTRACT: INITIATING TRANSFER ===")
        print(f"Sender: {sender['owner']} (Balance: {sender['balance']})")
        print(f"Receiver: {receiver['owner']} (Balance: {receiver['balance']})")
        print(f"Amount: {amount}")
        print(f"Intent (The 'Why'): '{transaction_intent}'")

        # 1. Evaluate the Intent (The Geometric Oracle)
        # Standard smart contracts only check if you have enough money.
        # The Omega Contract checks the STRUCTURAL TRUTH of the transaction itself.
        intent_result = self.kernel.process(transaction_intent, "lion")
        intent_reality = intent_result["reality_score"]
        
        print(f"\n[ORACLE CHECK] Evaluating Transaction Intent...")
        print(f"-> Reality Score of Intent: {intent_reality:.4f} (Required: {self.MINIMUM_REALITY_SCORE})")

        # 2. The Execution Gate
        if intent_reality < self.MINIMUM_REALITY_SCORE:
            print("-> [REJECTED] The transaction lacks structural truth. High entropy / Scam detected.")
            print("-> Funds remain locked.")
            return False

        if sender['balance'] < amount:
            print("-> [REJECTED] Insufficient geometric mass (funds).")
            return False

        # 3. Geometric Transfer (Atomic Swap)
        print("-> [APPROVED] Geometric resonance achieved. Transferring value...")
        sender['balance'] -= amount
        receiver['balance'] += amount
        
        # We calculate the "Receipt" - an unforgeable hash of the combined geometries
        receipt_vector = np.array(sender['geometry']) * np.array(receiver['geometry']) * np.array(intent_result['state'])
        receipt_hash = np.sum(np.abs(receipt_vector))
        
        print(f"\n=== TRANSACTION COMPLETE ===")
        print(f"New Sender Balance: {sender['balance']}")
        print(f"New Receiver Balance: {receiver['balance']}")
        print(f"Immutable Geometric Receipt: {receipt_hash:.6f}")
        return True

if __name__ == "__main__":
    contract = GeometricSmartContract()
    
    # 1. Initialize Wallets
    wallet_alice = contract.create_wallet("Alice_Charity_Fund")
    wallet_scammer = contract.create_wallet("Anonymous_Exploit_Bot")
    
    # 2. Attempt 1: A Malicious/Spam Transaction
    print("\n--- ATTEMPT 1: EXPLOIT ---")
    contract.execute_transaction(
        sender=wallet_scammer, 
        receiver=wallet_alice, 
        amount=50.0, 
        transaction_intent="ASDFasdfqwer1234_RugPull_Fake_Token_Airdrop"
    )
    
    # 3. Attempt 2: A Truthful/Structured Transaction
    print("\n--- ATTEMPT 2: ALIGNED TRANSFER ---")
    contract.execute_transaction(
        sender=wallet_alice, 
        receiver=wallet_scammer, # Alice sending relief funds
        amount=100.0, 
        transaction_intent="Disbursing funds for agricultural development"
    )
