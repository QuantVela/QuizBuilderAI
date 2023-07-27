from langchain.document_loaders import Docx2txtLoader
from models.files import File
from .common import process_file
from utils.vectors import VectorManager

def process_docx(file: File, vector_manager: VectorManager):
    return process_file(file, vector_manager, Docx2txtLoader)