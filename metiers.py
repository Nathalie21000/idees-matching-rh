"""
Bibliothèque des métiers, compétences, tâches et extraction structurée
Version V10

Objectifs :
- détecter le métier dominant ;
- extraire les compétences professionnelles réellement présentes ;
- détecter les tâches réalisées dans les CV, y compris dans une rubrique
  "Compétences" lorsque les lignes commencent par des verbes d'action ;
- lire précisément les rubriques de la fiche de poste ;
- reconnaître le libellé exact "Liste des tâches proposées" ;
- ne pas confondre le nom d'une rubrique avec son contenu ;
- éviter de fabriquer des compétences à partir des mots présents dans
  les intitulés du modèle de fiche de poste.
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
        "engins",
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
        "chariot élévateur",
        "chariot elevateur",
        "logistique",
    ],

    "Préparateur de commandes": [
        "préparateur de commandes",
        "preparateur de commandes",
        "préparateur",
        "preparateur",
        "préparation de commandes",
        "preparation de commandes",
        "commande",
        "commandes",
        "scan",
        "scanner",
        "picking",
        "logistique",
    ],

    "Agent de production": [
        "agent de production",
        "production",
        "industrie",
        "industriel",
        "conditionnement",
        "assemblage",
        "fabrication",
        "ligne de production",
    ],

    "Soudeur": [
        "soudeur",
        "soudure",
        "souder",
        "mig",
        "mag",
        "tig",
    ],

    "Électricien": [
        "électricien",
        "electricien",
        "électricité",
        "electricite",
        "habilitation électrique",
        "habilitation electrique",
        "b1",
        "b2",
        "br",
        "bc",
    ],

    "Maçon": [
        "maçon",
        "macon",
        "maçonnerie",
        "maconnerie",
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
        "chauffeur poids lourd",
        "poids lourd",
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
        "employé libre-service",
        "employe libre-service",
        "libre service",
        "libre-service",
        "grande distribution",
        "mise en rayon",
        "caisse",
    ],
}


# ============================================================
# RUBRIQUES DU MODELE DE FICHE DE POSTE
# ============================================================

# IMPORTANT :
# Les intitulés sont ceux utilisés dans le modèle de fiche de poste.
#
# "Liste des tâches proposées" est volontairement écrit exactement
# comme dans le modèle utilisé par l'agence.

LIBELLES_FICHE_POSTE = {
    "entreprise": [
        r"nom\s+de\s+l['’]entreprise",
        r"entreprise\s+cliente",
        r"nom\s+de\s+l['’]entreprise\s+cliente",
    ],

    "intitule": [
        r"intitul[ée]\s+du\s+poste",
        r"intitul[ée]\s+de\s+poste",
    ],

    "taches": [
        r"liste\s+des\s+tâches\s+propos[ée]es",
        r"liste\s+des\s+taches\s+proposees",
        r"liste\s+des\s+tâches\s+à\s+proposer",
        r"liste\s+des\s+taches\s+a\s+proposer",
    ],

    "conditions_travail": [
        r"conditions\s+de\s+travail\s+li[ée]es\s+au\s+poste",
        r"conditions\s+de\s+travail",
    ],

    "habilitations": [
        r"habilitations,?\s+certificats\s+et\s+diplômes\s+obligatoires",
        r"habilitations,?\s+certificats\s+et\s+diplomes\s+obligatoires",
        r"habilitations",
        r"certificats\s+et\s+diplômes",
        r"certificats\s+et\s+diplomes",
    ],

    "conduite_engins": [
        r"conduite\s+d['’]engins",
        r"conduite\s+engins",
    ],

    "machines_outils": [
        r"utilisation\s+de\s+machines\s*/?\s*outils",
        r"machines\s*/?\s*outils",
        r"machines\s+et\s+outils",
    ],

    "securite_risques": [
        r"sécurité\s+et\s+risques",
        r"securite\s+et\s+risques",
        r"consignes\s+de\s+sécurité",
        r"consignes\s+de\s+securite",
        r"risques",
    ],
}


# Toutes les rubriques connues permettent de savoir où une rubrique
# s'arrête et où commence la suivante.

TOUS_LES_LIBELLES = []

for motifs in LIBELLES_FICHE_POSTE.values():
    TOUS_LES_LIBELLES.extend(motifs)


# ============================================================
# DETECTION DU METIER
# ============================================================

def detecter_metier(texte):
    """
    Recherche le métier dominant en comptant les occurrences
    des mots-clés.

    La détection est volontairement effectuée sur l'ensemble du
    texte, mais les intitulés de rubriques ne sont pas considérés
    comme des compétences.
    """

    if not texte:
        return "Non détecté"

    texte_min = texte.lower()

    meilleur_metier = "Non détecté"
    meilleur_score = 0

    for metier, mots in METIERS.items():

        score = 0

        for mot in mots:

            motif = r"(?<!\w)" + re.escape(
                mot.lower()
            ) + r"(?!\w)"

            occurrences = len(
                re.findall(
                    motif,
                    texte_min
                )
            )

            score += occurrences

        if score > meilleur_score:

            meilleur_score = score
            meilleur_metier = metier

    return meilleur_metier


# ============================================================
# COMPETENCES PROFESSIONNELLES
# ============================================================

COMPETENCES_PRO = [
    "préparation de commandes",
    "préparation de commande",
    "conduite d'engins",
    "conduite d'engin",
    "chargement",
    "déchargement",
    "gestion des stocks",
    "gestion de stock",
    "utilisation d'outils",
    "utilisation des outils",
    "travail en équipe",
    "esprit d'équipe",
    "port de charges",
    "port de charge",
    "manutention",
    "contrôle qualité",
    "respect des consignes de sécurité",
    "respect des consignes",
    "polyvalence",
    "autonomie",
    "rigueur",
    "gestion du temps",
    "sens de l'organisation",
    "lecture de plan",
    "lecture de plans",
    "utilisation d'un scanner",
    "utilisation d'un chariot",
    "conduite de ligne",
    "conduite de ligne de production",
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
    Recherche uniquement les compétences professionnelles définies
    dans COMPETENCES_PRO.

    Les intitulés de rubriques ne sont pas ajoutés comme compétences.
    """

    if not texte:
        return []

    texte_min = texte.lower()

    resultats = []

    for competence in COMPETENCES_PRO:

        motif = r"(?<!\w)" + re.escape(
            competence.lower()
        ) + r"(?!\w)"

        if re.search(
            motif,
            texte_min
        ):
            resultats.append(competence)

    return resultats


# ============================================================
# TACHES / MISSIONS CONNUES
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
    Recherche des tâches connues dans le texte.
    """

    if not texte:
        return []

    texte_min = texte.lower()

    resultats = []

    for tache in TACHES:

        motif = r"(?<!\w)" + re.escape(
            tache.lower()
        ) + r"(?!\w)"

        if re.search(
            motif,
            texte_min
        ):
            resultats.append(tache)

    return resultats


# ============================================================
# VERBES D'ACTION
# ============================================================

VERBES_ACTION = [
    "préparer",
    "prépare",
    "prépares",
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
    "gere",
    "gestion",

    "réceptionner",
    "réceptionne",
    "receptionner",
    "réception",
    "reception",

    "expédier",
    "expédie",
    "expedier",
    "expédition",
    "expedition",

    "trier",
    "trie",
    "tri",

    "étiqueter",
    "étiquette",
    "etiqueter",
    "étiquetage",
    "etiquetage",

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
    "cablé",
    "câblage",
    "cablage",

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
    "verification",
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
    "palettisation",

    "conditionner",
    "conditionne",
    "conditionnement",

    "alimenter",
    "alimente",
    "alimentation",

    "réaliser",
    "réalise",
    "realiser",

    "effectuer",
    "effectue",

    "assurer",
    "assure",

    "participer",
    "participe",

    "préparer",
    "prépare",

    "mettre",
    "met",

    "déplacer",
    "déplace",

    "respecter",
    "respecte",

    "appliquer",
    "applique",

    "maintenir",
    "maintient",

    "entretenir",
    "entretient",
]


def _normaliser_premier_mot(ligne):
    """
    Nettoie le début d'une ligne afin de détecter correctement
    les lignes commençant par un verbe d'action.
    """

    ligne = ligne.strip()

    ligne = re.sub(
        r"^[\-\–\—•*·▪◦]+\s*",
        "",
        ligne
    )

    ligne = ligne.strip()

    premier_mot = re.split(
        r"[\s,;:.]+",
        ligne.lower(),
        maxsplit=1
    )[0]

    return premier_mot


def extraire_taches_par_lignes(
    texte_brut,
    rubrique_actuelle=""
):
    """
    Analyse le texte ligne par ligne.

    Une ligne est considérée comme une tâche lorsqu'elle commence
    par un verbe d'action connu.

    Cette méthode permet notamment de récupérer des tâches placées
    sous une rubrique "Compétences" dans un CV.
    """

    if not texte_brut:
        return {}

    taches_par_rubrique = {}

    for ligne in texte_brut.splitlines():

        ligne_nettoyee = ligne.strip()

        if not ligne_nettoyee:
            continue

        if len(ligne_nettoyee) > 180:
            continue

        premier_mot = _normaliser_premier_mot(
            ligne_nettoyee
        )

        if premier_mot in VERBES_ACTION:

            rubrique = (
                rubrique_actuelle
                if rubrique_actuelle
                else "Non précisée"
            )

            if rubrique not in taches_par_rubrique:
                taches_par_rubrique[rubrique] = []

            valeur = ligne_nettoyee.rstrip(
                ".,:;"
            )

            if valeur not in taches_par_rubrique[rubrique]:
                taches_par_rubrique[rubrique].append(
                    valeur
                )

    return taches_par_rubrique


# ============================================================
# EXTRACTION DU CONTENU D'UNE RUBRIQUE
# ============================================================

def _ligne_est_libelle(ligne):
    """
    Indique si une ligne correspond à une rubrique connue.
    """

    ligne = ligne.strip()

    if not ligne:
        return False

    ligne_sans_deux_points = re.sub(
        r"\s*:\s*$",
        "",
        ligne
    ).strip()

    for motif in TOUS_LES_LIBELLES:

        if re.fullmatch(
            motif,
            ligne_sans_deux_points,
            flags=re.IGNORECASE
        ):
            return True

    return False


def _correspondance_libelle(ligne, motifs):
    """
    Vérifie si une ligne correspond à l'un des motifs d'une rubrique.
    """

    ligne = ligne.strip()

    for motif in motifs:

        if re.fullmatch(
            motif,
            re.sub(
                r"\s*:\s*$",
                "",
                ligne
            ).strip(),
            flags=re.IGNORECASE
        ):
            return True

    return False


def _nettoyer_valeur_rubrique(valeur):
    """
    Nettoie le contenu extrait d'une rubrique.
    """

    if not valeur:
        return ""

    lignes = []

    for ligne in valeur.splitlines():

        ligne = ligne.strip()

        if not ligne:
            continue

        ligne = re.sub(
            r"\s+",
            " ",
            ligne
        ).strip()

        if ligne:
            lignes.append(ligne)

    return " / ".join(lignes)


def _capturer_contenu_rubrique(
    texte_brut,
    motifs
):
    """
    Recherche une rubrique puis récupère son contenu.

    Fonctionne lorsque :
    - le libellé est seul sur une ligne ;
    - le libellé est suivi de ":" ;
    - le contenu se trouve sur les lignes suivantes ;
    - le document contient plusieurs rubriques successives.
    """

    if not texte_brut:
        return ""

    lignes = texte_brut.splitlines()

    for index, ligne in enumerate(lignes):

        if not _correspondance_libelle(
            ligne,
            motifs
        ):
            continue

        contenu = []

        # ----------------------------------------------------
        # Cas 1 : une valeur se trouve après ":" sur la même ligne
        # ----------------------------------------------------

        if ":" in ligne:

            partie_apres = ligne.split(
                ":",
                1
            )[1].strip()

            if partie_apres:
                contenu.append(
                    partie_apres
                )

        # ----------------------------------------------------
        # Cas 2 : contenu sur les lignes suivantes
        # ----------------------------------------------------

        for suivante in lignes[index + 1:]:

            suivante = suivante.strip()

            if not suivante:
                # Une ligne vide n'est pas forcément la fin.
                # On continue car les tableaux Word/PDF peuvent
                # générer des séparations.
                continue

            if _ligne_est_libelle(suivante):
                break

            contenu.append(suivante)

        valeur = _nettoyer_valeur_rubrique(
            "\n".join(contenu)
        )

        if valeur:
            return valeur

        # Le libellé a bien été trouvé mais sa valeur est vide.
        return ""

    return ""


# ============================================================
# EXTRACTION SPECIFIQUE DE LA FICHE DE POSTE
# ============================================================

def extraire_sections_poste(texte_brut):
    """
    Extrait les rubriques structurées de la fiche de poste.

    Les intitulés utilisés correspondent au modèle de l'agence.

    En particulier :

        Liste des tâches proposées

    est directement affectée à :

        taches

    afin d'être affichée dans "Tâches à réaliser" dans l'application.
    """

    resultat = {
        "entreprise": "",
        "intitule": "",
        "taches": "",
        "competences": "",
        "habilitations": "",
        "conduite_engins": "",
        "machines_outils": "",
        "conditions_travail": "",
        "securite_risques": "",
        "vip": False,
        "sir": False,
    }

    if not texte_brut:
        return resultat

    # --------------------------------------------------------
    # ENTREPRISE
    # --------------------------------------------------------

    resultat["entreprise"] = _capturer_contenu_rubrique(
        texte_brut,
        LIBELLES_FICHE_POSTE["entreprise"]
    )

    # --------------------------------------------------------
    # INTITULE DU POSTE
    # --------------------------------------------------------

    resultat["intitule"] = _capturer_contenu_rubrique(
        texte_brut,
        LIBELLES_FICHE_POSTE["intitule"]
    )

    # --------------------------------------------------------
    # TACHES
    # --------------------------------------------------------

    resultat["taches"] = _capturer_contenu_rubrique(
        texte_brut,
        LIBELLES_FICHE_POSTE["taches"]
    )

    # --------------------------------------------------------
    # CONDITIONS DE TRAVAIL
    # --------------------------------------------------------

    resultat["conditions_travail"] = (
        _capturer_contenu_rubrique(
            texte_brut,
            LIBELLES_FICHE_POSTE[
                "conditions_travail"
            ]
        )
    )

    # --------------------------------------------------------
    # HABILITATIONS
    # --------------------------------------------------------

    resultat["habilitations"] = (
        _capturer_contenu_rubrique(
            texte_brut,
            LIBELLES_FICHE_POSTE[
                "habilitations"
            ]
        )
    )

    # --------------------------------------------------------
    # CONDUITE D'ENGINS
    # --------------------------------------------------------

    resultat["conduite_engins"] = (
        _capturer_contenu_rubrique(
            texte_brut,
            LIBELLES_FICHE_POSTE[
                "conduite_engins"
            ]
        )
    )

    # --------------------------------------------------------
    # MACHINES / OUTILS
    # --------------------------------------------------------

    resultat["machines_outils"] = (
        _capturer_contenu_rubrique(
            texte_brut,
            LIBELLES_FICHE_POSTE[
                "machines_outils"
            ]
        )
    )

    # --------------------------------------------------------
    # SECURITE / RISQUES
    # --------------------------------------------------------

    resultat["securite_risques"] = (
        _capturer_contenu_rubrique(
            texte_brut,
            LIBELLES_FICHE_POSTE[
                "securite_risques"
            ]
        )
    )

    # --------------------------------------------------------
    # COMPETENCES
    # --------------------------------------------------------
    #
    # Pour éviter les faux positifs, on ne prend PAS toutes les
    # occurrences de mots du document.
    #
    # On recherche uniquement les compétences professionnelles
    # réellement présentes dans le contenu du document.
    #
    # Si la fiche possède une rubrique explicitement intitulée
    # "Compétences", l'application peut utiliser son contenu.
    #

    motifs_competences = [
        r"comp[ée]tences",
        r"comp[ée]tences\s+requises",
        r"comp[ée]tences\s+professionnelles",
    ]

    resultat["competences"] = (
        _capturer_contenu_rubrique(
            texte_brut,
            motifs_competences
        )
    )

    # Si aucune rubrique Compétences n'existe,
    # on ne fabrique PAS une liste artificielle à partir
    # des mots du modèle.
    #
    # Les compétences pourront être complétées dans l'application.

    # --------------------------------------------------------
    # VIP / SIR
    # --------------------------------------------------------

    texte_min = texte_brut.lower()

    resultat["vip"] = bool(
        re.search(
            r"\bvip\b",
            texte_min
        )
        or "visite infirmier périodique" in texte_min
        or "visite infirmier periodique" in texte_min
        or "visite d'information et de prévention" in texte_min
        or "visite d information et de prévention" in texte_min
    )

    resultat["sir"] = bool(
        re.search(
            r"\bsir\b",
            texte_min
        )
        or "suivi individuel renforcé" in texte_min
        or "suivi individuel renforce" in texte_min
    )

    return resultat


# ============================================================
# ANALYSE COMPLETE DE LA FICHE DE POSTE
# ============================================================

def analyser_fiche_poste(texte_brut):
    """
    Analyse une fiche de poste.

    Priorité absolue :
    1. lecture des rubriques du modèle ;
    2. récupération du contenu réel de ces rubriques ;
    3. détection générique uniquement en secours.

    IMPORTANT :
    Le système ne doit jamais remplacer le contenu d'une rubrique
    par le nom d'une autre rubrique.
    """

    sections = extraire_sections_poste(
        texte_brut
    )

    # --------------------------------------------------------
    # METIER
    # --------------------------------------------------------

    if not sections.get("intitule"):

        sections["intitule"] = detecter_metier(
            texte_brut
        )

    # --------------------------------------------------------
    # TACHES
    # --------------------------------------------------------
    #
    # La rubrique "Liste des tâches proposées" est prioritaire.
    #
    # Si elle existe mais est vide, on ne la remplace pas
    # automatiquement par une mauvaise rubrique.
    #

    if not sections.get("taches"):

        taches_connues = extraire_taches(
            texte_brut
        )

        if taches_connues:
            sections["taches"] = " / ".join(
                taches_connues
            )

    # --------------------------------------------------------
    # COMPETENCES
    # --------------------------------------------------------

    if not sections.get("competences"):

        competences_connues = (
            extraire_competences_pro(
                texte_brut
            )
        )

        if competences_connues:
            sections["competences"] = (
                " / ".join(
                    competences_connues
                )
            )

    # --------------------------------------------------------
    # TACHES PAR LIGNES
    # --------------------------------------------------------

    sections["taches_par_rubrique"] = (
        extraire_taches_par_lignes(
            texte_brut
        )
    )

    # --------------------------------------------------------
    # INDICATEURS DE DETECTION
    # --------------------------------------------------------

    sections["rubrique_taches_detectee"] = bool(
        sections.get("taches")
    )

    sections["rubrique_entreprise_detectee"] = bool(
        sections.get("entreprise")
    )

    sections["rubrique_intitule_detectee"] = bool(
        sections.get("intitule")
    )

    return sections


# ============================================================
# VIP / SIR
# ============================================================

def detecter_vip_sir(texte):
    """
    Détecte si le texte mentionne un suivi VIP et/ou SIR.
    """

    if not texte:
        return ""

    texte_min = texte.lower()

    vip = (
        bool(
            re.search(
                r"\bvip\b",
                texte_min
            )
        )
        or "visite infirmier périodique" in texte_min
        or "visite infirmier periodique" in texte_min
        or "visite d'information et de prévention" in texte_min
        or "visite d information et de prévention" in texte_min
    )

    sir = (
        bool(
            re.search(
                r"\bsir\b",
                texte_min
            )
        )
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
