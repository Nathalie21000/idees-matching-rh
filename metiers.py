"""
Bibliothèque des métiers, compétences, tâches et extraction structurée
Version V9

Objectifs :
- détecter le métier dominant ;
- extraire les compétences sans prendre les intitulés de rubriques ;
- récupérer les tâches ligne par ligne, y compris lorsqu'elles sont placées
  dans une rubrique "Compétences" ;
- extraire les informations structurées d'une fiche de poste ;
- ne pas confondre les libellés du modèle avec leurs valeurs.
"""

import re
import unicodedata


# ============================================================
# METIERS
# ============================================================

METIERS = {
    "Ouvrier VRD": [
        "vrd", "voirie", "réseaux", "reseaux", "terrassement",
        "bordures", "canalisations", "assainissement", "enrobé", "enrobe"
    ],
    "Conducteur d'engins": [
        "conducteur d'engins", "engin", "mini pelle", "minipelle", "pelle",
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
    "Soudeur": ["soudeur", "mig", "mag", "tig", "soudure"],
    "Électricien": [
        "électricien", "electricien", "habilitation", "b1", "b2", "br", "bc"
    ],
    "Maçon": ["maçon", "macon", "coffrage", "béton", "beton", "ferraillage"],
    "Manutentionnaire": [
        "manutentionnaire", "manutention", "port de charges",
        "port de charge", "colis"
    ],
    "Chauffeur PL / SPL": [
        "chauffeur pl", "chauffeur spl", "permis c", "permis ce",
        "livraison", "transport routier"
    ],
    "Agent d'entretien": [
        "agent d'entretien", "entretien", "nettoyage", "propreté", "proprete"
    ],
    "Employé libre-service": [
        "libre service", "libre-service", "grande distribution",
        "mise en rayon", "caisse"
    ],
}


def _sans_accents(texte):
    texte = texte or ""
    return "".join(
        c for c in unicodedata.normalize("NFD", texte)
        if unicodedata.category(c) != "Mn"
    )


def _normaliser(texte):
    return re.sub(r"\s+", " ", _sans_accents(texte).lower()).strip()


def detecter_metier(texte):
    """Recherche le métier dominant dans le texte."""
    texte_min = _normaliser(texte)

    meilleur_metier = "Non détecté"
    meilleur_score = 0

    for metier, mots in METIERS.items():
        score = 0
        for mot in mots:
            mot_norm = _normaliser(mot)
            if mot_norm:
                score += len(re.findall(
                    rf"(?<!\w){re.escape(mot_norm)}(?!\w)",
                    texte_min
                ))

        if score > meilleur_score:
            meilleur_score = score
            meilleur_metier = metier

    return meilleur_metier


# ============================================================
# COMPETENCES
# ============================================================

COMPETENCES_PRO = [
    "préparation de commandes", "conduite d'engins", "chargement",
    "déchargement", "gestion des stocks", "gestion de stock",
    "utilisation d'outils", "travail en équipe", "esprit d'équipe",
    "port de charges", "manutention", "contrôle qualité",
    "respect des consignes de sécurité", "polyvalence", "autonomie",
    "rigueur", "gestion du temps", "sens de l'organisation",
    "lecture de plan", "lecture de plans", "utilisation d'un scanner",
    "conduite de ligne", "montage", "assemblage", "câblage", "soudure",
    "peinture industrielle", "nettoyage industriel", "tri", "emballage",
    "étiquetage", "inventaire", "réception de marchandises", "expédition",
    "supervision d'équipe", "encadrement",
    "formation de nouveaux salariés", "maintenance de premier niveau",
    "diagnostic de panne", "sens du contact", "relation client",
    "gestion des priorités", "réactivité", "adaptabilité",
]


def extraire_competences_pro(texte):
    """Recherche uniquement les compétences explicites dans le texte fourni."""
    texte_min = _normaliser(texte)
    resultats = []

    for competence in COMPETENCES_PRO:
        if _normaliser(competence) in texte_min:
            resultats.append(competence)

    return resultats


# ============================================================
# TACHES
# ============================================================

TACHES = [
    "préparation des commandes", "préparation de commandes",
    "chargement des camions", "déchargement des camions",
    "réception des marchandises", "expédition des marchandises",
    "conduite d'un chariot", "conduite de chariot",
    "conduite d'engins", "conduite de ligne de production",
    "approvisionnement des lignes", "contrôle qualité des produits",
    "emballage des produits", "étiquetage des produits",
    "inventaire du stock", "gestion des stocks",
    "rangement de l'entrepôt", "nettoyage du poste de travail",
    "montage de pièces", "assemblage de pièces", "câblage électrique",
    "soudure de pièces", "maintenance des équipements",
    "livraison de marchandises", "tri des colis", "utilisation d'un scanner",
    "encadrement d'équipe", "formation de nouveaux salariés",
    "lecture de plans", "pose de bordures", "terrassement",
    "pose de canalisations", "coffrage", "ferraillage",
    "coulage de béton", "mise en rayon", "encaissement",
    "accueil client", "picking", "palettisation",
]


def extraire_taches(texte):
    """Recherche des tâches connues dans le texte."""
    texte_min = _normaliser(texte)
    return [
        t for t in TACHES
        if _normaliser(t) in texte_min
    ]


# ============================================================
# VERBES D'ACTION
# ============================================================

VERBES_ACTION = {
    "préparer", "prépare", "préparez", "préparation",
    "charger", "charge", "chargez", "chargement",
    "décharger", "décharge", "déchargez", "déchargement",
    "contrôler", "contrôle", "contrôlez", "controle", "contrôle",
    "utiliser", "utilise", "utilisez", "utilisation",
    "conduire", "conduit", "conduisez", "conduite",
    "assembler", "assemble", "assemblez", "assemblage",
    "monter", "monte", "montez", "montage",
    "souder", "soude", "soudez", "soudure",
    "nettoyer", "nettoie", "nettoyez", "nettoyage",
    "ranger", "range", "rangez", "rangement",
    "gérer", "gère", "gérez", "gere", "gestion",
    "réceptionner", "réceptionne", "réceptionnez", "réception",
    "expédier", "expédie", "expédiez", "expédition",
    "trier", "trie", "triez", "tri",
    "étiqueter", "étiquette", "étiquetez", "étiquetage",
    "emballer", "emballe", "emballez", "emballage",
    "livrer", "livre", "livrez", "livraison",
    "encadrer", "encadre", "encadrez", "encadrement",
    "former", "forme", "formez", "formation",
    "câbler", "câble", "câblez", "cablage", "câblage",
    "poser", "pose", "posez",
    "couler", "coule", "coulez", "coulage",
    "coffrer", "coffre", "coffrez", "coffrage",
    "ferrailler", "ferraille", "ferraillez", "ferraillage",
    "terrasser", "terrasse", "terrassez", "terrassement",
    "encaisser", "encaisse", "encaissez", "encaissement",
    "accueillir", "accueille", "accueillez", "accueil",
    "manutentionner", "manutentionne", "manutentionnez", "manutention",
    "approvisionner", "approvisionne", "approvisionnez",
    "approvisionnement",
    "installer", "installe", "installez",
    "vérifier", "vérifie", "vérifiez", "verification", "vérification",
    "surveiller", "surveille", "surveillez", "surveillance",
    "inspecter", "inspecte", "inspectez", "inspection",
    "manipuler", "manipule", "manipulez", "manipulation",
    "fabriquer", "fabrique", "fabriquez", "fabrication",
    "produire", "produit", "produisez", "production",
    "peindre", "peint", "peignez", "peinture",
    "picker", "pick", "pickez",
    "palettiser", "palettise", "palettisez", "palettisation",
}


def _premier_mot(ligne):
    propre = ligne.strip()
    propre = re.sub(r"^[\s\-•*·▪◦●○]+", "", propre)
    propre = re.sub(r"^[0-9]+[\s.)-]+", "", propre)
    morceau = re.split(r"[\s,;:.!?/]+", propre.lower(), maxsplit=1)[0]
    return morceau.strip()


def ligne_commence_par_verbe_action(ligne):
    premier = _premier_mot(ligne)
    if not premier:
        return False
    return _normaliser(premier) in {
        _normaliser(v) for v in VERBES_ACTION
    }


def extraire_taches_par_lignes(texte_brut, rubrique_actuelle=""):
    """
    Récupère les lignes qui commencent par un verbe/mot d'action.
    La rubrique d'origine n'est pas utilisée pour exclure une tâche :
    une tâche placée sous "Compétences" reste donc détectée.
    """
    resultat = {}

    if not texte_brut:
        return resultat

    for ligne in texte_brut.splitlines():
        ligne = ligne.strip()
        if not ligne or len(ligne) > 180:
            continue

        if ligne_commence_par_verbe_action(ligne):
            resultat.setdefault(rubrique_actuelle or "Document", []).append(
                ligne.rstrip(".,:;")
            )

    return resultat


def extraire_taches_depuis_texte(texte_brut):
    """Retourne une liste unique de tâches détectées ligne par ligne."""
    resultat = []
    vus = set()

    for lignes in extraire_taches_par_lignes(texte_brut).values():
        for ligne in lignes:
            cle = _normaliser(ligne)
            if cle not in vus:
                vus.add(cle)
                resultat.append(ligne)

    return resultat


# ============================================================
# VIP / SIR
# ============================================================

def detecter_vip_sir(texte):
    texte_min = _normaliser(texte)

    vip = (
        bool(re.search(r"\bvip\b", texte_min))
        or "visite infirmier periodique" in texte_min
        or "visite d information et de prevention" in texte_min
    )

    sir = (
        bool(re.search(r"\bsir\b", texte_min))
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
# RUBRIQUES DE FICHE DE POSTE
# ============================================================

RUBRIQUES_FICHE_POSTE = {
    "entreprise": [
        "nom de l'entreprise",
        "nom de l’entreprise",
        "entreprise cliente",
        "nom entreprise",
    ],
    "intitule": [
        "intitulé du poste",
        "intitule du poste",
    ],
    "taches": [
        "liste des tâches à proposer",
        "liste des taches a proposer",
        "liste des tâches proposées",
        "liste des taches proposees",
        "tâches à proposer",
        "taches a proposer",
    ],
    "habilitations": [
        "habilitations, certificats et diplômes obligatoires",
        "habilitations certificats et diplômes obligatoires",
        "habilitations, certificats et diplomes obligatoires",
        "habilitations",
    ],
    "conduite_engins": [
        "conduite d'engins",
        "conduite d engins",
    ],
    "machines_outils": [
        "utilisation de machines / outils",
        "utilisation de machines/outils",
        "utilisation de machines",
        "utilisation d'outils",
    ],
    "securite_risques": [
        "sécurité et risques",
        "securite et risques",
        "conditions de travail liées au poste",
        "conditions de travail liees au poste",
        "sécurité",
        "securite",
        "risques",
    ],
}


def _ligne_est_libelle(ligne):
    n = _normaliser(ligne).rstrip(" :")
    for motifs in RUBRIQUES_FICHE_POSTE.values():
        for motif in motifs:
            if n == _normaliser(motif).rstrip(" :"):
                return True
    return False


def _trouver_ligne_libelle(lignes, motifs):
    motifs_n = [_normaliser(m).rstrip(" :") for m in motifs]

    for i, ligne in enumerate(lignes):
        n = _normaliser(ligne).rstrip(" :")
        for motif in motifs_n:
            if n == motif:
                return i
            # Autorise un libellé suivi de ":" et d'une valeur sur la même ligne.
            if n.startswith(motif + " :") or n.startswith(motif + ":"):
                return i

    return None


def _valeur_sur_meme_ligne(ligne, motifs):
    original = ligne.strip()
    n = _normaliser(original)

    for motif in motifs:
        motif_n = _normaliser(motif)
        if n.startswith(motif_n + ":") or n.startswith(motif_n + " :"):
            # On coupe sur le premier ":" de la ligne originale.
            if ":" in original:
                valeur = original.split(":", 1)[1].strip()
                if valeur:
                    return valeur

    return ""


def extraire_sections_poste(texte_brut):
    """
    Extraction structurée à partir des libellés du modèle de fiche.
    Cette fonction conserve les retours à la ligne et ne mélange pas
    les rubriques entre elles.
    """
    resultat = {
        "entreprise": "",
        "intitule": "",
        "taches": "",
        "habilitations": "",
        "conduite_engins": "",
        "machines_outils": "",
        "securite_risques": "",
        "competences": "",
        "vip": False,
        "sir": False,
        "vip_sir": "",
        "taches_par_rubrique": {},
    }

    if not texte_brut:
        return resultat

    lignes = [l.strip() for l in texte_brut.splitlines() if l.strip()]

    for cle, motifs in RUBRIQUES_FICHE_POSTE.items():
        index = _trouver_ligne_libelle(lignes, motifs)

        if index is None:
            continue

        valeur = _valeur_sur_meme_ligne(lignes[index], motifs)

        if valeur:
            resultat[cle] = valeur
            continue

        valeurs = []
        for ligne in lignes[index + 1:]:
            if _ligne_est_libelle(ligne):
                break

            # Ne récupère pas des morceaux manifestement génériques de formulaire.
            if ligne.strip():
                valeurs.append(ligne.strip())

            # Une rubrique structurée n'a normalement pas besoin de dizaines de lignes.
            if len(valeurs) >= 12:
                break

        resultat[cle] = "\n".join(valeurs)

    # VIP/SIR sur l'ensemble du document : ce champ est indépendant des autres zones.
    resultat["vip_sir"] = detecter_vip_sir(texte_brut)
    resultat["vip"] = resultat["vip_sir"] in {"VIP", "VIP + SIR"}
    resultat["sir"] = resultat["vip_sir"] in {"SIR", "VIP + SIR"}

    # Les tâches doivent venir en priorité de la zone dédiée.
    if resultat["taches"]:
        resultat["taches_par_rubrique"] = {
            "Liste des tâches à proposer": [
                l for l in resultat["taches"].splitlines() if l.strip()
            ]
        }

    return resultat


def analyser_fiche_poste(texte_brut):
    """
    Analyse complète avec priorité aux rubriques du modèle.
    Les replis génériques ne remplacent pas une rubrique trouvée.
    """
    sections = extraire_sections_poste(texte_brut)

    if not sections["intitule"]:
        sections["intitule"] = detecter_metier(texte_brut)

    # IMPORTANT : on ne fabrique plus les compétences de la fiche à partir
    # des mots trouvés dans tous les intitulés du document.
    # Elles sont laissées vides si aucune zone dédiée n'est exploitable.
    if not sections["competences"]:
        sections["competences"] = ""

    return sections
