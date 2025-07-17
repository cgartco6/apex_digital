import sqlite3
import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize database
conn = sqlite3.connect('apex_clients.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS clients
             (id INTEGER PRIMARY KEY, name TEXT, project TEXT, quote REAL, paid INTEGER)''')

def handle_inquiry(query):
    """AI-powered customer support"""
    # Connect to free Rasa chatbot
    response = requests.post(
        "http://localhost:5005/webhooks/rest/webhook",
        json={"message": query, "sender": "client"}
    )
    return response.json()[0]['text']

def generate_quote(project_details):
    """Auto-price projects"""
    complexity = len(project_details['features']) / 3
    quote = max(15000, complexity * 25000)  # Min R15k project
    c.execute("INSERT INTO clients (name, project, quote, paid) VALUES (?,?,?,?)",
              (project_details['client'], str(project_details), quote, 0))
    conn.commit()
    return quote

def process_payment(client_id, amount):
    """Simulate bank transfer to YOUR account"""
    c.execute("UPDATE clients SET paid=1 WHERE id=?", (client_id,))
    conn.commit()
    print(f"💰 R{amount} transferred to BANK ACC: {os.getenv('ACCOUNT_NUMBER')}")
