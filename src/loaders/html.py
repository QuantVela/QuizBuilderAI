import re
import unicodedata

import requests
from langchain.document_loaders import UnstructuredHTMLLoader
from models.files import File
from utils.vectors import VectorManager
from .common import process_file


def process_html(file: File, vector_manager: VectorManager):
    return process_file(file, vector_manager, UnstructuredHTMLLoader)


def get_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None


def slugify(text):
    text = unicodedata.normalize('NFKD', text).encode(
        'ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text