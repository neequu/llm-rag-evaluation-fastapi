def build_rag_prompt(
    query: str,
    contexts: list[str],
) -> str:

    joined_context = "\n\n".join(contexts)

    return f"""
You are a question-answering assistant. Answer the question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I could not find the answer in the provided documents."

Keep the answer concise. Answer in 2-4 sentences unless a list is more appropriate.

Context:
{joined_context}

Question:
{query}

Answer:
"""
