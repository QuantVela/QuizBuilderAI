from langchain.document_loaders import CSVLoader
from models.files import File
from .common import process_file
from utils.vectors import VectorManager


def process_csv(file: File, vector_manager: VectorManager):
    return process_file(file, vector_manager, CSVLoader)