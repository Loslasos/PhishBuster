import gspread
from google.oauth2.service_account import Credentials
import json
import os

# Načtení Google API klíče
credentials_json = os.getenv("GOOGLE_CREDENTIALS")
if credentials_json is None:
    print("❌ GOOGLE_CREDENTIALS není nastaveno!")
else:
    credentials_info = json.loads(credentials_json)
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)

    try:
        client = gspread.authorize(credentials)
        sheet = client.open_by_key("1KJLQ1ZKIxb443BZ1Rjc9JZ62eZaSan-uNBZ55NVcpXY").sheet1
        print("✅ Připojení k tabulce úspěšné!")

        # Testovací zápis
        sheet.append_row(["Testovací zpráva", "Phishing", ""])
        print("✅ Zápis úspěšný!")
    except Exception as e:
        print(f"❌ Chyba: {e}")
