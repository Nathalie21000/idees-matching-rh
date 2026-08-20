            if not poste_detecte:
                st.warning(
                    "La rubrique « Intitulé du poste » n'a pas été "
                    "identifiée automatiquement."
                )

            if not taches_detectees:
                st.warning(
                    "La rubrique « Liste des tâches à proposer » n'a pas "
                    "été identifiée automatiquement."
                )

            with st.form("form_poste"):

                entreprise = st.text_input(
                    "Entreprise cliente",
                    value=entreprise_detectee,
                )

                poste = st.text_input(
                    "Intitulé du poste",
                    value=poste_detecte,
                )

                competences = st.text_area(
                    "Compétences requises",
                    value=competences_detectees,
                    help=(
                        "Cette zone n'est plus remplie à partir des "
                        "mots trouvés dans les intitulés du formulaire."
                    ),
                )

                taches = st.text_area(
                    "Tâches à réaliser",
                    value=taches_detectees,
                    height=180,
                    help=(
                        "Le contenu de « Liste des tâches à proposer » "
                        "est repris directement ici."
                    ),
                )

                caces = st.text_input(
                    "CACES requis",
                    value=caces_detectes,
                )

                permis = st.text_input(
                    "Permis requis",
                    value=permis_detectes,
                )

                choix_vip_sir = ["", "VIP", "SIR", "VIP + SIR"]

                vip_sir = st.selectbox(
                    "Suivi médical requis",
                    choix_vip_sir,
                    index=(
                        choix_vip_sir.index(vip_sir_detecte)
                        if vip_sir_detecte in choix_vip_sir
                        else 0
                    ),
                    help=(
                        "VIP = Visite Infirmier Périodique. "
                        "SIR = Suivi Individuel Renforcé."
                    ),
                )

                valider = st.form_submit_button(
                    "Enregistrer cette fiche de poste"
                )

            if valider:

                if not entreprise or not poste:

                    st.error(
                        "Merci de renseigner au moins "
                        "l'entreprise et l'intitulé du poste."
                    )

                else:

                    try:

                        enregistrer_poste(
                            agence,
                            entreprise,
                            poste,
                            competences,
                            caces,
                            permis,
                            texte,
                            taches,
                            vip_sir,
                        )

                        st.success(
                            f"Fiche de poste « {poste} » enregistrée "
                            f"pour {entreprise}."
                        )

                        st.rerun()

                    except Exception as erreur:

                        st.error(
                            "Erreur lors de l'enregistrement de la fiche de poste."
                        )
                        st.exception(erreur)

            with st.expander("Voir le texte extrait de la fiche de poste"):
                st.text(texte)

            with st.expander("🔧 Voir l'analyse structurée détectée"):
                st.json({
                    "entreprise": analyse.get("entreprise", ""),
                    "intitule": analyse.get("intitule", ""),
                    "taches": analyse.get("taches", ""),
                    "competences": analyse.get("competences", ""),
                    "habilitations": analyse.get("habilitations", ""),
                    "conduite_engins": analyse.get("conduite_engins", ""),
                    "machines_outils": analyse.get("machines_outils", ""),
                    "securite_risques": analyse.get("securite_risques", ""),
                    "vip": analyse.get("vip", False),
                    "sir": analyse.get("sir", False),
                })


# ============================================================
# POSTETHEQUE
# ============================================================

elif page == "📁 Postethèque":

    st.title("📁 Postethèque")

    recherche_poste = st.text_input(
        "🔎 Rechercher une entreprise, un poste, une compétence..."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        filtre_poste_intitule = st.text_input("💼 Intitulé du poste")

    with col2:
        filtre_poste_caces = st.text_input("🚜 CACES")

    with col3:
        filtre_poste_permis = st.text_input("🚗 Permis")

    postes_liste = recuperer_postes(agence)

    if not postes_liste:
        st.info("Aucune fiche de poste enregistrée pour cette agence.")

    else:

        for poste_item in postes_liste:

            poste_id = poste_item.get("id")
            entreprise = poste_item.get("entreprise") or ""
            intitule = poste_item.get("poste") or ""
            competences = poste_item.get("competences") or ""
            taches = poste_item.get("taches") or ""
            vip_sir = poste_item.get("vip_sir") or ""
            caces = poste_item.get("caces") or ""
            permis = poste_item.get("permis") or ""
            date_creation = poste_item.get("date_creation") or ""
            texte_poste = poste_item.get("texte") or ""

            texte_recherche_poste = (
                f"{entreprise} {intitule} {competences} "
                f"{caces} {permis} {texte_poste}"
            ).lower()

            if (
                recherche_poste
                and recherche_poste.lower() not in texte_recherche_poste
            ):
                continue

            if (
                filtre_poste_intitule
                and filtre_poste_intitule.lower() not in intitule.lower()
            ):
                continue

            if (
                filtre_poste_caces
                and filtre_poste_caces.lower() not in caces.lower()
            ):
                continue

            if (
                filtre_poste_permis
                and filtre_poste_permis.lower() not in permis.lower()
            ):
                continue

            with st.expander(f"🏢 {entreprise} — {intitule}"):

                st.write(f"**Entreprise :** {entreprise}")
                st.write(f"**Intitulé du poste :** {intitule}")

                st.write(
                    f"**Compétences requises :** "
                    f"{competences if competences else 'Non renseigné'}"
                )

                st.write(
                    f"**Tâches à réaliser :** "
                    f"{taches if taches else 'Non renseigné'}"
                )

                st.write(
                    f"**CACES requis :** {caces if caces else 'Aucun'}"
                )

                st.write(
                    f"**Permis requis :** "
                    f"{permis if permis else 'Non renseigné'}"
                )

                st.write(
                    f"**Suivi médical :** "
                    f"{vip_sir if vip_sir else 'Non renseigné'}"
                )

                st.caption(f"Ajouté le {date_creation}")

                if texte_poste:
                    with st.expander(
                        "Voir le texte complet de la fiche de poste"
                    ):
                        st.text(texte_poste)

                st.markdown("---")

                if st.button(
                    "🗑️ Supprimer cette fiche de poste",
                    key=f"suppr_poste_{poste_id}",
                ):

                    try:
                        supprimer_poste(poste_id)
                        st.success("Fiche de poste supprimée.")
                        st.rerun()

                    except Exception as erreur:
                        st.error(
                            "Erreur lors de la suppression de la fiche de poste."
                        )
                        st.exception(erreur)


# ============================================================
# MATCHING
# ============================================================

elif page == "🔍 Matching":

    st.title("🔍 Matching CV / Fiches de poste")

    postes = recuperer_postes(agence)
    cvs = recuperer_cvs_matching(agence)

    if not postes:

        st.info(
            "Aucune fiche de poste enregistrée pour cette agence."
        )

    elif not cvs:

        st.info(
            "Aucun CV enregistré pour cette agence."
        )

    else:

        options_postes = {
            f"{p['poste']} — {p['entreprise']}": p["id"]
            for p in postes
        }

        choix_poste = st.selectbox(
            "Choisissez une fiche de poste",
            list(options_postes.keys()),
        )

        poste_id = options_postes[choix_poste]
        poste = recuperer_poste(poste_id)

        if not poste:

            st.error(
                "Impossible de récupérer cette fiche de poste."
            )

        else:

            poste_nom = poste.get("poste") or ""
            entreprise_nom = poste.get("entreprise") or ""

            resultats = []

            for cv in cvs:

                resultat_matching = calculer_score(
                    cv,
                    poste,
                )

                resultats.append(
                    {
                        "cv_id": cv.get("id"),
                        "candidat": cv.get("candidat") or "",
                        "metier": resultat_matching["metier_cv"],
                        "score": resultat_matching["score"],
                        "explication": resultat_matching["explication"],
                    }
                )

            resultats.sort(
                key=lambda r: r["score"],
                reverse=True,
            )

            st.subheader(
                f"Résultats pour : {poste_nom} — {entreprise_nom}"
            )

            for r in resultats:

                with st.expander(
                    f"{r['candidat']} — "
                    f"{r['score']}% de compatibilité "
                    f"({r['metier']})"
                ):

                    st.progress(
                        min(r["score"], 100) / 100
                    )

                    for ligne_explication in r["explication"]:
                        st.write(ligne_explication)

                    st.markdown("---")

                    statut = st.selectbox(
                        "Statut de la candidature",
                        STATUTS_SUIVI,
                        key=f"statut_{r['cv_id']}",
                    )

                    type_entreprise = st.radio(
                        "Type d'entreprise",
                        ["🟢 Client", "🟠 Prospect"],
                        horizontal=True,
                        key=f"type_entreprise_{r['cv_id']}",
                    )

                    if st.button(
                        "Ajouter au suivi",
                        key=f"suivi_{r['cv_id']}",
                    ):

                        try:

                            enregistrer_suivi(
                                agence,
                                r["candidat"],
                                entreprise_nom,
                                poste_nom,
                                statut,
                                type_entreprise,
                            )

                            st.success(
                                "Candidature ajoutée au suivi."
                            )
                            st.rerun()

                        except Exception as erreur:

                            st.error(
                                "Erreur lors de l'ajout au suivi."
                            )
                            st.exception(erreur)

                    st.markdown("---")

                    if st.button(
                        "📧 Générer une présentation",
                        key=f"presentation_{r['cv_id']}",
                    ):

                        cv_complet = recuperer_cv(r["cv_id"])

                        if cv_complet:

                            texte_presentation = generer_presentation(
                                cv_complet.get("candidat") or "",
                                cv_complet.get("metier") or "",
                                cv_complet.get("competences") or "",
                                cv_complet.get("caces") or "",
                                cv_complet.get("permis") or "",
                                entreprise_nom,
                                agence,
                            )

                            st.text_area(
                                "Présentation prête à copier",
                                value=texte_presentation,
                                height=300,
                                key=f"texte_{r['cv_id']}",
                            )


# ============================================================
# SUIVI
# ============================================================

elif page == "📋 Suivi des candidatures":

    st.title("📋 Suivi des candidatures")

    lignes = lister_suivi(agence)

    if not lignes:

        st.info(
            "Aucune candidature suivie pour le moment."
        )

    else:

        for ligne in lignes:

            suivi_id = ligne.get("id")
            candidat = ligne.get("candidat") or ""
            entreprise = ligne.get("entreprise") or ""
            poste = ligne.get("poste") or ""
            statut = ligne.get("statut") or ""
            type_entreprise = ligne.get("type_entreprise") or ""
            date_creation = ligne.get("date_creation") or ""

            col1, col2 = st.columns([4, 2])

            with col1:

                st.write(
                    f"**{candidat}** → "
                    f"{poste} chez {entreprise}"
                )

                if type_entreprise == "🟢 Client":
                    st.caption("🟢 Client")
                elif type_entreprise == "🟠 Prospect":
                    st.caption("🟠 Prospect")

                st.caption(f"Ajouté le {date_creation}")

            with col2:

                nouveau_statut = st.selectbox(
                    "Statut",
                    STATUTS_SUIVI,
                    index=(
                        STATUTS_SUIVI.index(statut)
                        if statut in STATUTS_SUIVI
                        else 0
                    ),
                    key=f"maj_statut_{suivi_id}",
                    label_visibility="collapsed",
                )

                if nouveau_statut != statut:

                    try:
                        modifier_statut_suivi(
                            suivi_id,
                            nouveau_statut,
                        )
                        st.rerun()

                    except Exception as erreur:

                        st.error(
                            "Erreur lors de la modification du statut."
                        )
                        st.exception(erreur)


# ============================================================
# STATISTIQUES
# ============================================================

elif page == "📈 Statistiques":

    st.title("📈 Statistiques de l'agence")

    st.subheader("Activité par semaine")

    stats = statistiques_par_semaine(agence)

    if not stats:

        st.info("Aucune donnée disponible.")

    else:

        for semaine, nb in stats:

            st.write(
                f"📅 **{semaine}** : {nb} candidature(s)"
            )
                 if not entreprise_detectee:
                st.warning(
                    "La rubrique « Nom de l'entreprise » n'a pas été "
                    "identifiée automatiquement."
                )       

            st.markdown("---")
