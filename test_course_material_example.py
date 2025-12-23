"""
Exemple de test pour la génération de supports de cours.

Ce fichier montre comment appeler l'endpoint /course_material/generate_CELERY
avec un UserEntryDto d'exemple.
"""

import requests
import json

# URL de l'API (à adapter selon votre configuration)
API_URL = "http://127.0.0.1:8003"

# Construire un UserEntryDto d'exemple
user_entry_data = {
    "context_entry": {
        "course": "Biologie",
        "topic_path": "Cellule/Photosynthèse",
        "fc_to_modify": ""
    },
    "book_scan_entry": [
        {
            "order": 1,
            "raw_data": "La photosynthèse est le processus par lequel les plantes vertes et certaines autres organismes transforment l'énergie lumineuse en énergie chimique. Ce processus se déroule principalement dans les chloroplastes, des organites présents dans les cellules végétales.",
            "scan_screenshot": []
        },
        {
            "order": 3,
            "raw_data": "Les produits de la photosynthèse sont le glucose (C6H12O6) et l'oxygène (O2). Le glucose est utilisé par la plante pour sa croissance et son développement, tandis que l'oxygène est rejeté dans l'atmosphère.",
            "scan_screenshot": []
        }
    ],
    "diction_entry": [
        {
            "order": 2,
            "text_blocs": [
                "Le processus de photosynthèse se déroule en deux grandes phases :",
                "1. Les réactions lumineuses (phase claire) qui se produisent dans les thylakoïdes",
                "2. Le cycle de Calvin (phase sombre) qui se produit dans le stroma du chloroplaste"
            ]
        }
    ],
    "img_entry": [
        {
            "order": 4,
            "img_description": "Schéma détaillé d'un chloroplaste montrant les thylakoïdes et le stroma",
            "img_url": "https://example.com/images/chloroplaste.png"
        }
    ],
    "video_entry": [
        {
            "order": 5,
            "video_url": "https://example.com/videos/photosynthese.mp4",
            "video_description": "Animation 3D du processus de photosynthèse",
            "video_start_time": "00:02:30"
        }
    ]
}

def test_course_material_generation():
    """
    Test de génération de support de cours via l'API.
    """
    print("🚀 Envoi de la requête de génération de support de cours...")
    print(f"📝 Contexte : {user_entry_data['context_entry']['course']} - {user_entry_data['context_entry']['topic_path']}")

    # Appel à l'endpoint
    response = requests.post(
        f"{API_URL}/course_material/generate_CELERY",
        json=user_entry_data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Tâche lancée avec succès !")
        print(f"📋 Task ID: {result['task_id']}")
        print(f"📊 Status: {result['status']}")
        print("\n💡 Pour récupérer le résultat :")
        print(f"   - Écouter le canal Redis 'course_material_events'")
        print(f"   - Filtrer par task_id: {result['task_id']}")
        return result
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(f"📄 Détails: {response.text}")
        return None

def test_health_check():
    """
    Test de l'endpoint de santé.
    """
    print("\n🏥 Vérification de la santé du service...")

    response = requests.get(f"{API_URL}/course_material/health")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Service opérationnel !")
        print(f"📊 Détails: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"❌ Service non disponible: {response.status_code}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Test de génération de support de cours")
    print("=" * 60)

    # Test du health check
    test_health_check()

    print("\n" + "=" * 60)

    # Test de génération
    test_course_material_generation()

    print("\n" + "=" * 60)
    print("\n📌 Note : Assurez-vous que :")
    print("   1. Le serveur FastAPI est lancé (uvicorn app.main:app)")
    print("   2. Celery worker est en cours d'exécution")
    print("   3. Redis est accessible")
    print("   4. PostgreSQL avec pgvector est configuré")
    print("=" * 60)
