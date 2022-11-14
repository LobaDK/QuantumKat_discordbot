from discord.ext import commands

class Control(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['serverownerlist', 'SOL'], brief="(Bot owner only, limited to DM's) Fetches a list of servers the bot is in.", description="Fetches a list of servers the bot is in, including the ID of the server, the owner username and the ID of the owner. Supports no arguments. Limited to bot owner, and DM's for privacy.")
    @commands.is_owner()
    @commands.dm_only()
    async def ServerOwnerList(self, ctx):
        servers_and_owners = []
        for guild in self.bot.guilds:
            servers_and_owners.append(f'Server: {guild.name} with ID: {guild.id}, owned by: {guild.owner.display_name}#{guild.owner.discriminator} with ID: {guild.owner.id}')
        await ctx.send("\n".join(servers_and_owners))

    print('Started Control!')
async def setup(bot):
    await bot.add_cog(Control(bot))