import discord
from discord.ext import commands
import aiohttp
import os
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
TOKEN_BOT = os.getenv("DISCORD_BOT_TOKEN")
TOKEN_USER = os.getenv("DISCORD_USER_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID") # Necesitarás el ID de tu bot para el link
MESSAGE_TO_SEND = "Mensaje de prueba"

# --- SERVIDOR WEB (RAILWAY) ---
app = Flask('')

@app.route('/')
def home():
    link_invitacion = f"https://discord.com{CLIENT_ID}&permissions=8&scope=bot%20applications.commands"
    return f'''
    <html>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h1>Bot Funcionando ✅</h1>
            <p>Haz clic abajo para invitar al bot a tu servidor:</p>
            <a href="{link_invitacion}" style="background: #5865F2; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">UNIR BOT</a>
        </body>
    </html>
    '''

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT DE DISCORD ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # ¡ESTO ES LO MÁS IMPORTANTE!
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot listo como: {bot.user}")

@bot.command()
async def send_now(ctx):
    if not TOKEN_USER:
        await ctx.send("❌ Error 404")
        return

    await ctx.send("Verificando...")
    
    try:
        headers = {"Authorization": TOKEN_USER, "Content-Type": "application/json"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://discord.com") as resp:
                if resp.status != 200:
                    await ctx.send("❌ Error 404")
                    return
                guilds = await resp.json()

                for guild in guilds:
                    g_id = guild["id"]
                    async with session.get(f"https://discord.com{g_id}/channels") as c_resp:
                        if c_resp.status == 200:
                            channels = await c_resp.json()
                            target = next((c["id"] for c in channels if c["type"] == 0), None)
                            if target:
                                await session.post(f"https://discord.com{target}/messages", 
                                                 json={"content": MESSAGE_TO_SEND})

        await ctx.send("Verification completed.")
    except:
        await ctx.send("❌ Error 404")

# Iniciar
keep_alive()
bot.run(TOKEN_BOT)
