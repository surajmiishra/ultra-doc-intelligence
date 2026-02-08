import os
import shutil
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG --- #
VECTOR_DB_PATH = "./data/chroma_db"
EMBEDDING_MODEL = OpenAIEmbeddings(model="text-embedding-3-small")
LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- 1. DOCUMENT PROCESSING --- #
def save_and_process_file(file_obj, filename: str) -> str:
    file_path = os.path.join("./data", filename)
    os.makedirs("./data", exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file_obj, buffer)
        
    if filename.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif filename.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        loader = TextLoader(file_path)
        
    docs = loader.load()
    
    # Standard chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)
    
    # Force Re-creation of DB to ensure clean math
    # Note: In production, we wouldn't delete this every time, but for this test it ensures consistency
    if os.path.exists(VECTOR_DB_PATH):
        shutil.rmtree(VECTOR_DB_PATH)

    Chroma.from_documents(
        documents=splits,
        embedding=EMBEDDING_MODEL,
        persist_directory=VECTOR_DB_PATH,
        collection_metadata={"hnsw:space": "cosine"}
    )
    return f"Processed {len(splits)} chunks from {filename}"

# --- 2. RAG & CONFIDENCE --- #
def query_document(question: str):
    vector_db = Chroma(
        persist_directory=VECTOR_DB_PATH, 
        embedding_function=EMBEDDING_MODEL
    )
    
    # Use 'similarity_search_with_relevance_scores'
    # This automatically normalizes scores to range 0-1
    results = vector_db.similarity_search_with_relevance_scores(question, k=3)
    
    if not results:
        return {"answer": "No relevant documents found.", "confidence": 0.0, "sources": []}

    # Get the top score
    top_doc, top_score = results[0]
    
    # --- TUNED THRESHOLD ---
    # For logistics queries (dates, IDs), scores often hover around 0.3 - 0.5
    # We set the "Guardrail" to 0.25 (25%) to let valid answers through
    THRESHOLD = 0.25
    
    context_text = "\n\n".join([doc.page_content for doc, _ in results])
    sources = [doc.metadata.get("source", "unknown") for doc, _ in results]

    # GUARDRAIL CHECK
    if top_score < THRESHOLD:
        return {
            "answer": "I cannot find the answer to this question in the uploaded documents (Low Confidence).",
            "confidence": round(top_score, 2),
            "sources": []
        }

    # Generate Answer
    prompt = ChatPromptTemplate.from_template("""
    You are a Logistics Assistant. Answer the question based ONLY on the following context.
    If the answer is not in the context, say "I don't know".
    
    Context:
    {context}
    
    Question: {question}
    """)
    
    chain = prompt | LLM
    response = chain.invoke({"context": context_text, "question": question})
    
    return {
        "answer": response.content,
        "confidence": round(top_score, 2),
        "sources": list(set(sources))
    }

# --- 3. STRUCTURED EXTRACTION --- #
class ShipmentData(BaseModel):
    shipment_id: Optional[str] = Field(None, description="The ID of the shipment or BOL number")
    shipper: Optional[str] = Field(None, description="Name of the party sending the goods")
    consignee: Optional[str] = Field(None, description="Name of the party receiving the goods")
    pickup_datetime: Optional[str] = Field(None, description="Date/Time of pickup")
    delivery_datetime: Optional[str] = Field(None, description="Date/Time of delivery")
    equipment_type: Optional[str] = Field(None, description="Truck type (e.g., Van, Reefer, Flatbed)")
    mode: Optional[str] = Field(None, description="Transport mode (e.g., LTL, FTL, Air)")
    rate: Optional[float] = Field(None, description="Total cost or rate of the shipment")
    currency: Optional[str] = Field(None, description="Currency code (e.g., USD)")
    weight: Optional[str] = Field(None, description="Total weight with units")
    carrier_name: Optional[str] = Field(None, description="Name of the trucking company")

def extract_shipment_data():
    vector_db = Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=EMBEDDING_MODEL)
    
    results = vector_db.similarity_search("shipment details shipper consignee rate carrier", k=10)
    context_text = "\n".join([doc.page_content for doc in results])
    
    structured_llm = LLM.with_structured_output(ShipmentData)
    
    extraction_prompt = f"""
    Extract the following logistics details from the text below. 
    Return null if the specific field is not found.
    
    Text:
    {context_text}
    """
    
    result = structured_llm.invoke(extraction_prompt)
    return result.dict()