import json
from flask import Flask, request, jsonify

app = Flask(__name__)

class SupportAgent:
    def __init__(self):
        self.quotes = {}

    def generate_quote(self, client_req):
        # Simple quote generation based on client request
        # In reality, we would have a pricing model
        quote_id = f"QUOTE{len(self.quotes)+1}"
        self.quotes[quote_id] = {
            "client_req": client_req,
            "amount": 80000,  # in ZAR
            "status": "pending"
        }
        return quote_id, self.quotes[quote_id]

    def process_payment(self, quote_id, payment_details):
        # This would interface with your bank account via an API (if available) or just simulate
        # For now, we mark as paid
        if quote_id in self.quotes:
            self.quotes[quote_id]['status'] = 'paid'
            return True
        return False

# Simple Flask API to handle support
@app.route('/quote', methods=['POST'])
def create_quote():
    data = request.json
    agent = SupportAgent()
    quote_id, quote = agent.generate_quote(data['request'])
    return jsonify({"quote_id": quote_id, "quote": quote})

@app.route('/pay', methods=['POST'])
def pay_quote():
    data = request.json
    agent = SupportAgent()
    success = agent.process_payment(data['quote_id'], data['payment_details'])
    return jsonify({"success": success})

if __name__ == '__main__':
    app.run(port=5000)
