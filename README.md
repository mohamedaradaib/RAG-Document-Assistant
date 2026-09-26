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
The Streamlit app sends PDF uploads and questions to Inngest. Helper code is in place to extract PDF text, split it into chunks, create embeddings, and store or search them in Qdrant. The Inngest upload function currently returns a placeholder, and there is no question handler yet, so these pieces are not connected into a working question-and-answer flow.

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

Open the Streamlit URL, `http://localhost:8501`.

## Live Demo

## License
[LICENSE](./LICENSE)
