import pydantic


class RAGChunkAndSrc(pydantic.BaseModel):
    chunks: list[str]
    source_id: str = None


class RAGSearchResult(pydantic.BaseModel):
    contexts: list[str]
    sources: list[str]
    error: str | None = None


class RAGUpsertResult(pydantic.BaseModel):
    ingested: int
    error: str | None = None


class RAQQueryResult(pydantic.BaseModel):
    answer: str
    sources: list[str]
    num_contexts: int
    error: str | None = None