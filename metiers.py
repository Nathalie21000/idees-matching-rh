"""
Bibliothèque des métiers, compétences, tâches et mots-clés
Version V8 - Modifiée pour répondre aux exigences de Nathalie
"""

import re


# ============================================================
# METIERS (mots-clés utilisés pour détecter le métier dominant)
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
    "Soudeur": ["soudeur", "mig", "mag", "tig", "soudure"],
    "Électricien": [
        "électricien", "electricien", "habilitation", "b1", "b2", "br", "bc"
    ],
    "Maçon": ["maçon", "macon", "coffrage", "béton", "beton", "ferraillage"],
    "Manutentionnaire": [
        "manutentionnaire", "manutention", "port de charges", "port de charge", "colis"
    ],
    "Chauffeur PL / SPL": [
        "chauffeur pl", "chauffeur spl", "permis c", "permis ce", "livraison", "transport routier"
    ],
    "Agent d'entretien": [
        "agent d'entretien", "entretien", "nettoyage", "propreté", "proprete"
    ],
    "Employé libre-service": [
        "libre service", "libre-service", "grande distribution",
        "mise en rayon", "caisse"
    ],
}


def detecter_metier(texte):
    """
    Recherche le métier dominant en comptant les occurrences
    des mots-clés sur l'ensemble du texte.
    """
    texte_min = texte.lower()
    meilleur_metier = "Non détecté"
    meilleur_score = 0

    for metier, mots in METIERS.items():
        score = sum(len(re.findall(re.escape(mot), texte_min)) for mot in mots)
        if score > meilleur_score:
            meilleur_score = score
            meilleur_metier = metier

    return meilleur_metier


# ============================================================
# COMPETENCES PROFESSIONNELLES
# ============================================================

COMPETENCES_PRO = [
    "préparation de commandes", "conduite d'engins", "chargement",
    "déchargement", "gestion des stocks", "gestion de stock",
    "utilisation d'outils", "travail en équipe", "esprit d'équipe",
    "port de charges", "manutention", "contrôle qualité",
    "respect des consignes de sécurité", "polyvalence", "autonomie",
    "rigueur", "gestion du temps", "sens de l'organisation",
    "lecture de plan", "utilisation d'un scanner", "conduite de ligne",
    "montage", "assemblage", "câblage", "soudure", "peinture industrielle",
    "nettoyage industriel", "tri", "emballage", "étiquetage",
    "inventaire", "réception de marchandises", "expédition",
    "supervision d'équipe", "encadrement", "formation de nouveaux salariés",
    "maintenance de premier niveau", "diagnostic de panne",
    "sens du contact", "relation client", "gestion des priorités",
    "réactivité", "adaptabilité"
]


def extraire_competences_pro(texte):
    """Recherche les compétences professionnelles génériques présentes dans le texte."""
    texte_min = texte.lower()
    return [c for c in COMPETENCES_PRO if c in texte_min]


# ============================================================
# TACHES / MISSIONS REALISEES
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
    "accueil client", "picking", "palettisation"
]


def extraire_taches(texte):
    """Recherche les tâches/missions concrètes mentionnées dans le texte."""
    texte_min = texte.lower()
    return [t for t in TACHES if t in texte_min]


# ============================================================
# VERBES D'ACTION POUR DETECTER LES TACHES LIGNE PAR LIGNE
# ============================================================

VERBES_ACTION = [
    "préparer", "prépare", "préparation", "charger", "charge", "chargement",
    "décharger", "décharge", "déchargement", "contrôler", "contrôle", "controle",
    "utiliser", "utilise", "utilisation", "conduire", "conduit", "conduite",
    "assembler", "assemble", "assemblage", "monter", "monte", "montage",
    "souder", "soude", "soudure", "nettoyer", "nettoie", "nettoyage",
    "ranger", "range", "rangement", "gérer", "gère", "gestion",
    "réceptionner", "réceptionne", "réception", "expédier", "expédie", "expédition",
    "trier", "trie", "tri", "étiqueter", "étiquette", "étiquetage",
    "emballer", "emballe", "emballage", "livrer", "livre", "livraison",
    "encadrer", "encadre", "encadrement", "former", "forme", "formation",
    "câbler", "câble", "câblage", "poser", "pose", "couler", "coule", "coulage",
    "coffrer", "coffre", "coffrage", "ferrailler", "ferraille", "ferraillage",
    "terrasser", "terrasse", "terrassement", "encaisser", "encaisse", "encaissement",
    "accueillir", "accueille", "accueil", "manutentionner", "manutentionne", "manutention",
    "approvisionner", "approvisionne", "approvisionnement", "installer", "installe",
    "vérifier", "vérifie", "vérification", "surveiller", "surveille", "surveillance",
    "inspecter", "inspecte", "inspection", "manipuler", "manipule", "manipulation",
    "fabriquer", "fabrique", "fabrication", "produire", "produit", "production",
    "peindre", "peint", "peinture", "picker", "pick", "palettiser", "palettise"
]


def extraire_taches_par_lignes(texte_brut, rubrique_actuelle=""):
    """
    Analyse le texte ligne par ligne et détecte les tâches commençant par un verbe d'action.
    **Nouveauté** : Conserve l'origine (rubrique) des tâches détectées.
    
    Args:
        texte_brut (str): Texte brut avec retours à la ligne.
        rubrique_actuelle (str): Rubrique en cours (ex: "Compétences", "Tâches").
    
    Returns:
        dict: Dictionnaire avec les tâches classées par rubrique.
    """
    if not texte_brut:
        return {}

    taches_par_rubrique = {}

    for ligne in texte_brut.split("\n"):
        ligne_nettoyee = ligne.strip()
        if not ligne_nettoyee:
            continue

        # Ignorer les lignes trop longues
        if len(ligne_nettoyee) > 120:
            continue

        premier_mot = re.split(r"[\s,;:.]+", ligne_nettoyee.lower())[0]
        premier_mot = premier_mot.lstrip("-•*·").strip()

        if premier_mot in VERBES_ACTION:
            if rubrique_actuelle not in taches_par_rubrique:
                taches_par_rubrique[rubrique_actuelle] = []
            taches_par_rubrique[rubrique_actuelle].append(ligne_nettoyee.rstrip(".,:;"))

    return taches_par_rubrique


# ============================================================
# SUIVI MEDICAL VIP / SIR
# ============================================================

def detecter_vip_sir(texte):
    """Détecte si le texte mentionne un suivi VIP et/ou SIR."""
    texte_min = texte.lower()
    vip = (
        bool(re.search(r"\bvip\b", texte_min))
        or "visite infirmier périodique" in texte_min
        or "visite infirmier periodique" in texte_min
        or "visite d'information et de prévention" in texte_min
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
# LECTURE "PAR ZONES" DE LA FICHE DE POSTE
# ============================================================

RUBRIQUES_FICHE_POSTE = [
    ("entreprise", [r"nom\s+de\s+l['’]entreprise\s*:?"]),
    ("intitule", [r"intitulé\s+du\s+poste\s*:?"]),
    ("taches", [r"liste\s+des\s+tâches\s+propos[ée]es\s*:?"]),
    ("habilitations", [
        r"habilitations,?\s+certificats\s+et\s+diplômes\s+obligatoires\s*:?"
    ]),
    ("conduite_engins", [r"conduite\s+d['’]engins\s*:?"]),
    ("machines_outils", [r"utilisation\s+de\s+machines\s*/?\s*outils\s*:?"]),
    # Nouvelle rubrique pour les informations de sécurité/risques
    ("securite_risques", [
        r"sécurité\s*:?",
        r"risques\s*:?",
        r"consignes\s+de\s+sécurité\s*:?",
        r"sécurité\s+et\s+risques\s*:?"
    ])
]


def _capturer_apres_libelle(texte_brut, motif_libelle):
    """Cherche un libellé et renvoie le texte qui suit jusqu'à la prochaine ligne vide ou rubrique."""
    correspondance = re.search(motif_libelle, texte_brut, flags=re.IGNORECASE)
    if not correspondance:
        return ""

    apres = texte_brut[correspondance.end():]
    lignes_capturees = []

    for ligne in apres.split("\n"):
        ligne_nettoyee = ligne.strip()
        if not ligne_nettoyee:
            if lignes_capturees:
                break
            continue

        # Vérifier si la ligne correspond à une autre rubrique
        est_une_autre_rubrique = any(
            re.match(motif, ligne_nettoyee, flags=re.IGNORECASE)
            for _, motifs in RUBRIQUES_FICHE_POSTE
            for motif in motifs
        )

        if est_une_autre_rubrique:
            break

        lignes_capturees.append(ligne_nettoyee)
        if len(lignes_capturees) >= 5:
            break

    return " / ".join(lignes_capturees)


def extraire_sections_poste(texte_brut):
    """
    Extrait les informations de la fiche de poste en s'appuyant sur les rubriques structurées.
    **Nouveauté** : Inclut la rubrique "sécurité_risques".
    """
    resultat = {cle: "" for cle, _ in RUBRIQUES_FICHE_POSTE}

    if not texte_brut:
        return resultat

    for cle, motifs in RUBRIQUES_FICHE_POSTE:
        for motif in motifs:
            resultat[cle] = _capturer_apres_libelle(texte_brut, motif)
            if resultat[cle]:
                break

    # Détection VIP/SIR
    resultat["vip"] = bool(
        re.search(
            r"\bvip\b|visite\s+d['’]information\s+et\s+de\s+prévention",
            texte_brut,
            flags=re.IGNORECASE,
        )
    )
    resultat["sir"] = bool(
        re.search(
            r"\bsir\b|suivi\s+individuel\s+renforc[ée]",
            texte_brut,
            flags=re.IGNORECASE,
        )
    )

    return resultat


def analyser_fiche_poste(texte_brut):
    """
    **Nouvelle fonction** : Analyse une fiche de poste en combinant :
    1. Extraction des rubriques structurées (priorité).
    2. Repli sur les méthodes génériques si une rubrique n'est pas trouvée.
    
    Args:
        texte_brut (str): Texte brut de la fiche de poste.
    
    Returns:
        dict: Dictionnaire complet avec toutes les informations extraites.
    """
    # 1. Extraire les sections structurées
    sections = extraire_sections_poste(texte_brut)

    # 2. Repli sur les méthodes génériques si nécessaire
    if not sections.get("intitule"):
        sections["intitule"] = detecter_metier(texte_brut)

    if not sections.get("taches"):
        sections["taches"] = " / ".join(extraire_taches(texte_brut))

    if not sections.get("competences"):
        sections["competences"] = " / ".join(extraire_competences_pro(texte_brut))

    # 3. Extraire les tâches par lignes (avec leur origine)
    # On simule une détection des rubriques pour l'exemple
    # (en pratique, il faudrait parser le texte pour identifier les rubriques)
    taches_par_rubrique = extraire_taches_par_lignes(texte_brut)
    sections["taches_par_rubrique"] = taches_par_rubrique

    return sections
