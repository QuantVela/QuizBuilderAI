import os
import time
from langchain.document_loaders.base import Document
from langchain.utilities import ApifyWrapper
from models.settings import Settings, common_dependencies
from utils.vectors import VectorManager
from models.urls import Url

settings = Settings()
openai_api_key = settings.openai_api_key
os.environ["APIFY_API_TOKEN"] = settings.apify_api_token
apify = ApifyWrapper()

async def process_web(
        url: Url, 
        vector_manager: VectorManager
):
    dateshort = time.strftime("%Y%m%d")
    loader = apify.call_actor(
        actor_id="apify/website-content-crawler",
        run_input={"startUrls": [{"url": url.url}]},
        dataset_mapping_function=lambda item: Document(
            page_content=item["text"] or "", metadata={"source": item["url"]}
        ),
    )
    documents = loader.load()
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