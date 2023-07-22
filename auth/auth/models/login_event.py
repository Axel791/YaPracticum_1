import uuid
import datetime

from sqlalchemy import Column, String, Enum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from auth.db.base_class import Base


class LoginEvent(Base):
    __tablename__ = 'login_events'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    timestamp = Column(DateTime, default=datetime.utcnow)
    login_success = Column(Boolean, nullable=False)

    user = relationship('User')