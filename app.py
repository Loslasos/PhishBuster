import csv
import os
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Databáze phishingových frází v češtině
PHISHING_PATTERNS = [
    r'Vaše heslo vyprší', r'Obnovte jej zde', r'Klikněte na tento odkaz', r'Potvrzení účtu',
    r'Nezaplacená faktura', r'Dluh bude postoupen exekutorovi', r'Neobvyklá aktivita na vašem účtu',
    r'Vyhráli jste iPhone', r'Výhra čeká', r'Musíte jednat ihned', r'Vaše banka vás kontaktuje',
    r'Přihlaste se pro potvrzení platby', r'Zabezpečení účtu bylo kompromitováno', r'Váš účet bude zablokován',
    r'Aktuální platba nebyla provedena', r'Ověřte svou totožnost', r'Nesrovnalost ve vašem účtu',
    r'Máte nové bezpečnostní upozornění', r'Zadejte své údaje pro ověření', r'Vaše karta byla zneužita',
    r'Poslední varování před deaktivací', r'Vaše zásilka nebyla doručena', r'Přístup k vašemu účtu byl omezen'
]

# Regulární výraz pro detekci URL adresy
URL_PATTERN = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'

# Název datasetu
DATASET_FILE = "dataset.csv"

# Funkce pro uložení výsledků analýzy
def save_to_dataset(text, prediction, user_feedback=None):
    file_exists = os.path.isfile(DATASET_FILE)
    with open(DATASET_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["text", "prediction", "user_feedback"])
        writer.writerow([text, prediction, user_feedback])

# API na ověření URL (příklad, použij VirusTotal nebo Google Safe Browsing)
def check_url_safety(url):
    try:
        response = requests.get(f"https://example-phishing-api.com/check?url={url}")
        return response.json().get("safe", False)
    except Exception:
        return False  # Pokud se nepodaří ověřit, označíme jako podezřelé

# Funkce na detekci phishingu
def detect_phishing(text):
    for pattern in PHISHING_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
import json
import os
import re
import requests
import gspread
from google.oauth2.service_account import Credentials
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Načtení Google API klíče z Render environment variable
credentials_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
credentials = Credentials.from_service_account_info(credentials_info)
client = gspread.authorize(credentials)

# Google Sheets ID
GOOGLE_SHEETS_ID = "1KJLQ1ZKIxb443BZ1Rjc9JZ62eZaSan-uNBZ55NVcpXY"
sheet = client.open_by_key(GOOGLE_SHEETS_ID).sheet1

# Databáze phishingových frází v češtině
PHISHING_PATTERNS = [
    r'Vaše heslo vyprší', r'Obnovte jej zde', r'Klikněte na tento odkaz', r'Potvrzení účtu',
    r'Nezaplacená faktura', r'Dluh bude postoupen exekutorovi', r'Neobvyklá aktivita na vašem účtu',
    r'Vyhráli jste iPhone', r'Výhra čeká', r'Musíte jednat ihned', r'Vaše banka vás kontaktuje',
    r'Přihlaste se pro potvrzení platby', r'Zabezpečení účtu bylo kompromitováno', r'Váš účet bude zablokován',
    r'Aktuální platba nebyla provedena', r'Ověřte svou totožnost', r'Nesrovnalost ve vašem účtu',
    r'Máte nové bezpečnostní upozornění', r'Zadejte své údaje pro ověření', r'Vaše karta byla zneužita',
    r'Poslední varování před deaktivací', r'Vaše zásilka nebyla doručena', r'Přístup k vašemu účtu byl omezen'
]

# Regulární výraz pro detekci URL adresy
URL_PATTERN = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'

# API na ověření URL (příklad, použij VirusTotal nebo Google Safe Browsing)
def check_url_safety(url):
    try:
        response = requests.get(f"https://example-phishing-api.com/check?url={url}")
        return response.json().get("safe", False)
    except Exception:
        return False  # Pokud se nepodaří ověřit, označíme jako podezřelé

# Funkce na detekci phishingu
def detect_phishing(text):
    for pattern in PHISHING_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get("text", "")
    url = None
    
    # Pokud vstup obsahuje URL, extrahujeme ji
    url_match = re.search(URL_PATTERN, text)
    if url_match:
        url = url_match.group(0)

    is_phishing = detect_phishing(text)
    is_safe_url = check_url_safety(url) if url else True

    result = {
        "phishing_detected": is_phishing,
        "url_safe": is_safe_url,
        "message": "⚠️ Podezření na phishing!" if is_phishing else "✅ Žádné hrozby nalezeny."
    }
    
    # Uložit výsledek do Google Sheets
    sheet.append_row([text, "Phishing" if is_phishing else "Safe", ""])
    
    return jsonify(result)

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    text = data.get("text", "")
    user_feedback = data.get("user_feedback", "")
    
    # Uložit zpětnou vazbu do Google Sheets
    sheet.append_row([text, "Corrected", user_feedback])
    
    return jsonify({"message": "Děkujeme za zpětnou vazbu!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
