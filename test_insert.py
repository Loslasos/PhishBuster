import psycopg2
import os

# Připojení k databázi
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Testovací zápis
cur.execute("""
    INSERT INTO phishing_data (text, classification, user_feedback)
    VALUES ('Toto je testovací phishingová zpráva.', 'phishing', NULL);
""")

# Uložit změny a zavřít připojení
conn.commit()
cur.close()
conn.close()

print("✅ Testovací data byla úspěšně vložena do databáze!")
