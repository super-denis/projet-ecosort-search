"""
Prediction : associe une image de produit a une categorie de poubelle.
Responsable : Denis (IA)

Expose la fonction du contrat :
    predire_categorie(image) -> dict
"""

import os
import re
import json
from PIL import Image
import numpy as np

# --- Ordre des classes EXACT tel qu'appris a l'entrainement ---
# Lu depuis le fichier genere par train.py (sinon fallback par defaut).
_CN_PATH = os.path.join(os.path.dirname(__file__), "class_names.json")
if os.path.exists(_CN_PATH):
    with open(_CN_PATH) as f:
        CLASSES = json.load(f)
else:
    CLASSES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

# --- Mapping classe modele -> poubelle + couleur ---
MAPPING = {
    "plastic":   ("JAUNE",          "#FFD700"),
    "metal":     ("JAUNE",          "#FFD700"),
    "cardboard": ("JAUNE",          "#FFD700"),
    "glass":     ("VERTE",          "#2E7D32"),
    "paper":     ("BLEUE",          "#1565C0"),
    "trash":     ("MARRON / NOIRE", "#4E342E"),
}

# --- D3E : detecte par mots-cles sur le TITRE (pas par l'image) ---
# 1) Sous-chaines sures (marques + appareils electroniques courants)
MOTS_CLES_D3E = [
    # appareils
    "smartphone", "telephone", "phone", "portable", "ecouteur", "casque",
    "chargeur", "charger", "batterie", "power bank", "powerbank", "pile",
    "smartwatch", "montre connectee", "mixeur", "blender", "ordinateur",
    "laptop", "tablette", "tablet", "camera", "television", "televiseur",
    "console", "manette", "clavier", "souris", "imprimante", "ventilateur",
    "refrigerateur", "climatiseur", "radio", "haut-parleur", "speaker",
    "enceinte", "ampoule", "projecteur", "decodeur",
    # marques repandues en Cote d'Ivoire
    "tecno", "infinix", "itel", "xiaomi", "redmi", "samsung", "galaxy",
    "iphone", "apple", "oppo", "huawei", "nokia", "realme", "vivo", "honor",
]

# 2) Motifs "mot entier" (specs) - evite les faux positifs type "caramel"
PATTERNS_D3E = [
    r"\bmah\b", r"\brom\b", r"\bram\b", r"\bsim\b", r"\bmpx\b", r"\bmp\b",
    r"\bgo\b", r"\bgb\b", r"\bused\b", r"\busb\b", r"\bled\b", r"\btv\b",
    r"\bpc\b", r"\b\dg\b",
]

COULEUR_D3E = "#616161"

_model = None  # charge une seule fois (lazy loading)


def _charger_modele():
    global _model
    if _model is None:
        from tensorflow.keras.models import load_model
        _model = load_model("model/modele_eco_sort.h5")
    return _model


def est_d3e(titre: str) -> bool:
    """True si le titre du produit evoque un appareil electrique/electronique."""
    t = titre.lower()
    if any(mot in t for mot in MOTS_CLES_D3E):
        return True
    return any(re.search(p, t) for p in PATTERNS_D3E)


def categorie_d3e() -> dict:
    return {
        "categorie": "D3E / ELECTRONIQUE",
        "couleur_hex": COULEUR_D3E,
        "classe_brute": "electronique",
        "confiance": 1.0,
    }


def predire_categorie(image) -> dict:
    """
    image : objet PIL.Image
    retourne : {categorie, couleur_hex, classe_brute, confiance}
    """
    model = _charger_modele()

    # Pretraitement : 224x224, image brute 0-255.
    # PAS de normalisation ici : preprocess_input est deja integre DANS le
    # modele (voir train.py), donc on lui passe l'image brute.
    img = image.convert("RGB").resize((224, 224))
    arr = np.array(img, dtype="float32")
    arr = np.expand_dims(arr, axis=0)

    probas = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(probas))
    classe = CLASSES[idx]
    confiance = float(probas[idx])

    categorie, couleur = MAPPING[classe]
    return {
        "categorie": categorie,
        "couleur_hex": couleur,
        "classe_brute": classe,
        "confiance": confiance,
    }
