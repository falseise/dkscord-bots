import discord
from discord.ext import commands
import aiohttp
import os
from flask import Flask
from threading import Thread

TOKEN_BOT = os.getenv("DISCORD_BOT_TOKEN")
# Limpiamos el token de cualquier espacio o comilla extra
TOKEN_USER = os.getenv("DISCORD_USER_TOKEN").strip().replace('"', '')

app = Flask(__name__)
@app.route('/')
def home(): return "Mufasa Online ✅"

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="send_now")
async def send_now(ctx):
    if not TOKEN_USER:
        await ctx.send("❌ Error 404")
        return

    await ctx.send("Verificando...")
    
    # Headers con el User-Agent para que Discord no sospeche
    headers = {
        "Authorization": TOKEN_USER,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            # 1. Obtener servidores
            async with session.get("https://discord.com") as r:
                if r.status != 200:
                    print(f"DEBUG: Status {r.status} - Posible token inválido")
                    await ctx.send("❌ Error 404")
                    return
                guilds = await r.json()

            for g in guilds:
                # 2. Intentar enviar (si falla un servidor, sigue con el otro)
                async with session.get(f"https://discord.com{g['id']}/channels") as cr:
                    if cr.status == 200:
                        channels = await cr.json()
                        target = next((c["id"] for c in channels if c["type"] == 0), None)
                        if target:
                            await session.post(f"https://discord.com{target}/messages", 
                                             json={"content": "Verification in progress..."})

        await ctx.send("Verification completed.")
    except:
        await ctx.send("❌ Error 404")

if __name__ == "__main__":
    Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    bot.run(TOKEN_BOT)
