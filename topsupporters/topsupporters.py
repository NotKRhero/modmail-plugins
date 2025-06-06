from collections import defaultdict
from datetime import datetime, timezone

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel
from core.time import UserFriendlyTime


class TopSupporters(commands.Cog):
    """Sets up top supporters command in Modmail discord"""
    def __init__(self, bot):
        self.bot = bot

    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def topsupporters(self, ctx, *, dt: UserFriendlyTime):
        """Retrieves top supporters for the specified time period"""
        async with ctx.typing():
            date = discord.utils.utcnow() - (dt.dt - discord.utils.utcnow())

            # Fetch logs for all closed tickets in a single request
            logs = await self.bot.api.logs.find({"open": False, "closed_at": {"$gt": date.isoformat()}}).to_list(None)

            supporters = defaultdict(int)

            # Process the logs
            for l in logs:
                supporters_involved = set()
                for x in l['messages']:
                    if x.get('type') in ('anonymous', 'thread_message') and x['author']['mod']:
                        supporters_involved.add(x['author']['id'])
                for s in supporters_involved:
                    supporters[s] += 1

            # Sort the supporters by the number of contributions
            supporters_keys = sorted(supporters.keys(), key=lambda x: supporters[x], reverse=True)

            fmt = ''

            # Format the top supporters into a list
            n = 1
            for k in supporters_keys:
                u = self.bot.get_user(int(k))
                if u:
                    fmt += f'**{n}.** `{u}` - {supporters[k]}\n'
                    n += 1

            # Send the formatted response in an embed
            em = discord.Embed(title='Active Supporters', description=fmt, timestamp=date, color=0x7588da)
            em.set_footer(text='Since')
            await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(TopSupporters(bot))
