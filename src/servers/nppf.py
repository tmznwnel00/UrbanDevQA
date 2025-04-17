from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores.base import VectorStoreRetriever
from mcp.server.fastmcp import FastMCP
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from loguru import logger
from pathlib import Path
import uuid

from ..config import ServersConfig
CONFIG = ServersConfig.national_policy_planning_framework()

def create_retriever() -> VectorStoreRetriever:
    """
    Creates and returns a document retriever based on FAISS vector store.

    This function performs the following steps:
    1. Loads a PDF document(place your PDF file in the data folder)
    2. Splits the document into manageable chunks
    3. Creates embeddings for each chunk
    4. Builds a FAISS vector store from the embeddings
    5. Returns a retriever interface to the vector store

    Returns:
        Any: A retriever object that can be used to query the document database
    """
    # Step 1: Load Documents
    # PyMuPDFLoader is used to extract text from PDF files
    with open(Path(CONFIG.data_path) / 'NPPF_December_2024.md', 'r') as f:
        content = f.read()

    pages = content.split('\n\n\n')
    docs = []
    for i, doc in enumerate(pages):
        # Create a Document object for each page
        document = Document(page_content=doc, metadata={
            "source": "NPPF_December_2024", "page": i + 1
        })
        docs.append(document)

    # Step 2: Split Documents
    # Recursive splitter divides documents into chunks with some overlap to maintain context
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    split_documents = text_splitter.split_documents(docs)
    # add unique id to each document
    for i, doc in enumerate(split_documents):
        doc.metadata['id'] = f'P{doc.metadata["page"]}_' + str(uuid.uuid4())

    # Step 3: Create Embeddings
    # OpenAI's text-embedding-3-small model is used to convert text chunks into vector embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Step 4: Create Vector Database
    # FAISS is an efficient similarity search library that stores vector embeddings
    # and allows for fast retrieval of similar vectors
    vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

    # Step 5: Create Retriever
    # The retriever provides an interface to search the vector database
    # and retrieve documents relevant to a query
    retriever = vectorstore.as_retriever()
    return retriever


retriever = create_retriever()
logger.debug(f"Retriever created.")

mcp = FastMCP(
    name=CONFIG.server_name,
    instructions="A Retriever that can retrieve information from the database.",
    host=CONFIG.host,
    port=CONFIG.port,
)


@mcp.tool()
async def retrieve_nppf(query: str) -> str:
    """
    Retrieves information from the document database based on the query.

    This function creates a retriever, queries it with the provided input,
    and returns the concatenated content of all retrieved documents.

    Args:
        query (str): The search query to find relevant information

    Returns:
        str: Concatenated text content from all retrieved documents
    """
    # Create a new retriever instance for each query
    # Note: In production, consider caching the retriever for better performance
    retriever = create_retriever()

    # Use the invoke() method to get relevant documents based on the query
    retrieved_docs = await retriever.ainvoke(query)

    # Join all document contents with newlines and return as a single string

    result = ""
    for doc in retrieved_docs:
        result += f"# Source ID: {doc.metadata['id']}"
        result += doc.page_content + "\n"

    return result

if __name__ == "__main__":
    # Run the MCP server with stdio transport for integration with MCP clients
    mcp.run(transport="sse")
    logger.info(f"Starting server on {CONFIG.host}:{CONFIG.port}")