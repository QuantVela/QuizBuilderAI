import time
from langchain.schema import Document
from models.files import File
from utils.vectors import VectorManager
from langchain.document_loaders import WhatsAppChatLoader

async def process_file(
    file: File,
    vector_manager: VectorManager,
    loader_class
):
    dateshort = time.strftime("%Y%m%d")

    file.compute_documents(loader_class)

    for doc in file.documents:
        metadata = {
            "file_sha1": file.file_sha1,
            "file_size": file.file_size,
            "file_name": file.file_name,
            "chunk_size": file.chunk_size,
            "chunk_overlap": file.chunk_overlap,
            "date": dateshort,
        }
        doc_with_metadata = Document(
            page_content=doc.page_content, metadata=metadata)
        
        created_vector = vector_manager.create_vector(doc_with_metadata)

    return 
