"""
Bibliothèque des métiers, compétences, tâches et extraction structurée
Version V10

Objectifs :
- détecter le métier dominant ;
- extraire les compétences sans prendre les intitulés de rubriques ;
- récupérer les tâches ligne par ligne, y compris lorsqu'elles sont placées
  dans une rubrique "Compétences" ;
- extraire les informations structurées d'une fiche de poste ;
- reconnaître précisément les rubriques du modèle de fiche de poste ;
- ne pas confondre les libellés du modèle avec leurs valeurs ;
- récupérer les tâches de la rubrique "Liste des tâches proposées" ;
- fournir une fonction extraire_taches_depuis_texte() utilisée par app.py.
"""

import re
import unicodedata


# ============================================================
# OUTILS DE NORMALISATION
# ============================================================

def _normaliser(texte):
    """
    Normalise un texte pour faciliter les comparaisons :
    - minuscules ;
    - suppression des accents ;
    - espaces multiples supprimés.
    """

    if not texte:
        return ""

    texte = str(texte).lower()

    texte = unicodedata.normalize(
        "NFD",
        texte,
    )

    texte = "".join(
        caractere
        for caractere in texte
        if unicodedata.category(caractere) != "Mn"
    )

    texte = re.sub(
        r"\s+",
        " ",
        texte,
    )

    return texte.strip()


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
        "industriel",
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
        "câblage",
        "cablage",
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
    des mots-clés sur l'ensemble du texte.
    """

    if not texte:
        return "Non détecté"

    texte_min = _normaliser(texte)

    meilleur_metier = "Non détecté"
    meilleur_score = 0

    for metier, mots in METIERS.items():

        score = 0

        for mot in mots:

            mot_normalise = _normaliser(mot)

            if not mot_normalise:
                continue

            score += len(
                re.findall(
                    re.escape(mot_normalise),
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

    Les résultats sont dédupliqués.
    """

    if not texte:
        return []

    texte_normalise = _normaliser(texte)

    resultat = []
    deja_vu = set()

    for competence in COMPETENCES_PRO:

        competence_normalisee = _normaliser(
            competence
        )

        if not competence_normalisee:
            continue

        if competence_normalisee in deja_vu:
            continue

        if competence_normalisee in texte_normalise:

            resultat.append(competence)
            deja_vu.add(competence_normalisee)

    return resultat


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
    Recherche les tâches/missions concrètes mentionnées
    dans le texte.
    """

    if not texte:
        return []

    texte_normalise = _normaliser(texte)

    resultat = []
    deja_vu = set()

    for tache in TACHES:

        tache_normalisee = _normaliser(tache)

        if not tache_normalisee:
            continue

        if tache_normalisee in deja_vu:
            continue

        if tache_normalisee in texte_normalise:

            resultat.append(tache)
            deja_vu.add(tache_normalisee)

    return resultat


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
    "contrôle",

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
    "installation",

    "vérifier",
    "vérifie",
    "vérification",
    "verifier",

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
    "palettisation",
]


def extraire_taches_par_lignes(
    texte_brut,
    rubrique_actuelle="",
):
    """
    Analyse le texte ligne par ligne.

    Une ligne est considérée comme une tâche lorsqu'elle
    commence par un verbe ou une forme de verbe connue.

    Cela permet notamment de récupérer les tâches placées
    dans une rubrique "Compétences".
    """

    if not texte_brut:
        return {}

    taches_par_rubrique = {}

    for ligne in texte_brut.splitlines():

        ligne_nettoyee = ligne.strip()

        if not ligne_nettoyee:
            continue

        # Supprime les puces éventuelles
        ligne_test = re.sub(
            r"^[\s\-•*·▪◦]+",
            "",
            ligne_nettoyee,
        ).strip()

        if not ligne_test:
            continue

        # Les lignes extrêmement longues sont généralement
        # des paragraphes et non des tâches.
        if len(ligne_test) > 180:
            continue

        premier_mot = re.split(
            r"[\s,;:.!?]+",
            ligne_test.lower(),
        )[0]

        premier_mot = premier_mot.strip(
            "-•*·▪◦"
        )

        premier_mot_normalise = _normaliser(
            premier_mot
        )

        verbes_normalises = {
            _normaliser(verbe)
            for verbe in VERBES_ACTION
        }

        if premier_mot_normalise in verbes_normalises:

            if rubrique_actuelle not in taches_par_rubrique:

                taches_par_rubrique[
                    rubrique_actuelle
                ] = []

            valeur = ligne_test.rstrip(
                ".,:;"
            )

            if valeur not in taches_par_rubrique[
                rubrique_actuelle
            ]:

                taches_par_rubrique[
                    rubrique_actuelle
                ].append(valeur)

    return taches_par_rubrique


# ============================================================
# NOUVELLE FONCTION UTILISEE PAR APP.PY
# ============================================================

def extraire_taches_depuis_texte(
    texte_brut,
):
    """
    Retourne une liste unique de tâches détectées
    ligne par ligne.

    Cette fonction est utilisée par app.py.

    Elle récupère les tâches quelle que soit la rubrique
    dans laquelle elles apparaissent, notamment lorsque
    des collègues placent des tâches dans la rubrique
    "Compétences".
    """

    if not texte_brut:
        return []

    resultat = []
    vus = set()

    taches_par_rubrique = extraire_taches_par_lignes(
        texte_brut
    )

    for lignes in taches_par_rubrique.values():

        for ligne in lignes:

            cle = _normaliser(ligne)

            if not cle:
                continue

            if cle in vus:
                continue

            vus.add(cle)
            resultat.append(ligne)

    return resultat


# ============================================================
# VIP / SIR
# ============================================================

def detecter_vip_sir(texte):
    """
    Détecte si le texte mentionne un suivi VIP et/ou SIR.
    """

    if not texte:
        return ""

    texte_min = _normaliser(texte)

    vip = (
        bool(
            re.search(
                r"\bvip\b",
                texte_min,
            )
        )
        or "visite infirmier periodique" in texte_min
        or "visite d information et de prevention" in texte_min
        or "visite d information et de prévention" in texte_min
    )

    sir = (
        bool(
            re.search(
                r"\bsir\b",
                texte_min,
            )
        )
        or "suivi individuel renforce" in texte_min
        or "suivi individuel renforcé" in texte_min
    )

    if vip and sir:
        return "VIP + SIR"

    if vip:
        return "VIP"

    if sir:
        return "SIR"

    return ""


# ============================================================
# RUBRIQUES FICHE DE POSTE
# ============================================================

RUBRIQUES_FICHE_POSTE = [

    (
        "entreprise",
        [
            r"nom\s+de\s+l['’]entreprise\s*:?",
            r"entreprise\s+cliente\s*:?",
            r"nom\s+entreprise\s*:?",
        ],
    ),

    (
        "intitule",
        [
            r"intitul[ée]\s+du\s+poste\s*:?",
            r"intitul[ée]\s*:?",
            r"poste\s*:?",
        ],
    ),

    (
        "taches",
        [
            r"liste\s+des\s+t[âa]ches\s+propos[ée]es?\s*:?",
            r"liste\s+des\s+t[âa]ches\s+[àa]\s+proposer\s*:?",
            r"t[âa]ches\s+[àa]\s+r[ée]aliser\s*:?",
            r"missions\s*:?",
        ],
    ),

    (
        "habilitations",
        [
            r"habilitations,?\s+certificats\s+et\s+dipl[ôo]mes\s+obligatoires\s*:?",
            r"habilitations\s*:?",
            r"certificats\s*:?",
            r"dipl[ôo]mes\s+obligatoires\s*:?",
        ],
    ),

    (
        "conduite_engins",
        [
            r"conduite\s+d['’]engins\s*:?",
        ],
    ),

    (
        "machines_outils",
        [
            r"utilisation\s+de\s+machines\s*/?\s*outils\s*:?",
            r"machines\s*/?\s*outils\s*:?",
        ],
    ),

    (
        "securite_risques",
        [
            r"conditions\s+de\s+travail\s+li[ée]es\s+au\s+poste\s*:?",
            r"s[ée]curit[ée]\s*:?",
            r"risques\s*:?",
            r"consignes\s+de\s+s[ée]curit[ée]\s*:?",
            r"s[ée]curit[ée]\s+et\s+risques\s*:?",
        ],
    ),
]


# ============================================================
# CAPTURE D'UNE RUBRIQUE
# ============================================================

def _capturer_apres_libelle(
    texte_brut,
    motif_libelle,
):
    """
    Cherche un libellé de rubrique et récupère ce qui se trouve
    après celui-ci, jusqu'à la prochaine rubrique reconnue.

    Important :
    on ne considère plus automatiquement la première ligne
    rencontrée comme étant la valeur de la rubrique.
    """

    if not texte_brut:
        return ""

    correspondance = re.search(
        motif_libelle,
        texte_brut,
        flags=re.IGNORECASE,
    )

    if not correspondance:
        return ""

    apres = texte_brut[
        correspondance.end():
    ]

    lignes_capturees = []

    for ligne in apres.splitlines():

        ligne_nettoyee = ligne.strip()

        if not ligne_nettoyee:

            if lignes_capturees:
                break

            continue

        est_une_autre_rubrique = False

        for cle, motifs in RUBRIQUES_FICHE_POSTE:

            for motif in motifs:

                if re.match(
                    r"^\s*" + motif,
                    ligne_nettoyee,
                    flags=re.IGNORECASE,
                ):

                    est_une_autre_rubrique = True
                    break

            if est_une_autre_rubrique:
                break

        if est_une_autre_rubrique:
            break

        lignes_capturees.append(
            ligne_nettoyee
        )

        if len(lignes_capturees) >= 20:
            break

    return " / ".join(
        lignes_capturees
    )


# ============================================================
# EXTRACTION DES SECTIONS DE FICHE DE POSTE
# ============================================================

def extraire_sections_poste(
    texte_brut,
):
    """
    Extrait les informations structurées d'une fiche de poste.

    Les rubriques du modèle sont recherchées explicitement.

    La rubrique "Liste des tâches proposées" est reconnue
    comme priorité pour alimenter le champ "taches".
    """

    resultat = {
        cle: ""
        for cle, _ in RUBRIQUES_FICHE_POSTE
    }

    if not texte_brut:
        resultat["vip"] = False
        resultat["sir"] = False
        return resultat

    # --------------------------------------------------------
    # EXTRACTION RUBRIQUES
    # --------------------------------------------------------

    for cle, motifs in RUBRIQUES_FICHE_POSTE:

        for motif in motifs:

            valeur = _capturer_apres_libelle(
                texte_brut,
                motif,
            )

            if valeur:

                resultat[cle] = valeur
                break

    # --------------------------------------------------------
    # VIP / SIR
    # --------------------------------------------------------

    resultat["vip"] = bool(
        re.search(
            r"\bvip\b|visite\s+d['’]information\s+et\s+de\s+prévention",
            texte_brut,
            flags=re.IGNORECASE,
        )
    )

    resultat["sir"] = bool(
        re.search(
            r"\bsir\b|suivi\s+individuel\s+renforcé",
            texte_brut,
            flags=re.IGNORECASE,
        )
    )

    return resultat


# ============================================================
# ANALYSE COMPLETE D'UNE FICHE DE POSTE
# ============================================================

def analyser_fiche_poste(
    texte_brut,
):
    """
    Analyse une fiche de poste.

    Priorités :

    1. Rubriques structurées du modèle ;
    2. Liste des tâches proposées ;
    3. Détection ligne par ligne des tâches ;
    4. Détection générique en dernier recours.

    Le but est d'éviter de transformer des intitulés de
    rubriques comme "Conditions de travail liées au poste"
    en intitulé réel du poste.
    """

    if not texte_brut:
        return {
            "entreprise": "",
            "intitule": "",
            "taches": "",
            "habilitations": "",
            "conduite_engins": "",
            "machines_outils": "",
            "securite_risques": "",
            "vip": False,
            "sir": False,
            "competences": "",
            "taches_par_rubrique": {},
        }

    sections = extraire_sections_poste(
        texte_brut
    )

    # --------------------------------------------------------
    # TACHES
    # --------------------------------------------------------

    taches_liste = []

    # Priorité absolue à la rubrique "Liste des tâches proposées"
    if sections.get("taches"):

        for morceau in re.split(
            r"\s*/\s*|\n|•|;|\|",
            sections["taches"],
        ):

            morceau = morceau.strip()

            if morceau:
                taches_liste.append(
                    morceau
                )

    # Si la rubrique n'a rien donné, récupération
    # des lignes commençant par un verbe.
    if not taches_liste:

        taches_liste = (
            extraire_taches_depuis_texte(
                texte_brut
            )
        )

    # Dernier recours : mots-clés génériques.
    if not taches_liste:

        taches_liste = extraire_taches(
            texte_brut
        )

    # Déduplication
    taches_finales = []
    taches_vues = set()

    for tache in taches_liste:

        cle = _normaliser(
            tache
        )

        if cle and cle not in taches_vues:

            taches_vues.add(cle)
            taches_finales.append(
                tache
            )

    sections["taches"] = " / ".join(
        taches_finales
    )

    # --------------------------------------------------------
    # COMPETENCES
    # --------------------------------------------------------

    competences = extraire_competences_pro(
        texte_brut
    )

    sections["competences"] = " / ".join(
        competences
    )

    # --------------------------------------------------------
    # METIER
    # --------------------------------------------------------

    sections["metier_detecte"] = detecter_metier(
        texte_brut
    )

    # --------------------------------------------------------
    # TACHES PAR RUBRIQUE
    # --------------------------------------------------------

    sections["taches_par_rubrique"] = (
        extraire_taches_par_lignes(
            texte_brut
        )
    )

    return sections
