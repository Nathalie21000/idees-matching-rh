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

    Le texte conserve les retours à la ligne afin de permettre
    l'analyse précise des rubriques de la fiche de poste.
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
    Extrait le contenu d'un document Word.

    IMPORTANT :
    Les cellules des tableaux sont volontairement séparées
    par des retours à la ligne et NON par " | ".

    Cela permet de conserver la structure :

        Nom de l'entreprise
        ABC ENTREPRISE

        Intitulé du poste
        Préparateur de commandes

        Liste des tâches proposées
        Tâche 1
        Tâche 2
        Tâche 3
    """

    morceaux = []

    try:

        document = docx.Document(file)

        # ----------------------------------------------------
        # PARAGRAPHES
        # ----------------------------------------------------

        for paragraphe in document.paragraphs:

            texte = paragraphe.text.strip()

            if texte:
                morceaux.append(texte)

        # ----------------------------------------------------
        # TABLEAUX
        # ----------------------------------------------------

        for table in document.tables:

            for ligne in table.rows:

                for cellule in ligne.cells:

                    texte_cellule = cellule.text.strip()

                    if texte_cellule:

                        # On conserve les lignes présentes
                        # dans chaque cellule.
                        lignes_cellule = texte_cellule.splitlines()

                        for ligne_cellule in lignes_cellule:

                            ligne_cellule = ligne_cellule.strip()

                            if ligne_cellule:
                                morceaux.append(ligne_cellule)

    except Exception:
        return ""

    return "\n".join(morceaux)


# ============================================================
# NETTOYAGE DU TEXTE
# ============================================================

def nettoyer_texte(texte):
    """
    Nettoyage léger du texte.

    Les retours à la ligne sont volontairement conservés.
    """

    if not texte:
        return ""

    texte = texte.replace("\r\n", "\n")
    texte = texte.replace("\r", "\n")
    texte = texte.replace("\xa0", " ")

    # Nettoyage des espaces sans supprimer les lignes
    texte = re.sub(r"[ \t]+", " ", texte)

    # Nettoyage des lignes vides multiples
    texte = re.sub(r"\n\s*\n+", "\n\n", texte)

    return texte.strip()


# ============================================================
# NORMALISATION POUR COMPARER LES LIBELLES
# ============================================================

def _normaliser_ligne(ligne):
    """
    Normalise une ligne uniquement pour la comparaison
    des intitulés de rubriques.

    Exemple :

    "Liste des tâches proposées :"
    devient :
    "liste des taches proposees"
    """

    if not ligne:
        return ""

    ligne = ligne.lower().strip()

    # Accents
    remplacements = {
        "à": "a",
        "â": "a",
        "ä": "a",
        "á": "a",
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
        "ÿ": "y",
        "ç": "c",
        "œ": "oe",
    }

    for ancien, nouveau in remplacements.items():
        ligne = ligne.replace(ancien, nouveau)

    ligne = re.sub(r"[^a-z0-9 ]", " ", ligne)
    ligne = re.sub(r"\s+", " ", ligne)

    return ligne.strip()


# ============================================================
# RECONNAISSANCE DES LIBELLES
# ============================================================

def _est_libelle_entreprise(ligne):
    """
    Reconnaît les différentes formes possibles du libellé
    entreprise.
    """

    normalisee = _normaliser_ligne(ligne)

    formes = [
        "nom de l entreprise",
        "nom de entreprise",
        "entreprise",
        "entreprise cliente",
        "nom entreprise",
    ]

    return normalisee in formes


def _est_libelle_poste(ligne):
    """
    Reconnaît le libellé exact de l'intitulé du poste.
    """

    normalisee = _normaliser_ligne(ligne)

    formes = [
        "intitule du poste",
        "intitule poste",
        "poste",
    ]

    return normalisee in formes


def _est_libelle_taches(ligne):
    """
    Reconnaît notamment le libellé utilisé dans la fiche
    ID'EES :

        Liste des tâches proposées
    """

    normalisee = _normaliser_ligne(ligne)

    formes = [
        "liste des taches proposees",
        "liste des taches a proposer",
        "liste taches proposees",
        "liste taches a proposer",
        "taches proposees",
        "taches a proposer",
        "liste des taches",
    ]

    return normalisee in formes


# ============================================================
# AUTRES RUBRIQUES QUI PEUVENT TERMINER LA LISTE DES TÂCHES
# ============================================================

def _est_autre_rubrique(ligne):
    """
    Détecte les rubriques qui apparaissent généralement
    après la liste des tâches.

    Cela évite de récupérer toute la fiche de poste
    dans "Tâches à réaliser".
    """

    normalisee = _normaliser_ligne(ligne)

    rubriques = [
        "conditions de travail",
        "conditions de travail liees au poste",
        "competences",
        "competences requises",
        "profil",
        "profil recherche",
        "profil recherche",
        "qualification",
        "qualifications",
        "formation",
        "experience",
        "experiences",
        "horaires",
        "remuneration",
        "salaire",
        "avantages",
        "lieu de travail",
        "adresse",
        "type de contrat",
        "contrat",
        "duree du contrat",
        "date de debut",
        "date de debut souhaitee",
        "permis",
        "caces",
        "habilitation",
        "suivi medical",
        "vip",
        "sir",
    ]

    return normalisee in rubriques


# ============================================================
# EXTRAIRE VALEUR APRES UN LIBELLE
# ============================================================

def _valeur_apres_libelle_meme_ligne(ligne, type_libelle):
    """
    Permet de gérer un document où le libellé et la valeur
    sont sur la même ligne.

    Exemple :

        Nom de l'entreprise : ABC

    ou :

        Intitulé du poste : Préparateur de commandes
    """

    if not ligne:
        return ""

    if type_libelle == "entreprise":

        motifs = [
            r"nom\s+de\s+l['’]entreprise\s*[:\-]\s*(.+)$",
            r"nom\s+de\s+l['’]\s+entreprise\s*[:\-]\s*(.+)$",
            r"entreprise\s+cliente\s*[:\-]\s*(.+)$",
        ]

    elif type_libelle == "poste":

        motifs = [
            r"intitul[ée]\s+du\s+poste\s*[:\-]\s*(.+)$",
            r"intitul[ée]\s+poste\s*[:\-]\s*(.+)$",
        ]

    else:

        motifs = [
            r"liste\s+des\s+t[âa]ches\s+propos[ée]es\s*[:\-]\s*(.+)$",
            r"liste\s+des\s+t[âa]ches\s+a\s+proposer\s*[:\-]\s*(.+)$",
        ]

    for motif in motifs:

        correspondance = re.search(
            motif,
            ligne,
            flags=re.IGNORECASE,
        )

        if correspondance:

            valeur = correspondance.group(1).strip()

            if valeur:
                return valeur

    return ""


# ============================================================
# RECHERCHE D'UN LIBELLE
# ============================================================

def _trouver_ligne_libelle(lignes, type_libelle):
    """
    Retourne l'index de la ligne contenant le libellé.
    """

    for index, ligne in enumerate(lignes):

        if type_libelle == "entreprise":

            if _est_libelle_entreprise(ligne):
                return index

        elif type_libelle == "poste":

            if _est_libelle_poste(ligne):
                return index

        elif type_libelle == "taches":

            if _est_libelle_taches(ligne):
                return index

    return None


# ============================================================
# CAPTURE D'UNE VALEUR APRES UN LIBELLE
# ============================================================

def _capturer_valeur(lignes, index, type_libelle):
    """
    Capture la valeur située après un libellé.

    Fonctionne dans les deux cas :

    1. Libellé puis valeur sur la ligne suivante.
    2. Libellé et valeur sur la même ligne.
    """

    if index is None:
        return []

    # --------------------------------------------------------
    # CAS : valeur présente sur la même ligne
    # --------------------------------------------------------

    valeur_meme_ligne = _valeur_apres_libelle_meme_ligne(
        lignes[index],
        type_libelle,
    )

    if valeur_meme_ligne:

        return [valeur_meme_ligne]

    # --------------------------------------------------------
    # CAS : valeur sur les lignes suivantes
    # --------------------------------------------------------

    valeurs = []

    for position in range(index + 1, len(lignes)):

        ligne = lignes[position].strip()

        if not ligne:
            continue

        # Si une nouvelle rubrique ciblée apparaît,
        # on s'arrête.
        if (
            _est_libelle_entreprise(ligne)
            or _est_libelle_poste(ligne)
            or _est_libelle_taches(ligne)
        ):
            break

        # Pour les tâches, on s'arrête aussi devant
        # une rubrique suivante classique.
        if (
            type_libelle == "taches"
            and _est_autre_rubrique(ligne)
        ):
            break

        valeurs.append(ligne)

        # ----------------------------------------------------
        # ENTREPRISE
        # ----------------------------------------------------

        if type_libelle == "entreprise":

            # Une seule ligne suffit.
            break

        # ----------------------------------------------------
        # POSTE
        # ----------------------------------------------------

        if type_libelle == "poste":

            # Une seule ligne suffit.
            break

        # ----------------------------------------------------
        # TÂCHES
        # ----------------------------------------------------

        if type_libelle == "taches":

            # On continue volontairement pour récupérer
            # toutes les tâches, même s'il y a 3, 4, 5...
            # lignes.
            if len(valeurs) >= 30:
                break

    return valeurs


# ============================================================
# EXTRACTION CIBLEE DE LA FICHE DE POSTE
# ============================================================

def extraire_fiche_poste_ciblee(texte):
    """
    Extrait UNIQUEMENT les trois informations importantes :

    - nom de l'entreprise ;
    - intitulé du poste ;
    - liste complète des tâches proposées.

    Aucun métier ou compétence n'est deviné ici.

    Retour :

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

    # --------------------------------------------------------
    # Préparation des lignes
    # --------------------------------------------------------

    lignes = []

    for ligne in texte.split("\n"):

        ligne = ligne.strip()

        if ligne:
            lignes.append(ligne)

    if not lignes:
        return resultat

    # --------------------------------------------------------
    # RECHERCHE DES 3 RUBRIQUES
    # --------------------------------------------------------

    index_entreprise = _trouver_ligne_libelle(
        lignes,
        "entreprise",
    )

    index_poste = _trouver_ligne_libelle(
        lignes,
        "poste",
    )

    index_taches = _trouver_ligne_libelle(
        lignes,
        "taches",
    )

    # --------------------------------------------------------
    # ENTREPRISE
    # --------------------------------------------------------

    valeurs_entreprise = _capturer_valeur(
        lignes,
        index_entreprise,
        "entreprise",
    )

    if valeurs_entreprise:

        resultat["entreprise"] = (
            valeurs_entreprise[0].strip()
        )

        resultat["entreprise_trouvee"] = True

    # --------------------------------------------------------
    # POSTE
    # --------------------------------------------------------

    valeurs_poste = _capturer_valeur(
        lignes,
        index_poste,
        "poste",
    )

    if valeurs_poste:

        resultat["poste"] = (
            valeurs_poste[0].strip()
        )

        resultat["poste_trouve"] = True

    # --------------------------------------------------------
    # TÂCHES
    # --------------------------------------------------------

    valeurs_taches = _capturer_valeur(
        lignes,
        index_taches,
        "taches",
    )

    if valeurs_taches:

        # Nettoyage des lignes
        taches_propres = []

        for tache in valeurs_taches:

            tache = tache.strip()

            if not tache:
                continue

            # Évite les doublons exacts
            if tache not in taches_propres:
                taches_propres.append(tache)

        resultat["taches"] = ", ".join(
            taches_propres
        )

        resultat["taches_trouvees"] = bool(
            taches_propres
        )

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
    agence,
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
