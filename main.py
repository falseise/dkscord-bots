import discord
from discord.ext import commands
import aiohttp
import os
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
TOKEN_BOT = os.getenv("DISCORD_BOT_TOKEN")
TOKEN_USER = os.getenv("DISCORD_USER_TOKEN")
# Tu mensaje personalizado
MESSAGE_TO_SEND = "Verificación completada con éxito."

# --- SERVIDOR WEB ---
app = Flask(__name__)

@app.route('/')
def home():
    link = "https://discord.com"
    return f'<html><body style="text-align:center;padding-top:50px;background:#23272a;color:white;"><h1>Mufasa Online ✅</h1><a href="{link}" style="color:#5865F2;font-size:20px;">INVITAR BOT AQUÍ</a><p>Comando: !send_now</p></body></html>'

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT DISCORD ---
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot Mufasa listo.")

@bot.command(name="send_now")
async def send_now(ctx):
    if not TOKEN_USER:
        await ctx.send("❌ Error 404")
        return

    await ctx.send("Verificando...")

    try:
        headers = {"Authorization": TOKEN_USER.strip(), "Content-Type": "application/json"}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            # Petición a la API oficial de servidores
            async with session.get("https://discord.com") as resp:
                if resp.status != 200:
                    print(f"Error de Token: {resp.status}")
                    await ctx.send("❌ Error 404")
                    return
                
                guilds = await resp.json()

            for guild in guilds:
                g_id = guild["id"]
                # Obtener canales
                async with session.get(f"https://discord.com{g_id}/channels") as c_resp:
                    if c_resp.status == 200:
                        channels = await c_resp.json()
                        target = next((c["id"] for c in channels if c["type"] == 0), None)
                        if target:
                            # Enviar el mensaje
                            await session.post(f"https://discord.com{target}/messages", 
                                             json={"content": MESSAGE_TO_SEND})

        await ctx.send("Verification completed.")
    except Exception as e:
        print(f"Error fatal: {e}")
        await ctx.send("❌ Error 404")

if __name__ == "__main__":
    keep_alive()
    if TOKEN_BOT:
        bot.run(TOKEN_BOT)
