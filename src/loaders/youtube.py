from langchain.document_loaders import YoutubeLoader
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import OpenAIWhisperParser
from langchain.document_loaders.blob_loaders.youtube_audio import YoutubeAudioLoader
from langchain.schema import Document
import os
import shutil
import openai
import time
from models.settings import Settings, common_dependencies
from utils.vectors import VectorManager
from models.urls import Url

async def process_youtube(
        url: Url, 
        vector_manager: VectorManager
):
    loader = YoutubeLoader.from_youtube_url(url.url, add_video_info=True)
    documents = loader.load()
    # print(documents)
    if not documents:  # 如果documents为空
        settings = Settings()
        openai.api_key = settings.openai_api_key # for whisper
        save_dir = "assets/utube_audio"
        loader = GenericLoader(YoutubeAudioLoader([url.url], save_dir), OpenAIWhisperParser())
        documents = loader.load()
        # print(documents)

        shutil.rmtree(save_dir)
        os.mkdir(save_dir)
    
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

