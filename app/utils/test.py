shit_test = {
    "template_name": "layouts/vertical_column/container",
    "spacing": "2rem",
    "items": [
        {
            "template_name": "layouts/vertical_column/item",
            "title": "Mini cours d’espagnol – Apprendre la conjugaison",
            "content": {
                "template_name": "text/sous_titre",
                "text": "Maîtriser la conjugaison des verbes espagnols réguliers au présent de l’indicatif et connaître deux verbes irréguliers essentiels, avec pronoms et traductions françaises.",
                "opacity": 0.9,
            },
        },
        {
            "template_name": "layouts/vertical_column/container",
            "spacing": "1.5rem",
            "items": [
                {
                    "template_name": "layouts/vertical_column/item",
                    "title": "Règles générales",
                    "content": {
                        "template_name": "text/description_longue",
                        "text": "En espagnol, les verbes se terminent par -ar, -er ou -ir. Au présent de l’indicatif, chaque groupe suit des terminaisons régulières. La terminaison du verbe indique la personne, ce qui rend souvent le pronom facultatif.",
                        "max_width": "100%",
                    },
                },
                {
                    "template_name": "layouts/vertical_column/container",
                    "spacing": "1rem",
                    "items": [
                        {
                            "template_name": "layouts/vertical_column/item",
                            "title": "{course_sections[]tables[]infinitive}",
                            "content": {
                                "template_name": "layouts/vertical_column/container",
                                "spacing": "0.75rem",
                                "items": [
                                    {
                                        "template_name": "tableaux/ligne_cle_valeur",
                                        "key": "Infinitif",
                                        "value": "{course_sections[]tables[]infinitive}",
                                        "separator": ":",
                                    },
                                    {
                                        "template_name": "tableaux/ligne_cle_valeur",
                                        "key": "Traduction",
                                        "value": "{course_sections[]tables[]infinitive_translation}",
                                        "separator": ":",
                                    },
                                    {
                                        "template_name": "tableaux/ligne_cle_valeur",
                                        "key": "Groupe",
                                        "value": "{course_sections[]tables[]verb_group}",
                                        "separator": ":",
                                    },
                                    {
                                        "template_name": "layouts/horizontal_line/container",
                                        "spacing": "1rem",
                                        "wrap": "wrap",
                                        "align_items": "stretch",
                                        "items": [
                                            {
                                                "template_name": "layouts/horizontal_line/item",
                                                "title": "{course_sections[]tables[]conjugation_table[]pronoun_es}",
                                                "content": "{course_sections[]tables[]conjugation_table[]verb_form}",
                                                "flex": "0 0 auto",
                                                "min_width": "120px",
                                            },
                                            {
                                                "template_name": "layouts/horizontal_line/item",
                                                "title": "Traduction",
                                                "content": "{course_sections[]tables[]conjugation_table[]translation_fr}",
                                                "flex": "1",
                                                "min_width": "150px",
                                            },
                                        ],
                                    },
                                ],
                            },
                        }
                    ],
                },
            ],
        },
        {
            "template_name": "layouts/vertical_column/item",
            "title": "Règles générales",
            "content": {
                "template_name": "text/liste_exemples",
                "items": "{course_sections[]tips[]}",
                "prefix": "💡",
            },
        },
        {
            "template_name": "conceptual/concept",
            "icon": "📚",
            "label": "STRUCTURE",
            "title": "Organisation du cours",
            "description": "Ce cours couvre les règles générales de conjugaison avec general_rules et les tables de conjugaison pour {course_sections[]tables[]infinitive} avec {course_sections[]tables[]conjugation_table[]pronoun_es}.",
        },
        {
            "template_name": "logical_relations/donc",
            "icon": "✓",
            "label": "APPRENTISSAGE",
            "content": "En maîtrisant la conjugaison des verbes réguliers et irréguliers, vous serez capable de former correctement les phrases au présent de l'indicatif en espagnol.",
        },
    ],
}
