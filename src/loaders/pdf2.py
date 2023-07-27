from langchain.document_loaders import PyMuPDFLoader
from langchain.vectorstores import SupabaseVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from supabase.client import Client, create_client
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv("../.env")
api_key = os.getenv('OPENAI_API_KEY')
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# loader = PyMuPDFLoader("resume.pdf")
# documents = loader.load()
# # print("documents", documents)

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
# docs = text_splitter.split_documents(documents)

# embeddings = OpenAIEmbeddings(openai_api_key=api_key)
# vector_store = SupabaseVectorStore.from_documents(docs, embeddings, client=supabase)

# query = "In which company did the candidate use firebase cloud firestore to design a nosql database?"
# matched_docs = vector_store.similarity_search(query, k=3)
# search_result ='\n'.join(["Matched Doc "+str(i+1) +": \n"+ doc.page_content for i,doc in enumerate(matched_docs)])
# print(search_result)

token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.command()
async def upload_and_ask(ctx, *, question):
    # Check if there are any attachments in the message
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            # Check if the attachment is a PDF
            if attachment.filename.endswith(".pdf"):
                # Download the file to a temporary directory
                await attachment.save(fp=attachment.filename)

                # Process the PDF
                loader = PyMuPDFLoader(attachment.filename)
                documents = loader.load()

                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
                docs = text_splitter.split_documents(documents)

                embeddings = OpenAIEmbeddings(openai_api_key=api_key)
                vector_store = SupabaseVectorStore.from_documents(docs, embeddings, client=supabase)
                

                # Search the vector store with the user's question
                matched_docs = vector_store.similarity_search(question, k=3)
                search_result ='\n'.join(["Matched Doc "+str(i+1) +": \n"+ doc.page_content for i,doc in enumerate(matched_docs)])

                # Reply with the search result
                await ctx.send(search_result)
    else:
        await ctx.send("Please upload a PDF with your question.")

bot.run(token)




