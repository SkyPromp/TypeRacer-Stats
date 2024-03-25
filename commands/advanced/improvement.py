from discord import Embed, File
from discord.ext import commands
import os
from datetime import datetime, timezone
from database.bot_users import get_user
import database.users as users
import database.races as races
from commands.advanced.races import get_params
import graphs
import utils
import errors

info = {
    "name": "improvement",
    "aliases": ["imp"],
    "description": "Displays a graph of a user's WPM over time",
    "parameters": "[username] <start_date/start_number> <end_date/end_number>",
    "defaults": {
        "end_date": "today",
        "end_number": "the user's most recent race number"
    },
    "usages": [
        "improvement keegant",
        "improvement keegant 2022-04-20 2023-04-20",
        "improvement keegant 800k 900k",
    ],
    "import": True,
}


class Improvement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=info["aliases"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def improvement(self, ctx, *params):
        user = get_user(ctx)

        try:
            username, start_date, end_date, start_number, end_number = await get_params(ctx, user, params, info)
        except ValueError:
            self.improvement.reset_cooldown(ctx)
            return

        await run(ctx, user, username, start_date, end_date, start_number, end_number)


async def run(ctx, user, username, start_date, end_date, start_number, end_number):
    stats = users.get_user(username)
    if not stats:
        utils.reset_cooldown(ctx.command, ctx)
        return await ctx.send(embed=errors.import_required(username))

    if start_number and not end_number:
        end_number = stats["races"]

    if start_date and not end_date:
        end_date = datetime.now(timezone.utc)

    title = "WPM Improvement"
    columns = ["wpm", "timestamp"]
    if start_date is None and start_number is None:
        timeframe = f" (All-Time)"
        title += " - All-Time"
        race_list = sorted(await races.get_races(username, columns=columns), key=lambda x: x[1])

    elif start_date is None:
        end_number = min(end_number, stats["races"])
        timeframe = f" {start_number:,} - {end_number:,}"
        title += f" - Races{timeframe}"
        race_list = sorted(await races.get_races(username, start_number=start_number, end_number=end_number, columns=columns), key=lambda x: x[1])

    else:
        timeframe = f" ({utils.get_display_date_range(start_date, end_date)})"
        title += f" - {utils.get_display_date_range(start_date, end_date)}"
        race_list = sorted(await races.get_races(username, start_date.timestamp(), end_date.timestamp(), columns=columns), key=lambda x: x[1])

    wpm = []
    best = 0
    average = 0
    recent_average = 0
    race_count = len(race_list)
    worst = float("inf")
    moving = min(max(race_count // 15, 1), 500)

    for race in race_list:
        race_wpm = race[0]
        wpm.append(race_wpm)
        if race_wpm > best:
            best = race_wpm
        if race_wpm < worst:
            worst = race_wpm
        average += race_wpm

    race_list = sorted(race_list, key=lambda x: x[1], reverse=True)
    for race in race_list[:moving]:
        recent_average += race[0]

    average /= race_count
    recent_average /= moving

    description = (
        f"**Races:** {race_count:,}\n"
        f"**Average:** {average:,.2f} WPM\n"
        f"**Best:** {best:,.2f} WPM\n"
        f"**Worst:** {worst:,.2f} WPM\n"
        f"**Average of Last {moving}:** {recent_average:,.2f} WPM"
    )

    embed = Embed(
        title=title,
        description=description,
        color=user["colors"]["embed"],
    )
    utils.add_profile(embed, stats)

    title = f"WPM Improvement - {username}"
    file_name = f"improvement_{username}.png"
    graphs.improvement(user, wpm, title, file_name, timeframe)

    embed.set_image(url=f"attachment://{file_name}")
    file = File(file_name, filename=file_name)

    await ctx.send(embed=embed, file=file)

    os.remove(file_name)


async def setup(bot):
    await bot.add_cog(Improvement(bot))
