
#  Ultra Doc-Intelligence

**Ultra Doc-Intelligence** is an AI-powered document assistant built for the **Logistics & Transportation industry**.  
It enables users to upload complex logistics documents—such as **Rate Confirmations, Bills of Lading (BOLs), and Invoices**—and interact with them using natural language or extract structured data automatically.

The system simulates an intelligent agent inside a **Transportation Management System (TMS)**, featuring **hallucination guardrails, confidence scoring, and strict JSON extraction**.

---

##  Features

-  **Multi-Format Support**  
  Ingests **PDF, DOCX, and TXT** files.

-  **RAG-Based Question Answering**  
  Answers questions **strictly based on document context**, with source-aware retrieval.

-  **Hallucination Guardrails**  
  Automatically rejects answers if retrieval confidence is below a defined threshold.

-  **Confidence Scoring**  
  Returns a **quantifiable confidence score (0–100%)** based on vector similarity.

-  **Structured Data Extraction**  
  Converts unstructured document text into a standardized **JSON schema**  
  (Shipment ID, Rate, Carrier, etc.), returning `null` for missing fields.

-  **Minimalist UI**  
  Clean **Streamlit interface** for uploading documents, querying, and extracting data.

---

##  Tech Stack

- **Language:** Python 3.10+  
- **LLM:** OpenAI `gpt-4o-mini` (optimized for speed & cost)  
- **Embeddings:** OpenAI `text-embedding-3-small`  
- **Vector Database:** ChromaDB (local, persistent)  
- **Orchestration:** LangChain  
- **Backend:** FastAPI  
- **Frontend:** Streamlit  

---

##  Architecture & Engineering Decisions

###  Chunking Strategy

**Decision:**  
`RecursiveCharacterTextSplitter`  
- `chunk_size = 1000`  
- `chunk_overlap = 200`

**Reasoning:**  
Logistics documents often contain wide tables (e.g., rate breakdowns).  
Sentence-based splitting can separate keys from values (e.g., `"Total"` and `"1000"`).  
The overlap preserves context across chunk boundaries.

---

###  Retrieval & Confidence Scoring

**Decision:**  
Cosine Similarity with normalized scoring.

**Formula:**
```

Confidence % = (1 - Cosine Distance) × 100

````

**Threshold:**  
- Minimum confidence: **25% (0.25)**

**Why 25%?**  
Keyword-heavy logistics queries often score around `0.3`.  
Scores below this typically indicate the concept is **not present** in the document.

---

###  Hallucination Guardrails

**Two-Layer Validation**

**Layer 1 – Retrieval Guardrail**
- If similarity score < threshold → return  
  **“I cannot find the answer in the document.”**
- Skips LLM call to save tokens and prevent hallucination.

**Layer 2 – Prompt Guardrail**
- System prompt enforces **“I don’t know”** if context does not contain the answer.

---

###  Structured Extraction

**Decision:**  
OpenAI **Function Calling** with `with_structured_output` + **Pydantic Models**

**Why?**
- Free-form prompting often breaks JSON.
- Pydantic enforces:
  - Required fields
  - Data types
  - `null` for missing values (no hallucinated data)

Example:  
If `carrier_name` is missing in a Shipper Quote, the model **must return `null`**.

---

## ⚙️ Installation & Run

### Prerequisites
- Python **3.8+**
- OpenAI API Key

---

###  Clone & Setup

```bash
git clone https://github.com/your-username/ultra-doc-intelligence.git
cd ultra-doc-intelligence

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
````

---

###  Configure Environment

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

---

###  Start Backend (FastAPI)

```bash
uvicorn backend.main:app --reload
```

API will be available at:
`http://127.0.0.1:8000`

---

###  Start Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

The UI will automatically open in your browser.

---

