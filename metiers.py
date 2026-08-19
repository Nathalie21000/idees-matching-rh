"""
Bibliothèque des métiers, compétences, tâches et mots-clés
Version V9 - Extraction renforcée des fiches de poste

Objectifs :
- Détecter le métier
- Extraire les compétences
- Extraire les tâches
- Détecter VIP / SIR
- Lire les rubriques structurées des fiches de poste
- Récupérer directement :
    * Nom de l'entreprise
    * Intitulé du poste
    * Liste des tâches à proposer
"""

import re


# ============================================================
# METIERS
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
        "enrobe",
    ],

    "Conducteur d'engins": [
        "conducteur d'engins",
        "conducteur engins",
        "engin",
        "mini pelle",
        "minipelle",
        "pelle",
        "chargeuse",
        "compacteur",
        "tractopelle",
        "r482",
        "caces r482",
    ],

    "Cariste": [
        "cariste",
        "r489",
        "caces r489",
        "gerbeur",
        "chariot",
        "logistique",
    ],

    "Préparateur de commandes": [
        "préparateur",
        "preparateur",
        "préparateur de commandes",
        "preparateur de commandes",
        "commande",
        "commandes",
        "scan",
        "picking",
        "logistique",
    ],

    "Agent de production": [
        "production",
        "industrie",
        "conditionnement",
        "assemblage",
        "fabrication",
    ],

    "Soudeur": [
        "soudeur",
        "mig",
        "mag",
        "tig",
        "soudure",
    ],

    "Électricien": [
        "électricien",
        "electricien",
        "habilitation",
        "b1",
        "b2",
        "br",
        "bc",
    ],

    "Maçon": [
        "maçon",
        "macon",
        "coffrage",
        "béton",
        "beton",
        "ferraillage",
    ],

    "Manutentionnaire": [
        "manutentionnaire",
        "manutention",
        "port de charges",
        "port de charge",
        "colis",
    ],

    "Chauffeur PL / SPL": [
        "chauffeur pl",
        "chauffeur spl",
        "conducteur pl",
        "conducteur spl",
        "permis c",
        "permis ce",
        "livraison",
        "transport routier",
    ],

    "Agent d'entretien": [
        "agent d'entretien",
        "entretien",
        "nettoyage",
        "propreté",
        "proprete",
    ],

    "Employé libre-service": [
        "libre service",
        "libre-service",
        "grande distribution",
        "mise en rayon",
        "caisse",
    ],
}


def detecter_metier(texte):
    """
    Recherche le métier dominant en comptant les occurrences
    des mots-clés présents dans le texte.
    """

    if not texte:
        return "Non détecté"

    texte_min = texte.lower()

    meilleur_metier = "Non détecté"
    meilleur_score = 0

    for metier, mots in METIERS.items():

        score = 0

        for mot in mots:
            score += len(
                re.findall(
                    re.escape(mot.lower()),
                    texte_min,
                )
            )

        if score > meilleur_score:
            meilleur_score = score
            meilleur_metier = metier

    return meilleur_metier


# ============================================================
# COMPETENCES PROFESSIONNELLES
# ============================================================

COMPETENCES_PRO = [
    "préparation de commandes",
    "préparation des commandes",
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
    "respect des consignes de sécurité",
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
    "soudure",
    "peinture industrielle",
    "nettoyage industriel",
    "tri",
    "emballage",
    "étiquetage",
    "inventaire",
    "réception de marchandises",
    "expédition",
    "supervision d'équipe",
    "encadrement",
    "formation de nouveaux salariés",
    "maintenance de premier niveau",
    "diagnostic de panne",
    "sens du contact",
    "relation client",
    "gestion des priorités",
    "réactivité",
    "adaptabilité",
]


def extraire_competences_pro(texte):
    """
    Recherche les compétences professionnelles génériques
    présentes dans le texte.
    """

    if not texte:
        return []

    texte_min = texte.lower()

    trouvees = []

    for competence in COMPETENCES_PRO:

        if competence.lower() in texte_min:
            trouvees.append(competence)

    return trouvees


# ============================================================
# TACHES / MISSIONS
# ============================================================

TACHES = [
    "préparation des commandes",
    "préparation de commandes",
    "chargement des camions",
    "déchargement des camions",
    "réception des marchandises",
    "expédition des marchandises",
    "conduite d'un chariot",
    "conduite de chariot",
    "conduite d'engins",
    "conduite de ligne de production",
    "approvisionnement des lignes",
    "contrôle qualité des produits",
    "emballage des produits",
    "étiquetage des produits",
    "inventaire du stock",
    "gestion des stocks",
    "rangement de l'entrepôt",
    "nettoyage du poste de travail",
    "montage de pièces",
    "assemblage de pièces",
    "câblage électrique",
    "soudure de pièces",
    "maintenance des équipements",
    "livraison de marchandises",
    "tri des colis",
    "utilisation d'un scanner",
    "encadrement d'équipe",
    "formation de nouveaux salariés",
    "lecture de plans",
    "pose de bordures",
    "terrassement",
    "pose de canalisations",
    "coffrage",
    "ferraillage",
    "coulage de béton",
    "mise en rayon",
    "encaissement",
    "accueil client",
    "picking",
    "palettisation",
]


def extraire_taches(texte):
    """
    Recherche les tâches/missions connues dans le texte.
    """

    if not texte:
        return []

    texte_min = texte.lower()

    trouvees = []

    for tache in TACHES:

        if tache.lower() in texte_min:
            trouvees.append(tache)

    return trouvees


# ============================================================
# VERBES D'ACTION
# ============================================================

VERBES_ACTION = [
    "préparer",
    "prépare",
    "préparation",

    "charger",
    "charge",
    "chargement",

    "décharger",
    "décharge",
    "déchargement",

    "contrôler",
    "contrôle",
    "controle",
    "contrôle qualité",

    "utiliser",
    "utilise",
    "utilisation",

    "conduire",
    "conduit",
    "conduite",

    "assembler",
    "assemble",
    "assemblage",

    "monter",
    "monte",
    "montage",

    "souder",
    "soude",
    "soudure",

    "nettoyer",
    "nettoie",
    "nettoyage",

    "ranger",
    "range",
    "rangement",

    "gérer",
    "gère",
    "gestion",

    "réceptionner",
    "réceptionne",
    "réception",

    "expédier",
    "expédie",
    "expédition",

    "trier",
    "trie",
    "tri",

    "étiqueter",
    "étiquette",
    "étiquetage",

    "emballer",
    "emballe",
    "emballage",

    "livrer",
    "livre",
    "livraison",

    "encadrer",
    "encadre",
    "encadrement",

    "former",
    "forme",
    "formation",

    "câbler",
    "câble",
    "câblage",

    "poser",
    "pose",

    "couler",
    "coule",
    "coulage",

    "coffrer",
    "coffre",
    "coffrage",

    "ferrailler",
    "ferraille",
    "ferraillage",

    "terrasser",
    "terrasse",
    "terrassement",

    "encaisser",
    "encaisse",
    "encaissement",

    "accueillir",
    "accueille",
    "accueil",

    "manutentionner",
    "manutentionne",
    "manutention",

    "approvisionner",
    "approvisionne",
    "approvisionnement",

    "installer",
    "installe",

    "vérifier",
    "vérifie",
    "vérification",

    "surveiller",
    "surveille",
    "surveillance",

    "inspecter",
    "inspecte",
    "inspection",

    "manipuler",
    "manipule",
    "manipulation",

    "fabriquer",
    "fabrique",
    "fabrication",

    "produire",
    "produit",
    "production",

    "peindre",
    "peint",
    "peinture",

    "picker",
    "pick",

    "palettiser",
    "palettise",
]


def extraire_taches_par_lignes(
    texte_brut,
    rubrique_actuelle=""
):
    """
    Détecte les lignes commençant par un verbe d'action.

    Cette fonction reste utile notamment pour les CV où les
    collègues écrivent des missions dans la rubrique
    "Compétences".
    """

    if not texte_brut:
        return {}

    taches_par_rubrique = {}

    for ligne in texte_brut.split("\n"):

        ligne_nettoyee = ligne.strip()

        if not ligne_nettoyee:
            continue

        if len(ligne_nettoyee) > 180:
            continue

        ligne_test = ligne_nettoyee.lower()

        # Suppression des puces
        ligne_test = re.sub(
            r"^[\-\–\—•\*\·]+\s*",
            "",
            ligne_test,
        )

        premier_mot = re.split(
            r"[\s,;:.]+",
            ligne_test,
        )[0]

        if premier_mot in VERBES_ACTION:

            if rubrique_actuelle not in taches_par_rubrique:
                taches_par_rubrique[rubrique_actuelle] = []

            valeur = ligne_nettoyee.rstrip(
                ".,:;"
            )

            if valeur not in taches_par_rubrique[rubrique_actuelle]:

                taches_par_rubrique[
                    rubrique_actuelle
                ].append(valeur)

    return taches_par_rubrique


# ============================================================
# VIP / SIR
# ============================================================

def detecter_vip_sir(texte):
    """
    Détecte la présence de VIP et/ou SIR.
    """

    if not texte:
        return ""

    texte_min = texte.lower()

    vip = (
        bool(re.search(r"\bvip\b", texte_min))
        or "visite infirmier périodique" in texte_min
        or "visite infirmier periodique" in texte_min
        or "visite d'information et de prévention" in texte_min
        or "visite d information et de prévention" in texte_min
        or "visite information et prevention" in texte_min
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


# ============================================================
# OUTILS DE NORMALISATION
# ============================================================

def _normaliser_texte(texte):
    """
    Normalise un texte pour permettre des recherches robustes
    même lorsque utils.py a supprimé les accents ou la ponctuation.
    """

    if not texte:
        return ""

    texte = texte.lower()

    remplacements = {
        "’": "'",
        "–": "-",
        "—": "-",
        "\n": " ",
        "\r": " ",
        "\t": " ",
    }

    for ancien, nouveau in remplacements.items():
        texte = texte.replace(ancien, nouveau)

    texte = re.sub(
        r"\s+",
        " ",
        texte,
    )

    return texte.strip()


def _normaliser_libelle(texte):
    """
    Rend les comparaisons de libellés plus tolérantes.
    """

    if not texte:
        return ""

    texte = texte.lower()

    # Accents
    traductions = str.maketrans(
        "àâäéèêëîïôöùûüÿç",
        "aaaeeeeiioouuuyc",
    )

    texte = texte.translate(traductions)

    texte = texte.replace(
        "’",
        "'",
    )

    texte = re.sub(
        r"[^a-z0-9]+",
        " ",
        texte,
    )

    texte = re.sub(
        r"\s+",
        " ",
        texte,
    )

    return texte.strip()


# ============================================================
# LIBELLES DU MODELE DE FICHE DE POSTE
# ============================================================

LIBELLES_FICHE_POSTE = {

    "entreprise": [
        "nom de l'entreprise",
        "nom de entreprise",
        "entreprise",
    ],

    "intitule": [
        "intitulé du poste",
        "intitule du poste",
        "intitulé poste",
        "intitule poste",
    ],

    "taches": [
        "liste des tâches à proposer",
        "liste des taches a proposer",
        "liste des tâches proposer",
        "liste des taches proposer",
        "tâches à proposer",
        "taches a proposer",
    ],

    "habilitations": [
        "habilitations, certificats et diplômes obligatoires",
        "habilitations certificats et diplômes obligatoires",
        "habilitations certificats et diplomes obligatoires",
        "habilitations",
    ],

    "conduite_engins": [
        "conduite d'engins",
        "conduite d engins",
    ],

    "machines_outils": [
        "utilisation de machines / outils",
        "utilisation de machines outils",
        "utilisation de machines",
        "machines / outils",
        "machines outils",
    ],

    "securite_risques": [
        "sécurité et risques",
        "securite et risques",
        "consignes de sécurité",
        "consignes de securite",
        "sécurité",
        "securite",
        "risques",
    ],
}


# ============================================================
# RECHERCHE D'UN LIBELLE
# ============================================================

def _trouver_libelle(
    texte,
    libelles,
):
    """
    Recherche la position d'un libellé dans le texte.

    Retourne :
        (position_debut, position_fin)
    ou :
        None
    """

    if not texte:
        return None

    texte_normalise = _normaliser_libelle(
        texte
    )

    meilleur = None

    for libelle in libelles:

        libelle_normalise = _normaliser_libelle(
            libelle
        )

        if not libelle_normalise:
            continue

        position = texte_normalise.find(
            libelle_normalise
        )

        if position >= 0:

            fin = position + len(
                libelle_normalise
            )

            if meilleur is None or position < meilleur[0]:

                meilleur = (
                    position,
                    fin,
                    libelle_normalise,
                )

    return meilleur


# ============================================================
# EXTRACTION ENTRE DEUX RUBRIQUES
# ============================================================

def _extraire_valeur_rubrique(
    texte,
    libelles_depart,
    toutes_les_rubriques,
):
    """
    Extrait le contenu situé après un libellé et avant
    le prochain libellé connu.

    Cette méthode est importante car le texte venant de
    utils.py peut être aplati sur une seule ligne.
    """

    if not texte:
        return ""

    texte_normalise = _normaliser_libelle(
        texte
    )

    depart = _trouver_libelle(
        texte,
        libelles_depart,
    )

    if not depart:
        return ""

    position_depart = depart[1]

    prochaine_position = len(
        texte_normalise
    )

    for nom_rubrique, libelles in toutes_les_rubriques.items():

        if libelles is libelles_depart:
            continue

        position = _trouver_libelle(
            texte,
            libelles,
        )

        if not position:
            continue

        position_debut = position[0]

        if position_debut > position_depart:

            prochaine_position = min(
                prochaine_position,
                position_debut,
            )

    valeur = texte_normalise[
        position_depart:prochaine_position
    ]

    valeur = valeur.strip(
        " :;-–—|/"
    )

    return valeur.strip()


# ============================================================
# EXTRACTION SPECIFIQUE DE LA FICHE DE POSTE
# ============================================================

def extraire_sections_poste(texte_brut):
    """
    Extraction structurée des informations de la fiche de poste.

    Priorité aux libellés du modèle :

    - Nom de l'entreprise
    - Intitulé du poste
    - Liste des tâches à proposer
    - Habilitations...
    - Conduite d'engins
    - Utilisation de machines / outils
    - Sécurité / risques

    Retourne un dictionnaire exploitable directement
    par app.py.
    """

    resultat = {
        "entreprise": "",
        "intitule": "",
        "taches": "",
        "habilitations": "",
        "conduite_engins": "",
        "machines_outils": "",
        "securite_risques": "",
        "vip": False,
        "sir": False,
    }

    if not texte_brut:
        return resultat

    for rubrique, libelles in LIBELLES_FICHE_POSTE.items():

        valeur = _extraire_valeur_rubrique(
            texte_brut,
            libelles,
            LIBELLES_FICHE_POSTE,
        )

        resultat[rubrique] = valeur

    # --------------------------------------------------------
    # VIP / SIR
    # --------------------------------------------------------

    texte_min = _normaliser_texte(
        texte_brut
    )

    resultat["vip"] = (
        bool(re.search(
            r"\bvip\b",
            texte_min,
        ))
        or "visite infirmier périodique" in texte_min
        or "visite infirmier periodique" in texte_min
        or "visite d'information et de prévention" in texte_min
        or "visite d information et de prevention" in texte_min
    )

    resultat["sir"] = (
        bool(re.search(
            r"\bsir\b",
            texte_min,
        ))
        or "suivi individuel renforcé" in texte_min
        or "suivi individuel renforce" in texte_min
    )

    return resultat


# ============================================================
# ANALYSE COMPLETE DE LA FICHE DE POSTE
# ============================================================

def analyser_fiche_poste(texte_brut):
    """
    Analyse complète d'une fiche de poste.

    Les rubriques du modèle sont prioritaires.

    Si une information n'est pas trouvée directement,
    l'application utilise les anciennes méthodes de secours.
    """

    sections = extraire_sections_poste(
        texte_brut
    )

    # --------------------------------------------------------
    # ENTREPRISE
    # --------------------------------------------------------

    if not sections.get("entreprise"):

        sections["entreprise"] = ""

    # --------------------------------------------------------
    # INTITULE
    # --------------------------------------------------------

    if not sections.get("intitule"):

        sections["intitule"] = detecter_metier(
            texte_brut
        )

    # --------------------------------------------------------
    # TACHES
    # --------------------------------------------------------

    if not sections.get("taches"):

        taches_generiques = extraire_taches(
            texte_brut
        )

        sections["taches"] = " / ".join(
            taches_generiques
        )

    # --------------------------------------------------------
    # COMPETENCES
    # --------------------------------------------------------

    sections["competences"] = " / ".join(
        extraire_competences_pro(
            texte_brut
        )
    )

    # --------------------------------------------------------
    # VIP / SIR
    # --------------------------------------------------------

    if sections.get("vip") and sections.get("sir"):

        sections["vip_sir"] = "VIP + SIR"

    elif sections.get("vip"):

        sections["vip_sir"] = "VIP"

    elif sections.get("sir"):

        sections["vip_sir"] = "SIR"

    else:

        sections["vip_sir"] = ""

    # --------------------------------------------------------
    # TACHES PAR RUBRIQUE
    # --------------------------------------------------------

    sections["taches_par_rubrique"] = (
        extraire_taches_par_lignes(
            texte_brut
        )
    )

    return sections
