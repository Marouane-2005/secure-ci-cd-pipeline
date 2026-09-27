# Secure CI/CD Pipeline

Pipeline DevSecOps de bout en bout qui scanne automatiquement chaque commit
pour détecter des vulnérabilités de code, de dépendances, des secrets exposés
et des failles dans l'image Docker — avec un **quality gate** qui bloque le
build si un seuil de sévérité est dépassé.

## Architecture

```
Push / Pull Request
        │
        ▼
┌───────────────────────────────────────────────────┐
│                 GitHub Actions                     │
│                                                     │
│  ┌──────────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Secret Scan  │  │   SAST   │  │     SCA      │  │
│  │  (Gitleaks)  │  │(Semgrep) │  │(Dependency-  │  │
│  │              │  │          │  │   Check)     │  │
│  └──────────────┘  └──────────┘  └──────────────┘  │
│                                                     │
│              ┌──────────────────┐                  │
│              │  Container Scan  │                  │
│              │     (Trivy)      │                  │
│              └──────────────────┘                  │
│                        │                            │
│                        ▼                            │
│              ┌──────────────────┐                  │
│              │   Quality Gate   │                  │
│              │  (Python script) │                  │
│              └──────────────────┘                  │
│                        │                            │
│            Pass ✅            Fail ❌               │
│      (merge autorisé)   (build bloqué)              │
└───────────────────────────────────────────────────┘
```

## Stack technique

| Type de scan | Outil utilisé | Équivalent "entreprise" |
|---|---|---|
| Secrets | Gitleaks | GitGuardian |
| SAST | Semgrep | SonarQube |
| SCA (dépendances / CVE) | OWASP Dependency-Check (source: NVD) | Nexus IQ, Snyk |
| Container | Trivy | Twistlock, Aqua |
| Quality Gate | Script Python custom | SonarQube Quality Gate |

> Les outils open-source ont été choisis pour être reproductibles sans
> licence payante, mais remplissent le même rôle que SonarQube / Nexus IQ.

## Étapes pour lancer le projet

### 1. Prérequis
- Un compte GitHub
- Docker installé en local (pour tester avant de pousser)
- Python 3.11+

### 2. Mise en place du repo
```bash
git init
git add .
git commit -m "Initial commit: vulnerable app + secure CI pipeline"
git remote add origin https://github.com/<ton-user>/secure-ci-project.git
git push -u origin main
```

Le simple fait de pousser déclenche automatiquement le pipeline
(`.github/workflows/secure-pipeline.yml`).

### 3. Vérifier les résultats
- Onglet **Actions** du repo GitHub → voir les jobs s'exécuter
- Chaque job upload ses résultats en tant qu'**artifact** téléchargeable
- Le job `quality-gate` publie un résumé dans l'onglet **Summary** du run

### 4. Tester le quality gate en local
```bash
pip install -r app/requirements.txt
python3 quality_gate.py --results-dir ./scan-results
```

### 5. Ajuster les seuils
Modifie les valeurs dans `quality_gate.py` :
```python
THRESHOLDS = {
    "CRITICAL": 0,
    "HIGH": 2,
    "MEDIUM": 10,
    "LOW": 999,
}
```

## Vulnérabilités volontairement présentes (pour test)

L'app `app/app.py` contient des failles intentionnelles afin d'avoir des
résultats concrets à montrer :
- Secret codé en dur → détecté par **Gitleaks**
- Injection SQL → détectée par **Semgrep**
- Injection de commande OS → détectée par **Semgrep**
- Dépendances obsolètes avec CVE connues (`requirements.txt`) → détectées
  par **OWASP Dependency-Check**

⚠️ Ce code ne doit jamais être déployé en production. Il sert uniquement à
démontrer que le pipeline de sécurité fonctionne.

## Pour aller plus loin

- Ajouter **OPA (Open Policy Agent)** pour du policy-as-code sur l'infra
- Publier les résultats vers un dashboard centralisé
- Intégrer un mapping automatique vers OWASP Top 10 / MITRE ATT&CK
- Ajouter une notification Slack/Teams en cas d'échec du quality gate

## Lien avec le poste visé

Ce projet démontre :
- L'intégration de contrôles de sécurité dans les pratiques **DevSecOps**
- L'usage de données **CVE/NVD** pour l'évaluation des vulnérabilités
- La capacité à concevoir une **quality gate automatisée** basée sur la
  sévérité (au lieu d'un audit manuel)
- Une logique de **suivi des actions correctives** via les rapports générés
