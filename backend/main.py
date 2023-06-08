#!/usr/bin/env python
# https://github.com/mdn/webextensions-examples/blob/main/native-messaging/app/ping_pong.py

import logging
import sys
import json
import struct

from pathlib import Path

from chromadb.config import Settings
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("search-gpt-debug.log"),
        logging.StreamHandler()
    ]
)

# Read a message from stdin and decode it.
def getMessage():
    rawLength = sys.stdin.buffer.read(4)
    if len(rawLength) == 0:
        sys.exit(0)
    messageLength = struct.unpack('@I', rawLength)[0]
    message = sys.stdin.buffer.read(messageLength).decode('utf-8')
    return json.loads(message)

# Encode a message for transmission, given its content.
def encodeMessage(messageContent):
    # https://docs.python.org/3/library/json.html#basic-usage
    # To get the most compact JSON representation, you should specify
    # (',', ':') to eliminate whitespace.
    # We want the most compact representation because the browser rejects
    # messages that exceed 1 MB.
    encodedContent = json.dumps(messageContent, separators=(',', ':')).encode('utf-8')
    encodedLength = struct.pack('@I', len(encodedContent))
    return {'length': encodedLength, 'content': encodedContent}

# Send an encoded message to stdout
def sendMessage(encodedMessage):
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.buffer.write(encodedMessage['content'])
    sys.stdout.buffer.flush()

def get_local_store(store_path_dir: str):
    """
    Creates or opens a local vector store.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    store_path = Path(store_path_dir)
    #if store_path.exists():
    db = Chroma(embedding_function=embeddings, client_settings=Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory=str(store_path),
        anonymized_telemetry=False
    ))

    return db

def get_doc_from_message(data):
    """
    This returns a langchain Document from the Firefox data packet.
    This assumes the format of the data coming from Firefox is fixed.
    """

    docs = []
    for d in data:
        doc_metadata = {k: v for k, v in d.items() if k != "title"}
        # Use the doc title as content.
        doc_content = d["title"] if d["title"] is not None else "Unknown"
        docs.append(Document(page_content=doc_content, metadata=doc_metadata))
    return docs

def record_documents_in_local_store(documents, store, chunk_size=500, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    store.add_documents(texts)

    store.persist()

def main():
    logging.info("Local search GPT server started")

    logging.debug("Loading or creating local DB")
    db = get_local_store("local_db")

    logging.info("Start listening for browser messages")
    while True:
        msg = getMessage()
        if msg["type"] == "sync":
            logging.debug("Parsing a sync message")
            parsed_docs = get_doc_from_message(msg["data"])
            logging.debug(f"Parsed {len(parsed_docs)} documents from the sync message")
            record_documents_in_local_store(parsed_docs, db)
        elif msg["type"] == "prompt":
            sendMessage(encodeMessage("Smart answer"))

if __name__ == '__main__':
    main()
