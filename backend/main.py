#!/usr/bin/env python

import logging
import uvicorn

from fastapi import Body, FastAPI
from pathlib import Path

from chromadb.config import Settings
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
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

def record_documents_in_local_store(documents, store, chunk_size=500, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    store.add_documents(texts)
    store.persist()

def execute_prompt(store, llm, prompt):
    retriever = store.as_retriever(search_kwargs={"k": 4})
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )
    return qa(prompt)

@app.on_event("startup")
async def startup_event():
    logging.info("Local search GPT server started")

    logging.debug("Loading or creating local DB")
    app.state.db = get_local_store("local_db")

    # Do not use `Path` or langchain will fail to load GPT4all on Windows.
    model_path = "models/ggml-gpt4all-j-v1.3-groovy.bin"
    logging.debug(f"Loading the LLM from {model_path}")

    app.state.llm = GPT4All(
        model=model_path,
        n_ctx=1000,
        backend='gptj',
        callbacks=[],
        verbose=False
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

@app.post("/prompt")
async def prompt(
    msg: dict = Body(...)
):
    response = execute_prompt(app.state.db, app.state.llm, msg["data"])
    return {"message": response}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=False)

