"""
Petite application Flask -- version CORRIGÉE après le premier run du
pipeline (voir le run #1 sur GitHub Actions pour la version vulnérable
d'origine, conservée dans l'historique Git comme preuve de détection).

Corrections apportées suite aux findings SAST/Trivy :
    1. Secret retiré du code, chargé depuis une variable d'environnement.
    2. Requête SQL paramétrée (plus de concaténation de chaîne).
    3. Suppression de l'appel os.system() avec input utilisateur non validé.
    4. Debug mode désactivé.
"""

import os
import sqlite3
from flask import Flask, request, abort

app = Flask(__name__)

# --- Correction 1 : secret chargé depuis l'environnement, jamais codé en dur ---
API_KEY = os.environ.get("API_KEY", "")


@app.route("/user")
def get_user():
    """--- Correction 2 : requête paramétrée, plus d'injection SQL possible ---"""
    user_id = request.args.get("id")

    if not user_id or not user_id.isdigit():
        abort(400, description="Paramètre 'id' invalide.")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Requête paramétrée : la valeur n'est jamais interprétée comme du SQL
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchall()
    conn.close()
    return {"result": result}


@app.route("/ping")
def ping():
    """--- Correction 3 : plus d'exécution de commande système arbitraire ---

    L'ancien endpoint utilisait os.system() avec un input utilisateur non
    validé (RCE potentiel). Un vrai besoin de "ping" en production devrait
    utiliser une librairie réseau (ex: `ping3`) sans passer par un shell,
    avec une validation stricte de l'hôte (whitelist ou regex IP/hostname).
    Ce endpoint est désactivé ici pour rester dans le périmètre de la démo.
    """
    return {"status": "disabled", "reason": "Use a validated networking library instead of shell execution."}, 501


if __name__ == "__main__":
    # --- Correction 4 : debug mode désactivé avant tout déploiement ---
    app.run(host="0.0.0.0", debug=False)
