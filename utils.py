import pdfplumber
import docx
import re
import pytesseract


# ============================================================
# EXTRACTION DE TEXTE
# PDF + WORD + OCR PDF SCANNÉ
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou Word (.docx).

    PDF :
    - utilise d'abord pdfplumber ;
    - si aucune texte n'est trouvé sur une page,
      utilise Tesseract OCR.

    DOCX :
    - lit les paragraphes ;
    - lit également les tableaux.
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
    Extrait le texte d'un PDF.

    1. Tentative classique avec pdfplumber.
    2. Si une page ne contient aucun texte,
       utilisation de Tesseract OCR.
    """

    morceaux = []

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                # ------------------------------------------------
                # 1. EXTRACTION CLASSIQUE
                # ------------------------------------------------

                texte_page = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3
                )

                if texte_page and texte_page.strip():

                    morceaux.append(texte_page)

                    continue

                # ------------------------------------------------
                # 2. OCR SI AUCUN TEXTE
                # ------------------------------------------------

                texte_ocr = extraire_page_avec_ocr(page)

                if texte_ocr:

                    morceaux.append(texte_ocr)

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# OCR D'UNE PAGE PDF
# ============================================================

def extraire_page_avec_ocr(page):
    """
    Convertit une page PDF en image puis utilise Tesseract
    avec le modèle français.
    """

    try:

        image_page = page.to_image(
            resolution=300
        ).original

        texte = pytesseract.image_to_string(
            image_page,
            lang="fra",
            config="--psm 6"
        )

        return texte or ""

    except Exception:
        return ""


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """
    Extrait le texte d'un document Word .docx.

    Les paragraphes et les tableaux sont lus.
    """

    morceaux = []

    try:

        document = docx.Document(file)

        # ------------------------------------------------
        # Paragraphes
        # ------------------------------------------------

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:
                morceaux.append(texte)

        # ------------------------------------------------
        # Tableaux
        # ------------------------------------------------

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

    Les retours à la ligne sont conservés car ils sont
    importants pour reconnaître les différentes rubriques.
    """

    if not texte:
        return ""

    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")

    texte = texte.replace("\xa0", " ")

    texte = re.sub(
        r"[ \t]+",
        " ",
        texte
    )

    texte = re.sub(
        r"\n[ \t]*\n[ \t]*\n+",
        "\n\n",
        texte
    )

    return texte.strip()


# ============================================================
# RUBRIQUES CIBLÉES
# ============================================================

MOTIF_ENTREPRISE = re.compile(
    r"^\s*nom\s+de\s+l['’]?entreprise\s*:?\s*$",
    re.IGNORECASE
)

MOTIF_POSTE = re.compile(
    r"^\s*intitul[ée]?\s+du\s+poste\s*:?\s*$",
    re.IGNORECASE
)

MOTIF_TACHES = re.compile(
    r"^\s*liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:?\s*$",
    re.IGNORECASE
)


# ============================================================
# NORMALISATION D'UNE LIGNE POUR L'OCR
# ============================================================

def _normaliser_ligne(ligne):
    """
    Normalise une ligne uniquement pour permettre
    la reconnaissance des libellés.

    Les petits caractères parasites produits par OCR
    en début de ligne sont supprimés.

    Exemple :

        | Nom de l'entreprise :

    devient :

        nom de l'entreprise :
    """

    if not ligne:
        return ""

    ligne = ligne.strip().lower()

    ligne = ligne.replace("’", "'")

    # Suppression des caractères parasites fréquents
    # avant un libellé OCR.
    ligne = re.sub(
        r"^[|¦Il1\[\]{}()<>]+[\s]*",
        "",
        ligne
    )

    ligne = re.sub(
        r"\s+",
        " ",
        ligne
    )

    return ligne.strip()


# ============================================================
# RECONNAISSANCE DU LIBELLÉ ENTREPRISE
# ============================================================

def _est_libelle_entreprise(ligne):

    texte = _normaliser_ligne(ligne)

    return bool(
        re.match(
            r"^nom\s+de\s+l['’]?entreprise\s*:?.*$",
            texte,
            re.IGNORECASE
        )
    )


# ============================================================
# RECONNAISSANCE DU LIBELLÉ POSTE
# ============================================================

def _est_libelle_poste(ligne):

    texte = _normaliser_ligne(ligne)

    return bool(
        re.match(
            r"^intitul[ée]?\s+du\s+poste\s*:?.*$",
            texte,
            re.IGNORECASE
        )
    )


# ============================================================
# RECONNAISSANCE DU LIBELLÉ TÂCHES
# ============================================================

def _est_libelle_taches(ligne):

    texte = _normaliser_ligne(ligne)

    return bool(
        re.match(
            r"^liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:?.*$",
            texte,
            re.IGNORECASE
        )
    )


# ============================================================
# LIBELLÉ CIBLE
# ============================================================

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

    Exemple :

        Nom de l'entreprise :
        COLAS

    ou :

        Nom de l'entreprise : COLAS

    Pour les tâches, toutes les lignes suivantes
    sont conservées jusqu'à la prochaine rubrique cible.
    """

    ligne_libelle = lignes[index_libelle].strip()

    # ========================================================
    # VALEUR SUR LA MÊME LIGNE
    # ========================================================

    if type_information == "entreprise":

        valeur = re.sub(
            r"^\s*[|¦Il1\[\]{}()<>]*\s*"
            r"nom\s+de\s+l['’]?entreprise\s*:?\s*",
            "",
            ligne_libelle,
            flags=re.IGNORECASE
        ).strip()

        if valeur:
            return valeur

    elif type_information == "poste":

        valeur = re.sub(
            r"^\s*[|¦Il1\[\]{}()<>]*\s*"
            r"intitul[ée]?\s+du\s+poste\s*:?\s*",
            "",
            ligne_libelle,
            flags=re.IGNORECASE
        ).strip()

        if valeur:
            return valeur

    elif type_information == "taches":

        valeur = re.sub(
            r"^\s*[|¦Il1\[\]{}()<>]*\s*"
            r"liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:?\s*",
            "",
            ligne_libelle,
            flags=re.IGNORECASE
        ).strip()

        if valeur:
            return valeur

    # ========================================================
    # VALEUR(S) SUR LES LIGNES SUIVANTES
    # ========================================================

    valeurs = []

    for i in range(
        index_libelle + 1,
        len(lignes)
    ):

        ligne = lignes[i].strip()

        # ----------------------------------------------------
        # Ligne vide
        # ----------------------------------------------------

        if not ligne:

            if valeurs:
                break

            continue

        # ----------------------------------------------------
        # Nouvelle rubrique cible
        # ----------------------------------------------------

        if _est_un_libelle_cible(ligne):

            break

        # ----------------------------------------------------
        # ENTREPRISE
        # ----------------------------------------------------

        if type_information == "entreprise":

            valeurs.append(ligne)

            break

        # ----------------------------------------------------
        # POSTE
        # ----------------------------------------------------

        elif type_information == "poste":

            valeurs.append(ligne)

            break

        # ----------------------------------------------------
        # TÂCHES
        # ----------------------------------------------------

        elif type_information == "taches":

            valeurs.append(ligne)

    # ========================================================
    # RÉSULTAT
    # ========================================================

    if type_information == "taches":

        return ", ".join(
            valeur.strip()
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

    Aucun métier n'est déduit.
    Aucune compétence n'est inventée.
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

    # ========================================================
    # PRÉPARATION DES LIGNES
    # ========================================================

    lignes = texte.split("\n")

    lignes = [
        ligne.strip()
        for ligne in lignes
        if ligne.strip()
    ]

    # ========================================================
    # RECHERCHE DES TROIS RUBRIQUES
    # ========================================================

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

    # ========================================================
    # ENTREPRISE
    # ========================================================

    if index_entreprise is not None:

        entreprise = _extraire_valeur_apres_libelle(
            lignes,
            index_entreprise,
            "entreprise"
        )

        if entreprise:

            resultat["entreprise"] = entreprise
            resultat["entreprise_trouvee"] = True

    # ========================================================
    # POSTE
    # ========================================================

    if index_poste is not None:

        poste = _extraire_valeur_apres_libelle(
            lignes,
            index_poste,
            "poste"
        )

        if poste:

            resultat["poste"] = poste
            resultat["poste_trouve"] = True

    # ========================================================
    # TÂCHES
    # ========================================================

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
