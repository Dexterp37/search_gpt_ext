#!/usr/bin/env python

import copy
import hashlib
import logging
import uvicorn

from collections import deque
from fastapi import Body, FastAPI
from pathlib import Path
from typing import List, Optional

from chromadb.config import Settings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.docstore.document import Document
from langchain.document_loaders.parsers.html.bs4 import BS4HTMLParser
from langchain.document_loaders.blob_loaders import Blob
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import GPT4All
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

app = FastAPI()
html_parser = BS4HTMLParser()

def get_local_store(store_path_dir: str):
    """
    Creates or opens a local vector store.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    store_path = Path(store_path_dir)
    db = Chroma(
        embedding_function=embeddings,
        client_settings=Settings(
            chroma_db_impl='duckdb+parquet',
            persist_directory=str(store_path),
            anonymized_telemetry=False
        ),
        # This is redundant, but without the persist_directory
        # here the persist() function will fail.
        persist_directory=str(store_path)
    )

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

def get_document_id(doc: Document):
    doc_identifier = f"{doc.metadata['url']}#chunk{doc.metadata['start_index']}".encode('utf-8')
    return hashlib.sha3_256(doc_identifier).hexdigest()

def record_documents_in_local_store(documents, store, chunk_size=512, chunk_overlap=25):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, add_start_index=True
    )
    texts = text_splitter.split_documents(documents)
    doc_ids = [get_document_id(d) for d in texts]
    try:
        # Try to add the documents. If the id is already present, the DB will not
        # like it. If that's the case, resort to updating the existing docs.
        store.add_documents(texts, ids=doc_ids)
    except:
        for id, doc in zip(doc_ids, texts):
            store.update_document(id, doc)
    store.persist()

def execute_prompt(chat_history, qa, prompt):
    # TODO: what about crafting a different prompt, always adding the page the first time,
    # along with 2-3 context?
    response = qa({"question": prompt, "chat_history": list(chat_history)})
    # Append to the chat history.
    chat_history.append((prompt, response["answer"]))
    return response

@app.on_event("startup")
async def startup_event():
    logging.info("Local search GPT server started")

    logging.debug("Loading or creating local DB")
    app.state.db = get_local_store("local_db")

    # Do not use `Path` or langchain will fail to load GPT4all on Windows.
    #model_path = "models/ggml-gpt4all-j-v1.3-groovy.bin"
    model_path = "models/orca-mini-7b.ggmlv3.q4_0.bin"
    logging.debug(f"Loading the LLM from {model_path}")

    app.state.llm = GPT4All(
        model=model_path,
        backend='gptj',
        callbacks=[],
        verbose=True
    )

    # Make sure to store the chat history.
    app.state.chat_history = deque(maxlen=50)
    app.state.retriever = app.state.db.as_retriever(
        search_type="mmr",
        #search_type="similarity_score_threshold",
        #search_kwargs={"score_threshold": .5},
        search_kwargs={"k": 2}
    )
    app.state.qa_chain = ConversationalRetrievalChain.from_llm(
        llm=app.state.llm, chain_type="stuff", retriever=app.state.retriever,
        return_source_documents=True, verbose=True
    )

    logging.info("Start listening for browser messages")

@app.post("/sync")
async def sync(
    msg: dict = Body(...)
):
    logging.debug("Parsing a sync message")
    parsed_docs = get_doc_from_message(msg["data"])
    logging.debug(f"Parsed {len(parsed_docs)} documents from the sync message")
    record_documents_in_local_store(parsed_docs, app.state.db)

@app.post("/store")
async def store(
    msg: dict = Body(...)
):
    data = msg["data"]
    page_context = data["context"]

    if page_context is not None and page_context["rawDOM"] is not None:
        # Extract the text using beautiful soup.
        raw_dom = page_context["rawDOM"]
        page_docs = html_parser.parse(Blob.from_data(raw_dom, path=page_context["pageUrl"]))
        for doc in page_docs:
            doc.metadata["url"] = page_context["pageUrl"]

        # Store the data in the vector DB.
        record_documents_in_local_store(page_docs, app.state.db)

@app.post("/prompt")
async def prompt(
    msg: dict = Body(...)
):
    prompt_data = msg["data"]
    prompt_text = prompt_data["prompt"]
    prompt_context = prompt_data["context"]

    # If there's some context (e.g. page content), add it to the store.
    # Only do that if not already present!
    if prompt_context is not None and "textContent" in prompt_context and prompt_context["textContent"] is not None:
        # Extract the text using beautiful soup.
        raw_dom = prompt_context["rawDOM"]
        page_docs = html_parser.parse(Blob.from_data(raw_dom, path=prompt_context["pageUrl"]))
        for doc in page_docs:
            doc.metadata["url"] = prompt_context["pageUrl"]

        # Don't rely on readermode extracted text for now, it might
        # not capture everything we need.
        #page_docs = [Document(page_content=prompt_context["textContent"], metadata={"url": prompt_context["pageUrl"]})]

        # Store the data in the vector DB.
        record_documents_in_local_store(page_docs, app.state.db)

    response = execute_prompt(app.state.chat_history, app.state.qa_chain, prompt_text)

    return {"message": response}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=False)

