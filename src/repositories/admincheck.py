from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.team_members import TeamMembers

async def is_admin(discord_id: int, session: AsyncSession) -> bool:
    """Check if a Discord user is registered as an admin in the database."""
    stmt = select(TeamMembers).where(TeamMembers.discord_id == str(discord_id))
    result = await session.execute(stmt)
    member = result.scalar_one_or_none()
    
    if member and member.is_admin:
        return True
    return False
