import pdfplumber
import docx
import re
import pytesseract

from PIL import Image


# ============================================================
# EXTRACTION DE TEXTE
# PDF + WORD
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou Word.

    Pour un PDF :
    1. On tente d'abord une extraction classique avec pdfplumber.
    2. Si le PDF ne contient pas suffisamment de texte,
       on utilise automatiquement Tesseract OCR.
    3. Le texte OCR est obtenu page par page.

    Pour un DOCX :
    - lecture des paragraphes ;
    - lecture des tableaux.
    """

    nom_fichier = getattr(file, "name", "") or ""
    nom_fichier_min = nom_fichier.lower()

    if nom_fichier_min.endswith(".docx"):

        texte = extraire_texte_docx(file)

    elif nom_fichier_min.endswith(".pdf"):

        texte = extraire_texte_pdf(file)

        # ----------------------------------------------------
        # Si l'extraction classique est vide ou trop faible,
        # on considère que le PDF est probablement scanné.
        # ----------------------------------------------------

        if len(texte.strip()) < 50:

            texte_ocr = extraire_texte_pdf_ocr(file)

            if texte_ocr.strip():

                texte = texte_ocr

    else:

        texte = ""

    return nettoyer_texte(texte)


# ============================================================
# EXTRACTION PDF CLASSIQUE
# ============================================================

def extraire_texte_pdf(file):
    """
    Extraction classique d'un PDF avec pdfplumber.
    """

    morceaux = []

    try:

        # Revenir au début du fichier si nécessaire
        try:
            file.seek(0)
        except Exception:
            pass

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3
                )

                if texte_page:

                    morceaux.append(
                        texte_page
                    )

    except Exception:

        return ""

    return "\n".join(morceaux)


# ============================================================
# EXTRACTION PDF PAR OCR
# ============================================================

def extraire_texte_pdf_ocr(file):
    """
    Utilise Tesseract pour lire un PDF scanné.

    La page PDF est convertie en image puis envoyée
    à Tesseract.

    La langue française est privilégiée.
    """

    morceaux = []

    try:

        try:
            file.seek(0)
        except Exception:
            pass

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                try:

                    image_page = page.to_image(
                        resolution=300
                    ).original

                    texte_page = pytesseract.image_to_string(
                        image_page,
                        lang="fra+eng"
                    )

                    if texte_page:

                        morceaux.append(
                            texte_page
                        )

                except Exception:

                    continue

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

        try:
            file.seek(0)
        except Exception:
            pass

        document = docx.Document(file)

        # ----------------------------------------------------
        # Paragraphes
        # ----------------------------------------------------

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:

                morceaux.append(
                    texte
                )

        # ----------------------------------------------------
        # Tableaux
        # ----------------------------------------------------

        for table in document.tables:

            for ligne in table.rows:

                cellules = []

                for cellule in ligne.cells:

                    texte_cellule = (
                        cellule.text.strip()
                    )

                    if texte_cellule:

                        cellules.append(
                            texte_cellule
                        )

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
    Nettoyage léger du texte.

    Les retours à la ligne sont conservés.
    """

    if not texte:

        return ""

    texte = texte.replace(
        "\r\n",
        "\n"
    )

    texte = texte.replace(
        "\r",
        "\n"
    )

    texte = texte.replace(
        "\xa0",
        " "
    )

    # Supprimer les balises SVG / liens accidentellement
    # récupérés par l'affichage Streamlit.
    texte = re.sub(
        r"\[svg\]\([^)]+\)",
        "",
        texte,
        flags=re.IGNORECASE
    )

    # Espaces multiples
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
# NORMALISATION D'UNE LIGNE
# ============================================================

def _normaliser_ligne(ligne):
    """
    Normalise une ligne pour faciliter la détection OCR.

    Exemple :

        | Nom de l'entreprise : | | Liste des tâches proposées : |

    devient une chaîne plus facile à analyser.
    """

    if not ligne:

        return ""

    ligne = ligne.strip()

    ligne = ligne.replace(
        "’",
        "'"
    )

    # Supprimer les barres verticales utilisées par l'OCR
    ligne = ligne.replace(
        "|",
        " "
    )

    # Supprimer certains caractères décoratifs
    ligne = ligne.replace(
        "®",
        " "
    )

    ligne = re.sub(
        r"\s+",
        " ",
        ligne
    )

    return ligne.strip()


# ============================================================
# DETECTION DES LIBELLES
# ============================================================

def _position_libelle_entreprise(texte):
    """
    Retourne la position du libellé entreprise.
    """

    motifs = [
        r"nom\s+de\s+l['’]entreprise\s*:?",
        r"nom\s+de\s+l['’]entreprise",
    ]

    for motif in motifs:

        resultat = re.search(
            motif,
            texte,
            flags=re.IGNORECASE
        )

        if resultat:

            return resultat.start(), resultat.end()

    return None


def _position_libelle_poste(texte):
    """
    Retourne la position du libellé poste.

    Tolère les erreurs OCR fréquentes :

        Intitulé du poste
        Intitule du poste
        Intitul du poste
        Intitulé du poste:
        Intitule du poste:
    """

    motifs = [

        r"intitul[ée]?\s+du\s+poste\s*:?",

        r"intitul[ée]?\s+de\s+poste\s*:?",

        r"intitul[ée]?\s+poste\s*:?",
    ]

    for motif in motifs:

        resultat = re.search(
            motif,
            texte,
            flags=re.IGNORECASE
        )

        if resultat:

            return (
                resultat.start(),
                resultat.end()
            )

    return None


def _position_libelle_taches(texte):
    """
    Retourne la position du libellé tâches.

    Tolère les erreurs d'accent et d'OCR.
    """

    motifs = [

        r"liste\s+des\s+t[âa]ches\s+propos[ée]es\s*:?",

        r"liste\s+des\s+taches\s+proposees\s*:?",

        r"liste\s+des\s+taches\s+proposées\s*:?",

        r"liste\s+des\s+t[âa]ches\s+proposees\s*:?",
    ]

    for motif in motifs:

        resultat = re.search(
            motif,
            texte,
            flags=re.IGNORECASE
        )

        if resultat:

            return (
                resultat.start(),
                resultat.end()
            )

    return None


# ============================================================
# TEST LIBELLE
# ============================================================

def _est_libelle_entreprise(ligne):

    texte = _normaliser_ligne(
        ligne
    )

    return (
        _position_libelle_entreprise(
            texte
        )
        is not None
    )


def _est_libelle_poste(ligne):

    texte = _normaliser_ligne(
        ligne
    )

    return (
        _position_libelle_poste(
            texte
        )
        is not None
    )


def _est_libelle_taches(ligne):

    texte = _normaliser_ligne(
        ligne
    )

    return (
        _position_libelle_taches(
            texte
        )
        is not None
    )


def _est_un_libelle_cible(ligne):

    return (
        _est_libelle_entreprise(ligne)
        or _est_libelle_poste(ligne)
        or _est_libelle_taches(ligne)
    )


# ============================================================
# NETTOYAGE VALEUR
# ============================================================

def _nettoyer_valeur(valeur):

    if not valeur:

        return ""

    valeur = valeur.strip()

    valeur = valeur.strip(
        "|:;,-"
    )

    valeur = re.sub(
        r"\s+",
        " ",
        valeur
    )

    return valeur.strip()


# ============================================================
# EXTRACTION ENTREPRISE
# ============================================================

def _extraire_entreprise_depuis_texte(texte):
    """
    Recherche :

        Nom de l'entreprise : COLAS

    ou :

        Nom de l'entreprise :
        COLAS

    ou dans une ligne OCR mélangée :

        Nom de l'entreprise : | | Liste des tâches proposées

    Dans ce dernier cas, on NE prend pas le libellé suivant
    comme nom d'entreprise.
    """

    position = _position_libelle_entreprise(
        texte
    )

    if position is None:

        return ""

    debut_valeur = position[1]

    reste = texte[debut_valeur:]

    # Si un autre libellé cible apparaît immédiatement,
    # il n'y a pas de valeur sur cette partie.
    positions_suivantes = []

    for fonction in (
        _position_libelle_poste,
        _position_libelle_taches,
    ):

        pos = fonction(reste)

        if pos is not None:

            positions_suivantes.append(
                pos[0]
            )

    if positions_suivantes:

        fin = min(
            positions_suivantes
        )

        candidat = reste[:fin]

    else:

        # On ne prend que la première ligne
        # lorsqu'il n'y a pas de libellé suivant.
        candidat = reste.split(
            "\n",
            1
        )[0]

    candidat = _nettoyer_valeur(
        candidat
    )

    # Si la valeur est vide, chercher la ligne suivante.
    if not candidat:

        lignes = texte.split(
            "\n"
        )

        for i, ligne in enumerate(
            lignes
        ):

            if _est_libelle_entreprise(
                ligne
            ):

                for suivante in lignes[
                    i + 1:
                ]:

                    suivante = _nettoyer_valeur(
                        suivante
                    )

                    if not suivante:

                        continue

                    if _est_un_libelle_cible(
                        suivante
                    ):

                        return ""

                    return suivante

    return candidat


# ============================================================
# EXTRACTION POSTE
# ============================================================

def _extraire_poste_depuis_texte(texte):
    """
    Recherche l'intitulé du poste.

    Exemple OCR :

        Intitulé du poste:
        OUVRIER VRD CONDUCTEUR D ENGINS
    """

    position = _position_libelle_poste(
        texte
    )

    if position is None:

        return ""

    reste = texte[
        position[1]:
    ]

    # --------------------------------------------------------
    # Le poste peut être sur la même ligne.
    # --------------------------------------------------------

    candidat = reste.split(
        "\n",
        1
    )[0]

    candidat = _nettoyer_valeur(
        candidat
    )

    # --------------------------------------------------------
    # Si rien n'est trouvé, chercher ligne suivante.
    # --------------------------------------------------------

    if not candidat:

        lignes = texte.split(
            "\n"
        )

        for i, ligne in enumerate(
            lignes
        ):

            if _est_libelle_poste(
                ligne
            ):

                for suivante in lignes[
                    i + 1:
                ]:

                    suivante = _nettoyer_valeur(
                        suivante
                    )

                    if not suivante:

                        continue

                    if _est_un_libelle_cible(
                        suivante
                    ):

                        return ""

                    return suivante

    return candidat


# ============================================================
# EXTRACTION TACHES
# ============================================================

def _extraire_taches_depuis_texte(texte):
    """
    Extrait les tâches situées après :

        Liste des tâches proposées :

    jusqu'au prochain libellé cible.

    Important :
    on limite volontairement la zone de lecture afin
    d'éviter que tout le reste du formulaire soit considéré
    comme une tâche.
    """

    position = _position_libelle_taches(
        texte
    )

    if position is None:

        return ""

    reste = texte[
        position[1]:
    ]

    # --------------------------------------------------------
    # Trouver le prochain libellé cible.
    # --------------------------------------------------------

    positions_suivantes = []

    for fonction in (
        _position_libelle_poste,
        _position_libelle_entreprise,
    ):

        pos = fonction(reste)

        if pos is not None:

            positions_suivantes.append(
                pos[0]
            )

    if positions_suivantes:

        fin = min(
            positions_suivantes
        )

        zone = reste[:fin]

    else:

        # Si le poste n'est pas détecté à cause de l'OCR,
        # on ne lit pas tout le document.
        #
        # On limite la recherche aux premières lignes.
        zone = "\n".join(
            reste.split("\n")[:8]
        )

    # --------------------------------------------------------
    # Nettoyage
    # --------------------------------------------------------

    lignes = zone.split(
        "\n"
    )

    valeurs = []

    for ligne in lignes:

        ligne = _normaliser_ligne(
            ligne
        )

        ligne = _nettoyer_valeur(
            ligne
        )

        if not ligne:

            continue

        if _est_un_libelle_cible(
            ligne
        ):

            break

        # ----------------------------------------------------
        # Éviter les éléments manifestement parasites.
        # ----------------------------------------------------

        if ligne in (
            "=",
            "!",
            "-",
            "_",
        ):

            continue

        valeurs.append(
            ligne
        )

    # --------------------------------------------------------
    # Nettoyage des tâches OCR.
    # --------------------------------------------------------

    taches_propres = []

    for valeur in valeurs:

        valeur = re.sub(
            r"^[•●▪◦\-]+\s*",
            "",
            valeur
        )

        valeur = _nettoyer_valeur(
            valeur
        )

        if valeur:

            taches_propres.append(
                valeur
            )

    return ", ".join(
        taches_propres
    )


# ============================================================
# EXTRACTION CIBLEE
# ============================================================

def extraire_fiche_poste_ciblee(texte):
    """
    Extrait uniquement :

    - entreprise
    - poste
    - tâches

    La fonction est spécialement adaptée aux PDF scannés
    lus par Tesseract.

    Retour :

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
    # Normalisation générale
    # --------------------------------------------------------

    texte_normalise = texte.replace(
        "\r\n",
        "\n"
    )

    texte_normalise = texte_normalise.replace(
        "\r",
        "\n"
    )

    # --------------------------------------------------------
    # ENTREPRISE
    # --------------------------------------------------------

    entreprise = _extraire_entreprise_depuis_texte(
        texte_normalise
    )

    if entreprise:

        resultat["entreprise"] = entreprise
        resultat["entreprise_trouvee"] = True

    # --------------------------------------------------------
    # POSTE
    # --------------------------------------------------------

    poste = _extraire_poste_depuis_texte(
        texte_normalise
    )

    if poste:

        resultat["poste"] = poste
        resultat["poste_trouve"] = True

    # --------------------------------------------------------
    # TACHES
    # --------------------------------------------------------

    taches = _extraire_taches_depuis_texte(
        texte_normalise
    )

    if taches:

        resultat["taches"] = taches
        resultat["taches_trouvees"] = True

    # --------------------------------------------------------
    # SECURITE :
    # Ne jamais considérer un libellé comme une valeur.
    # --------------------------------------------------------

    valeurs_interdites = [
        "nom de l'entreprise",
        "liste des tâches proposées",
        "liste des taches proposées",
        "liste des taches proposees",
        "intitulé du poste",
        "intitule du poste",
        "intitul du poste",
    ]

    for cle in (
        "entreprise",
        "poste",
        "taches",
    ):

        valeur = resultat[cle]

        valeur_min = (
            valeur.lower()
            .strip()
        )

        for interdit in valeurs_interdites:

            if valeur_min == interdit:

                resultat[cle] = ""

                resultat[
                    f"{cle}_trouvee"
                ] = False

                break

    return resultat


# ============================================================
# GENERATION PRESENTATION CANDIDAT
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
    Génère une présentation d'un candidat
    destinée à l'entreprise cliente.
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
