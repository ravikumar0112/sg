from flask import Flask, jsonify
from imapclient import IMAPClient
from elasticsearch import Elasticsearch
import threading
import time
import os
#es = Elasticsearch([{'host': 'localhost', 'port': 9200, 'scheme': 'http'}])
app = Flask(__name__)

# Email account details (update with your info)
EMAIL_HOST = "imap.gmail.com"
EMAIL_USER = "ravikumarks0112@gmail.com"
EMAIL_PASS = "diny opri mggh mss"

# Connect to Elasticsearch
#es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
es = Elasticsearch("http://localhost:9200")


# Test email data
test_email = {
    "subject": "Manual Test Email",
    "from": "test@example.com",
    "body": "This is a manually indexed email.",
    "date": "2025-02-27T12:30:00"
}

# Index it manually
res = es.index(index="emails", document=test_email)
print(r"✅ Indexed Email:", res["_id"])

def index_email(email_data):
    """
    Index an email document into Elasticsearch.
    email_data should be a dict with keys like 'subject', 'from', 'body', 'date'.
    """
    # You can use a unique ID for each email, for now we let ES auto-generate one.
    res = es.index(index="emails", body=email_data)
    print("Indexed email:", res['result'])

def sync_emails():
    try:
        with IMAPClient(EMAIL_HOST) as client:
            print("🔄 Connecting to IMAP server...")
            client.login(EMAIL_USER, EMAIL_PASS)
            print("✅ Login successful!")
            client.select_folder("INBOX")

            print("📩 Listening for new emails in real-time...")
            while True:
                client.idle()
                response = client.idle_check(timeout=60)
                if response:
                    print("📨 New email received!")
                    # For demonstration, let's create a dummy email data.
                    # In real implementation, you'll fetch the actual email details.
                    dummy_email = {
                        "subject": "Test Email",
                        "from": EMAIL_USER,
                        "body": "This is a test email received at " + time.ctime(),
                        "date": time.strftime("%Y-%m-%dT%H:%M:%S")
                    }
                    index_email(dummy_email)
                client.idle_done()
    except Exception as e:
        print("⚠️ Error:", e)

@app.route('/sync', methods=['GET'])
def sync():
    threading.Thread(target=sync_emails, daemon=True).start()
    return jsonify({"message": "Syncing emails in real-time!"})

@app.route('/sync-emails', methods=['POST'])
def sync_emails():
    return jsonify({"message": "Syncing emails in real-time!"})

# Optional: A simple homepage for testing
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Email Onebox API!"})

if __name__ == '__main__':
    app.run(debug=True)


