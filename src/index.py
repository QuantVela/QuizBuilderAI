import discord
from discord.ext import commands
import aiohttp
from gotrue import AsyncGoTrueClient
from gotrue import SignInWithOAuthCredentials
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)




token = "eyJhbGciOiJIUzI1NiIsImtpZCI6IjYrcEVyMWFwT1JJOFF2emkiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNjkyMDk1MjM0LCJpYXQiOjE2OTIwOTE2MzQsImlzcyI6Imh0dHBzOi8vaW1mZmZvZHJheW5mYWFqbmN5ZmIuc3VwYWJhc2UuY28vYXV0aC92MSIsInN1YiI6ImVhYTU2YjMzLTkwZmUtNGE2Ni04ZTM1LTg3NWNkMjMwYzZjOSIsImVtYWlsIjoiaGhoaG91anVlQGdtYWlsLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZW1haWwiLCJwcm92aWRlcnMiOlsiZW1haWwiXX0sInVzZXJfbWV0YWRhdGEiOnt9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNjkyMDkxNjM0fV0sInNlc3Npb25faWQiOiI3ZGUzZmMwMy1mODFjLTRhZmEtOTEyNS1iYjQ3ODI4OWFiNGMifQ.lPiADU6Q5BRq_igQJv6QaHAiYyU4tFE5rgecE72ZlkI"

@bot.command()
async def file(ctx):
    file = ctx.message.attachments[0]
    assert isinstance(file,discord.Attachment)
    
    async with AsyncGoTrueClient() as client:
        sign = SignInWithOAuthCredentials(provider="discord")
        result = await client.sign_in_with_oauth(sign)
    
    handler_url = "http://127.0.0.1:8000/file"
    payload = {
        "token":token,
        "url":file.url,
        "user_id":str(ctx.author.id),
        "filename":file.filename,
        "filesize":int(file.size),
        "mime_type":str(file.content_type),
        "upload":True
    }
    
    async with aiohttp.ClientSession() as session:
        result = await session.post(url=handler_url,json=payload)
        if result.status != 200:
            await ctx.send("error in your upload file")
            return
        
    await ctx.send("file upload Done, You can ask me about this file later")


bot.run(token="MTEyNzE4MTQ5ODIwNjkxNjYzOA.G79C-H.nencJA36EBQ-qTdM4OmN8Eisu5xMG73EYHSgEo")
