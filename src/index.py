import os
import logging
from utils.processors import filter_file
from utils.urlProcessors import filter_web
from models.settings import common_dependencies, Settings
from models.files import File
from models.urls import Url
from utils.vectors import VectorManager
from utils.chatProcessors import filter_chat
from loaders.dc import process_discord, load_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = Settings()
token = settings.discord_token

commons = common_dependencies()
vector_manager = VectorManager(commons=commons)
bot = commons["bot"]

@bot.command()
async def upload_and_ask(ctx, *, question):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_path = os.path.join('uploads', attachment.filename)
            await attachment.save(fp=file_path)   
            file = File(file=attachment) 
            msg = await filter_file(file, vector_manager)  
            # msg = await filter_chat(file, vector_manager, "telegram") 
            print(msg)  
            search_result = vector_manager.match_finder(question, top_k=3)

            # Reply with the search result
            await ctx.send(search_result)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        await ctx.send("Please upload a PDF with your question.")

@bot.command()
async def crawl(ctx, input_url: str):
    url = Url(url=input_url)
    web_result = await filter_web(url, vector_manager, "web")
    print(web_result)
    search_result = vector_manager.match_finder("撸毛博主常见的误区?", top_k=3)
    await ctx.send(search_result)

@bot.command()
async def history(ctx, *, question: str):
    # res = await load_data(bot, ctx)
    # print(res)
    message = await process_discord()
    print(message)
    search_result = vector_manager.match_finder(question, top_k=3)
    await ctx.send(search_result)

bot.run(token)




