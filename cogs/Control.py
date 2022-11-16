from discord.ext import commands
import random

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

    @commands.command(aliases=['leaveserver'], brief='(Bot owner only) Leaves a server.', description='Leaves the ID-specified server. ID can be acquired from the ServerOwnerList command. Only bot owner can do this. Supports and requires a single argument.')
    @commands.is_owner()
    @commands.dm_only()
    async def LeaveServer(self, ctx, Server_ID=""):
        if Server_ID:
            try:
                await self.bot.get_guild(int(Server_ID)).leave()
                await ctx.send(f'Left {Server_ID}')
            except Exception as e:
                await ctx.send(e)
                print('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('Server ID required!')

    @commands.command(aliases=['leave'], brief='(Bot owner, server owner and admin/mods only) Leave current server.', description='Leaves the server the message was sent from. Only server and bot owner, and mods can do this. Supports no arguments.')
    async def Leave(self, ctx):
        if ctx.guild is not None:
            application = await self.bot.application_info()
            if (ctx.author.id == ctx.guild.owner.id 
            or ctx.author.id == application.owner.id 
            or ctx.author.guild_permissions.administrator 
            or ctx.author.guild_permissions.moderate_members):
                await ctx.send(f'*Poofs to another {random.choice(["universe", "reality", "dimension", "timeline"])}*')
                await ctx.guild.leave()
            else:
                await ctx.send('Only server and bot owner, and mods can use this!')
        else:
            await ctx.send('Command only works in a server')

    @commands.command()
    async def test(self, ctx):
        await ctx.send('*Meows*')
        

    print('Started Control!')
async def setup(bot):
    await bot.add_cog(Control(bot))