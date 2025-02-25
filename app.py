from flask import Flask, render_template, request, jsonify
import re
import requests

app = Flask(__name__)

# Databáze phishingových frází v češtině
PHISHING_PATTERNS = [
    r'Vaše heslo vyprší', r'Obnovte jej zde', r'Klikněte na tento odkaz', r'Potvrzení účtu',
    r'Nezaplacená faktura', r'Dluh bude postoupen exekutorovi', r'Neobvyklá aktivita na vašem účtu',
    r'Vyhráli jste iPhone', r'Výhra čeká', r'Musíte jednat ihned', r'Vaše banka vás kontaktuje',
    r'Přihlaste se pro potvrzení platby', r'Zabezpečení účtu bylo kompromitováno', r'Váš účet bude zablokován',
    r'Aktuální platba nebyla provedena', r'Ověřte svou totožnost', r'Nesrovnalost ve vašem účtu',
    r'Máte nový bezpečnostní upozornění', r'Zadejte své údaje pro ověření', r'Vaše karta byla zneužita',
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
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

