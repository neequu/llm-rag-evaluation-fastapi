def build_rag_prompt(
    query: str,
    contexts: list[str],
) -> str:
    if not contexts:
        return "I could not find the answer in the provided documents."

    joined_context = "\n\n".join(contexts)

    return f"""Answer the question based ONLY on the context below.

Context:
{joined_context}

Question: {query}

Answer:"""
