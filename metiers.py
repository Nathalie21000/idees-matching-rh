"""
Bibliothèque des métiers, compétences, tâches et mots-clés
Version V9 - Extraction améliorée des tâches
"""

import re


# ============================================================
# METIERS
# ============================================================

METIERS = {
    "Ouvrier VRD": [
        "vrd", "voirie", "réseaux", "reseaux", "terrassement",
        "bordures", "canalisations", "assainissement", "enrobé", "enrobe"
    ],
    "Conducteur d'engins": [
        "conducteur d'engins", "engin", "mini pelle", "pelle",
        "chargeuse", "compacteur", "tractopelle", "r482", "caces r482"
    ],
    "Cariste": [
        "cariste", "r489", "caces r489", "gerbeur", "chariot", "logistique"
    ],
    "Préparateur de commandes": [
        "préparateur", "preparateur", "commande", "commandes",
        "scan", "picking", "logistique"
    ],
    "Agent de production": [
        "production", "industrie", "conditionnement", "assemblage", "fabrication"
    ],
    "Soudeur": [
        "soudeur", "mig", "mag", "tig", "soudure"
    ],
    "Électricien": [
        "électricien", "electricien", "habilitation",
        "b1", "b2", "br", "bc"
    ],
    "Maçon": [
        "maçon", "macon", "coffrage", "béton", "beton", "ferraillage"
    ],
    "Manutentionnaire": [
        "manutentionnaire", "manutention",
        "port de charges", "port de charge", "colis"
    ],
    "Chauffeur PL / SPL": [
        "chauffeur pl", "chauffeur spl",
        "permis c", "permis ce", "livraison", "transport routier"
    ],
    "Agent d'entretien": [
        "agent d'entretien", "entretien",
        "nettoyage", "propreté", "proprete"
    ],
    "Employé libre-service": [
        "libre service", "libre-service",
        "grande distribution", "mise en rayon", "caisse"
    ],
}


def detecter_metier(texte):
    """Détecte le métier dominant à partir des mots-clés."""

    if not texte:
        return "Non détecté"

    texte_min = texte.lower()
    meilleur_metier = "Non détecté"
    meilleur_score = 0

    for metier, mots in METIERS.items():
        score = sum(
            len(re.findall(re.escape(mot), texte_min))
            for mot in mots
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
    """Recherche les compétences professionnelles génériques."""

    if not texte:
        return []

    texte_min = texte.lower()

    return [
        competence
        for competence in COMPETENCES_PRO
        if competence in texte_min
    ]


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
    """Recherche les tâches connues présentes dans le texte."""

    if not texte:
        return []

    texte_min = texte.lower()

    return [
        tache
        for tache in TACHES
        if tache in texte_min
    ]


# ============================================================
# VERBES / FORMULATIONS D'ACTION
# ============================================================

VERBES_ACTION = [
    "préparer",
    "prépare",
    "charger",
    "charge",
    "décharger",
    "décharge",
    "contrôler",
    "controle",
    "contrôle",
    "utiliser",
    "utilise",
    "conduire",
    "conduit",
    "assembler",
    "assemble",
    "monter",
    "monte",
    "souder",
    "soude",
    "nettoyer",
    "nettoie",
    "ranger",
    "range",
    "gérer",
    "gere",
    "gère",
    "réceptionner",
    "receptionner",
    "réceptionne",
    "expédier",
    "expedier",
    "expédie",
    "trier",
    "trie",
    "étiqueter",
    "etiqueter",
    "étiquette",
    "emballer",
    "emballe",
    "livrer",
    "livre",
    "encadrer",
    "encadre",
    "former",
    "forme",
    "câbler",
    "cable",
    "câble",
    "poser",
    "pose",
    "couler",
    "coule",
    "coffrer",
    "coffre",
    "ferrailler",
    "ferraille",
    "terrasser",
    "terrasse",
    "encaisser",
    "encaisse",
    "accueillir",
    "accueille",
    "manutentionner",
    "manutentionne",
    "approvisionner",
    "approvisionne",
    "installer",
    "installe",
    "vérifier",
    "verifier",
    "vérifie",
    "surveiller",
    "surveille",
    "inspecter",
    "inspecte",
    "manipuler",
    "manipule",
    "fabriquer",
    "fabrique",
    "produire",
    "produit",
    "peindre",
    "peint",
    "picker",
    "pick",
    "palettiser",
    "palettise",
]


# Formulations nominales très fréquentes dans les CV.
# Elles sont considérées comme des tâches lorsqu'elles
# constituent une ligne ou un élément autonome.
FORMULATIONS_TACHES = [
    "préparation ",
    "chargement ",
    "déchargement ",
    "contrôle ",
    "controle ",
    "utilisation ",
    "conduite ",
    "assemblage ",
    "montage ",
    "soudure ",
    "nettoyage ",
    "rangement ",
    "gestion ",
    "réception ",
    "reception ",
    "expédition ",
    "expedition ",
    "tri ",
    "étiquetage ",
    "etiquetage ",
    "emballage ",
    "livraison ",
    "encadrement ",
    "formation ",
    "câblage ",
    "cablage ",
    "pose ",
    "coulage ",
    "coffrage ",
    "ferraillage ",
    "terrassement ",
    "manutention ",
    "approvisionnement ",
    "installation ",
    "vérification ",
    "verification ",
    "surveillance ",
    "inspection ",
    "manipulation ",
    "fabrication ",
    "production ",
    "peinture ",
    "palettisation ",
    "picking ",
    "mise en rayon ",
    "accueil ",
]


def _nettoyer_ligne_tache(ligne):
    """Nettoie une ligne avant analyse."""

    ligne = ligne.strip()

    # Suppression des puces
    ligne = re.sub(
        r"^[\s\-•*·▪◦►→]+",
        "",
        ligne
    )

    # Suppression des espaces multiples
    ligne = re.sub(r"\s+", " ", ligne)

    return ligne.strip(" .,;:-")


def _premier_mot(ligne):
    """Retourne le premier mot significatif d'une ligne."""

    ligne = _nettoyer_ligne_tache(ligne)

    if not ligne:
        return ""

    morceaux = re.split(r"[\s,;:.!?]+", ligne.lower())

    return morceaux[0].strip()


def est_ligne_tache(ligne):
    """
    Détermine si une ligne ressemble à une tâche réalisée.

    Une ligne est reconnue si :
    - elle commence par un verbe d'action ;
    - ou elle commence par une formulation nominale typique
      d'une tâche.
    """

    ligne = _nettoyer_ligne_tache(ligne)

    if not ligne:
        return False

    if len(ligne) > 180:
        return False

    ligne_min = ligne.lower()

    premier = _premier_mot(ligne)

    if premier in VERBES_ACTION:
        return True

    for formulation in FORMULATIONS_TACHES:
        if ligne_min.startswith(formulation):
            return True

    return False


def extraire_taches_par_lignes(
    texte_brut,
    rubrique_actuelle=""
):
    """
    Analyse le texte ligne par ligne.

    Les tâches sont conservées avec leur rubrique d'origine.

    Exemple :
        Compétences
        Préparer les commandes
        Charger les camions

    devient :
        {
            "Compétences": [
                "Préparer les commandes",
                "Charger les camions"
            ]
        }
    """

    if not texte_brut:
        return {}

    taches_par_rubrique = {}

    rubrique = rubrique_actuelle or "Document"

    for ligne in texte_brut.splitlines():

        ligne_nettoyee = _nettoyer_ligne_tache(ligne)

        if not ligne_nettoyee:
            continue

        if est_ligne_tache(ligne_nettoyee):

            if rubrique not in taches_par_rubrique:
                taches_par_rubrique[rubrique] = []

            if ligne_nettoyee not in taches_par_rubrique[rubrique]:
                taches_par_rubrique[rubrique].append(
                    ligne_nettoyee
                )

    return taches_par_rubrique


def extraire_taches_cv(texte_brut):
    """
    Extraction spécifique des tâches réalisées dans un CV.

    Contrairement à extraire_taches_par_lignes(), cette fonction
    renvoie directement une liste unique de tâches.
    """

    if not texte_brut:
        return []

    resultat = []

    for ligne in texte_brut.splitlines():

        ligne_nettoyee = _nettoyer_ligne_tache(ligne)

        if not ligne_nettoyee:
            continue

        if est_ligne_tache(ligne_nettoyee):

            if ligne_nettoyee not in resultat:
                resultat.append(ligne_nettoyee)

    # Ajout des tâches connues présentes dans le texte,
    # même si leur formulation n'était pas sur une ligne
    # commençant par un verbe.
    for tache in extraire_taches(texte_brut):

        if tache not in resultat:
            resultat.append(tache)

    return resultat


# ============================================================
# VIP / SIR
# ============================================================

def detecter_vip_sir(texte):
    """Détecte VIP et/ou SIR."""

    if not texte:
        return ""

    texte_min = texte.lower()

    vip = (
        bool(re.search(r"\bvip\b", texte_min))
        or "visite infirmier périodique" in texte_min
        or "visite infirmier periodique" in texte_min
        or "visite d'information et de prévention" in texte_min
        or "visite d information et de prevention" in texte_min
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
# LECTURE DES RUBRIQUES DE FICHE DE POSTE
# ============================================================

RUBRIQUES_FICHE_POSTE = [
    (
        "entreprise",
        [
            r"nom\s+de\s+l['’]entreprise\s*:?"
        ]
    ),
    (
        "intitule",
        [
            r"intitul[ée]\s+du\s+poste\s*:?"
        ]
    ),
    (
        "taches",
        [
            r"liste\s+des\s+t[âa]ches\s+propos[ée]es?\s*:?"
        ]
    ),
    (
        "habilitations",
        [
            r"habilitations,?\s+certificats\s+et\s+dipl[oô]mes\s+obligatoires\s*:?"
        ]
    ),
    (
        "conduite_engins",
        [
            r"conduite\s+d['’]engins\s*:?"
        ]
    ),
    (
        "machines_outils",
        [
            r"utilisation\s+de\s+machines\s*/?\s*outils\s*:?"
        ]
    ),
    (
        "securite_risques",
        [
            r"sécurité\s*:?",
            r"risques\s*:?",
            r"consignes\s+de\s+sécurité\s*:?",
            r"sécurité\s+et\s+risques\s*:?"
        ]
    ),
]


def _capturer_apres_libelle(
    texte_brut,
    motif_libelle
):
    """
    Capture les lignes situées après un libellé jusqu'à
    la prochaine rubrique reconnue.
    """

    correspondance = re.search(
        motif_libelle,
        texte_brut,
        flags=re.IGNORECASE
    )

    if not correspondance:
        return ""

    apres = texte_brut[correspondance.end():]

    lignes_capturees = []

    for ligne in apres.splitlines():

        ligne_nettoyee = ligne.strip()

        if not ligne_nettoyee:
            if lignes_capturees:
                continue
            continue

        est_une_autre_rubrique = any(
            re.match(
                motif,
                ligne_nettoyee,
                flags=re.IGNORECASE
            )
            for _, motifs in RUBRIQUES_FICHE_POSTE
            for motif in motifs
        )

        if est_une_autre_rubrique:
            break

        lignes_capturees.append(ligne_nettoyee)

        if len(lignes_capturees) >= 15:
            break

    return " / ".join(lignes_capturees)


def extraire_sections_poste(texte_brut):
    """Extrait les principales rubriques de la fiche de poste."""

    resultat = {
        cle: ""
        for cle, _ in RUBRIQUES_FICHE_POSTE
    }

    if not texte_brut:
        return resultat

    for cle, motifs in RUBRIQUES_FICHE_POSTE:

        for motif in motifs:

            valeur = _capturer_apres_libelle(
                texte_brut,
                motif
            )

            if valeur:
                resultat[cle] = valeur
                break

    vip_sir = detecter_vip_sir(texte_brut)

    resultat["vip"] = "VIP" in vip_sir
    resultat["sir"] = "SIR" in vip_sir
    resultat["vip_sir"] = vip_sir

    return resultat


def analyser_fiche_poste(texte_brut):
    """
    Analyse une fiche de poste en donnant priorité aux
    rubriques structurées du modèle ID'EES.
    """

    sections = extraire_sections_poste(
        texte_brut
    )

    if not sections.get("intitule"):
        sections["intitule"] = detecter_metier(
            texte_brut
        )

    if not sections.get("taches"):
        sections["taches"] = " / ".join(
            extraire_taches(texte_brut)
        )

    if not sections.get("competences"):
        sections["competences"] = " / ".join(
            extraire_competences_pro(texte_brut)
        )

    sections["taches_par_rubrique"] = (
        extraire_taches_par_lignes(
            texte_brut,
            "Tâches"
        )
    )

    return sections
