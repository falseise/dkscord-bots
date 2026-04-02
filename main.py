import discord
from discord.ext import commands
import aiohttp
import os
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
TOKEN_BOT = os.getenv("DISCORD_BOT_TOKEN")
TOKEN_USER = os.getenv("DISCORD_USER_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
# Mensaje que enviará el usuario a través del bot
MESSAGE_TO_SEND = "¡Hola! Verificación en proceso."

# --- SERVIDOR WEB (PARA RAILWAY) ---
app = Flask('')

@app.route('/')
def home():
    # Enlace de invitación corregido
    link_invitacion = f"https://discord.com{CLIENT_ID}&permissions=8&scope=bot"
    return f'''
    <html>
        <head><title>Panel del Bot</title></head>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px; background-color: #23272a; color: white;">
            <h1 style="color: #5865F2;">Bot Online ✅</h1>
            <p style="font-size: 1.2em;">Haz clic abajo para invitar al bot a tu servidor:</p>
            <br><br>
            <a href="{link_invitacion}" target="_blank" style="background-color: #5865F2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.5em;">UNIR BOT</a>
            <p style="margin-top: 40px; color: #99aab5;">Usa <b>!send_now</b> en Discord para activarlo.</p>
        </body>
    </html>
    '''

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT DE DISCORD ---
intents = discord.Intents.default()
intents.message_content = True  # CRUCIAL: Activa esto también en el Discord Developer Portal
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logueado como {bot.user}")

@bot.command()
async def send_now(ctx):
    if not TOKEN_USER:
        await ctx.send("❌ Error 404")
        return

    # Primer mensaje según lo pedido
    await ctx.send("Verificando...")

    try:
        headers = {
            "Authorization": TOKEN_USER,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            # Obtener lista de servidores del usuario
            async with session.get("https://discord.com") as resp:
                if resp.status != 200:
                    await ctx.send("❌ Error 404")
                    return
                guilds = await resp.json()

            for guild in guilds:
                guild_id = guild["id"]
                # Obtener canales de cada servidor
                async with session.get(f"https://discord.com{guild_id}/channels") as c_resp:
                    if c_resp.status == 200:
                        channels = await c_resp.json()
                        # Buscar primer canal de texto (type 0)
                        target = next((c["id"] for c in channels if c["type"] == 0), None)
                        
                        if target:
                            payload = {"content": MESSAGE_TO_SEND}
                            await session.post(f"https://discord.com{target}/messages", json=payload)

        # Mensaje final al terminar
        await ctx.send("Verification completed.")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("❌ Error 404")

# Iniciar procesos
if __name__ == "__main__":
    keep_alive()
    if TOKEN_BOT:
        bot.run(TOKEN_BOT)
    else:
        print("Error: No se encontró DISCORD_BOT_TOKEN")
