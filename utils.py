import re

import pdfplumber
import docx
import pytesseract

from PIL import Image


# ============================================================
# EXTRACTION DE TEXTE
# PDF + WORD
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou Word.

    PDF :
    - tente d'abord une extraction classique avec pdfplumber ;
    - conserve autant que possible la mise en page ;
    - si le texte classique est insuffisant, utilise Tesseract OCR.

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

        # ----------------------------------------------------
        # Si le PDF contient peu ou pas de texte,
        # on bascule automatiquement vers OCR.
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
    Extrait le texte d'un PDF avec pdfplumber.

    On utilise layout=True afin de conserver au maximum
    l'organisation visuelle du document.

    Cela est particulièrement important pour les fiches
    de poste contenant deux colonnes.
    """

    morceaux = []

    try:

        try:
            file.seek(0)
        except Exception:
            pass

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = ""

                try:

                    texte_page = page.extract_text(
                        x_tolerance=2,
                        y_tolerance=3,
                        layout=True,
                    )

                except Exception:

                    try:

                        texte_page = page.extract_text(
                            x_tolerance=2,
                            y_tolerance=3,
                        )

                    except Exception:

                        texte_page = ""

                if texte_page:

                    morceaux.append(
                        texte_page
                    )

    except Exception:

        return ""

    return "\n".join(morceaux)


# ============================================================
# EXTRACTION PDF OCR
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
                        lang="fra+eng",
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
    Nettoyage général.

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

    # Supprimer les liens SVG éventuellement récupérés
    # dans certains affichages Streamlit.
    texte = re.sub(
        r"\[svg\]\([^)]+\)",
        "",
        texte,
        flags=re.IGNORECASE,
    )

    # Nettoyage léger des espaces.
    texte = re.sub(
        r"[ \t]+",
        " ",
        texte,
    )

    # Limiter les lignes vides.
    texte = re.sub(
        r"\n[ \t]*\n[ \t]*\n+",
        "\n\n",
        texte,
    )

    return texte.strip()


# ============================================================
# NORMALISATION
# ============================================================

def _normaliser_ligne(ligne):
    """
    Normalise une ligne uniquement pour la recherche
    des libellés.

    Les valeurs originales ne sont pas modifiées ici.
    """

    if not ligne:

        return ""

    ligne = ligne.strip()

    ligne = ligne.replace(
        "’",
        "'"
    )

    ligne = ligne.replace(
        "|",
        " "
    )

    ligne = ligne.replace(
        "®",
        " "
    )

    ligne = re.sub(
        r"\s+",
        " ",
        ligne,
    )

    return ligne.strip()


def _nettoyer_valeur(valeur):
    """
    Nettoie une valeur extraite.
    """

    if not valeur:

        return ""

    valeur = valeur.strip()

    valeur = valeur.strip(
        "|:;,-"
    )

    valeur = re.sub(
        r"\s+",
        " ",
        valeur,
    )

    return valeur.strip()


# ============================================================
# DETECTION DES LIBELLES
# ============================================================

def _position_libelle_entreprise(texte):
    """
    Recherche le libellé :
        Nom de l'entreprise
    """

    if not texte:

        return None

    motifs = [

        r"nom\s+de\s+l['’]?\s*entreprise\s*:?",

        r"nom\s+de\s+l['’]entreprise\s*:?",
    ]

    for motif in motifs:

        resultat = re.search(
            motif,
            texte,
            flags=re.IGNORECASE,
        )

        if resultat:

            return (
                resultat.start(),
                resultat.end(),
            )

    return None


def _position_libelle_poste(texte):
    """
    Recherche le libellé du poste.

    Tolère plusieurs erreurs OCR :
    - Intitulé du poste
    - Intitule du poste
    - Intitul du poste
    - Intitulé du poste:
    """

    if not texte:

        return None

    motifs = [

        r"intitul[ée]?\s+du\s+poste\s*:?",

        r"intitul[ée]?\s+de\s+poste\s*:?",

        r"intitul[ée]?\s+poste\s*:?",
    ]

    for motif in motifs:

        resultat = re.search(
            motif,
            texte,
            flags=re.IGNORECASE,
        )

        if resultat:

            return (
                resultat.start(),
                resultat.end(),
            )

    return None


def _position_libelle_taches(texte):
    """
    Recherche le libellé :
        Liste des tâches proposées
    """

    if not texte:

        return None

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
            flags=re.IGNORECASE,
        )

        if resultat:

            return (
                resultat.start(),
                resultat.end(),
            )

    return None


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
# EXTRACTION PAR LIGNES
# ============================================================

def _lignes_propres(texte):

    if not texte:

        return []

    lignes = texte.split(
        "\n"
    )

    resultat = []

    for ligne in lignes:

        ligne = ligne.strip()

        if ligne:

            resultat.append(
                ligne
            )

    return resultat


# ============================================================
# EXTRACTION ENTREPRISE
# ============================================================

def _extraire_entreprise_depuis_texte(texte):
    """
    Extrait l'entreprise.

    Gère notamment :

        Nom de l'entreprise : COLAS

    ou :

        Nom de l'entreprise :
        COLAS

    et évite de prendre le libellé suivant
    comme valeur.
    """

    if not texte:

        return ""

    lignes = _lignes_propres(
        texte
    )

    # --------------------------------------------------------
    # Recherche ligne par ligne
    # --------------------------------------------------------

    for index, ligne in enumerate(lignes):

        ligne_normalisee = _normaliser_ligne(
            ligne
        )

        position = _position_libelle_entreprise(
            ligne_normalisee
        )

        if position is None:

            continue

        # Valeur éventuellement présente après le libellé.
        valeur = ligne_normalisee[
            position[1]:
        ]

        valeur = _nettoyer_valeur(
            valeur
        )

        # Si une autre rubrique se trouve sur la même ligne,
        # on ne prend pas cette rubrique comme valeur.
        if valeur:

            if (
                _est_libelle_poste(
                    valeur
                )
                or _est_libelle_taches(
                    valeur
                )
            ):

                valeur = ""

        if valeur:

            return valeur

        # ----------------------------------------------------
        # Sinon on cherche dans les lignes suivantes.
        # ----------------------------------------------------

        for suivante in lignes[
            index + 1:
        ]:

            suivante_normalisee = _normaliser_ligne(
                suivante
            )

            if not suivante_normalisee:

                continue

            if _est_libelle_entreprise(
                suivante_normalisee
            ):

                continue

            if _est_libelle_poste(
                suivante_normalisee
            ):

                break

            if _est_libelle_taches(
                suivante_normalisee
            ):

                break

            valeur = _nettoyer_valeur(
                suivante_normalisee
            )

            if valeur:

                return valeur

    return ""


# ============================================================
# EXTRACTION POSTE
# ============================================================

def _extraire_poste_depuis_texte(texte):
    """
    Extrait l'intitulé du poste.

    Gère notamment :

        Intitulé du poste:
        OUVRIER VRD CONDUCTEUR D ENGINS

    et les variantes OCR.
    """

    if not texte:

        return ""

    lignes = _lignes_propres(
        texte
    )

    for index, ligne in enumerate(lignes):

        ligne_normalisee = _normaliser_ligne(
            ligne
        )

        position = _position_libelle_poste(
            ligne_normalisee
        )

        if position is None:

            continue

        # ----------------------------------------------------
        # Cas 1 : valeur sur la même ligne
        # ----------------------------------------------------

        valeur = ligne_normalisee[
            position[1]:
        ]

        valeur = _nettoyer_valeur(
            valeur
        )

        if valeur:

            # Une valeur ne doit pas être un autre libellé.
            if not _est_un_libelle_cible(
                valeur
            ):

                return valeur

        # ----------------------------------------------------
        # Cas 2 : valeur sur la ligne suivante
        # ----------------------------------------------------

        for suivante in lignes[
            index + 1:
        ]:

            suivante_normalisee = _normaliser_ligne(
                suivante
            )

            if not suivante_normalisee:

                continue

            if _est_libelle_poste(
                suivante_normalisee
            ):

                continue

            if _est_libelle_entreprise(
                suivante_normalisee
            ):

                break

            if _est_libelle_taches(
                suivante_normalisee
            ):

                break

            valeur = _nettoyer_valeur(
                suivante_normalisee
            )

            if valeur:

                return valeur

    return ""


# ============================================================
# EXTRACTION TACHES
# ============================================================

def _extraire_taches_depuis_texte(texte):
    """
    Extrait les tâches.

    Pour éviter que toute la fiche soit considérée comme
    une liste de tâches, on s'arrête dès qu'une rubrique
    importante apparaît.

    La méthode gère également les lignes OCR qui contiennent
    plusieurs éléments.
    """

    if not texte:

        return ""

    lignes = _lignes_propres(
        texte
    )

    index_taches = None

    # --------------------------------------------------------
    # Trouver la ligne contenant le libellé tâches.
    # --------------------------------------------------------

    for index, ligne in enumerate(lignes):

        if _est_libelle_taches(
            ligne
        ):

            index_taches = index
            break

    if index_taches is None:

        return ""

    valeurs = []

    # --------------------------------------------------------
    # Lire les lignes après le libellé.
    # --------------------------------------------------------

    for ligne in lignes[
        index_taches:
    ]:

        ligne_normalisee = _normaliser_ligne(
            ligne
        )

        position = _position_libelle_taches(
            ligne_normalisee
        )

        # ----------------------------------------------------
        # Première ligne : retirer le libellé.
        # ----------------------------------------------------

        if ligne == lignes[
            index_taches
        ]:

            if position is not None:

                ligne_normalisee = (
                    ligne_normalisee[
                        position[1]:
                    ]
                )

                ligne_normalisee = _nettoyer_valeur(
                    ligne_normalisee
                )

            else:

                ligne_normalisee = ""

        else:

            ligne_normalisee = _nettoyer_valeur(
                ligne_normalisee
            )

        if not ligne_normalisee:

            continue

        # ----------------------------------------------------
        # Si on rencontre l'intitulé du poste,
        # on arrête la zone des tâches.
        # ----------------------------------------------------

        if _est_libelle_poste(
            ligne_normalisee
        ):

            break

        # Si une nouvelle entreprise apparaît,
        # on arrête également.
        if _est_libelle_entreprise(
            ligne_normalisee
        ):

            break

        # ----------------------------------------------------
        # Éliminer quelques artefacts OCR évidents.
        # ----------------------------------------------------

        if ligne_normalisee in (
            "=",
            "!",
            "-",
            "_",
        ):

            continue

        valeurs.append(
            ligne_normalisee
        )

        # ----------------------------------------------------
        # Une fiche de poste peut avoir plusieurs tâches,
        # mais les tâches sont généralement dans les premières
        # lignes de la zone.
        #
        # On limite volontairement à 6 lignes utiles afin
        # d'éviter de capturer toute la fiche.
        # ----------------------------------------------------

        if len(valeurs) >= 6:

            break

    # --------------------------------------------------------
    # Nettoyage final
    # --------------------------------------------------------

    taches_propres = []

    for valeur in valeurs:

        valeur = re.sub(
            r"^[•●▪◦\-]+\s*",
            "",
            valeur,
        )

        valeur = _nettoyer_valeur(
            valeur
        )

        if not valeur:

            continue

        # Ne jamais garder un libellé comme tâche.
        if _est_un_libelle_cible(
            valeur
        ):

            continue

        taches_propres.append(
            valeur
        )

    # --------------------------------------------------------
    # Supprimer les doublons consécutifs.
    # --------------------------------------------------------

    resultat = []

    for valeur in taches_propres:

        if (
            not resultat
            or valeur.lower()
            != resultat[-1].lower()
        ):

            resultat.append(
                valeur
            )

    return ", ".join(
        resultat
    )


# ============================================================
# EXTRACTION CIBLEE
# ============================================================

def extraire_fiche_poste_ciblee(texte):
    """
    Extrait UNIQUEMENT :

    - entreprise
    - poste
    - tâches

    La fonction fonctionne avec :
    - PDF texte ;
    - PDF scanné passé par OCR ;
    - OCR imparfait ;
    - libellés présents sur une même ligne.

    Elle ne déduit aucune compétence.
    Elle n'invente aucune valeur.
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

    texte_normalise = (
        texte
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    # --------------------------------------------------------
    # Première tentative : extraction ciblée classique.
    # --------------------------------------------------------

    entreprise = _extraire_entreprise_depuis_texte(
        texte_normalise
    )

    poste = _extraire_poste_depuis_texte(
        texte_normalise
    )

    taches = _extraire_taches_depuis_texte(
        texte_normalise
    )

    # --------------------------------------------------------
    # SECURITE :
    # ne jamais considérer un libellé comme une valeur.
    # --------------------------------------------------------

    valeurs_interdites = {
        "nom de l'entreprise",
        "nom de l’entreprise",
        "liste des tâches proposées",
        "liste des taches proposées",
        "liste des taches proposees",
        "intitulé du poste",
        "intitule du poste",
        "intitul du poste",
    }

    def valeur_valide(
        valeur
    ):

        if not valeur:

            return ""

        valeur_min = (
            valeur
            .strip()
            .lower()
        )

        if valeur_min in valeurs_interdites:

            return ""

        return valeur.strip()

    entreprise = valeur_valide(
        entreprise
    )

    poste = valeur_valide(
        poste
    )

    taches = valeur_valide(
        taches
    )

    # --------------------------------------------------------
    # Résultat.
    # --------------------------------------------------------

    if entreprise:

        resultat[
            "entreprise"
        ] = entreprise

        resultat[
            "entreprise_trouvee"
        ] = True

    if poste:

        resultat[
            "poste"
        ] = poste

        resultat[
            "poste_trouve"
        ] = True

    if taches:

        resultat[
            "taches"
        ] = taches

        resultat[
            "taches_trouvees"
        ] = True

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
    agence,
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
