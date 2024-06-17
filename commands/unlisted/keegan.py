from discord import Embed
from discord.ext import commands

command = {
    "name": "keegan",
    "aliases": ["keegant", "kegnat", "kt"],
    "description": "keegan",
}


class Keegan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=command["aliases"])
    async def keegan(self, ctx):
        await run(ctx)


async def run(ctx):
    embed = Embed(
        description="[But can you do this?](https://www.youtube.com/watch?v=9-cRwoIjfKM)",
        color=0,
    )

    await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Keegan(bot))
