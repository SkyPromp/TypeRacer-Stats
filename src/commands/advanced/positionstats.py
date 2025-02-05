from discord import Embed
from discord.ext import commands

import database.races as races
import database.users as users
from commands.basic.stats import get_args
from database.bot_users import get_user
from utils import errors, urls, embeds

command = {
    "name": "positionstats",
    "aliases": ["ps"],
    "description": "Displays stats about the positions of a user's races",
    "parameters": "[username]",
    "usages": ["positionstats keegant"],
}


class PositionStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=command["aliases"])
    async def positionstats(self, ctx, *args):
        user = get_user(ctx)

        result = get_args(user, args, command)
        if embeds.is_embed(result):
            return await ctx.send(embed=result)

        username = result
        await run(ctx, user, username)


async def run(ctx, user, username):
    universe = user["universe"]
    stats = users.get_user(username, universe)
    if not stats:
        return await ctx.send(embed=errors.import_required(username, universe))

    columns = ["number", "rank", "racers"]
    race_list = await races.get_races(username, columns=columns, universe=universe)
    race_list.sort(key=lambda x: x[0])

    result_dict = {}
    race_count = len(race_list)
    wins = 0
    most_racers = (0, 0, 0)
    biggest_win = (0, 0, 0)
    biggest_loss = (0, 1, 0)
    win_streak = (0, 0, 0)
    current_win_streak = 0

    for race in race_list:
        number, rank, racers = race
        result = f"{rank}/{racers}"
        if result in result_dict:
            result_dict[result] += 1
        else:
            result_dict[result] = 1

        if racers > most_racers[2]:
            most_racers = (number, rank, racers)

        if rank == 1:
            if racers > biggest_win[2]:
                biggest_win = (number, rank, racers)
            if racers > 1:
                wins += 1
            current_win_streak += 1
        else:
            if current_win_streak > win_streak[0]:
                win_streak = (current_win_streak, number - current_win_streak, number - 1)
            current_win_streak = 0

        if rank > biggest_loss[1]:
            biggest_loss = (number, rank, racers)

    if wins > 0 and win_streak[0] == 0:
        win_streak = (race_count, 1, race_count)

    win_percent = (wins / race_count) * 100
    sorted_results = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)
    description = (
        f"**Races:** {race_count:,}\n"
        f"**Wins:** {wins:,} ({win_percent:,.2f}%)\n"
        f"**Most Racers:** {most_racers[1]}/{most_racers[2]:,} "
        f"(Race [#{most_racers[0]:,}]({urls.replay(username, most_racers[0], universe)}))\n"
    )

    if wins > 0:
        description += (
            f"**Biggest Win:** {biggest_win[1]}/{biggest_win[2]:,} "
            f"(Race [#{biggest_win[0]:,}]({urls.replay(username, biggest_win[0], universe)}))\n"
        )

    if biggest_loss[0] != 0:
        description += (
            f"**Biggest Loss:** {biggest_loss[1]}/{biggest_loss[2]:,} "
            f"(Race [#{biggest_loss[0]:,}]({urls.replay(username, biggest_loss[0], universe)}))\n"
        )

    if wins > 0:
        description += (
            f"**Longest Win Streak:** {win_streak[0]:,} "
            f"(Races [#{win_streak[1]:,}]({urls.replay(username, win_streak[1], universe)}) - "
            f"[#{win_streak[2]:,}]({urls.replay(username, win_streak[2], universe)}))\n"
        )

    description += "\n**Positions**\n"

    for result, frequency in sorted_results[:20]:
        description += f"**{result}:** {frequency:,}\n"

    embed = Embed(
        title="Position Stats",
        description=description,
        color=user["colors"]["embed"],
    )
    embeds.add_profile(embed, stats, universe)
    embeds.add_universe(embed, universe)

    await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PositionStats(bot))
