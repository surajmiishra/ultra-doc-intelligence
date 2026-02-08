from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from backend.rag_engine import save_and_process_file, query_document, extract_shipment_data

app = FastAPI(title="Ultra Doc-Intelligence API")

class QuestionRequest(BaseModel):
    question: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    msg = save_and_process_file(file.file, file.filename)
    return {"message": msg}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    result = query_document(request.question)
    return result

@app.post("/extract")
async def extract_data():
    data = extract_shipment_data()
    return data