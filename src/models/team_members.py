from sqlalchemy import Boolean, Column, String, Uuid, DateTime, func
import uuid
from src.lib import db

class TeamMembers(db.BaseModel):
    """
    Maps to team_members table.
    """
    __tablename__ = "team_members"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    discord_id = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False, server_default='false')
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())