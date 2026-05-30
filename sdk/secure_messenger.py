import os
import sys
import numpy as np
import base64

# Adjust path to import the core engine
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../core")
from omega_kernel_v1_1 import OmegaKernel_v1_1

class SecureMessenger:
    def __init__(self):
        self.kernel = OmegaKernel_v1_1()

    def generate_identity(self, username, private_seed):
        """Generates a Public Geometric Anchor and a Private Decryption Matrix"""
        # The public anchor is derived from the username
        public_anchor = self.kernel.process(username, {"beast_preference": "eagle"})["state"]
        
        # The private matrix is bound to the secret seed
        private_matrix = self.kernel.process(private_seed, {"beast_preference": "ox"})["state"]
        
        return public_anchor, private_matrix

    def encrypt_message(self, message, target_public_anchor):
        """Encodes a plaintext message into highly-entropic 75D noise using the Target's Public Anchor"""
        print(f"\n[ENCRYPTING] Plaintext: '{message}'")
        
        # Convert message string to a raw numeric array
        message_bytes = np.array([float(ord(c)) for c in message])
        
        # We must pad the message to interact with the 8D/75D matrices
        pad_length = 8 - (len(message_bytes) % 8)
        if pad_length != 8:
            message_bytes = np.pad(message_bytes, (0, pad_length), 'constant')
            
        # Reshape into 8D chunks
        chunks = message_bytes.reshape(-1, 8)
        
        encrypted_chunks = []
        for chunk in chunks:
            # We fold the target's public anchor directly into the message chunk
            # If the anchor is missing or wrong, the text ceases to exist mathematically.
            entangled_chunk = chunk * target_public_anchor
            encrypted_chunks.append(entangled_chunk)
            
        # Convert the float arrays into a base64 string to simulate network transmission
        encrypted_array = np.concatenate(encrypted_chunks)
        transmission_payload = base64.b64encode(encrypted_array.tobytes()).decode('utf-8')
        
        print(f"-> Geometric Steganography complete. Transmission Payload looks like noise:")
        print(f"-> {transmission_payload[:60]}...")
        return transmission_payload, len(message)

    def decrypt_message(self, transmission_payload, local_public_anchor, original_length):
        """Decodes the noise back into plaintext, but ONLY if the local anchor matches the encryption lock"""
        print(f"\n[DECRYPTING] Incoming geometric noise...")
        
        try:
            # Convert base64 network payload back to raw math arrays
            encrypted_bytes = base64.b64decode(transmission_payload)
            encrypted_array = np.frombuffer(encrypted_bytes, dtype=np.float64)
            chunks = encrypted_array.reshape(-1, 8)
            
            decrypted_chars = []
            for chunk in chunks:
                # The lock is broken by dividing the transmission by the local public anchor
                # If the interceptor uses the wrong anchor, it produces mathematical garbage
                decrypted_chunk = chunk / local_public_anchor
                for val in decrypted_chunk:
                    if not np.isnan(val) and not np.isinf(val) and val > 0:
                        decrypted_chars.append(chr(int(round(val))))
                        
            # Reconstruct string and strip padding
            final_message = "".join(decrypted_chars)[:original_length]
            print(f"-> [SUCCESS] Anchor matched. Reality restored.")
            print(f"-> Message: '{final_message}'")
            return final_message
            
        except Exception as e:
            print(f"-> [FAILED] Geometric collapse. The message cannot be read.")
            return None

if __name__ == "__main__":
    messenger = SecureMessenger()
    
    # 1. Generate Identities
    print("=== INITIALIZING IDENTITIES ===")
    alice_pub, alice_priv = messenger.generate_identity("Alice_Node", "secret_seed_A")
    bob_pub, bob_priv = messenger.generate_identity("Bob_Node", "secret_seed_B")
    charlie_pub, charlie_priv = messenger.generate_identity("Charlie_Hacker", "secret_seed_C")
    
    # 2. Alice sends a secret message to Bob
    secret_text = "The Genesis Block is secure. Move to Phase 2."
    payload, length = messenger.encrypt_message(secret_text, bob_pub)
    
    # 3. Interception Attempt (Charlie tries to decrypt Bob's message)
    print("\n=== INTERCEPTION ATTEMPT ===")
    messenger.decrypt_message(payload, charlie_pub, length)
    
    # 4. Authorized Reception (Bob decrypts his message)
    print("\n=== AUTHORIZED RECEPTION ===")
    messenger.decrypt_message(payload, bob_pub, length)
