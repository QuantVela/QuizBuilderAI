from langchain.document_loaders import SlackDirectoryLoader
from models.files import File
from utils.vectors import VectorManager
from .common import process_file

def process_slack(file: File, vector_manager: VectorManager):
    return process_file(file, vector_manager, SlackDirectoryLoader)