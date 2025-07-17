# Save as security_test.py in root
from helpers import verify_watermark, blockchain_anchor
import os

def run_checks():
    print("🔒 Running Security Protocols:")
    # 1. Verify sample watermark
    wm = verify_watermark("data/sample_watermark.jpg")
    print(f"Watermark Status: {'VALID' if wm else 'INVALID'}")
    
    # 2. Check database encryption
    from devsec_agent import check_encryption
    print(f"DB Encryption: {check_encryption()}")
    
    # 3. Validate blockchain anchors
    last_hash = open("data/code_signatures.txt").readlines()[-1].split("|")[2].strip()
    print(f"Blockchain Verification: {blockchain_anchor(last_hash)}")

if __name__ == "__main__":
    run_checks()
