import json
import os
import re
import requests
import gspread
from google.oauth2.service_account import Credentials
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Načtení Google API klíče z Render environment variable
credentials_json = os.getenv("GOOGLE_CREDENTIALS")
if credentials_json:
    credentials_info = json.loads(credentials_json)
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    client = gspread.authorize(credentials)
    try:
        sheet = client.open_by_key("1KJLQ1ZKIxb443BZ1Rjc9JZ62eZaSan-uNBZ55NVcpXY").sheet1
        print("✅ Úspěšně připojeno k Google Sheets!")
    except gspread.exceptions.APIError as api_err:
        print(f"❌ Google Sheets API error: {api_err}")
        sheet = None
    except gspread.exceptions.SpreadsheetNotFound:
        print("❌ Chyba: Tabulka nebyla nalezena. Zkontroluj správnost ID!")
        sheet = None
    except PermissionError:
        print("❌ Chyba: Nedostatečná oprávnění k přístupu do tabulky!")
        sheet = None
    except Exception as e:
        print(f"❌ Neočekávaná chyba: {e}")
        sheet = None
else:
    sheet = None
    print("⚠️ GOOGLE_CREDENTIALS není nastaveno! Google Sheets nebude fungovat.")

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
    
    # Uložit výsledek do Google Sheets (pokud je připojení k dispozici)
    if sheet:
        sheet.append_row([text, "Phishing" if is_phishing else "Safe", ""])
    
    return jsonify(result)

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.json
    text = data.get("text", "")
    user_feedback = data.get("user_feedback", "")
    
    # Uložit zpětnou vazbu do Google Sheets (pokud je připojení k dispozici)
    if sheet:
        sheet.append_row([text, "Corrected", user_feedback])
    
    return jsonify({"message": "Děkujeme za zpětnou vazbu!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)

