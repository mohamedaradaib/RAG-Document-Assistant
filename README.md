# AI RAG Agent
An Artificial Intelligence Retrieval-Augmented Generation Agent designed to transfer data into an interactive actionable knowledge base.

## Features
- Upload PDFs and submit questions in the Streamlit app
- Extract text from PDFs and split it into overlapping chunks
- Create embeddings with OpenAI's `text-embedding-3-large` model
- Store chunks in Qdrant and search for relevant passages
- Include source names with search results
- Use Inngest to send upload and question events

## How it Works
This app lets users upload a PDF in Streamlit, processes the document into searchable text chunks, embeds those chunks with OpenAI, and stores them in Qdrant for semantic retrieval. When a question is asked, the app searches the most relevant chunks, uses them as context, and generates a grounded answer with source references so the response is based on the uploaded document content instead of general knowledge.

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

## Run the Application
1. Create a `.env` file in the project root and add your OpenAI key:
```env
OPENAI_API_KEY=your_openai_api_key
INNGEST_DEV=true
```

2. Install the project dependencies:
```bash
uv sync
```

3. Start the Inngest Dev Server in a terminal:
```bash
npx inngest-cli@latest dev
```

4. Start the FastAPI application in a second terminal:
```bash
uv run uvicorn main:app --reload --port 8000
```

5. Start Streamlit in a third terminal:
```bash
uv run streamlit run streamlit_app.py
```

Open the Streamlit localhost URL - `http://localhost:8501`

## Live Demo

## License
[LICENSE](./LICENSE)
