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
