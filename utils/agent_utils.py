import requests
import sqlite3
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .security_utils import validate_popia_compliance

def handle_customer_query(query, language='en'):
    """Process customer inquiries with AI"""
    ai_endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Respond to this customer query in {language}: {query}"
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }
    
    response = requests.post(ai_endpoint, headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

def extract_lead_info(text):
    """Extract contact info from text"""
    # South Africa phone number regex
    phone_regex = r'(\+27|0)[\s-]?(\d{2,3})[\s-]?(\d{3,4})[\s-]?(\d{3,4})'
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    phone_match = re.search(phone_regex, text)
    email_match = re.search(email_regex, text)
    
    return {
        "phone": phone_match.group(0) if phone_match else None,
        "email": email_match.group(0) if email_match else None
    }

def send_email(to, subject, body):
    """Send email using SMTP"""
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SMTP_USER')
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {str(e)}")
        return False

def log_client_interaction(client_id, interaction_type, details):
    """Record client interactions to DB"""
    conn = sqlite3.connect('data/apex_clients.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS interactions
                 (id INTEGER PRIMARY KEY, client_id INTEGER, timestamp TEXT, 
                 type TEXT, details TEXT)''')
    
    c.execute("INSERT INTO interactions (client_id, timestamp, type, details) VALUES (?, ?, ?, ?)",
              (client_id, datetime.datetime.now().isoformat(), interaction_type, details))
    conn.commit()
    conn.close()
    
def translate_content(text, target_lang='zu'):
    """Basic translation for South African languages"""
    lang_map = {
        'zu': 'Zulu',
        'af': 'Afrikaans',
        'en': 'English'
    }
    
    prompt = f"Translate this to {lang_map.get(target_lang, 'English')}: {text}"
    return handle_customer_query(prompt)
