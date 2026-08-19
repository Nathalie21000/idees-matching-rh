import pdfplumber
import docx
import re


# ============================================================
# EXTRACTION DE TEXTE (PDF + WORD)
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou Word (.docx).

    IMPORTANT :
    On conserve les retours à la ligne afin de permettre
    l'analyse des tâches et des rubriques.
    """

    nom_fichier = getattr(file, "name", "") or ""
    nom_fichier_min = nom_fichier.lower()

    if nom_fichier_min.endswith(".docx"):
        texte = extraire_texte_docx(file)
    else:
        texte = extraire_texte_pdf(file)

    return nettoyer_texte_structure(texte)


def extraire_texte_pdf(file):
    """
    Extrait le texte d'un fichier PDF en conservant
    autant que possible la structure des lignes.
    """

    texte = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_texte = page.extract_text() or ""

            if page_texte:
                texte.append(page_texte)

    return "\n".join(texte)


def extraire_texte_docx(file):
    """
    Extrait le texte d'un fichier Word (.docx).

    Lit :
    - les paragraphes ;
    - les tableaux.

    Les retours à la ligne sont conservés.
    """

    document = docx.Document(file)

    morceaux = []

    # Paragraphes
    for paragraphe in document.paragraphs:
        texte = paragraphe.text.strip()

        if texte:
            morceaux.append(texte)

    # Tableaux
    for table in document.tables:
        for ligne in table.rows:

            cellules = []

            for cellule in ligne.cells:
                texte_cellule = cellule.text.strip()

                if texte_cellule:
                    cellules.append(texte_cellule)

            if cellules:
                morceaux.append(" | ".join(cellules))

    return "\n".join(morceaux)


# ============================================================
# NETTOYAGE STRUCTURE
# ============================================================

def nettoyer_texte_structure(texte):
    """
    Nettoie le texte sans supprimer les retours à la ligne.

    Cette version est utilisée pour l'analyse des tâches
    et des rubriques.
    """

    if not texte:
        return ""

    lignes = []

    for ligne in texte.splitlines():

        ligne = ligne.strip()

        if not ligne:
            continue

        # Normalisation des espaces
        ligne = re.sub(r"\s+", " ", ligne)

        lignes.append(ligne)

    return "\n".join(lignes)


# ============================================================
# TEXTE NORMALISÉ POUR LES RECHERCHES
# ============================================================

def nettoyer_texte(texte):
    """
    Produit une version simplifiée du texte pour les recherches
    de mots-clés et le matching.

    Contrairement à nettoyer_texte_structure(), cette fonction
    supprime volontairement les retours à la ligne.
    """

    if not texte:
        return ""

    texte = texte.lower()

    texte = texte.replace("\n", " ")

    texte = re.sub(
        r"[^a-zàâçéèêëîïôûùüÿñæœ0-9 ]",
        " ",
        texte
    )

    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()


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
