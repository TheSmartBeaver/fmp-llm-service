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

shit_test_4 = {
    "success": True,
    "html_supports": {
        "course": '```html\n<div style="font-family: system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 40px 20px; background-color: #f9f9f9;">\n  <header style="margin-bottom: 40px; border-bottom: 3px solid #0066cc; padding-bottom: 20px;">\n    <h1 style="margin: 0 0 15px 0; color: #1a1a1a; font-size: 2em; line-height: 1.3;">Structuration pédagogique des contenus éducatifs</h1>\n    <p style="margin: 0; color: #666; font-size: 0.95em; font-weight: 500;">Groupe : Course</p>\n  </header>\n\n  <section style="margin-bottom: 35px;">\n    <h2 style="color: #0066cc; font-size: 1.4em; margin-top: 0; margin-bottom: 15px; border-left: 4px solid #0066cc; padding-left: 15px;">Résumé</h2>\n    <p style="color: #333; line-height: 1.8; font-size: 1em; margin: 0;">Ce module présente une approche systématique pour transformer des notes brutes en un contenu pédagogique structuré au format JSON. On y détaille pourquoi cette structuration est bénéfique, comment organiser les informations par thèmes logiques et comment intégrer de manière cohérente des supports multimédias pour enrichir l\'expérience d\'apprentissage. L\'objectif est de rendre les contenus plus lisibles, réutilisables et accessibles, tout en évitant les contenus d\'évaluation et les exercices, conformément aux principes pédagogiques décrits.</p>\n  </section>\n\n  <section style="margin-bottom: 35px;">\n    <h2 style="color: #0066cc; font-size: 1.4em; margin-top: 0; margin-bottom: 15px; border-left: 4px solid #0066cc; padding-left: 15px;">Prérequis</h2>\n    <p style="color: #333; line-height: 1.8; font-size: 1em; margin: 0;">Avoir des notes de cours brutes et une compréhension générale des objectifs d\'apprentissage visés par le module.</p>\n  </section>\n\n  <section>\n    <h2 style="color: #0066cc; font-size: 1.4em; margin-top: 0; margin-bottom: 20px; border-left: 4px solid #0066cc; padding-left: 15px;">Objectifs d\'apprentissage</h2>\n    <ol style="margin: 0; padding-left: 25px; list-style-position: outside;">\n      <li style="margin-bottom: 18px; color: #333; line-height: 1.8; font-size: 1em;">\n        <strong>Comprendre</strong> les principes fondamentaux de la conversion de notes brutes en un format structuré qui soutient l\'apprentissage durable.\n      </li>\n      <li style="margin-bottom: 18px; color: #333; line-height: 1.8; font-size: 1em;">\n        <strong>Savoir regrouper</strong> les informations en thèmes logiques et établir des liens explicites entre concepts pour favoriser la compréhension et la mémorisation.\n      </li>\n      <li style="margin-bottom: 18px; color: #333; line-height: 1.8; font-size: 1em;">\n        <strong>Maîtriser</strong> l\'intégration sémantique des médias disponibles (images et vidéos) afin d\'enrichir le cadre didactique sans perturber le flux pédagogique.\n      </li>\n      <li style="color: #333; line-height: 1.8; font-size: 1em;">\n        <strong>Adopter</strong> des pratiques descriptives et contextuelles qui évitent les phrases trop courtes et favorisent une narration pédagogique riche et accessible.\n      </li>\n    </ol>\n  </section>\n</div>\n```',
        "subjectPath": '```html\n<div style="font-family: system-ui, sans-serif; max-width: 900px; margin: 0; padding: 24px; background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px;">\n  \n  <div style="margin-bottom: 28px;">\n    <h2 style="margin: 0 0 12px 0; font-size: 14px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Groupe</h2>\n    <p style="margin: 0; font-size: 16px; color: #1f2937; font-weight: 500;">subjectPath</p>\n  </div>\n\n  <div style="margin-bottom: 28px; padding-bottom: 24px; border-bottom: 1px solid #e5e7eb;">\n    <h3 style="margin: 0 0 12px 0; font-size: 13px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Chemin pédagogique</h3>\n    <p style="margin: 0; font-size: 15px; color: #374151; line-height: 1.6;">Fondements <span style="color: #9ca3af;">&gt;</span> Structuration du contenu <span style="color: #9ca3af;">&gt;</span> Conception pédagogique</p>\n  </div>\n\n  <div style="margin-bottom: 28px; padding-bottom: 24px; border-bottom: 1px solid #e5e7eb;">\n    <h3 style="margin: 0 0 12px 0; font-size: 13px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Objectif pédagogique</h3>\n    <p style="margin: 0; font-size: 15px; color: #374151; line-height: 1.6;">Transposer des notes brutes en une structure réutilisable et évolutive, facilitant la compréhension et la maintenance du contenu.</p>\n  </div>\n\n  <div>\n    <h3 style="margin: 0 0 16px 0; font-size: 13px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px;">Contextes d\'application</h3>\n    <ol style="margin: 0; padding-left: 24px; font-size: 15px; color: #374151; line-height: 1.8;">\n      <li style="margin-bottom: 12px;">Utiliser une structure cohérente pour différents publics et niveaux de compétence.</li>\n      <li>Relier clairement les concepts entre eux pour montrer les relations de cause à effet, d\'exemple à règle, et d\'application à contexte.</li>\n    </ol>\n  </div>\n\n</div>\n```',
        "sections[0]": '```html\n<div style="font-family: system-ui, sans-serif; max-width: 900px; margin: 0; padding: 24px; background-color: #f9f9f9; border-left: 4px solid #2563eb;">\n  <header style="margin-bottom: 24px;">\n    <h1 style="margin: 0 0 8px 0; color: #1f2937; font-size: 28px; font-weight: 600;">Cadre conceptuel et objectifs d\'apprentissage</h1>\n    <div style="height: 2px; background: linear-gradient(90deg, #2563eb, transparent); width: 80px; margin-top: 12px;"></div>\n  </header>\n  \n  <article style="background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 20px;">\n    <section style="margin-bottom: 20px;">\n      <h2 style="color: #374151; font-size: 16px; font-weight: 600; margin: 0 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">Description</h2>\n      \n      <p style="color: #4b5563; line-height: 1.7; margin: 0 0 16px 0; font-size: 15px;">\n        Dans ce cadre, on expose pourquoi la structuration des notes est essentielle pour favoriser la compréhension sur le long terme. On précise que le formatage en JSON offre une base adaptable où les catégories génériques permettent d\'organiser les informations sans se lier à des contenus spécifiques.\n      </p>\n      \n      <p style="color: #4b5563; line-height: 1.7; margin: 0; font-size: 15px;">\n        Cette approche facilite la réutilisation, la mise à jour et le déploiement du contenu dans différents contextes pédagogiques, tout en clarifiant les objectifs d\'apprentissage qui guident la profondeur des explications et le choix des détails à fournir.\n      </p>\n    </section>\n    \n    <footer style="margin-top: 20px; padding-top: 16px; border-top: 1px solid #f0f0f0;">\n      <span style="display: inline-block; background-color: #eff6ff; color: #1e40af; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 500;">Section 1</span>\n    </footer>\n  </article>\n</div>\n```',
        "sections[1]": '```html\n<div style="font-family: system-ui, sans-serif; max-width: 900px; margin: 0 auto; padding: 32px; background-color: #f9f9f9; border-radius: 8px;">\n  <header style="margin-bottom: 32px; border-bottom: 2px solid #0066cc; padding-bottom: 16px;">\n    <h1 style="margin: 0 0 12px 0; color: #003d99; font-size: 28px; font-weight: 700;">Organisation et relations entre concepts</h1>\n    <p style="margin: 0; color: #666; font-size: 14px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Section 2</p>\n  </header>\n\n  <main>\n    <section style="background-color: white; padding: 24px; border: 1px solid #ddd; border-radius: 6px; line-height: 1.8;">\n      <h2 style="color: #0066cc; font-size: 18px; margin-top: 0; margin-bottom: 16px; font-weight: 600;">Description</h2>\n      \n      <p style="color: #333; margin: 0 0 16px 0; font-size: 16px;">Cette section met en lumière <strong>l\'importance de regrouper les informations par thèmes logiques</strong> et de rendre explicites les relations entre idées.</p>\n\n      <h3 style="color: #1a1a1a; font-size: 16px; margin: 24px 0 12px 0; font-weight: 600;">Points clés couverts</h3>\n      <ul style="margin: 0 0 16px 0; padding-left: 24px; color: #333;">\n        <li style="margin-bottom: 10px;">Similarités entre concepts</li>\n        <li style="margin-bottom: 10px;">Différences et contrastes</li>\n        <li style="margin-bottom: 10px;">Dépendances et relations causales</li>\n        <li style="margin-bottom: 10px;">Construction d\'une carte cognitive robuste</li>\n      </ul>\n\n      <h3 style="color: #1a1a1a; font-size: 16px; margin: 24px 0 12px 0; font-weight: 600;">Types de relations explorées</h3>\n      <ul style="margin: 0 0 16px 0; padding-left: 24px; color: #333;">\n        <li style="margin-bottom: 10px;"><strong>Comparaison</strong> : mise en évidence des similitudes et différences</li>\n        <li style="margin-bottom: 10px;"><strong>Extension</strong> : approfondissement et élargissement des concepts</li>\n        <li style="margin-bottom: 10px;"><strong>Interdépendance</strong> : connexions mutuelles et influences réciproques</li>\n      </ul>\n\n      <p style="color: #333; margin: 16px 0 0 0; font-size: 16px;">Ces relations sont articulées dans la structure JSON pour <strong>soutenir la cohérence du discours pédagogique</strong> et faciliter la compréhension systématique des concepts.</p>\n\n      <div style="background-color: #f0f7ff; border-left: 4px solid #0066cc; padding: 16px; margin-top: 24px; border-radius: 4px;">\n        <p style="margin: 0; color: #003d99; font-size: 14px; font-weight: 500;">📌 Note pédagogique : Cette section ne contient pas d\'exercices ou d\'évaluations. Elle fournit les fondations conceptuelles et méthodologiques nécessaires pour structurer efficacement une base de connaissances.</p>\n      </div>\n    </section>\n  </main>\n</div>\n```',
        "sections[2]": '```html\n<div style="font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; background-color: #f9f9f9; border-radius: 8px;">\n  <header style="margin-bottom: 2rem; border-bottom: 3px solid #0066cc; padding-bottom: 1.5rem;">\n    <h1 style="margin: 0; color: #0066cc; font-size: 2rem; line-height: 1.3;">Intégration des médias et accessibilité</h1>\n    <p style="margin: 0.5rem 0 0 0; color: #666; font-size: 0.95rem; font-weight: 500;">Section 3 • Thème pédagogique</p>\n  </header>\n\n  <main style="line-height: 1.8; color: #333;">\n    <section style="margin-bottom: 1.5rem;">\n      <h2 style="color: #0066cc; font-size: 1.3rem; margin: 0 0 1rem 0;">Description</h2>\n      \n      <article style="background-color: white; padding: 1.5rem; border-left: 4px solid #0066cc; border-radius: 4px;">\n        <p style="margin: 0 0 1rem 0;">On détaille l\'apport des supports disponibles pour enrichir l\'expérience d\'apprentissage. L\'image et la vidéo servent de <strong>médiateurs visuels et temporels</strong> qui clarifient les explications et ancrent les concepts dans des exemples concrets.</p>\n        \n        <p style="margin: 0;">On explique comment référencer ces médias de manière sémantique dans le parcours pédagogique, en indiquant des <strong>URLs pertinentes</strong> et des <strong>repères temporels</strong> lorsque nécessaire, afin que l\'apprenant puisse accéder rapidement aux ressources sans rompre le flux pédagogique et sans détourner l\'attention de l\'objectif éducatif.</p>\n      </article>\n    </section>\n\n    <section style="margin-top: 2rem; padding: 1.5rem; background-color: #e6f2ff; border-radius: 4px;">\n      <h3 style="color: #0066cc; margin: 0 0 1rem 0; font-size: 1.1rem;">Points clés</h3>\n      <ul style="margin: 0; padding-left: 1.5rem; color: #333;">\n        <li style="margin-bottom: 0.75rem;">Médias comme vecteurs de clarification et de concrétisation</li>\n        <li style="margin-bottom: 0.75rem;">Référencement sémantique dans le parcours pédagogique</li>\n        <li style="margin-bottom: 0.75rem;">Utilisation d\'URLs pertinentes et de repères temporels</li>\n        <li style="margin-bottom: 0;">Continuité du flux pédagogique et maintien de la concentration</li>\n      </ul>\n    </section>\n  </main>\n</div>\n```',
        "sections[3]": '```html\n<div style="font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #2c5aa0;">\n  <header style="margin-bottom: 2rem;">\n    <h1 style="font-size: 1.75rem; color: #1a1a1a; margin: 0 0 0.5rem 0;">Bonnes pratiques et recommandations</h1>\n    <div style="height: 3px; width: 60px; background: linear-gradient(to right, #2c5aa0, #5a9fd4); border-radius: 2px; margin: 1rem 0;"></div>\n  </header>\n\n  <article style="line-height: 1.8; color: #333;">\n    <p style="font-size: 1rem; margin-bottom: 1.5rem;">Cette dernière partie propose des pratiques qui favorisent une structuration claire et évolutive.</p>\n\n    <section style="margin: 2rem 0;">\n      <h2 style="font-size: 1.25rem; color: #2c5aa0; margin-bottom: 1rem;">Principes clés</h2>\n      <ul style="list-style-position: inside; margin: 0; padding-left: 1.5rem;">\n        <li style="margin-bottom: 0.75rem;">Privilégier des descriptions <strong>développées et contextuelles</strong></li>\n        <li style="margin-bottom: 0.75rem;">Éviter les formulations trop brèves qui limitent la compréhension</li>\n        <li style="margin-bottom: 0.75rem;">Assurer que chaque section peut être comprise de manière <strong>autonome</strong> tout en s\'inscrivant dans l\'ensemble du module</li>\n      </ul>\n    </section>\n\n    <section style="margin: 2rem 0; padding: 1.25rem; background-color: #e8f0f8; border-radius: 6px; border-left: 3px solid #2c5aa0;">\n      <h2 style="font-size: 1.25rem; color: #2c5aa0; margin-top: 0;">Points importants à retenir</h2>\n      <ul style="list-style-position: inside; margin: 0; padding-left: 1.5rem;">\n        <li style="margin-bottom: 0.75rem;"><strong>Absence d\'exercices ou de quiz</strong> dans ce cadre pédagogique</li>\n        <li style="margin-bottom: 0.75rem;">Importance d\'une <strong>narration explicative riche et accessible</strong></li>\n        <li>Une narration qui <strong>soutient l\'apprentissage</strong> tout au long du module</li>\n      </ul>\n    </section>\n  </article>\n</div>\n```',
        "media": '```html\n<div style="font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 8px;">\n  <h1 style="color: #1a1a1a; margin-bottom: 30px; font-size: 28px; border-bottom: 3px solid #0066cc; padding-bottom: 10px;">Ressources Média</h1>\n  \n  <section style="margin-bottom: 40px;">\n    <h2 style="color: #0066cc; font-size: 20px; margin-bottom: 20px;">Images</h2>\n    <article style="background-color: white; border: 1px solid #ddd; border-radius: 6px; padding: 20px; margin-bottom: 15px;">\n      <h3 style="color: #333; font-size: 16px; margin-top: 0;">Image 1</h3>\n      <dl style="margin: 15px 0; line-height: 1.8;">\n        <dt style="font-weight: bold; color: #555; margin-top: 10px;">URL:</dt>\n        <dd style="margin-left: 0; color: #0066cc; word-break: break-all;">https://example.org/image1.jpg</dd>\n        \n        <dt style="font-weight: bold; color: #555; margin-top: 10px;">Texte alternatif:</dt>\n        <dd style="margin-left: 0; color: #333;">Illustration conceptuelle liée à la structuration pédagogique</dd>\n        \n        <dt style="font-weight: bold; color: #555; margin-top: 10px;">Notes d\'utilisation:</dt>\n        <dd style="margin-left: 0; color: #666; font-style: italic;">Intégrée dans la section sur les relations entre concepts pour fournir un repère visuel des interconnexions.</dd>\n      </dl>\n    </article>\n  </section>\n  \n  <section>\n    <h2 style="color: #0066cc; font-size: 20px; margin-bottom: 20px;">Vidéos</h2>\n    <article style="background-color: white; border: 1px solid #ddd; border-radius: 6px; padding: 20px; margin-bottom: 15px;">\n      <h3 style="color: #333; font-size: 16px; margin-top: 0;">Vidéo 1</h3>\n      <dl style="margin: 15px 0; line-height: 1.8;">\n        <dt style="font-weight: bold; color: #555; margin-top: 10px;">URL:</dt>\n        <dd style="margin-left: 0; color: #0066cc; word-break: break-all;">https://example.org/video1.mp4</dd>\n        \n        <dt style="font-weight: bold; color: #555; margin-top: 10px;">Début:</dt>\n        <dd style="margin-left: 0; color: #333;">00:00:00</dd>\n        \n        <dt style="font-weight: bold; color: #555; margin-top: 10px;">Légende:</dt>\n        <dd style="margin-left: 0; color: #333;">Introduction visuelle à la structure pédagogique et à son utilité.</dd>\n        \n        <dt style="font-weight: bold; color: #555; margin-top: 10px;">Notes d\'utilisation:</dt>\n        <dd style="margin-left: 0; color: #666; font-style: italic;">Utilisée comme ressource d\'ouverture pour présenter les objectifs et l\'architecture du module.</dd>\n      </dl>\n    </article>\n  </section>\n</div>\n```',
    },
    "pedagogical_json": {
        "course": {
            "title": "Structuration pédagogique des contenus éducatifs",
            "summary": "Ce module présente une approche systématique pour transformer des notes brutes en un contenu pédagogique structuré au format JSON. On y détaille pourquoi cette structuration est bénéfique, comment organiser les informations par thèmes logiques et comment intégrer de manière cohérente des supports multimédias pour enrichir l’expérience d’apprentissage. L’objectif est de rendre les contenus plus lisibles, réutilisables et accessibles, tout en évitant les contenus d’évaluation et les exercices, conformément aux principes pédagogiques décrits.",
            "prerequisites": "Avoir des notes de cours brutes et une compréhension générale des objectifs d’apprentissage visés par le module.",
            "learningObjectives": [
                "Comprendre les principes fondamentaux de la conversion de notes brutes en un format structuré qui soutient l’apprentissage durable.",
                "Savoir regrouper les informations en thèmes logiques et établir des liens explicites entre concepts pour favoriser la compréhension et la mémorisation.",
                "Maîtriser l’intégration sémantique des médias disponibles (images et vidéos) afin d’enrichir le cadre didactique sans perturber le flux pédagogique.",
                "Adopter des pratiques descriptives et contextuelles qui évitent les phrases trop courtes et favorisent une narration pédagogique riche et accessible.",
            ],
        },
        "subjectPath": {
            "path": "Fondements > Structuration du contenu > Conception pédagogique",
            "focus": "Transposer des notes brutes en une structure réutilisable et évolutive, facilitant la compréhension et la maintenance du contenu.",
            "contexts": [
                "Utiliser une structure cohérente pour différents publics et niveaux de compétence.",
                "Relier clairement les concepts entre eux pour montrer les relations de cause à effet, d’exemple à règle, et d’application à contexte.",
            ],
        },
        "sections": [
            {
                "theme": {
                    "name": "Cadre conceptuel et objectifs d'apprentissage",
                    "description": "Dans ce cadre, on expose pourquoi la structuration des notes est essentielle pour favoriser la compréhension sur le long terme. On précise que le formatage en JSON offre une base adaptable où les catégories génériques permettent d’organiser les informations sans se lier à des contenus spécifiques. Cette approche facilite la réutilisation, la mise à jour et le déploiement du contenu dans différents contextes pédagogiques, tout en clarifiant les objectifs d’apprentissage qui guident la profondeur des explications et le choix des détails à fournir.",
                }
            },
            {
                "theme": {
                    "name": "Organisation et relations entre concepts",
                    "description": "Cette section met en lumière l’importance de regrouper les informations par thèmes logiques et de rendre explicites les relations entre idées. On décrit comment les similarités, les différences et les dépendances entre concepts aident à construire une carte cognitive robuste. On illustre comment articuler des liens tels que comparaison, extension et interdépendance dans la structure JSON, en fournissant des scénarios d’usage qui montrent comment ces relations soutiennent la cohérence du discours pédagogique, sans introduire d’exercices ou d’évaluations.",
                }
            },
            {
                "theme": {
                    "name": "Intégration des médias et accessibilité",
                    "description": "On détaille l’apport des supports disponibles pour enrichir l’expérience d’apprentissage. L’image et la vidéo servent de médiateurs visuels et temporels qui clarifient les explications et ancrent les concepts dans des exemples concrets. On explique comment référencer ces médias de manière sémantique dans le parcours pédagogique, en indiquant des URLs pertinentes et des repères temporels lorsque nécessaire, afin que l’apprenant puisse accéder rapidement aux ressources sans rompre le flux pédagogique et sans détourner l’attention de l’objectif éducatif.",
                }
            },
            {
                "theme": {
                    "name": "Bonnes pratiques et recommandations",
                    "description": "Cette dernière partie propose des pratiques qui favorisent une structuration claire et évolutive: privilégier des descriptions développées et contextuelles, éviter les formulations trop brèves qui limitent la compréhension, et assurer que chaque section peut être comprise de manière autonome tout en s’inscrivant dans l’ensemble du module. On rappelle l’absence d’exercices ou de quiz dans ce cadre et l’importance d’une narration explicative riche et accessible qui soutient l’apprentissage.",
                }
            },
        ],
        "media": {
            "images": [
                {
                    "id": "Image 1",
                    "url": "https://example.org/image1.jpg",
                    "altText": "Illustration conceptuelle liée à la structuration pédagogique",
                    "usageNotes": "Intégrée dans la section sur les relations entre concepts pour fournir un repère visuel des interconnexions.",
                }
            ],
            "videos": [
                {
                    "id": "Vidéo 1",
                    "url": "https://example.org/video1.mp4",
                    "start": "00:00:00",
                    "caption": "Introduction visuelle à la structure pédagogique et à son utilité.",
                    "usageNotes": "Utilisée comme ressource d’ouverture pour présenter les objectifs et l’architecture du module.",
                }
            ],
        },
    },
    "debug_info": {
        "pedagogical_prompt": 'System: Tu es un expert pédagogue spécialisé dans la structuration de contenu éducatif.\n\nCONTEXTE PÉDAGOGIQUE:\n- Cours: string\n- Chemin du sujet: string\n\nMÉDIAS DISPONIBLES:\nIMAGES DISPONIBLES:\n  - Image 1: string (URL: string)\n\nVIDÉOS DISPONIBLES:\n  - Vidéo 1: string (URL: string, Début: string)\n\nTa mission : transformer des notes de cours brutes en un JSON structuré OPTIMAL pour l\'apprentissage.\n\nRÈGLES CRITIQUES:\n1. ✅ Crée des explications COMPLÈTES et CONTEXTUALISÉES (plusieurs phrases développées)\n2. ✅ NE fais PAS de phrases trop courtes - développe les concepts avec du contexte\n3. ✅ Ajoute du contexte pour faciliter la compréhension (pourquoi, comment, dans quel cas)\n4. ✅ Regroupe les informations par thèmes logiques et cohérents\n5. ✅ Explicite les liens entre les concepts (similitudes, différences, relations)\n6. ✅ Enrichis avec des exemples concrets et pertinents\n7. ✅ Intègre les références aux médias disponibles de manière sémantique\n8. 🚫 INTERDICTION ABSOLUE: NE crée PAS d\'exercices, questions, QCM, quiz ou évaluations\n9. ✅ Utilise un langage clair et pédagogique, adapté à l\'apprentissage\n10. ⚠️ RÈGLE STRUCTURELLE CRITIQUE: Les clés (noms de propriétés) du JSON ne doivent JAMAIS représenter des valeurs ou du contenu réel\n    - ❌ INTERDIT: {"Principe de responsabilité unique": "explication..."}\n    - ❌ INTERDIT: {"SRP": "définition...", "OCP": "définition..."}\n    - ✅ CORRECT: {"concepts": [{"name": "Principe de responsabilité unique", "explanation": "..."}]}\n    - ✅ CORRECT: {"principles": [{"acronym": "SRP", "definition": "..."}]}\n    - Les clés doivent être des CATÉGORIES ou des RÔLES génériques, jamais des valeurs spécifiques\n\nHuman: Voici les notes de cours brutes à transformer en JSON pédagogique optimal:\n\nCONTENU TEXTUEL:\nstring\n\nstring\n\nGénère le JSON structuré en suivant STRICTEMENT les règles ci-dessus. Développe les explications, ajoute du contexte, ne fais pas de phrases courtes.',
        "path_to_value_map": {
            "course->title": "Structuration pédagogique des contenus éducatifs",
            "course->summary": "Ce module présente une approche systématique pour transformer des notes brutes en un contenu pédagogique structuré au format JSON. On y détaille pourquoi cette structuration est bénéfique, comment organiser les informations par thèmes logiques et comment intégrer de manière cohérente des supports multimédias pour enrichir l’expérience d’apprentissage. L’objectif est de rendre les contenus plus lisibles, réutilisables et accessibles, tout en évitant les contenus d’évaluation et les exercices, conformément aux principes pédagogiques décrits.",
            "course->prerequisites": "Avoir des notes de cours brutes et une compréhension générale des objectifs d’apprentissage visés par le module.",
            "course->learningObjectives[0]": "Comprendre les principes fondamentaux de la conversion de notes brutes en un format structuré qui soutient l’apprentissage durable.",
            "course->learningObjectives[1]": "Savoir regrouper les informations en thèmes logiques et établir des liens explicites entre concepts pour favoriser la compréhension et la mémorisation.",
            "course->learningObjectives[2]": "Maîtriser l’intégration sémantique des médias disponibles (images et vidéos) afin d’enrichir le cadre didactique sans perturber le flux pédagogique.",
            "course->learningObjectives[3]": "Adopter des pratiques descriptives et contextuelles qui évitent les phrases trop courtes et favorisent une narration pédagogique riche et accessible.",
            "subjectPath->path": "Fondements > Structuration du contenu > Conception pédagogique",
            "subjectPath->focus": "Transposer des notes brutes en une structure réutilisable et évolutive, facilitant la compréhension et la maintenance du contenu.",
            "subjectPath->contexts[0]": "Utiliser une structure cohérente pour différents publics et niveaux de compétence.",
            "subjectPath->contexts[1]": "Relier clairement les concepts entre eux pour montrer les relations de cause à effet, d’exemple à règle, et d’application à contexte.",
            "sections[0]->theme->name": "Cadre conceptuel et objectifs d'apprentissage",
            "sections[0]->theme->description": "Dans ce cadre, on expose pourquoi la structuration des notes est essentielle pour favoriser la compréhension sur le long terme. On précise que le formatage en JSON offre une base adaptable où les catégories génériques permettent d’organiser les informations sans se lier à des contenus spécifiques. Cette approche facilite la réutilisation, la mise à jour et le déploiement du contenu dans différents contextes pédagogiques, tout en clarifiant les objectifs d’apprentissage qui guident la profondeur des explications et le choix des détails à fournir.",
            "sections[1]->theme->name": "Organisation et relations entre concepts",
            "sections[1]->theme->description": "Cette section met en lumière l’importance de regrouper les informations par thèmes logiques et de rendre explicites les relations entre idées. On décrit comment les similarités, les différences et les dépendances entre concepts aident à construire une carte cognitive robuste. On illustre comment articuler des liens tels que comparaison, extension et interdépendance dans la structure JSON, en fournissant des scénarios d’usage qui montrent comment ces relations soutiennent la cohérence du discours pédagogique, sans introduire d’exercices ou d’évaluations.",
            "sections[2]->theme->name": "Intégration des médias et accessibilité",
            "sections[2]->theme->description": "On détaille l’apport des supports disponibles pour enrichir l’expérience d’apprentissage. L’image et la vidéo servent de médiateurs visuels et temporels qui clarifient les explications et ancrent les concepts dans des exemples concrets. On explique comment référencer ces médias de manière sémantique dans le parcours pédagogique, en indiquant des URLs pertinentes et des repères temporels lorsque nécessaire, afin que l’apprenant puisse accéder rapidement aux ressources sans rompre le flux pédagogique et sans détourner l’attention de l’objectif éducatif.",
            "sections[3]->theme->name": "Bonnes pratiques et recommandations",
            "sections[3]->theme->description": "Cette dernière partie propose des pratiques qui favorisent une structuration claire et évolutive: privilégier des descriptions développées et contextuelles, éviter les formulations trop brèves qui limitent la compréhension, et assurer que chaque section peut être comprise de manière autonome tout en s’inscrivant dans l’ensemble du module. On rappelle l’absence d’exercices ou de quiz dans ce cadre et l’importance d’une narration explicative riche et accessible qui soutient l’apprentissage.",
            "media->images[0]->id": "Image 1",
            "media->images[0]->url": "https://example.org/image1.jpg",
            "media->images[0]->altText": "Illustration conceptuelle liée à la structuration pédagogique",
            "media->images[0]->usageNotes": "Intégrée dans la section sur les relations entre concepts pour fournir un repère visuel des interconnexions.",
            "media->videos[0]->id": "Vidéo 1",
            "media->videos[0]->url": "https://example.org/video1.mp4",
            "media->videos[0]->start": "00:00:00",
            "media->videos[0]->caption": "Introduction visuelle à la structure pédagogique et à son utilité.",
            "media->videos[0]->usageNotes": "Utilisée comme ressource d’ouverture pour présenter les objectifs et l’architecture du module.",
        },
        "path_groups": [
            "course",
            "subjectPath",
            "sections[0]",
            "sections[1]",
            "sections[2]",
            "sections[3]",
            "media",
        ],
        "num_groups": 7,
        "num_paths": 28,
    },
}
