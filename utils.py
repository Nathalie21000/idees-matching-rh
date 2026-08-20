import pdfplumber
import docx
import re


# ============================================================
# EXTRACTION DE TEXTE (PDF + WORD)
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF (.pdf) ou Word (.docx).

    IMPORTANT :
    On conserve les retours à la ligne afin de permettre
    l'analyse structurée des fiches de poste.
    """

    nom_fichier = getattr(file, "name", "") or ""
    nom_fichier_min = nom_fichier.lower()

    if nom_fichier_min.endswith(".docx"):
        texte = extraire_texte_docx(file)

    else:
        texte = extraire_texte_pdf(file)

    return nettoyer_texte(texte)


# ============================================================
# EXTRACTION PDF
# ============================================================

def extraire_texte_pdf(file):
    """
    Extrait le texte d'un PDF en conservant les lignes.
    """

    morceaux = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            texte_page = page.extract_text(
                x_tolerance=2,
                y_tolerance=3
            )

            if texte_page:
                morceaux.append(texte_page)

    return "\n".join(morceaux)


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """
    Extrait le contenu d'un document Word.

    Les paragraphes et les tableaux sont conservés avec
    leurs retours à la ligne.

    C'est particulièrement important pour les fiches
    de poste qui utilisent des tableaux.
    """

    document = docx.Document(file)

    morceaux = []

    # --------------------------------------------------------
    # PARAGRAPHES
    # --------------------------------------------------------

    for paragraphe in document.paragraphs:

        texte = paragraphe.text.strip()

        if texte:
            morceaux.append(texte)

    # --------------------------------------------------------
    # TABLEAUX
    # --------------------------------------------------------

    for table in document.tables:

        for ligne in table.rows:

            cellules = []

            for cellule in ligne.cells:

                texte_cellule = cellule.text.strip()

                if texte_cellule:
                    cellules.append(texte_cellule)

            if cellules:
                morceaux.append(
                    "\n".join(cellules)
                )

    return "\n".join(morceaux)


# ============================================================
# NETTOYAGE DU TEXTE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoie le texte sans supprimer les retours à la ligne.

    IMPORTANT :
    Ne surtout pas transformer les retours à la ligne en espaces.
    Ils sont nécessaires pour analyser les rubriques des fiches
    de poste.
    """

    if not texte:
        return ""

    # Normalisation des retours à la ligne
    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")

    # Suppression des espaces inutiles en fin de ligne
    lignes = []

    for ligne in texte.split("\n"):

        ligne = re.sub(
            r"[ \t]+",
            " ",
            ligne
        ).strip()

        if ligne:
            lignes.append(ligne)

    texte = "\n".join(lignes)

    # Espaces multiples éventuels
    texte = re.sub(
        r"[ ]{2,}",
        " ",
        texte
    )

    return texte.strip()


# ============================================================
# TEXTE NORMALISÉ POUR LES RECHERCHES
# ============================================================

def texte_normalise(texte):
    """
    Produit une version aplatie du texte uniquement pour
    les recherches génériques.

    Cette fonction NE doit PAS remplacer le texte structuré.
    """

    if not texte:
        return ""

    resultat = texte.lower()

    resultat = resultat.replace("\n", " ")

    resultat = re.sub(
        r"\s+",
        " ",
        resultat
    )

    return resultat.strip()


# ============================================================
# GÉNÉRATION PRÉSENTATION CANDIDAT
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

    return texte
