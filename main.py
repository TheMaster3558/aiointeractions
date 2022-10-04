import aiointeractions
import asyncio
import discord


client = discord.Client(intents=discord.Intents.none())
app = aiointeractions.InteractionsApp(client)


async def run():
    async with client:
        await app.start('MTAyNDgxNzc3NTQ4MDQyMjQ2MQ.G1XX7Q.k9_QfNmle3_thMZShhL4rKu4e3GMiN-IiQEsF0', port=8080)


async def main():
    asyncio.create_task(run())
    await asyncio.sleep(10)
    app.close()


asyncio.run(main())


