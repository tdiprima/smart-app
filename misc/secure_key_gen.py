"""
Use the secrets module (best for crypto stuff) to create a secure random string.
Unlike random, secrets is designed for security (e.g., keys, tokens).
"""
import secrets

# Generate a 32-byte random string (hex format, 64 chars)
secure_key = secrets.token_hex(32)
print(secure_key)
