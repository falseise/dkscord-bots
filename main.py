import discord
from discord.ext import commands
import aiohttp
import os
from flask import Flask
from threading import Thread

# --- VARIABLES ---
TOKEN_BOT = os.getenv("DISCORD_BOT_TOKEN")
TOKEN_USER = os.getenv("DISCORD_USER_TOKEN")
MESSAGE_TO_SEND = "Verificación en curso... Mensaje enviado correctamente."

# --- SERVIDOR WEB ---
app = Flask(__name__)

@app.route('/')
def home():
    # URL FIJA: Sin variables para que no se pegue el ID al dominio
    link_directo = "https://discord.com"
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Bot Panel</title></head>
    <body style="font-family: sans-serif; text-align: center; padding-top: 80px; background-color: #23272a; color: white;">
        <div style="background-color: #2c2f33; display: inline-block; padding: 40px; border-radius: 15px; border: 2px solid #5865F2;">
            <h1 style="color: #5865F2;">Bot Online ✅</h1>
            <p style="font-size: 1.1em;">El bot <b>Mufasa#5751</b> está listo.</p>
            <br>
            <a href="{link_directo}" target="_blank" 
               style="background-color: #5865F2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 1.2em; display: inline-block;">
               UNIR BOT AL SERVIDOR
            </a>
            <div style="margin-top: 30px; color: #99aab5;">
                <p>Comando: <code style="color: #ffcc00; font-size: 1.2em;">!send_now</code></p>
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
    print(f"Logueado como {bot.user}")

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
