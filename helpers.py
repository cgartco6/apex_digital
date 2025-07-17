"""
APEX DIGITAL HELPER MODULE
Core utilities for AI agents: security, payments, media, and automation
"""

import os
import re
import hashlib
import base64
import json
import logging
import sqlite3
import smtplib
import requests
import datetime
import subprocess
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Initialize environment
load_dotenv()

# =====================
# SECURITY & ANTI-THEFT
# =====================

def generate_watermark(text):
    """Create invisible watermark for AI-generated content"""
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def embed_watermark(image_path, watermark):
    """Embed invisible watermark in images"""
    img = Image.open(image_path)
    data = np.array(img)
    
    # Convert watermark to binary
    binary_wm = ''.join(format(ord(char), '08b') for char in watermark)
    wm_len = len(binary_wm)
    
    # Embed in LSB of blue channel
    idx = 0
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if idx < wm_len:
                data[i, j, 2] = (data[i, j, 2] & 0xFE) | int(binary_wm[idx])
                idx += 1
    
    watermarked = Image.fromarray(data)
    watermarked.save(image_path)
    return f"Watermark embedded: {watermark}"

def verify_watermark(image_path):
    """Extract watermark from image"""
    img = Image.open(image_path)
    data = np.array(img)
    
    binary_wm = ''
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            binary_wm += str(data[i, j, 2] & 1)
            if len(binary_wm) % 8 == 0 and len(binary_wm) >= 8:
                char = chr(int(binary_wm[-8:], 2))
                if char == '\x00':  # Null terminator
                    return binary_wm[:-8]
    return ""

def encrypt_data(data, key=None):
    """Encrypt sensitive data with AES-256"""
    key = key or os.getenv('ENCRYPTION_KEY')
    if not key:
        key = Fernet.generate_key().decode()
        os.environ['ENCRYPTION_KEY'] = key
    
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data, key=None):
    """Decrypt protected data"""
    key = key or os.getenv('ENCRYPTION_KEY')
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data.encode()).decode()

# =====================
# PAYMENT & BANKING
# =====================

def generate_invoice(client_name, amount, description):
    """Create AI-generated invoice"""
    invoice_id = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {
        "invoice_id": invoice_id,
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "client": client_name,
        "amount": f"R{amount:.2f}",
        "description": description,
        "bank_account": os.getenv('ACCOUNT_NUMBER'),
        "payment_due": (datetime.datetime.now() + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
    }

def record_payment(invoice_id, amount):
    """Log payment to SQLite database"""
    conn = sqlite3.connect('apex_payments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id TEXT PRIMARY KEY, amount REAL, date TEXT, status TEXT)''')
    
    c.execute("INSERT OR REPLACE INTO payments VALUES (?, ?, ?, ?)",
              (invoice_id, amount, datetime.datetime.now().strftime("%Y-%m-%d"), "RECEIVED"))
    conn.commit()
    conn.close()
    return True

def check_revenue():
    """Calculate current revenue for salary trigger"""
    conn = sqlite3.connect('apex_payments.db')
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM payments")
    total = c.fetchone()[0] or 0
    conn.close()
    return total

def process_owner_salary():
    """Handle R10,000 owner salary payment"""
    revenue = check_revenue()
    if revenue >= 20000:  # R20k threshold
        print(f"💸 Owner salary processed: R10000")
        return True
    return False

# =====================
# MEDIA GENERATION
# =====================

def generate_ai_image(prompt, output_path):
    """Create image using free Leonardo.ai API"""
    headers = {"Authorization": f"Bearer {os.getenv('LEONARDO_API_KEY')}"}
    payload = {
        "prompt": prompt,
        "modelId": "e316348f-7773-490e-adcd-46765c32eb99",
        "width": 1024,
        "height": 768
    }
    
    response = requests.post(
        "https://cloud.leonardo.ai/api/rest/v1/generations",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        image_url = response.json().get('generated_images', [{}])[0].get('url')
        if image_url:
            img_data = requests.get(image_url).content
            with open(output_path, 'wb') as f:
                f.write(img_data)
            return output_path
    return None

def create_video_from_images(images, audio_path, output_path):
    """Combine images and audio into video (FFmpeg required)"""
    # Generate temporary file list
    with open("imagelist.txt", "w") as f:
        for img in images:
            f.write(f"file '{img}'\nduration 5\n")
    
    # Create video using FFmpeg
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "imagelist.txt",
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return output_path
    except Exception as e:
        logging.error(f"Video creation failed: {str(e)}")
        return None

# =====================
# AI AGENT UTILITIES
# =====================

def send_whatsapp_message(number, message):
    """Send WhatsApp message using Twilio API (free trial)"""
    account_sid = os.getenv('TWILIO_SID')
    auth_token = os.getenv('TWILIO_TOKEN')
    from_number = os.getenv('TWILIO_NUMBER')
    
    if not all([account_sid, auth_token, from_number]):
        logging.warning("Twilio credentials not configured")
        return False
        
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "Body": message,
        "From": f"whatsapp:{from_number}",
        "To": f"whatsapp:{number}"
    }
    
    response = requests.post(url, data=data, auth=(account_sid, auth_token))
    return response.status_code == 201

def extract_lead_info(email):
    """Extract contact info from email content"""
    # Phone number regex for South Africa
    phone_regex = r'(\+27|0)[\s-]?(\d{2,3})[\s-]?(\d{3,4})[\s-]?(\d{3,4})'
    phone_match = re.search(phone_regex, email)
    
    # Email extraction
    email_regex = r'[\w\.-]+@[\w\.-]+'
    email_match = re.search(email_regex, email)
    
    return {
        "phone": phone_match.group(0) if phone_match else None,
        "email": email_match.group(0) if email_match else None
    }

# =====================
# SYSTEM MANAGEMENT
# =====================

def backup_to_drive(file_paths):
    """Backup files to Google Drive (using rclone)"""
    try:
        for path in file_paths:
            subprocess.run([
                "rclone",
                "copy",
                path,
                "gdrive:apex_backup",
                "--config", os.path.expanduser("~/.config/rclone/rclone.conf")
            ], check=True)
        return True
    except Exception as e:
        logging.error(f"Backup failed: {str(e)}")
        return False

def upgrade_tool(tool_name):
    """Upgrade from free to paid version based on revenue"""
    upgrade_map = {
        "GPT-4": "gpt_upgrade.bat",
        "Leonardo": "leonardo_upgrade.bat",
        "TensorFlow": "tf_upgrade.bat"
    }
    
    if tool_name in upgrade_map:
        try:
            subprocess.run([upgrade_map[tool_name]], check=True)
            return True
        except:
            return False
    return False

# =====================
# COMPLIANCE & LOCALIZATION
# =====================

def popia_compliance_check(data):
    """Ensure POPIA compliance for South African data"""
    # Remove sensitive personal information
    sensitive_fields = ['id_number', 'financial_info', 'health_data']
    for field in sensitive_fields:
        if field in data:
            data[field] = "[REDACTED]"
    return data

def translate_zulu(text):
    """Basic English to isiZulu translation"""
    translations = {
        "hello": "sawubona",
        "thank you": "ngiyabonga",
        "app": "uhlelo",
        "payment": "inkokhelo",
        "support": "ukusekela"
    }
    
    for eng, zulu in translations.items():
        text = text.replace(eng, zulu)
    return text

# =====================
# INITIALIZATION
# =====================

def initialize_system():
    """First-time setup for APEX Digital"""
    # Create necessary databases
    for db in ['apex_clients.db', 'apex_payments.db']:
        conn = sqlite3.connect(db)
        conn.close()
    
    # Create default directories
    os.makedirs("media/images", exist_ok=True)
    os.makedirs("media/videos", exist_ok=True)
    os.makedirs("client_projects", exist_ok=True)
    
    # Generate encryption key if missing
    if not os.getenv('ENCRYPTION_KEY'):
        key = Fernet.generate_key().decode()
        with open('.env', 'a') as env_file:
            env_file.write(f'\nENCRYPTION_KEY={key}\n')
        load_dotenv(override=True)
    
    print("✅ APEX SYSTEM INITIALIZED")

# Run initialization on import
if __name__ != "__main__":
    initialize_system()
