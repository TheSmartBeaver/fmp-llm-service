from typing import Any, Optional
import datetime
import uuid

from sqlalchemy import Boolean, CHAR, Column, Computed, DateTime, Double, ForeignKeyConstraint, Identity, Index, Integer, LargeBinary, PrimaryKeyConstraint, SmallInteger, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import NullType

class Base(DeclarativeBase):
    pass


class AppUsers(Base):
    __tablename__ = 'AppUsers'
    __table_args__ = (
        PrimaryKeyConstraint('SKU', name='PK_AppUsers'),
        Index('IX_AppUsers_AuthentUid', 'AuthentUid', unique=True)
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AuthentUid: Mapped[str] = mapped_column(Text, nullable=False)
    LanguageCode: Mapped[Optional[str]] = mapped_column(Text)

    CourseMaterials: Mapped[list['CourseMaterials']] = relationship('CourseMaterials', back_populates='AppUsers_')
    Topics: Mapped[list['Topics']] = relationship('Topics', back_populates='AppUsers_')
    AppUserRoles: Mapped[list['AppUserRoles']] = relationship('AppUserRoles', back_populates='AppUsers_')
    AssemblyCategories: Mapped[list['AssemblyCategories']] = relationship('AssemblyCategories', back_populates='AppUsers_')
    CardTemplates: Mapped[list['CardTemplates']] = relationship('CardTemplates', back_populates='AppUsers_')
    CourseMaterialHtmlContents: Mapped[list['CourseMaterialHtmlContents']] = relationship('CourseMaterialHtmlContents', back_populates='AppUsers_')
    Courses: Mapped[list['Courses']] = relationship('Courses', back_populates='AppUsers_')
    DeviceTokens: Mapped[list['DeviceTokens']] = relationship('DeviceTokens', back_populates='AppUsers_')
    Downloads: Mapped[list['Downloads']] = relationship('Downloads', back_populates='AppUsers_')
    FileContents: Mapped[list['FileContents']] = relationship('FileContents', back_populates='AppUsers_')
    Groups: Mapped[list['Groups']] = relationship('Groups', back_populates='AppUsers_')
    HtmlContents: Mapped[list['HtmlContents']] = relationship('HtmlContents', back_populates='AppUsers_')
    InAppMarketingEvents: Mapped[list['InAppMarketingEvents']] = relationship('InAppMarketingEvents', back_populates='AppUsers_')
    LearningProfileEntries: Mapped[list['LearningProfileEntries']] = relationship('LearningProfileEntries', back_populates='AppUsers_')
    QuizMaterials: Mapped[list['QuizMaterials']] = relationship('QuizMaterials', back_populates='AppUsers_')
    QuizQuestions: Mapped[list['QuizQuestions']] = relationship('QuizQuestions', back_populates='AppUsers_')
    Subscriptions: Mapped[list['Subscriptions']] = relationship('Subscriptions', back_populates='AppUsers_')
    Cards: Mapped[list['Cards']] = relationship('Cards', back_populates='AppUsers_')
    EasterEggContents: Mapped[list['EasterEggContents']] = relationship('EasterEggContents', back_populates='AppUsers_')
    QuizAttempts: Mapped[list['QuizAttempts']] = relationship('QuizAttempts', back_populates='AppUsers_')


class CourseCategories(Base):
    __tablename__ = 'CourseCategories'
    __table_args__ = (
        PrimaryKeyConstraint('CategoryCode', 'LanguageCode', name='PK_CourseCategories'),
        UniqueConstraint('CategoryCode', name='AK_CourseCategories_CategoryCode')
    )

    CategoryCode: Mapped[str] = mapped_column(Text, primary_key=True)
    LanguageCode: Mapped[str] = mapped_column(Text, primary_key=True)
    Title: Mapped[str] = mapped_column(Text, nullable=False)

    CourseCategoryLinks: Mapped[list['CourseCategoryLinks']] = relationship('CourseCategoryLinks', back_populates='CourseCategories_')


class CourseMaterials(Base):
    __tablename__ = 'CourseMaterials'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_CourseMaterials_AppUsers_AppUserSKU'),
        ForeignKeyConstraint(['CourseSKU'], ['Courses.SKU'], ondelete='RESTRICT', name='FK_CourseMaterials_Courses_CourseSKU'),
        ForeignKeyConstraint(['HtmlContentSKU'], ['CourseMaterialHtmlContents.SKU'], ondelete='RESTRICT', name='FK_CourseMaterials_CourseMaterialHtmlContents_HtmlContentSKU'),
        ForeignKeyConstraint(['TopicSKU'], ['Topics.SKU'], ondelete='RESTRICT', name='FK_CourseMaterials_Topics_TopicSKU'),
        PrimaryKeyConstraint('SKU', name='PK_CourseMaterials'),
        Index('IX_CourseMaterials_AppUserSKU', 'AppUserSKU'),
        Index('IX_CourseMaterials_CourseSKU', 'CourseSKU'),
        Index('IX_CourseMaterials_HtmlContentSKU', 'HtmlContentSKU'),
        Index('IX_CourseMaterials_TopicSKU', 'TopicSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    TaskId: Mapped[Optional[str]] = mapped_column(Text)
    HtmlContentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    TopicSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    CourseSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    TemplatesUsed: Mapped[Optional[int]] = mapped_column(Integer)
    Prompt: Mapped[Optional[str]] = mapped_column(Text)
    DebugDataJson: Mapped[Optional[str]] = mapped_column(Text)
    CreatedAt: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='CourseMaterials')
    Courses: Mapped[Optional['Courses']] = relationship('Courses', back_populates='CourseMaterials_')
    CourseMaterialHtmlContents: Mapped[Optional['CourseMaterialHtmlContents']] = relationship('CourseMaterialHtmlContents', back_populates='CourseMaterials_')
    Topics: Mapped[Optional['Topics']] = relationship('Topics', foreign_keys=[TopicSKU], back_populates='CourseMaterials_')
    Topics_: Mapped[list['Topics']] = relationship('Topics', foreign_keys='[Topics.CourseMaterialSKU]', back_populates='CourseMaterials1')
    CourseMaterialLinkedQuizzes: Mapped[list['CourseMaterialLinkedQuizzes']] = relationship('CourseMaterialLinkedQuizzes', back_populates='CourseMaterials_')


class HumanProofs(Base):
    __tablename__ = 'HumanProofs'
    __table_args__ = (
        PrimaryKeyConstraint('SKU', name='PK_HumanProofs'),
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    Url: Mapped[str] = mapped_column(Text, nullable=False)
    ProofType: Mapped[str] = mapped_column(Text, nullable=False)
    Date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)


class LinkedToPromoCodes(Base):
    __tablename__ = 'LinkedToPromoCodes'
    __table_args__ = (
        PrimaryKeyConstraint('SKU', name='PK_LinkedToPromoCodes'),
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    Code: Mapped[str] = mapped_column(Text, nullable=False)
    CourseSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Langage: Mapped[str] = mapped_column(Text, nullable=False)
    MarketingDescription: Mapped[str] = mapped_column(Text, nullable=False)


class MarketingEvents(Base):
    __tablename__ = 'MarketingEvents'
    __table_args__ = (
        PrimaryKeyConstraint('SKU', name='PK_MarketingEvents'),
        Index('IX_MarketingEvents_MkIdsMarketingEventSKU', 'MkIdsMarketingEventSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    EventType: Mapped[int] = mapped_column(Integer, nullable=False)
    Date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text("'-infinity'::timestamp with time zone"))
    Email: Mapped[Optional[str]] = mapped_column(Text)
    Url: Mapped[Optional[str]] = mapped_column(Text)
    Ip: Mapped[Optional[str]] = mapped_column(Text)
    MkIdsMarketingEventSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    MarketingEventTrackingIdss_: Mapped[Optional['MarketingEventTrackingIdss']] = relationship('MarketingEventTrackingIdss', uselist=False, back_populates='MarketingEvents_')


class MarketingEventTrackingIdss(Base):
    __tablename__ = 'MarketingEventTrackingIdss'
    __table_args__ = (
        ForeignKeyConstraint(['MarketingEventSKU'], ['MarketingEvents.SKU'], ondelete='RESTRICT', name='FK_MarketingEventTrackingIdss_MarketingEvents_MarketingEventSKU'),
        PrimaryKeyConstraint('MarketingEventSKU', name='PK_MarketingEventTrackingIdss')
    )

    MarketingEventSKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    fbp: Mapped[Optional[str]] = mapped_column(Text)
    fbc: Mapped[Optional[str]] = mapped_column(Text)
    ttclid: Mapped[Optional[str]] = mapped_column(Text)
    ttp: Mapped[Optional[str]] = mapped_column(Text)
    eventId: Mapped[Optional[str]] = mapped_column(Text)

    MarketingEvents_: Mapped['MarketingEvents'] = relationship('MarketingEvents', foreign_keys=[MarketingEventSKU], back_populates='MarketingEventTrackingIdss_')


class Topics(Base):
    __tablename__ = 'Topics'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_Topics_AppUsers_AppUserSKU'),
        ForeignKeyConstraint(['CourseMaterialSKU'], ['CourseMaterials.SKU'], ondelete='RESTRICT', name='FK_Topics_CourseMaterials_CourseMaterialSKU'),
        ForeignKeyConstraint(['EasterEggContentSKU'], ['EasterEggContents.SKU'], ondelete='RESTRICT', name='FK_Topics_EasterEggContents_EasterEggContentSKU'),
        ForeignKeyConstraint(['FileSKU'], ['FileContents.SKU'], ondelete='RESTRICT', name='FK_Topics_FileContents_FileSKU'),
        ForeignKeyConstraint(['GroupSKU'], ['Groups.SKU'], ondelete='RESTRICT', name='FK_Topics_Groups_GroupSKU'),
        ForeignKeyConstraint(['HtmlContentSKU'], ['HtmlContents.SKU'], ondelete='RESTRICT', name='FK_Topics_HtmlContents_HtmlContentSKU'),
        ForeignKeyConstraint(['ParentCourseSKU'], ['Courses.SKU'], ondelete='RESTRICT', name='FK_Topics_Courses_ParentCourseSKU'),
        ForeignKeyConstraint(['ParentSKU'], ['Topics.SKU'], ondelete='RESTRICT', name='FK_Topics_Topics_ParentSKU'),
        PrimaryKeyConstraint('SKU', name='PK_Topics'),
        Index('IX_Topics_AppUserSKU', 'AppUserSKU'),
        Index('IX_Topics_CourseMaterialSKU', 'CourseMaterialSKU', unique=True),
        Index('IX_Topics_EasterEggContentSKU', 'EasterEggContentSKU', unique=True),
        Index('IX_Topics_FileSKU', 'FileSKU', unique=True),
        Index('IX_Topics_GroupSKU', 'GroupSKU', unique=True),
        Index('IX_Topics_HtmlContentSKU', 'HtmlContentSKU', unique=True),
        Index('IX_Topics_ParentCourseSKU', 'ParentCourseSKU'),
        Index('IX_Topics_ParentSKU', 'ParentSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    Title: Mapped[str] = mapped_column(Text, nullable=False)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    IsPremium: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    IsUnpublished: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    Order: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    Path: Mapped[Optional[str]] = mapped_column(Text)
    ParentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ParentCourseSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    GroupSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    FileSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    HtmlContentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    CourseMaterialSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    RedditUrl: Mapped[Optional[str]] = mapped_column(Text)
    EasterEggContentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    CourseMaterials_: Mapped[list['CourseMaterials']] = relationship('CourseMaterials', foreign_keys='[CourseMaterials.TopicSKU]', back_populates='Topics')
    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Topics')
    CourseMaterials1: Mapped[Optional['CourseMaterials']] = relationship('CourseMaterials', foreign_keys=[CourseMaterialSKU], back_populates='Topics_')
    EasterEggContents: Mapped[Optional['EasterEggContents']] = relationship('EasterEggContents', back_populates='Topics_')
    FileContents: Mapped[Optional['FileContents']] = relationship('FileContents', back_populates='Topics_')
    Groups: Mapped[Optional['Groups']] = relationship('Groups', back_populates='Topics_')
    HtmlContents: Mapped[Optional['HtmlContents']] = relationship('HtmlContents', back_populates='Topics_')
    Courses: Mapped[Optional['Courses']] = relationship('Courses', back_populates='Topics_')
    Topics: Mapped[Optional['Topics']] = relationship('Topics', remote_side=[SKU], back_populates='Topics_reverse')
    Topics_reverse: Mapped[list['Topics']] = relationship('Topics', remote_side=[ParentSKU], back_populates='Topics')
    Reviews: Mapped[list['Reviews']] = relationship('Reviews', back_populates='Topics_')


class EFMigrationsHistory(Base):
    __tablename__ = '__EFMigrationsHistory'
    __table_args__ = (
        PrimaryKeyConstraint('MigrationId', name='PK___EFMigrationsHistory'),
    )

    MigrationId: Mapped[str] = mapped_column(String(150), primary_key=True)
    ProductVersion: Mapped[str] = mapped_column(String(32), nullable=False)


class AppUserRoles(Base):
    __tablename__ = 'AppUserRoles'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='CASCADE', name='FK_AppUserRoles_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_AppUserRoles'),
        Index('IX_AppUserRoles_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Role: Mapped[int] = mapped_column(Integer, nullable=False)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='AppUserRoles')


class AssemblyCategories(Base):
    __tablename__ = 'AssemblyCategories'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_AssemblyCategories_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_AssemblyCategories'),
        Index('IX_AssemblyCategories_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Path: Mapped[str] = mapped_column(Text, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='AssemblyCategories')
    HtmlContents: Mapped[list['HtmlContents']] = relationship('HtmlContents', secondary='AssemblyCategoryHtmlContent', back_populates='AssemblyCategories_')


class CardTemplates(Base):
    __tablename__ = 'CardTemplates'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_CardTemplates_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_CardTemplates'),
        Index('IX_CardTemplates_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Path: Mapped[str] = mapped_column(Text, nullable=False)
    Template: Mapped[str] = mapped_column(Text, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    TemplateFieldsUsage: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    FullSemanticRepresentation: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    ShortSemanticRepresentation: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    IsEnabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    GrammarStructure: Mapped[str] = mapped_column(CHAR(1), nullable=False, server_default=text("' '::bpchar"))
    Embedding: Mapped[Optional[bytes]] = mapped_column(NullType)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='CardTemplates')


class CourseCategoryLinks(Base):
    __tablename__ = 'CourseCategoryLinks'
    __table_args__ = (
        ForeignKeyConstraint(['CategoryCode'], ['CourseCategories.CategoryCode'], ondelete='RESTRICT', name='FK_CourseCategoryLinks_CourseCategories_CategoryCode'),
        PrimaryKeyConstraint('CourseCode', 'CategoryCode', name='PK_CourseCategoryLinks'),
        Index('IX_CourseCategoryLinks_CategoryCode', 'CategoryCode')
    )

    CourseCode: Mapped[str] = mapped_column(Text, primary_key=True)
    CategoryCode: Mapped[str] = mapped_column(Text, primary_key=True)

    CourseCategories_: Mapped['CourseCategories'] = relationship('CourseCategories', back_populates='CourseCategoryLinks')


class CourseMaterialHtmlContents(Base):
    __tablename__ = 'CourseMaterialHtmlContents'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_CourseMaterialHtmlContents_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_CourseMaterialHtmlContents'),
        Index('IX_CourseMaterialHtmlContents_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    MaterialsJson: Mapped[Optional[str]] = mapped_column(Text)
    MaterialsJsonType: Mapped[Optional[int]] = mapped_column(Integer)

    CourseMaterials_: Mapped[list['CourseMaterials']] = relationship('CourseMaterials', back_populates='CourseMaterialHtmlContents')
    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='CourseMaterialHtmlContents')
    CourseMaterialHtmlContentFiles: Mapped[list['CourseMaterialHtmlContentFiles']] = relationship('CourseMaterialHtmlContentFiles', back_populates='CourseMaterialHtmlContents_')


class Courses(Base):
    __tablename__ = 'Courses'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_Courses_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_Courses'),
        Index('IX_Courses_AppUserSKU', 'AppUserSKU'),
        Index('IX_Courses_SearchVector', 'SearchVector')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    ImageUrl: Mapped[str] = mapped_column(Text, nullable=False)
    Title: Mapped[str] = mapped_column(Text, nullable=False)
    Description: Mapped[str] = mapped_column(Text, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    CourseCode: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    FreePercent: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text('0'))
    LanguageCode: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    SearchVector: Mapped[Any] = mapped_column(TSVECTOR, Computed('to_tsvector(\'simple\'::regconfig, ((COALESCE("Title", \'\'::text) || \' \'::text) || COALESCE("Description", \'\'::text)))', persisted=True), nullable=False)
    IsPublished: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    ImageRaw: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    CourseMaterials_: Mapped[list['CourseMaterials']] = relationship('CourseMaterials', back_populates='Courses')
    Topics_: Mapped[list['Topics']] = relationship('Topics', back_populates='Courses')
    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Courses')


class DeviceTokens(Base):
    __tablename__ = 'DeviceTokens'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='CASCADE', name='FK_DeviceTokens_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_DeviceTokens'),
        Index('IX_DeviceTokens_AppUserSKU', 'AppUserSKU'),
        Index('IX_DeviceTokens_FcmToken', 'FcmToken')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    FcmToken: Mapped[str] = mapped_column(Text, nullable=False)
    DeviceType: Mapped[str] = mapped_column(Text, nullable=False)
    IsActive: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    CreatedAt: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    UpdatedAt: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    DeviceName: Mapped[Optional[str]] = mapped_column(Text)
    LastUsed: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='DeviceTokens')


class Downloads(Base):
    __tablename__ = 'Downloads'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='CASCADE', name='FK_Downloads_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('Id', name='PK_Downloads'),
        Index('IX_Downloads_AppUserSKU_CourseCode', 'AppUserSKU', 'CourseCode', unique=True),
        Index('IX_Downloads_AppUserSKU_CourseCode_TopicSKU', 'AppUserSKU', 'CourseCode', 'TopicSKU', unique=True)
    )

    Id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    CourseCode: Mapped[str] = mapped_column(Text, nullable=False)
    DownloadedAt: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    TopicSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Downloads')


class FileContents(Base):
    __tablename__ = 'FileContents'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_FileContents_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_FileContents'),
        Index('IX_FileContents_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Name: Mapped[str] = mapped_column(Text, nullable=False)
    Format: Mapped[str] = mapped_column(Text, nullable=False)
    Content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    Path: Mapped[Optional[str]] = mapped_column(Text)

    Topics_: Mapped[list['Topics']] = relationship('Topics', back_populates='FileContents')
    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='FileContents')
    HtmlContents: Mapped[list['HtmlContents']] = relationship('HtmlContents', secondary='FileContentHtmlContent', back_populates='FileContents_')
    CourseMaterialHtmlContentFiles: Mapped[list['CourseMaterialHtmlContentFiles']] = relationship('CourseMaterialHtmlContentFiles', back_populates='FileContents_')
    EasterEggContents: Mapped[list['EasterEggContents']] = relationship('EasterEggContents', back_populates='FileContents_')


class Groups(Base):
    __tablename__ = 'Groups'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_Groups_AppUsers_AppUserSKU'),
        ForeignKeyConstraint(['ParentSKU'], ['Groups.SKU'], ondelete='RESTRICT', name='FK_Groups_Groups_ParentSKU'),
        PrimaryKeyConstraint('SKU', name='PK_Groups'),
        Index('IX_Groups_AppUserSKU', 'AppUserSKU'),
        Index('IX_Groups_ParentSKU', 'ParentSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Title: Mapped[str] = mapped_column(Text, nullable=False)
    Tags: Mapped[str] = mapped_column(Text, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    Path: Mapped[Optional[str]] = mapped_column(Text)
    ParentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    Topics_: Mapped[list['Topics']] = relationship('Topics', back_populates='Groups')
    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Groups')
    Groups: Mapped[Optional['Groups']] = relationship('Groups', remote_side=[SKU], back_populates='Groups_reverse')
    Groups_reverse: Mapped[list['Groups']] = relationship('Groups', remote_side=[ParentSKU], back_populates='Groups')
    Cards: Mapped[list['Cards']] = relationship('Cards', back_populates='Groups_')


class HtmlContents(Base):
    __tablename__ = 'HtmlContents'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_HtmlContents_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_HtmlContents'),
        Index('IX_HtmlContents_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    IsTemplated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    CardTemplatedJson: Mapped[str] = mapped_column(Text, nullable=False)
    IsAssembly: Mapped[bool] = mapped_column(Boolean, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    FullHtmlContent: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''::text"))
    IsFullHtml: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    Path: Mapped[Optional[str]] = mapped_column(Text)
    Recto: Mapped[Optional[str]] = mapped_column(Text)
    Verso: Mapped[Optional[str]] = mapped_column(Text)

    Topics_: Mapped[list['Topics']] = relationship('Topics', back_populates='HtmlContents')
    FileContents_: Mapped[list['FileContents']] = relationship('FileContents', secondary='FileContentHtmlContent', back_populates='HtmlContents')
    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='HtmlContents')
    AssemblyCategories_: Mapped[list['AssemblyCategories']] = relationship('AssemblyCategories', secondary='AssemblyCategoryHtmlContent', back_populates='HtmlContents')
    Cards: Mapped[list['Cards']] = relationship('Cards', back_populates='HtmlContents_')


class InAppMarketingEvents(Base):
    __tablename__ = 'InAppMarketingEvents'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='CASCADE', name='FK_InAppMarketingEvents_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('Id', name='PK_InAppMarketingEvents'),
        Index('IX_InAppMarketingEvents_AppUserSKU', 'AppUserSKU')
    )

    Id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    SignalCode: Mapped[str] = mapped_column(Text, nullable=False)
    EmissionDate: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    IP: Mapped[Optional[str]] = mapped_column(Text)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='InAppMarketingEvents')


class LearningProfileEntries(Base):
    __tablename__ = 'LearningProfileEntries'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='CASCADE', name='FK_LearningProfileEntries_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('LearningProfileEntrySKU', name='PK_LearningProfileEntries'),
        Index('IX_LearningProfileEntries_AppUserSKU_EntryType_Label', 'AppUserSKU', 'EntryType', 'Label', unique=True)
    )

    LearningProfileEntrySKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    EntryType: Mapped[str] = mapped_column(Text, nullable=False)
    Label: Mapped[str] = mapped_column(Text, nullable=False)
    SortOrder: Mapped[int] = mapped_column(Integer, nullable=False)
    RatingValue: Mapped[Optional[float]] = mapped_column(Double(53))

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='LearningProfileEntries')


class QuizMaterials(Base):
    __tablename__ = 'QuizMaterials'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_QuizMaterials_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_QuizMaterials'),
        Index('IX_QuizMaterials_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='QuizMaterials')
    CourseMaterialLinkedQuizzes: Mapped[list['CourseMaterialLinkedQuizzes']] = relationship('CourseMaterialLinkedQuizzes', back_populates='QuizMaterials_')
    QuizAttempts: Mapped[list['QuizAttempts']] = relationship('QuizAttempts', back_populates='QuizMaterials_')
    QuizMaterialQuestionOrders: Mapped[list['QuizMaterialQuestionOrders']] = relationship('QuizMaterialQuestionOrders', back_populates='QuizMaterials_')


class QuizQuestions(Base):
    __tablename__ = 'QuizQuestions'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_QuizQuestions_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_QuizQuestions'),
        Index('IX_QuizQuestions_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    QuestionJson: Mapped[str] = mapped_column(Text, nullable=False)
    AnswersJson: Mapped[str] = mapped_column(Text, nullable=False)
    ExplanationJson: Mapped[str] = mapped_column(Text, nullable=False)
    CorrectAnswerOrder: Mapped[int] = mapped_column(Integer, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='QuizQuestions')
    QuizMaterialQuestionOrders: Mapped[list['QuizMaterialQuestionOrders']] = relationship('QuizMaterialQuestionOrders', back_populates='QuizQuestions_')


class Reviews(Base):
    __tablename__ = 'Reviews'
    __table_args__ = (
        ForeignKeyConstraint(['TopicSKU'], ['Topics.SKU'], ondelete='RESTRICT', name='FK_Reviews_Topics_TopicSKU'),
        PrimaryKeyConstraint('SKU', name='PK_Reviews'),
        Index('IX_Reviews_TopicSKU', 'TopicSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    Rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    LanguageCode: Mapped[str] = mapped_column(Text, nullable=False)
    CourseCode: Mapped[str] = mapped_column(Text, nullable=False)
    Comment: Mapped[Optional[str]] = mapped_column(Text)
    TopicSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    Topics_: Mapped[Optional['Topics']] = relationship('Topics', back_populates='Reviews')


class Subscriptions(Base):
    __tablename__ = 'Subscriptions'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='CASCADE', name='FK_Subscriptions_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_Subscriptions'),
        Index('IX_Subscriptions_AppUserSKU', 'AppUserSKU'),
        Index('IX_Subscriptions_AppUserSKU_Platform_PurchaseToken', 'AppUserSKU', 'Platform', 'PurchaseToken', unique=True)
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Platform: Mapped[str] = mapped_column(Text, nullable=False)
    ProductId: Mapped[str] = mapped_column(Text, nullable=False)
    PurchaseToken: Mapped[str] = mapped_column(Text, nullable=False)
    IsActive: Mapped[bool] = mapped_column(Boolean, nullable=False)
    CreatedAt: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    UpdatedAt: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    ExpiresAt: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    CancelledAt: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Subscriptions')


class SynchronizationInfos(AppUsers):
    __tablename__ = 'SynchronizationInfos'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='CASCADE', name='FK_SynchronizationInfos_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('AppUserSKU', name='PK_SynchronizationInfos')
    )

    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)


t_AssemblyCategoryHtmlContent = Table(
    'AssemblyCategoryHtmlContent', Base.metadata,
    Column('AssembliesSKU', Uuid, primary_key=True),
    Column('AssemblyCategoriesSKU', Uuid, primary_key=True),
    ForeignKeyConstraint(['AssembliesSKU'], ['HtmlContents.SKU'], ondelete='CASCADE', name='FK_AssemblyCategoryHtmlContent_HtmlContents_AssembliesSKU'),
    ForeignKeyConstraint(['AssemblyCategoriesSKU'], ['AssemblyCategories.SKU'], ondelete='CASCADE', name='FK_AssemblyCategoryHtmlContent_AssemblyCategories_AssemblyCate~'),
    PrimaryKeyConstraint('AssembliesSKU', 'AssemblyCategoriesSKU', name='PK_AssemblyCategoryHtmlContent'),
    Index('IX_AssemblyCategoryHtmlContent_AssemblyCategoriesSKU', 'AssemblyCategoriesSKU')
)


class Cards(Base):
    __tablename__ = 'Cards'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_Cards_AppUsers_AppUserSKU'),
        ForeignKeyConstraint(['GroupSKU'], ['Groups.SKU'], ondelete='RESTRICT', name='FK_Cards_Groups_GroupSKU'),
        ForeignKeyConstraint(['HtmlContentSKU'], ['HtmlContents.SKU'], ondelete='RESTRICT', name='FK_Cards_HtmlContents_HtmlContentSKU'),
        PrimaryKeyConstraint('SKU', name='PK_Cards'),
        Index('IX_Cards_AppUserSKU', 'AppUserSKU'),
        Index('IX_Cards_GroupSKU', 'GroupSKU'),
        Index('IX_Cards_HtmlContentSKU', 'HtmlContentSKU', unique=True)
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Tags: Mapped[str] = mapped_column(Text, nullable=False)
    NextRevisionDateMultiplicator: Mapped[float] = mapped_column(Double(53), nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    GroupSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    HtmlContentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    MnemotechnicHint: Mapped[Optional[str]] = mapped_column(Text)
    NextRevisionDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    Path: Mapped[Optional[str]] = mapped_column(Text)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Cards')
    Groups_: Mapped[Optional['Groups']] = relationship('Groups', back_populates='Cards')
    HtmlContents_: Mapped[Optional['HtmlContents']] = relationship('HtmlContents', back_populates='Cards')


class CourseMaterialHtmlContentFiles(Base):
    __tablename__ = 'CourseMaterialHtmlContentFiles'
    __table_args__ = (
        ForeignKeyConstraint(['CourseMaterialHtmlContentSKU'], ['CourseMaterialHtmlContents.SKU'], name='FK_CourseMaterialHtmlContentFiles_CourseMaterialHtmlContents_C~'),
        ForeignKeyConstraint(['FileSKU'], ['FileContents.SKU'], name='FK_CourseMaterialHtmlContentFiles_FileContents_FileSKU'),
        PrimaryKeyConstraint('SKU', name='PK_CourseMaterialHtmlContentFiles'),
        Index('IX_CourseMaterialHtmlContentFiles_CourseMaterialHtmlContentSKU', 'CourseMaterialHtmlContentSKU'),
        Index('IX_CourseMaterialHtmlContentFiles_FileSKU', 'FileSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    FileSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    CourseMaterialHtmlContentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    CourseMaterialHtmlContents_: Mapped[Optional['CourseMaterialHtmlContents']] = relationship('CourseMaterialHtmlContents', back_populates='CourseMaterialHtmlContentFiles')
    FileContents_: Mapped[Optional['FileContents']] = relationship('FileContents', back_populates='CourseMaterialHtmlContentFiles')


class CourseMaterialLinkedQuizzes(Base):
    __tablename__ = 'CourseMaterialLinkedQuizzes'
    __table_args__ = (
        ForeignKeyConstraint(['CourseMaterialSKU'], ['CourseMaterials.SKU'], ondelete='RESTRICT', name='FK_CourseMaterialLinkedQuizzes_CourseMaterials_CourseMaterialS~'),
        ForeignKeyConstraint(['QuizMaterialSKU'], ['QuizMaterials.SKU'], ondelete='RESTRICT', name='FK_CourseMaterialLinkedQuizzes_QuizMaterials_QuizMaterialSKU'),
        PrimaryKeyConstraint('SKU', name='PK_CourseMaterialLinkedQuizzes'),
        Index('IX_CourseMaterialLinkedQuizzes_CourseMaterialSKU', 'CourseMaterialSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    QuizMaterialSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    CourseMaterialSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    CourseMaterials_: Mapped[Optional['CourseMaterials']] = relationship('CourseMaterials', back_populates='CourseMaterialLinkedQuizzes')
    QuizMaterials_: Mapped[Optional['QuizMaterials']] = relationship('QuizMaterials', back_populates='CourseMaterialLinkedQuizzes')


class EasterEggContents(Base):
    __tablename__ = 'EasterEggContents'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_EasterEggContents_AppUsers_AppUserSKU'),
        ForeignKeyConstraint(['FileSKU'], ['FileContents.SKU'], ondelete='RESTRICT', name='FK_EasterEggContents_FileContents_FileSKU'),
        PrimaryKeyConstraint('SKU', name='PK_EasterEggContents'),
        Index('IX_EasterEggContents_AppUserSKU', 'AppUserSKU'),
        Index('IX_EasterEggContents_FileSKU', 'FileSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    Title: Mapped[Optional[str]] = mapped_column(Text)
    BodyText: Mapped[Optional[str]] = mapped_column(Text)
    FileSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    Topics_: Mapped[list['Topics']] = relationship('Topics', back_populates='EasterEggContents')
    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='EasterEggContents')
    FileContents_: Mapped[Optional['FileContents']] = relationship('FileContents', back_populates='EasterEggContents')


t_FileContentHtmlContent = Table(
    'FileContentHtmlContent', Base.metadata,
    Column('FileContentsSKU', Uuid, primary_key=True),
    Column('HtmlContentSKU', Uuid, primary_key=True),
    ForeignKeyConstraint(['FileContentsSKU'], ['FileContents.SKU'], ondelete='CASCADE', name='FK_FileContentHtmlContent_FileContents_FileContentsSKU'),
    ForeignKeyConstraint(['HtmlContentSKU'], ['HtmlContents.SKU'], ondelete='CASCADE', name='FK_FileContentHtmlContent_HtmlContents_HtmlContentSKU'),
    PrimaryKeyConstraint('FileContentsSKU', 'HtmlContentSKU', name='PK_FileContentHtmlContent'),
    Index('IX_FileContentHtmlContent_HtmlContentSKU', 'HtmlContentSKU')
)


class QuizAttempts(Base):
    __tablename__ = 'QuizAttempts'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_QuizAttempts_AppUsers_AppUserSKU'),
        ForeignKeyConstraint(['QuizMaterialSKU'], ['QuizMaterials.SKU'], ondelete='RESTRICT', name='FK_QuizAttempts_QuizMaterials_QuizMaterialSKU'),
        PrimaryKeyConstraint('SKU', name='PK_QuizAttempts'),
        Index('IX_QuizAttempts_AppUserSKU', 'AppUserSKU'),
        Index('IX_QuizAttempts_QuizMaterialSKU', 'QuizMaterialSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    Score: Mapped[int] = mapped_column(Integer, nullable=False)
    TotalQuestions: Mapped[int] = mapped_column(Integer, nullable=False)
    CreatedAt: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)
    QuizMaterialSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='QuizAttempts')
    QuizMaterials_: Mapped[Optional['QuizMaterials']] = relationship('QuizMaterials', back_populates='QuizAttempts')


class QuizMaterialQuestionOrders(Base):
    __tablename__ = 'QuizMaterialQuestionOrders'
    __table_args__ = (
        ForeignKeyConstraint(['QuizMaterialSKU'], ['QuizMaterials.SKU'], ondelete='RESTRICT', name='FK_QuizMaterialQuestionOrders_QuizMaterials_QuizMaterialSKU'),
        ForeignKeyConstraint(['QuizQuestionSKU'], ['QuizQuestions.SKU'], ondelete='RESTRICT', name='FK_QuizMaterialQuestionOrders_QuizQuestions_QuizQuestionSKU'),
        PrimaryKeyConstraint('SKU', name='PK_QuizMaterialQuestionOrders'),
        Index('IX_QuizMaterialQuestionOrders_QuizQuestionSKU', 'QuizQuestionSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    Order: Mapped[int] = mapped_column(Integer, nullable=False)
    QuizMaterialSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    QuizQuestionSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    QuizMaterials_: Mapped[Optional['QuizMaterials']] = relationship('QuizMaterials', back_populates='QuizMaterialQuestionOrders')
    QuizQuestions_: Mapped[Optional['QuizQuestions']] = relationship('QuizQuestions', back_populates='QuizMaterialQuestionOrders')
