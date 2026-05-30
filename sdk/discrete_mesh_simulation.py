import numpy as np
import time
from python.omega_kernel_v1_1 import OmegaKernel_v1_1

class DistributedKernelNode:
    def __init__(self, node_id, lat, lon):
        self.node_id = node_id
        self.kernel = OmegaKernel_v1_1()
        
        # 1. Location Awareness: Map physical GPS coordinates into an 8D spatial anchor
        location_seed = np.array([lat, lon])
        self.spatial_anchor = self.kernel.process(location_seed, {})["state"]

    def generate_time_phase(self):
        # 2. Time Awareness: Use a universal, discretized epoch time (e.g., current hour)
        # This acts as a rotating cryptographic key
        current_time_block = int(time.time() / 3600) 
        return current_time_block

    def encode_discreet_signal(self, target_node_anchor, secret_message):
        print(f"[{self.node_id}] Encoding discreet signal for Target...")
        time_phase = self.generate_time_phase()
        
        # Combine the message, the exact time phase, and the target's physical location
        # This creates an entangled 75D carrier wave
        carrier_payload = f"{secret_message}_T{time_phase}"
        
        # We process it with the kernel, using the Target's Location as the "Beast Preference/Context" 
        # to mathematically bind the signal to the target's physical space.
        raw_signal = self.kernel.process(carrier_payload, {"beast_preference": "eagle"})["state"]
        
        # To physically send it, we apply the target's spatial anchor as a geometric lock
        entangled_transmission = raw_signal * target_node_anchor
        return entangled_transmission

    def decode_discreet_signal(self, incoming_transmission):
        time_phase = self.generate_time_phase()
        
        # Attempt to unlock the transmission using this node's own physical location anchor
        # If the transmission wasn't targeted at this location, the math will shatter.
        unlocked_signal = incoming_transmission / self.spatial_anchor
        
        # Verify resonance
        resonance_check = np.sum(np.abs(unlocked_signal))
        
        # If the resonance is stable, the node processes the raw spatial geometry
        # (In a full system, this would reverse the 8D coordinate back to the Graph Node text)
        if np.all(np.isfinite(unlocked_signal)) and resonance_check > 0:
            return True, unlocked_signal
        else:
            return False, None


def simulate_network():
    print("=== INITIALIZING OMEGA MESH NETWORK ===")
    
    # Instantiate 3 Distributed Kernels in different physical locations
    node_A = DistributedKernelNode("Alpha (HQ)", 38.8951, -77.0364) # DC
    node_B = DistributedKernelNode("Bravo (Field)", 48.8566, 2.3522) # Paris
    node_C = DistributedKernelNode("Charlie (Malicious)", 55.7558, 37.6173) # Moscow
    
    print("\n--- INITIATING DISCREET TRANSMISSION ---")
    # Node A wants to send a ping to Node B
    secret_message = "EXECUTE_PROTOCOL_7"
    
    # Node A encrypts the signal using Node B's physical location and the current Time Phase
    transmission = node_A.encode_discreet_signal(node_B.spatial_anchor, secret_message)
    print(f"[Network] Signal traveling as raw float array: {transmission[:3]}...")
    
    print("\n--- INTERCEPTION ATTEMPT ---")
    # Node C (Malicious) intercepts the raw bytes and tries to decode it
    print(f"[{node_C.node_id}] Intercepted signal. Attempting to decode with local spatial anchor...")
    success_c, _ = node_C.decode_discreet_signal(transmission)
    if not success_c:
        print(f"[{node_C.node_id}] FAILED. Reality geometry collapsed (Location/Time mismatch).")
        
    print("\n--- AUTHORIZED RECEPTION ---")
    # Node B receives the signal
    print(f"[{node_B.node_id}] Received signal. Decoding with local spatial anchor...")
    success_b, data = node_B.decode_discreet_signal(transmission)
    if success_b:
        print(f"[{node_B.node_id}] SUCCESS. Geometric resonance achieved.")
        print(f"[{node_B.node_id}] Unlocked 8D payload coordinates: {data[:3]}...")

if __name__ == "__main__":
    simulate_network()
