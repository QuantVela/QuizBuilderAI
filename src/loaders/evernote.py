from langchain.document_loaders import EverNoteLoader
from models.files import File
from .common import process_file
from utils.vectors import VectorManager

#如何从 Evernote导出文件.enex https://help.evernote.com/hc/en-us/articles/209005557-Export-notes-and-notebooks-as-ENEX-or-HTML
def process_evernote(file: File, vector_manager: VectorManager):
    return process_file(file, vector_manager, EverNoteLoader)

