# backend/app/db/models.py
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, JSON, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    storage_key = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    status = Column(String, nullable=False, default="UPLOADED")
    title = Column(String, nullable=True)
    page_count = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    pages = relationship("Page", back_populates="document", cascade="all, delete-orphan")
    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "document_pages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSON, nullable=False, default={})

    document = relationship("Document", back_populates="pages")
    sections = relationship("Section", back_populates="page")
    chunks = relationship("Chunk", back_populates="page")

class Section(Base):
    __tablename__ = "document_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_id = Column(UUID(as_uuid=True), ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String, nullable=False)
    level = Column(Integer, nullable=False)
    section_path = Column(String, nullable=True)
    metadata_json = Column("metadata", JSON, nullable=False, default={})

    document = relationship("Document", back_populates="sections")
    page = relationship("Page", back_populates="sections")
    chunks = relationship("Chunk", back_populates="section")

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_id = Column(UUID(as_uuid=True), ForeignKey("document_pages.id", ondelete="SET NULL"), nullable=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("document_sections.id", ondelete="SET NULL"), nullable=True)
    
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    
    embedding = Column(Vector) 
    search_vector = Column(TSVECTOR)
    metadata_json = Column("metadata", JSON, nullable=False, default={})
    
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")
    page = relationship("Page", back_populates="chunks")
    section = relationship("Section", back_populates="chunks")