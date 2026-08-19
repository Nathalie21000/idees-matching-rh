import pdfplumber
import docx
import re


# ============================================================
# EXTRACTION DE TEXTE (PDF + WORD)
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF (.pdf) ou Word (.docx).
    Le format est détecté automatiquement à partir du nom
    du fichier.
    """

    nom_fichier = getattr(file, "name", "") or ""

    nom_fichier_min = nom_fichier.lower()

    if nom_fichier_min.endswith(".docx"):
        texte = extraire_texte_docx(file)

    else:
        # Par défaut (et pour les .pdf) on tente une lecture PDF
        texte = extraire_texte_pdf(file)

    return nettoyer_texte(texte)


def extraire_texte_pdf(file):
    """
    Extrait le texte d'un fichier PDF.
    """

    texte = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texte += page.extract_text() or ""

    return texte


def extraire_texte_docx(file):
    """
    Extrait le texte d'un fichier Word (.docx).
    Lit à la fois les paragraphes et le contenu des tableaux,
    car les fiches de poste et CV utilisent souvent des tableaux.
    """

    document = docx.Document(file)

    morceaux = []

    for paragraphe in document.paragraphs:
        if paragraphe.text:
            morceaux.append(paragraphe.text)

    for table in document.tables:
        for ligne in table.rows:
            for cellule in ligne.cells:
                if cellule.text:
                    morceaux.append(cellule.text)

    return "\n".join(morceaux)


def nettoyer_texte(texte):
    """
    Nettoyage du texte avant analyse.
    """

    texte = texte.lower()

    texte = texte.replace("\n", " ")

    texte = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9 ]", " ", texte)

    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()


# ----------------------------
# GÉNÉRATION PRÉSENTATION CANDIDAT
# ----------------------------

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
