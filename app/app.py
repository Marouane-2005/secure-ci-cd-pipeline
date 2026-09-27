"""
Petite application Flask VOLONTAIREMENT VULNÉRABLE.
Sert uniquement à générer des résultats de scan (SAST) intéressants
pour démontrer le pipeline CI/CD sécurisé.

NE JAMAIS DÉPLOYER CE CODE EN PRODUCTION TEL QUEL.
"""

import sqlite3
from flask import Flask, request

app = Flask(__name__)

# --- Vulnérabilité 1 : secret codé en dur (sera détecté par Gitleaks) ---
API_KEY = "FAKE_DEMO_API_KEY_1234567890abcdef"
DB_PASSWORD = "SuperSecretPassword123!"


@app.route("/user")
def get_user():
    """--- Vulnérabilité 2 : SQL Injection (sera détecté par Semgrep) ---"""
    user_id = request.args.get("id")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Concaténation directe de l'input utilisateur = injection SQL
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    cursor.execute(query)
    result = cursor.fetchall()
    return {"result": result}


@app.route("/ping")
def ping():
    """--- Vulnérabilité 3 : os.system avec input utilisateur (RCE potentiel) ---"""
    import os
    host = request.args.get("host", "localhost")
    os.system("ping -c 1 " + host)  # Commande injectable
    return {"status": "pinged"}


if __name__ == "__main__":
    # --- Vulnérabilité 4 : debug mode activé + bind sur toutes les interfaces ---
    app.run(host="0.0.0.0", debug=True)
