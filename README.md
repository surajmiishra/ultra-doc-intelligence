# Ultra Doc-Intelligence

**Ultra Doc-Intelligence** is an AI-powered document assistant built for the **Logistics & Transportation industry**.  
It enables users to upload complex logistics documents—such as **Rate Confirmations, Bills of Lading (BOLs), and Invoices**—and interact with them using natural language or extract structured data automatically.

The system simulates an intelligent agent inside a **Transportation Management System (TMS)**, featuring **hallucination guardrails, confidence scoring, and strict JSON extraction**.

---

## Features

- **Multi-Format Support**  
  Ingests **PDF, DOCX, and TXT** files using robust loaders.

- **RAG-Based Question Answering**  
  Answers questions **strictly based on document context**, with source-aware retrieval and citation.

- **Hallucination Guardrails**  
  Automatically rejects answers if retrieval confidence is below a defined threshold, preventing the AI from guessing.

- **Confidence Scoring**  
  Returns a **quantifiable confidence score (0–100%)** based on vector similarity, allowing users to trust (or verify) the output.

- **Structured Data Extraction**  
  Converts unstructured document text into a standardized **JSON schema** (Shipment ID, Rate, Carrier, etc.), returning `null` for missing fields rather than hallucinating.

- **Minimalist UI**  
  Clean **Streamlit interface** for uploading documents, querying, and extracting data.

---

## System Architecture

The system follows a modular RAG (Retrieval-Augmented Generation) pipeline:

1. **Ingestion:**  
   User uploads a file (PDF/DOCX) → Text is parsed & cleaned.

2. **Chunking:**  
   Text is split into overlapping chunks to preserve context.

3. **Embedding:**  
   Chunks are converted to vectors (OpenAI `text-embedding-3-small`) and stored in **ChromaDB**.

4. **Retrieval:**  
   User query is embedded → System finds top 3 semantic matches (Cosine Similarity).

5. **Guardrail Check:**  
   If similarity score < Threshold (0.25) → **Stop & Return "Not Found"**

6. **Generation:**  
   If Pass → Top chunks + System Prompt sent to LLM (`gpt-4o-mini`) → Answer generated.

---

## Engineering Decisions

### 1. Chunking Strategy

**Decision:** `RecursiveCharacterTextSplitter`  
- `chunk_size = 1000`  
- `chunk_overlap = 200`

**Reasoning:**  
Logistics documents often contain wide tables (e.g., Rate Breakdowns) where the "Header" is far from the "Value". A standard sentence splitter would break the link between "Total Rate" and "$1000".  

The 1000-character chunk size captures full table rows, while the 200-character overlap ensures no critical data is lost at chunk boundaries.

---

### 2. Retrieval & Confidence Scoring

**Method:** Cosine Similarity with Normalized Scoring

**Formula:**

```python
Confidence % = (1 - Cosine Distance) * 100
````

**Threshold:**

* **Minimum Confidence:** 25% (0.25)

**Why 25%?**
Unlike general knowledge queries, logistics queries are often keyword-heavy (e.g., "Reference ID"). Vector databases may assign lower semantic scores (~0.30) even when matches are correct.

A threshold of 0.25 filters irrelevant noise while allowing valid, specific lookups.

---

### 3. Guardrails Approach

**Layer 1: Retrieval Guardrail (Pre-Computation)**

* Vector similarity is checked before calling the LLM
* **Action:** If score < 0.25 → Return
  `"I cannot find the answer in the document"`

**Benefit:**
Prevents hallucination and reduces unnecessary API calls.

---

**Layer 2: Prompt Guardrail (In-Context)**

System Prompt Instruction:

> *"Answer based ONLY on the provided context. If the answer is not found, say 'I don't know'."*

**Benefit:**
Handles edge cases where retrieval succeeds but the required detail is missing.

---

### 4. Structured Extraction

**Method:** OpenAI Function Calling (`with_structured_output`) + Pydantic Models

**Why?**
Free-form prompting often produces invalid JSON or hallucinated values.

Pydantic enforces schema compliance. Missing fields (e.g., `carrier_name`) are returned as `null`, ensuring downstream data integrity.

---

## Failure Cases & Limitations

1. **Handwritten Text:**
   Uses standard PDF extraction (`pypdf`). Cannot read scanned images or handwritten notes.

2. **Complex Table Alignment:**
   Extremely complex multi-page tables may lose row alignment during chunking.

3. **Ambiguous Entities:**
   Documents listing multiple addresses without clear labels may occasionally cause misclassification.

---

## Future Improvement Ideas

1. **OCR Integration:**
   Add AWS Textract / Tesseract for scanned & handwritten documents.

2. **Multi-File Reasoning:**
   Cross-document validation (e.g., Invoice vs Rate Confirmation).

3. **User Feedback Loop:**
   UI-based thumbs up/down for adaptive threshold tuning.

4. **Advanced Table Parsing:**
   Integrate `pdfplumber` / `unstructured` for better table handling.

---

## Installation & Run

### Prerequisites

* Python **3.8+**
* OpenAI API Key

---

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/ultra-doc-intelligence.git
cd ultra-doc-intelligence

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

### 2. Configure Environment

Create a `.env` file:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

---

### 3. Start Backend (FastAPI)

```bash
uvicorn backend.main:app --reload
```

API runs at:

```
http://127.0.0.1:8000
```

---

### 4. Start Frontend (Streamlit)

Open a **new terminal**:

```bash
streamlit run frontend/app.py
```

The UI will open automatically in your browser.

```


