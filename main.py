import discord
from discord.ext import commands
import aiohttp
import os
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
TOKEN_BOT = os.getenv("DISCORD_BOT_TOKEN")
TOKEN_USER = os.getenv("DISCORD_USER_TOKEN")
MESSAGE_TO_SEND = "Verificación en curso... Mensaje enviado correctamente."

# --- SERVIDOR WEB (RAILWAY) ---
app = Flask(__name__)

@app.route('/')
def home():
    # TU LINK REAL DE INVITACIÓN
    link_invitacion = "https://discord.com/oauth2/authorize?client_id=1457946196071944325&permissions=8&integration_type=0&scope=bot"
    
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="UTF-8"><title>Bot Panel</title></head>
    <body style="font-family: sans-serif; text-align: center; padding-top: 100px; background-color: #23272a; color: white;">
        <div style="background-color: #2c2f33; display: inline-block; padding: 50px; border-radius: 20px; border: 3px solid #5865F2; box-shadow: 0px 0px 20px rgba(88, 101, 242, 0.5);">
            <h1 style="color: #5865F2; font-size: 2.5em; margin-bottom: 10px;">Mufasa#5751 ✅</h1>
            <p style="font-size: 1.2em; color: #ffffff;">Sistema de verificación activo y en línea.</p>
            <br><br>
            <a href="{link_invitacion}" target="_blank" 
               style="background-color: #5865F2; color: white; padding: 20px 40px; text-decoration: none; border-radius: 10px; font-weight: bold; font-size: 1.5em; display: inline-block; transition: 0.3s;">
               UNIR BOT AL SERVIDOR
            </a>
            <div style="margin-top: 50px; border-top: 1px solid #4f545c; padding-top: 20px;">
                <p style="color: #99aab5;">Escribe en el chat:</p>
                <code style="background: #23272a; padding: 10px 20px; border-radius: 8px; color: #ffcc00; font-size: 1.4em; font-weight: bold;">!send_now</code>
            </div>
        </div>
    </body>
    </html>
    '''

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT DE DISCORD ---
intents = discord.Intents.default()
intents.message_content = True 
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Mufasa#5751 conectado y listo.")

@bot.command(name="send_now")
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
    except Exception:
        await ctx.send("❌ Error 404")

if __name__ == "__main__":
    keep_alive()
    if TOKEN_BOT:
        bot.run(TOKEN_BOT)
