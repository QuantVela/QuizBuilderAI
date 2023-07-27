from langchain.document_loaders import TelegramChatFileLoader, TelegramChatApiLoader
from models.files import File
from utils.vectors import VectorManager
from .common import process_file

def process_telegram(file: File, vector_manager: VectorManager):
    return process_file(file, vector_manager, TelegramChatFileLoader)