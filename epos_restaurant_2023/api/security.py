from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib
import base64

# Function to pad or hash the key to the required length
def get_aes_key(key, length=16):
    # Ensure the length is 16, 24, or 32 bytes
    if length not in [16, 24, 32]:
        raise ValueError("Key length must be 16, 24, or 32 bytes")
    
    # Use SHA-256 hash to get a fixed-length key
    hash = hashlib.sha256(key.encode('utf-8')).digest()
    
    # Return the key truncated or padded to the desired length
    return hash[:length]

# Function to encrypt data using AES
def aes_encrypt(data, key):
    # Generate a random initialization vector (IV)
    iv = get_random_bytes(16)

    # Create a new AES cipher object with the key
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Pad the data to be a multiple of 16 bytes
    padded_data = pad(data.encode('utf-8'), AES.block_size)

    # Encrypt the padded data
    encrypted_data = cipher.encrypt(padded_data)

    # Return the IV and encrypted data concatenated
    return iv + encrypted_data

# Function to decrypt data using AES
def aes_decrypt(encrypted_data, key):
    # Extract the IV from the beginning of the encrypted data
    iv = encrypted_data[:16]

    # Extract the actual encrypted data
    encrypted_data = encrypted_data[16:]

    # Create a new AES cipher object with the key and IV
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt and unpad the data
    decrypted_padded_data = cipher.decrypt(encrypted_data)
    decrypted_data = unpad(decrypted_padded_data, AES.block_size)

    # Return the decrypted data
    return decrypted_data.decode('utf-8')

# Function to encode the encrypted data to a base64 string for database storage
def encode_base64(data):
    return base64.b64encode(data).decode('utf-8')

# Function to decode the base64 string back to binary data for decryption
def decode_base64(data):
    return base64.b64decode(data.encode('utf-8'))
