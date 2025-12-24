#!/usr/bin/env python3
"""
Script de test pour vérifier que Celery stocke bien les résultats dans Redis.
Usage: python scripts/test_celery_result.py <task_id>
"""

import sys
import os
import redis

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery.result import AsyncResult
from app.workers.celery_app import celery

def test_task_result(task_id):
    """Teste la récupération d'un résultat de tâche Celery"""

    print(f"\n{'='*60}")
    print(f"🔍 DIAGNOSTIC CELERY TASK RESULT")
    print(f"{'='*60}\n")

    # 1. Vérifier la connexion Redis
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    print(f"📡 Connexion Redis: {redis_host}:{redis_port}")

    try:
        r = redis.Redis(host=redis_host, port=redis_port, db=1, decode_responses=True)
        r.ping()
        print("✅ Redis connecté\n")
    except Exception as e:
        print(f"❌ Erreur Redis: {e}\n")
        return

    # 2. Vérifier les clés dans Redis
    print("🔑 Clés dans Redis (db=1, backend Celery):")
    keys = r.keys(f"*{task_id}*")
    if keys:
        for key in keys:
            print(f"  - {key}")
            value = r.get(key)
            if value:
                print(f"    Valeur: {value[:200]}...")
    else:
        print(f"  ⚠️  Aucune clé trouvée pour task_id: {task_id}")
    print()

    # 3. Tester avec AsyncResult
    print(f"📦 Test AsyncResult pour task_id: {task_id}")
    task_result = AsyncResult(task_id, app=celery)

    print(f"  État (state): {task_result.state}")
    print(f"  Prêt (ready): {task_result.ready()}")
    print(f"  Succès (successful): {task_result.successful() if task_result.ready() else 'N/A'}")
    print(f"  Backend: {task_result.backend}")
    print()

    # 4. Essayer de récupérer le résultat
    if task_result.state == "SUCCESS":
        print("✅ Résultat disponible:")
        result = task_result.result
        print(f"  Type: {type(result)}")
        if isinstance(result, dict):
            print(f"  Clés: {list(result.keys())}")
            if 'supports' in result:
                print(f"  Supports count: {len(result.get('supports', []))}")
    elif task_result.state == "PENDING":
        print("⏳ Tâche en attente (PENDING)")
        print("  Note: PENDING peut signifier:")
        print("    - La tâche est vraiment en cours")
        print("    - La tâche n'existe pas")
        print("    - Le résultat a expiré")
    elif task_result.state == "FAILURE":
        print(f"❌ Tâche échouée: {task_result.info}")
    else:
        print(f"🔄 État: {task_result.state}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_celery_result.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]
    test_task_result(task_id)
