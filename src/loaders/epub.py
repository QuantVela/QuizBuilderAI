from langchain.document_loaders.epub import UnstructuredEPubLoader
from models.files import File
from utils.vectors import VectorManager
from .common import process_file


def process_epub(file: File, vector_manager: VectorManager):
    file.chunk_overlap = 0
    return process_file(file, vector_manager, UnstructuredEPubLoader)