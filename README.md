Extraction‑FastAPI

A FastAPI‑based extraction service that provides endpoints to extract structured information from input data (e.g., text files, PDFs, or other sources) using configurable extractors and Language Model backends.

This project aims to be a scalable and extensible microservice for extraction workflows. It can be used as a standalone API or integrated into larger LLM‑powered pipelines.

⸻

 Features
	•	 Extraction API endpoints for sending raw content and receiving extracted structured results
	•	 Support for file upload and text input
	•	 Modular architecture built on FastAPI for easy expansion
	•	 Included tests for reliability
	•	 Example .env configuration file

⸻

 Tech Stack
	•	Python 3.11+
	•	FastAPI — high‑performance API framework  ￼
	•	Uvicorn — ASGI server
	•	Pydantic — data validation
	•	Optional LLM frameworks depending on implementation (e.g., OpenAI, LangChain)
