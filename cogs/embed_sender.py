import os

from discord import SlashCommandGroup
from discord.ext import commands
import discord
from orjson import loads


class EmbedSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    embedSenderGroup = SlashCommandGroup("embed", "Create Embed Messages")

    @staticmethod
    def parse_embed_json(json_file):
        embeds_json = loads(json_file)['embeds']

        for embed_json in embeds_json:
            embed = discord.Embed().from_dict(embed_json)
            yield embed

    async def get_all_json_files(ctx: discord.AutocompleteContext):
        json_files = [pos_json for pos_json in os.listdir('embed_jsons') if pos_json.endswith('.json')]
        return json_files



    @embedSenderGroup.command()
    async def send(self, ctx,
                   embed_file_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_all_json_files))):
        with open(f"embed_jsons/{embed_file_name}", "r") as file:
            temp_embeds = self.parse_embed_json(file.read())

        for embed in temp_embeds:
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(EmbedSender(bot))
