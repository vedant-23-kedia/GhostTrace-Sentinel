\# GhostTrace Sentinel



GhostTrace Sentinel is an AI-powered code governance dashboard that validates frontend code against business requirements and generates PASS/FAIL audit reports.



\## Features


\- Premium frontend dashboard

\- Team/operator login

\- Business requirement sync

\- Design image upload support

\- Local audit engine using `judge\_engine.py`

\- PASS/FAIL audit reporting

\- `current\_context.json` and `latest\_report.json` workflow

\- Git commit integration from frontend

\- FastAPI backend

## RAG Pipeline

GhostTrace Sentinel uses Retrieval-Augmented Generation (RAG) to provide relevant business requirement context during frontend validation.

The pipeline retrieves relevant requirements from the vector database and supplies the retrieved context to the LLM during analysis. This helps the validation workflow compare the frontend implementation against the expected business requirements and generate structured PASS/FAIL audit results.

## RAG Workflow

1. Business requirements are processed and stored for retrieval.
2. Relevant requirement context is retrieved based on the validation input.
3. Retrieved context is provided to the LLM along with the frontend implementation.
4. The system analyzes the implementation against the relevant requirements.
5. Validation results are returned as structured PASS/FAIL audit output.

\## Tech Stack



\- HTML

\- CSS

\- JavaScript

\- Python

\- FastAPI

\- Uvicorn

\- Git



\## How to Run



Install dependencies:



```bash

pip install fastapi uvicorn python-multipart

