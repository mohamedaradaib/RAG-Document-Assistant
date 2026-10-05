def normalize_chat_history(chat_history):
    """Normalize chat history into a list of role/content dictionaries."""
    if not chat_history:
        return []

    normalized = []
    for item in chat_history:
        if not isinstance(item, dict):
            continue

        role = str(item.get("role", "")).strip().lower()
        content = str(item.get("content", "")).strip()

        if role not in {"user", "assistant"} or not content:
            continue

        normalized.append({"role": role, "content": content})

    return normalized


def build_rag_prompt(question: str, context_block: str, chat_history=None) -> str:
    """Build the final user prompt used for grounded answering."""
    cleaned_question = (question or "").strip()
    context = (context_block or "").strip() or "No additional context provided."
    history = normalize_chat_history(chat_history)

    prompt_lines = [
        "Use the following context to answer the question.",
        "",
        "Context:",
        context,
        "",
    ]

    if history:
        prompt_lines.extend(["Previous conversation:"])
        for item in history:
            prompt_lines.append(f"{item['role'].capitalize()}: {item['content']}")
        prompt_lines.append("")

    prompt_lines.extend([
        f"Question: {cleaned_question}",
        "Answer concisely using the context above and the previous conversation when relevant.",
    ])

    return "\n".join(prompt_lines)
