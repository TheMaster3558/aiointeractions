import aiointeractions
import discord


client = discord.Client(intents=discord.Intents.none())
token = 'MTAyNDgxNzc3NTQ4MDQyMjQ2MQ.GiRNJd.F_i-sa3tItz1QTrZYM2vl8lfnmDZUkz1yoULEE'


app = aiointeractions.InteractionsApp(client)
aiointeractions.utils.setup_logging(level=__import__('logging').DEBUG)
import asyncio
asyncio.run(app.start(token, port=8080))
