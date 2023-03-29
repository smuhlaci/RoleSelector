import discord
from discord import RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Bot
from discord.commands import SlashCommandGroup
from tinydb import TinyDB, Query
import logging

DB_NAME = 'role_reactions_db.json'


class Reactions(commands.Cog):
    """
    This instance handles all reaction role events.
    """
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    reactionGroup = SlashCommandGroup("reaction", "Reactions comes with roles")

    async def process_reaction(self, payload: RawReactionActionEvent, r_type=None) -> None:
        reactions_db = TinyDB(DB_NAME).table("reactions")
        data = Query()

        reaction_data = reactions_db.get((data.message == payload.message_id) & (data.message.emoji_name == payload.emoji.name))

        if reaction_data is not None:
            guild = self.bot.get_guild(payload.guild_id)
            user = await guild.fetch_member(payload.user_id)
            role_id = reaction_data.get('role_id')
            role = guild.get_role(role_id)
            if role is None:
                self.logger.warning(f"Couldn't find a role with {role_id} ID but it contains in database."
                                    f" Message ID: {payload.message_id} Emoji name: {payload.emoji.name}")
                self.logger.warning("Not performing any action as result.")
            elif r_type == "add":
                await user.add_roles(role)
            elif r_type == "remove":
                await user.remove_roles(role)
            else:
                self.logger.warning("Invalid reaction type was provided in `process_reaction`.")
                self.logger.warning("Not performing any action as result.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        logging.info(payload)
        await self.process_reaction(payload, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        logging.info(payload)
        await self.process_reaction(payload, "remove")

#    @discord.slash_command()
    @reactionGroup.command()
    async def reaction_add(self, interaction: discord.Interaction) -> None:
        logging.info('hello world!')
        pass


def setup(bot):
    bot.add_cog(Reactions(bot))

