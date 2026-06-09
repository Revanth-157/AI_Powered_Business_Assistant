"""
User service - handles user management and authentication.
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid

from database.models import UserModel, ApiKeyModel, AuditLogModel
from schemas.schemas import UserCreate, UserUpdate, UserResponse
from auth import hash_password, verify_password, create_api_key_token

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management."""
    
    @staticmethod
    def create_user(
        db: Session,
        user_create: UserCreate,
        accessible_regions: list = None
    ) -> UserResponse:
        """Create a new user."""
        
        # Check if user exists
        existing = db.query(UserModel).filter(
            (UserModel.email == user_create.email) |
            (UserModel.username == user_create.username)
        ).first()
        
        if existing:
            raise ValueError("User with this email or username already exists")
        
        # Create user
        user = UserModel(
            id=str(uuid.uuid4()),
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password=hash_password(user_create.password),
            accessible_regions=accessible_regions or ["North", "South", "East", "West"],
            role="analyst"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created user {user.username}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
        """Get user by email."""
        return db.query(UserModel).filter(UserModel.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
        """Get user by username."""
        return db.query(UserModel).filter(UserModel.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[UserModel]:
        """Get user by ID."""
        return db.query(UserModel).filter(UserModel.id == user_id).first()
    
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[UserModel]:
        """Authenticate user with email/password."""
        
        user = UserService.get_user_by_email(db, email)
        
        if not user or not verify_password(password, user.hashed_password):
            # Log failed attempt
            UserService.log_audit(db, None, "login", "user", None, False, ip_address, "Invalid credentials")
            return None
        
        if not user.is_active:
            UserService.log_audit(db, user.id, "login", "user", None, False, ip_address, "User inactive")
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Log successful login
        UserService.log_audit(db, user.id, "login", "user", user.id, True, ip_address)
        
        logger.info(f"User {user.username} authenticated")
        return user
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: str,
        user_update: UserUpdate
    ) -> Optional[UserResponse]:
        """Update user profile."""
        
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        if user_update.full_name:
            user.full_name = user_update.full_name
        
        if user_update.password:
            user.hashed_password = hash_password(user_update.password)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        
        logger.info(f"Updated user {user.username}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
    
    @staticmethod
    def log_audit(
        db: Session,
        user_id: Optional[str],
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        status: bool = True,
        ip_address: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Log audit event."""
        
        audit = AuditLogModel(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status="success" if status else "failure",
            ip_address=ip_address,
            error_message=error_message
        )
        
        db.add(audit)
        db.commit()


class ApiKeyService:
    """Service for API key management."""
    
    @staticmethod
    def create_api_key(
        db: Session,
        user_id: str,
        name: str,
        permissions: list,
        expires_in_days: Optional[int] = None
    ) -> dict:
        """Create a new API key."""
        
        # Generate key
        key_token = create_api_key_token(user_id, name)
        from auth import hash_password
        key_hash = hash_password(key_token)
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Store hashed key
        api_key = ApiKeyModel(
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            permissions=permissions,
            expires_at=expires_at
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        logger.info(f"Created API key '{name}' for user {user_id}")
        
        # Return response with plain key (only time it's shown)
        return {
            "id": api_key.id,
            "name": api_key.name,
            "key": key_token,  # Plain key - only shown once!
            "permissions": api_key.permissions,
            "created_at": api_key.created_at
        }
    
    @staticmethod
    def revoke_api_key(
        db: Session,
        user_id: str,
        key_id: str
    ) -> bool:
        """Revoke an API key."""
        
        api_key = db.query(ApiKeyModel).filter(
            ApiKeyModel.id == key_id,
            ApiKeyModel.user_id == user_id
        ).first()
        
        if not api_key:
            return False
        
        api_key.is_active = False
        db.commit()
        
        logger.info(f"Revoked API key {key_id}")
        return True
    
    @staticmethod
    def list_api_keys(
        db: Session,
        user_id: str
    ) -> list:
        """List all API keys for a user (without showing the key)."""
        
        keys = db.query(ApiKeyModel).filter(
            ApiKeyModel.user_id == user_id
        ).all()
        
        return [
            {
                "id": k.id,
                "name": k.name,
                "permissions": k.permissions,
                "is_active": k.is_active,
                "created_at": k.created_at,
                "expires_at": k.expires_at,
                "last_used_at": k.last_used_at
            }
            for k in keys
        ]
