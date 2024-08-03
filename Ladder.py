import argparse, discord, json, glob, requests, shutil
from discord.ext import commands
import config

from cogs.exceptions import APIException
import cogs.request_generator as ai_arena_urls
import cogs.api as ai_arena_api

file_path = './replays/'  # insert file path

race_dict = {"P": "Protoss", "T": "Terran", "Z": "Zerg", "R": "Random"}


class Ladder(commands.Cog, name="ladder"):
    def __init__(self, bot):
        self.bot = bot

    # Unused, can be removed?
    # @staticmethod
    # async def get_discord_name(self, context: discord.ext.commands.Context, discord_id: str):
    #     discord_user = await context.message.guild.get_member(discord_id)
    #     return discord_user.nick

    @staticmethod
    async def send_files(context: discord.ext.commands.Context, directory: str):
        if len(glob.glob(directory + '/*.SC2Replay')) == 0:
            await context.message.author.send(f"Could not find any SC2 replays with the criteria: "
                                              f"{context.message.content}")
            return
        await context.message.author.send(f"Sending you {len(glob.glob(directory + '/*.SC2Replay'))} SC2 replay files...")
        for file in glob.glob(directory + "/*.SC2Replay"):
            try:
                await context.message.author.send(file=discord.File(file))
            except Exception as e:
                await context.message.author.send(f"Replay {file.split('/')[-1]} is too big!")
        await context.message.author.send(f"Have a nice day {config.SMILEY}")
        shutil.rmtree(directory)

    @commands.command(name="top10")
    async def top10(self, context: discord.ext.commands.Context):
        request_url = ai_arena_urls.make_top_ten_bots_request()
        response = requests.get(ai_arena_urls.make_top_ten_bots_request(), headers=config.AUTH)
        if response.status_code != 200:
            raise APIException("Could not retrieve top 10 bots!", request_url, response)
        bots = json.loads(response.text)

        bot_infos = []
        for participant in bots["results"]:
            b_id = participant["bot"]
            bot_info = ai_arena_api.get_bot_info(b_id)
            bot_infos.append((bot_info["name"], participant["elo"]))

        embed = discord.Embed(
            title="Leaderboard",
            description="Top 10 Bots",
            color=0x00FF00
        )

        for bot in bot_infos:
            embed.add_field(
                name=f"{bot[0]}",
                value=f"ELO: {bot[1]}",
                inline=False
            )
        await context.reply(embed=embed)

    @commands.command(name="top16")
    async def top16(self, context: discord.ext.commands.Context):
        request_url = ai_arena_urls.make_top_sixteen_bots_request()
        response = requests.get(request_url, headers=config.AUTH)
        if response.status_code != 200:
            raise APIException("Could not retrieve top 10 bots!", request_url, response)
        bots = json.loads(response.text)
