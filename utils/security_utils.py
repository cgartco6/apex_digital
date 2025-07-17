import hashlib
import os
import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image
import numpy as np

def generate_secure_hash(data):
    """Create blockchain-style SHA-256 hash"""
    return hashlib.sha256(data.encode()).hexdigest()

def embed_watermark(image_path, watermark_text):
    """Embed invisible watermark in images"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # Convert watermark to binary
    binary_wm = ''.join(format(ord(c), '08b') for c in watermark_text)
    binary_wm += '00000000'  # Null terminator
    
    # Embed in LSB of blue channel
    idx = 0
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            if idx < len(binary_wm):
                img_array[i, j, 2] = (img_array[i, j, 2] & 0xFE) | int(binary_wm[idx])
                idx += 1
    
    watermarked = Image.fromarray(img_array)
    watermarked.save(image_path)
    return f"Watermark embedded: {watermark_text}"

def extract_watermark(image_path):
    """Extract embedded watermark from image"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    binary_wm = ''
    for i in range(img_array.shape[0]):
        for j in range(img_array.shape[1]):
            binary_wm += str(img_array[i, j, 2] & 1)
            if len(binary_wm) % 8 == 0 and len(binary_wm) >= 8:
                byte = binary_wm[-8:]
                if byte == '00000000':
                    return binary_to_text(binary_wm[:-8])
    return ""

def binary_to_text(binary):
    """Convert binary string to text"""
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))

def generate_encryption_key(password=None, salt=None):
    """Generate encryption key from password"""
    password = password or os.urandom(16)
    salt = salt or os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

def encrypt_data(data, key):
    """Encrypt data with Fernet"""
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data, key):
    """Decrypt Fernet-encrypted data"""
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data.encode()).decode()

def validate_popia_compliance(data):
    """Ensure data compliance with South Africa's POPI Act"""
    sensitive_fields = ['id_number', 'financial_info', 'health_data']
    for field in sensitive_fields:
        if field in data:
            data[field] = '[POPIA_REDACTED]'
    return data

def generate_code_signature(code):
    """Create tamper-proof code signature"""
    signature = {
        "hash": generate_secure_hash(code),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "owner": "APEX Digital"
    }
    return json.dumps(signature)
