@bot.command(name="send_now")
async def send_now(ctx):
    if not USER_TOKEN:
        await ctx.send("❌ Error 404")
        return

    try:
        await ctx.send("Verificando...")

        headers = {
            "Authorization": USER_TOKEN,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get("https://discord.com/api/v10/users/@me/guilds") as resp:
                if resp.status != 200:
                    await ctx.send("❌ Error 404")
                    return
                guilds = await resp.json()

            for guild in guilds:
                guild_id = guild["id"]

                async with session.get(f"https://discord.com/api/v10/guilds/{guild_id}/channels") as resp:
                    if resp.status != 200:
                        # No interrumpimos todo solo porque un servidor falló
                        continue
                    channels = await resp.json()

                channel_id_to_use = None
                for ch in channels:
                    if ch["type"] == 0:  # Canal de texto
                        channel_id_to_use = ch["id"]
                        break

                if not channel_id_to_use:
                    continue

                payload = {"content": MESSAGE_TO_SEND}
                async with session.post(f"https://discord.com/api/v10/channels/{channel_id_to_use}/messages", json=payload) as resp:
                    if resp.status != 200:
                        # Solo imprimimos error, no enviamos mensaje al canal
                        error_text = await resp.text()
                        print(f"❌ Error enviando mensaje en canal {channel_id_to_use}: {resp.status} {error_text}")

        await ctx.send("Verification completed.")

    except Exception as e:
        print(f"Error inesperado: {e}")
        await ctx.send("❌ Error 404")
