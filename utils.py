```python
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
    - utilise pdfplumber si le PDF contient du vrai texte ;
    - utilise Tesseract OCR si le PDF est scanné.

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

    Si pdfplumber ne trouve pas de texte sur une page,
    Tesseract est utilisé.
    """

    morceaux = []

    try:

        with pdfplumber.open(file) as pdf:

            for page in pdf.pages:

                texte_page = page.extract_text(
                    x_tolerance=2,
                    y_tolerance=3
                )

                if texte_page and texte_page.strip():

                    morceaux.append(texte_page)

                else:

                    texte_ocr = extraire_page_avec_ocr(page)

                    if texte_ocr:
                        morceaux.append(texte_ocr)

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# OCR CLASSIQUE
# ============================================================

def extraire_page_avec_ocr(page):
    """
    Convertit une page PDF en image puis utilise Tesseract.
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
# OCR AVEC COORDONNÉES
# ============================================================

def extraire_donnees_ocr(page):
    """
    Effectue un OCR avec coordonnées.

    Tesseract retourne pour chaque mot :
    - son texte ;
    - sa position X ;
    - sa position Y ;
    - sa largeur ;
    - sa hauteur ;
    - son niveau de confiance.

    Cette information permet de reconstruire les colonnes
    du formulaire au lieu de dépendre uniquement de l'ordre
    du texte OCR.
    """

    try:

        image_page = page.to_image(
            resolution=300
        ).original

        donnees = pytesseract.image_to_data(
            image_page,
            lang="fra",
            config="--psm 6",
            output_type=pytesseract.Output.DICT
        )

        mots = []

        nombre = len(
            donnees.get("text", [])
        )

        for i in range(nombre):

            texte = (
                donnees["text"][i]
                or ""
            ).strip()

            if not texte:
                continue

            try:
                confiance = float(
                    donnees["conf"][i]
                )
            except Exception:
                confiance = 0

            try:
                x = int(
                    donnees["left"][i]
                )

                y = int(
                    donnees["top"][i]
                )

                largeur = int(
                    donnees["width"][i]
                )

                hauteur = int(
                    donnees["height"][i]
                )

            except Exception:
                continue

            mots.append({
                "texte": texte,
                "x": x,
                "y": y,
                "largeur": largeur,
                "hauteur": hauteur,
                "confiance": confiance
            })

        return mots

    except Exception:

        return []


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

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:
                morceaux.append(texte)

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
# NORMALISATION
# ============================================================

def _normaliser_ligne(ligne):

    if not ligne:
        return ""

    ligne = ligne.strip().lower()

    ligne = ligne.replace(
        "’",
        "'"
    )

    ligne = re.sub(
        r"[|¦]+",
        " ",
        ligne
    )

    ligne = re.sub(
        r"\s+",
        " ",
        ligne
    )

    return ligne.strip()


# ============================================================
# RECONNAISSANCE ENTREPRISE
# ============================================================

def _est_libelle_entreprise(ligne):

    texte = _normaliser_ligne(
        ligne
    )

    return bool(
        re.search(
            r"nom\s+de\s+l['’]?entreprise",
            texte,
            re.IGNORECASE
        )
    )


# ============================================================
# RECONNAISSANCE TÂCHES
# ============================================================

def _est_libelle_taches(ligne):

    texte = _normaliser_ligne(
        ligne
    )

    return bool(
        re.search(
            r"liste\s+des\s+t[âa]ches\s+propos[ée]es",
            texte,
            re.IGNORECASE
        )
    )


# ============================================================
# RECONNAISSANCE POSTE
# ============================================================

def _est_libelle_poste(ligne):

    texte = _normaliser_ligne(
        ligne
    )

    # Reconnaissance normale
    if re.search(
        r"intitul[ée]?\s+du\s+poste",
        texte,
        re.IGNORECASE
    ):
        return True

    # Variantes observées dans notre OCR
    variantes = [
        "linie du poste",
        "linte du poste",
        "linie poste",
        "linte poste",
        "intitul poste",
        "intitule poste",
        "intitul du poste",
        "intitule du poste",
    ]

    for variante in variantes:

        if variante in texte:
            return True

    # Détection souple
    if (
        "poste" in texte
        and (
            "linie" in texte
            or "linte" in texte
            or "intitul" in texte
            or "intitule" in texte
        )
    ):
        return True

    return False


# ============================================================
# NETTOYAGE MOT OCR
# ============================================================

def _nettoyer_mot(mot):

    if not mot:
        return ""

    mot = str(mot).strip()

    mot = mot.strip(
        "|¦:;,. "
    )

    return mot


# ============================================================
# REGROUPEMENT DES MOTS PAR LIGNE
# ============================================================

def _regrouper_mots_par_ligne(
    mots,
    tolerance_y=15
):
    """
    Regroupe les mots ayant une position verticale proche.

    Cela permet de reconstituer des lignes à partir des
    coordonnées fournies par Tesseract.
    """

    lignes = []

    mots_tries = sorted(
        mots,
        key=lambda mot: (
            mot["y"],
            mot["x"]
        )
    )

    for mot in mots_tries:

        ajoute = False

        centre_y = (
            mot["y"]
            + mot["hauteur"] / 2
        )

        for ligne in lignes:

            if abs(
                centre_y
                - ligne["centre_y"]
            ) <= tolerance_y:

                ligne["mots"].append(
                    mot
                )

                centres = [
                    m["y"]
                    + m["hauteur"] / 2
                    for m in ligne["mots"]
                ]

                ligne["centre_y"] = (
                    sum(centres)
                    / len(centres)
                )

                ajoute = True
                break

        if not ajoute:

            lignes.append({
                "centre_y": centre_y,
                "mots": [mot]
            })

    # --------------------------------------------------------
    # Tri horizontal des mots
    # --------------------------------------------------------

    for ligne in lignes:

        ligne["mots"] = sorted(
            ligne["mots"],
            key=lambda mot: mot["x"]
        )

        ligne["texte"] = " ".join(
            _nettoyer_mot(
                mot["texte"]
            )
            for mot in ligne["mots"]
            if _nettoyer_mot(
                mot["texte"]
            )
        )

        ligne["x_min"] = min(
            mot["x"]
            for mot in ligne["mots"]
        )

        ligne["x_max"] = max(
            mot["x"]
            + mot["largeur"]
            for mot in ligne["mots"]
        )

    lignes.sort(
        key=lambda ligne: ligne["centre_y"]
    )

    return lignes


# ============================================================
# RECONSTRUCTION DES COLONNES DU FORMULAIRE
# ============================================================

def _extraire_formulaire_par_coordonnees(
    mots
):
    """
    Reconstruit les trois informations principales
    du formulaire à partir des coordonnées OCR.

    Structure attendue :

        COLONNE GAUCHE
        Nom de l'entreprise
        COLAS
        Intitulé du poste
        OUVRIER VRD CONDUCTEUR D ENGINS

        COLONNE DROITE
        Liste des tâches proposées
        Maçonnerie VRD
        Pose de bordures
        Pose de tuyaux
        Réglage et nivellement divers matériaux
    """

    resultat = {
        "entreprise": "",
        "poste": "",
        "taches": "",
        "entreprise_trouvee": False,
        "poste_trouve": False,
        "taches_trouvees": False,
    }

    if not mots:
        return resultat

    lignes = _regrouper_mots_par_ligne(
        mots
    )

    if not lignes:
        return resultat

    # ========================================================
    # RECHERCHE DES MOTS-CLÉS
    # ========================================================

    index_entreprise = None
    index_taches = None
    index_poste = None

    for index, ligne in enumerate(lignes):

        texte = _normaliser_ligne(
            ligne["texte"]
        )

        if (
            index_entreprise is None
            and "nom de l'entreprise"
            in texte
        ):
            index_entreprise = index

        if (
            index_taches is None
            and (
                "liste des tâches proposées"
                in texte
                or (
                    "liste des taches proposées"
                    in texte
                )
            )
        ):
            index_taches = index

        if (
            index_poste is None
            and _est_libelle_poste(
                ligne["texte"]
            )
        ):
            index_poste = index

    # ========================================================
    # DÉTERMINATION DU MILIEU DE LA PAGE
    # ========================================================

    x_global_min = min(
        mot["x"]
        for mot in mots
    )

    x_global_max = max(
        mot["x"]
        + mot["largeur"]
        for mot in mots
    )

    milieu = (
        x_global_min
        + (
            x_global_max
            - x_global_min
        ) / 2
    )

    # ========================================================
    # ENTREPRISE
    # ========================================================

    if index_entreprise is not None:

        ligne_entete = lignes[
            index_entreprise
        ]

        # --------------------------------------------
        # Cherche les mots situés dans la colonne
        # gauche et immédiatement sous le libellé.
        # --------------------------------------------

        y_entete = (
            ligne_entete["centre_y"]
        )

        candidats = []

        for ligne in lignes:

            if (
                ligne["centre_y"]
                <= y_entete
            ):
                continue

            if (
                ligne["centre_y"]
                > y_entete + 180
            ):
                continue

            # Colonne gauche
            if ligne["x_min"] < milieu:

                texte = ligne["texte"].strip()

                if not texte:
                    continue

                if _est_libelle_poste(
                    texte
                ):
                    continue

                if _est_libelle_taches(
                    texte
                ):
                    continue

                if (
                    "habilitations"
                    in texte.lower()
                ):
                    continue

                candidats.append(
                    (
                        ligne["centre_y"],
                        texte
                    )
                )

        if candidats:

            candidats.sort(
                key=lambda element:
                element[0]
            )

            resultat["entreprise"] = (
                candidats[0][1]
            )

            resultat[
                "entreprise_trouvee"
            ] = True

    # ========================================================
    # POSTE
    # ========================================================

    if index_poste is not None:

        ligne_poste = lignes[
            index_poste
        ]

        y_poste = (
            ligne_poste["centre_y"]
        )

        candidats = []

        for ligne in lignes:

            if (
                ligne["centre_y"]
                <= y_poste
            ):
                continue

            if (
                ligne["centre_y"]
                > y_poste + 180
            ):
                continue

            # Le poste est dans la colonne gauche.
            if ligne["x_min"] < milieu:

                texte = ligne["texte"].strip()

                if not texte:
                    continue

                if _est_libelle_taches(
                    texte
                ):
                    continue

                if _est_libelle_entreprise(
                    texte
                ):
                    continue

                if (
                    "habilitations"
                    in texte.lower()
                    or "risques"
                    in texte.lower()
                ):
                    continue

                candidats.append(
                    (
                        ligne["centre_y"],
                        texte
                    )
                )

        if candidats:

            candidats.sort(
                key=lambda element:
                element[0]
            )

            # ------------------------------------------------
            # On recherche de préférence une ligne suffisamment
            # longue pour être un véritable intitulé.
            # ------------------------------------------------

            for _, candidat in candidats:

                if len(candidat) >= 10:

                    resultat["poste"] = (
                        candidat
                    )

                    resultat[
                        "poste_trouve"
                    ] = True

                    break

            if not resultat["poste_trouve"]:

                resultat["poste"] = (
                    candidats[0][1]
                )

                resultat[
                    "poste_trouve"
                ] = True

    # ========================================================
    # TÂCHES
    # ========================================================

    if index_taches is not None:

        ligne_taches = lignes[
            index_taches
        ]

        y_taches = (
            ligne_taches["centre_y"]
        )

        taches = []

        for ligne in lignes:

            if (
                ligne["centre_y"]
                <= y_taches
            ):
                continue

            # Zone raisonnable sous le titre.
            if (
                ligne["centre_y"]
                > y_taches + 220
            ):
                continue

            # Colonne droite.
            if ligne["x_min"] >= milieu:

                texte = ligne["texte"].strip()

                if not texte:
                    continue

                texte_bas = texte.lower()

                # On ignore les éléments manifestement
                # étrangers aux tâches.
                if (
                    "intitulé du poste"
                    in texte_bas
                    or "intitule du poste"
                    in texte_bas
                    or "habilitations"
                    in texte_bas
                    or "risques"
                    in texte_bas
                    or "conditions particulières"
                    in texte_bas
                    or "vip" in texte_bas
                    or "sir" in texte_bas
                ):
                    continue

                # On élimine les lignes très courtes
                # ou manifestement parasites.
                if len(texte) < 4:
                    continue

                # On élimine certaines erreurs OCR connues.
                if (
                    texte_bas.startswith(
                        "dre panne"
                    )
                    or texte_bas.startswith(
                        "!"
                    )
                    or texte_bas.startswith(
                        "="
                    )
                    or texte_bas.startswith(
                        "sondtons"
                    )
                ):
                    continue

                taches.append(
                    texte
                )

        # ----------------------------------------------------
        # Les tâches utiles du formulaire se trouvent au début
        # de cette zone.
        # ----------------------------------------------------

        taches_finales = []

        for tache in taches:

            if tache in taches_finales:
                continue

            taches_finales.append(
                tache
            )

        # Quatre premières tâches maximum.
        taches_finales = (
            taches_finales[:4]
        )

        if taches_finales:

            resultat["taches"] = (
                ", ".join(
                    taches_finales
                )
            )

            resultat[
                "taches_trouvees"
            ] = True

    return resultat


# ============================================================
# EXTRACTION CIBLÉE
# ============================================================

def extraire_fiche_poste_ciblee(
    texte
):
    """
    Extrait :

    - entreprise
    - poste
    - tâches

    Pour le texte déjà extrait, cette fonction conserve
    une méthode classique de secours.

    L'OCR avec coordonnées est utilisé par la fonction
    dédiée lorsqu'il est disponible.
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

    lignes = [
        ligne.strip()
        for ligne in texte.split("\n")
        if ligne.strip()
    ]

    # ========================================================
    # RECHERCHE CLASSIQUE ENTREPRISE
    # ========================================================

    for index, ligne in enumerate(lignes):

        if _est_libelle_entreprise(
            ligne
        ):

            # Valeur éventuellement sur la même ligne.
            valeur = re.sub(
                r".*nom\s+de\s+l['’]?entreprise\s*:?",
                "",
                ligne,
                flags=re.IGNORECASE
            ).strip()

            valeur = _nettoyer_mot(
                valeur
            )

            if valeur:

                resultat["entreprise"] = (
                    valeur
                )

                resultat[
                    "entreprise_trouvee"
                ] = True

            else:

                # Cherche la valeur suivante.
                for suivant in range(
                    index + 1,
                    min(
                        index + 4,
                        len(lignes)
                    )
                ):

                    candidat = (
                        lignes[suivant]
                        .strip()
                    )

                    if not candidat:
                        continue

                    morceaux = [
                        _nettoyer_mot(m)
                        for m in candidat.split("|")
                        if m.strip()
                    ]

                    if morceaux:

                        valeur = morceaux[0]

                        if (
                            valeur
                            and not _est_libelle_poste(
                                valeur
                            )
                            and not _est_libelle_taches(
                                valeur
                            )
                        ):

                            resultat[
                                "entreprise"
                            ] = valeur

                            resultat[
                                "entreprise_trouvee"
                            ] = True

                            break

            break

    # ========================================================
    # RECHERCHE CLASSIQUE POSTE
    # ========================================================

    for index, ligne in enumerate(lignes):

        if _est_libelle_poste(
            ligne
        ):

            # ------------------------------------------------
            # Valeur sur la même ligne
            # ------------------------------------------------

            motifs = [
                r"intitul[ée]?\s+du\s+poste\s*:?",
                r"linie\s+du\s+poste\s*:?",
                r"linte\s+du\s+poste\s*:?",
            ]

            valeur = ""

            for motif in motifs:

                valeur = _extraire_apres_texte(
                    ligne,
                    motif
                )

                if valeur:
                    break

            if valeur:

                resultat["poste"] = (
                    valeur
                )

                resultat[
                    "poste_trouve"
                ] = True

            else:

                # ------------------------------------------------
                # Recherche sur les lignes suivantes
                # ------------------------------------------------

                for suivant in range(
                    index + 1,
                    min(
                        index + 5,
                        len(lignes)
                    )
                ):

                    candidat = (
                        lignes[suivant]
                        .strip()
                    )

                    if not candidat:
                        continue

                    if _est_libelle_taches(
                        candidat
                    ):
                        continue

                    if (
                        "habilitations"
                        in candidat.lower()
                    ):
                        break

                    morceaux = [
                        _nettoyer_mot(m)
                        for m in candidat.split("|")
                        if m.strip()
                    ]

                    if len(morceaux) == 1:

                        if len(
                            morceaux[0]
                        ) >= 4:

                            resultat[
                                "poste"
                            ] = morceaux[0]

                            resultat[
                                "poste_trouve"
                            ] = True

                            break

            break

    # ========================================================
    # RECHERCHE CLASSIQUE TÂCHES
    # ========================================================

    for index, ligne in enumerate(lignes):

        if _est_libelle_taches(
            ligne
        ):

            taches = []

            for suivant in range(
                index + 1,
                min(
                    index + 8,
                    len(lignes)
                )
            ):

                candidat = (
                    lignes[suivant]
                    .strip()
                )

                if not candidat:
                    continue

                if _est_libelle_poste(
                    candidat
                ):
                    break

                morceaux = [
                    _nettoyer_mot(m)
                    for m in candidat.split("|")
                    if m.strip()
                ]

                for morceau in morceaux:

                    if len(morceau) >= 4:

                        texte_bas = (
                            morceau.lower()
                        )

                        if (
                            "habilitation"
                            in texte_bas
                            or "risque"
                            in texte_bas
                            or "conditions particulières"
                            in texte_bas
                        ):
                            continue

                        taches.append(
                            morceau
                        )

            # Suppression doublons.
            taches = list(
                dict.fromkeys(
                    taches
                )
            )

            if taches:

                resultat["taches"] = (
                    ", ".join(
                        taches[:4]
                    )
                )

                resultat[
                    "taches_trouvees"
                ] = True

            break

    return resultat


# ============================================================
# PETITE FONCTION UTILITAIRE
# ============================================================

def _extraire_apres_texte(
    ligne,
    motif
):

    resultat = re.search(
        motif,
        ligne,
        flags=re.IGNORECASE
    )

    if not resultat:
        return ""

    valeur = ligne[
        resultat.end():
    ]

    valeur = valeur.strip()

    valeur = valeur.lstrip(
        ":|¦ "
    )

    return _nettoyer_mot(
        valeur
    )


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
```
