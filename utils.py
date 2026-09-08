import re

import pdfplumber
import docx


# ============================================================
# OUTILS GÉNÉRAUX
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoyage léger du texte tout en conservant
    les retours à la ligne.
    """
    if not texte:
        return ""

    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")
    texte = texte.replace("\xa0", " ")
    texte = texte.replace("\u200b", "")

    texte = re.sub(
        r"[ \t]+",
        " ",
        texte,
    )

    texte = re.sub(
        r"[ \t]*\n[ \t]*",
        "\n",
        texte,
    )

    texte = re.sub(
        r"\n{3,}",
        "\n\n",
        texte,
    )

    return texte.strip()


def _normaliser_ligne(ligne):
    """
    Normalise une ligne pour faciliter la reconnaissance
    des intitulés.
    """
    if not ligne:
        return ""

    texte = ligne.lower()

    texte = texte.replace(
        "’",
        "'",
    )

    texte = texte.replace(
        "|",
        " ",
    )

    texte = re.sub(
        r"\s+",
        " ",
        texte,
    )

    return texte.strip()


# ============================================================
# DÉTECTION DE LA FICHE DE POSTE ID'EES
# ============================================================

def _semble_etre_une_fiche_de_poste(texte):
    """
    Vérifie si le texte ressemble à notre fiche de poste
    ID'EES INTERIM.

    Aucun nom d'entreprise n'est recherché.
    """

    if not texte:
        return False

    texte_normalise = _normaliser_ligne(
        texte
    )

    nombre_indices = 0

    # Tolérance aux erreurs OCR :
    # l'entreprise peut être reconnue comme :
    # l'entreprise
    # I'entreprise
    # l entreprise
    # I entreprise

    if re.search(
        r"nom\s+de\s+[lI]['’]?\s*entreprise",
        texte_normalise,
        re.IGNORECASE,
    ):
        nombre_indices += 1

    if re.search(
        r"liste\s+des\s+t[âa]ches\s+propos[ée]es",
        texte_normalise,
        re.IGNORECASE,
    ):
        nombre_indices += 1

    if re.search(
        r"intitul[ée]\s+du\s+poste",
        texte_normalise,
        re.IGNORECASE,
    ):
        nombre_indices += 1

    return nombre_indices >= 2


# ============================================================
# LECTURE DES CHAMPS D'UN PDF MODIFIABLE
# ============================================================

def _decoder_valeur_pdf(valeur):
    """
    Transforme une valeur de champ PDF en texte exploitable.
    """

    if valeur is None:
        return ""

    if isinstance(
        valeur,
        bytes,
    ):
        try:
            return valeur.decode(
                "latin-1",
                errors="ignore",
            ).strip()
        except Exception:
            return ""

    return str(
        valeur
    ).strip()


def _extraire_champs_formulaire_idees(file):
    """
    Lit directement les champs de formulaire du PDF ID'EES
    avec PyMuPDF.

    Texte 01 = entreprise
    Texte 02 = intitulé du poste
    Texte 03 = liste des tâches

    Aucun nom d'entreprise n'est recherché.
    """

    resultat = {
        "entreprise": "",
        "poste": "",
        "taches": "",
    }

    try:
        import pymupdf

        file.seek(0)

        contenu = file.read()

        document = pymupdf.open(
            stream=contenu,
            filetype="pdf",
        )

        for page in document:

            widgets = page.widgets()

            if widgets is None:
                continue

            for widget in widgets:

                nom_champ = _decoder_valeur_pdf(
                    widget.field_name
                )

                valeur_champ = _decoder_valeur_pdf(
                    widget.field_value
                )

                if nom_champ == "Texte 01":
                    resultat["entreprise"] = valeur_champ

                elif nom_champ == "Texte 02":
                    resultat["poste"] = valeur_champ

                elif nom_champ == "Texte 03":
                    resultat["taches"] = valeur_champ

        document.close()

    except Exception:
        pass

    try:
        file.seek(0)
    except Exception:
        pass

    return resultat


# ============================================================
# CRÉATION D'UN TEXTE STRUCTURÉ POUR UNE FICHE MODIFIABLE
# ============================================================

def _construire_texte_fiche_formulaire(champs):
    """
    Transforme les champs PDF en texte structuré.
    """

    morceaux = []

    entreprise = (
        champs.get(
            "entreprise",
            "",
        )
        or ""
    ).strip()

    poste = (
        champs.get(
            "poste",
            "",
        )
        or ""
    ).strip()

    taches = (
        champs.get(
            "taches",
            "",
        )
        or ""
    ).strip()

    if entreprise:
        morceaux.append(
            "Nom de l'entreprise : "
            + entreprise
        )

    if poste:
        morceaux.append(
            "Intitulé du poste : "
            + poste
        )

    if taches:

        morceaux.append(
            "Liste des tâches proposées :"
        )

        taches = taches.replace(
            "\r\n",
            "\n",
        )

        taches = taches.replace(
            "\r",
            "\n",
        )

        lignes_taches = []

        for ligne in taches.split("\n"):

            ligne = ligne.strip()

            if not ligne:
                continue

            ligne = re.sub(
                r"^\s*[-•●▪◦]+\s*",
                "",
                ligne,
            )

            if ligne:
                lignes_taches.append(
                    ligne
                )

        if len(lignes_taches) == 1:

            ligne_unique = lignes_taches[0]

            morceaux_taches = re.split(
                r"\s*-\s*",
                ligne_unique,
            )

            morceaux_taches = [
                morceau.strip()
                for morceau in morceaux_taches
                if morceau.strip()
            ]

            if len(morceaux_taches) > 1:
                lignes_taches = morceaux_taches

        morceaux.extend(
            lignes_taches
        )

    return "\n".join(
        morceaux
    )


# ============================================================
# EXTRACTION PDF AVEC PYMUPDF
# ============================================================

def _extraire_texte_pdf_pymupdf(file):
    """
    Extraction classique du texte avec PyMuPDF.
    """

    try:

        import pymupdf

        file.seek(0)

        contenu = file.read()

        document = pymupdf.open(
            stream=contenu,
            filetype="pdf",
        )

        morceaux = []

        for page in document:

            texte_page = page.get_text(
                "text"
            )

            if texte_page:
                morceaux.append(
                    texte_page
                )

        document.close()

        try:
            file.seek(0)
        except Exception:
            pass

        return nettoyer_texte(
            "\n".join(
                morceaux
            )
        )

    except Exception:

        try:
            file.seek(0)
        except Exception:
            pass

        return ""


# ============================================================
# NOUVEAU : OCR DE L'EN-TÊTE À DEUX COLONNES
# ============================================================

def _ocr_zone_haute_deux_colonnes(document):
    """
    Extrait l'en-tête de la première page d'une fiche scannée.

    La fiche ID'EES possède un en-tête organisé en deux colonnes :
        - colonne gauche : entreprise / informations du poste
        - colonne droite : tâches

    Tesseract peut mélanger les deux colonnes lorsqu'il lit
    toute la page d'un seul coup.

    On isole donc les 30 % supérieurs de la page puis :
        - colonne gauche = 44 % de la largeur
        - colonne droite = reste de la largeur

    Chaque colonne est envoyée séparément à Tesseract.
    """

    try:
        import pymupdf
        import pytesseract
        from PIL import Image

        if document.page_count == 0:
            return ""

        page = document[0]

        matrice = pymupdf.Matrix(
            2.5,
            2.5,
        )

        pixmap = page.get_pixmap(
            matrix=matrice,
            alpha=False,
        )

        image = Image.frombytes(
            "RGB",
            (
                pixmap.width,
                pixmap.height,
            ),
            pixmap.samples,
        )

        largeur = image.width
        hauteur = image.height

        # ----------------------------------------------------
        # Zone haute : 30 % de la hauteur
        # ----------------------------------------------------

        hauteur_haute = int(
            hauteur * 0.30
        )

        zone_haute = image.crop(
            (
                0,
                0,
                largeur,
                hauteur_haute,
            )
        )

        largeur_haute = zone_haute.width

        # ----------------------------------------------------
        # Découpage à 44 % de la largeur
        # ----------------------------------------------------

        limite_colonne = int(
            largeur_haute * 0.44
        )

        colonne_gauche = zone_haute.crop(
            (
                0,
                0,
                limite_colonne,
                zone_haute.height,
            )
        )

        colonne_droite = zone_haute.crop(
            (
                limite_colonne,
                0,
                zone_haute.width,
                zone_haute.height,
            )
        )

        # ----------------------------------------------------
        # OCR séparé de chaque colonne
        # ----------------------------------------------------

        texte_gauche = pytesseract.image_to_string(
            colonne_gauche,
            lang="fra+eng",
        )

        texte_droite = pytesseract.image_to_string(
            colonne_droite,
            lang="fra+eng",
        )

        texte_final = (
            (texte_gauche or "")
            + "\n"
            + (texte_droite or "")
        )

        return nettoyer_texte(
            texte_final
        )

    except Exception:
        return ""


# ============================================================
# NOUVEAU : OCR GLOBAL AVEC EN-TÊTE DOUBLE COLONNE
# ============================================================

def _extraire_texte_pdf_ocr_global(document):
    """
    OCR global d'un PDF scanné.

    Pour la première page :
        1. l'en-tête est OCRisé séparément en deux colonnes ;
        2. le reste de la page est OCRisé normalement ;
        3. l'en-tête est placé au tout début du texte.

    Pour les pages suivantes :
        OCR normal de toute la page.

    Cela évite que Tesseract mélange le nom de l'entreprise
    avec les tâches situées dans la colonne voisine.
    """

    try:
        import pymupdf
        import pytesseract
        from PIL import Image

        morceaux = []

        # ----------------------------------------------------
        # EN-TÊTE DE LA PREMIÈRE PAGE
        # ----------------------------------------------------

        texte_entete = _ocr_zone_haute_deux_colonnes(
            document
        )

        if texte_entete:
            morceaux.append(
                texte_entete
            )

        # ----------------------------------------------------
        # OCR DU RESTE DES PAGES
        # ----------------------------------------------------

        for numero_page in range(
            document.page_count
        ):

            page = document[
                numero_page
            ]

            matrice = pymupdf.Matrix(
                2.5,
                2.5,
            )

            pixmap = page.get_pixmap(
                matrix=matrice,
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                (
                    pixmap.width,
                    pixmap.height,
                ),
                pixmap.samples,
            )

            # Sur la première page, on ne ré-OCRise pas
            # les 30 % du haut : ils viennent déjà de l'OCR
            # à deux colonnes.
            if numero_page == 0:

                debut_reste = int(
                    image.height * 0.30
                )

                image = image.crop(
                    (
                        0,
                        debut_reste,
                        image.width,
                        image.height,
                    )
                )

            texte_page = pytesseract.image_to_string(
                image,
                lang="fra+eng",
            )

            if texte_page:

                morceaux.append(
                    texte_page
                )

        return nettoyer_texte(
            "\n".join(morceaux)
        )

    except Exception:
        return ""


# ============================================================
# OCR PDF SCANNÉ
# ============================================================

def extraire_texte_pdf_ocr(file):
    """
    OCR d'un PDF avec traitement spécial de l'en-tête
    à deux colonnes.

    Cette fonction est utilisée pour les PDF scannés.
    """

    try:
        import pymupdf

        file.seek(0)

        contenu = file.read()

        document = pymupdf.open(
            stream=contenu,
            filetype="pdf",
        )

        texte = _extraire_texte_pdf_ocr_global(
            document
        )

        document.close()

        try:
            file.seek(0)
        except Exception:
            pass

        return nettoyer_texte(
            texte
        )

    except Exception:

        try:
            file.seek(0)
        except Exception:
            pass

        return ""


# ============================================================
# EXTRACTION PDFPLUMBER DE SECOURS
# ============================================================

def _extraire_texte_pdf_pdfplumber(file):
    """
    Extraction de secours avec pdfplumber.
    """

    try:

        file.seek(0)

        morceaux = []

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3,
                )

                if texte_page:

                    morceaux.append(
                        texte_page
                    )

        try:
            file.seek(0)
        except Exception:
            pass

        return nettoyer_texte(
            "\n".join(morceaux)
        )

    except Exception:

        try:
            file.seek(0)
        except Exception:
            pass

        return ""


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """
    Extrait le texte d'un fichier Word,
    y compris les tableaux.
    """

    morceaux = []

    try:

        file.seek(0)

        document = docx.Document(
            file
        )

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:

                morceaux.append(
                    texte
                )

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
                        " | ".join(
                            cellules
                        )
                    )

    except Exception:

        return ""

    return nettoyer_texte(
        "\n".join(
            morceaux
        )
    )


# ============================================================
# EXTRACTION PRINCIPALE
# ============================================================

def extract_text(file):
    """
    Fonction principale appelée par app.py.

    PDF modifiable :
        lecture directe des champs du formulaire.

    PDF scanné :
        OCR avec traitement spécial de l'en-tête
        à deux colonnes.

    Aucun nom d'entreprise n'est utilisé pour déterminer
    si le document peut être lu.
    """

    nom_fichier = getattr(
        file,
        "name",
        "",
    ) or ""

    nom_fichier = nom_fichier.lower()

    # ========================================================
    # WORD
    # ========================================================

    if nom_fichier.endswith(
        ".docx"
    ):

        return extraire_texte_docx(
            file
        )

    # ========================================================
    # PDF
    # ========================================================

    if nom_fichier.endswith(
        ".pdf"
    ):

        # ----------------------------------------------------
        # Première lecture du PDF
        # ----------------------------------------------------

        texte_normal = (
            _extraire_texte_pdf_pymupdf(
                file
            )
        )

        if not texte_normal:

            texte_normal = (
                _extraire_texte_pdf_pdfplumber(
                    file
                )
            )

        # ----------------------------------------------------
        # PDF MODIFIABLE ID'EES
        # ----------------------------------------------------

        # IMPORTANT :
        # on conserve ce traitement AVANT l'OCR.
        # Le PDF modifiable ENERSCIENCE continue donc
        # à être lu directement par ses champs.

        champs = (
            _extraire_champs_formulaire_idees(
                file
            )
        )

        formulaire_trouve = any(
            [
                champs.get("entreprise", ""),
                champs.get("poste", ""),
                champs.get("taches", ""),
            ]
        )

        if formulaire_trouve:

            texte_formulaire = (
                _construire_texte_fiche_formulaire(
                    champs
                )
            )

            if texte_formulaire:

                return nettoyer_texte(
                    texte_formulaire
                )

        # ----------------------------------------------------
        # PDF SCANNÉ ID'EES
        # ----------------------------------------------------

        # Si la lecture classique reconnaît déjà la fiche,
        # on passe quand même par l'OCR spécialisé.
        #
        # Cela garantit que l'en-tête à deux colonnes
        # est correctement séparé.

        if _semble_etre_une_fiche_de_poste(
            texte_normal
        ):

            texte_ocr = (
                extraire_texte_pdf_ocr(
                    file
                )
            )

            if texte_ocr:

                return nettoyer_texte(
                    texte_ocr
                )

            return nettoyer_texte(
                texte_normal
            )

        # ----------------------------------------------------
        # Si l'extraction classique ne reconnaît pas la fiche,
        # on tente quand même l'OCR spécialisé.
        # ----------------------------------------------------

        texte_ocr = (
            extraire_texte_pdf_ocr(
                file
            )
        )

        if texte_ocr:

            return nettoyer_texte(
                texte_ocr
            )

        # ====================================================
        # PDF CLASSIQUE : TEXTE NORMAL
        # ====================================================

        if texte_normal and len(
            texte_normal.strip()
        ) >= 30:

            return nettoyer_texte(
                texte_normal
            )

        return ""

    # ========================================================
    # FORMAT INCONNU
    # ========================================================

    return ""


# ============================================================
# OUTILS POUR LA FICHE DE POSTE
# ============================================================

def _extraire_valeur_apres_libelle(
    ligne,
    type_information,
):
    """
    Cherche une valeur placée directement après un libellé.

    Pour l'entreprise, tolère les erreurs OCR
    l'entreprise / I'entreprise.
    """

    if not ligne:
        return ""

    texte = ligne.strip()

    if type_information == "entreprise":

        motif = (
            r"nom\s+de\s+[lI]['’]?\s*entreprise"
            r"\s*:?\s*(.*)$"
        )

    elif type_information == "poste":

        motif = (
            r"intitul[ée]\s+du\s+poste"
            r"\s*:?\s*(.*)$"
        )

    elif type_information == "taches":

        motif = (
            r"liste\s+des\s+t[âa]ches\s+propos[ée]es"
            r"\s*:?\s*(.*)$"
        )

    else:

        return ""

    correspondance = re.search(
        motif,
        texte,
        re.IGNORECASE,
    )

    if not correspondance:
        return ""

    valeur = correspondance.group(
        1
    ).strip()

    valeur = valeur.strip(
        " |:-"
    )

    return valeur


def _est_libelle_entreprise(
    ligne
):
    """
    Détecte le libellé Nom de l'entreprise.

    Tolère notamment :
        Nom de l'entreprise
        Nom de I'entreprise
        Nom de l entreprise
        Nom de I entreprise
    """

    if not ligne:
        return False

    texte = _normaliser_ligne(
        ligne
    )

    return bool(
        re.search(
            r"\bnom\s+de\s+[lI]['’]?\s*entreprise\b",
            texte,
            re.IGNORECASE,
        )
    )


def _est_libelle_poste(
    ligne
):

    texte = _normaliser_ligne(
        ligne
    )

    return bool(
        re.search(
            r"intitul[ée]\s+du\s+poste",
            texte,
            re.IGNORECASE,
        )
    )


def _est_libelle_taches(
    ligne
):

    texte = _normaliser_ligne(
        ligne
    )

    return bool(
        re.search(
            r"liste\s+des\s+t[âa]ches\s+propos[ée]es",
            texte,
            re.IGNORECASE,
        )
    )


# ============================================================
# EXTRACTION CIBLÉE FICHE DE POSTE
# ============================================================

def extraire_fiche_poste_ciblee(
    texte
):
    """
    Extrait uniquement :

    - entreprise
    - poste
    - tâches

    Aucun CACES, permis, VIP ou autre information
    n'est automatiquement récupéré ici.
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

    texte = nettoyer_texte(
        texte
    )

    lignes = [
        ligne.strip()
        for ligne in texte.split(
            "\n"
        )
        if ligne.strip()
    ]

    # ========================================================
    # ENTREPRISE
    # ========================================================

    for index, ligne in enumerate(
        lignes
    ):

        if not _est_libelle_entreprise(
            ligne
        ):
            continue

        valeur = _extraire_valeur_apres_libelle(
            ligne,
            "entreprise",
        )

        if not valeur:

            for suivant in lignes[
                index + 1:
            ]:

                if (
                    _est_libelle_poste(
                        suivant
                    )
                    or _est_libelle_taches(
                        suivant
                    )
                ):
                    break

                if not _est_libelle_entreprise(
                    suivant
                ):

                    valeur = suivant.strip(
                        " |:-"
                    )

                    if valeur:
                        break

        if valeur:

            resultat[
                "entreprise"
            ] = valeur.strip()

            resultat[
                "entreprise_trouvee"
            ] = True

            break

    # ========================================================
    # POSTE
    # ========================================================

    for index, ligne in enumerate(
        lignes
    ):

        if not _est_libelle_poste(
            ligne
        ):
            continue

        valeur = _extraire_valeur_apres_libelle(
            ligne,
            "poste",
        )

        if not valeur:

            for suivant in lignes[
                index + 1:
            ]:

                if (
                    _est_libelle_entreprise(
                        suivant
                    )
                    or _est_libelle_taches(
                        suivant
                    )
                ):
                    break

                if not _est_libelle_poste(
                    suivant
                ):

                    valeur = suivant.strip(
                        " |:-"
                    )

                    if valeur:
                        break

        if valeur:

            resultat[
                "poste"
            ] = valeur.strip()

            resultat[
                "poste_trouve"
            ] = True

            break

    # ========================================================
    # TÂCHES
    # ========================================================

    for index, ligne in enumerate(
        lignes
    ):

        if not _est_libelle_taches(
            ligne
        ):
            continue

        taches = []

        # ----------------------------------------------------
        # Tâche éventuelle sur la même ligne
        # ----------------------------------------------------

        valeur = _extraire_valeur_apres_libelle(
            ligne,
            "taches",
        )

        if valeur:

            morceaux = re.split(
                r"\s*\|\s*",
                valeur,
            )

            for morceau in morceaux:

                morceau = morceau.strip(
                    " |:-"
                )

                if morceau:

                    taches.append(
                        morceau
                    )

        # ----------------------------------------------------
        # Lignes suivantes
        # ----------------------------------------------------

        for suivant in lignes[
            index + 1:
        ]:

            if _est_libelle_entreprise(
                suivant
            ):
                break

            if _est_libelle_poste(
                suivant
            ):
                break

            texte_suivant = (
                suivant.strip()
            )

            if not texte_suivant:
                continue

            texte_normalise = (
                _normaliser_ligne(
                    texte_suivant
                )
            )

            rubriques_arret = [
                "conditions de travail",
                "conditions particulières",
                "habilitations obligatoires",
                "habilitations, certificats",
                "equipements de protection",
                "équipements de protection",
                "pénibilité",
                "sécurité dans votre entreprise",
                "formation renforcée",
                "accueil sécurité",
                "suivi médical",
                "travaux en hauteur",
                "informations du signataire",
                "signature",
            ]

            if any(
                rubrique in texte_normalise
                for rubrique in rubriques_arret
            ):
                break

            texte_suivant = re.sub(
                r"^[|•●▪◦*\-]+\s*",
                "",
                texte_suivant,
            )

            texte_suivant = (
                texte_suivant.strip()
            )

            if texte_suivant:

                taches.append(
                    texte_suivant
                )

        # ----------------------------------------------------
        # Suppression des doublons
        # ----------------------------------------------------

        taches_finales = []

        for tache in taches:

            tache = tache.strip()

            if not tache:
                continue

            if tache not in taches_finales:

                taches_finales.append(
                    tache
                )

        if taches_finales:

            resultat[
                "taches"
            ] = ", ".join(
                taches_finales
            )

            resultat[
                "taches_trouvees"
            ] = True

        break

    # ========================================================
    # NETTOYAGE FINAL
    # ========================================================

    resultat[
        "entreprise"
    ] = (
        resultat[
            "entreprise"
        ]
        or ""
    ).strip()

    resultat[
        "poste"
    ] = (
        resultat[
            "poste"
        ]
        or ""
    ).strip()

    resultat[
        "taches"
    ] = (
        resultat[
            "taches"
        ]
        or ""
    ).strip()

    return resultat


# ============================================================
# GÉNÉRATION DE PRÉSENTATION
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
    Génère une présentation du candidat pour l'entreprise.
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