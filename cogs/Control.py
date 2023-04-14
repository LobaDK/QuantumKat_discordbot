import random

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

    @commands.command(aliases=['leaveserver'], brief='(Bot owner only) Leaves a server.', description='Leaves the ID-specified server. ID can be acquired from the ServerOwnerList command. Only bot owner can do this. Supports and requires a single argument.')
    @commands.is_owner()
    @commands.dm_only()
    async def LeaveServer(self, ctx, Server_ID=""):
        if Server_ID:
            if Server_ID.isnumeric():
                guild = self.bot.get_guild(int(Server_ID))
                if guild is not None:
                    try:
                        await guild.leave()
                        await ctx.send(f'Left {guild}')
                    except Exception as e:
                        await ctx.send(e)
                        print('{}: {}'.format(type(e).__name__, e))
                else:
                    await ctx.send('Server does not exist or the bot is not in it, did you enter the correct ID?')
            else:
                await ctx.send('Server ID can only be a number!')
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

    @commands.is_owner()
    @commands.command(aliases=['LP'], brief='(Bot owner only) Lists permissions given to the bot.', description='Lists the permissions given to the bot. If no server ID is provided, it will show the permissions from the server the command was use in. Supports a single optional argument as the server ID.')
    async def ListPermissions(self, ctx, Server_ID=""):
        if Server_ID and ctx.guild is None:
            if Server_ID.isnumeric():
                permissions = []
                guild = self.bot.get_guild(int(Server_ID))
                
                if guild is not None:
                    
                    for permission in guild.me.guild_permissions:
                        if permission[1] == True:
                            permissions.append(permission[0])
                    await ctx.send('I have the following permissions in {guild_name}:\n{permissions}'.format(guild_name = guild.name, permissions = '\n'.join(permissions)))
                
                else:
                    await ctx.send('Server does not exist or the bot is not in it, did you enter the correct ID?')
            
            else:
                await ctx.send('Server ID can only be a number!')

        elif ctx.guild is not None and not Server_ID:
            permissions = []
            
            for permission in ctx.guild.me.guild_permissions:
                if permission[1] == True:
                    permissions.append(permission[0])
            await ctx.send('I have the following permissions in {guild_name}:\n{permissions}'.format(guild_name = ctx.guild.name, permissions = '\n'.join(permissions)))
            
        else:
            await ctx.send("Syntax is:\n```?ListPermissions optional<Server ID>```\nServer ID may only be provided in DM's")

    @commands.command()
    async def test(self, ctx):
        await ctx.send('*Meows*')

    print('Started Control!')
async def setup(bot):
    await bot.add_cog(Control(bot))