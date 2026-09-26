# AI RAG Agent
An Artificial Intelligence Retrieval-Augmented Generation Agent designed to transfer data into an interactive actionable knowledge base.

## Features
- PDF upload and ingestion flow from the Streamlit UI
- Automatic PDF chunking using sentence-aware splitting
- Embedding generation with OpenAI `text-embedding-3-large`
- Semantic retrieval from a Qdrant vector database
- Context-grounded answer generation using GPT models
- Event-driven workflows with Inngest for async processing and observability
- Source tracking so answers can be traced back to the uploaded documents
- Local development setup suitable for experimenting with production-style RAG patterns

## How it Works
Users upload a PDF through the Streamlit app, which triggers an Inngest workflow that extracts and chunks the document, embeds each chunk with OpenAI, and stores the vectors in Qdrant for semantic search. When a question is asked, the app embeds the query, retrieves the most relevant chunks, and sends them to GPT-4o-mini to generate a concise answer grounded in the document context.

## Tech Stack

- Python
- FastAPI
- LlamaIndex
- Qdrant
- Streamlit
- Inngest
- OpenAI

## Getting Started
### Prerequisites
- OpenAI API Key

### Installation
1. Clone the repository
```bash
git clone https://github.com/mohamedaradaib/AI-RAG-Agent.git
cd AI-RAG-Agent
```

## Live Demo

## License
[LICENSE](./LICENSE)
