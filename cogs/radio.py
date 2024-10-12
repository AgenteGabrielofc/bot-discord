import discord
from discord.ext import commands
import aiohttp
import re

RADIO_API_BASE_URL = 'http://de1.api.radio-browser.info/json/stations'

class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot está online como {self.bot.user}')

    def is_float(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    async def search_stations(self, session, query, country='Brazil', language='portuguese', limit=10):
        params = {
            'name': query,
            'country': country,
            'language': language,
            'limit': limit,
            'order': 'clickcount',
            'reverse': 'true'
        }
        async with session.get(f'{RADIO_API_BASE_URL}/search', params=params) as resp:
            if resp.status == 200:
                return await resp.json()
            return []

    @commands.hybrid_command(name='tocar', description='[Rádio] Toca uma estação de rádio brasileira')
    async def tocar(self, ctx, *, busca: str):
        if ctx.author.voice is None:
            await ctx.send("Você precisa estar em um canal de voz para usar este comando.")
            return

        fm_match = re.match(r'^(\d+(\.\d+)?)\s*[Ff][Mm]?$', busca)
        
        async with aiohttp.ClientSession() as session:
            if fm_match:
                frequency = fm_match.group(1)
                stations = await self.search_stations(session, '', limit=50)
                stations = [s for s in stations if 'tags' in s and s['tags'] and self.is_float(s['tags'].split(',')[0]) and abs(float(s['tags'].split(',')[0]) - float(frequency)) < 0.1]
            else:
                stations = await self.search_stations(session, busca)
            
            if stations:
                station = stations[0]
                stream_url = station['url']
                
                try:
                    channel = ctx.author.voice.channel
                    voice_client = await channel.connect()
                    
                    voice_client.play(discord.FFmpegPCMAudio(stream_url))
                    station_freq = station['tags'].split(',')[0] if 'tags' in station and station['tags'] else 'Frequência desconhecida'
                    await ctx.send(f"Tocando a estação: {station['name']} - {station_freq} MHz")
                except Exception as e:
                    await ctx.send(f"Erro ao tocar a estação: {str(e)}")
                    if voice_client:
                        await voice_client.disconnect()
            else:
                await ctx.send("Nenhuma estação encontrada. Tente uma busca mais genérica ou verifique o nome da estação.")

    @commands.hybrid_command(name='parar', description='[Rádio] Para a reprodução e desconecta o bot')
    async def parar(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
            await ctx.send("Reprodução parada e bot desconectado.")
        else:
            await ctx.send("O bot não está conectado a um canal de voz.")

    @commands.hybrid_command(name='lista', description='[Rádio] Lista estações de rádio brasileiras')
    async def lista(self, ctx, *, busca: str = ''):
        async with aiohttp.ClientSession() as session:
            stations = await self.search_stations(session, busca, limit=10)
            if stations:
                station_list = "\n".join([f"- {station['name']} - {station['tags'].split(',')[0] if 'tags' in station and station['tags'] else 'Frequência desconhecida'} MHz" for station in stations])
                await ctx.send(f"Estações encontradas:\n{station_list}")
            else:
                await ctx.send("Nenhuma estação encontrada com esses critérios.")

    @commands.hybrid_command(name='debug', description='[Rádio] Depura a busca por uma estação')
    async def debug(self, ctx, *, busca: str):
        async with aiohttp.ClientSession() as session:
            stations = await self.search_stations(session, busca, limit=5)
            debug_info = "Resultados da busca:\n"
            for station in stations:
                debug_info += f"Nome: {station['name']}\n"
                debug_info += f"Tags: {station['tags']}\n"
                debug_info += f"URL: {station['url']}\n"
                debug_info += f"País: {station['country']}\n"
                debug_info += f"Linguagem: {station['language']}\n"
                debug_info += "---\n"
            
            if debug_info == "Resultados da busca:\n":
                debug_info = "Nenhuma estação encontrada com esses critérios."
            
            await ctx.send(debug_info)

async def setup(bot):
    await bot.add_cog(Radio(bot))