import psycopg2
import os

# Připojení k databázi
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Vytvoření tabulky pro phishing data
cur.execute("""
    CREATE TABLE IF NOT EXISTS phishing_data (
        id SERIAL PRIMARY KEY,
        text TEXT NOT NULL,
        classification TEXT NOT NULL,
        user_feedback TEXT
    );
""")

# Uložit změny a zavřít připojení
conn.commit()
cur.close()
conn.close()

print("✅ Tabulka 'phishing_data' byla úspěšně vytvořena!")
