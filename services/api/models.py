from sqlalchemy import Column, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(String, unique=True, nullable=False, index=True)
    source = Column(String, nullable=False)
    title = Column(String, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    raw_storage_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Fields for future phases (nullable for now)
    cleaned_text = Column(Text, nullable=True)
    word_count = Column(Text, nullable=True) # Storing as text or int? Spec said "Word count stored". Int is better.
    language = Column(String, nullable=True)
    language_confidence = Column(String, nullable=True) 
    primary_category = Column(String, nullable=True)
    topic_confidence = Column(String, nullable=True)
    summary_text = Column(Text, nullable=True)
    summary_bullets = Column(Text, nullable=True)
    embedding = Column(Vector(384))

    # Relationships
    entities = relationship("Entity", secondary="article_entities", back_populates="articles")

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(String, nullable=False)
    type = Column(String, nullable=False) # PERSON, ORG, LOC
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (UniqueConstraint('text', 'type', name='_text_type_uc'),)

    # Relationships
    articles = relationship("Article", secondary="article_entities", back_populates="entities")

class ArticleEntity(Base):
    __tablename__ = "article_entities"
    
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'), primary_key=True)
    entity_id = Column(UUID(as_uuid=True), ForeignKey('entities.id'), primary_key=True)

    
    # We can add more fields as we reach those phases to keep schema clean or add them now as nullable.
    # Spec says "Phase 1 Output: Metadata stored in Postgres".
