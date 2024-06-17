from discord.ext import commands
from config import prefix
from database.bot_users import get_user
from commands.advanced.day import get_args, run
import utils

command = {
    "name": "month",
    "aliases": ["m", "lastmonth", "yestermonth", "lm", "ym", "minimonth", "mm"],
    "description": "Displays a user's stats for a given month\n"
                   f"`{prefix}lastmonth [username]` shows stats for the previous month\n"
                   f"`{prefix}minimonth [username]` will only show basic stats",
    "parameters": "[username] <month>",
    "defaults": {
        "date": "this month"
    },
    "usages": ["month keegant 2021-01"],
}


class Month(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=command["aliases"])
    async def month(self, ctx, *args):
        user = get_user(ctx)

        result = get_args(user, args, command)
        if utils.is_embed(result):
            return await ctx.send(embed=result)

        username, date = result
        await run(ctx, user, username, date)


async def setup(bot):
    await bot.add_cog(Month(bot))
