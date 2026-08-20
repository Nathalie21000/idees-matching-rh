import pdfplumber
import docx
import re


# ============================================================
# EXTRACTION DE TEXTE
# PDF + WORD
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou Word (.docx).

    PDF :
    - utilise pdfplumber
    - conserve les retours à la ligne

    DOCX :
    - lit les paragraphes
    - lit également les tableaux
    """

    nom_fichier = getattr(file, "name", "") or ""
    nom_fichier_min = nom_fichier.lower()

    if nom_fichier_min.endswith(".docx"):
        texte = extraire_texte_docx(file)

    elif nom_fichier_min.endswith(".pdf"):
        texte = extraire_texte_pdf(file)

    else:
        texte = ""

    return nettoyer_texte(texte)


# ============================================================
# EXTRACTION PDF
# ============================================================

def extraire_texte_pdf(file):
    """
    Extrait le texte d'un PDF avec pdfplumber.

    Les retours à la ligne sont conservés afin de permettre
    l'analyse précise des rubriques de la fiche de poste.
    """

    morceaux = []

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3
                )

                if texte_page:
                    morceaux.append(texte_page)

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """
    Extrait le texte d'un document Word.

    Les paragraphes et les tableaux sont lus.
    """

    morceaux = []

    try:

        document = docx.Document(file)

        # ----------------------------
        # Paragraphes
        # ----------------------------

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:
                morceaux.append(texte)

        # ----------------------------
        # Tableaux
        # ----------------------------

        for table in document.tables:

            for ligne in table.rows:

                cellules = []

                for cellule in ligne.cells:

                    texte_cellule = cellule.text.strip()

                    if texte_cellule:
                        cellules.append(texte_cellule)

                if cellules:
                    morceaux.append(
                        " | ".join(cellules)
                    )

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# NETTOYAGE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoyage léger.

    IMPORTANT :
    On conserve les retours à la ligne car ils sont essentiels
    pour reconnaître les différentes rubriques de la fiche.
    """

    if not texte:
        return ""

    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")

    texte = texte.replace("\xa0", " ")

    # Espaces multiples sur une même ligne
    texte = re.sub(
        r"[ \t]+",
        " ",
        texte
    )

    # Lignes vides multiples
    texte = re.sub(
        r"\n[ \t]*\n[ \t]*\n+",
        "\n\n",
        texte
    )

    return texte.strip()


# ============================================================
# RUBRIQUES CIBLÉES
# ============================================================

# IMPORTANT :
# On ne cherche volontairement QUE ces trois informations.
#
# Cela évite que l'application invente :
# - une entreprise à partir d'une autre rubrique ;
# - un métier à partir d'un titre quelconque ;
# - des compétences génériques ;
# - des tâches qui ne sont pas réellement dans la rubrique
#   "Liste des tâches proposées".

MOTIF_ENTREPRISE = re.compile(
    r"^\s*nom\s+de\s+l['’]entreprise\s*:?\s*$",
    re.IGNORECASE
)

MOTIF_POSTE = re.compile(
    r"^\s*intitul[ée]\s+du\s+poste\s*:?\s*$",
    re.IGNORECASE
)

MOTIF_TACHES = re.compile(
    r"^\s*liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:?\s*$",
    re.IGNORECASE
)


# ============================================================
# NORMALISATION D'UNE LIGNE POUR LA RECHERCHE
# ============================================================

def _normaliser_ligne(ligne):
    """
    Normalise une ligne uniquement pour faciliter la détection
    des libellés.

    Le texte original est conservé pour les valeurs.
    """

    if not ligne:
        return ""

    ligne = ligne.strip().lower()

    ligne = ligne.replace("’", "'")

    ligne = re.sub(
        r"\s+",
        " ",
        ligne
    )

    return ligne


# ============================================================
# RECONNAISSANCE D'UN LIBELLÉ
# ============================================================

def _est_libelle_entreprise(ligne):
    texte = _normaliser_ligne(ligne)

    return bool(
        re.match(
            r"^nom\s+de\s+l['’]?entreprise\s*:?\s*$",
            texte,
            re.IGNORECASE
        )
    )


def _est_libelle_poste(ligne):
    texte = _normaliser_ligne(ligne)

    return bool(
        re.match(
            r"^intitul[ée]\s+du\s+poste\s*:?\s*$",
            texte,
            re.IGNORECASE
        )
    )


def _est_libelle_taches(ligne):
    texte = _normaliser_ligne(ligne)

    return bool(
        re.match(
            r"^liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:?\s*$",
            texte,
            re.IGNORECASE
        )
    )


def _est_un_libelle_cible(ligne):
    return (
        _est_libelle_entreprise(ligne)
        or _est_libelle_poste(ligne)
        or _est_libelle_taches(ligne)
    )


# ============================================================
# EXTRACTION APRÈS UN LIBELLÉ
# ============================================================

def _extraire_valeur_apres_libelle(
    lignes,
    index_libelle,
    type_information
):
    """
    Récupère la valeur située après un libellé.

    Cas pris en charge :

        Nom de l'entreprise
        ABC INDUSTRIE

    ou :

        Nom de l'entreprise : ABC INDUSTRIE

    Pour les tâches :

        Liste des tâches proposées
        tâche 1
        tâche 2
        tâche 3

    Les trois tâches sont conservées.
    """

    ligne_libelle = lignes[index_libelle].strip()

    # --------------------------------------------------------
    # 1. Valeur éventuellement présente sur la même ligne
    # --------------------------------------------------------

    if type_information == "entreprise":

        valeur = re.sub(
            r"^\s*nom\s+de\s+l['’]?entreprise\s*:?\s*",
            "",
            ligne_libelle,
            flags=re.IGNORECASE
        ).strip()

        if valeur:
            return valeur

    elif type_information == "poste":

        valeur = re.sub(
            r"^\s*intitul[ée]\s+du\s+poste\s*:?\s*",
            "",
            ligne_libelle,
            flags=re.IGNORECASE
        ).strip()

        if valeur:
            return valeur

    elif type_information == "taches":

        valeur = re.sub(
            r"^\s*liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:?\s*",
            "",
            ligne_libelle,
            flags=re.IGNORECASE
        ).strip()

        if valeur:
            return valeur

    # --------------------------------------------------------
    # 2. Valeur(s) sur les lignes suivantes
    # --------------------------------------------------------

    valeurs = []

    for i in range(
        index_libelle + 1,
        len(lignes)
    ):

        ligne = lignes[i].strip()

        if not ligne:
            # Une ligne vide arrête la rubrique uniquement
            # si on a déjà trouvé quelque chose.
            if valeurs:
                break

            continue

        # Une autre rubrique cible arrête la capture.
        if _est_un_libelle_cible(ligne):

            break

        # ----------------------------------------------------
        # ENTREPRISE
        # ----------------------------------------------------

        if type_information == "entreprise":

            valeurs.append(ligne)

            # Une seule valeur suffit.
            break

        # ----------------------------------------------------
        # POSTE
        # ----------------------------------------------------

        elif type_information == "poste":

            valeurs.append(ligne)

            # Une seule valeur suffit.
            break

        # ----------------------------------------------------
        # TÂCHES
        # ----------------------------------------------------

        elif type_information == "taches":

            valeurs.append(ligne)

    # --------------------------------------------------------
    # Résultat
    # --------------------------------------------------------

    if type_information == "taches":

        # Chaque ligne de tâche est conservée.
        #
        # On sépare par des virgules car le matching attend
        # actuellement une chaîne de type :
        #
        # tâche 1, tâche 2, tâche 3

        return ", ".join(
            valeur
            for valeur in valeurs
            if valeur.strip()
        )

    if valeurs:

        return valeurs[0].strip()

    return ""


# ============================================================
# EXTRACTION CIBLÉE DE LA FICHE DE POSTE
# ============================================================

def extraire_fiche_poste_ciblee(texte):
    """
    Extrait UNIQUEMENT :

    1. Nom de l'entreprise
    2. Intitulé du poste
    3. Liste des tâches proposées

    Aucune compétence n'est inventée.
    Aucun métier n'est déduit.
    Aucun intitulé voisin n'est utilisé comme valeur.

    Retourne :

    {
        "entreprise": "...",
        "poste": "...",
        "taches": "...",
        "entreprise_trouvee": True/False,
        "poste_trouve": True/False,
        "taches_trouvees": True/False,
    }
    """

    resultat = {
        "entreprise": "",
        "poste": "",
        "taches": "",
        "entreprise_trouvee": False,
        "poste_trouve": False,
        "taches_trouvees": False,
    }

    if not texte:
        return resultat

    # --------------------------------------------------------
    # Préparation des lignes
    # --------------------------------------------------------

    lignes = texte.split("\n")

    lignes = [
        ligne.strip()
        for ligne in lignes
        if ligne.strip()
    ]

    # --------------------------------------------------------
    # Recherche des trois rubriques
    # --------------------------------------------------------

    index_entreprise = None
    index_poste = None
    index_taches = None

    for index, ligne in enumerate(lignes):

        if index_entreprise is None:
            if _est_libelle_entreprise(ligne):
                index_entreprise = index
                continue

        if index_poste is None:
            if _est_libelle_poste(ligne):
                index_poste = index
                continue

        if index_taches is None:
            if _est_libelle_taches(ligne):
                index_taches = index
                continue

    # --------------------------------------------------------
    # Entreprise
    # --------------------------------------------------------

    if index_entreprise is not None:

        entreprise = _extraire_valeur_apres_libelle(
            lignes,
            index_entreprise,
            "entreprise"
        )

        if entreprise:

            resultat["entreprise"] = entreprise
            resultat["entreprise_trouvee"] = True

    # --------------------------------------------------------
    # Poste
    # --------------------------------------------------------

    if index_poste is not None:

        poste = _extraire_valeur_apres_libelle(
            lignes,
            index_poste,
            "poste"
        )

        if poste:

            resultat["poste"] = poste
            resultat["poste_trouve"] = True

    # --------------------------------------------------------
    # Tâches
    # --------------------------------------------------------

    if index_taches is not None:

        taches = _extraire_valeur_apres_libelle(
            lignes,
            index_taches,
            "taches"
        )

        if taches:

            resultat["taches"] = taches
            resultat["taches_trouvees"] = True

    return resultat


# ============================================================
# GÉNÉRATION DE PRÉSENTATION CANDIDAT
# ============================================================

def generer_presentation(
    candidat,
    metier,
    competences,
    caces,
    permis,
    entreprise,
    agence
):
    """
    Génère une présentation d'un candidat destinée
    à l'entreprise cliente.
    """

    texte = f"""
Objet : Proposition de candidature – {metier}

Bonjour,

Suite à votre recherche, nous avons le plaisir de vous proposer la candidature de {candidat}.

Son profil présente plusieurs atouts :

- Métier : {metier}

- Compétences : {competences}

- CACES : {caces if caces else "Non renseigné"}

- Permis : {permis if permis else "Non renseigné"}

Ce candidat semble correspondre aux critères recherchés pour votre besoin.

Nous restons à votre disposition pour toute information complémentaire ou pour organiser une rencontre.

Cordialement,

ID'EES Intérim
Agence de {agence}
"""

    return texte.strip()
