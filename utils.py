import re
import pdfplumber
import docx


# ============================================================
# NETTOYAGE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoyage léger du texte.

    IMPORTANT :
    On conserve les retours à la ligne car ils sont indispensables
    pour identifier correctement les rubriques d'une fiche de poste.
    """

    if not texte:
        return ""

    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")

    # Nettoyage des espaces en fin de ligne
    lignes = []

    for ligne in texte.split("\n"):

        ligne = re.sub(
            r"[ \t]+",
            " ",
            ligne,
        ).strip()

        lignes.append(ligne)

    # Réduction des lignes vides successives
    resultat = []
    ligne_vide_precedente = False

    for ligne in lignes:

        if not ligne:

            if not ligne_vide_precedente:
                resultat.append("")

            ligne_vide_precedente = True

        else:

            resultat.append(ligne)
            ligne_vide_precedente = False

    return "\n".join(resultat).strip()


# ============================================================
# EXTRACTION PDF
# ============================================================

def extraire_texte_pdf(file):
    """
    Extrait le texte d'un PDF en conservant les retours à la ligne.

    Si le PDF est scanné et ne contient pas de couche texte,
    pdfplumber retournera peu ou pas de texte.
    """

    texte_pages = []

    with pdfplumber.open(file) as pdf:

        for page in pdf.pages:

            texte_page = page.extract_text(
                x_tolerance=2,
                y_tolerance=3,
            )

            if texte_page:
                texte_pages.append(
                    texte_page
                )

    return "\n".join(
        texte_pages
    )


# ============================================================
# EXTRACTION WORD
# ============================================================

def extraire_texte_docx(file):
    """
    Extrait le texte d'un Word.

    On conserve la structure :
    - paragraphes ;
    - lignes des tableaux ;
    - cellules des tableaux.

    C'est important pour les fiches de poste qui utilisent
    des tableaux.
    """

    document = docx.Document(file)

    morceaux = []

    # --------------------------------------------------------
    # PARAGRAPHES
    # --------------------------------------------------------

    for paragraphe in document.paragraphs:

        texte = paragraphe.text.strip()

        if texte:

            morceaux.append(
                texte
            )

    # --------------------------------------------------------
    # TABLEAUX
    # --------------------------------------------------------

    for table in document.tables:

        for ligne in table.rows:

            cellules = []

            for cellule in ligne.cells:

                texte_cellule = cellule.text.strip()

                cellules.append(
                    texte_cellule
                )

            # On conserve les cellules sur une même ligne
            # avec une séparation claire.
            if any(cellules):

                morceaux.append(
                    " | ".join(
                        cellules
                    )
                )

    return "\n".join(
        morceaux
    )


# ============================================================
# EXTRACTION GENERALE
# ============================================================

def extract_text(file):
    """
    Extrait le texte d'un fichier PDF ou DOCX.

    Le texte est volontairement conservé avec ses retours
    à la ligne afin de permettre une lecture structurée.
    """

    nom_fichier = getattr(
        file,
        "name",
        "",
    ) or ""

    nom_fichier_min = nom_fichier.lower()

    if nom_fichier_min.endswith(
        ".docx"
    ):

        texte = extraire_texte_docx(
            file
        )

    elif nom_fichier_min.endswith(
        ".pdf"
    ):

        texte = extraire_texte_pdf(
            file
        )

    else:

        texte = ""

    return nettoyer_texte(
        texte
    )


# ============================================================
# NORMALISATION POUR RECHERCHE DES RUBRIQUES
# ============================================================

def _normaliser_libelle(texte):
    """
    Normalise uniquement pour comparer les intitulés
    de rubriques.

    Exemple :
    "Liste des tâches proposées"
    devient :
    "liste des taches proposees"
    """

    if not texte:
        return ""

    texte = texte.lower()

    remplacements = {
        "à": "a",
        "â": "a",
        "ä": "a",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "î": "i",
        "ï": "i",
        "ô": "o",
        "ö": "o",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c",
    }

    for ancien, nouveau in remplacements.items():

        texte = texte.replace(
            ancien,
            nouveau,
        )

    texte = re.sub(
        r"\s+",
        " ",
        texte,
    )

    texte = re.sub(
        r"[:\-]+$",
        "",
        texte,
    )

    return texte.strip()


# ============================================================
# RECHERCHE D'UNE RUBRIQUE
# ============================================================

def _ligne_correspond_a_un_libelle(
    ligne,
    libelles,
):
    """
    Vérifie si une ligne correspond à un des libellés recherchés.

    Accepte :
        Nom de l'entreprise
        Nom de l'entreprise :
        NOM DE L'ENTREPRISE
    """

    ligne_normalisee = _normaliser_libelle(
        ligne
    )

    for libelle in libelles:

        libelle_normalise = _normaliser_libelle(
            libelle
        )

        if ligne_normalisee == libelle_normalise:

            return True

        # Accepte également "libellé :"
        if ligne_normalisee.rstrip(":") == libelle_normalise:

            return True

    return False


# ============================================================
# EXTRACTION D'UNE RUBRIQUE
# ============================================================

def _extraire_valeur_apres_libelle(
    lignes,
    index,
    libelles,
    autres_rubriques,
):
    """
    Cherche la valeur située après une rubrique.

    Cas 1 :
        Nom de l'entreprise
        DUPONT

    Cas 2 :
        Nom de l'entreprise : DUPONT

    Cas 3 dans un tableau :
        Nom de l'entreprise | DUPONT

    On s'arrête dès qu'une nouvelle rubrique connue apparaît.
    """

    ligne = lignes[index]

    ligne_normalisee = _normaliser_libelle(
        ligne
    )

    # --------------------------------------------------------
    # CAS 1 : LIBELLE ET VALEUR SUR LA MEME LIGNE
    # --------------------------------------------------------

    for libelle in libelles:

        libelle_normalise = _normaliser_libelle(
            libelle
        )

        # Recherche "libellé : valeur"
        motif = (
            r"^\s*"
            + re.escape(
                libelle_normalise
            )
            + r"\s*[:\-]\s*(.+?)\s*$"
        )

        # On travaille sur une version normalisée uniquement
        # pour détecter la structure.
        ligne_test = _normaliser_libelle(
            ligne
        )

        correspondance = re.match(
            motif,
            ligne_test,
            flags=re.IGNORECASE,
        )

        if correspondance:

            valeur = correspondance.group(
                1
            ).strip()

            if valeur:

                return valeur

    # --------------------------------------------------------
    # CAS 2 : TABLEAU "LIBELLE | VALEUR"
    # --------------------------------------------------------

    if "|" in ligne:

        morceaux = [
            morceau.strip()
            for morceau in ligne.split("|")
        ]

        for position, morceau in enumerate(
            morceaux
        ):

            if _ligne_correspond_a_un_libelle(
                morceau,
                libelles,
            ):

                if position + 1 < len(
                    morceaux
                ):

                    valeur = morceaux[
                        position + 1
                    ].strip()

                    if valeur:

                        return valeur

    # --------------------------------------------------------
    # CAS 3 : VALEUR SUR LA LIGNE SUIVANTE
    # --------------------------------------------------------

    valeurs = []

    for j in range(
        index + 1,
        min(
            index + 20,
            len(lignes),
        ),
    ):

        suivante = lignes[j].strip()

        if not suivante:

            if valeurs:
                break

            continue

        # Si on rencontre une autre rubrique,
        # on s'arrête.
        if _ligne_correspond_a_un_libelle(
            suivante,
            autres_rubriques,
        ):

            break

        # Dans un tableau, on peut avoir :
        # "Nom entreprise | DUPONT"
        if "|" in suivante:

            morceaux = [
                morceau.strip()
                for morceau in suivante.split("|")
            ]

            # On prend les cellules non vides
            # comme valeur potentielle.
            morceaux = [
                morceau
                for morceau in morceaux
                if morceau
            ]

            if morceaux:

                valeurs.extend(
                    morceaux
                )

        else:

            valeurs.append(
                suivante
            )

        # Pour entreprise et intitulé,
        # une ou deux lignes suffisent normalement.
        if len(valeurs) >= 2:

            break

    if valeurs:

        return " / ".join(
            valeurs
        ).strip()

    return ""


# ============================================================
# EXTRACTION CIBLEE FICHE DE POSTE
# ============================================================

def extraire_fiche_poste_ciblee(
    texte,
):
    """
    Extraction volontairement simple d'une fiche de poste.

    L'application cherche UNIQUEMENT :

    1. Nom de l'entreprise
    2. Intitulé du poste
    3. Liste des tâches proposées

    Elle ne tente PAS de deviner l'entreprise,
    le poste ou les compétences.

    Retourne :

    {
        "entreprise": "...",
        "poste": "...",
        "taches": "...",
        "entreprise_trouvee": True/False,
        "poste_trouve": True/False,
        "taches_trouvees": True/False
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

    lignes = texte.splitlines()

    # --------------------------------------------------------
    # RUBRIQUES EXACTES DU MODELE
    # --------------------------------------------------------

    libelles_entreprise = [
        "Nom de l'entreprise",
        "Nom de l'entreprise :",
        "Entreprise cliente",
        "Nom entreprise",
    ]

    libelles_poste = [
        "Intitulé du poste",
        "Intitulé du poste :",
    ]

    libelles_taches = [
        "Liste des tâches proposées",
        "Liste des tâches proposées :",
        "Liste des tâches à proposer",
        "Liste des tâches à proposer :",
    ]

    toutes_rubriques = (
        libelles_entreprise
        + libelles_poste
        + libelles_taches
        + [
            "Habilitations, certificats et diplômes obligatoires",
            "Conduite d'engins",
            "Utilisation de machines / outils",
            "Conditions de travail liées au poste",
            "Sécurité",
            "Risques",
        ]
    )

    # --------------------------------------------------------
    # ENTREPRISE
    # --------------------------------------------------------

    for i, ligne in enumerate(
        lignes
    ):

        if _ligne_correspond_a_un_libelle(
            ligne,
            libelles_entreprise,
        ):

            valeur = _extraire_valeur_apres_libelle(
                lignes,
                i,
                libelles_entreprise,
                toutes_rubriques,
            )

            if valeur:

                resultat[
                    "entreprise"
                ] = valeur

                resultat[
                    "entreprise_trouvee"
                ] = True

                break

    # --------------------------------------------------------
    # POSTE
    # --------------------------------------------------------

    for i, ligne in enumerate(
        lignes
    ):

        if _ligne_correspond_a_un_libelle(
            ligne,
            libelles_poste,
        ):

            valeur = _extraire_valeur_apres_libelle(
                lignes,
                i,
                libelles_poste,
                toutes_rubriques,
            )

            if valeur:

                resultat[
                    "poste"
                ] = valeur

                resultat[
                    "poste_trouve"
                ] = True

                break

    # --------------------------------------------------------
    # TACHES
    # --------------------------------------------------------

    for i, ligne in enumerate(
        lignes
    ):

        if _ligne_correspond_a_un_libelle(
            ligne,
            libelles_taches,
        ):

            valeurs = []

            # ------------------------------------------------
            # Même ligne
            # ------------------------------------------------

            if "|" in ligne:

                morceaux = [
                    morceau.strip()
                    for morceau in ligne.split("|")
                ]

                for position, morceau in enumerate(
                    morceaux
                ):

                    if _ligne_correspond_a_un_libelle(
                        morceau,
                        libelles_taches,
                    ):

                        valeurs.extend(
                            morceaux[
                                position + 1:
                            ]
                        )

                        break

            # ------------------------------------------------
            # Lignes suivantes
            # ------------------------------------------------

            for j in range(
                i + 1,
                len(lignes),
            ):

                suivante = lignes[
                    j
                ].strip()

                if not suivante:

                    if valeurs:

                        break

                    continue

                # Nouvelle rubrique =
                # fin de la liste des tâches.
                if _ligne_correspond_a_un_libelle(
                    suivante,
                    toutes_rubriques,
                ):

                    break

                # Les tâches peuvent être :
                # - une par ligne
                # - plusieurs dans une cellule
                if "|" in suivante:

                    morceaux = [
                        morceau.strip()
                        for morceau in suivante.split("|")
                        if morceau.strip()
                    ]

                    valeurs.extend(
                        morceaux
                    )

                else:

                    valeurs.append(
                        suivante
                    )

            # Nettoyage des tâches
            propres = []

            for valeur in valeurs:

                valeur = valeur.strip()

                if not valeur:
                    continue

                if valeur in propres:
                    continue

                propres.append(
                    valeur
                )

            if propres:

                resultat[
                    "taches"
                ] = "\n".join(
                    propres
                )

                resultat[
                    "taches_trouvees"
                ] = True

            break

    return resultat


# ============================================================
# PRESENTATION CANDIDAT
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
