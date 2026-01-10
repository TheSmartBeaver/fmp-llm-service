from typing import Any, Optional
import datetime
import uuid

from sqlalchemy import Boolean, CHAR, Column, DateTime, Double, ForeignKeyConstraint, Index, Integer, LargeBinary, PrimaryKeyConstraint, String, Table, Text, Uuid, text
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

    AssemblyCategories: Mapped[list['AssemblyCategories']] = relationship('AssemblyCategories', back_populates='AppUsers_')
    CardTemplates: Mapped[list['CardTemplates']] = relationship('CardTemplates', back_populates='AppUsers_')
    Courses: Mapped[list['Courses']] = relationship('Courses', back_populates='AppUsers_')
    FileContents: Mapped[list['FileContents']] = relationship('FileContents', back_populates='AppUsers_')
    Groups: Mapped[list['Groups']] = relationship('Groups', back_populates='AppUsers_')
    HtmlContents: Mapped[list['HtmlContents']] = relationship('HtmlContents', back_populates='AppUsers_')
    Cards: Mapped[list['Cards']] = relationship('Cards', back_populates='AppUsers_')
    Topics: Mapped[list['Topics']] = relationship('Topics', back_populates='AppUsers_')
    DeviceTokens: Mapped[list['DeviceTokens']] = relationship('DeviceTokens', back_populates='AppUsers_')

class HumanProofs(Base):
    __tablename__ = 'HumanProofs'
    __table_args__ = (
        PrimaryKeyConstraint('SKU', name='PK_HumanProofs'),
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    Url: Mapped[str] = mapped_column(Text, nullable=False)
    ProofType: Mapped[str] = mapped_column(Text, nullable=False)
    Date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)

class EFMigrationsHistory(Base):
    __tablename__ = '__EFMigrationsHistory'
    __table_args__ = (
        PrimaryKeyConstraint('MigrationId', name='PK___EFMigrationsHistory'),
    )

    MigrationId: Mapped[str] = mapped_column(String(150), primary_key=True)
    ProductVersion: Mapped[str] = mapped_column(String(32), nullable=False)


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


class Courses(Base):
    __tablename__ = 'Courses'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_Courses_AppUsers_AppUserSKU'),
        PrimaryKeyConstraint('SKU', name='PK_Courses'),
        Index('IX_Courses_AppUserSKU', 'AppUserSKU')
    )

    SKU: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    AppUserSKU: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    ImageUrl: Mapped[str] = mapped_column(Text, nullable=False)
    Title: Mapped[str] = mapped_column(Text, nullable=False)
    Description: Mapped[str] = mapped_column(Text, nullable=False)
    LastUpdated: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Courses')
    Topics: Mapped[list['Topics']] = relationship('Topics', back_populates='Courses_')


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

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='FileContents')
    HtmlContents: Mapped[list['HtmlContents']] = relationship('HtmlContents', secondary='FileContentHtmlContent', back_populates='FileContents_')
    Topics: Mapped[list['Topics']] = relationship('Topics', back_populates='FileContents_')


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

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Groups')
    Groups: Mapped[Optional['Groups']] = relationship('Groups', remote_side=[SKU], back_populates='Groups_reverse')
    Groups_reverse: Mapped[list['Groups']] = relationship('Groups', remote_side=[ParentSKU], back_populates='Groups')
    Cards: Mapped[list['Cards']] = relationship('Cards', back_populates='Groups_')
    Topics: Mapped[list['Topics']] = relationship('Topics', back_populates='Groups_')


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
    Path: Mapped[Optional[str]] = mapped_column(Text)
    Recto: Mapped[Optional[str]] = mapped_column(Text)
    Verso: Mapped[Optional[str]] = mapped_column(Text)

    FileContents_: Mapped[list['FileContents']] = relationship('FileContents', secondary='FileContentHtmlContent', back_populates='HtmlContents')
    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='HtmlContents')
    AssemblyCategories_: Mapped[list['AssemblyCategories']] = relationship('AssemblyCategories', secondary='AssemblyCategoryHtmlContent', back_populates='HtmlContents')
    Cards: Mapped[list['Cards']] = relationship('Cards', back_populates='HtmlContents_')
    Topics: Mapped[list['Topics']] = relationship('Topics', back_populates='HtmlContents_')


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


t_FileContentHtmlContent = Table(
    'FileContentHtmlContent', Base.metadata,
    Column('FileContentsSKU', Uuid, primary_key=True),
    Column('HtmlContentSKU', Uuid, primary_key=True),
    ForeignKeyConstraint(['FileContentsSKU'], ['FileContents.SKU'], ondelete='CASCADE', name='FK_FileContentHtmlContent_FileContents_FileContentsSKU'),
    ForeignKeyConstraint(['HtmlContentSKU'], ['HtmlContents.SKU'], ondelete='CASCADE', name='FK_FileContentHtmlContent_HtmlContents_HtmlContentSKU'),
    PrimaryKeyConstraint('FileContentsSKU', 'HtmlContentSKU', name='PK_FileContentHtmlContent'),
    Index('IX_FileContentHtmlContent_HtmlContentSKU', 'HtmlContentSKU')
)


class Topics(Base):
    __tablename__ = 'Topics'
    __table_args__ = (
        ForeignKeyConstraint(['AppUserSKU'], ['AppUsers.SKU'], ondelete='RESTRICT', name='FK_Topics_AppUsers_AppUserSKU'),
        ForeignKeyConstraint(['FileSKU'], ['FileContents.SKU'], ondelete='RESTRICT', name='FK_Topics_FileContents_FileSKU'),
        ForeignKeyConstraint(['GroupSKU'], ['Groups.SKU'], ondelete='RESTRICT', name='FK_Topics_Groups_GroupSKU'),
        ForeignKeyConstraint(['HtmlContentSKU'], ['HtmlContents.SKU'], ondelete='RESTRICT', name='FK_Topics_HtmlContents_HtmlContentSKU'),
        ForeignKeyConstraint(['ParentCourseSKU'], ['Courses.SKU'], ondelete='RESTRICT', name='FK_Topics_Courses_ParentCourseSKU'),
        ForeignKeyConstraint(['ParentSKU'], ['Topics.SKU'], ondelete='RESTRICT', name='FK_Topics_Topics_ParentSKU'),
        PrimaryKeyConstraint('SKU', name='PK_Topics'),
        Index('IX_Topics_AppUserSKU', 'AppUserSKU'),
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
    Path: Mapped[Optional[str]] = mapped_column(Text)
    ParentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    ParentCourseSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    GroupSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    FileSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    HtmlContentSKU: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='Topics')
    FileContents_: Mapped[Optional['FileContents']] = relationship('FileContents', back_populates='Topics')
    Groups_: Mapped[Optional['Groups']] = relationship('Groups', back_populates='Topics')
    HtmlContents_: Mapped[Optional['HtmlContents']] = relationship('HtmlContents', back_populates='Topics')
    Courses_: Mapped[Optional['Courses']] = relationship('Courses', back_populates='Topics')
    Topics: Mapped[Optional['Topics']] = relationship('Topics', remote_side=[SKU], back_populates='Topics_reverse')
    Topics_reverse: Mapped[list['Topics']] = relationship('Topics', remote_side=[ParentSKU], back_populates='Topics')

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
    DeviceName: Mapped[Optional[str]] = mapped_column(Text)
    IsActive: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    CreatedAt: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('NOW()'))
    UpdatedAt: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('NOW()'))
    LastUsed: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    AppUsers_: Mapped['AppUsers'] = relationship('AppUsers', back_populates='DeviceTokens')