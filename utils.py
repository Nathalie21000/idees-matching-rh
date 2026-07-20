import pdfplumber
import re


def extract_text(file):
    """
    Extrait le texte d'un PDF.
    """

    texte = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texte += page.extract_text() or ""

    return nettoyer_texte(texte)


def nettoyer_texte(texte):
    """
    Nettoyage du texte avant analyse.
    """

    texte = texte.lower()

    texte = texte.replace("\n", " ")

    texte = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ0-9 ]", " ", texte)

    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()
