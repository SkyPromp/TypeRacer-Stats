from discord.ext import commands
import utils
import errors
from database.bot_users import get_user
from commands.basic.stats import get_args
from api.users import get_stats

command = {
    "name": "profilepicture",
    "aliases": ["pfp"],
    "description": "Displays a user's profile picture",
    "parameters": "[username]",
    "usages": ["profilepicture keegant"],
}

class ProfilePicture(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=command["aliases"])
    async def profilepicture(self, ctx, *args):
        user = get_user(ctx)

        result = get_args(user, args, command)
        if utils.is_embed(result):
            return await ctx.send(embed=result)

        username = result
        await run(ctx, username)

async def run(ctx, username):
    stats = get_stats(username)
    if not stats:
        return await ctx.send(embed=errors.invalid_username())

    await ctx.send(content=f"https://data.typeracer.com/misc/pic?uid=tr:{username}")

async def setup(bot):
    await bot.add_cog(ProfilePicture(bot))