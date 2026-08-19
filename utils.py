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
    Le texte brut conserve les retours à la ligne afin de permettre
    l'analyse des tâches ligne par ligne.
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
    Extrait le texte d'un fichier PDF.

    Les retours à la ligne des pages sont conservés.
    """

    morceaux = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            texte_page = page.extract_text()

            if texte_page:
                morceaux.append(texte_page)

    return "\n".join(morceaux)


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """
    Extrait le texte d'un fichier Word (.docx).

    Lit :
    - les paragraphes ;
    - les tableaux.

    Les lignes sont conservées afin de permettre la détection
    des tâches commençant par des verbes d'action.
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
                morceaux.append(" | ".join(cellules))

    return "\n".join(morceaux)


# ============================================================
# NETTOYAGE DU TEXTE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoie le texte sans supprimer les retours à la ligne.

    C'est important car metiers.py utilise les lignes du CV
    pour identifier les tâches commençant par des verbes d'action.

    Exemple conservé :

        Préparer les commandes
        Charger les camions
        Contrôler les marchandises

    """

    if not texte:
        return ""

    # Normalisation des retours à la ligne
    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")

    lignes_nettoyees = []

    for ligne in texte.split("\n"):

        ligne = ligne.strip()

        if not ligne:
            continue

        # Remplacement de certains caractères gênants
        ligne = ligne.replace("\u00a0", " ")
        ligne = re.sub(r"[ \t]+", " ", ligne)

        lignes_nettoyees.append(ligne)

    return "\n".join(lignes_nettoyees)


# ============================================================
# TEXTE NORMALISÉ POUR LES RECHERCHES
# ============================================================

def normaliser_texte(texte):
    """
    Produit une version simplifiée du texte pour les recherches
    par mots-clés.

    Cette fonction ne remplace PAS nettoyer_texte().
    Elle est disponible lorsque l'application a besoin d'un texte
    sans accents ni ponctuation.
    """

    if not texte:
        return ""

    texte = texte.lower()

    texte = re.sub(
        r"[^a-zàâçéèêëîïôûùüÿñæœ0-9\s]",
        " ",
        texte,
    )

    texte = re.sub(
        r"\s+",
        " ",
        texte,
    )

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
    agence,
):
    """
    Génère une présentation simple du candidat à envoyer
    à l'entreprise.
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
