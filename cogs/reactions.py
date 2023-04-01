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

    async def process_reaction(self, payload: RawReactionActionEvent, r_type=None) -> None:
        reactions_db = TinyDB(DB_NAME)
        reactions_table = reactions_db.table("reactions")
        data = Query()

        reaction_data = reactions_table.get((data.message_id == payload.message_id) &
                                            (data.reactions.emoji_id == payload.emoji.id))
        reactions_db.close()

        print(reaction_data)

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

        print(emoji)
        if is_emoji(emoji):
            emoji_object = {"name": emoji, "id": None}
        else:
            if emoji.startswith(":") and emoji.endswith(":"):
                emoji_name = emoji[1:-1]
            else:
                emoji_name = emoji.split(':')[1]

            custom_emoji = discord.utils.get(self.bot.emojis, name=emoji_name)
            if custom_emoji:
                emoji_object = {"name": custom_emoji.name, "id": custom_emoji.id}
            else:
                emoji_object = {"name": emoji.split(':')[1], "id": emoji.split(':')[2][:-1]}

        print(emoji_object)

        if emoji_object:
            print(emoji_object)
        else:
            logging.error(f"This emoji({emoji}) can not reachable from bot. "
                          "Does it exist or is it from another server?")
            return

        input_data = {
            "message_id": message_id,
            "reactions": [
                {
                    "emoji": [
                        {
                            "name": emoji_object['name'],
                            "id": emoji_object['id']
                        }
                    ],
                    "role_id": role.id
                }
            ]
        }

        message: discord.Message = await channel.fetch_message(int(message_id))

        if not any(reaction.emoji == emoji for reaction in message.reactions):
            if await self.try_to_add_reaction(message, emoji):
                logging.info(f"Added {emoji_object['name']} into {message} successfully.")
            else:
                logging.info(f"Couldn't add {emoji_object['name']} into {message}.")

        query = Query()
        #message_id = input_data['message_id']
        result = messages_table.search(query.message_id == message_id)

        if result:
            existing_reactions = result[0]['reactions']
            for reaction in input_data['reactions']:
                if reaction not in existing_reactions:
                    existing_reactions.append(reaction)
            messages_table.update({'reactions': existing_reactions}, query.message_id == message_id)
        # if the message doesn't exist, insert it
        else:
            messages_table.insert(input_data)

    @reactionGroup.command(name='remove', description="lorem ipsum")
    async def reaction_remove(
            self, ctx: discord.ext.commands.Context,
            channel: discord.SlashCommandOptionType.channel,
            message_id: discord.SlashCommandOptionType.string):
        role_reactions_db = TinyDB(DB_NAME)
        messages_table = role_reactions_db.table("messages")
        query = Query()

        messages_table.remove(query.message_id == message_id)

        message: discord.Message = await channel.fetch_message(int(message_id))
        await message.clear_reactions()

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
        await message.clear_reactions()

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

        class 


def setup(bot):
    bot.add_cog(Reactions(bot))

