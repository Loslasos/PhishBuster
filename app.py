import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Připojení k databázi
DATABASE_URL = os.getenv("DATABASE_URL")

def save_to_db(text, classification, user_feedback=None):
    """Uloží zprávu do databáze."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO phishing_data (text, classification, user_feedback)
            VALUES (%s, %s, %s);
        """, (text, classification, user_feedback))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Chyba při zápisu do databáze: {e}")

@app.route('/')
def home():
    return "✅ PhishBuster API běží! Použij /analyze pro analýzu textu."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get("text", "")

    phishing_keywords = [
        "výhra", "dárek", "klikněte zde", "ověřte účet", "přihlaste se", "gratuluji",
        "iphone", "zdarma", "akce", "investice", "rychlý zisk", "bankovní údaje",
        "ověřovací kód", "získejte nyní", "exkluzivní nabídka", "vaše heslo vyprší",
        "bezplatná registrace", "vaše karta byla zablokována"
    ]

    classification = "phishing" if any(word in text.lower() for word in phishing_keywords) else "legit"

    # Uložíme výsledek do databáze
    save_to_db(text, classification)

    return jsonify({"message": f"✅ Analyzováno: {classification}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render nastavuje PORT automaticky
    app.run(host='0.0.0.0', port=port, debug=True)
