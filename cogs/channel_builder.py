import os

import discord
from discord import SlashCommandGroup
from discord.ext import commands
from orjson import loads


class ChannelBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    channelBuilderGroup = SlashCommandGroup("builder", "Create a channel from JSON files.")

    @staticmethod
    def parse_embed_json(embeds_json):

        for embed_json in embeds_json:
            embed = discord.Embed().from_dict(embed_json)
            yield embed

    async def get_all_json_files(ctx: discord.AutocompleteContext):
        json_files = [pos_json for pos_json in os.listdir('embed_jsons') if pos_json.endswith('.json')]
        return json_files

    @channelBuilderGroup.command()
    async def send(self, ctx,
                   embed_file_name: discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_all_json_files))):
        with open(f"embed_jsons/{embed_file_name}", "r") as file:
            embeds_json = loads(file.read())
            embed_objects = self.parse_embed_json(embeds_json['embeds'])

        for index, embed in enumerate(embed_objects):
            embed_json = embeds_json["embeds"][index]
            if "interaction" in embed_json:
                interaction = embed_json["interaction"]
                interaction_type = interaction["interaction_type"]
                match interaction_type:
                    case "select_menu":
                        options = []
                        for option in interaction["parameters"]:
                            options.append(
                                discord.SelectOption(label=option["label"], description=option["description"], emoji=option["emoji"]))
                        select = discord.ui.Select(placeholder="Choose an option", options=options)

                        class SelectView(discord.ui.View):
                            @discord.ui.select(placeholder="Choose an option", options=options)
                            async def select_callback(self, select, interaction):
                                await interaction.response.send_message(f"You selected {select.values}!")

                        await ctx.send(embed=embed, view=SelectView())
                        continue  # Move to the next embed if there are more

                    case "select_menu":
                        pass

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ChannelBuilder(bot))
