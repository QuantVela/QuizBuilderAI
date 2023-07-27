from langchain.document_loaders import TextLoader
from models.files import File

from .common import process_file
from utils.vectors import VectorManager


async def process_txt(file: File, vector_manager: VectorManager):
    return await process_file(file, vector_manager, TextLoader)