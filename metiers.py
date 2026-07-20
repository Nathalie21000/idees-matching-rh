"""
Bibliothèque des métiers et mots-clés
Version V6
"""

METIERS = {

    "Ouvrier VRD": [
        "vrd",
        "voirie",
        "réseaux",
        "reseaux",
        "terrassement",
        "bordures",
        "canalisations",
        "assainissement",
        "enrobé",
        "enrobe"
    ],

    "Conducteur d'engins": [
        "conducteur d'engins",
        "engin",
        "mini pelle",
        "pelle",
        "chargeuse",
        "compacteur",
        "tractopelle",
        "r482",
        "caces r482"
    ],

    "Cariste": [
        "cariste",
        "r489",
        "caces r489",
        "gerbeur",
        "chariot",
        "logistique"
    ],

    "Préparateur de commandes": [
        "préparateur",
        "preparateur",
        "commande",
        "commandes",
        "scan",
        "picking",
        "logistique"
    ],

    "Agent de production": [
        "production",
        "industrie",
        "conditionnement",
        "assemblage",
        "fabrication"
    ],

    "Soudeur": [
        "soudeur",
        "mig",
        "mag",
        "tig",
        "soudure"
    ],

    "Électricien": [
        "électricien",
        "electricien",
        "habilitation",
        "b1",
        "b2",
        "br",
        "bc"
    ],

    "Maçon": [
        "maçon",
        "macon",
        "coffrage",
        "béton",
        "beton",
        "ferraillage"
    ]
}


def detecter_metier(texte):
    """
    Recherche le métier dominant.
    """

    texte = texte.lower()

    meilleur_metier = "Non détecté"
    meilleur_score = 0

    for metier, mots in METIERS.items():

        score = 0

        for mot in mots:
            if mot in texte:
                score += 1

        if score > meilleur_score:
            meilleur_score = score
            meilleur_metier = metier

    return meilleur_metier
