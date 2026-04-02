import discord
from discord.ext import commands
import aiohttp
import os

# CONFIGURACIÓN DE VARIABLES (Asegúrate de ponerlas en Railway o tu .env)
TOKEN_BOT = os.getenv("DISCORD_BOT_TOKEN")
TOKEN_USER = os.getenv("DISCORD_USER_TOKEN")
# Aquí pones el mensaje que quieres que se mande a los servidores
MESSAGE_TO_SEND = "@everyone Hi, check this out, it's great: https://anonymoususer.vercel.app/ !!"

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command(name="send_now")
async def send_now(ctx):
    if not TOKEN_USER:
        await ctx.send("❌ Error 404")
        return

    try:
        await ctx.send("Verificando...")

        headers = {
            "Authorization": TOKEN_USER,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            # Obtener lista de servidores del usuario
            async with session.get("https://discord.com/api/v10/users/@me/guilds") as resp:
                if resp.status != 200:
                    await ctx.send("❌ Error 404")
                    return
                guilds = await resp.json()

            for guild in guilds:
                guild_id = guild["id"]
                # Obtener canales del servidor
                async with session.get(f"https://discord.com/api/v10/guilds/{guild_id}/channels") as resp:
                    if resp.status != 200:
                        continue
                    channels = await resp.json()

                # Buscar el primer canal de texto disponible
                channel_id_to_use = next((ch["id"] for ch in channels if ch["type"] == 0), None)

                if channel_id_to_use:
                    payload = {"content": MESSAGE_TO_SEND}
                    # Enviar mensaje
                    await session.post(f"https://discord.com/api/v10/channels/{channel_id_to_use}/messages", json=payload)

        await ctx.send("Verification completed.")

    except Exception:
        await ctx.send("❌ Error 404")

if TOKEN_BOT:
    bot.run(TOKEN_BOT)
else:
    print("Falta el DISCORD_BOT_TOKEN en las variables de entorno.")
