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

    Pour un PDF :
    - lecture du texte natif avec pdfplumber.

    Pour un DOCX :
    - lecture des paragraphes ;
    - lecture des tableaux.

    Le texte retourné conserve les retours à la ligne afin
    de permettre l'analyse des rubriques de fiches de poste.
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
    Extrait le texte d'un PDF page par page.

    Important :
    pdfplumber ne fait PAS d'OCR.
    Un PDF constitué uniquement d'images/scans pourra donc
    retourner très peu ou pas de texte.
    """

    texte_pages = []

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = page.extract_text()

                if texte_page:
                    texte_pages.append(texte_page)

    except Exception:
        return ""

    return "\n".join(texte_pages)


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """
    Extrait le contenu d'un document Word .docx.

    Les paragraphes ET les tableaux sont lus.
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
                    morceaux.append(" | ".join(cellules))

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# NETTOYAGE DU TEXTE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoie légèrement le texte sans supprimer les retours
    à la ligne.

    C'est volontaire :
    l'analyse des fiches de poste a besoin de connaître
    les différentes lignes et rubriques.
    """

    if not texte:
        return ""

    # Normalisation des retours à la ligne
    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")

    # Espaces insécables
    texte = texte.replace("\xa0", " ")

    # Plusieurs espaces -> un seul
    texte = re.sub(r"[ \t]+", " ", texte)

    # Plusieurs lignes vides -> une seule
    texte = re.sub(r"\n\s*\n+", "\n\n", texte)

    return texte.strip()


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
    Génère la présentation d'un candidat destinée
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
