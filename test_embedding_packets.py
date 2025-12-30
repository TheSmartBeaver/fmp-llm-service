#!/usr/bin/env python3
"""
Script de test pour vérifier la création des paquets d'embedding.
"""
import json
from app.utils.structure_process import create_embedding_packets

# JSON d'exemple similaire à celui fourni par l'utilisateur
sample_json = {
    "structure": {
        "sujet_principal": "Archéologie moléculaire et histoire de la fermentation",
        "synthese_introductive": "Comment les traces chimiques révèlent l'histoire des boissons fermentées",
        "archeologie_moleculaire": {
            "etude_de_cas_chine": {
                "chercheur": "Dr. Patrick McGovern",
                "objet_etude": "Poterie néolithique",
                "decouverte_majeure": "Résidus de bière vieille de 9000 ans",
                "processus_chimique_presume": "Fermentation de riz, miel et fruits"
            },
            "hypothese_egypte": "Utilisation de dattes pour brasser"
        },
        "evolution_scientifique": {
            "transition_savoir": "Du mythe à la science expérimentale",
            "theorie_cle": "Théorie microbienne de Pasteur"
        },
        "chronologie_historique": [
            {
                "periode": "Néolithique",
                "evenement": "Premières traces de fermentation",
                "annee": "7000 av. J.-C.",
                "savant": "Inconnu",
                "decouverte": "Bière primitive en Mésopotamie"
            },
            {
                "periode": "Antiquité égyptienne",
                "evenement": "Industrialisation du brassage",
                "annee": "3000 av. J.-C.",
                "savant": "Inconnu",
                "decouverte": "Brasseries à grande échelle"
            },
            {
                "periode": "XIXe siècle",
                "evenement": "Révolution scientifique",
                "annee": "1857",
                "savant": "Louis Pasteur",
                "decouverte": "Théorie microbienne de la fermentation"
            }
        ]
    }
}

def main():
    print("=" * 80)
    print("TEST: Création des paquets d'embedding")
    print("=" * 80)

    # Créer les paquets
    packets = create_embedding_packets(sample_json)

    print(f"\n✓ Nombre de paquets créés: {len(packets)}\n")

    # Afficher chaque paquet
    for i, packet in enumerate(packets, 1):
        print(f"{'=' * 80}")
        print(f"PAQUET {i} - Type: {packet['type'].upper()}")
        print(f"{'=' * 80}")
        print(f"Contexte: {packet['context'] if packet['context'] else '(racine)'}")
        print(f"\nClés ({len(packet['keys'])}):")
        for key in packet['keys']:
            print(f"  - {key}")
        print(f"\nTexte pour embedding:")
        print(f"  {packet['text']}")
        print()

    # Afficher un résumé
    print(f"{'=' * 80}")
    print("RÉSUMÉ")
    print(f"{'=' * 80}")
    macro_count = sum(1 for p in packets if p['type'] == 'macro')
    micro_count = sum(1 for p in packets if p['type'] == 'micro')
    print(f"Paquets macro: {macro_count}")
    print(f"Paquets micro: {micro_count}")
    print(f"Total: {len(packets)}")

    # Vérifications
    print(f"\n{'=' * 80}")
    print("VÉRIFICATIONS")
    print(f"{'=' * 80}")

    checks = []

    # Vérifier qu'on a au moins 1 paquet macro
    if macro_count >= 1:
        checks.append("✓ Au moins 1 paquet macro créé")
    else:
        checks.append("✗ ERREUR: Aucun paquet macro")

    # Vérifier qu'on a des paquets micro
    if micro_count >= 1:
        checks.append(f"✓ {micro_count} paquet(s) micro créé(s)")
    else:
        checks.append("✗ ERREUR: Aucun paquet micro")

    # Vérifier que tous les paquets ont du texte
    if all(p['text'] for p in packets):
        checks.append("✓ Tous les paquets ont du texte")
    else:
        checks.append("✗ ERREUR: Certains paquets n'ont pas de texte")

    # Vérifier que tous les paquets ont des clés
    if all(len(p['keys']) > 0 for p in packets):
        checks.append("✓ Tous les paquets ont des clés")
    else:
        checks.append("✗ ERREUR: Certains paquets n'ont pas de clés")

    for check in checks:
        print(check)

    print()

    # Retourner le statut
    all_passed = all('✓' in check for check in checks)
    if all_passed:
        print("🎉 Tous les tests sont passés!")
        return 0
    else:
        print("❌ Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    exit(main())
