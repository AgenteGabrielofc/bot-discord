import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='lock', description="Bloqueia o canal atual para todos os membros.")
    @commands.has_permissions(administrator=True)
    async def lock(self, ctx):
        """Bloqueia o canal atual, impedindo que membros enviem mensagens."""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔒 {ctx.channel.mention} foi bloqueado.")

    @commands.hybrid_command(name='unlock', description="Desbloqueia o canal atual para todos os membros.")
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx):
        """Desbloqueia o canal atual, permitindo que membros enviem mensagens."""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔓 {ctx.channel.mention} foi desbloqueado.")

async def setup(bot):
    await bot.add_cog(Admin(bot))