from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    embeddings = embedding_model.encode(
        texts,
        show_progress_bar=False,
    )

    return embeddings.tolist()
