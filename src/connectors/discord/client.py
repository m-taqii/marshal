import discord
from discord import app_commands
from discord.ext import commands

from src.lib.config import get_settings
from src.repositories.admincheck import is_admin

settings = get_settings()

def require_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild and interaction.guild.owner_id == interaction.user.id:
            return True
            
        async with interaction.client.db() as session:
            return await is_admin(interaction.user.id, session)
    return app_commands.check(predicate)


class GithubCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._owner = None
        
    async def get_owner(self):
        if not self._owner:
            user = await self.bot.github.get_authenticated_user()
            self._owner = user["login"]
        return self._owner

    @app_commands.command(name="ping", description="test command")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message("pong")

    @app_commands.command(name="add_member", description="Register a new team member in the database")
    @require_admin()
    async def add_member(self, interaction: discord.Interaction, user: discord.Member, name: str, is_admin: bool = False):
        await interaction.response.defer()
        try:
            from src.models.team_members import TeamMembers
            async with interaction.client.db() as session:
                member = TeamMembers(
                    discord_id=str(user.id),
                    name=name,
                    is_admin=is_admin
                )
                session.add(member)
                await session.commit()
            await interaction.followup.send(f"Successfully added {user.mention} to the database! Admin privileges: {is_admin}")
        except Exception as e:
            await interaction.followup.send(f"Failed to add member: {e}")

    @app_commands.command(name="assign", description="Assign an issue to a maintainer")
    @require_admin()
    async def assign(self, interaction: discord.Interaction, repo: str, issue_number: int, username: str):
        await interaction.response.defer()
        try:
            owner = await self.get_owner()
            await self.bot.github.assign_issue(owner, repo, issue_number, username)
            await interaction.followup.send(f"Assigned #{issue_number} to {username} in {repo}")
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="unassign", description="Unassign an issue from a maintainer")
    @require_admin()
    async def unassign(self, interaction: discord.Interaction, repo: str, issue_number: int, username: str):
        await interaction.response.defer()
        try:
            owner = await self.get_owner()
            await self.bot.github.unassign_issue(owner, repo, issue_number, username)
            await interaction.followup.send(f"Unassigned {username} from #{issue_number} in {repo}")
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="label", description="Label an issue")
    @require_admin()
    async def label(self, interaction: discord.Interaction, repo: str, issue_number: int, label: str):
        await interaction.response.defer()
        try:
            owner = await self.get_owner()
            await self.bot.github.add_label(owner, repo, issue_number, label)
            await interaction.followup.send(f"Labeled #{issue_number} with {label} in {repo}")
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="unlabel", description="Remove a label from an issue")
    @require_admin()
    async def unlabel(self, interaction: discord.Interaction, repo: str, issue_number: int, label: str):
        await interaction.response.defer()
        try:
            owner = await self.get_owner()
            await self.bot.github.remove_label(owner, repo, issue_number, label)
            await interaction.followup.send(f"Removed {label} from #{issue_number} in {repo}")
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="comment", description="Comment on an issue")
    @require_admin()
    async def comment(self, interaction: discord.Interaction, repo: str, issue_number: int, comment: str):
        await interaction.response.defer()
        try:
            owner = await self.get_owner()
            await self.bot.github.post_comment(owner, repo, issue_number, comment)
            await interaction.followup.send(f"Commented on #{issue_number} in {repo}")
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="close", description="Close an issue")
    @require_admin()
    async def close(self, interaction: discord.Interaction, repo: str, issue_number: int):
        await interaction.response.defer()
        try:
            owner = await self.get_owner()
            await self.bot.github.close_issue(owner, repo, issue_number)
            await interaction.followup.send(f"Closed #{issue_number} in {repo}")
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")

    @app_commands.command(name="reopen", description="Reopen an issue")
    @require_admin()
    async def reopen(self, interaction: discord.Interaction, repo: str, issue_number: int):
        await interaction.response.defer()
        try:
            owner = await self.get_owner()
            await self.bot.github.reopen_issue(owner, repo, issue_number)
            await interaction.followup.send(f"Reopened #{issue_number} in {repo}")
        except Exception as e:
            await interaction.followup.send(f"Failed: {e}")


class DiscordClient(commands.Bot):
    def __init__(self, github_client, db):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.github = github_client
        self.db = db

    async def setup_hook(self):
        await self.add_cog(GithubCommands(self))
        if settings.app_env == "development":
            guild = discord.Object(id=settings.discord_dev_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
    
    async def start(self):
        await super().start(settings.discord_bot_token)
    
    async def stop(self):
        await super().close()
        self.github = None
        self.db = None

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Process standard commands first
        await self.process_commands(message)

        is_dm = isinstance(message.channel, discord.DMChannel)
        if self.user.mentioned_in(message) or is_dm:
            # Determine if the user is an admin
            is_user_admin = False
            if message.guild and message.guild.owner_id == message.author.id:
                is_user_admin = True
            else:
                async with self.db() as session:
                    from src.repositories.admincheck import is_admin
                    is_user_admin = await is_admin(message.author.id, session)
            
            agent_system_prompt = (
                "You are a helpful AI assistant managing a GitHub repository. "
                f"The user speaking to you {'IS an admin' if is_user_admin else 'is NOT an admin'}. "
                "If the user is NOT an admin, you MUST refuse to perform any actions that modify the repository, "
                "and instead only answer questions or provide guidance."
            )
            
            # TODO: Pass `agent_system_prompt` into AI agent here!
