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
    "learning_objective": "Comprendre l'histoire profonde et multidimensionnelle de la fermentation, depuis ses premières manifestations archéologiques jusqu'à l'explication scientifique moderne de ses mécanismes microbiologiques. L'objectif est d'expliquer comment des techniques empiriques de transformation des aliments et des boissons se sont développées indépendamment dans différentes cultures, comment des preuves chimiques et matérielles permettent de reconstituer ces pratiques anciennes, et enfin comment les découvertes scientifiques des XIXe et XXe siècles ont permis d'identifier les micro-organismes responsables et de lier ces savoir-faire traditionnels à des processus biologiques bien définis. L'apprenant devra ainsi être capable de situer la fermentation dans son contexte historique, technique et scientifique, et de reconnaître les principales différences et similitudes entre types de fermentations (par ex. fermentation alcoolique, lactique, ou à l'aide de moisissures).",
    "course_sections": [
      {
        "section_title": "Origines culturelles et diversité des pratiques fermentaires",
        "section_description": "La fermentation accompagne l'alimentation humaine depuis des millénaires et se manifeste dans une grande diversité de produits culturels, allant des boissons alcoolisées antiques aux condiments et viandes fermentées contemporaines. Cette section situe la fermentation comme une pratique culturelle universelle et adaptive qui sert à conserver, transformer et diversifier les matières premières alimentaires. Elle met en lumière pourquoi et comment des sociétés différentes ont développé des procédés fermentaires distincts en fonction des ressources disponibles, des contraintes climatiques et des préférences gustatives.",
        "key_concepts": [
          {
            "concept_name": "Fermentations alimentaires traditionnelles",
            "explanation": "Les fermentations traditionnelles sont des procédés permettant la transformation biochimique d'aliments ou de boissons par l'action de micro-organismes tels que les levures, bactéries lactiques ou moisissures. Ces transformations peuvent améliorer la conservation, augmenter la valeur nutritionnelle, modifier la texture et développer des arômes complexes. Selon les environnements et les matières premières, différents types de fermentation ont émergé : fermentation alcoolique pour les boissons, fermentation lactique pour les légumes et produits laitiers, ou fermentations impliquant des moisissures pour certains grains et légumes. Ces pratiques ont souvent été développées empiriquement, par essais et erreurs, bien avant la compréhension scientifique des microbes.",
            "examples": [
              "Vin de riz néolithique (découvert dans la province du Henan) : une boisson obtenue à partir de riz, de miel et de fruits sauvages, où des moisissures et des levures ont vraisemblablement contribué à la fermentation et à la production d'alcool.",
              "Choucroute : exemple de fermentation lactique du chou au cours de laquelle des bactéries lactiques transforment les sucres en acide lactique, ce qui conserve le légume et lui confère son goût caractéristique.",
              "Hákarl (Islande) : viande de requin fermentée et séchée, illustrant une tradition où la fermentation sert à rendre comestible une ressource difficile à consommer fraîchement, en modifiant sa composition chimique et organoleptique."
            ],
            "related_media": {
              "image_url": "string",
              "image_description": "Image illustrative montrant une sélection d'aliments fermentés traditionnels (boissons et mets), permettant de visualiser la diversité des produits issus de la fermentation et de saisir les différences d'aspect et de préparation entre boissons alcoolisées, légumes lactofermentés et viandes fermentées.",
              "video_url": "string",
              "video_description": "Courte vidéo présentant des pratiques fermentaires traditionnelles dans différentes régions du monde, montrant la préparation et le résultat final de produits fermentés afin de relier la théorie aux pratiques concrètes.",
              "video_timestamp": "string"
            }
          }
        ],
        "additional_notes": "Il est important de comprendre que la fermentation n'est pas un phénomène unique mais un ensemble de procédés où la composition microbienne, la matière première et les conditions de transformation (température, aération, durée) définissent le produit final. Les mêmes principes biologiques peuvent produire des résultats très différents suivant la culture et les techniques employées, ce qui explique la grande variété des produits fermentés observés à travers le monde."
      },
      {
        "section_title": "Preuves archéologiques et archéologie moléculaire",
        "section_description": "Les recherches archéologiques et les méthodes de l'archéologie moléculaire ont permis de remonter aux origines des boissons fermentées en identifiant des résidus chimiques et des signatures moléculaires sur des poteries et autres contenants. Ces approches combinent l'analyse chimique, la palynologie, l'étude des résidus organiques et la contextualisation archéologique pour reconstituer les ingrédients et les procédés utilisés par les populations anciennes. La découverte d'indices de fermentation dans des contextes néolithiques illustre comment des pratiques alimentaires complexes existaient bien avant la compréhension scientifique des micro-organismes.",
        "key_concepts": [
          {
            "concept_name": "Étude de Patrick McGovern et preuves de vin de riz néolithique",
            "explanation": "En 2000, Patrick McGovern et ses collègues ont appliqué des méthodes d'archéologie moléculaire à des fragments de poteries néolithiques provenant du Henan, en Chine, afin d'identifier des résidus de boissons. Au lieu d'étudier la poterie comme objet, l'équipe a analysé chimiquement les traces organiques emprisonnées qui révélaient des marqueurs de produits fermentés. Les résultats ont montré des signatures chimiques compatibles avec une boisson obtenue à partir de riz, de miel et de fruits sauvages (aubépine ou raisin sauvage). Les similitudes moléculaires avec le vin de riz contemporain et la présence de marqueurs d'écume ont permis aux chercheurs de proposer que ces contenants renfermaient une boisson fermentée filtrée et probablement aidée par des moisissures qui décomposaient les sucres des grains.",
            "examples": [
              "Analyse de la céramique du Henan : détection de résidus moléculaires (acides organiques et composés aromatiques) indiquant la présence de riz fermenté mélangé à des sucres d'origine végétale comme le miel.",
              "Comparaison chimique avec le vin de riz moderne : identification de similitudes dans certains marqueurs chimiques, fournissant un lien plausible entre pratiques anciennes et techniques contemporaines de fermentation du riz."
            ],
            "related_media": {
              "image_url": "string",
              "image_description": "Photographie d'une poterie néolithique ou d'un fragment d'urne similaire à celles étudiées par les archéologues, utile pour comprendre le type de récipients utilisés pour la fermentation et le stockage des boissons.",
              "video_url": "string",
              "video_description": "Vidéo décrivant la méthode d'archéologie moléculaire, montrant comment les scientifiques prélèvent et analysent des résidus sur des céramiques anciennes pour identifier des traces de boissons fermentées.",
              "video_timestamp": "string"
            }
          },
          {
            "concept_name": "Interprétation des données archéologiques et limites",
            "explanation": "Les preuves obtenues par analyses chimiques sont puissantes mais doivent être interprétées avec prudence : les signatures moléculaires indiquent la présence de certains composants organiques, mais l'identification précise des recettes, des proportions ou du mode exact de production reste souvent fragmentaire. En outre, la contamination, la diagenèse (altération postérieure des composés organiques) et le contexte archéologique influencent les conclusions possibles. Ainsi, les résultats sont interprétés en termes de probabilité et de plausibilité culturelle plutôt qu'en certitude absolue.",
            "examples": [
              "Résidus d'écume interprétés comme indicateurs d'une boisson filtrée : cette interprétation suppose des phases de fermentation et de décantation mais ne permet pas de reconstituer exactement chaque étape de la production.",
              "Possibilité de contamination : des composés ressemblant à ceux du vin de riz peuvent parfois provenir d'autres sources végétales, d'où la nécessité d'approches multiples (analyse isotopique, comparaison ethnographique) pour renforcer les hypothèses."
            ],
            "related_media": {
              "image_url": "string",
              "image_description": "Image montrant un laboratoire d'archéologie moléculaire avec équipement d'analyse, pour illustrer les techniques modernes utilisées pour détecter et interpréter des résidus organiques anciens.",
              "video_url": "string",
              "video_description": "Séquence vidéo expliquant les précautions méthodologiques en archéologie moléculaire, incluant des illustrations des étapes d'extraction et d'analyse des résidus.",
              "video_timestamp": "string"
            }
          }
        ],
        "additional_notes": "Les études archéologiques sur la fermentation ouvrent une fenêtre sur des pratiques sociales et rituelles anciennes car boissons et aliments fermentés occupaient souvent des rôles cérémoniels, médicinaux ou sociaux. Les résultats doivent toujours être replacés dans leur contexte archéologique (emplacement du site, datation, association avec d'autres artefacts) pour construire une histoire complète et crédible des usages alimentaires anciens."
      },
      {
        "section_title": "Compréhension microbienne et avancées scientifiques",
        "section_description": "La compréhension scientifique de la fermentation est le fruit de découvertes progressives culminant au XIXe siècle, lorsque les premiers observateurs et microbiologistes ont lié l'activité microbienne à la transformation des aliments et des boissons. Cette section explique comment des observations microscopiques et des expériences contrôlées ont permis de formaliser la notion que des êtres vivants invisibles, les micro-organismes, sont les agents directs de la fermentation et que leurs activités peuvent être décrites, contrôlées et appliquées industriellement.",
        "key_concepts": [
          {
            "concept_name": "Observations de Charles Cagniard de La Tour (1835)",
            "explanation": "En 1835, Charles Cagniard de La Tour observa au microscope la multiplication des levures par bourgeonnement dans des solutions alcooliques, fournissant l'une des premières observations expérimentales directes de l'activité d'organismes microscopiques impliqués dans la production d'alcool. Ces observations ont jeté les bases expérimentales montrant que la fermentation n'était pas simplement une transformation chimique spontanée de la matière, mais impliquait des entités vivantes capables de se reproduire et de métaboliser les sucres.",
            "examples": [
              "Observation microscopique de levures dans des moûts : mise en évidence du bourgeonnement et de la croissance cellulaire associée à la production d'éthanol.",
              "Expériences de contrôle de conditions : montrer que la présence et l'activité des levures varient selon la température, la concentration en sucres et la disponibilité d'oxygène, ce qui influence le rendement et le profil aromatique."
            ],
            "related_media": {
              "image_url": "string",
              "image_description": "Image conceptuelle montrant des cellules de levure au microscope et illustrant le phénomène de bourgeonnement observé par Cagniard de La Tour.",
              "video_url": "string",
              "video_description": "Animation ou vidéo microscopique montrant la multiplication par bourgeonnement des levures dans un milieu riche en sucres, utile pour visualiser le processus biologique sous-jacent à la fermentation alcoolique.",
              "video_timestamp": "string"
            }
          },
          {
            "concept_name": "Travaux de Louis Pasteur et théorie des germes (1857)",
            "explanation": "Louis Pasteur établit au milieu du XIXe siècle que des levures étaient responsables de la fermentation alcoolique et démontra que des micro-organismes étaient liés à des processus de dégradation et de transformation organique, contribuant ainsi à la formulation de la théorie des germes pour expliquer certaines maladies. En démontrant que la contamination microbienne pouvait être contrôlée et que différentes espèces microbiennes produisaient des effets différents, Pasteur a permis la rationalisation des procédés fermentaires et l'amélioration des techniques de conservation et de sécurité alimentaire.",
            "examples": [
              "Démonstration expérimentale que l'absence de contamination microbienne empêche certaines fermentations non désirées, ouvrant la voie à la pasteurisation pour prolonger la conservation des boissons et aliments.",
              "Différenciation entre fermentation alcoolique et fermentation lactique : Pasteur a contribué à établir que différents groupes microbiaux (levures vs bactéries lactiques) conduisent à des produits finaux distincts, permettant le développement ciblé de procédés industriels."
            ],
            "related_media": {
              "image_url": "string",
              "image_description": "Portrait ou représentation historique de Louis Pasteur accompagné d'illustrations de ses expériences, montrant son rôle dans la mise en évidence du lien entre microbes et fermentation.",
              "video_url": "string",
              "video_description": "Vidéo historique expliquant les étapes majeures des travaux de Pasteur et leur impact sur la microbiologie et les pratiques alimentaires modernes.",
              "video_timestamp": "string"
            }
          },
          {
            "concept_name": "Différences biologiques entre types de fermentation",
            "explanation": "Les fermentations alcooliques, lactiques et celles impliquant des moisissures reposent sur des organismes différents et des voies métaboliques distinctes. Les levures (par ex. Saccharomyces cerevisiae) convertissent les sucres en éthanol et dioxyde de carbone lors de la fermentation alcoolique. Les bactéries lactiques transforment les sucres en acide lactique dans des processus de conservation et d'acidification. Certaines fermentations de grains ou de riz mobilisent des moisissures (koji, Aspergillus spp.) pour décomposer l'amidon en sucres fermentescibles, étape essentielle pour ensuite produire de l'alcool. Comprendre ces différences permet de choisir, contrôler et optimiser les procédés selon le produit désiré.",
            "examples": [
              "Brassage de la bière : action principale de levures alcooliques transformant le moût en bière par production d'éthanol et d'arômes spécifiques.",
              "Fabrication de yaourt ou de choucroute : utilisation de bactéries lactiques pour acidifier et conserver le produit, ce qui influence la texture et la durée de conservation.",
              "Utilisation de moisissures en fermentation du riz (sake) : rôle enzymatique des moisissures pour hydrolyser l'amidon en sucres fermentescibles, étape clé avant l'action des levures."
            ],
            "related_media": {
              "image_url": "string",
              "image_description": "Schéma comparatif des principaux types de fermentation (alcoolique, lactique, à moisissures) montrant les organismes impliqués et les produits finaux typiques pour clarifier les différences métaboliques et techniques.",
              "video_url": "string",
              "video_description": "Vidéo pédagogique décrivant les mécanismes métaboliques fondamentaux de chaque type de fermentation et illustrant des applications pratiques dans l'alimentation.",
              "video_timestamp": "string"
            }
          }
        ],
        "additional_notes": "La reconnaissance du rôle des micro-organismes a permis non seulement de comprendre la fermentation mais aussi d'en maîtriser les risques sanitaires et les rendements. Aujourd'hui, les connaissances en microbiologie sont appliquées pour améliorer les procédés traditionnels, développer des starters contrôlés et assurer la sécurité alimentaire tout en préservant les caractéristiques organoleptiques des produits."
      },
      {
        "section_title": "Repères chronologiques essentiels",
        "section_description": "Pour saisir la profondeur historique de la fermentation, il est utile de placer quelques jalons significatifs dans le temps. Cette section présente une sélection de dates clés qui illustrent la continuité et l'évolution de la pratique fermentaire, depuis les manifestations archéologiques les plus anciennes jusqu'aux découvertes scientifiques qui ont permis d'expliquer ses mécanismes.",
        "key_concepts": [
          {
            "concept_name": "Jalons historiques choisis",
            "explanation": "La chronologie des fermentations combine preuves matérielles anciennes et jalons scientifiques modernes. Des traces probables de boissons fermentées apparaissent très tôt dans l'histoire humaine, puis des observations microscopiques et des expériences contrôlées au XIXe siècle ont formalisé la compréhension des processus. Rassembler ces dates permet de voir la fermentation comme un continuum entre pratiques empiriques et connaissances scientifiques.",
            "examples": [
              "7000–5500 av. J.-C. : premières preuves de boissons fermentées en Chine, attestées par des analyses archéologiques sur des poteries, indiquant l'antériorité de ces pratiques alimentaires dans des sociétés néolithiques.",
              "1835 : observation par Charles Cagniard de La Tour de la multiplication des levures par bourgeonnement dans des solutions alcooliques, apportant des preuves visuelles précoces du rôle des micro-organismes.",
              "1857 : travaux de Louis Pasteur qui établissent la présence de levures et démontrent le rôle central des micro-organismes dans la fermentation, contribuant à la formulation de la théorie des germes et à la rationalisation des procédés alimentaires."
            ],
            "related_media": {
              "image_url": "string",
              "image_description": "Frise chronologique visuelle résumant les dates clés et les événements associés à l'histoire de la fermentation, utile pour situer rapidement les évolutions majeures.",
              "video_url": "string",
              "video_description": "Vidéo de synthèse présentant la chronologie de la fermentation, mêlant illustrations archéologiques et explications scientifiques pour relier passé et présent.",
              "video_timestamp": "string"
            }
          }
        ],
        "additional_notes": "Cette chronologie est sélective et vise à mettre en évidence des points d'inflexion conceptuels et empiriques. De nombreuses autres découvertes régionales et datations précises enrichissent ce panorama, mais ces jalons permettent de comprendre l'arc général qui va de pratiques ancestrales à une compréhension scientifique moderne."
      }
    ]
  }