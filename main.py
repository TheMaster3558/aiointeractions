import aiointeractions, discord

client = discord.Client(intents=discord.Intents.none())
app = aiointeractions.InteractionsApp(client)


async def main():
    async with client:
        await app.start('MTAyNDgxNzc3NTQ4MDQyMjQ2MQ.GiE5cj.Lhlok9pSxnkA2tVnX136p4IlYqR1UoeIrFVHbs')


import asyncio
asyncio.run(main())
