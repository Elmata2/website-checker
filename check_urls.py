import requests
import csv
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import os

# Configuration
URLS_FILE = 'urls.txt'
HTML_FILE = 'status.html'
HISTORY_FILE = 'history.txt'

# Email Configuration (Gmail example)
EMAIL_TO = 'jort@wiebrens.com'
SMTP_USER = os.environ.get('SMTP_USER')  # Set in GitHub Secrets
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')  # Set in GitHub Secrets
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  # Set in GitHub Secrets
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')  # Set in GitHub Secrets

def check_url(url):
    try:
        response = requests.get(url, timeout=10)
        return 'Live' if response.status_code == 200 else 'Down'
    except:
        return 'Down'

def load_history():
    history = {}
    try:
        with open(HISTORY_FILE, 'r') as f:
            for line in f:
                url, status = line.strip().split(',')
                history[url] = status
    except FileNotFoundError:
        pass
    return history

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        for url, status in history.items():
            f.write(f"{url},{status}\n")

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = EMAIL_TO

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, EMAIL_TO, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Telegram API error: {response.text}")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

def generate_html(status_list):
    html = """
    <html>
    <head><title>URL Status Monitor</title></head>
    <body>
        <h1>URL Status</h1>
        <table border="1">
            <tr><th>Name</th><th>URL</th><th>Status</th><th>Last Checked</th></tr>
    """
    for name, url, status, timestamp in status_list:
        color = 'green' if status == 'Live' else 'red'
        html += f"<tr><td>{name}</td><td><a href='{url}'>{url}</a></td><td style='color:{color}'>{status}</td><td>{timestamp}</td></tr>"
    html += "</table></body></html>"

    with open(HTML_FILE, 'w') as f:
        f.write(html)

def main():
    history = load_history()
    status_list = []
    current_status = {}

    with open(URLS_FILE, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) != 2:
                continue
            name, url = row
            status = check_url(url)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_list.append((name, url, status, timestamp))
            current_status[url] = status

            # Check for status change
            if url in history and history[url] != "Down":
                message = f"Status Change: {name} ({url}) changed from {history[url]} to {status}"
                print(message)
                send_email("URL Status Alert", message)
                send_telegram(message)

    save_history(current_status)
    generate_html(status_list)

if __name__ == "__main__":
    main()