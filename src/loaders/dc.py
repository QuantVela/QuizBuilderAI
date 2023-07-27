import discord
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.settings import common_dependencies
from utils.file import compute_sha1_from_content
from models.chats import ChatHistory

commons = common_dependencies()
bot = commons["bot"]

def create_response(message, type):
    return {"message": message, "type": type}

def documents_is_empty(file_size):
    return file_size  < 1

def documents_already_exists(file_sha1: str):
    commons = common_dependencies() 
    response = (
        commons["supabase"].table("vectors")
        .select("id")
        .filter("metadata->>file_sha1", "eq", file_sha1)
        .execute()
    )
    vectors_ids = response.data
    if len(vectors_ids) == 0:
        return False
    return True

async def read_channel(
    bot, 
    channel_id: int, 
    before: Optional[datetime], 
    after: Optional[datetime], 
    oldest_first: bool
):
    """Async read channel."""
    messages_data: List[dict] = []

    try:
        channel = bot.get_channel(channel_id)
        print(f"Added {channel.name} from {channel.guild.name}")
        # only work for text channels for now
        if not isinstance(channel, discord.TextChannel):
            raise ValueError(f"Channel {channel_id} is not a text channel. Only text channels are supported for now.")
        thread_dict = {}
        for thread in channel.threads:
            thread_dict[thread.id] = thread
        async for msg in channel.history(before=before, after=after, oldest_first=oldest_first):
            messages_data.append({
                "channel_id": channel_id,
                "channel_name": channel.name,
                "role": 'bot' if msg.author.bot else 'user',
                "name": msg.author.display_name,
                "content": msg.content,
                "msg_time": msg.created_at.isoformat(),
            })
            if msg.id in thread_dict:
                thread = thread_dict[msg.id]
                async for thread_msg in thread.history(before=before, after=after, oldest_first=oldest_first):
                    messages_data.append({
                        "channel_id": channel_id,
                        "channel_name": channel.name,
                        "role": 'bot' if thread_msg.author.bot else 'user',
                        "name": thread_msg.author.display_name,
                        "content": thread_msg.content,
                        "msg_time": thread_msg.created_at.isoformat(),
                    })
    except Exception as e:
            print(f"Error processing discord chat history: {e}")
            return create_response(
                f"⚠️ An error occurred while processing {channel.name}.", 
                "error",
            )

    return messages_data

async def load_data(
    bot, 
    ctx, 
    before: Optional[datetime] = None, 
    after: Optional[datetime] = None,
    oldest_first: bool = True
) -> Dict:
    """Load data from the input directory."""
    chat_history = []
    channel_ids: List[int] = []
    before = datetime.now(timezone.utc)

    for c in ctx.guild.text_channels:
        channel_ids.append(c.id)    
    # print(channel_ids)
    for channel_id in channel_ids:
        if not isinstance(channel_id, int):
            raise ValueError(f"Channel id {channel_id} must be an integer, not {type(channel_id)}.")
        chat_history.extend(await read_channel(bot, channel_id, before=before, after=after, oldest_first=oldest_first))
    for record in chat_history:
        chat_record = ChatHistory(**record)
        response = chat_record.update_chat_history()
    return response

async def process_discord():
    #数据库里取聊天记录
    chat_history = ChatHistory()
    chat_to_vectordb = chat_history.get_chat_history()
    chat_ids = [chat['chat_id'] for chat in chat_to_vectordb]
    chat_data_by_channel = {}
    latest_channel_name = {}

    for record in chat_to_vectordb:
        channel_id = record['channel_id']
        channel_name = record['channel_name']
        role = record['role']
        name = record['name']
        content = record['content']

        latest_channel_name[channel_id] = channel_name
        message = f"{name}({role}): {content}"

        if channel_id in chat_data_by_channel:
            chat_data_by_channel[channel_id].append(message)
        else:
            chat_data_by_channel[channel_id] = [message]

    #拼接格式
    chat_data_by_channel_name = {}
    for channel_id, messages in chat_data_by_channel.items():
        chat_data_by_channel_name[latest_channel_name[channel_id]] = "\n\n".join(messages)

    #loader
    file_sha = ""
    dateshort = time.strftime("%Y%m%d")

    for channel_name, documents in chat_data_by_channel_name.items():
        file_sha = compute_sha1_from_content(documents.encode("utf-8"))
        file_size = len(documents.encode("utf-8"))
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=20
        )
        if documents_is_empty(file_size):
            return create_response(
                f"❌ {channel_name} is empty.",  
                "error",
            )   
        elif documents_already_exists(file_sha):
            return create_response(
                f"🤔 {channel_name} already exists.",  
                "success",
            )         
        documents = text_splitter.split_text(documents)

        docs_with_metadata = [
            Document(
                page_content=doc,
                metadata={
                    "file_sha1": file_sha,
                    "file_size": file_size,
                    "channel_name": channel_name,
                    "chunk_size": 500,
                    "chunk_overlap": 20,
                    "date": dateshort,
                },
            )
            for doc in documents
        ]
              
        commons = common_dependencies()
        commons["chats_vector_store"].add_documents(docs_with_metadata)
    chat_history.update_vectorized_at(chat_ids)

    return create_response(
        f"✅ {len(chat_to_vectordb)} chat records has been uploaded.",  
        "success",
    )        
