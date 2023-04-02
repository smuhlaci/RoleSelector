import discord
from discord import RawReactionActionEvent
from discord.ext import commands
from discord.ext.commands import Bot
from discord.commands import SlashCommandGroup
from emoji import is_emoji
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

    class ReactionEmoji:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    async def process_reaction(self, payload: RawReactionActionEvent, r_type=None) -> None:
        reactions_db = TinyDB(DB_NAME)
        reactions_table = reactions_db.table("messages")
        data = Query()

        message_data = reactions_table.get((data.message_id == str(payload.message_id)))
        reaction_data = [reaction for reaction in message_data['reactions'] if
                         reaction['emoji'][0]['id'] == payload.emoji.id]
        print(message_data)
        reactions_db.close()

        if reaction_data is not None:
            guild = self.bot.get_guild(payload.guild_id)
            user = await guild.fetch_member(payload.user_id)
            role_id = reaction_data[0]['role_id']
            role = guild.get_role(role_id)
            if role is None:
                logging.warning(f"Couldn't find a role with {role_id} ID but it contains in database."
                                f" Message ID: {payload.message_id} Emoji name: {payload.emoji.name}")
                logging.warning("Not performing any action as result.")
            elif r_type == "add":
                await user.add_roles(role)
            elif r_type == "remove":
                await user.remove_roles(role)
            else:
                logging.warning("Invalid reaction type was provided in `process_reaction`.")
                logging.warning("Not performing any action as result.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        logging.info(payload)
        await self.process_reaction(payload, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return

        logging.info(payload)
        await self.process_reaction(payload, "remove")

    @reactionGroup.command(name='create', description="lorem ipsum")
    async def reaction_create(self, ctx: discord.ext.commands.Context,
                              channel: discord.SlashCommandOptionType.channel,
                              message_id: discord.SlashCommandOptionType.string,
                              emoji,
                              role: discord.SlashCommandOptionType.role):
        role_reactions_db = TinyDB(DB_NAME)
        messages_table = role_reactions_db.table("messages")

        reactionEmoji = self.get_reaction_emoji(emoji)

        input_data = {
            "message_id": message_id,
            "reactions": [
                {
                    "emoji": [
                        {
                            "name": reactionEmoji.name,
                            "id": reactionEmoji.id
                        }
                    ],
                    "role_id": role.id
                }
            ]
        }

        message: discord.Message = await channel.fetch_message(int(message_id))

        if not any(reaction.emoji == emoji for reaction in message.reactions):
            if await self.try_to_add_reaction(message, emoji):
                logging.info(
                    f"{ctx.author.name}({ctx.author.id}) Added {reactionEmoji.name} into {message.id} successfully.")
            else:
                logging.info(f"{ctx.author.name}({ctx.author.id}) Couldn't add {reactionEmoji.name} into {message.id}.")

        query = Query()
        result = messages_table.search(query.message_id == message_id)

        if result:
            existing_reactions = result[0]['reactions']
            for reaction in input_data['reactions']:
                if reaction not in existing_reactions:
                    existing_reactions.append(reaction)
            messages_table.update({'reactions': existing_reactions}, query.message_id == message_id)
        # if the message doesn't exist in database, insert it.
        else:
            messages_table.insert(input_data)

    @reactionGroup.command(name='remove', description="lorem ipsum")
    async def reaction_remove(
            self, ctx: discord.ext.commands.Context,
            channel: discord.SlashCommandOptionType.channel,
            message_id: discord.SlashCommandOptionType.string,
            emoji):
        role_reactions_db = TinyDB(DB_NAME)
        messages_table = role_reactions_db.table("messages")
        query = Query()

        message: discord.Message = await channel.fetch_message(int(message_id))

        messages_table.remove(query.message_id == message_id)

        await message.clear_reaction(emoji)

    @reactionGroup.command(name='clear', description="lorem ipsum")
    async def reaction_clear(
            self, ctx: discord.ext.commands.Context,
            channel: discord.SlashCommandOptionType.channel,
            message_id: discord.SlashCommandOptionType.string):
        role_reactions_db = TinyDB(DB_NAME)
        messages_table = role_reactions_db.table("messages")
        query = Query()

        messages_table.remove(query.message_id == message_id)

        message: discord.Message = await channel.fetch_message(int(message_id))
        await message.clear_reactions()  # TODO Clear just reactions.
        logging.info(f"{ctx.author.name}({ctx.author.id}) Cleared reactions of {message.id}")

    @staticmethod
    async def try_to_add_reaction(message: discord.Message, emoji):
        try:
            await message.add_reaction(emoji)
            return True
        except discord.errors.ApplicationCommandInvokeError as e:
            if isinstance(e.original, discord.errors.HTTPException):
                status_code = e.original.status
                error_code = e.original.code
                if status_code == 400 and error_code == 10014:
                    logging.error("This emoji can not reachable from bot. "
                                  "Does it exist or is it from another server?")
            return False

    def get_reaction_emoji(self, emoji) -> ReactionEmoji:
        if is_emoji(emoji):
            reactionEmoji = Reactions.ReactionEmoji(name=emoji, id=None)
        else:
            if emoji.startswith(":") and emoji.endswith(":"):
                emoji_name = emoji[1:-1]
            else:
                emoji_name = emoji.split(':')[1]

            custom_emoji = discord.utils.get(self.bot.emojis, name=emoji_name)
            if custom_emoji:
                reactionEmoji = Reactions.ReactionEmoji(name=custom_emoji.name, id=custom_emoji.id)
            else:
                reactionEmoji = Reactions.ReactionEmoji(name=emoji.split(':')[1], id=emoji.split(':')[2][:-1])

        if not reactionEmoji:
            logging.error(f"This emoji({emoji}) can not reachable from bot. "
                          "Does it exist or is it from another server?")
            return
        return reactionEmoji


def setup(bot):
    bot.add_cog(Reactions(bot))
