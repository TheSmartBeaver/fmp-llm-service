"""Local audit: actual service/models, fake LLM, no external database or network."""
import asyncio
import datetime as dt
import importlib
import sys
import types
import uuid
from types import SimpleNamespace as NS

from pathlib import Path
ROOT = str(Path(__file__).resolve().parents[1])
sys.path.insert(0, ROOT)
stub = types.ModuleType('app.chains.llm.universal_llm')
stub.create_universal_llm = lambda *_: None
sys.modules[stub.__name__] = stub
m = importlib.import_module('app.services.course_translation_service')
from sqlalchemy import create_engine, event, insert, MetaData, Text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

NOW = dt.datetime.now(dt.timezone.utc)
UID = uuid.uuid4

class RecordingDB:
    def __init__(self):
        self.added = []
        self.executed = []
    def add(self, row):
        self.added.append(row)
    def execute(self, statement):
        self.executed.append(statement)
        return NS(all=lambda: [])

def service(db=None):
    return m.CourseTranslationService(db or RecordingDB())

def topic(**kw):
    fields = dict(SKU=UID(), Title='Topic', AppUserSKU=UID(), LastUpdated=NOW,
                  IsPremium=False, IsUnpublished=False, Order=0, Path=None,
                  ParentSKU=None, GroupSKU=None, FileSKU=None, HtmlContentSKU=None,
                  CourseMaterialSKU=None, RedditUrl=None, EasterEggContentSKU=None,
                  Groups=None, HtmlContents=None, EasterEggContents=None)
    fields.update(kw)
    return NS(**fields)

def html(**kw):
    fields = dict(SKU=UID(), AppUserSKU=UID(), IsTemplated=False,
                  CardTemplatedJson='', IsAssembly=False, LastUpdated=NOW,
                  FullHtmlContent='<p>source</p>', IsFullHtml=True, Path=None,
                  Recto=None, Verso=None, Cards=[], AssemblyCategories_=[])
    fields.update(kw)
    return NS(**fields)

def group(**kw):
    fields = dict(SKU=UID(), AppUserSKU=UID(), Title='Group', Tags='',
                  LastUpdated=NOW, Path=None, ParentSKU=None, Groups=None, Cards=[])
    fields.update(kw)
    return NS(**fields)

def check(name, condition):
    assert condition, name
    print('CONFIRMED:', name)

def reproduce_groups():
    s = service()
    g = group(Cards=[NS(SKU=UID(), HtmlContents_=html())])
    s._clone_topic(topic(GroupSKU=g.SKU, Groups=g), UID(), 'Target')
    check('group cloned without its Cards/HtmlContents',
          any(isinstance(x, m.Groups) for x in s.db.added)
          and not any(isinstance(x, (m.Cards, m.HtmlContents)) for x in s.db.added))

def reproduce_quiz():
    s = service()
    q = NS(SKU=UID(), AppUserSKU=UID(), QuestionJson='{"type":"html","version":1}',
           AnswersJson='[]', ExplanationJson='[]', CorrectAnswerOrder=1,
           LastUpdated=NOW, QuizQuestionHtmlContents=[NS(Slot='question', HtmlContents=html())])
    order = NS(SKU=UID(), Order=1, QuizQuestionSKU=q.SKU, QuizQuestions_=q)
    qm = NS(SKU=UID(), AppUserSKU=UID(), LastUpdated=NOW, QuizMaterialQuestionOrders=[order])
    s._clone_quiz_material(qm)
    check('HTML quiz marker cloned without slot or HtmlContents',
          any(isinstance(x, m.QuizQuestions) for x in s.db.added)
          and not any(isinstance(x, m.HtmlContents) for x in s.db.added)
          and 'QuizQuestionHtmlContents' not in m.QuizQuestions.metadata.tables)
    check('quiz order LastUpdated absent from Python mapping',
          'LastUpdated' not in m.QuizMaterialQuestionOrders.__table__.c)
    check('quiz material link LastUpdated absent from Python mapping',
          'LastUpdated' not in m.CourseMaterialLinkedQuizzes.__table__.c)

def reproduce_group_remap():
    s = service()
    g = group()
    card = NS(SKU=UID(), AppUserSKU=UID(), Tags='', NextRevisionDateMultiplicator=1,
              LastUpdated=NOW, GroupSKU=g.SKU, MnemotechnicHint=None,
              NextRevisionDate=None, Path=None)
    s._clone_flashcard_html(html(Cards=[card]))
    s._clone_group_chain(g)
    copied = next(x for x in s.db.added if isinstance(x, m.Cards))
    check('Card.GroupSKU remains source SKU when group cloned later',
          copied.GroupSKU == g.SKU and copied.GroupSKU != s.sku_map[g.SKU])
    s = service()
    s._clone_flashcard_html(html(IsAssembly=True, AssemblyCategories_=[NS(SKU=UID())]))
    check('assembly category links ignored', not s.db.executed or all(
        statement.table.name != 'AssemblyCategoryHtmlContent'
        for statement in s.db.executed if hasattr(statement, 'table')))

async def sync_service(source_topics, target_topics):
    s = service()
    source = NS(SKU=UID(), LanguageCode='fr', LastUpdated=NOW, Title='Source', Description='Source')
    target = NS(SKU=UID(), LanguageCode='en', LastUpdated=NOW, Title='Target', Description='Target')
    s._load_topics = lambda sku: source_topics if sku == source.SKU else target_topics
    s._load_course_materials = lambda *args: []
    async def translate(texts, *_):
        return texts
    s._translate_batch = translate
    await s._sync_course(source, target, 'en')
    return s

async def reproduce_sync():
    source_parent = topic(Order=0, Path='root')
    target_parent = topic(Order=0, Path='root')
    source_parent.Groups = group(Cards=[NS(SKU=UID())])
    source_parent.GroupSKU = source_parent.Groups.SKU
    s = await sync_service([source_parent], [target_parent])
    check('sync ignores missing group/cards on existing topic', s.db.added == [])
    child = topic(Order=1, Path='root/child', ParentSKU=source_parent.SKU)
    s = await sync_service([source_parent, child], [target_parent])
    copied = next(x for x in s.db.added if isinstance(x, m.Topics))
    check('sync new child retains parent SKU from source course',
          copied.ParentSKU == source_parent.SKU and copied.ParentSKU != target_parent.SKU)
    s = await sync_service([topic(), topic()], [topic()])
    check('sync Order/Path collision masks missing topic', s.stats['topics_created'] == 0)

def reproduce_file_insert():
    engine = create_engine('sqlite:///:memory:')
    @event.listens_for(engine, 'connect')
    def fk_on(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
    tables = [m.HtmlContents.metadata.tables[n] for n in
              ['AppUsers', 'FileContents', 'HtmlContents', 'FileContentHtmlContent']]
    schema = MetaData()
    for table in tables:
        copied = table.to_metadata(schema)
        for column in copied.columns:
            # SQLite fixture only: omit PostgreSQL-specific default casts.
            column.server_default = None
    schema.create_all(engine)
    owner, file_sku = UID(), UID()
    hc = html(AppUserSKU=owner)
    with engine.begin() as conn:
        conn.execute(insert(m.HtmlContents.metadata.tables['AppUsers']).values(SKU=owner, AuthentUid='audit'))
        conn.execute(insert(m.HtmlContents.metadata.tables['FileContents']).values(
            SKU=file_sku, AppUserSKU=owner, Name='audit', Format='png', Content=b'local', LastUpdated=NOW))
        fields = {c.name: getattr(hc, c.name) for c in m.HtmlContents.__table__.columns}
        conn.execute(insert(m.HtmlContents.__table__).values(**fields))
        conn.execute(insert(m.t_FileContentHtmlContent).values(FileContentsSKU=file_sku, HtmlContentSKU=hc.SKU))
    with Session(engine, autoflush=False) as db:
        s = service(db)
        try:
            s._clone_flashcard_html(hc)
        except IntegrityError as exc:
            check('file junction inserted before pending HTML row: foreign key failure',
                  'FOREIGN KEY constraint failed' in str(exc))
            db.rollback()
        else:
            raise AssertionError('Expected foreign key error')

def reproduce_topic_file_unique():
    index = next(i for i in m.Topics.__table__.indexes if i.name == 'IX_Topics_FileSKU')
    s = service()
    file_sku = UID()
    s._clone_topic(topic(FileSKU=file_sku), UID(), 'Target')
    copied = next(x for x in s.db.added if isinstance(x, m.Topics))
    check('topic file shared despite unique Topics.FileSKU index', index.unique and copied.FileSKU == file_sku)

async def reproduce_material_cycle():
    engine = create_engine('sqlite:///:memory:')
    @event.listens_for(engine, 'connect')
    def fk_on(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
    names = ['AppUsers', 'Courses', 'Topics', 'CourseMaterials', 'Groups',
             'HtmlContents', 'EasterEggContents', 'FileContents', 'CourseMaterialHtmlContents']
    schema = MetaData()
    for name in names:
        table = m.Topics.metadata.tables[name].to_metadata(schema)
        for column in table.columns:
            column.server_default = None
        if name == 'Courses':
            column = table.c.SearchVector
            column.type = Text()
            column.computed = None
            column.server_default = None
            column.server_onupdate = None
            column.nullable = True
    schema.create_all(engine)
    owner = UID()
    with engine.begin() as conn:
        conn.execute(insert(m.Topics.metadata.tables['AppUsers']).values(SKU=owner, AuthentUid='cycle'))
    with Session(engine, autoflush=False) as db:
        s = service(db)
        t = topic(AppUserSKU=owner, CourseMaterialSKU=UID())
        material = NS(SKU=t.CourseMaterialSKU, AppUserSKU=owner, TopicSKU=t.SKU,
                      HtmlContentSKU=None, CourseMaterialHtmlContents=None, TaskId=None,
                      TemplatesUsed=None, Prompt=None, DebugDataJson=None, CreatedAt=NOW,
                      CourseMaterialLinkedQuizzes=[])
        source = NS(SKU=UID(), AppUserSKU=owner, LanguageCode='fr', Title='Source',
                    Description='Source', ImageUrl='', ImageRaw=None, CourseCode='audit',
                    FreePercent=0, IsPublished=False)
        s._load_topics = lambda *_: [t]
        s._load_course_materials = lambda *_: [material]
        async def translate(texts, *_):
            return texts
        s._translate_batch = translate
        await s._clone_course(source, 'en')
        try:
            db.flush()
        except IntegrityError as exc:
            check('mutual Topic/CourseMaterial scalar FKs fail at flush',
                  'FOREIGN KEY constraint failed' in str(exc))
            print('  failing table:', exc.statement.split('(')[0].strip())
            db.rollback()
        else:
            print('NOT REPRODUCED: Topic/CourseMaterial insertion cycle')
    with Session(engine, autoflush=False) as db:
        s = service(db)
        parent = topic(AppUserSKU=owner, Order=0)
        child = topic(AppUserSKU=owner, Order=1, ParentSKU=parent.SKU)
        s._load_topics = lambda *_: [child, parent]
        s._load_course_materials = lambda *_: []
        s._translate_batch = translate
        await s._clone_course(source, 'en')
        try:
            db.flush()
        except IntegrityError as exc:
            check('unordered topics with child first fail parent foreign key at flush',
                  'FOREIGN KEY constraint failed' in str(exc))
            db.rollback()
        else:
            print('NOT REPRODUCED: unordered topic insertion')

reproduce_groups()
reproduce_quiz()
reproduce_group_remap()
asyncio.run(reproduce_sync())
reproduce_file_insert()
reproduce_topic_file_unique()
asyncio.run(reproduce_material_cycle())
