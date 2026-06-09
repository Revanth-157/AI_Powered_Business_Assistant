"""
SQLAlchemy database models for FMCG AI Assistant.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()


class UserModel(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    
    # Permissions
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), default="analyst")  # analyst, manager, admin
    accessible_regions = Column(JSON, default=list)  # RLS: regions user can access
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    sessions = relationship("SessionModel", back_populates="user")
    conversations = relationship("ConversationModel", back_populates="user")
    reports = relationship("ReportModel", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class SessionModel(Base):
    """Chat session model."""
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session metadata
    title = Column(String(255))
    is_active = Column(Boolean, default=True)
    context_data = Column(JSON, default=dict)  # Stores filters, intent, etc.
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)  # TTL for session
    
    # Relationships
    user = relationship("UserModel", back_populates="sessions")
    conversations = relationship("ConversationModel", back_populates="session")
    
    def __repr__(self):
        return f"<Session {self.id}>"


class ConversationModel(Base):
    """Individual conversation turn (message pair)."""
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Message content
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text)
    
    # Processing
    intent = Column(String(100))  # PROMO_PERFORMANCE, INVENTORY_MOVEMENT, etc.
    entities = Column(JSON)  # Extracted entities
    sql_query = Column(Text)  # Generated SQL
    
    # Results
    kpis = Column(JSON)  # KPI results
    insights = Column(JSON)  # Generated insights
    visualizations = Column(JSON)  # Chart specs
    
    # Metadata
    confidence_score = Column(Float)  # 0.0-1.0
    processing_time_ms = Column(Integer)  # How long to process
    error_message = Column(Text)  # If error occurred
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    session = relationship("SessionModel", back_populates="conversations")
    user = relationship("UserModel", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation {self.id}>"


class ReportModel(Base):
    """Generated report model."""
    __tablename__ = "reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), index=True)
    
    # Report content
    title = Column(String(255), nullable=False)
    summary = Column(Text)
    executive_summary = Column(Text)
    
    # Data
    kpis = Column(JSON)  # All KPIs in report
    insights = Column(JSON)  # All insights
    visualizations = Column(JSON)  # All charts
    
    # Report metadata
    intent = Column(String(100))
    report_type = Column(String(50), default="standard")  # standard, custom, scheduled
    
    # Sharing
    is_shared = Column(Boolean, default=False)
    shared_with = Column(JSON, default=list)  # User IDs
    is_public = Column(Boolean, default=False)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="reports")
    
    def __repr__(self):
        return f"<Report {self.id}>"


class ApiKeyModel(Base):
    """API key for programmatic access."""
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Key info
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)  # Hashed
    
    # Permissions
    permissions = Column(JSON, default=list)  # ["chat", "analytics", "reports"]
    scopes = Column(JSON, default=list)  # Rate limit scopes
    
    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Optional expiration
    
    def __repr__(self):
        return f"<ApiKey {self.name}>"


class AuditLogModel(Base):
    """Audit trail for compliance."""
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    
    # Action
    action = Column(String(100), nullable=False)  # login, query, export, share
    resource_type = Column(String(100))  # session, report, analytics
    resource_id = Column(String(36))
    
    # Details
    details = Column(JSON)  # Additional context
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    
    # Status
    status = Column(String(50))  # success, failure
    error_message = Column(Text)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action}>"


class CacheModel(Base):
    """Query result caching."""
    __tablename__ = "cache"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    
    # Data
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    result = Column(JSON, nullable=False)
    
    # TTL
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Metadata
    hit_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Cache {self.cache_key}>"
