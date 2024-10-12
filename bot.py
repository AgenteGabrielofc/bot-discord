import discord
from discord.ext import commands
import asyncio
import os

# Define os clusters e shards
clusters = {
    "cluster1": [0, 1, 2, 3, 4, 5],
    "cluster2": [6, 7, 8, 9, 10, 11],
    "cluster3": [12, 13, 14, 15, 16, 17],
    "cluster4": [18, 19, 20, 21, 22, 23],
}
shards = list(range(24))

# Cria o bot com intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.AutoShardedBot(command_prefix="!", shard_count=2, intents=intents)

# Evento on_ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - ID: {bot.user.id}')
    cluster_name = next((name for name, shard_ids in clusters.items() if bot.shard_id in shard_ids), None)
    print(f'Cluster: {cluster_name} - Shard ID: {bot.shard_id}')

    # Mostra status de inicialização
    await bot.change_presence(activity=discord.Game(name="🌅 O bot está ligando..."))
    await asyncio.sleep(30)  # Aguarda 30 segundos
    await bot.change_presence(activity=discord.Game(name="🛠️ Pronto para ajudar!"))

# Comando para forçar a sincronização dos comandos de barra
@bot.command(name='sync', description='[Dono] Sincroniza os comandos de barra')
@commands.is_owner()
async def sync(ctx):
    synced = await bot.tree.sync()
    await ctx.send(f"Sincronizados {len(synced)} comandos de barra com sucesso!")

# Comando para simular reinicialização e mostrar o status de reinicialização
@bot.hybrid_command(name='desligar', description="[Dono] Desliga o bot e mostra o status de reinicialização")
@commands.is_owner()
async def reniciar(ctx):
    await ctx.send("Desligando o bot...")
    await bot.change_presence(activity=discord.Game(name="💤😴 O bot está desligando..."))
    await asyncio.sleep(5)
    await ctx.send("Bot Desligado!")
    await bot.close()

# Carrega os Cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

# Setup inicial do bot para carregar os cogs
@bot.event
async def setup_hook():
    await load_cogs()
    print("Cogs carregados")

bot.run("YOUR TOKEN")