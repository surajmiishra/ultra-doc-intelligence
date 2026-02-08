# Ultra Doc Intelligence

An intelligent document processing system using RAG (Retrieval-Augmented Generation).

## Project Structure

- **data/**: Stores uploaded files and vector database
- **backend/**: FastAPI server with RAG logic
- **frontend/**: Streamlit user interface

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run backend: `uvicorn backend.main:app --reload`
3. Run frontend: `streamlit run frontend/app.py`
