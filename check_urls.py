import requests
import csv
from datetime import datetime

# Configuration
URLS_FILE = 'urls.txt'
HTML_FILE = 'status.html'
HISTORY_FILE = 'history.txt'

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
            name, url = row
            status = check_url(url)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_list.append((name, url, status, timestamp))
            current_status[url] = status

            # Check for status change
            if url in history and history[url] != status:
                print(f"Status Change: {name} ({url}) changed from {history[url]} to {status}")

    save_history(current_status)
    generate_html(status_list)

if __name__ == "__main__":
    main()