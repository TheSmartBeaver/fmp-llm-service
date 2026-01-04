"""
Exemple de test pour CourseMaterialGeneratorV2.

Ce fichier montre comment utiliser le nouveau générateur qui utilise TemplateStructureGenerator.
"""

from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from app.chains.course_material_generator_v2 import CourseMaterialGeneratorV2
from app.models.dto.user_entry.user_entry_dto import UserEntryDto
from app.models.dto.user_entry.context_entry_dto import ContextEntryDto
from app.models.dto.user_entry.book_scan_entry_dto import BookScanEntryDto
from app.models.dto.user_entry.diction_entry_dto import DictionEntryDto
from app.models.dto.user_entry.img_entry_dto import ImgEntryDto
from app.models.dto.user_entry.video_entry_dto import VideoEntryDto
from app.db.session import SessionLocal
import json


def create_example_user_entry() -> UserEntryDto:
    """
    Crée un UserEntryDto d'exemple pour tester le générateur.

    Returns:
        UserEntryDto configuré avec des données de test
    """
    # Contexte
    context = ContextEntryDto(
        course="Espagnol",
        topic_path="Grammaire/Verbes/Ser et Estar",
        fc_to_modify=""
    )

    # Book scan entries
    book_scans = [
        BookScanEntryDto(
            order=1,
            raw_data="Le verbe SER: yo soy, tú eres, él/ella es, nosotros somos, vosotros sois, ellos/ellas son",
            scan_screenshot=[]
        ),
        BookScanEntryDto(
            order=3,
            raw_data="Le verbe ESTAR: yo estoy, tú estás, él/ella está, nosotros estamos, vosotros estáis, ellos/ellas están",
            scan_screenshot=[]
        )
    ]

    # Diction entries
    dictions = [
        DictionEntryDto(
            order=2,
            text_blocs=[
                "SER s'utilise pour les caractéristiques permanentes (identité, profession, origine).",
                "Exemples: Soy estudiante (je suis étudiant), Es de Madrid (il/elle est de Madrid)"
            ]
        ),
        DictionEntryDto(
            order=4,
            text_blocs=[
                "ESTAR s'utilise pour les états temporaires, les émotions et la localisation.",
                "Exemples: Estoy cansado (je suis fatigué), Está en casa (il/elle est à la maison)"
            ]
        )
    ]

    # Images
    images = [
        ImgEntryDto(
            order=5,
            img_description="Tableau comparatif des conjugaisons de SER et ESTAR",
            img_url="https://example.com/images/ser_estar_table.png"
        )
    ]

    # Vidéos
    videos = [
        VideoEntryDto(
            order=6,
            video_url="https://example.com/videos/ser_vs_estar.mp4",
            video_description="Explication vidéo des différences entre SER et ESTAR avec exemples",
            video_start_time="00:01:15"
        )
    ]

    # Créer le UserEntryDto
    user_entry = UserEntryDto(
        context_entry=context,
        book_scan_entry=book_scans,
        diction_entry=dictions,
        img_entry=images,
        video_entry=videos
    )

    return user_entry


def test_course_material_generator_v2():
    """
    Test du CourseMaterialGeneratorV2 avec des données d'exemple.
    """
    print("=" * 80)
    print("TEST: CourseMaterialGeneratorV2")
    print("=" * 80)

    # Créer une session de base de données
    db: Session = SessionLocal()

    try:
        # Charger le modèle d'embedding
        print("\n📦 Chargement du modèle d'embedding...")
        embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Créer le générateur
        print("🔧 Initialisation de CourseMaterialGeneratorV2...")
        generator = CourseMaterialGeneratorV2(
            db_session=db,
            embedding_model=embedding_model
        )

        # Créer des données d'exemple
        print("\n📝 Création des données d'exemple...")
        user_entry = create_example_user_entry()
        print(f"   - Cours: {user_entry.context_entry.course}")
        print(f"   - Sujet: {user_entry.context_entry.topic_path}")
        print(f"   - {len(user_entry.book_scan_entry)} book scans")
        print(f"   - {len(user_entry.diction_entry)} dictions")
        print(f"   - {len(user_entry.img_entry)} images")
        print(f"   - {len(user_entry.video_entry)} vidéos")

        # Générer le support de cours
        print("\n🚀 Génération du support de cours...")
        print("   Étape 1: Génération du JSON pédagogique enrichi...")
        print("   Étape 2: Mapping vers templates avec TemplateStructureGenerator...")
        print("   Étape 3: Construction du JSON final...")
        print("   Étape 4: Validation...")

        result = generator.generate_course_material(
            user_entry=user_entry,
            top_k=20,
            category_quotas={"layouts/": 5, "conceptual/": 10, "text/": 5}
        )

        # Afficher les résultats
        print("\n" + "=" * 80)
        print("✅ RÉSULTATS")
        print("=" * 80)

        print("\n📋 SUPPORT GÉNÉRÉ:")
        print(json.dumps(result["support"], indent=2, ensure_ascii=False))

        print("\n" + "=" * 80)
        print("📝 PROMPT ÉTAPE 1 (JSON Pédagogique):")
        print("=" * 80)
        print(result["prompts"]["step1_pedagogical_json"])

        print("\n" + "=" * 80)
        print("📝 PROMPT ÉTAPE 2 (Structure Templates):")
        print("=" * 80)
        print(result["prompts"]["step2_template_structure"])

        print("\n" + "=" * 80)
        print("✅ Test terminé avec succès!")
        print("=" * 80)

        return result

    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        db.close()


if __name__ == "__main__":
    test_course_material_generator_v2()
