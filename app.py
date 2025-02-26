kdef save_to_db(text, classification, user_feedback=None):
    """Uloží zprávu do databáze nebo aktualizuje existující záznam."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO phishing_data (text, classification, user_feedback)
            VALUES (%s, %s, %s)
            ON CONFLICT (text) DO UPDATE SET classification = EXCLUDED.classification, user_feedback = EXCLUDED.user_feedback;
        """, (text, classification, user_feedback))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Chyba při zápisu do databáze: {e}")
