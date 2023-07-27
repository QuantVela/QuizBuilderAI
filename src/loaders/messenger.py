from langchain.document_loaders import FacebookChatLoader
from models.files import File
from utils.vectors import VectorManager
from .common import process_file

def process_messenger(file: File, vector_manager: VectorManager):
    return process_file(file, vector_manager, FacebookChatLoader)