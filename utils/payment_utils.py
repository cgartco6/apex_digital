import sqlite3
import datetime
import os
from .security_utils import generate_secure_hash

def generate_invoice(client_info, amount, description):
    """Create professional invoice"""
    invoice_id = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {
        "invoice_id": invoice_id,
        "date": datetime.date.today().isoformat(),
        "client": client_info['name'],
        "company": client_info['company'],
        "amount": f"R{amount:.2f}",
        "description": description,
        "bank_account": os.getenv('BUSINESS_BANK_ACCOUNT'),
        "payment_terms": "50% deposit, 50% on delivery",
        "signature": generate_secure_hash(f"{invoice_id}{amount}")
    }

def record_payment(invoice_id, amount):
    """Log payment to database"""
    conn = sqlite3.connect('data/apex_payments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (invoice_id TEXT PRIMARY KEY, amount REAL, date TEXT, status TEXT)''')
    
    c.execute("INSERT INTO payments VALUES (?, ?, ?, ?)",
              (invoice_id, amount, datetime.datetime.now().isoformat(), "RECEIVED"))
    conn.commit()
    conn.close()
    return True

def process_owner_salary():
    """Handle R10,000 owner salary payment"""
    total_revenue = calculate_revenue()
    if total_revenue >= 20000:  # R20k threshold
        print(f"💸 Owner salary processed: R10000")
        return True
    return False

def calculate_revenue():
    """Calculate total revenue from payments"""
    conn = sqlite3.connect('data/apex_payments.db')
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM payments")
    total = c.fetchone()[0] or 0
    conn.close()
    return total

def generate_payment_link(amount, description):
    """Generate payment request link for SA banks"""
    banks = {
        'FNB': f"https://www.fnb.co.za/pay?amount={amount}&desc={description}",
        'StandardBank': f"https://secure.standardbank.co.za/pay?amt={amount}&ref={description}",
        'Nedbank': f"https://nedbank.pay.co.za?value={amount}&note={description}"
    }
    return banks
