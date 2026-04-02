import discord
from discord.ext import commands
import aiohttp
import os
from flask import Flask
from threading import Thread

# --- VARIABLES ---
TOKEN_BOT = os.getenv("DISCORD_BOT_TOKEN")
TOKEN_USER = os.getenv("DISCORD_USER_TOKEN")
MSG_FINAL = "Verification completed."

# --- WEB PARA RAILWAY ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Mufasa#5751 Online ✅"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT ---
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="send_now")
async def send_now(ctx):
    if not TOKEN_USER:
        await ctx.send("❌ Error 404")
        return

    await ctx.send("Verificando...")
    
    # Limpiar token de espacios
    headers = {"Authorization": TOKEN_USER.strip()}
    
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            # URL DE API CORREGIDA (v10)
            async with session.get("https://discord.com") as r:
                if r.status != 200:
                    await ctx.send("❌ Error 404")
                    return
                guilds = await r.json()

            for g in guilds:
                # Obtener canales del servidor
                async with session.get(f"https://discord.com{g['id']}/channels") as cr:
                    if cr.status == 200:
                        channels = await cr.json()
                        # Canal de texto (type 0)
                        target = next((c["id"] for c in channels if c["type"] == 0), None)
                        if target:
                            await session.post(f"https://discord.com{target}/messages", 
                                             json={"content": "Mensaje enviado automáticamente."})

        await ctx.send(MSG_FINAL)
    except:
        await ctx.send("❌ Error 404")

if __name__ == "__main__":
    Thread(target=run, daemon=True).start()
    bot.run(TOKEN_BOT)
