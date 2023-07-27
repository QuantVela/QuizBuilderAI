import os
import tempfile
import time
import aiohttp
import json
import base64
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models.files import File
from utils.file import compute_sha1_from_content
from utils.vectors import VectorManager
from models.settings import Settings, common_dependencies

async def process_image(
    file: File,
    vector_manager: VectorManager
):
    temp_filename = None
    file_sha = ""
    dateshort = time.strftime("%Y%m%d")
    file_name = file.file_name

    # use this for google cloud vision
    settings = Settings() 
    google_cloud_api_key = settings.google_cloud_api_key

    try:
        upload_file = file.file
        content = await upload_file.read()
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=upload_file.filename, 
            mode='wb'
        ) as tmp_file:
            tmp_file.write(content)  
            tmp_file.flush()
            tmp_file.close()

            temp_filename = tmp_file.name

            # Process the image
            with open(tmp_file.name, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Prepare the JSON payload
            payload = {
                "requests": [
                    {
                        "image": {"content": encoded_image},
                        "features": [{"type": "TEXT_DETECTION"}],
                    }
                ]
            }

            header = {
                "Content-Type": "application/json; charset=utf-8",
            }

            url = f"https://vision.googleapis.com/v1/images:annotate?key={google_cloud_api_key}"

            # Send the async request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, headers=header, data=json.dumps(payload)
                ) as response:
                    result = await response.json()

                    if response.status == 200:
                        # Get fullTextAnnotation
                        full_text_annotation = result.get("responses", [])[0].get(
                            "fullTextAnnotation"
                        )

                        if full_text_annotation:
                            extracted_text = full_text_annotation.get("text")
                        else:
                            extracted_text = ""
                    else:
                        raise Exception(
                            f"Google Cloud Vision API returned an error. Status code: {response.status}, Error: {result}"
                        )

        print("Extracted text:", extracted_text)

        file_sha = compute_sha1_from_content(extracted_text.encode("utf-8"))
        file_size = len(extracted_text.encode("utf-8"))

        chunk_size = 500
        chunk_overlap = 20
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_text(extracted_text)

        docs_with_metadata = [
            Document(
                page_content=text,
                metadata={
                    "file_sha1": file_sha,
                    "file_size": file_size,
                    "file_name": file_name,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "date": dateshort,
                },
            )
            for text in texts
        ]

        commons = common_dependencies()
        commons["documents_vector_store"].add_documents(docs_with_metadata)
        # vector_manager.create_vector(docs_with_metadata)

    finally:
        if temp_filename and os.path.exists(temp_filename):
            os.remove(temp_filename)
