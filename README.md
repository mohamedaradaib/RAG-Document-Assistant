# VectorRAG

## Planned Features

- [ ] PDF ingestion and chunking
- [ ] Vector embeddings with OpenAI
- [ ] Vector storage with Qdrant
- [ ] RAG query functionality
- [ ] Streamlit web interface
- [ ] API endpoints
- [ ] Workflow orchestration with Inngest

## Tech Stack

- FastAPI - Web framework
- LlamaIndex - Data indexing
- Qdrant - Vector database
- Streamlit - Frontend UI
- OpenAI - Embeddings & LLM
- Inngest - Workflow orchestration

## Getting Started

```bash
# Install dependencies
uv sync

# Set environment variables
echo "OPENAI_API_KEY=your-key" > .env
```

## TODO

- [ ] Implement PDF loader
- [ ] Set up Qdrant integration
- [ ] Create FastAPI endpoints
- [ ] Build Streamlit UI
- [ ] Add documentation
- [ ] Set up error handling
- [ ] Add tests

## Project Structure

```
VectorRAG/
├── main.py             
├── streamlit_app.py     
├── vector_db.py         
├── custom_types.py     
└── pyproject.toml
```