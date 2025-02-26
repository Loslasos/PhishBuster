import os
import psycopg2
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Připojení k databázi
DATABASE_URL = os.getenv("DATABASE_URL")

def get_classification_from_db(text):
    """Zjistí, zda text již existuje v databázi."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT classification FROM phishing_data WHERE text = %s", (text,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return result[0]
        return None
    except Exception as e:
        print(f"❌ Chyba při načítání z databáze: {e}")
        return None

def save_to_db(text, classification, user_feedback=None):
    """Uloží zprávu do databáze nebo aktualizuje existující záznam."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO phishing_data (text, classification, user_feedback)
            VALUES (%s, %s, %s)
            ON CONFLICT (text) DO UPDATE 
            SET classification = EXCLUDED.classification, 
                user_feedback = EXCLUDED.user_feedback;
        """, (text, classification, user_feedback))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Chyba při zápisu do databáze: {e}")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get("text", "")

    # Nejprve zkontrolujeme, zda už text není v databázi
    previous_classification = get_classification_from_db(text)
    if previous_classification:
        return jsonify({"message": f"✅ Analyzováno (historie): {previous_classification}"})

    # Detekce phishingu
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

@app.route('/feedback', methods=['POST'])
def feedback():
    """Zpracování zpětné vazby od uživatele."""
    data = request.json
    text = data.get("text", "")
    correct = data.get("correct", True)

    # Aktualizujeme databázi zpětnou vazbou
    save_to_db(text, "phishing" if not correct else "legit", user_feedback=correct)

    return jsonify({"message": "✅ Děkujeme za zpětnou vazbu!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render nastavuje PORT automaticky
    app.run(host='0.0.0.0', port=port, debug=True)
