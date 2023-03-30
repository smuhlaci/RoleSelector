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
        reactions_db = TinyDB(DB_NAME)
        reactions_table = reactions_db.table("reactions")
        data = Query()

        reaction_data = reactions_table.get((data.message_id == payload.message_id) & (data.message.emoji_name == payload.emoji.name))
        reactions_db.close()

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

    @reactionGroup.command(name='create', description="lorem ipsum")
    async def reaction_create(self, ctx: discord.ext.commands.Context, channel_id, message_id, emoji, role_id):
        reactions_db = TinyDB(DB_NAME)
        reactions_table = reactions_db.table("reactions")
        data = Query()

        channel: discord.abc.Messageable = ctx.guild.get_channel(int(channel_id))
        message: discord.Message = await channel.fetch_message(int(message_id))
        if any(reaction.emoji == emoji for reaction in message.reactions):
            logging.error("Target message is already has that reaction. Remove it first.")
        else:
            try:
                await message.add_reaction(emoji)
                pass
            except discord.errors.ApplicationCommandInvokeError as e:
                if isinstance(e.original, discord.errors.HTTPException):
                    status_code = e.original.status
                    error_code = e.original.code
                    if status_code == 400 and error_code == 10014:
                        logging.error("This emoji can not reachable from bot. "
                                      "Does it exist or is it from another server?")


        #if reactions_db.contains(data.message_id == message_id):
    pass

    @reactionGroup.command(name='remove', description="lorem ipsum")
    async def reaction_remove(self, message_id, emoji):
        logging.info('hello world!')
        pass

    @reactionGroup.command(name='clear', description="lorem ipsum")
    async def reaction_clear(self, message_id):
        logging.info('hello world!')
        pass

def setup(bot):
    bot.add_cog(Reactions(bot))

