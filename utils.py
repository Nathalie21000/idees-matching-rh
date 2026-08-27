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
# NORMALISATION D'UNE LIGNE
# ============================================================

def _normaliser_ligne(ligne):
    """
    Normalise une ligne uniquement pour faciliter
    la reconnaissance des libellés.

    Le texte original est conservé pour les valeurs.
    """

    if not ligne:
        return ""

    ligne = ligne.strip().lower()

    ligne = ligne.replace("’", "'")

    # Suppression des caractères parasites fréquents
    # produits par OCR en début de ligne.
    ligne = re.sub(
        r"^[|¦]+[\s]*",
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
# RECONNAISSANCE DES LIBELLÉS
# ============================================================

def _est_libelle_entreprise(ligne):
    """
    Reconnaît le libellé 'Nom de l'entreprise'
    même si l'OCR ajoute des caractères parasites.
    """

    texte = _normaliser_ligne(ligne)

    return bool(
        re.search(
            r"\bnom\s+de\s+l['’]?entreprise\b",
            texte,
            re.IGNORECASE
        )
    )


def _est_libelle_poste(ligne):
    """
    Reconnaît le libellé 'Intitulé du poste'.
    """

    texte = _normaliser_ligne(ligne)

    return bool(
        re.search(
            r"\bintitul[ée]?\s+du\s+poste\b",
            texte,
            re.IGNORECASE
        )
    )


def _est_libelle_taches(ligne):
    """
    Reconnaît le libellé 'Liste des tâches proposées'.
    """

    texte = _normaliser_ligne(ligne)

    return bool(
        re.search(
            r"\bliste\s+des\s+t[âa]ches\s+propos[ée]es\b",
            texte,
            re.IGNORECASE
        )
    )


def _est_un_libelle_cible(ligne):
    return (
        _est_libelle_entreprise(ligne)
        or _est_libelle_poste(ligne)
        or _est_libelle_taches(ligne)
    )


# ============================================================
# NETTOYAGE D'UNE VALEUR OCR
# ============================================================

def _nettoyer_valeur_ocr(valeur):
    """
    Nettoie les caractères de tableau ou d'OCR autour
    d'une valeur.

    Exemple :
        '| COLAS |'
    devient :
        'COLAS'
    """

    if not valeur:
        return ""

    valeur = valeur.strip()

    valeur = re.sub(
        r"^[|¦]+",
        "",
        valeur
    )

    valeur = re.sub(
        r"[|¦]+$",
        "",
        valeur
    )

    return valeur.strip()


# ============================================================
# EXTRACTION D'UNE VALEUR SUR UNE LIGNE
# ============================================================

def _extraire_apres_texte(
    ligne,
    motif
):
    """
    Extrait ce qui se trouve après un libellé sur une même ligne.
    """

    resultat = re.search(
        motif,
        ligne,
        flags=re.IGNORECASE
    )

    if not resultat:
        return ""

    valeur = ligne[resultat.end():]

    valeur = valeur.strip()

    valeur = valeur.lstrip(":|¦ ")

    return _nettoyer_valeur_ocr(valeur)


# ============================================================
# EXTRACTION SPÉCIALE DU FORMULAIRE OCR
# ============================================================

def _extraire_formulaire_ocr(lignes):
    """
    Gère la structure particulière du formulaire scanné.

    Le formulaire peut présenter les rubriques en colonnes :

        | Nom de l'entreprise : | | Liste des tâches proposées : | |
        | COLAS                  | Maçonnerie VRD                 |
        |                        | Pose de bordures               |
        ...
        Intitulé du poste:
        ...
        OUVRIER VRD CONDUCTEUR D ENGINS

    Cette fonction cherche donc les informations
    sans supposer qu'une rubrique occupe une ligne entière.
    """

    resultat = {
        "entreprise": "",
        "poste": "",
        "taches": "",
        "entreprise_trouvee": False,
        "poste_trouve": False,
        "taches_trouvees": False,
    }

    # ========================================================
    # ÉTAPE 1 : rechercher la ligne contenant les en-têtes
    # ========================================================

    index_entete_colonnes = None

    for index, ligne in enumerate(lignes):

        normalisee = _normaliser_ligne(ligne)

        if (
            "nom de l'entreprise" in normalisee
            and "liste des tâches proposées" in normalisee
        ):
            index_entete_colonnes = index
            break

    # ========================================================
    # ÉTAPE 2 : formulaire en colonnes
    # ========================================================

    if index_entete_colonnes is not None:

        # ----------------------------------------------------
        # Ligne suivante : entreprise + première tâche
        # ----------------------------------------------------

        for index in range(
            index_entete_colonnes + 1,
            min(
                index_entete_colonnes + 8,
                len(lignes)
            )
        ):

            ligne = lignes[index]

            # ------------------------------------------------
            # Entreprise
            # ------------------------------------------------

            if not resultat["entreprise"]:

                # Recherche de COLAS ou autre valeur située
                # après le libellé entreprise.
                valeur = _extraire_apres_texte(
                    ligne,
                    r"nom\s+de\s+l['’]?entreprise\s*:?"
                )

                if valeur:

                    resultat["entreprise"] = valeur
                    resultat["entreprise_trouvee"] = True

                else:

                    # Dans le formulaire OCR, la valeur peut
                    # être sur la ligne suivante.
                    #
                    # On évite cependant de prendre une tâche
                    # comme nom d'entreprise.
                    if (
                        not _est_libelle_taches(ligne)
                        and not _est_libelle_poste(ligne)
                    ):

                        morceaux = [
                            _nettoyer_valeur_ocr(
                                morceau
                            )
                            for morceau in ligne.split("|")
                            if morceau.strip()
                        ]

                        if morceaux:

                            premiere_valeur = morceaux[0]

                            if (
                                premiere_valeur
                                and premiere_valeur.lower()
                                not in (
                                    "nom de l'entreprise",
                                    "liste des tâches proposées"
                                )
                            ):

                                resultat["entreprise"] = (
                                    premiere_valeur
                                )

                                resultat[
                                    "entreprise_trouvee"
                                ] = True

            # ------------------------------------------------
            # Tâches
            # ------------------------------------------------

            # On récupère les lignes situées dans la zone
            # des tâches jusqu'à l'arrivée du poste.
            if not resultat["taches_trouvees"]:

                morceaux = [
                    _nettoyer_valeur_ocr(morceau)
                    for morceau in ligne.split("|")
                    if morceau.strip()
                ]

                # Si plusieurs colonnes sont présentes,
                # la deuxième colonne correspond aux tâches.
                if len(morceaux) >= 2:

                    for morceau in morceaux[1:]:

                        if not morceau:
                            continue

                        texte_morceau = morceau.lower()

                        if (
                            "liste des tâches proposées"
                            in texte_morceau
                        ):
                            continue

                        if (
                            "nom de l'entreprise"
                            in texte_morceau
                        ):
                            continue

                        if (
                            "intitulé du poste"
                            in texte_morceau
                        ):
                            continue

                        resultat["taches"] = (
                            morceau
                            if not resultat["taches"]
                            else resultat["taches"]
                            + ", "
                            + morceau
                        )

            # ------------------------------------------------
            # Arrêt lorsqu'on arrive au poste
            # ------------------------------------------------

            if _est_libelle_poste(ligne):

                break

        # ----------------------------------------------------
        # Recherche plus large des tâches après l'en-tête
        # ----------------------------------------------------

        taches = []

        for index in range(
            index_entete_colonnes + 1,
            len(lignes)
        ):

            ligne = lignes[index]

            # Le poste marque la fin de la zone.
            if _est_libelle_poste(ligne):
                break

            # On ignore les lignes de libellés.
            normalisee = _normaliser_ligne(ligne)

            if (
                "nom de l'entreprise" in normalisee
                or "liste des tâches proposées" in normalisee
            ):
                continue

            morceaux = [
                _nettoyer_valeur_ocr(morceau)
                for morceau in ligne.split("|")
                if morceau.strip()
            ]

            # Pour une ligne avec deux colonnes,
            # la deuxième partie est la tâche.
            if len(morceaux) >= 2:

                candidat_tache = morceaux[-1]

                if candidat_tache:

                    taches.append(candidat_tache)

            elif len(morceaux) == 1:

                morceau = morceaux[0]

                # On ne prend pas une éventuelle valeur
                # d'entreprise comme tâche.
                if (
                    morceau
                    and morceau != resultat["entreprise"]
                ):

                    # On évite les lignes manifestement
                    # étrangères à la rubrique.
                    if len(morceau) > 2:

                        taches.append(morceau)

        # ----------------------------------------------------
        # Nettoyage des tâches
        # ----------------------------------------------------

        taches_finales = []

        for tache in taches:

            tache = tache.strip()

            if not tache:
                continue

            if tache in taches_finales:
                continue

            # On évite de capturer le libellé du poste
            # ou des éléments manifestement étrangers.
            if _est_libelle_poste(tache):
                continue

            taches_finales.append(tache)

        if taches_finales:

            resultat["taches"] = ", ".join(
                taches_finales
            )

            resultat["taches_trouvees"] = True

    # ========================================================
    # ÉTAPE 3 : recherche du poste
    # ========================================================

    for index, ligne in enumerate(lignes):

        if not _est_libelle_poste(ligne):
            continue

        # Valeur éventuellement sur la même ligne.
        valeur = _extraire_apres_texte(
            ligne,
            r"intitul[ée]?\s+du\s+poste\s*:?"
        )

        if valeur:

            resultat["poste"] = valeur
            resultat["poste_trouve"] = True
            break

        # Sinon, chercher les lignes suivantes.
        for suivant in range(
            index + 1,
            min(index + 5, len(lignes))
        ):

            candidat = lignes[suivant].strip()

            if not candidat:
                continue

            if _est_un_libelle_cible(candidat):
                break

            # On ignore les éléments très courts ou manifestement
            # issus d'une autre rubrique.
            if len(candidat) >= 4:

                morceaux = [
                    _nettoyer_valeur_ocr(morceau)
                    for morceau in candidat.split("|")
                    if morceau.strip()
                ]

                # Si une seule valeur est présente,
                # c'est très probablement l'intitulé.
                if len(morceaux) == 1:

                    resultat["poste"] = morceaux[0]
                    resultat["poste_trouve"] = True
                    break

                # Si plusieurs colonnes sont présentes,
                # on recherche une valeur suffisamment longue.
                for morceau in morceaux:

                    if len(morceau) >= 8:

                        resultat["poste"] = morceau
                        resultat["poste_trouve"] = True
                        break

                if resultat["poste_trouve"]:
                    break

        if resultat["poste_trouve"]:
            break

    return resultat


# ============================================================
# EXTRACTION CIBLÉE DE LA FICHE DE POSTE
# ============================================================

def extraire_fiche_poste_ciblee(texte):
    """
    Extrait :

    1. Nom de l'entreprise
    2. Intitulé du poste
    3. Liste des tâches proposées

    La fonction tient compte de la structure particulière
    des formulaires scannés en colonnes.
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
    # TENTATIVE SPÉCIALE FORMULAIRE OCR
    # ========================================================

    resultat = _extraire_formulaire_ocr(lignes)

    # ========================================================
    # SECOURS : EXTRACTION CLASSIQUE
    # ========================================================

    # Si une information n'a pas été trouvée,
    # on applique l'ancienne méthode.

    index_entreprise = None
    index_poste = None
    index_taches = None

    for index, ligne in enumerate(lignes):

        if (
            index_entreprise is None
            and _est_libelle_entreprise(ligne)
        ):

            index_entreprise = index

        if (
            index_poste is None
            and _est_libelle_poste(ligne)
        ):

            index_poste = index

        if (
            index_taches is None
            and _est_libelle_taches(ligne)
        ):

            index_taches = index

    # ========================================================
    # ENTREPRISE - SECOURS
    # ========================================================

    if (
        not resultat["entreprise_trouvee"]
        and index_entreprise is not None
    ):

        ligne = lignes[index_entreprise]

        valeur = _extraire_apres_texte(
            ligne,
            r"nom\s+de\s+l['’]?entreprise\s*:?"
        )

        if valeur:

            resultat["entreprise"] = valeur
            resultat["entreprise_trouvee"] = True

        else:

            for suivant in range(
                index_entreprise + 1,
                min(index_entreprise + 4, len(lignes))
            ):

                candidat = lignes[suivant].strip()

                if not candidat:
                    continue

                if _est_libelle_poste(candidat):
                    break

                if _est_libelle_taches(candidat):
                    continue

                morceaux = [
                    _nettoyer_valeur_ocr(morceau)
                    for morceau in candidat.split("|")
                    if morceau.strip()
                ]

                if morceaux:

                    valeur = morceaux[0]

                    if (
                        valeur
                        and valeur.lower()
                        not in (
                            "nom de l'entreprise",
                            "liste des tâches proposées"
                        )
                    ):

                        resultat["entreprise"] = valeur
                        resultat["entreprise_trouvee"] = True
                        break

    # ========================================================
    # POSTE - SECOURS
    # ========================================================

    if (
        not resultat["poste_trouve"]
        and index_poste is not None
    ):

        ligne = lignes[index_poste]

        valeur = _extraire_apres_texte(
            ligne,
            r"intitul[ée]?\s+du\s+poste\s*:?"
        )

        if valeur:

            resultat["poste"] = valeur
            resultat["poste_trouve"] = True

        else:

            for suivant in range(
                index_poste + 1,
                min(index_poste + 5, len(lignes))
            ):

                candidat = lignes[suivant].strip()

                if not candidat:
                    continue

                if _est_un_libelle_cible(candidat):
                    break

                morceaux = [
                    _nettoyer_valeur_ocr(morceau)
                    for morceau in candidat.split("|")
                    if morceau.strip()
                ]

                if len(morceaux) == 1:

                    resultat["poste"] = morceaux[0]
                    resultat["poste_trouve"] = True
                    break

    # ========================================================
    # TÂCHES - SECOURS
    # ========================================================

    if (
        not resultat["taches_trouvees"]
        and index_taches is not None
    ):

        taches = []

        for suivant in range(
            index_taches + 1,
            len(lignes)
        ):

            candidat = lignes[suivant].strip()

            if not candidat:
                if taches:
                    break

                continue

            if _est_libelle_poste(candidat):
                break

            if _est_libelle_entreprise(candidat):
                break

            morceaux = [
                _nettoyer_valeur_ocr(morceau)
                for morceau in candidat.split("|")
                if morceau.strip()
            ]

            for morceau in morceaux:

                if not morceau:
                    continue

                if (
                    morceau
                    == resultat["entreprise"]
                ):
                    continue

                taches.append(morceau)

        if taches:

            resultat["taches"] = ", ".join(
                dict.fromkeys(taches)
            )

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
