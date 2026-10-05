from pathlib import Path

from openai import OpenAI
from llama_index.readers.file.html import HTMLTagReader
from llama_index.core.node_parser import SentenceSplitter
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader

load_dotenv()

client = OpenAI()
EMBED_MODEL = "text-embedding-3-large"

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)


def load_and_chunk_file(path: str):
    file_path = Path(path)
    if file_path.suffix.lower() in {".html", ".htm"}:
        docs = HTMLTagReader(tag="body").load_data(file=file_path)
    else:
        docs = SimpleDirectoryReader(input_files=[path]).load_data()
    texts = [doc.text for doc in docs if getattr(doc, "text", None)]
    chunks = []
    for text in texts:
        chunks.extend(splitter.split_text(text))
    return chunks

def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]