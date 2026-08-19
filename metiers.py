"""
Bibliothèque des métiers, compétences, tâches et mots-clés
Version V7
"""

import re


# ============================================================
# METIERS (mots-clés utilisés pour détecter le métier dominant)
# ============================================================

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
    ],

    "Manutentionnaire": [
        "manutentionnaire",
        "manutention",
        "port de charges",
        "port de charge",
        "colis"
    ],

    "Chauffeur PL / SPL": [
        "chauffeur pl",
        "chauffeur spl",
        "permis c",
        "permis ce",
        "livraison",
        "transport routier"
    ],

    "Agent d'entretien": [
        "agent d'entretien",
        "entretien",
        "nettoyage",
        "propreté",
        "proprete"
    ],

    "Employé libre-service": [
        "libre service",
        "libre-service",
        "grande distribution",
        "mise en rayon",
        "caisse"
    ],
}


def detecter_metier(texte):
    """
    Recherche le métier dominant en comptant les occurrences
    des mots-clés sur l'ensemble du texte (et non uniquement
    leur présence), pour mieux refléter le thème dominant
    du document.
    """

    texte_min = texte.lower()

    meilleur_metier = "Non détecté"
    meilleur_score = 0

    for metier, mots in METIERS.items():

        score = 0

        for mot in mots:
            score += len(re.findall(re.escape(mot), texte_min))

        if score > meilleur_score:
            meilleur_score = score
            meilleur_metier = metier

    return meilleur_metier


# ============================================================
# COMPETENCES PROFESSIONNELLES
# (indépendantes du métier, transférables)
# ============================================================

COMPETENCES_PRO = [
    "préparation de commandes",
    "conduite d'engins",
    "chargement",
    "déchargement",
    "gestion des stocks",
    "gestion de stock",
    "utilisation d'outils",
    "travail en équipe",
    "esprit d'équipe",
    "port de charges",
    "manutention",
    "contrôle qualité",
    "controle qualite",
    "respect des consignes de sécurité",
    "respect des consignes de securite",
    "polyvalence",
    "autonomie",
    "rigueur",
    "gestion du temps",
    "sens de l'organisation",
    "lecture de plan",
    "lecture de plans",
    "utilisation d'un scanner",
    "conduite de ligne",
    "montage",
    "assemblage",
    "câblage",
    "cablage",
    "soudure",
    "peinture industrielle",
    "nettoyage industriel",
    "tri",
    "emballage",
    "étiquetage",
    "etiquetage",
    "inventaire",
    "réception de marchandises",
    "reception de marchandises",
    "expédition",
    "expedition",
    "supervision d'équipe",
    "encadrement",
    "formation de nouveaux salariés",
    "maintenance de premier niveau",
    "diagnostic de panne",
    "sens du contact",
    "relation client",
    "gestion des priorités",
    "réactivité",
    "reactivite",
    "adaptabilité",
    "adaptabilite",
]


def extraire_competences_pro(texte):
    """
    Recherche les compétences professionnelles génériques
    présentes dans le texte.
    """

    texte_min = texte.lower()

    trouve = [
        c for c in COMPETENCES_PRO
        if c in texte_min
    ]

    return trouve


# ============================================================
# TACHES / MISSIONS REALISEES
# ============================================================

TACHES = [
    "préparation des commandes",
    "préparation de commandes",
    "chargement des camions",
    "déchargement des camions",
    "chargement de camions",
    "déchargement de camions",
    "réception des marchandises",
    "reception des marchandises",
    "expédition des marchandises",
    "expedition des marchandises",
    "conduite d'un chariot",
    "conduite de chariot",
    "conduite d'engins",
    "conduite de ligne de production",
    "approvisionnement des lignes",
    "approvisionnement de la ligne",
    "approvisionnement de ligne",
    "contrôle qualité des produits",
    "controle qualite des produits",
    "contrôle des produits",
    "controle des produits",
    "emballage des produits",
    "étiquetage des produits",
    "etiquetage des produits",
    "inventaire du stock",
    "inventaire des stocks",
    "gestion des stocks",
    "rangement de l'entrepôt",
    "rangement de l'entrepot",
    "nettoyage du poste de travail",
    "montage de pièces",
    "montage de pieces",
    "assemblage de pièces",
    "assemblage de pieces",
    "câblage électrique",
    "cablage electrique",
    "soudure de pièces",
    "soudure de pieces",
    "maintenance des équipements",
    "maintenance des equipements",
    "livraison de marchandises",
    "tri des colis",
    "tri des produits",
    "utilisation d'un scanner",
    "encadrement d'équipe",
    "encadrement d'equipe",
    "formation de nouveaux salariés",
    "formation de nouveaux salaries",
    "lecture de plans",
    "pose de bordures",
    "terrassement",
    "pose de canalisations",
    "coffrage",
    "ferraillage",
    "coulage de béton",
    "coulage de beton",
    "mise en rayon",
    "encaissement",
    "accueil client",
    "picking",
    "palettisation",
]


def extraire_taches(texte):
    """
    Recherche les tâches / missions concrètes mentionnées
    dans le texte (CV ou fiche de poste).
    """

    texte_min = texte.lower()

    trouve = [
        t for t in TACHES
        if t in texte_min
    ]

    return trouve


# ============================================================
# SUIVI MEDICAL VIP / SIR
# ============================================================

def detecter_vip_sir(texte):
    """
    Détecte si le texte mentionne un suivi VIP
    (Visite Infirmier Périodique) et/ou SIR
    (Suivi Individuel Renforcé).
    Utilise des bornes de mots pour éviter les faux positifs
    (ex : "désir", "choisir").
    """

    texte_min = texte.lower()

    vip = (
        bool(re.search(r"\bvip\b", texte_min))
        or "visite infirmier périodique" in texte_min
        or "visite infirmier periodique" in texte_min
    )

    sir = (
        bool(re.search(r"\bsir\b", texte_min))
        or "suivi individuel renforcé" in texte_min
        or "suivi individuel renforce" in texte_min
    )

    if vip and sir:
        return "VIP + SIR"

    if vip:
        return "VIP"

    if sir:
        return "SIR"

    return ""
