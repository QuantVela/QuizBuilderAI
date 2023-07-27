from langchain.document_loaders import GitbookLoader
from models.settings import common_dependencies
from langchain.schema import Document
from utils.vectors import VectorManager
from models.urls import Url
import time

async def process_gitbook(
        url: Url, 
        vector_manager: VectorManager
):
    loader = GitbookLoader(url.url, load_all_paths=True)
    documents = loader.load()
    print(f"fetched {len(documents)} documents.")

    dateshort = time.strftime("%Y%m%d")
    url.compute_documents(documents)

    doc_with_metadata = [
        Document(
            page_content=doc.page_content,
            metadata={
                "url": url.url,
                "url_site": url.url_site,
                "docs_size": url.docs_size,
                "chunk_size": url.chunk_size,
                "chunk_overlap": url.chunk_overlap,
                "date": dateshort,
            },
        )
        for doc in url.documents
    ]
        
    commons = common_dependencies()
    commons["documents_vector_store"].add_documents(doc_with_metadata)

    return

