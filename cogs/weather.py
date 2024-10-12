import discord
from discord.ext import commands
import aiohttp
import json

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_weather_data(self, city):
        api_key = 'YOUR_API_WEATHERAPI'  # Substitua com sua chave de API da WeatherAPI
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang=pt"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None

    @commands.hybrid_command(name="weather", description="Mostra a previsão do tempo para uma cidade")
    async def weather(self, ctx, *, cidade: str):
        await ctx.defer()  # Defer para comandos de slash

        data = await self.get_weather_data(cidade)
        if data:
            city_name = data['location']['name']
            country = data['location']['country']
            condition = data['current']['condition']['text']
            icon = data['current']['condition']['icon']
            temp_c = data['current']['temp_c']
            temp_min_c = temp_c - 2  # Apenas um exemplo, pode ajustar conforme necessário
            temp_max_c = temp_c + 2
            humidity = data['current']['humidity']
            wind_kph = data['current']['wind_kph']
            pressure_mb = data['current']['pressure_mb']

            # Embed formatado como o da imagem
            embed = discord.Embed(
                title=f"Previsão do tempo para {city_name}, {country}",
                description=f"**{condition}**",
                color=discord.Color.blue()
            )

            embed.add_field(name="🌡️ Temperatura", value=f"Atual: {temp_c} °C\nMáxima: {temp_max_c} °C\nMínima: {temp_min_c} °C", inline=True)
            embed.add_field(name="💧 Umidade", value=f"{humidity}%", inline=True)
            embed.add_field(name="💨 Velocidade do Vento", value=f"{wind_kph} km/h", inline=True)
            embed.add_field(name="🌡️ Pressão do Ar", value=f"{pressure_mb} kPa", inline=True)

            embed.set_thumbnail(url=f"http:{icon}")
            embed.set_footer(text=f"Pedido por {ctx.author}", icon_url=ctx.author.avatar.url)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Desculpe, não consegui encontrar informações sobre o tempo para **{cidade}**.")

async def setup(bot):
    await bot.add_cog(Weather(bot))