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

shit_test2 = {
    "course": "Mini cours d’espagnol – Apprendre la conjugaison",
    "topicPath": "string",
    "summary": {
        "title": "Principes généraux de la conjugaison espagnole au présent de l'indicatif",
        "explanation": "En espagnol, la conjugaison des verbes dépend du groupe verbal (terminaisons en -ar, -er, -ir), de la personne grammaticale et du temps. Au présent de l'indicatif, chaque groupe suit des terminaisons régulières qui permettent d'identifier la personne du sujet uniquement à partir de la forme verbale. En parallèle, certains verbes très fréquents sont irréguliers et nécessitent un apprentissage spécifique. Comprendre ces règles générales facilite la compréhension, la production et la reconnaissance des formes verbales à l'oral comme à l'écrit.",
    },
    "themes": [
        {
            "name": "Groupes verbaux réguliers",
            "explanation": "Les verbes réguliers se classent en trois groupes selon leur infinitif : -ar, -er, -ir. Chacun de ces groupes partage des terminaisons fixes au présent de l'indicatif. Apprendre un verbe modèle par groupe aide à appliquer le même schéma à d'autres verbes du même groupe, ce qui est essentiel pour construire vite des phrases correctes en espagnol.",
            "groups": [
                {
                    "label": "Verbes en -ar (modèle : hablar)",
                    "ending": "-ar",
                    "explanation": "Les verbes en -ar forment le groupe le plus vaste et suivent un modèle régulier. En retirant -ar à l'infinitif et en ajoutant les terminaisons du présent, on obtient les formes correspondantes à chaque personne.",
                    "conjugationTable": [
                        {
                            "person": "1re personne du singulier",
                            "pronoun": "yo",
                            "translation": "je",
                            "form": "yo hablo",
                            "meaning": "je parle",
                        },
                        {
                            "person": "2e personne du singulier (familier)",
                            "pronoun": "tú",
                            "translation": "tu",
                            "form": "tú hablas",
                            "meaning": "tu parles",
                        },
                        {
                            "person": "3e personne du singulier",
                            "pronoun": "él/ella",
                            "translation": "il/elle",
                            "form": "él/ella habla",
                            "meaning": "il/elle parle",
                        },
                        {
                            "person": "1re personne du pluriel",
                            "pronoun": "nosotros",
                            "translation": "nous",
                            "form": "nosotros hablamos",
                            "meaning": "nous parlons",
                        },
                        {
                            "person": "2e personne du pluriel (Espagne)",
                            "pronoun": "vosotros",
                            "translation": "vous (plural, informel en Espagne)",
                            "form": "vosotros habláis",
                            "meaning": "vous parlez",
                        },
                        {
                            "person": "3e personne du pluriel",
                            "pronoun": "ellos",
                            "translation": "ils",
                            "form": "ellos hablan",
                            "meaning": "ils parlent",
                        },
                    ],
                    "exampleSentences": [
                        "Yo hablo español con mis amigos. — J’utilise la première personne pour dire que je parle espagnol.",
                        "Nosotros hablamos todos los días para practicar. — Exemple montrant l'usage régulier de la forme nosotros.",
                    ],
                },
                {
                    "label": "Verbes en -er (modèle : comer)",
                    "ending": "-er",
                    "explanation": "Les verbes en -er partagent un autre ensemble de terminaisons au présent. Le principe reste le même : enlever -er et ajouter les terminaisons correspondantes. Ces formes servent pour de nombreux verbes fréquents comme comer, beber, aprender.",
                    "conjugationTable": [
                        {
                            "person": "1re personne du singulier",
                            "pronoun": "yo",
                            "translation": "je",
                            "form": "yo como",
                            "meaning": "je mange",
                        },
                        {
                            "person": "2e personne du singulier (familier)",
                            "pronoun": "tú",
                            "translation": "tu",
                            "form": "tú comes",
                            "meaning": "tu manges",
                        },
                        {
                            "person": "3e personne du singulier",
                            "pronoun": "él/ella",
                            "translation": "il/elle",
                            "form": "él/ella come",
                            "meaning": "il/elle mange",
                        },
                        {
                            "person": "1re personne du pluriel",
                            "pronoun": "nosotros",
                            "translation": "nous",
                            "form": "nosotros comemos",
                            "meaning": "nous mangeons",
                        },
                        {
                            "person": "2e personne du pluriel (Espagne)",
                            "pronoun": "vosotros",
                            "translation": "vous (plural, informel en Espagne)",
                            "form": "vosotros coméis",
                            "meaning": "vous mangez",
                        },
                        {
                            "person": "3e personne du pluriel",
                            "pronoun": "ellos",
                            "translation": "ils",
                            "form": "ellos comen",
                            "meaning": "ils mangent",
                        },
                    ],
                    "exampleSentences": [
                        "Tú comes una manzana cada día. — Illustration d'une action habituelle à la 2e personne.",
                        "Ellos comen juntos en la cafetería. — Phrase simple montrant la 3e personne du pluriel.",
                    ],
                },
                {
                    "label": "Verbes en -ir (modèle : vivir)",
                    "ending": "-ir",
                    "explanation": "Les verbes en -ir ont des terminaisons semblables à celles des verbes en -er pour certaines personnes, mais diffèrent au pluriel. Vivre (vivir) est un bon verbe modèle à mémoriser pour appliquer la règle aux autres verbes en -ir.",
                    "conjugationTable": [
                        {
                            "person": "1re personne du singulier",
                            "pronoun": "yo",
                            "translation": "je",
                            "form": "yo vivo",
                            "meaning": "je vis",
                        },
                        {
                            "person": "2e personne du singulier (familier)",
                            "pronoun": "tú",
                            "translation": "tu",
                            "form": "tú vives",
                            "meaning": "tu vis",
                        },
                        {
                            "person": "3e personne du singulier",
                            "pronoun": "él/ella",
                            "translation": "il/elle",
                            "form": "él/ella vive",
                            "meaning": "il/elle vit",
                        },
                        {
                            "person": "1re personne du pluriel",
                            "pronoun": "nosotros",
                            "translation": "nous",
                            "form": "nosotros vivimos",
                            "meaning": "nous vivons",
                        },
                        {
                            "person": "2e personne du pluriel (Espagne)",
                            "pronoun": "vosotros",
                            "translation": "vous (plural, informel en Espagne)",
                            "form": "vosotros vivís",
                            "meaning": "vous vivez",
                        },
                        {
                            "person": "3e personne du pluriel",
                            "pronoun": "ellos",
                            "translation": "ils",
                            "form": "ellos viven",
                            "meaning": "ils vivent",
                        },
                    ],
                    "exampleSentences": [
                        "Yo vivo en una ciudad pequeña. — Exemple montrant l'usage du verbe vivir à la 1re personne.",
                        "Vosotros vivís cerca de la escuela. — Mise en contexte pour l'usage de vosotros en Espagne.",
                    ],
                },
            ],
        },
        {
            "name": "Verbes irréguliers essentiels",
            "explanation": "Certains verbes très fréquents ne suivent pas les modèles réguliers et affichent des irrégularités de radical ou de forme. Ces verbes sont prioritaires à mémoriser car ils apparaissent constamment à l'oral et à l'écrit. Comprendre la nature de l'irrégularité (changement de radical, formes spéciales en première personne, etc.) aide à les utiliser correctement.",
            "examples": [
                {
                    "label": "Ser (être)",
                    "infinitive": "ser",
                    "explanation": "Le verbe ser est fondamental pour exprimer l'identité, la profession, l'origine, la description et des caractéristiques permanentes. Il est fortement irrégulier au présent et chaque personne a une forme spécifique qui ne se déduit pas du radical normal.",
                    "conjugation": [
                        {"pronoun": "yo", "form": "soy", "meaning": "je suis"},
                        {"pronoun": "tú", "form": "eres", "meaning": "tu es"},
                        {"pronoun": "él/ella", "form": "es", "meaning": "il/elle est"},
                        {
                            "pronoun": "nosotros",
                            "form": "somos",
                            "meaning": "nous sommes",
                        },
                        {
                            "pronoun": "vosotros",
                            "form": "sois",
                            "meaning": "vous êtes (Espagne)",
                        },
                        {"pronoun": "ellos", "form": "son", "meaning": "ils sont"},
                    ],
                    "usageNotes": "Ser sert pour des traits considérés comme durables ou essentiels (origine, nationalité, profession, caractéristiques). Attention : il existe un autre verbe être (estar) employé pour des états temporaires.",
                },
                {
                    "label": "Tener (avoir)",
                    "infinitive": "tener",
                    "explanation": "Tener sert à exprimer la possession, l'obligation (avec que + infinitif dans certaines constructions), l'âge et d'autres expressions idiomatiques. Il présente une irrégularité marquante en première personne du singulier et des modifications du radical pour certaines personnes.",
                    "conjugation": [
                        {"pronoun": "yo", "form": "tengo", "meaning": "j'ai"},
                        {"pronoun": "tú", "form": "tienes", "meaning": "tu as"},
                        {"pronoun": "él/ella", "form": "tiene", "meaning": "il/elle a"},
                        {
                            "pronoun": "nosotros",
                            "form": "tenemos",
                            "meaning": "nous avons",
                        },
                        {
                            "pronoun": "vosotros",
                            "form": "tenéis",
                            "meaning": "vous avez (Espagne)",
                        },
                        {"pronoun": "ellos", "form": "tienen", "meaning": "ils ont"},
                    ],
                    "usageNotes": "La forme yo tengo est irrégulière (ajout d'un -g-). De plus, tener est souvent utilisé dans des expressions idiomatiques (par ejemplo: tener calor, tener hambre) où il ne correspond pas littéralement à « posséder ».",
                },
            ],
        },
        {
            "name": "Pronoms et omission du sujet",
            "explanation": "En espagnol, les pronoms personnels sujets (yo, tú, él, ella, nosotros, vosotros, ellos) existent mais sont souvent facultatifs parce que la terminaison verbale indique déjà la personne. Cette omission est courante à l'oral et dans la langue écrite informelle. Toutefois, le pronom peut être maintenu pour insister sur le sujet ou lever les ambiguïtés.",
            "details": [
                "La terminaison verbale permet d'identifier la personne dans la plupart des cas; dire « hablo » suffit pour comprendre que le locuteur parle à la première personne du singulier, sans dire « yo ».",
                "Dans certains contextes, on utilisera le pronom pour clarifier ou contraster (« Yo hablo, pero él no »).",
                "Le pluriel vosotros est surtout utilisé en Espagne ; en Amérique latine, on emploie généralement ustedes pour la 2e personne du pluriel, avec les mêmes formes verbales que ellos/ellas.",
            ],
        },
    ],
    "relations": {
        "similarities": "Les terminaisons des verbes en -er et -ir sont proches pour plusieurs personnes au présent (par exemple: yo como / yo vivo partagent la même terminaison -o). Cette similarité facilite l'apprentissage lorsque l'on repère les motifs communs.",
        "differences": "Les verbes en -ar ont des terminaisons distinctes (par exemple -amos au nous) alors que -er et -ir diffèrent parfois au pluriel (nosotros comemos vs nosotros vivimos). Les irrégularités, quant à elles, rompent ces schémas et nécessitent un apprentissage ciblé.",
        "practicalLinks": "Apprendre un verbe modèle par groupe (hablar, comer, vivir) crée une base régulière. Ensuite, mémoriser les principaux irréguliers (ser, tener, ir, haber, etc.) permet de couvrir un grand nombre de situations réelles.",
    },
    "learningStrategies": {
        "principles": "Une progression efficace combine mémorisation ciblée, répétition quotidienne et pratique orale. Mémoriser un verbe modèle par groupe aide à internaliser les terminaisons régulières, tandis que la pratique quotidienne renforce la fluidité et la reconnaissance automatique des formes verbales.",
        "concreteTips": [
            "Choisir un verbe modèle pour chaque groupe (hablar, comer, vivir) et conjuguer ces verbes à voix haute chaque jour pour renforcer la mémoire auditive et musculaire.",
            "Se concentrer d'abord sur les verbes fréquents (être, avoir, aller, faire, pouvoir) et apprendre leurs formes irrégulières avant d'élargir le vocabulaire.",
            "Pratiquer à l'oral en situations réelles ou simulées, car l'usage oral force l'omission naturelle des pronoms et aide à automatiser les terminaisons.",
            "Varier les entrées d'apprentissage : écrire des phrases, écouter des dialogues et reproduire les formes rencontrées permet d'ancrer la conjugaison dans différents contextes.",
        ],
        "pitfallsToAvoid": "Éviter de simplement répéter des tableaux sans contexte. Sans phrases et situations concrètes, les formes restent abstraites et plus difficiles à réutiliser spontanément. Ne pas négliger les différences régionales, notamment l'usage de vosotros vs ustedes.",
    },
    "media": {
        "images": [
            {
                "label": "Tableau de conjugaison (exemple visuel)",
                "url": "string",
                "usageSuggestion": "Utiliser cette image pour visualiser côte à côte les conjugaisons des trois groupes; associer le visuel aux exemples oraux améliore la mémorisation. Afficher le tableau pendant la pratique quotidienne aide à renforcer la correspondance forme-signification.",
            }
        ],
        "videos": [
            {
                "label": "Introduction orale au présent de l'indicatif",
                "url": "string",
                "start": "string",
                "usageSuggestion": "Regarder cette vidéo depuis le point de départ indiqué pour entendre la prononciation des terminaisons et des pronoms. Écouter et répéter les exemples à voix haute permet d'améliorer l'aisance à l'oral et de vérifier la prosodie propre à l'espagnol.",
            }
        ],
    },
    "examplesCollection": {
        "purpose": "Fournir des phrases modèles utilisables immédiatement en conversation ou en écriture pour illustrer chaque type de verbe et chaque personne.",
        "examples": [
            {
                "sentence": "Yo hablo con mi profesora.",
                "translation": "Je parle avec ma professeure.",
                "notes": "Verbe en -ar, 1re personne du singulier.",
            },
            {
                "sentence": "Tú comes pan por la mañana.",
                "translation": "Tu manges du pain le matin.",
                "notes": "Verbe en -er, 2e personne du singulier.",
            },
            {
                "sentence": "Él vive cerca de la playa.",
                "translation": "Il vit près de la plage.",
                "notes": "Verbe en -ir, 3e personne du singulier.",
            },
            {
                "sentence": "Nosotros hablamos todos los días.",
                "translation": "Nous parlons tous les jours.",
                "notes": "Forme de groupe montrant une habitude.",
            },
            {
                "sentence": "Yo soy estudiante y tengo veinte años.",
                "translation": "Je suis étudiant et j'ai vingt ans.",
                "notes": "Usage des verbes irréguliers ser et tener pour présenter l'identité et l'âge.",
            },
        ],
    },
    "glossary": [
        {
            "term": "Infinitif",
            "definition": "Forme nominale du verbe en espagnol, généralement terminée par -ar, -er ou -ir, qui sert de base pour former les conjugaisons.",
        },
        {
            "term": "Radical (ou thème)",
            "definition": "La partie du verbe qui reste après avoir retiré la terminaison de l’infinitif; sur laquelle on ajoute les terminaisons conjuguées.",
        },
        {
            "term": "Terminaisons",
            "definition": "Les éléments ajoutés au radical pour indiquer la personne, le nombre et le temps. Au présent de l’indicatif, elles varient selon les groupes -ar, -er et -ir.",
        },
        {
            "term": "Présent de l'indicatif",
            "definition": "Temps verbal utilisé pour exprimer des actions habituelles, des vérités générales, des états présents ou des actions en cours selon le contexte.",
        },
        {
            "term": "Pronoms sujets",
            "definition": "Mots qui indiquent la personne grammaticale (yo, tú, él, nosotros, vosotros, ellos). En espagnol, ils sont souvent facultatifs car la forme verbale véhicule l'information de personne.",
        },
    ],
}

shit_path_group = [
    {
        "group_name": "Métadonnées globales",
        "keys": ["course", "topicPath"],
        "format": "Identifiants et contexte général du cours",
    },
    {
        "group_name": "Résumé et relations",
        "keys": [
            "summary->explanation",
            "summary->title",
            "relations->differences",
            "relations->practicalLinks",
            "relations->similarities",
        ],
        "format": "Textes descriptifs du cours et relations avec d'autres concepts",
    },
    {
        "group_name": "Stratégies d'apprentissage",
        "keys": [
            "learningStrategies->concreteTips",
            "learningStrategies->pitfallsToAvoid",
            "learningStrategies->principles",
        ],
        "format": "Conseils et principes pédagogiques pour maîtriser le concept",
    },
    {
        "group_name": "Glossaire simple",
        "keys": ["glossary[x]definition", "glossary[x]term"],
        "format": "Termes et définitions indexés par position",
    },
    {
        "group_name": "Groupe Examplescollection",
        "keys": ["examplesCollection->purpose"],
        "format": "Groupe parent sans variable de tableau",
    },
    {
        "group_name": "Groupe Examplescollection",
        "keys": ["examplesCollection->examples[x]"],
        "format": "Groupe parent sans variable de tableau",
    },
    {
        "group_name": "Collection d'exemples",
        "keys": [
            "examplesCollection->examples[x]notes",
            "examplesCollection->examples[x]sentence",
            "examplesCollection->examples[x]translation",
        ],
        "format": "Phrases d'exemple avec traductions et annotations groupées",
    },
    {
        "group_name": "Média images",
        "keys": [
            "media->images[x]label",
            "media->images[x]url",
            "media->images[x]usageSuggestion",
        ],
        "format": "Images avec métadonnées (titre, URL, mode d'utilisation)",
    },
    {
        "group_name": "Média vidéos",
        "keys": [
            "media->videos[x]label",
            "media->videos[x]start",
            "media->videos[x]url",
            "media->videos[x]usageSuggestion",
        ],
        "format": "Vidéos avec timestamps et métadonnées de consultation",
    },
    {
        "group_name": "Thèmes - niveau racine",
        "keys": ["themes[x]name", "themes[x]explanation", "themes[x]details"],
        "format": "Informations générales de chaque thème de conjugaison",
    },
    {
        "group_name": "Thèmes - niveau racine",
        "keys": ["themes[x]examples[y]", "themes[x]groups[y]"],
        "format": "Informations générales de chaque thème de conjugaison",
    },
    {
        "group_name": "Thèmes - exemples avec conjugaisons",
        "keys": [
            "themes[x]examples[y]label",
            "themes[x]examples[y]infinitive",
            "themes[x]examples[y]explanation",
            "themes[x]examples[y]usageNotes",
        ],
        "format": "Exemples complets avec formes conjuguées, significations et pronoms associés",
    },
    {
        "group_name": "Thèmes - exemples avec conjugaisons",
        "keys": [
            "themes[x]examples[y]conjugation[z]",
            "themes[x]examples[y]conjugation[z]form",
            "themes[x]examples[y]conjugation[z]meaning",
            "themes[x]examples[y]conjugation[z]pronoun",
        ],
        "format": "Exemples complets avec formes conjuguées, significations et pronoms associés",
    },
    {
        "group_name": "Thèmes - groupes de conjugaison",
        "keys": [
            "themes[x]groups[y]label",
            "themes[x]groups[y]ending",
            "themes[x]groups[y]explanation",
            "themes[x]groups[y]exampleSentences",
        ],
        "format": "Groupes de conjugaison avec tables détaillées (formes, personnes, traductions)",
    },
    {
        "group_name": "Thèmes - groupes de conjugaison",
        "keys": [
            "themes[x]groups[y]conjugationTable[z]",
            "themes[x]groups[y]conjugationTable[z]form",
            "themes[x]groups[y]conjugationTable[z]person",
            "themes[x]groups[y]conjugationTable[z]pronoun",
            "themes[x]groups[y]conjugationTable[z]meaning",
            "themes[x]groups[y]conjugationTable[z]translation",
        ],
        "format": "Groupes de conjugaison avec tables détaillées (formes, personnes, traductions)",
    },
    {
        "group_name": "Groupe Media",
        "keys": ["media->images[x]", "media->videos[x]"],
        "format": "Groupe parent pour media",
    },
    {
        "group_name": "Groupe Glossary",
        "keys": ["glossary[x]"],
        "format": "Groupe parent pour glossary",
    },
    {
        "group_name": "Groupe Themes",
        "keys": ["themes[x]"],
        "format": "Groupe parent pour themes",
    },
]

shit_test_3 = [
    {
        "support": {
            "template_name": "layouts/vertical_column/container",
            "items": [
                {
                    "template_name": "text/description_courte",
                    "text": {
                        "template_name": "layouts/vertical_column/container",
                        "items": [
                            {
                                "template_name": "text/description_courte",
                                "text": "{-{-course-}-}",
                            },
                            {
                                "template_name": "text/explication",
                                "text": "{-{-topicPath-}-}",
                            },
                        ],
                    },
                },
                {
                    "template_name": "text/explication",
                    "text": {
                        "template_name": "layouts/vertical_column/container",
                        "items": [
                            {
                                "template_name": "text/description_courte",
                                "text": "{-{-course-}-}",
                            },
                            {
                                "template_name": "text/explication",
                                "text": "{-{-topicPath-}-}",
                            },
                        ],
                    },
                },
            ],
        }
    },
    {
        "support": {
            "template_name": "text/titre_principal",
            "text": {
                "template_name": "text/titre_principal",
                "text": "{-{-summary->title-}-}",
                "items": [
                    {
                        "template_name": "text/description_longue",
                        "text": "{-{-summary->explanation-}-}",
                    }
                ],
            },
            "items": [
                {
                    "template_name": "text/description_longue",
                    "text": {
                        "template_name": "text/titre_principal",
                        "text": "{-{-summary->title-}-}",
                        "items": [
                            {
                                "template_name": "text/description_longue",
                                "text": "{-{-summary->explanation-}-}",
                            }
                        ],
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "conceptual/concept",
            "title": "Thèmes grammaticaux",
            "description": "Structure organisée des thèmes d'apprentissage",
            "items": [
                {
                    "template_name": "conceptual/concept",
                    "title": {
                        "template_name": "conceptual/concept",
                        "title": "Thèmes grammaticaux",
                        "description": "Structure organisée des thèmes d'apprentissage",
                        "items": [
                            {
                                "template_name": "conceptual/concept",
                                "title": "{-{-themes[0]->name-}-}",
                                "description": {
                                    "template_name": "text/explication",
                                    "text": "{-{-themes[0]->explanation-}-}",
                                },
                            }
                        ],
                    },
                    "description": {
                        "template_name": "text/explication",
                        "text": {
                            "template_name": "conceptual/concept",
                            "title": "Thèmes grammaticaux",
                            "description": "Structure organisée des thèmes d'apprentissage",
                            "items": [
                                {
                                    "template_name": "conceptual/concept",
                                    "title": "{-{-themes[0]->name-}-}",
                                    "description": {
                                        "template_name": "text/explication",
                                        "text": "{-{-themes[0]->explanation-}-}",
                                    },
                                }
                            ],
                        },
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "layouts/tree_left_right/item",
            "title": {
                "template_name": "layouts/tree_left_right/item",
                "title": "{-{-themes[0]->groups[0]->label-}-}",
                "content": {
                    "template_name": "text/liste_hierarchique",
                    "items": [
                        {
                            "template_name": "logical_relations/si_alors",
                            "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[0]->ending-}-}",
                            "alors_content": "{-{-themes[0]->groups[0]->explanation-}-}",
                        }
                    ],
                },
            },
            "content": {
                "template_name": "text/liste_hierarchique",
                "items": [
                    {
                        "template_name": "logical_relations/si_alors",
                        "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[0]->ending-}-}",
                        "alors_content": {
                            "template_name": "layouts/tree_left_right/item",
                            "title": "{-{-themes[0]->groups[0]->label-}-}",
                            "content": {
                                "template_name": "text/liste_hierarchique",
                                "items": [
                                    {
                                        "template_name": "logical_relations/si_alors",
                                        "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[0]->ending-}-}",
                                        "alors_content": "{-{-themes[0]->groups[0]->explanation-}-}",
                                    }
                                ],
                            },
                        },
                    }
                ],
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[0]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[1]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[2]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[3]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[4]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[0]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[0]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[0]->conjugationTable[5]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": {
                "template_name": "text/liste_exemples",
                "items": "{-{-themes[0]->groups[0]->exampleSentences[0]-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": {
                "template_name": "text/liste_exemples",
                "items": "{-{-themes[0]->groups[0]->exampleSentences[1]-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "layouts/tree_left_right/item",
            "title": {
                "template_name": "layouts/tree_left_right/item",
                "title": "{-{-themes[0]->groups[1]->label-}-}",
                "content": {
                    "template_name": "text/liste_hierarchique",
                    "items": [
                        {
                            "template_name": "logical_relations/si_alors",
                            "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[1]->ending-}-}",
                            "alors_content": "{-{-themes[0]->groups[1]->explanation-}-}",
                        }
                    ],
                },
            },
            "content": {
                "template_name": "text/liste_hierarchique",
                "items": [
                    {
                        "template_name": "logical_relations/si_alors",
                        "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[1]->ending-}-}",
                        "alors_content": {
                            "template_name": "layouts/tree_left_right/item",
                            "title": "{-{-themes[0]->groups[1]->label-}-}",
                            "content": {
                                "template_name": "text/liste_hierarchique",
                                "items": [
                                    {
                                        "template_name": "logical_relations/si_alors",
                                        "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[1]->ending-}-}",
                                        "alors_content": "{-{-themes[0]->groups[1]->explanation-}-}",
                                    }
                                ],
                            },
                        },
                    }
                ],
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[0]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[1]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[2]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[3]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[4]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[1]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[1]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[1]->conjugationTable[5]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": {
                "template_name": "text/liste_exemples",
                "items": "{-{-themes[0]->groups[1]->exampleSentences[0]-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": {
                "template_name": "text/liste_exemples",
                "items": "{-{-themes[0]->groups[1]->exampleSentences[1]-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "layouts/tree_left_right/item",
            "title": {
                "template_name": "layouts/tree_left_right/item",
                "title": "{-{-themes[0]->groups[2]->label-}-}",
                "content": {
                    "template_name": "text/liste_hierarchique",
                    "items": [
                        {
                            "template_name": "logical_relations/si_alors",
                            "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[2]->ending-}-}",
                            "alors_content": "{-{-themes[0]->groups[2]->explanation-}-}",
                        }
                    ],
                },
            },
            "content": {
                "template_name": "text/liste_hierarchique",
                "items": [
                    {
                        "template_name": "logical_relations/si_alors",
                        "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[2]->ending-}-}",
                        "alors_content": {
                            "template_name": "layouts/tree_left_right/item",
                            "title": "{-{-themes[0]->groups[2]->label-}-}",
                            "content": {
                                "template_name": "text/liste_hierarchique",
                                "items": [
                                    {
                                        "template_name": "logical_relations/si_alors",
                                        "si_content": "Terminaison de l'infinitif: {-{-themes[0]->groups[2]->ending-}-}",
                                        "alors_content": "{-{-themes[0]->groups[2]->explanation-}-}",
                                    }
                                ],
                            },
                        },
                    }
                ],
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[0]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[0]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[0]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[1]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[1]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[1]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[2]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[2]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[2]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[3]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[3]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[3]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[4]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[4]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[4]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "tableaux/tableau_decisionnel",
            "title": "Tables de Conjugaison",
            "header1": "Personne",
            "header2": "Pronom",
            "header3": "Forme Conjuguée",
            "row1_col1": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->translation-}-}",
            },
            "row1_col2": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->translation-}-}",
            },
            "row1_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->translation-}-}",
            },
            "row2_col1": "Sens",
            "row2_col2": "Traduction",
            "row2_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->translation-}-}",
            },
            "row3_col1": "Référence",
            "row3_col2": "Détail",
            "row3_col3": {
                "template_name": "tableaux/tableau_decisionnel",
                "title": "Tables de Conjugaison",
                "header1": "Personne",
                "header2": "Pronom",
                "header3": "Forme Conjuguée",
                "row1_col1": "{-{-themes[0]->groups[2]->conjugationTable[5]->person-}-}",
                "row1_col2": "{-{-themes[0]->groups[2]->conjugationTable[5]->pronoun-}-}",
                "row1_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->form-}-}",
                "row2_col1": "Sens",
                "row2_col2": "Traduction",
                "row2_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->meaning-}-}",
                "row3_col1": "Référence",
                "row3_col2": "Détail",
                "row3_col3": "{-{-themes[0]->groups[2]->conjugationTable[5]->translation-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": {
                "template_name": "text/liste_exemples",
                "items": "{-{-themes[0]->groups[2]->exampleSentences[0]-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": {
                "template_name": "text/liste_exemples",
                "items": "{-{-themes[0]->groups[2]->exampleSentences[1]-}-}",
            },
        }
    },
    {
        "support": {
            "template_name": "conceptual/concept",
            "title": "Thèmes grammaticaux",
            "description": "Structure organisée des thèmes d'apprentissage",
            "items": [
                {
                    "template_name": "conceptual/concept",
                    "title": {
                        "template_name": "conceptual/concept",
                        "title": "Thèmes grammaticaux",
                        "description": "Structure organisée des thèmes d'apprentissage",
                        "items": [
                            {
                                "template_name": "conceptual/concept",
                                "title": "{-{-themes[1]->name-}-}",
                                "description": {
                                    "template_name": "text/explication",
                                    "text": "{-{-themes[1]->explanation-}-}",
                                },
                            }
                        ],
                    },
                    "description": {
                        "template_name": "text/explication",
                        "text": {
                            "template_name": "conceptual/concept",
                            "title": "Thèmes grammaticaux",
                            "description": "Structure organisée des thèmes d'apprentissage",
                            "items": [
                                {
                                    "template_name": "conceptual/concept",
                                    "title": "{-{-themes[1]->name-}-}",
                                    "description": {
                                        "template_name": "text/explication",
                                        "text": "{-{-themes[1]->explanation-}-}",
                                    },
                                }
                            ],
                        },
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": [
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>{-{-themes[1]->examples[0]->label-}-}</strong><br/><em>Infinitif:</em> {-{-themes[1]->examples[0]->infinitive-}-}<br/><br/><strong>Explication:</strong><br/>{-{-themes[1]->examples[0]->explanation-}-}<br/><br/><strong>Notes d'usage:</strong><br/>{-{-themes[1]->examples[0]->usageNotes-}-}",
                },
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>{-{-themes[1]->examples[0]->label-}-}</strong><br/><em>Infinitif:</em> {-{-themes[1]->examples[0]->infinitive-}-}<br/><br/><strong>Explication:</strong><br/>{-{-themes[1]->examples[0]->explanation-}-}<br/><br/><strong>Notes d'usage:</strong><br/>{-{-themes[1]->examples[0]->usageNotes-}-}",
                },
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[0]->conjugation[0]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[0]->conjugation[0]->form-}-} - {-{-themes[1]->examples[0]->conjugation[0]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[0]->conjugation[0]->form-}-} - {-{-themes[1]->examples[0]->conjugation[0]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[0]->conjugation[1]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[0]->conjugation[1]->form-}-} - {-{-themes[1]->examples[0]->conjugation[1]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[0]->conjugation[1]->form-}-} - {-{-themes[1]->examples[0]->conjugation[1]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[0]->conjugation[2]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[0]->conjugation[2]->form-}-} - {-{-themes[1]->examples[0]->conjugation[2]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[0]->conjugation[2]->form-}-} - {-{-themes[1]->examples[0]->conjugation[2]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[0]->conjugation[3]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[0]->conjugation[3]->form-}-} - {-{-themes[1]->examples[0]->conjugation[3]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[0]->conjugation[3]->form-}-} - {-{-themes[1]->examples[0]->conjugation[3]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[0]->conjugation[4]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[0]->conjugation[4]->form-}-} - {-{-themes[1]->examples[0]->conjugation[4]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[0]->conjugation[4]->form-}-} - {-{-themes[1]->examples[0]->conjugation[4]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[0]->conjugation[5]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[0]->conjugation[5]->form-}-} - {-{-themes[1]->examples[0]->conjugation[5]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[0]->conjugation[5]->form-}-} - {-{-themes[1]->examples[0]->conjugation[5]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": [
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>{-{-themes[1]->examples[1]->label-}-}</strong><br/><em>Infinitif:</em> {-{-themes[1]->examples[1]->infinitive-}-}<br/><br/><strong>Explication:</strong><br/>{-{-themes[1]->examples[1]->explanation-}-}<br/><br/><strong>Notes d'usage:</strong><br/>{-{-themes[1]->examples[1]->usageNotes-}-}",
                },
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>{-{-themes[1]->examples[1]->label-}-}</strong><br/><em>Infinitif:</em> {-{-themes[1]->examples[1]->infinitive-}-}<br/><br/><strong>Explication:</strong><br/>{-{-themes[1]->examples[1]->explanation-}-}<br/><br/><strong>Notes d'usage:</strong><br/>{-{-themes[1]->examples[1]->usageNotes-}-}",
                },
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[1]->conjugation[0]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[1]->conjugation[0]->form-}-} - {-{-themes[1]->examples[1]->conjugation[0]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[1]->conjugation[0]->form-}-} - {-{-themes[1]->examples[1]->conjugation[0]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[1]->conjugation[1]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[1]->conjugation[1]->form-}-} - {-{-themes[1]->examples[1]->conjugation[1]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[1]->conjugation[1]->form-}-} - {-{-themes[1]->examples[1]->conjugation[1]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[1]->conjugation[2]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[1]->conjugation[2]->form-}-} - {-{-themes[1]->examples[1]->conjugation[2]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[1]->conjugation[2]->form-}-} - {-{-themes[1]->examples[1]->conjugation[2]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[1]->conjugation[3]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[1]->conjugation[3]->form-}-} - {-{-themes[1]->examples[1]->conjugation[3]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[1]->conjugation[3]->form-}-} - {-{-themes[1]->examples[1]->conjugation[3]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[1]->conjugation[4]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[1]->conjugation[4]->form-}-} - {-{-themes[1]->examples[1]->conjugation[4]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[1]->conjugation[4]->form-}-} - {-{-themes[1]->examples[1]->conjugation[4]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "tableaux/ligne_cle_valeur",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": "{-{-themes[1]->examples[1]->conjugation[5]->pronoun-}-}",
                                "value": {
                                    "template_name": "text/resume",
                                    "text": "{-{-themes[1]->examples[1]->conjugation[5]->form-}-} - {-{-themes[1]->examples[1]->conjugation[5]->meaning-}-}",
                                },
                            }
                        ],
                    },
                    "value": {
                        "template_name": "text/resume",
                        "text": "{-{-themes[1]->examples[1]->conjugation[5]->form-}-} - {-{-themes[1]->examples[1]->conjugation[5]->meaning-}-}",
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "conceptual/concept",
            "title": "Thèmes grammaticaux",
            "description": "Structure organisée des thèmes d'apprentissage",
            "items": [
                {
                    "template_name": "conceptual/concept",
                    "title": {
                        "template_name": "conceptual/concept",
                        "title": "Thèmes grammaticaux",
                        "description": "Structure organisée des thèmes d'apprentissage",
                        "items": [
                            {
                                "template_name": "conceptual/concept",
                                "title": "{-{-themes[2]->name-}-}",
                                "description": {
                                    "template_name": "text/explication",
                                    "text": "{-{-themes[2]->explanation-}-}",
                                },
                            }
                        ],
                    },
                    "description": {
                        "template_name": "text/explication",
                        "text": {
                            "template_name": "conceptual/concept",
                            "title": "Thèmes grammaticaux",
                            "description": "Structure organisée des thèmes d'apprentissage",
                            "items": [
                                {
                                    "template_name": "conceptual/concept",
                                    "title": "{-{-themes[2]->name-}-}",
                                    "description": {
                                        "template_name": "text/explication",
                                        "text": "{-{-themes[2]->explanation-}-}",
                                    },
                                }
                            ],
                        },
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "layouts/vertical_column/item",
            "title": "Détails de thèmes",
            "content": {
                "template_name": "text/liste_exemples",
                "items": {
                    "template_name": "layouts/vertical_column/item",
                    "title": "Détails de thèmes",
                    "content": {
                        "template_name": "text/liste_exemples",
                        "items": "{-{-themes[2]->details[0]-}-}",
                    },
                },
            },
        }
    },
    {
        "support": {
            "template_name": "layouts/vertical_column/item",
            "title": "Détails de thèmes",
            "content": {
                "template_name": "text/liste_exemples",
                "items": {
                    "template_name": "layouts/vertical_column/item",
                    "title": "Détails de thèmes",
                    "content": {
                        "template_name": "text/liste_exemples",
                        "items": "{-{-themes[2]->details[1]-}-}",
                    },
                },
            },
        }
    },
    {
        "support": {
            "template_name": "layouts/vertical_column/item",
            "title": "Détails de thèmes",
            "content": {
                "template_name": "text/liste_exemples",
                "items": {
                    "template_name": "layouts/vertical_column/item",
                    "title": "Détails de thèmes",
                    "content": {
                        "template_name": "text/liste_exemples",
                        "items": "{-{-themes[2]->details[2]-}-}",
                    },
                },
            },
        }
    },
    {
        "support": {
            "template_name": "text/description_longue",
            "fields": {
                "text": {
                    "template_name": "text/description_longue",
                    "fields": {"text": "{-{-relations->similarities-}-}"},
                }
            },
        }
    },
    {
        "support": {
            "template_name": "layouts/vertical_column/container",
            "items": [
                {
                    "template_name": "text/nom_categorie",
                    "text": "Principes d'apprentissage",
                },
                {
                    "template_name": "text/liste_hierarchique",
                    "items": {
                        "template_name": "layouts/vertical_column/container",
                        "items": [
                            {
                                "template_name": "text/nom_categorie",
                                "text": "Principes d'apprentissage",
                            },
                            {
                                "template_name": "text/liste_hierarchique",
                                "items": "{-{-learningStrategies->principles-}-}",
                            },
                            {
                                "template_name": "text/nom_categorie",
                                "text": "Pièges à éviter",
                            },
                            {
                                "template_name": "text/liste_hierarchique",
                                "items": "{-{-learningStrategies->pitfallsToAvoid-}-}",
                            },
                        ],
                    },
                },
                {"template_name": "text/nom_categorie", "text": "Pièges à éviter"},
                {
                    "template_name": "text/liste_hierarchique",
                    "items": {
                        "template_name": "layouts/vertical_column/container",
                        "items": [
                            {
                                "template_name": "text/nom_categorie",
                                "text": "Principes d'apprentissage",
                            },
                            {
                                "template_name": "text/liste_hierarchique",
                                "items": "{-{-learningStrategies->principles-}-}",
                            },
                            {
                                "template_name": "text/nom_categorie",
                                "text": "Pièges à éviter",
                            },
                            {
                                "template_name": "text/liste_hierarchique",
                                "items": "{-{-learningStrategies->pitfallsToAvoid-}-}",
                            },
                        ],
                    },
                },
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_numerotee",
            "items": [
                {
                    "template_name": "text/note",
                    "text": {
                        "template_name": "text/liste_numerotee",
                        "items": [
                            {
                                "template_name": "text/note",
                                "text": "{-{-learningStrategies->concreteTips[0]-}-}",
                            }
                        ],
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_numerotee",
            "items": [
                {
                    "template_name": "text/note",
                    "text": {
                        "template_name": "text/liste_numerotee",
                        "items": [
                            {
                                "template_name": "text/note",
                                "text": "{-{-learningStrategies->concreteTips[1]-}-}",
                            }
                        ],
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_numerotee",
            "items": [
                {
                    "template_name": "text/note",
                    "text": {
                        "template_name": "text/liste_numerotee",
                        "items": [
                            {
                                "template_name": "text/note",
                                "text": "{-{-learningStrategies->concreteTips[2]-}-}",
                            }
                        ],
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_numerotee",
            "items": [
                {
                    "template_name": "text/note",
                    "text": {
                        "template_name": "text/liste_numerotee",
                        "items": [
                            {
                                "template_name": "text/note",
                                "text": "{-{-learningStrategies->concreteTips[3]-}-}",
                            }
                        ],
                    },
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/titre_principal",
            "text": "Galerie d'images indexées",
            "items": [
                {
                    "template_name": "tableaux/ligne_cle_valeur",
                    "key": {
                        "template_name": "text/label_court",
                        "text": {
                            "template_name": "text/titre_principal",
                            "text": "Galerie d'images indexées",
                            "items": [
                                {
                                    "template_name": "tableaux/ligne_cle_valeur",
                                    "key": {
                                        "template_name": "text/label_court",
                                        "text": "{-{-media->images[0]->label-}-}",
                                    },
                                    "value": {
                                        "template_name": "tableaux/ligne_cle_valeur",
                                        "key": "URL",
                                        "value": "{-{-media->images[0]->url-}-}",
                                    },
                                },
                                {
                                    "template_name": "text/annotation",
                                    "text": "{-{-media->images[0]->usageSuggestion-}-}",
                                },
                            ],
                        },
                    },
                    "value": {
                        "template_name": "tableaux/ligne_cle_valeur",
                        "key": "URL",
                        "value": {
                            "template_name": "text/titre_principal",
                            "text": "Galerie d'images indexées",
                            "items": [
                                {
                                    "template_name": "tableaux/ligne_cle_valeur",
                                    "key": {
                                        "template_name": "text/label_court",
                                        "text": "{-{-media->images[0]->label-}-}",
                                    },
                                    "value": {
                                        "template_name": "tableaux/ligne_cle_valeur",
                                        "key": "URL",
                                        "value": "{-{-media->images[0]->url-}-}",
                                    },
                                },
                                {
                                    "template_name": "text/annotation",
                                    "text": "{-{-media->images[0]->usageSuggestion-}-}",
                                },
                            ],
                        },
                    },
                },
                {
                    "template_name": "text/annotation",
                    "text": {
                        "template_name": "text/titre_principal",
                        "text": "Galerie d'images indexées",
                        "items": [
                            {
                                "template_name": "tableaux/ligne_cle_valeur",
                                "key": {
                                    "template_name": "text/label_court",
                                    "text": "{-{-media->images[0]->label-}-}",
                                },
                                "value": {
                                    "template_name": "tableaux/ligne_cle_valeur",
                                    "key": "URL",
                                    "value": "{-{-media->images[0]->url-}-}",
                                },
                            },
                            {
                                "template_name": "text/annotation",
                                "text": "{-{-media->images[0]->usageSuggestion-}-}",
                            },
                        ],
                    },
                },
            ],
        }
    },
    {
        "support": {
            "template_name": "temporal/chronologie/container",
            "items": [
                {
                    "template_name": "temporal/chronologie/item",
                    "start": {
                        "template_name": "temporal/chronologie/container",
                        "items": [
                            {
                                "template_name": "temporal/chronologie/item",
                                "start": "{-{-media->videos[0]->start-}-}",
                            },
                            {
                                "template_name": "text/liste_exemples",
                                "items": [
                                    {
                                        "template_name": "text/liste_tags",
                                        "items": ["{-{-media->videos[0]->label-}-}"],
                                    },
                                    {
                                        "template_name": "text/liste_exemples",
                                        "items": [
                                            "URL: {-{-media->videos[0]->url-}-}",
                                            "Usage: {-{-media->videos[0]->usageSuggestion-}-}",
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                },
                {
                    "template_name": "text/liste_exemples",
                    "items": [
                        {
                            "template_name": "text/liste_tags",
                            "items": [
                                {
                                    "template_name": "temporal/chronologie/container",
                                    "items": [
                                        {
                                            "template_name": "temporal/chronologie/item",
                                            "start": "{-{-media->videos[0]->start-}-}",
                                        },
                                        {
                                            "template_name": "text/liste_exemples",
                                            "items": [
                                                {
                                                    "template_name": "text/liste_tags",
                                                    "items": [
                                                        "{-{-media->videos[0]->label-}-}"
                                                    ],
                                                },
                                                {
                                                    "template_name": "text/liste_exemples",
                                                    "items": [
                                                        "URL: {-{-media->videos[0]->url-}-}",
                                                        "Usage: {-{-media->videos[0]->usageSuggestion-}-}",
                                                    ],
                                                },
                                            ],
                                        },
                                    ],
                                }
                            ],
                        },
                        {
                            "template_name": "text/liste_exemples",
                            "items": [
                                "URL: {-{-media->videos[0]->url-}-}",
                                "Usage: {-{-media->videos[0]->usageSuggestion-}-}",
                            ],
                        },
                    ],
                },
            ],
        }
    },
    {
        "support": {
            "template_name": "layouts/vertical_column/container",
            "items": [
                {"template_name": "text/nom_categorie", "text": "Examplesscollection"},
                {
                    "template_name": "text/liste_hierarchique",
                    "items": {
                        "template_name": "layouts/vertical_column/container",
                        "items": [
                            {
                                "template_name": "text/nom_categorie",
                                "text": "Examplesscollection",
                            },
                            {
                                "template_name": "text/liste_hierarchique",
                                "items": "{-{-examplesCollection->purpose-}-}",
                            },
                        ],
                    },
                },
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": [
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>Phrase:</strong> {-{-examplesCollection->examples[0]->sentence-}-}<br/><strong>Traduction:</strong> {-{-examplesCollection->examples[0]->translation-}-}<br/><strong>Note:</strong> {-{-examplesCollection->examples[0]->notes-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": [
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>Phrase:</strong> {-{-examplesCollection->examples[1]->sentence-}-}<br/><strong>Traduction:</strong> {-{-examplesCollection->examples[1]->translation-}-}<br/><strong>Note:</strong> {-{-examplesCollection->examples[1]->notes-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": [
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>Phrase:</strong> {-{-examplesCollection->examples[2]->sentence-}-}<br/><strong>Traduction:</strong> {-{-examplesCollection->examples[2]->translation-}-}<br/><strong>Note:</strong> {-{-examplesCollection->examples[2]->notes-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": [
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>Phrase:</strong> {-{-examplesCollection->examples[3]->sentence-}-}<br/><strong>Traduction:</strong> {-{-examplesCollection->examples[3]->translation-}-}<br/><strong>Note:</strong> {-{-examplesCollection->examples[3]->notes-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_exemples",
            "items": [
                {
                    "template_name": "text/description_longue",
                    "text": "<strong>Phrase:</strong> {-{-examplesCollection->examples[4]->sentence-}-}<br/><strong>Traduction:</strong> {-{-examplesCollection->examples[4]->translation-}-}<br/><strong>Note:</strong> {-{-examplesCollection->examples[4]->notes-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_puces",
            "items": [
                {
                    "template_name": "text/definition",
                    "text": "{-{-glossary[0]->term-}-}: {-{-glossary[0]->definition-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_puces",
            "items": [
                {
                    "template_name": "text/definition",
                    "text": "{-{-glossary[1]->term-}-}: {-{-glossary[1]->definition-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_puces",
            "items": [
                {
                    "template_name": "text/definition",
                    "text": "{-{-glossary[2]->term-}-}: {-{-glossary[2]->definition-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_puces",
            "items": [
                {
                    "template_name": "text/definition",
                    "text": "{-{-glossary[3]->term-}-}: {-{-glossary[3]->definition-}-}",
                }
            ],
        }
    },
    {
        "support": {
            "template_name": "text/liste_puces",
            "items": [
                {
                    "template_name": "text/definition",
                    "text": "{-{-glossary[4]->term-}-}: {-{-glossary[4]->definition-}-}",
                }
            ],
        }
    },
]

shit_test_4 = [
    {
        "recto": {
            "template_name": "big_question",
            "field_name_1": "Qu'est-ce que le Principe de Responsabilité Unique (SRP) ?",
            "field_name_2": "Un concept fondamental de l'architecture logicielle",
            "field_name_3": {
                "template_name": "hint_box",
                "field_name_1": "💡 Une classe = Une raison de changer",
            },
        },
        "verso": {
            "template_name": "definition_with_justification",
            "field_name_1": "Définition du SRP",
            "field_name_2": "Une classe ou un module ne doit avoir qu'une seule raison de changer, c'est-à-dire une responsabilité métier clairement identifiée.",
            "field_name_3": "Pourquoi c'est important",
            "field_name_4": [
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Compréhension",
                    "field_name_2": "Rôle rapide et clair de chaque unité de code",
                },
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Maintenabilité",
                    "field_name_2": "Limiter l'impact d'un changement à une dimension précise du système",
                },
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Flexibilité",
                    "field_name_2": "Modifier une responsabilité sans affecter les autres",
                },
            ],
            "field_name_5": "Application pratique",
            "field_name_6": [
                {
                    "template_name": "layer_item",
                    "field_name_1": "Couche Métier",
                    "field_name_2": "Responsabilité: Implémenter les règles métiers et la logique applicative",
                },
                {
                    "template_name": "layer_item",
                    "field_name_1": "Couche Données",
                    "field_name_2": "Responsabilité: Gérer l'accès et la persistance des données",
                },
                {
                    "template_name": "layer_item",
                    "field_name_1": "Couche Orchestration",
                    "field_name_2": "Responsabilité: Coordonner les interactions entre composants",
                },
            ],
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "question_template",
            "field_name_1": "Quels sont les bénéfices directs de l'application du Principe de Responsabilité Unique?",
        },
        "verso": {
            "template_name": "benefits_template",
            "field_name_1": "Bénéfices du Principe de Responsabilité Unique (SRP)",
            "field_name_2": [
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Modularité renforcée",
                    "field_name_2": "Évolution indépendante des composants grâce à la séparation des responsabilités",
                },
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Tests plus fiables et simples",
                    "field_name_2": "Les changements sont confinés à une porte d'entrée délimitée, facilitant la testabilité ciblée",
                },
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Réduction des régressions",
                    "field_name_2": "L'isolation de chaque responsabilité réduit le risque de régressions lors des modifications",
                },
            ],
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "question_template",
            "field_name_1": "Qu'est-ce que le Principe Ouvert/Fermé (OCP) ?",
            "field_name_2": {
                "template_name": "hint_template",
                "field_name_1": "Un principe SOLID fondamental pour écrire du code flexible et maintenable",
            },
        },
        "verso": {
            "template_name": "definition_template",
            "field_name_1": "Principe Ouvert/Fermé (OCP)",
            "field_name_2": "Une entité logicielle doit être ouverte à l'extension mais fermée à la modification",
            "field_name_3": [
                {
                    "template_name": "principle_item",
                    "field_name_1": "Principe Technique",
                    "field_name_2": "Ne pas modifier le code existant pour ajouter de nouveaux comportements",
                },
                {
                    "template_name": "principle_item",
                    "field_name_1": "Mécanisme de Mise en Œuvre",
                    "field_name_2": "Créer de nouvelles implémentations conformes à une abstraction commune (interfaces ou classes abstraites)",
                },
                {
                    "template_name": "principle_item",
                    "field_name_1": "Avantages Clés",
                    "field_name_2": "Minimise les risques de régressions et les perturbations des fonctionnalités déjà déployées",
                },
            ],
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "question_template",
            "field_name_1": "Qu'est-ce que le Principe de Substitution de Liskov (LSP) ?",
            "field_name_2": {
                "template_name": "hint_template",
                "field_name_1": "Un principe SOLID qui régit la relation entre classes dérivées et classe de base",
            },
        },
        "verso": {
            "template_name": "definition_template",
            "field_name_1": "Principe de Substitution de Liskov (LSP)",
            "field_name_2": "Toute classe dérivée doit pouvoir remplacer sa classe de base sans altérer le comportement attendu du programme",
            "field_name_3": [
                {
                    "template_name": "contract_item",
                    "field_name_1": "Contrat avec la classe de base",
                    "field_name_2": "Les objets d'une sous-classe doivent être utilisables partout où l'on attend un objet de la super-classe",
                },
                {
                    "template_name": "contract_item",
                    "field_name_1": "Respect des préconditions",
                    "field_name_2": "Les conditions nécessaires avant l'exécution d'une méthode ne doivent pas être renforcées dans la sous-classe",
                },
                {
                    "template_name": "contract_item",
                    "field_name_1": "Respect des postconditions",
                    "field_name_2": "Les garanties après l'exécution d'une méthode ne doivent pas être affaiblies dans la sous-classe",
                },
                {
                    "template_name": "contract_item",
                    "field_name_1": "Respect des invariants",
                    "field_name_2": "Les propriétés invariantes de la classe de base doivent rester vraies dans la sous-classe",
                },
            ],
            "field_name_4": [
                {
                    "template_name": "application_item",
                    "field_name_1": "Prévention des violations contractuelles",
                    "field_name_2": "Évite les comportements inattendus lors de la substitution de types",
                },
                {
                    "template_name": "application_item",
                    "field_name_1": "Système prévisible",
                    "field_name_2": "Augmente la fiabilité et la maintenabilité du code polymorphe",
                },
                {
                    "template_name": "application_item",
                    "field_name_1": "Design orienté objet robuste",
                    "field_name_2": "Assure que l'héritage est utilisé correctement pour la spécialisation, pas la dérive comportementale",
                },
            ],
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "question_template",
            "question_text": "Qu'est-ce que le Principe de Ségrégation des Interfaces (ISP) ?",
        },
        "verso": {
            "template_name": "definition_with_principle_template",
            "definition_title": "Principe de Ségrégation des Interfaces (ISP)",
            "definition_text": "L'ISP recommande de créer des interfaces spécifiques et légères plutôt qu'une interface générale trop large.",
            "principle_title": "Principe de Granularité",
            "principle_details": [
                {
                    "template_name": "principle_item",
                    "principle_name": "Scinder les interfaces",
                    "principle_description": "Diviser les interfaces en ensembles fonctionnels plus petits et cohérents",
                },
                {
                    "template_name": "principle_item",
                    "principle_name": "Implémentation sélective",
                    "principle_description": "Chaque classe n'implémente que les méthodes dont elle a réellement besoin",
                },
            ],
            "advantages_title": "Avantages",
            "advantages_list": [
                {
                    "template_name": "advantage_item",
                    "advantage_name": "Réduction du couplage",
                    "advantage_description": "Les dépendances entre composants sont minimisées et localisées",
                },
                {
                    "template_name": "advantage_item",
                    "advantage_name": "Clarté des contrats",
                    "advantage_description": "Les interfaces communiquent clairement leurs responsabilités",
                },
                {
                    "template_name": "advantage_item",
                    "advantage_name": "Facilité de remplacement",
                    "advantage_description": "Les composants peuvent être remplacés sans affecter le reste du système",
                },
                {
                    "template_name": "advantage_item",
                    "advantage_name": "Amélioration des tests",
                    "advantage_description": "Les tests unitaires deviennent plus simples et plus ciblés",
                },
            ],
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "centered_title_template",
            "title": "Qu'est-ce que le Principe d'Inversion des Dépendances (DIP) ?",
            "subtitle": "Abstractions et Testabilité",
        },
        "verso": {
            "template_name": "definition_with_details_template",
            "definition": "Le DIP (Dependency Inversion Principle) stipule que les modules de haut niveau ne doivent pas dépendre des modules de bas niveau, mais tous deux doivent dépendre d'abstractions (interfaces).",
            "details": [
                {
                    "template_name": "section_template",
                    "title": "Mécanisme de fonctionnement",
                    "content": [
                        {
                            "template_name": "point_template",
                            "label": "Introduction d'abstractions",
                            "description": "Créer des interfaces que les modules consomment plutôt que de dépendre directement d'implémentations concrètes",
                        },
                        {
                            "template_name": "point_template",
                            "label": "Injection de dépendances",
                            "description": "Passer les implémentations concrètes aux modules via le constructeur ou des méthodes, plutôt que de les créer en interne",
                        },
                        {
                            "template_name": "point_template",
                            "label": "Découplage architectural",
                            "description": "Les modules interagissent via des contrats (interfaces) plutôt que via des implémentations directes",
                        },
                    ],
                },
                {
                    "template_name": "section_template",
                    "title": "Bénéfices pour les tests",
                    "content": [
                        {
                            "template_name": "point_template",
                            "label": "Échange facile des implémentations",
                            "description": "Remplacer facilement les implémentations concrètes par des mocks ou stubs sans modifier la logique métier",
                        },
                        {
                            "template_name": "point_template",
                            "label": "Tests unitaires isolés",
                            "description": "Tester chaque module indépendamment en injectant des implémentations de test",
                        },
                        {
                            "template_name": "point_template",
                            "label": "Réduction de la complexité",
                            "description": "Simplifier la mise en place de scénarios de test en controlant les dépendances",
                        },
                        {
                            "template_name": "point_template",
                            "label": "Flexibilité et maintenabilité",
                            "description": "Adapter le système aux besoins sans modification de la logique métier existante",
                        },
                    ],
                },
            ],
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "question_template",
            "field_name_1": "Comment le Principe de Responsabilité Unique et le Principe de Ségrégation des Interfaces travaillent-ils ensemble?",
            "field_name_2": {
                "template_name": "hint_template",
                "field_name_1": "Deux principes SOLID qui se complètent pour améliorer la conception",
            },
        },
        "verso": {
            "template_name": "interaction_template",
            "field_name_1": "Synergie entre SRP et ISP",
            "field_name_2": [
                {
                    "template_name": "interaction_element",
                    "field_name_1": "Principe de Responsabilité Unique (SRP)",
                    "field_name_2": "Éclate les responsabilités en composants distincts",
                    "field_name_3": "Une classe = une raison de changer",
                },
                {
                    "template_name": "interaction_element",
                    "field_name_1": "Principe de Ségrégation des Interfaces (ISP)",
                    "field_name_2": "S'assure que chaque classe n'accède qu'aux interfaces nécessaires",
                    "field_name_3": "Évite les dépendances à des interfaces trop larges",
                },
            ],
            "field_name_4": {
                "template_name": "synthesis_template",
                "field_name_1": "Résultat de la combinaison",
                "field_name_2": [
                    {
                        "template_name": "benefit_item",
                        "field_name_1": "Limite la surface de responsabilité d'une classe",
                    },
                    {
                        "template_name": "benefit_item",
                        "field_name_1": "Maximise la modularité du système",
                    },
                    {
                        "template_name": "benefit_item",
                        "field_name_1": "Réduit le couplage entre composants",
                    },
                    {
                        "template_name": "benefit_item",
                        "field_name_1": "Améliore la maintenabilité et l'évolutivité",
                    },
                ],
            },
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "question_template",
            "question_text": "Comment le Principe Ouvert/Fermé et le Principe d'Inversion des Dépendances se complètent-ils?",
            "visual_hint": {
                "template_name": "hint_template",
                "hint_text": "Deux principes SOLID qui travaillent ensemble pour une architecture flexible",
            },
        },
        "verso": {
            "template_name": "relationship_diagram",
            "title": "Complémentarité entre OCP et DIP",
            "relationships": [
                {
                    "template_name": "relationship_item",
                    "source": "Principe d'Inversion des Dépendances (DIP)",
                    "action": "Crée les abstractions nécessaires",
                    "target": "Interfaces et classes abstraites",
                    "description": "DIP introduit des couches d'abstraction et permet l'injection de dépendances",
                },
                {
                    "template_name": "relationship_item",
                    "source": "Principe Ouvert/Fermé (OCP)",
                    "action": "Utilise les abstractions pour",
                    "target": "Ajouter des fonctionnalités sans modification",
                    "description": "OCP s'appuie sur les abstractions créées par DIP pour étendre le code",
                },
            ],
            "synergy": {
                "template_name": "definition_template",
                "title": "Synergie OCP + DIP",
                "content": "L'extension par des abstractions (DIP) rend possible l'ajout de nouvelles fonctionnalités sans bouleversement du code existant (OCP)",
            },
            "demonstration": {
                "template_name": "sequential_steps_template",
                "title": "Démonstration de complémentarité",
                "steps": [
                    {
                        "template_name": "step_item",
                        "step_title": "DIP établit l'abstraction",
                        "step_content": "Une classe dépend d'une interface plutôt que d'une implémentation concrète",
                    },
                    {
                        "template_name": "step_item",
                        "step_title": "OCP utilise l'abstraction",
                        "step_content": "Ajouter une nouvelle implémentation de l'interface sans toucher à la classe qui l'utilise",
                    },
                    {
                        "template_name": "step_item",
                        "step_title": "Résultat",
                        "step_content": "Code ouvert à l'extension (nouvelles implémentations) et fermé à la modification (classe originale intacte)",
                    },
                ],
            },
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "question_template",
            "field_name_1": "Comment le Principe de Substitution de Liskov soutient-il le Principe d'Inversion des Dépendances?",
            "field_name_2": {
                "template_name": "hint_template",
                "field_name_1": "Deux principes SOLID qui travaillent ensemble pour une meilleure architecture",
            },
        },
        "verso": {
            "template_name": "concept_relationship_template",
            "field_name_1": "Relation de Support entre LSP et DIP",
            "field_name_2": [
                {
                    "template_name": "concept_block",
                    "field_name_1": "Rôle du Principe de Substitution de Liskov (LSP)",
                    "field_name_2": "Assure que les substitutions de types maintiennent le comportement prévu en respectant les contrats et invariants",
                    "field_name_3": "Garantit la prévisibilité comportementale",
                },
                {
                    "template_name": "concept_block",
                    "field_name_1": "Rôle du Principe d'Inversion des Dépendances (DIP)",
                    "field_name_2": "Assure que les substitutions se font via des abstractions plutôt que via des types concrets",
                    "field_name_3": "Garantit le découplage architectural",
                },
            ],
            "field_name_3": {
                "template_name": "benefit_template",
                "field_name_1": "Renforcement Mutuel",
                "field_name_2": [
                    {
                        "template_name": "benefit_item",
                        "field_name_1": "Stabilité accrue",
                        "field_name_2": "On peut remplacer une implémentation par une autre sans surprises comportementales",
                    },
                    {
                        "template_name": "benefit_item",
                        "field_name_1": "Testabilité améliorée",
                        "field_name_2": "Les abstractions permettent l'injection de dépendances et les mocks pour les tests",
                    },
                    {
                        "template_name": "benefit_item",
                        "field_name_1": "Flexibilité architecturale",
                        "field_name_2": "La combinaison LSP + DIP permet l'évolution du code sans casser les dépendances",
                    },
                ],
            },
        },
        "version": "1.0.0",
    },
    {
        "recto": {
            "template_name": "question_template",
            "field_name_1": "Quel est l'impact global de l'application conjointe de tous les principes SOLID?",
        },
        "verso": {
            "template_name": "synthesis_template",
            "field_name_1": "Impact collectif des principes SOLID",
            "field_name_2": [
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Systèmes robustes",
                    "field_name_2": "Fondations solides et fiables",
                },
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Systèmes flexibles",
                    "field_name_2": "Capacité à s'adapter aux changements",
                },
                {
                    "template_name": "benefit_item",
                    "field_name_1": "Évolution facilitée",
                    "field_name_2": "Maintenance et modifications sans régression",
                },
            ],
            "field_name_3": "Socle cohérent et renforcé",
            "field_name_4": [
                {
                    "template_name": "reinforcement_pillar",
                    "field_name_1": "Modularité",
                    "field_name_2": "SRP + ISP créent des composants indépendants et ciblés",
                },
                {
                    "template_name": "reinforcement_pillar",
                    "field_name_1": "Extensibilité",
                    "field_name_2": "OCP + DIP permettent d'ajouter sans modifier l'existant",
                },
                {
                    "template_name": "reinforcement_pillar",
                    "field_name_1": "Substitution sûre",
                    "field_name_2": "LSP garantit la compatibilité entre composants",
                },
            ],
            "field_name_5": "Architectures modulaires, maintenables et évolutives sans risques",
        },
        "version": "1.0.0",
    },
]
